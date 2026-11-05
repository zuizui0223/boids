"""v49: exact original AHN2-C-valid GPS next direction vs next terrain z(C).

Same original 2010+2011 wild GPS triples, identical 2010-selected AHN2
source tiles, RWS WATHTE NAP phase and year-ago ghost as frozen in v48.
Adds ORIGINAL B->C unit direction to the height-valid v48 source rows by
exact same bird+original B timestamp. DO NOT claim actual front tracking.
"""
from __future__ import annotations
import argparse,json,math,tempfile
from collections import Counter,defaultdict
from datetime import timedelta,timezone
from pathlib import Path
import numpy as np

from source_preflight import download_and_pin
from ameland_external_site import original_gps
from source_fetch_resilience import observed_rws_year
from source_original_gps_ahn2_overlap import (
    SITES,source_hourly,freeze_training_cells,
    original_ahn2_layer,source_tile)
from ahn2_destination_z_tide_prediction import (
    CLOCKS,SOURCE_YEARS,MIN_TRAIN,MIN_TEST,MIN_TEST_BIRDS,
    MIN_TEST_WEEKS,MIN_TEST_CELLS,
    triplets_with_past_motion,admission_rows,predict_z)
from original_heading_tide import unit_direction,vector,RIDGE,forecast
from tide_phase_yearago_placebo import percentile_interval
from tide_phase_yearago_placebo import percentile_interval

TRAIN_YEAR=2010
TEST_YEAR=2011

def attach_exact_next_heading(rows,original_hourly,clock_shift_s=0):
    if clock_shift_s not in CLOCKS:
        raise ValueError("Source native clock choice is not frozen")
    originals,source_exc=triplets_with_past_motion(original_hourly)
    mapping={}
    for original in originals:
        key=(original["bird"],original["B_time"].replace(tzinfo=timezone.utc)
             +timedelta(seconds=clock_shift_s))
        if key in mapping:raise ValueError("SOURCE_STOP_DUPLICATE_MIDDLE_GPS_KEY")
        b=(original["B_time"],original["B_lat"],original["B_lon"])
        c=(original["time"],original["lat"],original["lon"])
        direction=unit_direction(b,c)
        if direction is None:raise ValueError("SOURCE_STOP_UNEXPECTED_ZERO_NEXT_MOVEMENT")
        mapping[key]={
            "target_e":direction[0],"target_n":direction[1],
            "B_lat":original["B_lat"],"B_lon":original["B_lon"],
            "previous_e":original["previous_e"],
            "previous_n":original["previous_n"],
            "previous_speed_log":original["previous_speed_log"]}
    merged=[];matchedkeys=set()
    for row in rows:
        key=(row["id"],row["t"])
        if key in matchedkeys:raise ValueError("SOURCE_STOP_DUPLICATE_V48_ADMISSION_KEY")
        matchedkeys.add(key)
        source=mapping.get(key)
        if source is None:raise ValueError("SOURCE_STOP_V48_ROW_NOT_IN_ORIGINAL_GPS_TRIPLE")
        for k in ("lat","lon"):
            field="B_"+k
            if abs(row[k]-source[field])>1e-9:
                raise ValueError("SOURCE_STOP_B_POSITION_CHANGED")
        for k in ("previous_e","previous_n","previous_speed_log"):
            if abs(row[k]-source[k])>1e-9:
                raise ValueError("SOURCE_STOP_ORIGINAL_PREVIOUS_MOVE_DIFFERED")
        merged.append({**row,"target_e":source["target_e"],
                              "target_n":source["target_n"]})
    return merged,{
        "matched_original_B_to_C_heading_and_AHN2_C_destination_height":len(merged),
        "original_source_GPS_3fix_candidate_keys_before_AHN2_source_filter":len(mapping),
        "all_v48_source_rows_matched_exactly":len(merged)==len(rows),
        "next_C_position_and_target_altitude_not_used_as_features":True}

def joint_predict(train,test,model):
    if model not in ("M0","Mreal","Mghost"):
        raise ValueError("Unknown original tide model")
    level=0 if model=="M0" else 1
    def features(r):
        if model=="Mghost":return vector({**r,"phase":r["ghost_phase"]},1)
        return vector(r,level)
    x=np.asarray([features(r) for r in train],dtype=float)
    z=np.asarray([features(r) for r in test],dtype=float)
    y=np.asarray([[r["target_e"],r["target_n"],r["target_z_C_NAP_m"]]
                  for r in train])
    means=x[:,1:].mean(0);sd=x[:,1:].std(0)
    sd[sd<1e-9]=1
    x[:,1:]=(x[:,1:]-means)/sd
    z[:,1:]=(z[:,1:]-means)/sd
    counts=Counter(r["id"] for r in train)
    weights=np.asarray([1/counts[r["id"]] for r in train])
    weights*=len(train)/weights.sum()
    penalty=np.eye(x.shape[1])*RIDGE;penalty[0,0]=0
    coefficients=np.linalg.solve(x.T@(x*weights[:,None])+penalty,
                                 x.T@(weights[:,None]*y))
    pred=z@coefficients
    re_train=([{**r,"phase":r["ghost_phase"]} for r in train]
              if model=="Mghost" else train)
    re_test=([{**r,"phase":r["ghost_phase"]} for r in test]
             if model=="Mghost" else test)
    ref=forecast(re_train,re_test,level)
    if not np.allclose(pred[:,:2],ref,atol=1e-9,rtol=1e-9):
        raise ValueError("SOURCE_STOP_FROZEN_V41_DIRECTION_PREDICTIONS_NOT_REPLAYED")
    elev=predict_z(train,test,model)
    if not np.allclose(pred[:,2],elev,atol=1e-9,rtol=1e-9):
        raise ValueError("SOURCE_STOP_FROZEN_V48_ELEVATION_PREDICTIONS_NOT_REPLAYED")
    return pred

def relative_fractions(means):
    m=np.asarray(means,dtype=float)
    if m.shape[-1]!=4:raise ValueError("Same-source 4 loss means required")
    h0,h1,z0,z1=[m[...,i] for i in range(4)]
    if np.any(h0<=0) or np.any(z0<=0):
        raise ValueError("Nonpositive original baseline prediction loss")
    hskill=(h0-h1)/h0
    zskill=(z0-z1)/z0
    return np.stack((hskill,zskill,hskill-zskill),axis=-1)

def score(train,test,*,seed=20261105,bird_draws=10000,week_draws=4000):
    if {r["t"].year for r in train}!={TRAIN_YEAR} or {r["t"].year for r in test}!={TEST_YEAR}:
        raise ValueError("Original 2010 training and 2011 holdout source year required")
    bybird=defaultdict(list);byweek=defaultdict(list)
    for i,r in enumerate(test):
        bybird[r["id"]].append(i)
        byweek[r["t"].isocalendar()[:2]].append(i)
    ntiles=len({r["source_C_selected_tile"] for r in test})
    if (len(train)<MIN_TRAIN or len(test)<MIN_TEST or
        len(bybird)<MIN_TEST_BIRDS or len(byweek)<MIN_TEST_WEEKS or
        ntiles<MIN_TEST_CELLS):
        return {"admission":"NOT_ADMITTED_MATCHED_SOURCE_GPS_AHN2_TIDE",
                "train_rows":len(train),"test_rows":len(test),
                "test_birds":len(bybird),"test_weeks":len(byweek),
                "test_AHN2_source_cells":ntiles,
                "matched_axis_outcome":"NOT_ESTIMATED"}
    y=np.asarray([[r["target_e"],r["target_n"],r["target_z_C_NAP_m"]]
                  for r in test])
    predictions={m:joint_predict(train,test,m) for m in ("M0","Mreal","Mghost")}
    loss={}
    for model,pred in predictions.items():
        loss[model]={
            "direction":.5*np.square(y[:,:2]-pred[:,:2]).sum(axis=1),
            "altitude":np.square(y[:,2]-pred[:,2])}
    four=np.column_stack([
        loss["M0"]["direction"],loss["Mreal"]["direction"],
        loss["M0"]["altitude"],loss["Mreal"]["altitude"]])
    bird_losses=np.stack([four[idx].mean(0) for idx in bybird.values()])
    week_losses=[]
    for inds in byweek.values():
        present=defaultdict(list)
        for i in inds:present[test[i]["id"]].append(i)
        week_losses.append(np.mean([four[v].mean(0) for v in present.values()],axis=0))
    week_losses=np.asarray(week_losses)
    bird_means=bird_losses.mean(axis=0)
    week_means=week_losses.mean(axis=0)
    rng=np.random.default_rng(seed)
    bootbird=relative_fractions(
        bird_losses[rng.integers(len(bird_losses),
            size=(bird_draws,len(bird_losses)))].mean(1))
    bootweek=relative_fractions(
        week_losses[rng.integers(len(week_losses),
            size=(week_draws,len(week_losses)))].mean(1))
    skill_names=("direction_phase_fractional_MSE_reduction",
                 "destination_height_phase_fractional_MSE_reduction",
                 "direction_minus_destination_height_phase_relative_skill_gap")
    field={}
    birdind=relative_fractions(bird_losses)
    weekind=relative_fractions(week_losses)
    pointbird=relative_fractions(bird_means)
    pointweek=relative_fractions(week_means)
    for k,name in enumerate(skill_names):
        field[name]={
            "pooled_equal_bird_relative_gain":float(pointbird[k]),
            "pooled_equal_bird_paired_bootstrap95":
                np.quantile(bootbird[:,k],[.025,.975]).tolist(),
            "positive_test_birds":int(sum(birdind[:,k]>0)),
            "separate_equal_week_bird_relative_gain":float(pointweek[k]),
            "separate_equal_week_paired_bootstrap95":
                np.quantile(bootweek[:,k],[.025,.975]).tolist(),
            "positive_test_weeks":int(sum(weekind[:,k]>0))}
    # Negative-control real-phase vs year-ago gauge, on exact same terrain rows.
    ghost={}
    for j,axis in enumerate(("direction","altitude")):
        vals=loss["Mghost"][axis]-loss["Mreal"][axis]
        bird=[float(np.mean(vals[ix])) for ix in bybird.values()]
        ghost[axis]={
            "ghost_minus_real_pooled_equal_bird_loss_gain":
                float(np.mean(bird)),
            "original_bird_bootstrap95":
                percentile_interval(bird,bird_draws,seed+400+j),
            "n_birds_real_phase_better_than_ghost":int(sum(v>0 for v in bird))}
    return {
        "admission":"MATCHED_ORIGINAL_AHN2_C_VALID_GPS_DIRECTION_ELEVATION_TIDE_PREDICTION",
        "train_source_genuine_three_fix_rows":len(train),
        "test_source_genuine_three_fix_rows":len(test),
        "test_source_birds":len(bybird),
        "test_source_ISO_weeks":len(byweek),
        "test_original_2010_selected_AHN2_cells":ntiles,
        "exact_identical_source_GPS_C_height_and_heading_rows":True,
        "frozen_v41_direction_and_v48_elevation_predictors_replay":True,
        "observed_equal_bird_original_MSE":{
            "direction_half_unit_vector":[float(bird_means[0]),float(bird_means[1])],
            "destination_elevation_NAP_m2":[float(bird_means[2]),float(bird_means[3])]},
        "observed_equal_week_original_MSE":{
            "direction_half_unit_vector":[float(week_means[0]),float(week_means[1])],
            "destination_elevation_NAP_m2":[float(week_means[2]),float(week_means[3])]},
        "paired_original_relative_predictive_skill":field,
        "previous_year_tidal_phase_negative_controls":ghost,
        "no_actual_physical_wet_dry_front_or_social_Boids_effect":"NOT_ESTIMATED"}

def run(site,outfile):
    if site not in SITES:raise ValueError("Site not in frozen source universe")
    station={"schiermonnikoog":"schiermonnikoog.waddenzee",
             "ameland":"ameland.nes"}[site]
    gauges={};gauge_audit={}
    for year in (2009,2010,2011):
        tide,source=observed_rws_year(station,year)
        if source["gauge_rows"]<50000:raise ValueError("SOURCE_STOP_RWS_MEASURED_NAP_INSUFFICIENT")
        gauges[year]=tide
        gauge_audit[str(year)]={"original_WATHTE_NAP_measured_values":
                                source["gauge_rows"],"source_station":station}
    tracks={};gps={}
    with tempfile.TemporaryDirectory(prefix="boids_v49_source_") as temp:
        for year in (2010,2011):
            path=Path(temp)/f"{site}_{year}.csv.gz"
            manifest=(download_and_pin(year,path) if site=="schiermonnikoog"
                      else original_gps(year,path))
            track,audit=source_hourly(path,site,year)
            tracks[year]=track
            gps[str(year)]={"original_provider_MD5_verified":
                            manifest.get("provider_md5_match",manifest.get("provider_original_md5_matched")),
                            "original_source_SHA256":manifest["original_sha256"],
                            "original_hourly_source_QA":audit}
            path.unlink(missing_ok=True)
    selected,rank=freeze_training_cells(tracks[2010])
    cov,format_name=original_ahn2_layer()
    tiles={};tile_records=[]
    for rankidx,cell in enumerate(selected):
        try:
            z=source_tile(cell,cov,format_name)
            tiles[cell]=z
            tile_records.append({"rank":rankidx+1,"source_status":"AHN2_ORIGINAL_DTM_READ",
                                 "original_SHA256":z["original_source_patch_SHA256"],
                                 "valid_terrain_candidate_pixels":z["valid_NAP_candidate_pixels"]})
        except Exception as e:
            tiles[cell]=None
            tile_records.append({"rank":rankidx+1,"source_status":"SOURCE_STOP",
                                 "source_error":(type(e).__name__+"_"+str(e).splitlines()[0])[:160]})
    results={};admitted_source={}
    for offset in CLOCKS:
        one={}
        for year in (2010,2011):
            base,qa=admission_rows(tracks[year],tiles,selected,gauges[year],
                                   gauges[year-1],clock_shift_s=offset)
            matched,mqa=attach_exact_next_heading(base,tracks[year],offset)
            one[year]=matched
            admitted_source[f"{year}_clock_{offset}s"]={
                "v48_original_C_height_and_gauge_admission":qa,
                "original_next_heading_exact_source_match":mqa}
        results[f"original_GPS_clock_shift_{offset}s"]=score(one[2010],one[2011])
    report={"analysis":"V49_POSTRESULT_SAME_AHN2_C_VALID_GPS_TIDE_DIRECTION_AND_ALTITUDE",
            "site":site,"source":"authentic_Zenodo_GPS_RWS_NAP_and_AHN2_WCS",
            "test_year":2011,"training_year":2010,
            "original_GPS_manifest":gps,
            "original_RWS_measured_NAP_sources":gauge_audit,
            "original_AHN2_source_tiles":tile_records,
            "original_2010_training_tile_metadata":rank,
            "same_original_source_join_audit":admitted_source,
            "scenarios":results,
            "interpretation_boundary":"Post_v48_exploratory_predicative_not_3D_social_or_true_exposure_front"}
    Path(outfile).parent.mkdir(parents=True,exist_ok=True)
    Path(outfile).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=SITES,required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.site,a.output),sort_keys=True))
