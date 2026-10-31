#!/usr/bin/env python3
"""v45 post-outcome wild focal turning toward previous near vs far headings.

Replays all v43 and v44 old numerical wild source results BEFORE new turning
inferences. This is not a causal, independent or 3D social-force demonstration.
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
for path in ("validation_v44","validation_v43","validation_v40","validation_v42",
             "validation_v41","validation_v39","validation_v34","validation_v33",
             "validation_v32"):
    sys.path.insert(0,str(ROOT/path))
import balanced_near_far as v44
import near_heading as v43
import vector_history as v40
import conditional_history as v39
import ebb_flood_height_matched as old
import tidal_forecast as tide
import forecast as source

PREVIOUS_43=ROOT/"validation_v43/results/original_near_bird_heading_forecast_v43.json"
PREVIOUS_44=ROOT/"validation_v44/results/original_both_near_far_heading_v44.json"
PROTOCOL="docs/V45_ORIGINAL_TURN_TOWARD_NEIGHBOR_PROTOCOL.md"
MIN_MOVEMENT_KM=.05
MIN_OTHER_RESULTANT=.25
MIN_BIRDS=12
MIN_BIRD_STEPS=10
MIN_SOURCE_STEPS=2500
MIN_MONTHS=6
MIN_YEARS=2
BOOT=10000
SEED=20261031
SHAM=100
SHAM_MIN_BIRDS=10
SHAM_MIN_STEPS=1000
LABELS=("PRIMARY_NEAR_MINUS_FAR_TURN_CONVERGENCE",
        "secondary_NEAR_TURN_CONVERGENCE",
        "secondary_FAR_TURN_CONVERGENCE")

def source_replay(geo_files,astronomy,tideqa):
    (points,pinned,Y,dist,X40,indices40,_,prior_gate)=v43.replay_sources(
        geo_files,astronomy,tideqa)
    control,near,far,nmask,fmask,near_qa=v43.construct_source_neighbor_table(
        points,pinned)
    X,models=v43.model_matrix(X40,indices40,control,near,far)
    errors,angles,folds,fit_qa=v40.chronological_vector_forecast(
        pinned,X,Y,dist,models)
    original43=v43.evaluate(pinned,errors,angles,nmask,fmask)
    pinned43=json.loads(PREVIOUS_43.read_text())
    source_compare={
        "frozen_v41_v42_v33_v39_v40_all_source_receipts":prior_gate,
        "source_spatial_neighbor_time_support_before_behavior_score":near_qa,
        "source_chronological_month_7day_embargo_training_QA":fit_qa,
        "original_monthwise_model_fitting_counts":[
            {"year":r["year"],"month":r["month"],
             "all_original_future_start_episodes_tested":r["future_target_steps"],
             "prior_original_training_steps_before_7day_embargo":
              r["original_training_steps_before_7day_embargo"]}
            for r in folds],
        "observed_near_bird_direction_forecast":original43}
    for key,obj in source_compare.items():
        if not old.nested_close(obj,pinned43.get(key),1e-12):
            raise ValueError("Original v43 source or numerical per-bird receipt drift: "+key)
    original44=v44.matched_cohort_score(pinned,errors,angles,nmask,fmask)
    pinned44=json.loads(PREVIOUS_44.read_text())
    if not old.nested_close(original44,pinned44.get("matched_future_episode_score"),1e-12):
        raise ValueError("Original v44 balanced near/far 18-bird numeric receipt drift")
    eligible,original_idx,months,years,support=v44.target_indices(
        pinned,errors,nmask,fmask)
    if (original44["status"]!="EXPLORATORY_ORIGINAL_BOTH_OBSERVED_NEAR_FAR_HEADING_CONTRAST" or
        len(eligible)!=18 or len(original_idx)!=68232 or len(pinned["y"])!=328323):
        raise ValueError("Original v44 matching source and cohort not admitted")
    return pinned,Y,dist,X40,near,far,original_idx,{
        "status":"V41_V42_V33_V39_V40_V43_V44_COMPLETE_ORIGINAL_SOURCE_NUMERIC_REPLAY",
        "v43_original_cotimed_near_source_events":near_qa["near_source_starts_2010_2012"],
        "v43_original_4fix_source_episodes":len(pinned["y"]),
        "v44_original_balanced_birds":len(eligible),
        "v44_original_balanced_future_episodes":len(original_idx),
        "full_old_replays_absolute_tolerance":1e-12,
        "original_models_coefficients_and_training_UNCHANGED":True}

def normalize_rows(x):
    x=np.asarray(x,float)
    norm=np.linalg.norm(x,axis=1)
    out=np.zeros_like(x)
    has=norm>0
    out[has]=x[has]/norm[has,None]
    return out,norm

def direction_ready(pinned,Y,distance,X40,near,far,original):
    if Y.shape!=near.shape or near.shape!=far.shape:
        raise ValueError("Source direction arrays must share the original fixed episode count")
    past_duration_ix=v39.ENV_FIELDS.index(
        "prior_observed_device_pair_elapsed_minutes_over_30")
    previous_minutes=pinned["X"][:,past_duration_ix]*30
    past_speed=np.expm1(pinned["X"][:,-3])
    prev_distance=past_speed*previous_minutes/60
    if (np.any(previous_minutes<5-1e-8) or
        np.any(previous_minutes>30+1e-8) or
        not np.isfinite(prev_distance).all()):
        raise ValueError("Original previous-source fix duration/speed gate drift")
    prev_head=X40[:,-2:]
    next_head,_=normalize_rows(np.sinh(Y))
    near_head,near_strength=normalize_rows(near)
    far_head,far_strength=normalize_rows(far)
    keep=np.zeros(len(Y),bool);keep[original]=True
    qa={
       "original_v44_matched_future_steps_before_displacement_gates":len(original),
       "old_focal_step_displacement_ge_50m":int(np.sum(keep&(prev_distance>=MIN_MOVEMENT_KM))),
       "new_focal_step_displacement_ge_50m":int(np.sum(keep&(distance>=MIN_MOVEMENT_KM))),
       "source_near_mean_direction_resultant_ge_0p25":int(np.sum(keep&(near_strength>=MIN_OTHER_RESULTANT))),
       "source_far_mean_direction_resultant_ge_0p25":int(np.sum(keep&(far_strength>=MIN_OTHER_RESULTANT)))}
    keep &= (prev_distance>=MIN_MOVEMENT_KM)&(distance>=MIN_MOVEMENT_KM)&(
             near_strength>=MIN_OTHER_RESULTANT)&(far_strength>=MIN_OTHER_RESULTANT)
    idx=np.flatnonzero(keep)
    qa["all_prior_future_and_other_direction_gates_passed"]=len(idx)
    turn=next_head[idx]-prev_head[idx]
    if len(idx) and (np.linalg.norm(prev_head[idx],axis=1).min()<1-1e-8 or
                     np.linalg.norm(next_head[idx],axis=1).min()<1-1e-8):
        raise ValueError("Original nonzero movement has invalid prior/future unit heading")
    return idx,turn,near_head[idx],far_head[idx],qa

def eligible_birds(pinned,idx):
    bybird=collections.defaultdict(list)
    for i,sourceidx in enumerate(idx):
        bybird[int(pinned["bird"][sourceidx])].append(i)
    accepted={b:np.asarray(ix,dtype=int) for b,ix in bybird.items()
              if len(ix)>=MIN_BIRD_STEPS}
    selected=np.concatenate(list(accepted.values())) if accepted else np.array([],dtype=int)
    months=sorted({str(pinned["start"][idx[j]])[:7] for j in selected})
    years=sorted({int(str(pinned["start"][idx[j]])[:4]) for j in selected})
    return accepted,selected,months,years,{
       "source_birds_with_any_original_direction_data":len(bybird),
       "source_birds_with_10plus_original_direction_episodes":len(accepted),
       "original_direction_episodes_in_admitted_whole_birds":len(selected),
       "source_UTC_months":len(months),"source_UTC_years":years,
       "fixed_original_min_birds":MIN_BIRDS,"fixed_original_min_episodes":MIN_SOURCE_STEPS,
       "fixed_original_min_months":MIN_MONTHS,"fixed_original_min_years":MIN_YEARS}

def bird_summary(bird_effects,bootstrap):
    val=np.asarray(bird_effects,float)
    npositive=int(np.sum(val>0));nonzero=int(np.sum(val!=0))
    return {"equal_bird_mean":float(np.mean(val)),
        "paired_whole_bird_bootstrap_95":list(map(float,np.quantile(
             val[bootstrap].mean(axis=1),[.025,.975]))),
        "positive_original_birds":npositive,
        "negative_original_birds":int(np.sum(val<0)),
        "exact_one_sided_positive_bird_sign_tail":v39.sign_tail(npositive,nonzero)}

def sham(pinned,idx,turn,n,f,accepted):
    # Secondary negative-control ONLY. Does not change primary cohort or result.
    group=collections.defaultdict(list)
    slope_ix=v39.ENV_FIELDS.index("current_dH_m_per_h")
    for bird,positions in accepted.items():
        for p in positions:
            j=idx[p]
            date=pinned["start"][j].astype("datetime64[us]").astype(dt.datetime)
            slope=pinned["X"][j,slope_ix]
            kind="rising" if slope>0 else "falling" if slope<0 else "turning"
            group[(bird,date.year,date.month,date.hour//6,kind)].append(int(p))
    groups=[np.asarray(v,dtype=int) for v in group.values() if len(v)>=2]
    effective=np.concatenate(groups) if groups else np.array([],dtype=int)
    bybird=collections.defaultdict(list)
    for p in effective:bybird[int(pinned["bird"][idx[p]])].append(p)
    possible={b:np.array(a,dtype=int) for b,a in bybird.items()
              if len(a)>=MIN_BIRD_STEPS}
    total=sum(len(v) for v in possible.values())
    support={"sham_group_count_with_two_plus_original_episodes":len(groups),
             "source_permutable_episodes_before_bird_min":len(effective),
             "birds_with_10plus_permutable_source_episodes":len(possible),
             "original_permutable_episodes_in_accepted_birds":total,
             "fixed_sham_replicates":SHAM}
    if len(possible)<SHAM_MIN_BIRDS or total<SHAM_MIN_STEPS:
        return {"status":"NOT_ADMITTED_POSTOUTCOME_SHAM_SOURCE_SUPPORT",
                "support":support,"no_sham_effect_exported":True}
    ok=np.zeros(len(idx),dtype=bool)
    for positions in possible.values():ok[positions]=True
    selected_groups=[g for g in groups if np.all(ok[g])]
    birds=sorted(possible)
    dif=np.sum(turn*(n-f),axis=1)
    observed=float(np.mean([np.mean(dif[possible[b]]) for b in birds]))
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(SHAM):
        order=np.arange(len(idx))
        for g in selected_groups:order[g]=rng.permutation(g)
        sham_effect=np.sum(turn*(n[order]-f[order]),axis=1)
        null.append(float(np.mean([np.mean(sham_effect[possible[b]]) for b in birds])))
    return {"status":"DESCRIPTIVE_POSTOUTCOME_SAME_BIRD_MONTH_CLOCK_TIDE_SHUFFLE",
       "support":support,
       "observed_convergence_on_permutable_source_cohort":observed,
       "mean_100_permutations":float(np.mean(null)),
       "permutation_5_95_percentile":list(map(float,np.quantile(null,[.05,.95]))),
       "observed_minus_mean_sham":observed-float(np.mean(null)),
       "permutes_NEAR_and_FAR_other_heading_pairs_together":True,
       "coarse_clock_not_exact_location_or_wind_matched":True}

def evaluate(pinned,idx,turn,near,far,sourceqa):
    accepted,selected,months,years,support=eligible_birds(pinned,idx)
    support["source_direction_reliability_gates"]=sourceqa
    if (len(accepted)<MIN_BIRDS or len(selected)<MIN_SOURCE_STEPS or
        len(months)<MIN_MONTHS or len(years)<MIN_YEARS):
        return {"status":"NOT_ADMITTED_ORIGINAL_DIRECTION_CONVERGENCE",
                "support":support,"any_turning_effect_reported":False}
    near_c=np.sum(turn*near,axis=1)
    far_c=np.sum(turn*far,axis=1)
    differ=near_c-far_c
    if np.abs(differ[selected]).max()>4.000001:
        raise ValueError("Impossible cosine source turning amount")
    birds=sorted(accepted)
    matrix=np.array([[np.mean(differ[accepted[b]]),
                      np.mean(near_c[accepted[b]]),
                      np.mean(far_c[accepted[b]])] for b in birds])
    draw=np.random.default_rng(SEED).integers(0,len(birds),size=(BOOT,len(birds)))
    effects={label:bird_summary(matrix[:,k],draw)
             for k,label in enumerate(LABELS)}
    yearly=[]
    for yr in years:
        bv=[];count=0
        for b in birds:
            rows=[x for x in accepted[b] if int(str(pinned["start"][idx[x]])[:4])==yr]
            if rows:
                bv.append(float(np.mean(differ[rows])))
                count+=len(rows)
        if bv:yearly.append({"original_UTC_year":yr,
            "whole_birds":len(bv),"original_source_directional_steps":count,
            "equal_bird_NEAR_minus_FAR_convergence":float(np.mean(bv))})
    monthly=[]
    for period in months:
        rows=[p for p in selected if str(pinned["start"][idx[p]])[:7]==period]
        monthly.append(float(np.mean(differ[rows])))
    bs=np.random.default_rng(SEED).integers(0,len(months),size=(BOOT,len(months)))
    sh=sham(pinned,idx,turn,near,far,accepted)
    return {"status":"EXPLORATORY_WILD_NEAR_VS_FAR_FOCAL_TURNING_CONVERGENCE",
       "support":support,"primary_directional_convergence_orientation":LABELS[0],
       "all_three_frozen_signed_estimands":effects,
       "same_original_focal_before_and_after_direction_for_NEAR_and_FAR":True,
       "yearwise_source_descriptive":yearly,
       "calendar_month_descriptive":{
           "source_calendar_months":len(months),
           "equal_month_difference_not_equal_bird_primary":float(np.mean(monthly)),
           "naive_shared_month_bootstrap95":list(map(float,np.quantile(
               np.array(monthly)[bs].mean(axis=1),[.025,.975])))},
       "time_aligned_bird_clock_tide_sham":sh,
       "anonymous_bird_mean_convergence":{
            f"bird_{i+1:03d}":{"original_directional_steps":len(accepted[b]),
                "NEAR_minus_FAR_turn":float(matrix[i,0]),
                "NEAR_only_turn":float(matrix[i,1]),
                "FAR_only_turn":float(matrix[i,2])}
            for i,b in enumerate(birds)},
       "one_original_field_site_only":True,
       "no_GPS_ID_coordinate_exact_animal_UTC_or_per_episode_bearing_exported":True}

def run():
    astro,yearqa=tide.load_original_astronomy()
    with tempfile.TemporaryDirectory() as folder:
        files=source.original_files_to_temp(Path(folder))
        pinned,Y,dist,X40,near,far,originalidx,receipt=source_replay(files,astro,yearqa)
    idx,turn,n,f,gates=direction_ready(pinned,Y,dist,X40,near,far,originalidx)
    out=evaluate(pinned,idx,turn,n,f,gates)
    return {"status":out["status"],"protocol":PROTOCOL,
       "source":"SHA-pinned Zenodo 10053970 v4 Schiermonnikoog GPS and seven RWS astronomical tide years",
       "complete_old_v41_v42_v33_v39_v40_v43_v44_receipt":receipt,
       "original_untouched_v44_matched_source_opportunities":len(originalidx),
       "observed_orientation_association":out,
       "precommitted_distance_threshold_m":50,
       "precommitted_mean_other_bird_direction_resultant_threshold":MIN_OTHER_RESULTANT,
       "previous_v29_to_v44_source_and_numerical_results_unchanged":True,
       "no_original_animal_ID_GPS_UTC_position_heading_or_tide_heights_published":True,
       "limits":[
          "Post-outcome same population, not independent confirmation or causal alignment",
          "Full observation behavior is derived only from two originally recorded GPS points per segment",
          "Disjoint focal prior/future fixes reduce trivial overlap but not field/device autocorrelation",
          "Neighbor availability and directions vary by position, corridor, prey and source GPS duty",
          "Tide source does not provide pointwise real-time mudflat exposure",
          "Heading convergence is two-dimensional and not 3D ecological niche partition"]}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path,
          default=Path("validation_v45/results/original_near_far_turning_convergence_v45.json"))
    args=ap.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",
         dir=args.out.parent,prefix=".v45-",delete=False) as tmp:
        tmp.write(payload);name=Path(tmp.name)
    os.replace(name,args.out)
    print("V45_OLD_SOURCE_AND_SCORE_RECEIPTS",json.dumps(result["complete_old_v41_v42_v33_v39_v40_v43_v44_receipt"],sort_keys=True))
    out=result["observed_orientation_association"]
    print("V45_SOURCE_DIRECTION_SUPPORT",json.dumps(out["support"],sort_keys=True))
    print("V45_STATUS",result["status"])
    if out.get("all_three_frozen_signed_estimands"):
        print("V45_OBSERVED_TURN_CONVERGENCE",json.dumps(out["all_three_frozen_signed_estimands"],sort_keys=True))
        print("V45_POSTOUTCOME_SHAM",json.dumps(out["time_aligned_bird_clock_tide_sham"],sort_keys=True))
    else:
        print("V45_NO_NEW_TURNING_SCORE",json.dumps(out,sort_keys=True))
    print("V45_FULL_ANON_AGGREGATE",json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    main()
