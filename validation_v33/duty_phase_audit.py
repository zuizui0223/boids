#!/usr/bin/env python3
"""v33-E: explicitly POST-outcome GPS duty and tide phase robustness audit.

Do not use these diagnostics to revise the original fixed v33-D primary
effect, cohort, tidal gauge, tide-category boundaries or causal interpretation.
Original animal positions / IDs are ephemeral; export aggregates only.
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
import tidal_forecast as tide
import phase_response as phase
import forecast as v32

D_RECEIPT=ROOT/"validation_v33/results/oystercatcher_tide_speed_v33.json"
PROTOCOL="docs/V33E_POSTOUTCOME_TIDE_OBSERVATION_AUDIT_PROTOCOL.md"
OFFSETS=(0,3,6)
BIN_NAMES=("ALL","SHORT_5_TO_30","MEDIUM_30_TO_90","LONG_90_TO_180")
MIN_CATEGORY_N=2
MIN_STRATA=8
MIN_BIRDS=20
MIN_TOTAL_STRATA=200
REPS=10000
SEED=20261031

def duration_bin(minutes):
    if not 5<=minutes<=180: raise ValueError("Invalid original pair duration")
    if minutes<30:return "SHORT_5_TO_30"
    if minutes<90:return "MEDIUM_30_TO_90"
    return "LONG_90_TO_180"

def _equal(a,b):
    if isinstance(a,dict):
        return isinstance(b,dict) and a.keys()==b.keys() and all(_equal(a[k],b[k]) for k in a)
    if isinstance(a,list):
        return isinstance(b,list) and len(a)==len(b) and all(_equal(x,y) for x,y in zip(a,b))
    if isinstance(a,float) and isinstance(b,(int,float)):
        return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=1e-12
    return a==b

def replay_v33_D(points, astronomy, q1,q3):
    saved=json.loads(D_RECEIPT.read_text())
    if saved["status"]!="EXPLORATORY_ORIGINAL_HIGH_VS_LOW_TIDE_LOCAL_SPEED_ASSOCIATION":
        raise ValueError("Original D receipt is not an admitted observed effect")
    if abs(saved["tidal_source_only_high_low_quartiles_m_NAP"]["low_q25"]-q1)>1e-12 or abs(
        saved["tidal_source_only_high_low_quartiles_m_NAP"]["high_q75"]-q3)>1e-12:
        raise ValueError("Original D fixed astronomical tide quartile drift")
    strata,qa=phase.original_step_strata(points,astronomy,q1,q3)
    actual=phase.evaluate(strata)
    if not _equal(saved["observed_association"],actual) or not _equal(
        saved["geographic_and_clock_month_tide_pair_audit"],qa):
        raise ValueError("Original D full observed-score or source-quality receipt mismatch")
    return {"status":"FULL_ORIGINAL_V33D_36_BIRD_RECEIPT_MATCH",
            "tolerance":1e-12,
            "original_birds":actual["support"]["birds_with_minimum_clock_matched_strata"],
            "original_matched_strata":actual["support"]["paired_original_bird_month_hour_strata"],
            "all_published_anonymous_original_bird_effects_preserved":True}

def _empty():
    # Low vs high: number of step pairs, sum log(1+speed), sum duration in minutes.
    return [[0,0.,0.],[0,0.,0.]]

def accumulate_step_strata(points, astronomy, q1,q3):
    """Only fixed lag offsets / duration bins, no response-dependent selection.

    Keys kept internally: (diagnostic, raw private bird ID, year, month, UTC hour).
    Raw IDs never enter the returned or saved JSON.
    """
    seen=collections.Counter((p[0],p[1]) for p in points)
    ordered=sorted((p for p in points if seen[p[0],p[1]]==1),
                   key=lambda p:(p[0],p[1]))
    accum=collections.defaultdict(_empty)
    counts=collections.Counter()
    counts["original_source_valid_GPS_fixes_before_duplicates"]=len(points)
    counts["source_duplicate_fixes_dropped"]=sum(n for n in seen.values() if n>1)
    for bird, group in itertools.groupby(ordered,key=lambda p:p[0]):
        prev=None
        for row in group:
            if prev is None:
                prev=row;continue
            _,date,lat,lon=row
            _,earlier,plat,plon=prev
            prev=row
            minutes=(date-earlier).total_seconds()/60.
            if not phase.MIN_PAIR_MINUTES<=minutes<=phase.MAX_PAIR_MINUTES:
                counts["duration_out_of_fixed_range"]+=1;continue
            if (phase.haversine_km(lat,lon,phase.STATION_LAT,phase.STATION_LON)>phase.LOCAL_RADIUS_KM
                or phase.haversine_km(plat,plon,phase.STATION_LAT,phase.STATION_LON)>phase.LOCAL_RADIUS_KM):
                counts["outside_fixed_gauge_radius"]+=1;continue
            mid=earlier+(date-earlier)/2
            speed=phase.haversine_km(plat,plon,lat,lon)/(minutes/60)
            if not math.isfinite(speed):raise ValueError("Nonfinite original movement speed")
            log_speed=math.log1p(speed)
            d_bin=duration_bin(minutes)
            counts["source_local_valid_original_step_pairs"]+=1
            for offset in OFFSETS:
                adjusted=mid+dt.timedelta(hours=offset)
                level=astronomy.get(phase.nearest_tide_key(adjusted))
                if level is None:
                    counts[f"missing_tide_offset_plus_{offset}h"]+=1;continue
                if level<=q1:category=0
                elif level>=q3:category=1
                else:
                    counts[f"middle_tide_offset_plus_{offset}h"]+=1;continue
                if offset==0:
                    names=("OFFSET_0H_ALL","OFFSET_0H_"+d_bin)
                else:
                    names=(f"OFFSET_PLUS_{offset}H_ALL",)
                for name in names:
                    val=accum[name,bird,mid.year,mid.month,mid.hour][category]
                    val[0]+=1
                    val[1]+=log_speed
                    val[2]+=minutes
                    counts[f"selected_original_steps_{name}"]+=1
    return accum,dict(counts)

def paired_strata(accum, diag):
    grouped=collections.defaultdict(list)
    total_valid=0
    for (label,bird,year,month,hour),(low,high) in accum.items():
        if label!=diag:continue
        if low[0]<MIN_CATEGORY_N or high[0]<MIN_CATEGORY_N:continue
        row={"log_speed_difference":high[1]/high[0]-low[1]/low[0],
             "elapsed_minutes_difference":high[2]/high[0]-low[2]/low[0],
             "year":year,"n_low":low[0],"n_high":high[0]}
        grouped[bird].append(row)
        total_valid+=1
    admitted={bird:v for bird,v in grouped.items() if len(v)>=MIN_STRATA}
    support={"possible_paired_strata_before_bird_gate":total_valid,
             "accepted_whole_birds":len(admitted),
             "accepted_paired_strata":sum(len(v) for v in admitted.values()),
             "original_steps_low_in_accepted_strata":sum(r["n_low"] for v in admitted.values() for r in v),
             "original_steps_high_in_accepted_strata":sum(r["n_high"] for v in admitted.values() for r in v)}
    return admitted,support

def comparison(admitted,support):
    if support["accepted_whole_birds"]<MIN_BIRDS or support["accepted_paired_strata"]<MIN_TOTAL_STRATA:
        return {"status":"NOT_ADMITTED_POSTOUTCOME_DIAGNOSTIC_SUPPORT",
                "support":support,"any_new_effect_reported":False}
    birds=sorted(admitted)
    metrics=np.array([[float(np.mean([x[k] for x in admitted[b]]))
                       for k in ("log_speed_difference","elapsed_minutes_difference")]
                      for b in birds])
    samples=np.random.default_rng(SEED).integers(0,len(birds),size=(REPS,len(birds)))
    def summary(values):
        npos=int((values>0).sum())
        nonzero=int((values!=0).sum())
        return {
            "equal_bird_mean":float(values.mean()),
            "whole_bird_bootstrap_95_percentile":list(map(float,np.quantile(values[samples].mean(axis=1),[.025,.975]))),
            "birds_with_positive_high_minus_low":npos,
            "birds_with_negative_high_minus_low":int((values<0).sum()),
            "nonzero_birds":nonzero,
            "positive_direction_exact_sign_p":sum(math.comb(nonzero,k) for k in range(npos,nonzero+1))/(2**nonzero) if nonzero else 1.
        }
    return {"status":"EXPLORATORY_POSTOUTCOME_DURATION_OR_PHASE_DIAGNOSTIC",
            "support":support,
            "response_high_minus_low_log1p_speed":summary(metrics[:,0]),
            "elapsed_minutes_high_minus_low":summary(metrics[:,1]),
            "anonymized_bird_effects":{f"bird_{i+1:03d}":{
                "matched_strata":len(admitted[b]),
                "mean_high_minus_low_log_speed":float(metrics[i,0]),
                "mean_high_minus_low_elapsed_minutes":float(metrics[i,1])
            } for i,b in enumerate(birds)},
            "original_population_count":1,"source_original_birds_only":len(birds),
            "post_outcome_audit_not_confirmatory":True}

def yearly_descriptive(original_admitted):
    result={}
    for yr in tide.YEARS:
        bybird={}
        for bird,rows in original_admitted.items():
            subset=[x["log_speed_difference"] for x in rows if x["year"]==yr]
            if subset:
                bybird[bird]=float(np.mean(subset))
        vals=list(bybird.values())
        result[str(yr)]={
           "matched_birds":len(vals),
           "bird_month_hour_paired_strata":sum(
               sum(x["year"]==yr for x in rs) for rs in original_admitted.values()),
           "equal_bird_mean_high_minus_low_log_speed":float(np.mean(vals)) if vals else None,
           "birds_high_minus_low_negative":sum(v<0 for v in vals),
           "birds_high_minus_low_positive":sum(v>0 for v in vals),
           "one_site_shared_environment_year_not_independent_replication":True}
    return result

def run():
    astro,aq=tide.load_original_astronomy()
    q1,q3=phase.source_level_quartiles(astro)
    with tempfile.TemporaryDirectory() as path:
        files=v32.original_files_to_temp(Path(path))
        points,gps_qa=phase.read_original_valid_gps(files)
    receipt=replay_v33_D(points,astro,q1,q3)  # Stop if old known result differs.
    groups,source_counts=accumulate_step_strata(points,astro,q1,q3)
    plans=("OFFSET_0H_ALL","OFFSET_0H_SHORT_5_TO_30",
           "OFFSET_0H_MEDIUM_30_TO_90","OFFSET_0H_LONG_90_TO_180",
           "OFFSET_PLUS_3H_ALL","OFFSET_PLUS_6H_ALL")
    outputs={}
    baseline_birds={}
    for name in plans:
        matched,support=paired_strata(groups,name)
        if name=="OFFSET_0H_ALL":
            baseline_birds=matched
            if support["accepted_whole_birds"]!=receipt["original_birds"] or (
               support["accepted_paired_strata"]!=receipt["original_matched_strata"]):
                raise ValueError("Within-hour D baseline matching drift")
        outputs[name]=comparison(matched,support)
    main=outputs["OFFSET_0H_ALL"]
    expected=json.loads(D_RECEIPT.read_text())["observed_association"]["mean_high_minus_low_log_speed"]
    if (main["status"]!="EXPLORATORY_POSTOUTCOME_DURATION_OR_PHASE_DIAGNOSTIC" or
        abs(main["response_high_minus_low_log1p_speed"]["equal_bird_mean"]-expected)>1e-12):
        raise ValueError("Replayed main high-vs-low bird mean changed")
    return {"study":"v33-E original oystercatcher post-outcome tide/GPS observation auditing",
           "status":"COMPLETED_POSTOUTCOME_DUTY_AND_PHASE_AUDIT",
           "protocol":PROTOCOL,
           "source_GPS":"original Zenodo 10053970 v4 original seven years 2008-2014",
           "source_astro":"RWS astronomical WATHTE NAP Schiermonnikoog Waddenzee",
           "original_v33D_all_effects_source_receipt_replayed":receipt,
           "source_quality":gps_qa,
           "tide_quartiles_m_NAP":{"low":q1,"high":q3},
           "source_GPS_pair_counts":source_counts,
           "fixed_diagnostic_order":list(plans),
           "fixed_post_outcome_diagnostics":outputs,
           "all_seven_year_descriptives_from_original_hour_matched_cohort":yearly_descriptive(baseline_birds),
           "no_GPS_animal_IDs_coordinates_or_original_UTC_exported":True,
           "interpretation_limits":[
               "Original v33-D direction known before diagnostic specification; no independent confirmation",
               "GPS duty-cycle/elapsed-time differences may bias original speed associations",
               "Temporal tidal shifts are mathematically linked through 12.4h periodicity",
               "Only one coastal bird source and study; no causal tidal-foraging or Boids claim",
               "No post-hoc selection of duration bin or tide offset permitted"]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path("validation_v33/results/oystercatcher_tide_duty_phase_audit_v33.json"))
    args=parser.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    encoded=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
          prefix=".v33audit-",delete=False) as temp:
        temp.write(encoded);name=Path(temp.name)
    os.replace(name,args.out)
    print("V33E_FROZEN_D_REPLAY",json.dumps(result["original_v33D_all_effects_source_receipt_replayed"],sort_keys=True))
    print("V33E_POSTOUTCOME_DIAGNOSTICS",json.dumps({
       k:{"status":v["status"],
          "support":v["support"],
          "mean_high_minus_low_speed":v.get("response_high_minus_low_log1p_speed",{}).get("equal_bird_mean"),
          "mean_high_minus_low_elapsed_minutes":v.get("elapsed_minutes_high_minus_low",{}).get("equal_bird_mean")}
          for k,v in result["fixed_post_outcome_diagnostics"].items()},sort_keys=True))
    print("V33E_YEARS",json.dumps(result["all_seven_year_descriptives_from_original_hour_matched_cohort"],sort_keys=True))
    print("V33E_AGGREGATE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))

if __name__=="__main__":main()
