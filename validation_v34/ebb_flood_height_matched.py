#!/usr/bin/env python3
"""v34: within-bird clock/month/height/duty-matched ebb versus flood speed.

Exploratory after v33-D. Replays v33-D entire frozen original-source receipt
before opening any new source-linked phase-conditional outcome. Not a causal
test of foraging, resource exposure, memory, or Reynolds Boids forces.
"""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import itertools
import json
import math
import os
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v33"))
sys.path.insert(0,str(ROOT/"validation_v32"))
import phase_response as phase
import tidal_forecast as tide
import forecast as v32

FROZEN_D=ROOT/"validation_v33/results/oystercatcher_tide_speed_v33.json"
PROTOCOL="docs/V34_EBB_FLOOD_HEIGHT_MATCHED_PROTOCOL.md"
HALF_HEIGHT_BIN_M=.5
SLOPE_HALF_WINDOW_MINUTES=30
MIN_SAMPLES_EACH_PHASE=2
MIN_PAIRED_STRATA_PER_BIRD=8
MIN_BIRDS=20
MIN_TOTAL_PAIRED_STRATA=200
BOOT_REPS=10000
BOOT_SEED=20261031
DURATION_BINS=("short_5_30","medium_30_90","long_90_180")
EPOCH=dt.datetime(1970,1,1)

def nested_close(a,b,tol=1e-12):
    if isinstance(a,dict):
        return isinstance(b,dict) and a.keys()==b.keys() and all(nested_close(a[k],b[k],tol) for k in a)
    if isinstance(a,list):
        return isinstance(b,list) and len(a)==len(b) and all(nested_close(x,y,tol) for x,y in zip(a,b))
    if isinstance(a,float) and isinstance(b,(int,float)):
        return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol
    return a==b

def replay_original_D(points,astronomy, original_qa):
    saved=json.loads(FROZEN_D.read_text(encoding="utf-8"))
    q1=saved["tidal_source_only_high_low_quartiles_m_NAP"]["low_q25"]
    q3=saved["tidal_source_only_high_low_quartiles_m_NAP"]["high_q75"]
    sq1,sq3=phase.source_level_quartiles(astronomy)
    if abs(sq1-q1)>1e-12 or abs(sq3-q3)>1e-12:
        raise ValueError("Previously frozen astronomical tide quartile drift")
    if not nested_close(saved["source_data_quality"],original_qa):
        raise ValueError("Previously frozen original GPS source-quality drift")
    groups,qa=phase.original_step_strata(points,astronomy,q1,q3)
    observed=phase.evaluate(groups)
    if not nested_close(saved["geographic_and_clock_month_tide_pair_audit"],qa):
        raise ValueError("Frozen original GPS-tide step opportunities mismatch")
    if not nested_close(saved["observed_association"],observed):
        raise ValueError("Frozen original v33-D all-bird numerical receipt mismatch")
    return {"status":"COMPLETE_FROZEN_V33D_ORIGINAL_GPS_TIDE_RECEIPT_MATCH",
            "original_source_whole_birds":observed["support"]["birds_with_minimum_clock_matched_strata"],
            "original_bird_month_clock_strata":observed["support"]["paired_original_bird_month_hour_strata"],
            "all_source_and_per_bird_fields_within_abs_tolerance":1e-12}

def fixed_duration_bin(elapsed):
    if not phase.MIN_PAIR_MINUTES<=elapsed<=phase.MAX_PAIR_MINUTES:
        raise ValueError("Step duration outside registered 5 to 180 min")
    if elapsed<30:return "short_5_30"
    if elapsed<90:return "medium_30_90"
    return "long_90_180"

def height_bin(height):
    if not math.isfinite(height):raise ValueError("Nonfinite original tide height")
    return math.floor(height/HALF_HEIGHT_BIN_M)

def astronomical_phase(mid,series):
    """Instantaneous +/-30min RWS astronomical slope around fix midpoint."""
    center=phase.nearest_tide_key(mid)
    before=center-dt.timedelta(minutes=SLOPE_HALF_WINDOW_MINUTES)
    after=center+dt.timedelta(minutes=SLOPE_HALF_WINDOW_MINUTES)
    h=series.get(center);a=series.get(after);b=series.get(before)
    if h is None or a is None or b is None:
        return None
    if not all(math.isfinite(v) for v in (h,a,b)):
        raise ValueError("Invalid admitted tide series at an original time")
    if a>b:return "flood",h,a-b
    if a<b:return "ebb",h,a-b
    return ("turning",h,0.)

def new_strata(points,astronomy):
    """Each stratum contains ebb/flood n,sum(log speed),sum(elapsed),sum(height).

    Key: original private bird × calendar year × month × UTC hour × 0.5m
    absolute tide height band × fixed step-duration bin. Nothing raw exported.
    """
    seen=collections.Counter((p[0],p[1]) for p in points)
    clean=sorted((p for p in points if seen[p[0],p[1]]==1),
                 key=lambda p:(p[0],p[1]))
    qa=collections.Counter()
    qa["valid_source_fixes_before_all_duplicate_rejection"]=len(points)
    qa["original_duplicate_fix_rows_discarded"]=sum(n for n in seen.values() if n>1)
    # Each category: sample count, log1p-speed sum, elapsed-time sum, source water-height sum.
    groups=collections.defaultdict(lambda:[[0,0.,0.,0.],[0,0.,0.,0.]])
    for bird, it in itertools.groupby(clean,key=lambda p:p[0]):
        previous=None
        for current in it:
            if previous is None:
                previous=current;continue
            _,at,lat,lon=current
            _,before,plat,plon=previous
            previous=current
            elapsed=(at-before).total_seconds()/60.
            if not phase.MIN_PAIR_MINUTES<=elapsed<=phase.MAX_PAIR_MINUTES:
                qa["pairs_rejected_by_original_duration_gate"]+=1;continue
            if (phase.haversine_km(lat,lon,phase.STATION_LAT,phase.STATION_LON)>phase.LOCAL_RADIUS_KM or
                phase.haversine_km(plat,plon,phase.STATION_LAT,phase.STATION_LON)>phase.LOCAL_RADIUS_KM):
                qa["pairs_rejected_outside_25km_original_gauge"]+=1;continue
            midpoint=before+(at-before)/2
            state=astronomical_phase(midpoint,astronomy)
            if state is None:
                qa["local_pairs_missing_plus_minus_30min_astronomy"]+=1;continue
            name,h,derivative=state
            if name=="turning":
                qa["local_pairs_at_exact_slope_zero"]+=1;continue
            vel=phase.haversine_km(plat,plon,lat,lon)/(elapsed/60.)
            if not math.isfinite(vel):raise ValueError("Nonfinite Haversine step displacement speed")
            if vel>100:qa["source_pairs_over_100_km_per_hour_descriptive"]+=1
            duration=fixed_duration_bin(elapsed)
            key=(bird,midpoint.year,midpoint.month,midpoint.hour,height_bin(h),duration)
            ix=0 if name=="ebb" else 1
            v=groups[key][ix]
            v[0]+=1;v[1]+=math.log1p(vel);v[2]+=elapsed;v[3]+=h
            qa["valid_local_pairs_with_both_height_and_slope"]+=1
            qa["valid_original_ebb_pairs" if ix==0 else "valid_original_flood_pairs"]+=1
    return groups,dict(qa)

def matched_strata(groups):
    per_bird=collections.defaultdict(list)
    qa=collections.Counter()
    for (bird,year,month,hour,hbin,duration),(ebb,flood) in groups.items():
        if ebb[0]<MIN_SAMPLES_EACH_PHASE or flood[0]<MIN_SAMPLES_EACH_PHASE:
            qa["strata_missing_two_original_pairs_per_phase"]+=1
            continue
        per_bird[bird].append({
          "year":year,"height_band":hbin,"duration":duration,
          "n_ebb":ebb[0],"n_flood":flood[0],
          "ebb_minus_flood_speed":ebb[1]/ebb[0]-flood[1]/flood[0],
          "ebb_minus_flood_elapsed_minutes":ebb[2]/ebb[0]-flood[2]/flood[0],
          "ebb_minus_flood_water_height_m":ebb[3]/ebb[0]-flood[3]/flood[0],
        })
        qa["paired_bird_month_clock_height_duration_strata_before_bird_gate"]+=1
    retained={bird:rs for bird,rs in per_bird.items() if len(rs)>=MIN_PAIRED_STRATA_PER_BIRD}
    qa["whole_birds_admitted"]=len(retained)
    qa["paired_strata_admitted"]=sum(len(rs) for rs in retained.values())
    qa["paired_strata_from_ineligible_birds"]=sum(len(rs) for bird,rs in per_bird.items()
                                                     if bird not in retained)
    qa["ebb_steps_in_retained_strata"]=sum(r["n_ebb"] for rs in retained.values() for r in rs)
    qa["flood_steps_in_retained_strata"]=sum(r["n_flood"] for rs in retained.values() for r in rs)
    return retained,dict(qa)

def summarize(per_bird,qa):
    if qa["whole_birds_admitted"]<MIN_BIRDS or qa["paired_strata_admitted"]<MIN_TOTAL_PAIRED_STRATA:
        return {"status":"NOT_ADMITTED_EBB_FLOOD_HEIGHT_DUTY_MATCHED_SUPPORT",
                "support":qa,"any_ebb_flood_effect_reported":False}
    birds=sorted(per_bird)
    mean_bird=np.array([[float(np.mean([r[k] for r in per_bird[b]]))
                        for k in ("ebb_minus_flood_speed","ebb_minus_flood_elapsed_minutes",
                                  "ebb_minus_flood_water_height_m")]
                       for b in birds])
    if not np.isfinite(mean_bird).all():raise ValueError("Nonfinite stratum-to-bird mean")
    draw=np.random.default_rng(BOOT_SEED).integers(0,len(birds),size=(BOOT_REPS,len(birds)))
    summaries={}
    for idx,label in enumerate(("PRIMARY_EBB_minus_FLOOD_log1p_speed",
                                 "audit_EBB_minus_FLOOD_elapsed_minutes",
                                 "audit_EBB_minus_FLOOD_actual_height_m")):
        vals=mean_bird[:,idx]
        npos=int((vals>0).sum());nnonzero=int((vals!=0).sum())
        summaries[label]={
           "equal_bird_mean":float(vals.mean()),
           "bootstrap_95_percentile":list(map(float,np.quantile(vals[draw].mean(axis=1),[.025,.975]))),
           "positive_birds":npos,"negative_birds":int((vals<0).sum()),
           "nonzero_birds":nnonzero,
           "one_sided_positive_sign_p":sum(math.comb(nnonzero,k)
                for k in range(npos,nnonzero+1))/2**nnonzero if nnonzero else 1.,
        }
    diagnostics={}
    for key,values in (
        ("duration",DURATION_BINS),
        ("water_height_half_m_bin",sorted({r["height_band"] for rs in per_bird.values() for r in rs})),
    ):
        info={}
        for val in values:
            per={}
            for bird,rs in per_bird.items():
                d=[r["ebb_minus_flood_speed"] for r in rs if
                   (r["duration"] if key=="duration" else r["height_band"])==val]
                if d:per[bird]=float(np.mean(d))
            sign=collections.Counter(1 if e>0 else -1 if e<0 else 0 for e in per.values())
            info[str(val)]={"birds_with_strata":len(per),
                "total_matched_strata":sum(sum(
                    (r["duration"] if key=="duration" else r["height_band"])==val
                    for r in rs) for rs in per_bird.values()),
                "descriptive_equal_available_bird_effect":float(np.mean(list(per.values()))) if per else None,
                "descriptive_positive_birds":sign[1],
                "descriptive_negative_birds":sign[-1]}
        diagnostics[key]=info
    years={}
    for year in range(2008,2015):
        per={}
        for bird,rs in per_bird.items():
            v=[r["ebb_minus_flood_speed"] for r in rs if r["year"]==year]
            if v:per[bird]=float(np.mean(v))
        years[str(year)]={
           "birds":len(per),
           "strata":sum(sum(r["year"]==year for r in rs) for rs in per_bird.values()),
           "descriptive_equal_available_bird_effect":float(np.mean(list(per.values()))) if per else None,
           "birds_ebb_speed_positive":sum(v>0 for v in per.values()),
           "birds_ebb_speed_negative":sum(v<0 for v in per.values()),
        }
    return {"status":"EXPLORATORY_MATCHED_EBB_FLOOD_MOVEMENT_HYSTERESIS",
      "support":qa,
      "all_original_birds_equal_weight":True,
      "fixed_source_tide_height_band_m":HALF_HEIGHT_BIN_M,
      "fixed_slope_window":f"+/-{SLOPE_HALF_WINDOW_MINUTES} min of astronomical RWS",
      "fixed_duration_bins":list(DURATION_BINS),
      "source_original_study_count":1,
      "matched_estimands":summaries,
      "descriptive_stratified_diagnostics":diagnostics,
      "year_descriptives_not_independent_replicates":years,
      "anonymous_original_bird_means":{f"bird_{i+1:03d}":{
          "matched_strata":len(per_bird[b]),
          "ebb_minus_flood_log1p_speed":float(mean_bird[i,0]),
          "ebb_minus_flood_elapsed_minutes":float(mean_bird[i,1]),
          "ebb_minus_flood_actual_height_m":float(mean_bird[i,2])
        } for i,b in enumerate(birds)},
      "bootstrap_reps":BOOT_REPS,"seed":BOOT_SEED,
      "this_analysis_specified_after_v33_results":True,
      "no_claim_of_causal_tidal_foraging_or_social_Boids":True}

def run():
    astronomy,astro_year_quality=tide.load_original_astronomy()
    with tempfile.TemporaryDirectory() as d:
        paths=v32.original_files_to_temp(Path(d))
        points,source_quality=phase.read_original_valid_gps(paths)
    old=replay_original_D(points,astronomy,source_quality)
    g,quality=new_strata(points,astronomy)
    matched,support=matched_strata(g)
    outcome=summarize(matched,support)
    return {"status":outcome["status"],"protocol":PROTOCOL,
       "study":"v34 Schiermonnikoog source-verified RWS astronomical ebb versus flood at matched tide height",
       "source_original_RWS_station":tide.STATION,
       "source_tide_years":list(tide.YEARS),
       "source_year_10min_coverage":astro_year_quality,
       "source_original_gps_quality":source_quality,
       "frozen_v33D_full_reproduction":old,
       "local_step_tide_source_and_temporal_support":quality,
       "matched_cohort_audit":support,
       "observed_outcome":outcome,
       "no_animal_ID_GPS_positions_UTC_timestamps_or_raw_tide_heights_exported":True,
       "previous_v29_v30_v31_v32_v33_results_unchanged":True,
       "scientific_boundaries":[
           "Exploratory same GPS study AFTER strong v33-D high-low original result was known",
           "Astronomical ebb/flood phase calculated from one gauge proxy; not actual shorefront water movement",
           "Within 0.5m height bands residual height difference may still confound ebb versus flood",
           "Original GPS duty and speed from two fixes, no measured foraging or resource patches",
           "One site and nonindependent shared weather/bird tracking, no causal social Boids force",
       ]}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,
         default=Path("validation_v34/results/ebb_flood_height_matched_v34.json"))
    args=parser.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
          prefix=".v34-",delete=False) as f:
        f.write(payload);temp=Path(f.name)
    os.replace(temp,args.out)
    print("V34_COMPLETE_D_REPLAY",json.dumps(result["frozen_v33D_full_reproduction"],sort_keys=True))
    print("V34_SOURCE_SUPPORT",json.dumps(result["local_step_tide_source_and_temporal_support"],sort_keys=True))
    print("V34_MATCHED_SUPPORT",json.dumps(result["matched_cohort_audit"],sort_keys=True))
    print("V34_STATUS",result["status"])
    if result["observed_outcome"].get("matched_estimands"):
        print("V34_PRIMARY_AND_AUDITS",json.dumps(result["observed_outcome"]["matched_estimands"],sort_keys=True))
    else:
        print("V34_NO_EBB_FLOOD_EFFECT_SCORED")
    print("V34_COMPLETE_AGGREGATE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
