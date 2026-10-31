#!/usr/bin/env python3
"""v34-B: post-outcome composition and 1-minute GPS-duty artifact diagnostics.

The full original v34 AND the prior v33-D GPS/tide numerical receipts are
replayed before new scores. These diagnostics were chosen AFTER seeing v34
height-band directions, and are not independent biological confirmations.
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
sys.path.insert(0,str(ROOT/"validation_v34"))
sys.path.insert(0,str(ROOT/"validation_v33"))
sys.path.insert(0,str(ROOT/"validation_v32"))
import ebb_flood_height_matched as v34
import phase_response as phase
import tidal_forecast as tide
import forecast as v32

FROZEN_V34=ROOT/"validation_v34/results/ebb_flood_height_matched_v34.json"
PROTOCOL="docs/V34B_SAME_BIRD_HEIGHT_AND_ONE_MINUTE_DUTY_AUDIT_PROTOCOL.md"
THRESHOLD_NAP_M=.5  # selected post v34 height-band output, not ecological breakpoint
MIN_PER_BIRD_PER_REGIME=8
MIN_PER_BIRD_MINUTE=8
MIN_SUPPORT_BIRDS=20
MIN_TOTAL_STRATA=200
BOOT_REPS=10000
BOOT_SEED=20261031

def strict_v34_original_receipt(astro,year_qa,points,gps_qa):
    prev=v34.replay_original_D(points,astro,gps_qa)
    groups,step_qa=v34.new_strata(points,astro)
    old_matched,old_qa=v34.matched_strata(groups)
    old_effect=v34.summarize(old_matched,old_qa)
    saved=json.loads(FROZEN_V34.read_text(encoding="utf-8"))
    checks={
      "source_year_10min_coverage":year_qa,
      "source_original_gps_quality":gps_qa,
      "frozen_v33D_full_reproduction":prev,
      "local_step_tide_source_and_temporal_support":step_qa,
      "matched_cohort_audit":old_qa,
      "observed_outcome":old_effect,
    }
    for name,x in checks.items():
        if not v34.nested_close(x,saved.get(name),1e-12):
            raise ValueError("Frozen original v34 source/score receipt mismatch: "+name)
    if (old_qa["whole_birds_admitted"]!=39 or old_qa["paired_strata_admitted"]!=25855):
        raise ValueError("Frozen original v34 support changed unexpectedly")
    return old_matched,{
        "status":"V34_ALL_39_BIRDS_25855_STRATA_AND_ORIGINAL_V33D_MATCH",
        "source_unchanged_and_all_anonymized_bird_fields_matched":True,
        "absolute_error_tolerance":1e-12,
        "original_v34_birds":old_qa["whole_birds_admitted"],
        "original_v34_strata":old_qa["paired_strata_admitted"],
        "frozen_v33D_replay":prev,
    }

def sign_p(npositive,nnonzero):
    if not nnonzero:return 1.
    return sum(math.comb(nnonzero,k) for k in range(npositive,nnonzero+1))/(2**nnonzero)

def equal_bird_summary(values):
    """One vector of equal-weight per-bird effects with complete paired CI."""
    a=np.array(values,dtype=float)
    if not len(a) or not np.isfinite(a).all():raise ValueError("Missing finite matched original bird effects")
    inds=np.random.default_rng(BOOT_SEED).integers(0,len(a),size=(BOOT_REPS,len(a)))
    npositive=int(np.sum(a>0));nnonzero=int(np.sum(a!=0))
    return {
        "mean":float(a.mean()),
        "bird_bootstrap_95_percentile":list(map(float,np.quantile(a[inds].mean(axis=1),[.025,.975]))),
        "positive_birds":npositive,"negative_birds":int(np.sum(a<0)),
        "nonzero_birds":nnonzero,"exact_one_sided_positive_sign_p":sign_p(npositive,nnonzero),
        "original_birds":len(a),
    }

def same_bird_height_contrast(matched):
    grouped={}
    source=collections.Counter()
    for bird,rs in matched.items():
        low=[r for r in rs if r["height_band"]<=0]
        high=[r for r in rs if r["height_band"]>=1]
        source["birds_with_either_original_0p5m_regime"]+=1
        source["raw_v34_admitted_low_strata"]+=len(low)
        source["raw_v34_admitted_high_strata"]+=len(high)
        if len(low)<MIN_PER_BIRD_PER_REGIME or len(high)<MIN_PER_BIRD_PER_REGIME:
            source["birds_failing_one_tide_height_regime"]+=1;continue
        grouped[bird]=(low,high)
    support={"original_v34_matched_birds_in_both_height_regimes":len(grouped),
             "low_height_strata_from_matched_birds":sum(len(v[0]) for v in grouped.values()),
             "high_height_strata_from_matched_birds":sum(len(v[1]) for v in grouped.values()),
             "birds_missing_regime_support":source["birds_failing_one_tide_height_regime"],
             "LOW_definition":"original 0.5m height bins <=0, H < +0.5m NAP",
             "HIGH_definition":"original height bins >=1, H >= +0.5m NAP",
             "threshold_selected_after_opening_v34_original_height_results":True}
    if (len(grouped)<MIN_SUPPORT_BIRDS or
        support["low_height_strata_from_matched_birds"]<MIN_TOTAL_STRATA or
        support["high_height_strata_from_matched_birds"]<MIN_TOTAL_STRATA):
        return {"status":"NOT_ADMITTED_V34B_WITHIN_BIRD_HEIGHT_SUPPORT",
                "support":support,"any_new_paired_height_effect_reported":False}
    rows=[]
    anon={}
    for ix,b in enumerate(sorted(grouped)):
        lo,hi=grouped[b]
        l=float(np.mean([r["ebb_minus_flood_speed"] for r in lo]))
        h=float(np.mean([r["ebb_minus_flood_speed"] for r in hi]))
        rows.append((l,h,l-h))
        anon[f"bird_{ix+1:03d}"]={
          "low_strata":len(lo),"high_strata":len(hi),
          "ebb_minus_flood_low":l,"ebb_minus_flood_high":h,
          "low_minus_high_phase_asymmetry":l-h}
    mat=np.array(rows)
    return {"status":"EXPLORATORY_POSTOUTCOME_SAME_BIRD_HEIGHT_DIRECTION_AUDIT",
        "support":support,
        "all_birds_matched_to_themselves_across_LOW_and_HIGH":True,
        "effects":{
            "LOW_ebb_minus_flood":equal_bird_summary(mat[:,0]),
            "HIGH_ebb_minus_flood":equal_bird_summary(mat[:,1]),
            "PRIMARY_POSTOUTCOME_LOW_minus_HIGH":equal_bird_summary(mat[:,2]),
        },
        "birds_with_LOW_positive_and_HIGH_negative":int(((mat[:,0]>0)&(mat[:,1]<0)).sum()),
        "birds_with_LOW_negative_and_HIGH_positive":int(((mat[:,0]<0)&(mat[:,1]>0)).sum()),
        "original_source_anonymized_birds":anon,
        "post_outcome_threshold_not_confirmatory":True}

def one_minute_bin(elapsed):
    if not v34.phase.MIN_PAIR_MINUTES<=elapsed<=v34.phase.MAX_PAIR_MINUTES:
        raise ValueError("Original GPS elapsed-time gate violated")
    # Tie to earlier / lower integer minute. Numerical jitter <1e-10 is ignored.
    return math.floor(elapsed +.5-1e-9)

def minute_resolution_strata(points,astro):
    """Reprocess exact v34 source with an additional 1-minute duration key.

    All other v34 original source gates and unit definitions are identical.
    """
    seen=collections.Counter((p[0],p[1]) for p in points)
    ordered=sorted((p for p in points if seen[p[0],p[1]]==1),
                   key=lambda p:(p[0],p[1]))
    qa=collections.Counter()
    data=collections.defaultdict(lambda:[[0,0.,0.,0.],[0,0.,0.,0.]])
    for bird, it in itertools.groupby(ordered,key=lambda p:p[0]):
        prior=None
        for now in it:
            if prior is None:prior=now;continue
            _,end,lat,lon=now
            _,start,plat,plon=prior
            prior=now
            elapsed=(end-start).total_seconds()/60.
            if not phase.MIN_PAIR_MINUTES<=elapsed<=phase.MAX_PAIR_MINUTES:
                qa["original_rejected_elapsed"]+=1;continue
            if (phase.haversine_km(lat,lon,phase.STATION_LAT,phase.STATION_LON)>phase.LOCAL_RADIUS_KM or
                phase.haversine_km(plat,plon,phase.STATION_LAT,phase.STATION_LON)>phase.LOCAL_RADIUS_KM):
                qa["original_rejected_geography"]+=1;continue
            center=start+(end-start)/2
            state=v34.astronomical_phase(center,astro)
            if state is None:
                qa["original_missing_tide"]+=1;continue
            label,h,_=state
            if label=="turning":
                qa["original_zero_tide_slope"]+=1;continue
            vel=phase.haversine_km(plat,plon,lat,lon)/(elapsed/60.)
            if not math.isfinite(vel):raise ValueError("Nonfinite original GPS speed")
            key=(bird,center.year,center.month,center.hour,v34.height_bin(h),
                 one_minute_bin(elapsed))
            col=0 if label=="ebb" else 1
            v=data[key][col]
            v[0]+=1;v[1]+=math.log1p(vel);v[2]+=elapsed;v[3]+=h
            qa["original_valid_tide_phase_local_pairs"]+=1
            qa["ebb_original_pairs" if col==0 else "flood_original_pairs"]+=1
    return data,dict(qa)

def minute_matched_pairs(accum):
    groups=collections.defaultdict(list)
    qa=collections.Counter()
    for (bird,year,month,clock,height,minute),(ebb,flood) in accum.items():
        if ebb[0]<2 or flood[0]<2:
            qa["one_minute_strata_insufficient_ebb_or_flood"]+=1;continue
        groups[bird].append({
          "log_speed":ebb[1]/ebb[0]-flood[1]/flood[0],
          "elapsed_minutes":ebb[2]/ebb[0]-flood[2]/flood[0],
          "water_height_m":ebb[3]/ebb[0]-flood[3]/flood[0],
          "n_ebb":ebb[0],"n_flood":flood[0],
        })
        qa["candidate_one_minute_matched_strata"]+=1
    retained={bird:rs for bird,rs in groups.items() if len(rs)>=MIN_PER_BIRD_MINUTE}
    qa["admitted_original_birds"]=len(retained)
    qa["admitted_one_minute_matched_strata"]=sum(len(rs) for rs in retained.values())
    qa["admitted_ebb_steps"]=sum(x["n_ebb"] for rs in retained.values() for x in rs)
    qa["admitted_flood_steps"]=sum(x["n_flood"] for rs in retained.values() for x in rs)
    return retained,dict(qa)

def minute_effect(matched,support):
    if (support["admitted_original_birds"]<MIN_SUPPORT_BIRDS or
        support["admitted_one_minute_matched_strata"]<MIN_TOTAL_STRATA):
        return {"status":"NOT_ADMITTED_V34B_ONE_MINUTE_DURATION_SUPPORT",
                "support":support,"any_one_minute_effect_reported":False}
    anon={}
    means=[]
    for ix,b in enumerate(sorted(matched)):
        rs=matched[b]
        mu=[float(np.mean([r[k] for r in rs]))
            for k in ("log_speed","elapsed_minutes","water_height_m")]
        means.append(mu)
        anon[f"bird_{ix+1:03d}"]={
             "one_minute_height_clock_matched_strata":len(rs),
             "ebb_minus_flood_log_speed":mu[0],
             "ebb_minus_flood_actual_elapsed_minutes":mu[1],
             "ebb_minus_flood_actual_water_height_m":mu[2]}
    mat=np.array(means)
    return {"status":"EXPLORATORY_POSTOUTCOME_ONE_MINUTE_DUTY_MATCHED_AUDIT",
            "support":support,
            "one_minute_time_bin_ties_to_lower_minute":True,
            "matched_effects":{
                "ebb_minus_flood_log1p_speed":equal_bird_summary(mat[:,0]),
                "ebb_minus_flood_elapsed_minutes":equal_bird_summary(mat[:,1]),
                "ebb_minus_flood_water_height_m":equal_bird_summary(mat[:,2])
             },
             "anonymized_source_bird_means":anon,
             "post_outcome_not_independent":True}

def run():
    astro,year_quality=tide.load_original_astronomy()
    with tempfile.TemporaryDirectory() as tmp:
        gps=v32.original_files_to_temp(Path(tmp))
        points,gps_qa=phase.read_original_valid_gps(gps)
    matched,original_gate=strict_v34_original_receipt(astro,year_quality,points,gps_qa)
    paired=same_bird_height_contrast(matched)
    duration_source,step_quality=minute_resolution_strata(points,astro)
    # Refuse any change to original source opportunity count.
    if step_quality["original_valid_tide_phase_local_pairs"]!=470685:
        raise ValueError("Previously frozen original ebb/flood source step opportunity changed")
    minute_birds,minute_support=minute_matched_pairs(duration_source)
    duration=minute_effect(minute_birds,minute_support)
    return {
        "status":"V34B_POSTOUTCOME_AUDITS_COMPLETED_WITH_FROZEN_V34_REPLAY",
        "original_v34_full_source_and_anonymous_receipt":original_gate,
        "original_source":"Zenodo 10053970 v4 + original Rijkswaterstaat 7-year 10-minute WATHTE astronomical",
        "original_RWS_annual_10minute_source_quality":year_quality,
        "original_source_GPS_quality":gps_qa,
        "strict_original_1min_source_coverage":step_quality,
        "same_original_bird_LOW_vs_HIGH_audit":paired,
        "same_original_1minute_GPS_duration_audit":duration,
        "registered_protocol":PROTOCOL,
        "no_raw_GPS_animal_ID_coordinate_UTC_or_tidal_time_series_exported":True,
        "original_v29_v30_v31_v32_v33_v34_results_unchanged":True,
        "limits":[
          "This audit was designed after observing original v34 height-band signs",
          "0.5m water-height threshold was chosen after original results, not biological preregistration",
          "One-minute duration bin does not exactly equal identical original timestamps or GPS error",
          "Only one original coastal population; same shared tides and observation process",
          "A speed difference does not label feeding, roosting, tidal prey exposure or social Boids causation",
        ]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,default=Path("validation_v34b/results/within_bird_height_one_minute_audit.json"))
    args=p.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    txt=json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
           prefix=".v34b-",delete=False) as f:
        f.write(txt);temp=Path(f.name)
    os.replace(temp,args.out)
    print("V34B_OLD_SOURCE_AND_BIRD_RECEIPT",json.dumps(out["original_v34_full_source_and_anonymous_receipt"],sort_keys=True))
    for label,key in (("V34B_SAME_BIRD_HEIGHT_AUDIT","same_original_bird_LOW_vs_HIGH_audit"),
                      ("V34B_ONE_MINUTE_DUTY_AUDIT","same_original_1minute_GPS_duration_audit")):
        x=out[key]
        scores=x.get("effects") or x.get("matched_effects")
        print(label,json.dumps({"status":x["status"],"support":x["support"],
              "effects":scores},sort_keys=True))
    print("V34B_COMPLETE_AGGREGATE_JSON",json.dumps(out,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
