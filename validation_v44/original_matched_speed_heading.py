"""v44 post-v43 exploratory paired speed vs heading on IDENTICAL original GPS triples.

Source/model contract frozen before opening any joint scores:
docs/V44_PREOUTCOME_MATCHED_EPISODE_TIDE_SPEED_DIRECTION.md.

Original v41 3-fix GPS rows and 2D target headings are accepted unchanged.
The next B->C speed target is attached from a second independent traversal
of the exact same original source GPS fixes, joined by (bird, original B time).
No source GPS IDs, coordinates, times or raw water values leave an Actions runner.
"""
from __future__ import annotations
import argparse,csv,gzip,json,math,tempfile
from collections import Counter,defaultdict
from datetime import timedelta,timezone
from pathlib import Path
import numpy as np

from source_preflight import download_and_pin,parse_stamp,haversine_m
from source_gate_2012 import get_ameland_original,REGIONS
from ameland_external_site import original_gps
from source_fetch_resilience import observed_rws_year
from heldout_2012_tidal_lag import original_2012_gauge
from original_heading_tide import (
    CLOCKS,SITES,ORIGINAL_FIELDS,MIN_DT_S,MAX_DT_S,MIN_KMPH,MAX_KMPH,RIDGE,
    original_three_fix_heading_episodes,unit_direction,vector,forecast as v41_forecast)

YEARS=(2010,2011,2012)
EVALUATIONS=((2010,2011),(2010,2012))
SOURCE_MIN_TRAIN=1000
SOURCE_MIN_TEST=1000
SOURCE_MIN_TEST_BIRDS=3
SOURCE_MIN_TEST_WEEKS=4

def attach_same_next_fix_speed(source_path, original_heading_rows, site, clock_shift_s):
    """Derive next GPS speed from exactly the same B->C original source fix.

    Critical source-invariant gate: every v41-qualified heading row must
    match the original B coordinate and original next B->C heading exactly.
    No re-sampling or dropping episodes after source admission.
    """
    if site not in SITES or clock_shift_s not in CLOCKS:
        raise ValueError("Unfrozen original source or GPS clock")
    original_seen=set();by_bird=defaultdict(dict)
    bounds=REGIONS[site]
    with gzip.open(source_path,"rt",encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        if not ORIGINAL_FIELDS<=set(reader.fieldnames or ()):
            raise ValueError("Original GPS schema mismatch during independent speed target match")
        for row in reader:
            eid=(row.get("event-id") or "").strip()
            if not eid or eid in original_seen:continue
            original_seen.add(eid)
            if row["visible"].strip().upper() in ("FALSE","0"):continue
            bird=(row.get("individual-local-identifier") or "").strip()
            if not bird:continue
            try:
                t=parse_stamp(row["timestamp"]).replace(tzinfo=timezone.utc)+timedelta(seconds=clock_shift_s)
                lat=float(row["location-lat"]);lon=float(row["location-long"])
            except (ValueError,TypeError):continue
            if not all(map(math.isfinite,[lat,lon])):continue
            if not(bounds[0]<=lat<=bounds[1] and bounds[2]<=lon<=bounds[3]):continue
            hour=t.replace(minute=0,second=0,microsecond=0)
            old=by_bird[bird].get(hour)
            if old is None or t<old[0]:by_bird[bird][hour]=(t,lat,lon)
    original_next={}
    for bird,bin_map in by_bird.items():
        fixes=sorted(bin_map.values())
        for b,c in zip(fixes,fixes[1:]):
            dt=(c[0]-b[0]).total_seconds()
            if not MIN_DT_S<=dt<=MAX_DT_S:continue
            kmph=haversine_m((None,b[1],b[2]),(None,c[1],c[2]))*3.6/dt
            if not MIN_KMPH<=kmph<=MAX_KMPH:continue
            direction=unit_direction(b,c)
            if direction is None:continue
            key=(bird,b[0])
            if key in original_next:
                raise ValueError("SOURCE_STOP_DUPLICATE_B_FIX_BIRD_CLOCK")
            original_next[key]=(b[1],b[2],kmph,direction)
    matched=[];keys=set()
    for record in original_heading_rows:
        key=(record["id"],record["t"])
        if key in keys:raise ValueError("SOURCE_STOP_DUPLICATE_V41_HEADING_KEY")
        keys.add(key)
        item=original_next.get(key)
        if item is None:
            raise ValueError("SOURCE_STOP_V41_DIRECTION_MISSING_IN_INDEPENDENT_ORIGINAL_SPEED")
        lat,lon,speed,direction=item
        if abs(lat-record["lat"])>1e-9 or abs(lon-record["lon"])>1e-9:
            raise ValueError("SOURCE_STOP_ORIGINAL_MIDDLE_POSITION_DOES_NOT_MATCH")
        if (abs(direction[0]-record["target_e"])>1e-9 or
            abs(direction[1]-record["target_n"])>1e-9):
            raise ValueError("SOURCE_STOP_ORIGINAL_NEXT_HEADING_DOES_NOT_MATCH")
        matched.append({**record,"target_speed_log":math.log1p(speed)})
    if len(matched)!=len(original_heading_rows):
        raise ValueError("SOURCE_STOP_DIFFERENT_ORIGINAL_GPS_EPISODE_COHORT")
    return matched,{"v41_source_heading_episodes":len(original_heading_rows),
                    "original_next_displacement_speed_targets_matched":len(matched),
                    "exact_same_middle_original_GPS_fix":True,
                    "exact_same_B_to_C_source_heading_verified":True,
                    "no_new_speed_outcome_sampling_filter":True}

def joint_predict(train,test,level):
    """Exactly v41 feature/weight/ridge design, simultaneously 3 targets.

    Returns [log1p(next km/h), unit heading east, unit heading north].
    No future target enters v41.vector features.
    """
    if not train or not test:raise ValueError("Missing original source episodes")
    x=np.asarray([vector(r,level) for r in train],dtype=float)
    z=np.asarray([vector(r,level) for r in test],dtype=float)
    y=np.asarray([[r["target_speed_log"],r["target_e"],r["target_n"]]
                  for r in train],dtype=float)
    center=x[:,1:].mean(0);sd=x[:,1:].std(0)
    sd[sd<1e-9]=1
    x[:,1:]=(x[:,1:]-center)/sd
    z[:,1:]=(z[:,1:]-center)/sd
    counts=Counter(r["id"] for r in train)
    weight=np.asarray([1/counts[r["id"]] for r in train],dtype=float)
    weight*=len(train)/weight.sum()
    penalty=np.eye(x.shape[1])*RIDGE
    penalty[0,0]=0.
    betas=np.linalg.solve(x.T@(x*weight[:,None])+penalty,
                          x.T@(weight[:,None]*y))
    predictions=z@betas
    if not np.allclose(predictions[:,1:],v41_forecast(train,test,level),
                       rtol=1e-9,atol=1e-9):
        raise AssertionError("SOURCE_STOP_DIRECTIONAL_REPLAY_DIVERGED_FROM_FROZEN_V41")
    return predictions

def mean_ratio_summary(four_loss_means):
    """Relative MSE improvement and paired dimensionless gap for 4 loss cells."""
    a=np.asarray(four_loss_means,dtype=float)
    if a.shape[-1]!=4:raise ValueError("Four original same-episode losses required")
    speed0,speed1,head0,head1=[a[...,i] for i in range(4)]
    if np.any(speed0<=0) or np.any(head0<=0):
        raise ValueError("Nonpositive baseline source MSE")
    speed=(speed0-speed1)/speed0
    direction=(head0-head1)/head0
    return np.stack((speed,direction,direction-speed),axis=-1)

def grouped_score(train,test,*,year,bird_draws=10000,week_draws=4000,seed=20261105):
    """Bootstrap paired FOUR errors at whole-bird and whole-week units."""
    if year not in (2011,2012):
        raise ValueError("Only frozen historic temporal holdout years")
    for r in test:
        if r["t"].year!=year:
            raise ValueError("Test original year must not include other data")
    allowed_train={2011:{2010},2012:{2010,2011}}[year]
    if {r["t"].year for r in train}!=allowed_train:
        raise ValueError("Unfrozen training calendar years")
    birds=defaultdict(list);weeks=defaultdict(list)
    for i,r in enumerate(test):
        birds[r["id"]].append(i)
        weeks[r["t"].isocalendar()[:2]].append(i)
    if (len(train)<SOURCE_MIN_TRAIN or len(test)<SOURCE_MIN_TEST or
        len(birds)<SOURCE_MIN_TEST_BIRDS or len(weeks)<SOURCE_MIN_TEST_WEEKS):
        return {"admission":"NOT_ADMITTED_INSUFFICIENT_MATCHED_ORIGINAL_THREE_FIX_SOURCE",
                "training_original_episodes":len(train),
                "test_original_episodes":len(test),
                "test_birds":len(birds),"test_weeks":len(weeks),
                "speed_or_heading_delta": "NOT_ESTIMATED"}
    pr0=joint_predict(train,test,0)
    pr1=joint_predict(train,test,1)
    y=np.array([[r["target_speed_log"],r["target_e"],r["target_n"]]
                for r in test],dtype=float)
    errors=np.column_stack([
        np.square(y[:,0]-pr0[:,0]),
        np.square(y[:,0]-pr1[:,0]),
        .5*np.square(y[:,1:]-pr0[:,1:]).sum(axis=1),
        .5*np.square(y[:,1:]-pr1[:,1:]).sum(axis=1)])
    # Each bird contributes exactly one mean row in each original endpoint.
    per_bird=np.stack([errors[ix].mean(axis=0) for ix in birds.values()])
    per_week=[]
    for ix in weeks.values():
        present=defaultdict(list)
        for i in ix:present[test[i]["id"]].append(i)
        per_week.append(np.mean([errors[ii].mean(axis=0)
                                 for ii in present.values()],axis=0))
    per_week=np.asarray(per_week,dtype=float)
    pooled_bird=per_bird.mean(axis=0)
    pooled_week=per_week.mean(axis=0)
    point_bird=mean_ratio_summary(pooled_bird)
    point_week=mean_ratio_summary(pooled_week)
    rng=np.random.default_rng(seed)
    bird_index=rng.integers(len(per_bird),size=(bird_draws,len(per_bird)))
    week_index=rng.integers(len(per_week),size=(week_draws,len(per_week)))
    bird_boot=mean_ratio_summary(per_bird[bird_index].mean(axis=1))
    week_boot=mean_ratio_summary(per_week[week_index].mean(axis=1))
    labels=("speed_fractional_MSE_reduction",
            "direction_fractional_MSE_reduction",
            "direction_minus_speed_fractional_reduction")
    summaries={}
    per_bird_skill=mean_ratio_summary(per_bird)
    per_week_skill=mean_ratio_summary(per_week)
    for i,name in enumerate(labels):
        summaries[name]={
            "pooled_equal_bird_fractional_gain":float(point_bird[i]),
            "pooled_equal_bird_paired_bootstrap95":np.quantile(bird_boot[:,i],[.025,.975]).tolist(),
            "separate_equal_week_bird_fractional_gain":float(point_week[i]),
            "separate_equal_week_paired_bootstrap95":np.quantile(week_boot[:,i],[.025,.975]).tolist(),
            "positive_individual_birds":int(sum(per_bird_skill[:,i]>0)),
            "positive_test_weeks":int(sum(per_week_skill[:,i]>0))}
    return {"admission":"OBSERVED_MATCHED_EPISODE_PREDICTIVE_COMPARISON_EXPLORATORY",
            "fit_years":sorted(allowed_train),"heldout_year":year,
            "training_genuine_three_fix_episodes":len(train),
            "test_genuine_three_fix_episodes":len(test),
            "n_test_birds":len(birds),"n_test_ISO_weeks":len(weeks),
            "same_original_test_rows_for_both_axes":True,
            "source_features_identical_for_both_axes":True,
            "v41_heading_forecast_replayed_exactly":True,
            "M0_M1_equal_bird_loss":{
                "speed_log1p_kmph_MSE":[float(pooled_bird[0]),float(pooled_bird[1])],
                "direction_half_unit_vector_MSE":[float(pooled_bird[2]),float(pooled_bird[3])]},
            "M0_M1_equal_week_loss":{
                "speed_log1p_kmph_MSE":[float(pooled_week[0]),float(pooled_week[1])],
                "direction_half_unit_vector_MSE":[float(pooled_week[2]),float(pooled_week[3])]},
            "paired_relative_skill_comparisons":summaries,
            "no_raw_gps_location_or_animal_ids_exported":True,
            "causal_tidal_front_or_boids_force":"NOT_IDENTIFIED"}

def run(site,out):
    if site not in SITES:raise ValueError("Unfrozen original island")
    gauge_station={"schiermonnikoog":"schiermonnikoog.waddenzee",
                   "ameland":"ameland.nes"}[site]
    data={clock:{} for clock in CLOCKS}
    receipt={}
    with tempfile.TemporaryDirectory(prefix="boids_v44_original_gps_") as folder:
        for year in YEARS:
            path=Path(folder)/f"{site}_{year}_original.csv.gz"
            if site=="schiermonnikoog":
                manifest=download_and_pin(year,path)
            else:
                manifest=get_ameland_original(path) if year==2012 else original_gps(year,path)
            tide,gauge=(original_2012_gauge(gauge_station) if year==2012
                        else observed_rws_year(gauge_station,year))
            if gauge["gauge_rows"]<50000:
                raise ValueError("SOURCE_STOP_RWS_ORIGINAL_GAUGE_INCOMPLETE")
            this={"original_GPS_provider_MD5_match":
                    manifest.get("provider_md5_match",manifest.get("provider_original_md5_matched")),
                  "original_GPS_compressed_SHA256":manifest["original_sha256"],
                  "RWS_original_measured_NAP_count":gauge["gauge_rows"],
                  "RWS_original_station":gauge_station}
            for clock in CLOCKS:
                heading,audit=original_three_fix_heading_episodes(path,tide,site,clock)
                attached,matched=attach_same_next_fix_speed(path,heading,site,clock)
                data[clock][year]=attached
                this[f"native_clock_shift_{clock}s"]={
                    "v41_existing_heading_source":audit,
                    "matched_original_future_speed_and_heading":matched}
            receipt[str(year)]=this
            path.unlink(missing_ok=True)
    outcomes={}
    for clock in CLOCKS:
        train2010=data[clock][2010]
        trainboth=data[clock][2010]+data[clock][2011]
        outcomes[f"native_clock_shift_{clock}s"]={
            "train_2010_test_2011":grouped_score(train2010,data[clock][2011],year=2011),
            "train_2010_2011_test_2012":grouped_score(trainboth,data[clock][2012],year=2012)}
    report={"analysis":"V44_POSTRESULT_SAME_GPS_TRIPLE_SPEED_DIRECTION_TIDE",
            "source":"original_Zenodo_GPS_MD5_and_RWS_measured_WATHTE_NAP",
            "site":site,"study_years":[2010,2011,2012],
            "source_receipts":receipt,
            "scenarios":outcomes,
            "source_clock":"NATIVE_ORIGINAL_UTC_OR_GPS_TIME_UNRESOLVED",
            "v44_outcome":"POST_v41_v43_EXPLORATORY_SAME_ANIMALS",
            "interpretation":"Same-row dimensionless predictive relative-skill contrast, NOT causal axis preference"}
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=SITES,required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    print(json.dumps(run(args.site,args.output),sort_keys=True))
