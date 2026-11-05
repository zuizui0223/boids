"""v50: v43 FULL original 2010-trained tide-phase heading forecast partitioned by 2011 AHN2 source observability.

No model fit or feature is conditioned on 2011 group label. All original GPS
source positions and tag identities stay in-memory only, only aggregates saved.
Original v43 whole cohort source/metric replay is MANDATORY before new subgroup
claims. Source mask is NOT verified water or actual moving front.
"""
from __future__ import annotations

import argparse,json,math,tempfile
from collections import defaultdict
from datetime import timezone
from pathlib import Path

import numpy as np

from source_preflight import download_and_pin
from ameland_external_site import original_gps
from source_fetch_resilience import observed_rws_year
from original_heading_tide import (
    original_three_fix_heading_episodes,forecast,unit_direction,SITES)
from source_original_gps_ahn2_overlap import (
    source_hourly,freeze_training_cells,original_ahn2_layer,source_tile)
from ahn2_destination_z_tide_prediction import triplets_with_past_motion
from ahn2_both_original_endpoints_source import height_from_original_tile
from tide_phase_yearago_placebo import percentile_interval

TRAIN_YEAR=2010
TEST_YEAR=2011
CLOCK_SHIFT_SECONDS=0
GROUPS=("C_AHN2_VALID","C_SELECTED_CELL_AHN2_MISSING",
        "C_OUTSIDE_2010_SELECTED_CELLS")
GROUP_MIN_ROWS=200
GROUP_MIN_BIRDS=3
GROUP_MIN_WEEKS=4
MIN_WITHIN_BIRD_EPISODES_EACH=5
MIN_SAME_BIRDS=3
REF_V43={
    "schiermonnikoog":{"n_test":4948,"n_birds":13,
                        "M0":0.4491437063035975,
                        "M1":0.41370693859833235,
                        "C_height":1009},
    "ameland":{"n_test":4678,"n_birds":5,
                "M0":0.5107931836556263,
                "M1":0.43464618382116776,
                "C_height":1238},
}

def exact_original_C_for_v41_rows(source_2011_original_hourly,v41_test):
    # Independent original source reads do not change cohort. The v41 rows
    # are a subset solely due source gauge/slack admission, not masked terrain.
    all_original,excluded=triplets_with_past_motion(source_2011_original_hourly)
    lookup={}
    for x in all_original:
        key=(x["bird"],x["B_time"].replace(tzinfo=timezone.utc))
        if key in lookup:raise ValueError("SOURCE_STOP_DUPLICATE_ORIGINAL_B_GPS_KEY")
        lookup[key]=x
    out=[]
    used=set()
    for row in v41_test:
        key=(row["id"],row["t"])
        if key in used:raise ValueError("SOURCE_STOP_DUPLICATE_V41_ROW")
        used.add(key)
        x=lookup.get(key)
        if x is None:raise ValueError("SOURCE_STOP_V41_ROW_NOT_IN_ORIGINAL_GPS")
        if abs(x["B_lat"]-row["lat"])>1e-9 or abs(x["B_lon"]-row["lon"])>1e-9:
            raise ValueError("SOURCE_STOP_CHANGED_GPS_B_POSITION")
        for f in ("previous_e","previous_n","previous_speed_log"):
            if abs(x[f]-row[f])>1e-9:
                raise ValueError("SOURCE_STOP_CHANGED_OWN_PAST_MOTION")
        b=(x["B_time"],x["B_lat"],x["B_lon"])
        c=(x["time"],x["lat"],x["lon"])
        nextdir=unit_direction(b,c)
        if nextdir is None or any(abs(a-b)>1e-9 for a,b in
                                  zip(nextdir,(row["target_e"],row["target_n"]))):
            raise ValueError("SOURCE_STOP_CHANGED_ORIGINAL_NEXT_GPS_HEADING")
        out.append({"bird":row["id"],"time":row["t"],
                    "lat_C":x["lat"],"lon_C":x["lon"]})
    return out,{"source_original_three_fix_destination_candidate_count":len(lookup),
                "whole_original_v41_test_episodes_exact_C_gps_matched":len(out),
                "no_future_C_coordinates_in_v41_model_features":True}

def classify_original_C_source(row,selected,tiles):
    elevation=height_from_original_tile(row["lat_C"],row["lon_C"],set(selected),tiles)
    status=elevation["status"]
    if status=="ORIGINAL_AHN2_NAP_HEIGHT_CANDIDATE":
        return GROUPS[0]
    if status=="OUTSIDE_ORIGINAL_2010_SELECTED_TILES":
        return GROUPS[2]
    return GROUPS[1]

def same_fit_errors(train,test,site):
    if site not in REF_V43:raise ValueError("Unfrozen source site")
    truth=np.asarray([[r["target_e"],r["target_n"]] for r in test])
    p0=forecast(train,test,0)
    p1=forecast(train,test,1)
    e0=.5*np.square(truth-p0).sum(axis=1)
    e1=.5*np.square(truth-p1).sum(axis=1)
    birds=defaultdict(list)
    for i,r in enumerate(test):birds[r["id"]].append(i)
    mse0=float(np.mean([np.mean(e0[ix]) for ix in birds.values()]))
    mse1=float(np.mean([np.mean(e1[ix]) for ix in birds.values()]))
    ref=REF_V43[site]
    if len(test)!=ref["n_test"] or len(birds)!=ref["n_birds"] or (
        abs(mse0-ref["M0"])>1e-9 or abs(mse1-ref["M1"])>1e-9):
        raise ValueError("SOURCE_STOP_ORIGINAL_V43_FULL_FIELD_PREDICTOR_NOT_REPLAYED")
    return e0,e1,{
        "original_v43_full_test_n":len(test),
        "original_v43_full_test_birds":len(birds),
        "original_v43_M0_pooled_equal_bird_MSE":mse0,
        "original_v43_M1_pooled_equal_bird_MSE":mse1,
        "original_v43_full_model_source_replay_exact":True}

def skill_pair(losses):
    a=np.asarray(losses,dtype=float)
    if a.shape[-1]!=2:raise ValueError("Expected M0 M1 direction losses")
    if np.any(a[...,0]<=0):raise ValueError("Non-positive M0 baseline")
    return (a[...,0]-a[...,1])/a[...,0]

def group_score(test,errors0,errors1,labels,label,*,seed=20261105,
                bird_draws=10000,week_draws=4000):
    ix=[i for i,g in enumerate(labels) if g==label]
    bird=defaultdict(list);week=defaultdict(list)
    for i in ix:
        bird[test[i]["id"]].append(i)
        week[test[i]["t"].isocalendar()[:2]].append(i)
    if len(ix)<GROUP_MIN_ROWS or len(bird)<GROUP_MIN_BIRDS or len(week)<GROUP_MIN_WEEKS:
        return {"admission":"NOT_ADMITTED_INSUFFICIENT_SOURCE_GROUP",
                "source_group":label,"test_original_rows":len(ix),
                "test_source_birds":len(bird),"test_ISO_weeks":len(week)}
    b=np.array([[np.mean(errors0[rows]),np.mean(errors1[rows])]
                for rows in bird.values()])
    w=[]
    for rows in week.values():
        gb=defaultdict(list)
        for i in rows:gb[test[i]["id"]].append(i)
        w.append(np.mean([[np.mean(errors0[x]),np.mean(errors1[x])]
                          for x in gb.values()],axis=0))
    w=np.asarray(w,dtype=float)
    rng=np.random.default_rng(seed)
    bootb=skill_pair(b[rng.integers(len(b),size=(bird_draws,len(b)))].mean(1))
    bootw=skill_pair(w[rng.integers(len(w),size=(week_draws,len(w)))].mean(1))
    return {"admission":"ORIGINAL_GPS_PREDICTION_GROUP_DESCRIPTIVE",
            "source_group":label,
            "test_original_rows":len(ix),
            "test_source_birds":len(bird),
            "test_ISO_weeks":len(week),
            "M0_M1_pooled_equal_bird_heading_MSE":b.mean(0).tolist(),
            "source_group_pooled_equal_bird_relative_gain":float(skill_pair(b.mean(0))),
            "source_group_whole_bird_bootstrap95":
                np.quantile(bootb,[.025,.975]).tolist(),
            "n_birds_positive_gain":int(sum(b[:,0]>b[:,1])),
            "separate_equal_week_then_bird_heading_MSE":w.mean(0).tolist(),
            "separate_equal_week_then_bird_relative_gain":float(skill_pair(w.mean(0))),
            "separate_equal_week_bootstrap95":
                np.quantile(bootw,[.025,.975]).tolist(),
            "n_weeks_positive":int(sum(w[:,0]>w[:,1]))}

def within_bird_masked_minus_valid(test,e0,e1,labels,seed=20261105,
                                   bird_draws=10000):
    groups={g:defaultdict(list) for g in GROUPS}
    for i,r in enumerate(test):groups[labels[i]][r["id"]].append(i)
    valid=groups[GROUPS[0]];masked=groups[GROUPS[1]]
    both=sorted(set(valid)&set(masked))
    eligible=[b for b in both if len(valid[b])>=MIN_WITHIN_BIRD_EPISODES_EACH
              and len(masked[b])>=MIN_WITHIN_BIRD_EPISODES_EACH]
    nvalid=sum(len(valid[b]) for b in eligible)
    nmasked=sum(len(masked[b]) for b in eligible)
    if len(eligible)<MIN_SAME_BIRDS or nvalid<GROUP_MIN_ROWS or nmasked<GROUP_MIN_ROWS:
        return {"admission":"NOT_ADMITTED_SOURCE_MASK_WITHIN_BIRD_CONTRAST",
                "n_shared_original_birds_with_at_least_5_each":len(eligible),
                "matched_C_valid_test_episodes":nvalid,
                "matched_C_masked_test_episodes":nmasked}
    v=np.asarray([[np.mean(e0[valid[b]]),np.mean(e1[valid[b]])] for b in eligible])
    m=np.asarray([[np.mean(e0[masked[b]]),np.mean(e1[masked[b]])] for b in eligible])
    delta=float(skill_pair(m.mean(0))-skill_pair(v.mean(0)))
    rng=np.random.default_rng(seed)
    index=rng.integers(len(eligible),size=(bird_draws,len(eligible)))
    distribution=skill_pair(m[index].mean(1))-skill_pair(v[index].mean(1))
    return {"admission":"POSTRESULT_SOURCE_MASK_CONDITIONAL_PREDICTIVE_COMPARISON",
            "n_shared_original_birds_with_at_least_5_each":len(eligible),
            "matched_C_valid_test_episodes":nvalid,
            "matched_C_masked_test_episodes":nmasked,
            "masked_minus_valid_relative_phase_gain":delta,
            "paired_common_bird_bootstrap95":
                np.quantile(distribution,[.025,.975]).tolist(),
            "n_individual_birds_masked_skill_higher":int(sum(skill_pair(m)>skill_pair(v))),
            "source_AHN2_mask_is_not_true_water_or_prey":True}

def run(site,outfile):
    if site not in SITES:raise ValueError("Source site outside frozen comparison")
    station={"schiermonnikoog":"schiermonnikoog.waddenzee",
             "ameland":"ameland.nes"}[site]
    data={};hourly={};audit={}
    with tempfile.TemporaryDirectory(prefix="boids_v50_original_") as root:
        for year in (TRAIN_YEAR,TEST_YEAR):
            path=Path(root)/f"{site}_{year}.gz"
            original=(download_and_pin(year,path) if site=="schiermonnikoog"
                      else original_gps(year,path))
            tide,gauge=observed_rws_year(station,year)
            if gauge["gauge_rows"]<50000:raise ValueError("SOURCE_STOP_GAUGE_MEASURED_NAP_INCOMPLETE")
            data[year],heading_audit=original_three_fix_heading_episodes(
                path,tide,site,clock_shift_s=CLOCK_SHIFT_SECONDS)
            hourly[year],location_audit=source_hourly(path,site,year)
            audit[str(year)]={
                "original_provider_MD5_verified":original.get("provider_md5_match",original.get("provider_original_md5_matched")),
                "original_source_gps_SHA256":original["original_sha256"],
                "original_RWS_NAP_measurement_count":gauge["gauge_rows"],
                "source_original_moving_heading":heading_audit,
                "source_independent_original_hourly_fix":location_audit}
            path.unlink(missing_ok=True)
    e0,e1,full_replay=same_fit_errors(data[2010],data[2011],site)
    chosen,ranking=freeze_training_cells(hourly[2010])
    coverage,fmt=original_ahn2_layer()
    tiles={};patches=[]
    for n,cell in enumerate(chosen):
        try:
            p=source_tile(cell,coverage,fmt)
            tiles[cell]=p
            patches.append({"source_rank":n+1,"source_status":"READ",
                            "AHN2_original_SHA256":p["original_source_patch_SHA256"],
                            "valid_pixel_count":p["valid_NAP_candidate_pixels"]})
        except Exception as err:
            tiles[cell]=None
            patches.append({"source_rank":n+1,"source_status":"SOURCE_STOP",
                            "reason":(type(err).__name__+"_"+str(err).splitlines()[0])[:150]})
    gpsC,matching=exact_original_C_for_v41_rows(hourly[2011],data[2011])
    labels=[classify_original_C_source(c,chosen,tiles) for c in gpsC]
    counts={group:labels.count(group) for group in GROUPS}
    if sum(counts.values())!=len(data[2011]):
        raise ValueError("SOURCE_STOP_ORIGINAL_GPS_PARTITION_COUNT_MISMATCH")
    if counts[GROUPS[0]]!=REF_V43[site]["C_height"]:
        raise ValueError("SOURCE_STOP_FIXED_V49_C_HEIGHT_SOURCE_COUNT_NOT_REPLAYED")
    groups={g:group_score(data[2011],e0,e1,labels,g) for g in GROUPS}
    matched=within_bird_masked_minus_valid(data[2011],e0,e1,labels)
    report={"analysis":"V50_ORIGINAL_WILD_TIDE_HEADING_PREDICTION_AHN2_OBSERVABILITY_DOMAIN",
            "site":site,
            "science_status":"POST_v49_EXPLORATORY_OBSERVATION_DOMAIN_NOT_TRUE_FRONT",
            "frozen_full_original_v43_replay":full_replay,
            "original_2010_2011_source_quality":audit,
            "original_2010_only_eight_RD_AHN2_source_cells":ranking,
            "original_AHN2_source_patches":patches,
            "original_C_next_destination_GPS_source_matching":matching,
            "all_source_2011_heading_episodes_partitioned_once":counts,
            "original_source_groups":groups,
            "primary_same_bird_masked_minus_valid_tide_phase_heading_skill":matched,
            "native_original_gps_clock":"UTC_OR_GPS_TIME_UNVERIFIED_ASSUMED_UTC",
            "causal_boundary":"AHN2 source missingness != measured wet_dry front; no prey/social Boids"}
    Path(outfile).parent.mkdir(parents=True,exist_ok=True)
    Path(outfile).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--site",choices=SITES,required=True)
    parser.add_argument("--output",required=True)
    arg=parser.parse_args()
    print(json.dumps(run(arg.site,arg.output),sort_keys=True))
