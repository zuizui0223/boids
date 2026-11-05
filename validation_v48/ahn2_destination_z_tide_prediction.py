"""v48: authentic destination z_C from AHN2 vs true and year-ago RWS tide phase.

Post-v47 ORIGINAL SOURCE science: B height not admitted, so no B->C elevation
change or exposure-front tracking. The target is independent AHN2 elevation
at original next GPS destination C, NOT a water-level-derived wet/dry label.
"""
from __future__ import annotations
import argparse,json,math,tempfile
from collections import Counter,defaultdict
from datetime import timedelta,timezone
from pathlib import Path
import numpy as np

from source_preflight import download_and_pin,haversine_m
from source_gate_2012 import get_ameland_original
from ameland_external_site import original_gps
from source_fetch_resilience import observed_rws_year
from source_original_gps_ahn2_overlap import (
    SITES,source_hourly,source_triples,source_destination_support,
    freeze_training_cells,original_ahn2_layer,source_tile)
from ahn2_both_original_endpoints_source import height_from_original_tile
from original_heading_tide import unit_direction,vector,RIDGE
from tide_phase_yearago_placebo import percentile_interval

SOURCE_YEARS=(2010,2011)
TRAIN_YEAR=2010
TEST_YEAR=2011
CLOCKS=(0,-15)
MIN_TRAIN=400
MIN_TEST=500
MIN_TEST_BIRDS=3
MIN_TEST_WEEKS=4
MIN_TEST_CELLS=2
TIDE_PHASE_SLOPE_THRESHOLD=.012
PREVIOUS_GAUGE_DAYS=365

def triplets_with_past_motion(hourly):
    """Identical v46 source A,B,C sample, attach source past direction/speed."""
    out=[];excluded=Counter()
    for bird,fixes in hourly.items():
        for a,b,c in zip(fixes,fixes[1:],fixes[2:]):
            dt1=(b[0]-a[0]).total_seconds()
            dt2=(c[0]-b[0]).total_seconds()
            if not (1800<=dt1<=7200 and 1800<=dt2<=7200):
                excluded["source_time_gap"]+=1;continue
            speed1=haversine_m((None,a[1],a[2]),(None,b[1],b[2]))*3.6/dt1
            speed2=haversine_m((None,b[1],b[2]),(None,c[1],c[2]))*3.6/dt2
            if not(.4<=speed1<=120 and .4<=speed2<=120):
                excluded["source_stationary_or_outlier"]+=1;continue
            prev=unit_direction(a,b)
            if prev is None:raise ValueError("Original nonstationary A->B heading not defined")
            out.append({
                "bird":bird,"time":c[0],"lat":c[1],"lon":c[2],
                "B_time":b[0],"B_lat":b[1],"B_lon":b[2],
                "previous_e":prev[0],"previous_n":prev[1],
                "previous_speed_log":math.log1p(speed1)})
    return out,dict(excluded)

def admission_rows(hourly,tiles,chosen,tide,yearago_tide,clock_shift_s=0):
    if clock_shift_s not in CLOCKS:
        raise ValueError("Unfrozen original source GPS clock")
    original_C,orig_exc=source_triples(hourly)
    sampled,exc=triplets_with_past_motion(hourly)
    if exc!=orig_exc or len(sampled)!=len(original_C):
        raise ValueError("SOURCE_STOP_V46_SAME_ORIGINAL_C_COHORT_NOT_REPLAYED")
    for a,b in zip(sampled,original_C):
        if any(a[k]!=b[k] for k in ("bird","time","lat","lon")):
            raise ValueError("SOURCE_STOP_ORIGINAL_C_GPS_FIX_CHANGED")
    previous_C=source_destination_support(original_C,tiles,chosen)
    count_C=0;missing=Counter();eligible=[]
    original_C_height_tally=defaultdict(int)
    for item in sampled:
        location=height_from_original_tile(item["lat"],item["lon"],
                                           set(chosen),tiles)
        if location["status"]!="ORIGINAL_AHN2_NAP_HEIGHT_CANDIDATE":
            missing["C_original_AHN2_source_not_valid"]+=1;continue
        count_C+=1
        original_C_height_tally[location["cell"]]+=1
        when=item["B_time"].replace(tzinfo=timezone.utc)+timedelta(seconds=clock_shift_s)
        try:
            height,phase,_=tide.at_with_phase(
                when,tolerance_m_per_hour=TIDE_PHASE_SLOPE_THRESHOLD)
            _,ghost,_=yearago_tide.at_with_phase(
                when-timedelta(days=PREVIOUS_GAUGE_DAYS),
                tolerance_m_per_hour=TIDE_PHASE_SLOPE_THRESHOLD)
        except ValueError:
            missing["RWS_source_phase_missing_or_gap"]+=1;continue
        if phase==0:
            missing["true_source_phase_slack"]+=1;continue
        hour=when.hour+when.minute/60+when.second/3600
        day=when.timetuple().tm_yday
        z=location["z"]
        eligible.append({
            "id":item["bird"],"t":when,
            "lat":item["B_lat"],"lon":item["B_lon"],
            "clocksin":math.sin(2*math.pi*hour/24),
            "clockcos":math.cos(2*math.pi*hour/24),
            "yearsin":math.sin(2*math.pi*day/365.25),
            "yearcos":math.cos(2*math.pi*day/365.25),
            "previous_e":item["previous_e"],
            "previous_n":item["previous_n"],
            "previous_speed_log":item["previous_speed_log"],
            "h":height,"phase":int(phase),"ghost_phase":int(ghost),
            "target_z_C_NAP_m":float(z),
            "source_C_selected_tile":location["cell"]})
    if count_C!=previous_C["n_original_C_with_valid_AHN2_height"]:
        raise ValueError("SOURCE_STOP_V46_SOURCE_C_ONLY_COUNT_MISMATCH")
    audit={"original_source_three_fix_candidates":len(original_C),
           "independent_v46_C_only_height_support_replayed":True,
           "original_C_source_valid_heights_before_tide_join":count_C,
           "source_height_valid_and_actual_and_ghost_phase_rows":len(eligible),
           "source_valid_C_original_cells_before_tide":len(original_C_height_tally),
           "eligible_source_test_birds":len({r["id"] for r in eligible}),
           "eligible_ISO_weeks":len({r["t"].isocalendar()[:2] for r in eligible}),
           "eligible_2010_only_selected_tile_count":
               len({r["source_C_selected_tile"] for r in eligible}),
           "source_missing_reason_counts":dict(missing),
           "target_source_is_original_AHN2_DTM_z_C_not_function_of_RWS":True,
           "any_original_B_height_imputed":False}
    return eligible,audit

def predict_z(train,test,model):
    """Uses exactly v41's baseline and tide-phase columns, with z_C target."""
    if model not in ("M0","Mreal","Mghost"):
        raise ValueError("Unknown source-frozen elevation model")
    def xrow(r):
        if model=="M0":return vector(r,0)
        if model=="Mreal":return vector(r,1)
        # Previous-year original measured gauge phase only; true h(B) fixed.
        return vector({**r,"phase":r["ghost_phase"]},1)
    x=np.asarray([xrow(r) for r in train],dtype=float)
    z=np.asarray([xrow(r) for r in test],dtype=float)
    y=np.asarray([r["target_z_C_NAP_m"] for r in train],dtype=float)
    centre=x[:,1:].mean(axis=0);sd=x[:,1:].std(axis=0)
    sd[sd<1e-9]=1
    x[:,1:]=(x[:,1:]-centre)/sd
    z[:,1:]=(z[:,1:]-centre)/sd
    total=Counter(r["id"] for r in train)
    w=np.asarray([1/total[r["id"]] for r in train],dtype=float)
    w*=len(train)/w.sum()
    penalty=np.eye(x.shape[1])*RIDGE
    penalty[0,0]=0
    coefs=np.linalg.solve(x.T@(x*w[:,None])+penalty,x.T@(w*y))
    return z@coefs

def score(train,test,*,seed=20261105,bird_draws=10000,week_draws=4000):
    if {r["t"].year for r in train}!={TRAIN_YEAR}:
        raise ValueError("Train must be source year 2010 only")
    if {r["t"].year for r in test}!={TEST_YEAR}:
        raise ValueError("Test must be source year 2011 only")
    bybird=defaultdict(list);byweek=defaultdict(list)
    for i,r in enumerate(test):
        bybird[r["id"]].append(i)
        byweek[r["t"].isocalendar()[:2]].append(i)
    ntile=len({r["source_C_selected_tile"] for r in test})
    if (len(train)<MIN_TRAIN or len(test)<MIN_TEST or
        len(bybird)<MIN_TEST_BIRDS or len(byweek)<MIN_TEST_WEEKS or
        ntile<MIN_TEST_CELLS):
        return {"admission":"NOT_ADMITTED_DESTINATION_TERRAIN_OR_TIDE_SOURCE",
                "train_rows":len(train),"test_rows":len(test),
                "test_birds":len(bybird),"test_weeks":len(byweek),
                "test_source_AHN2_cells":ntile,
                "test_outcome":"NOT_ESTIMATED"}
    target=np.asarray([r["target_z_C_NAP_m"] for r in test])
    loss={k:(target-predict_z(train,test,k))**2 for k in
          ("M0","Mreal","Mghost")}
    mse={k:float(np.mean([np.mean(e[ix]) for ix in bybird.values()]))
         for k,e in loss.items()}
    pairs={"M0_minus_Mreal":("M0","Mreal"),
           "Mghost_minus_Mreal":("Mghost","Mreal"),
           "M0_minus_Mghost":("M0","Mghost")}
    contrasts={}
    for j,(name,(first,second)) in enumerate(pairs.items()):
        delta=loss[first]-loss[second]
        bird=[float(np.mean(delta[ix])) for ix in bybird.values()]
        week=[]
        for inds in byweek.values():
            local=defaultdict(list)
            for i in inds:local[test[i]["id"]].append(i)
            week.append(float(np.mean([np.mean(delta[v]) for v in local.values()])))
        contrasts[name]={
            "pooled_equal_bird_MSE_gain_NAP_m2":float(np.mean(bird)),
            "pooled_equal_bird_95CI_NAP_m2":
                percentile_interval(bird,bird_draws,seed+j),
            "n_birds_positive":int(sum(v>0 for v in bird)),
            "separate_equal_week_then_bird_MSE_gain_NAP_m2":
                float(np.mean(week)),
            "separate_equal_week_95CI_NAP_m2":
                percentile_interval(week,week_draws,seed+j+100),
            "n_weeks_positive":int(sum(v>0 for v in week))}
    return {"admission":"OBSERVED_ORIGINAL_NEXT_DESTINATION_AHN2_ELEVATION_TIDE_PREDICTION",
            "train_rows":len(train),"test_rows":len(test),
            "test_birds":len(bybird),"test_weeks":len(byweek),
            "test_source_AHN2_cells":ntile,
            "original_true_AHN2_destination_z_C_not_tide_defined":True,
            "MSE_pooled_equal_bird_NAP_m2":mse,
            "contrasts":contrasts,
            "original_B_and_C_height_delta":"NOT_ESTIMATED",
            "tidal_exposure_front_causality":"NOT_IDENTIFIED"}

def run(site,outfile):
    if site not in SITES:raise ValueError("Site not from original GPS cohorts")
    station={"schiermonnikoog":"schiermonnikoog.waddenzee",
             "ameland":"ameland.nes"}[site]
    # The previous-year source is authentic 2009 water only (no 2009 GPS here).
    water={}
    water_receipts={}
    for year in (2009,2010,2011):
        obj,source=observed_rws_year(station,year)
        if source["gauge_rows"]<50000:
            raise ValueError("SOURCE_STOP_INCOMPLETE_RWS_ORIGINAL_WATER_YEAR")
        water[year]=obj
        water_receipts[str(year)]={
            "original_measured_WATHTE_NAP_observations":source["gauge_rows"],
            "original_source_station":station}
    original_tracks={}
    gps_receipts={}
    with tempfile.TemporaryDirectory(prefix="v48_AHN2_original_") as temp:
        for year in SOURCE_YEARS:
            path=Path(temp)/f"{site}_{year}_original.csv.gz"
            source=(download_and_pin(year,path) if site=="schiermonnikoog"
                    else original_gps(year,path))
            hourly,admission=source_hourly(path,site,year)
            original_tracks[year]=hourly
            gps_receipts[str(year)]={
                "original_MD5_verified":source.get(
                    "provider_md5_match",source.get("provider_original_md5_matched")),
                "original_SHA256":source["original_sha256"],
                "original_source_fix_QA":admission}
            path.unlink(missing_ok=True)
    chosen,rank=freeze_training_cells(original_tracks[2010])
    layer,format_name=original_ahn2_layer()
    tiles={};patches=[]
    for rank_idx,cell in enumerate(chosen):
        try:
            source=source_tile(cell,layer,format_name)
            tiles[cell]=source
            patches.append({"rank":rank_idx+1,
                            "original_source_SHA256":source["original_source_patch_SHA256"],
                            "original_valid_candidate_pixels":source["valid_NAP_candidate_pixels"],
                            "original_broad_tide_candidate_pixels":source["candidate_minus3_plus3_NAP_pixels"],
                            "source_status":"SOURCE_VALID"})
        except Exception as error:
            tiles[cell]=None
            patches.append({"rank":rank_idx+1,"source_status":"SOURCE_STOP",
                            "reason":(type(error).__name__+"_"+str(error).splitlines()[0])[:140]})
    byclock={}
    diagnostics={}
    for clock in CLOCKS:
        train,train_audit=admission_rows(original_tracks[2010],tiles,chosen,water[2010],water[2009],clock)
        test,test_audit=admission_rows(original_tracks[2011],tiles,chosen,water[2011],water[2010],clock)
        byclock[f"original_GPS_clock_shift_{clock}s"]=score(train,test)
        diagnostics[f"clock_{clock}s_source_admission"]={
            "train_2010":train_audit,"test_2011":test_audit}
    result={"analysis":"V48_ORIGINAL_AHN2_NEXT_DESTINATION_ELEVATION_VS_REAL_YEARAGO_TIDE",
            "site":site,"source":"provider_verified_original_GPS_RWS_NAP_AHN2_WCS",
            "train_year":2010,"test_year":2011,
            "fixed_original_2010_selected_AHN2_tile_rank":rank,
            "AHN2_original_tile_QA":patches,
            "GPS_provider_original_source_receipts":gps_receipts,
            "RWS_original_source_receipts":water_receipts,
            "original_source_admission":diagnostics,
            "model_outcomes":byclock,
            "claim_boundaries":["post_v44_exploratory_original_species_and_sites",
                "source_GPS_UTC_or_GPS_time_unresolved",
                "source_AHN2_first_height_band_and_second_mask_semantics_unverified",
                "not_an_exposed_flat_or_physical_front_measure",
                "z_C_AHN2_height_is_independent_of_RWS_water_level"]}
    Path(outfile).parent.mkdir(parents=True,exist_ok=True)
    Path(outfile).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=SITES,required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.site,a.output),sort_keys=True))
