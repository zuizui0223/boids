"""v60: source-blind reassembly and genuinely observed opposite-phase B->C headings.

Never publish original match indices, original bird IDs, source coordinates,
times, pair-specific headings, model coefficients or gauge measurements.
v59 frozen source pairing is replayed and verified before opening targets.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from itertools import product
from math import acos, degrees
import numpy as np

import matched_tide_support as v59

SEED=20261107
EXPECTED_AMELAND={
    "source_rows":4678,
    "source_birds":5,
    "unique_disjoint_actual_opposite_tide_pairs":168,
    "birds_with_at_least_ten_pairs":5,
    "matched_distinct_ISO_weeks":46,
    "matched_distinct_calendar_months":11}
EXPECTED_STAGE_COUNTS=(1991,1319,1303,942,550,240,182)
METRICS=("observed_paired_tide_direction_concordance",
         "actual_vs_flipped_tide_cosine_loss_gain",
         "observed_paired_absolute_heading_separation_degrees",
         "orthogonal_direction_projection")

def reconstruct_private_pair_indices(rows):
    """Reproduce v59 greedy B-only pairs, independently compare source receipt.

    Return indices only in ephemeral private Python; never include in JSON.
    """
    states=[v59._state(r) for r in rows]
    if len({(s["bird"],s["t"]) for s in states})!=len(states):
        raise ValueError("SOURCE_STOP_DUPLICATE_2011_ORIGINAL_B")
    grouped=defaultdict(lambda:{1:[],-1:[]})
    for i,s in enumerate(states):
        grouped[(s["bird"],s["cell"])][s["phase"]].append((s,i))
    pairs=[]
    stages=Counter()
    for key in sorted(grouped):
        rising=sorted(grouped[key][1],key=lambda z:z[0]["t"])
        falling=sorted(grouped[key][-1],key=lambda z:(z[0]["h"],z[0]["t"]))
        if not falling:continue
        heights=[s["h"] for s,_ in falling]
        used=set()
        for plus,ip in rising:
            stages[v59.STAGES[0]]+=1
            lo=bisect_left(heights,plus["h"]-v59.HEIGHT_TOL_M-1e-12)
            hi=bisect_right(heights,plus["h"]+v59.HEIGHT_TOL_M+1e-12)
            flags=[False]*6
            options=[]
            for j in range(lo,hi):
                minus,im=falling[j]
                d=v59._different(plus,minus)
                active=True
                for step,check in enumerate(v59._conditions(d)):
                    active=active and check
                    if active:flags[step]=True
                    else:break
                if active and j not in used:
                    cost=(d[0]/v59.HEIGHT_TOL_M)**2+(d[2]/v59.DOY_TOL_DAYS)**2
                    cost+=(d[3]/v59.CLOCK_TOL_H)**2
                    cost+=(d[4]/v59.PRIOR_ANGLE_TOL_DEG)**2
                    cost+=(d[5]/v59.PRIOR_LOG_SPEED_TOL)**2
                    options.append((cost,minus["t"],j,im))
            for idx,ok in enumerate(flags):
                if ok:stages[v59.STAGES[idx+1]]+=1
            if options:
                _,_,j,im=min(options)
                used.add(j)
                pairs.append((ip,im))
    old=v59.audit_source_only(rows)
    all_counts={stage:stages[stage] for stage in v59.STAGES}
    if all_counts!=old["rising_rows_with_candidate_after_sequential_gates"]:
        raise ValueError("SOURCE_STOP_V59_MATCH_STAGE_RECEIPT_DIVERGED")
    if len(pairs)!=old["unique_disjoint_actual_opposite_tide_pairs"]:
        raise ValueError("SOURCE_STOP_V59_PAIR_COUNT_DIVERGED")
    keys=[s["bird"] for s in states]
    bybird=Counter(keys[p] for p,_ in pairs)
    if len(bybird)!=old["matched_birds"]:
        raise ValueError("SOURCE_STOP_V59_MATCHED_BIRD_COUNT_DIVERGED")
    used_indices=[i for p in pairs for i in p]
    if len(set(used_indices))!=len(used_indices):
        raise ValueError("SOURCE_STOP_MATCH_REUSED_GPS_EPISODE")
    for i,j in pairs:
        if keys[i]!=keys[j] or states[i]["cell"]!=states[j]["cell"] or states[i]["phase"]!=1 or states[j]["phase"]!=-1:
            raise ValueError("SOURCE_STOP_NOT_AN_ORIGINAL_OPPOSITE_PHASE_PAIR")
        if not all(v59._conditions(v59._different(states[i],states[j]))):
            raise ValueError("SOURCE_STOP_ORIGINAL_MATCH_CONDITIONS_VIOLATED")
    return pairs,old

def verify_frozen_primary_source(rows,pairs,audit):
    if audit["admission"]!="SOURCE_SUPPORT_ADMITTED_FOR_LATER_PREREGISTERED_OUTCOME":
        raise ValueError("NOT_ADMITTED_V59_SOURCE_ONLY_GATE")
    for k,v in EXPECTED_AMELAND.items():
        if audit.get(k)!=v:
            raise ValueError("SOURCE_STOP_FROZEN_V59_AMELAND_AGGREGATE_DRIFT: "+k)
    if tuple(audit["rising_rows_with_candidate_after_sequential_gates"][s] for s in v59.STAGES)!=EXPECTED_STAGE_COUNTS:
        raise ValueError("SOURCE_STOP_FROZEN_V59_STAGE_COUNTS_DRIFT")
    if len(pairs)!=EXPECTED_AMELAND["unique_disjoint_actual_opposite_tide_pairs"]:
        raise ValueError("SOURCE_STOP_FROZEN_V59_PRIVATE_PAIR_COUNT_DRIFT")
    return True

def _unit(values,name):
    a=np.asarray(values,dtype=float)
    if a.ndim!=2 or a.shape[1]!=2 or not np.isfinite(a).all():
        raise ValueError("ESTIMAND_STOP_INVALID_"+name+"_VECTOR")
    n=np.linalg.norm(a,axis=1)
    if (n<=1e-10).any():
        raise ValueError("ESTIMAND_STOP_ZERO_"+name+"_VECTOR")
    return a/n[:,None]

def _bootstrap_stats(rows,pairs,data,bird_draws,week_draws,seed):
    birds=defaultdict(list)
    weeks=defaultdict(lambda:defaultdict(list))
    for k,(p,_m) in enumerate(pairs):
        bird=rows[p]["id"]
        week=rows[p]["t"].isocalendar()[:2] # predeclared rising-B week
        birds[bird].append(data[k])
        weeks[week][bird].append(data[k])
    bird_mat=np.asarray([np.mean(v,axis=0) for v in birds.values()])
    week_mat=np.asarray([np.mean([np.mean(v,axis=0) for v in birds.values()],axis=0)
                         for birds in weeks.values()])
    if bird_mat.shape!=(len(birds),len(METRICS)) or week_mat.shape[1]!=len(METRICS):
        raise ValueError("ESTIMAND_STOP_AGGREGATE_SHAPE")
    rng=np.random.default_rng(seed)
    boot_b=np.mean(bird_mat[rng.integers(len(bird_mat),size=(bird_draws,len(bird_mat)))],axis=1)
    boot_w=np.mean(week_mat[rng.integers(len(week_mat),size=(week_draws,len(week_mat)))],axis=1)
    out={}
    for j,k in enumerate(METRICS):
        out[k]={
            "equal_bird_mean":float(bird_mat[:,j].mean()),
            "whole_bird_bootstrap_95":np.quantile(boot_b[:,j],[.025,.975]).tolist(),
            "positive_birds":int((bird_mat[:,j]>0).sum()),
            "separate_equal_week_then_bird_mean":float(week_mat[:,j].mean()),
            "whole_week_bootstrap_95":np.quantile(boot_w[:,j],[.025,.975]).tolist(),
            "positive_weeks":int((week_mat[:,j]>0).sum())}
    means=bird_mat[:,0]
    obs=means.mean()
    null=np.array([np.mean(means*np.asarray(signs)) for signs in product((-1,1),repeat=len(means))])
    out["observed_paired_tide_direction_concordance"]["equal_bird_one_sided_sign_flip_sensitivity_p"]=float(np.mean(null>=obs-1e-14))
    out["observed_paired_tide_direction_concordance"]["exact_bird_sign_flip_combinations"]=len(null)
    return out

def score_matched_observed_heading(train,test,pairs,forecast_fn,*,bird_draws=10000,week_draws=4000,seed=SEED):
    """Read observed next-heading targets only AFTER matching and source admission."""
    if not train or not test or not pairs:
        raise ValueError("ESTIMAND_STOP_MISSING_ADMITTED_SOURCE")
    n=len(test)
    rising=[{**r,"phase":1} for r in test]
    falling=[{**r,"phase":-1} for r in test]
    # ONE fixed original 2010 ridge model fit; all three evaluated in one call.
    pred=np.asarray(forecast_fn(train,list(test)+rising+falling,1),dtype=float)
    if pred.shape!=(3*n,2):
        raise ValueError("ESTIMAND_STOP_MODEL_PREDICTION_SHAPE")
    actual=_unit(pred[:n],"ACTUAL")
    plus=_unit(pred[n:2*n],"RISING")
    minus=_unit(pred[2*n:],"FALLING")
    actual_signs=np.asarray([r["phase"] for r in test])
    if not np.allclose(actual,np.where(actual_signs[:,None]==1,plus,minus),
                       atol=1e-10,rtol=1e-10):
        raise ValueError("ESTIMAND_STOP_REAL_PHASE_MODEL_REPLAY")
    obs=_unit([[r["target_e"],r["target_n"]] for r in test],"OBSERVED")
    pairvals=np.zeros((len(pairs),len(METRICS)),dtype=float)
    diffs=[]
    zero_g=0
    for k,(ip,im) in enumerate(pairs):
        if (test[ip]["id"]!=test[im]["id"]
            or test[ip]["phase"]!=1 or test[im]["phase"]!=-1):
            raise ValueError("ESTIMAND_STOP_UNMATCHED_ORIGINAL_PAIR")
        g=((plus[ip]-minus[ip])+(plus[im]-minus[im]))/2.
        d=obs[ip]-obs[im]
        pairvals[k,0]=float(np.dot(d,g)/4.)
        actualgain=(float(np.dot(obs[ip],actual[ip]-minus[ip]))+
                    float(np.dot(obs[im],actual[im]-plus[im])))/2.
        pairvals[k,1]=actualgain
        pairvals[k,2]=degrees(acos(float(np.clip(np.dot(obs[ip],obs[im]),-1.,1.))))
        pairvals[k,3]=float(np.dot(d,[-g[1],g[0]])/4.)
        zero_g+=int(float(np.linalg.norm(g))<=1e-10)
        a=v59._state(test[ip])
        b=v59._state(test[im])
        diffs.append(v59._different(a,b))
    out={
        "endpoint":"V60_ACTUALLY_OBSERVED_OPPOSITE_PHASE_PAIRED_NEXT_HEADING",
        "source_test_year":2011,"source_train_year":2010,
        "actual_real_disjoint_matched_pairs":len(pairs),
        "original_test_rows_unchanged":n,
        "model_fit_once_on_original_2010":True,
        "all_actual_sign_predictions_exactly_replayed":True,
        "paired_score_range":[-1.,1.],
        "zero_model_switch_pairs_scored_zero_not_dropped":zero_g,
        "matching_has_no_future_heading_access":True,
        "primary":"observed_paired_tide_direction_concordance",
        "metrics":_bootstrap_stats(test,pairs,pairvals,bird_draws,week_draws,seed),
        "original_matched_B_state_difference_aggregate_only":{},
        "limitations":"Matched real rising/falling observed GPS headings; association with a 2010-fitted phase-response direction, NOT observed causal steering or prey-front or social Boids force."}
    arr=np.asarray(diffs)
    for j,metric in enumerate(("water_height_abs_m","separated_time_hours","cyclic_season_days",
                               "cyclic_UTC_diel_hours","prior_heading_angle_degrees",
                               "prior_log1p_speed_difference")):
        out["original_matched_B_state_difference_aggregate_only"][metric]={
            "mean":float(arr[:,j].mean()),"median":float(np.median(arr[:,j])),
            "max":float(arr[:,j].max())}
    x=out["metrics"][out["primary"]]
    out["observational_concordance_status"]=(
        "POSITIVE_CONCORDANCE_EXPLORATORY" if x["equal_bird_mean"]>0 and
            x["whole_bird_bootstrap_95"][0]>0 else
        "NO_ROBUST_POSITIVE_CONCORDANCE")
    return out
