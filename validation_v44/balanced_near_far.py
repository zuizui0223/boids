#!/usr/bin/env python3
"""v44: BOTH-observed-source NEAR≤200m & FAR≥1km headings on SAME heldout episodes.

Post-v43 descriptive, exploratory: no retraining/change to v43 S0..S3
coefficient/target/control specifications. Verifies entire source original
v43 result within 1e-12 BEFORE any new balanced subset MSE is reported.
"""
from __future__ import annotations
import argparse
import collections
import json
import os
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
for p in ("validation_v43","validation_v40","validation_v42","validation_v41",
          "validation_v39","validation_v34","validation_v33","validation_v32"):
    sys.path.insert(0,str(ROOT/p))
import near_heading as prior
import vector_history as vector
import tidal_forecast as tide
import forecast as source
import conditional_history as past
import ebb_flood_height_matched as original_gate

PROTOCOL="docs/V44_BALANCED_NEAR_FAR_ORIGINAL_GPS_PROTOCOL.md"
V43_RECEIPT=ROOT/"validation_v43/results/original_near_bird_heading_forecast_v43.json"
ORIGINAL_V43_EXPECTED_SOURCE_EPISODES=328323
ORIGINAL_V43_EXPECTED_NEAR_CANDIDATES=171041
BOOTS=10000
SEED=20261031
MIN_BIRDS=15
MIN_ORIGINAL_FUTURE_STEPS=25000
MIN_BIRD_STEPS=30
MIN_CALENDAR_MONTHS=8
MIN_YEARS=2
MIN_ANGLE_BIRDS=15
MIN_ANGLE_STEPS_PER_BIRD=20
MIN_ANGULAR_TOTAL=8000
MODELS=prior.MODELS
PRIMARY="PRIMARY_NEAR_GAIN_MINUS_FAR_GAIN_MATCHED_BOTH"
CONTRASTS=(
    (PRIMARY,2,1), # (S0-S1)-(S0-S2) = S2-S1
    ("SECONDARY_S0_MINUS_S1_NEAR",0,1),
    ("SECONDARY_S0_MINUS_S2_FAR",0,2),
    ("SECONDARY_S2_MINUS_S3_NEAR_AFTER_FAR",2,3),
    ("SECONDARY_S1_MINUS_S3_FAR_AFTER_NEAR",1,3),
)

def replay_previous_original_before_balanced_scoring(files,astro,tideqa):
    points,pinned,Y,dist,X40,idx40,old_error,oldgate=prior.replay_sources(
        files,astro,tideqa)
    ctx,nd,fd,near,far,sourceqa=prior.construct_source_neighbor_table(
        points,pinned)
    X,cols=prior.model_matrix(X40,idx40,ctx,nd,fd)
    errors,angles,folds,fitqa=vector.chronological_vector_forecast(
        pinned,X,Y,dist,cols)
    original=prior.evaluate(pinned,errors,angles,near,far)
    saved=json.loads(V43_RECEIPT.read_text(encoding="utf-8"))
    checks={
       "frozen_v41_v42_v33_v39_v40_all_source_receipts":oldgate,
       "source_spatial_neighbor_time_support_before_behavior_score":sourceqa,
       "source_chronological_month_7day_embargo_training_QA":fitqa,
       "original_monthwise_model_fitting_counts":[
         {"year":x["year"],"month":x["month"],
          "all_original_future_start_episodes_tested":x["future_target_steps"],
          "prior_original_training_steps_before_7day_embargo":
               x["original_training_steps_before_7day_embargo"]}
         for x in folds],
       "observed_near_bird_direction_forecast":original,
    }
    for label,obj in checks.items():
        if not original_gate.nested_close(obj,saved.get(label),1e-12):
            raise ValueError("OLD original v43 source/per-bird/model receipt drift: "+label)
    if (len(pinned["y"])!=ORIGINAL_V43_EXPECTED_SOURCE_EPISODES or
        sourceqa["near_source_starts_2010_2012"]!=ORIGINAL_V43_EXPECTED_NEAR_CANDIDATES or
        original["status"]!="EXPLORATORY_WILD_NEAR_BIRD_PAST_HEADING_PREDICTIVE_TEST" or
        original["support"]["original_birds_with_30plus_heldout_near_steps"]!=20 or
        original["support"]["original_200m_heldout_vector_step_episodes"]!=171013):
        raise ValueError("Original v43 entire source or score cohort drift")
    replay={
       "status":"V43_COMPLETE_FROZEN_ORIGINAL_GPS_RWS_V41_V42_V39_V40_SCORE_REPLAY",
       "original_v43_num_4fix_source_episodes":len(pinned["y"]),
       "original_2010_2012_200m_source_candidates":sourceqa["near_source_starts_2010_2012"],
       "original_v43_near_only_heldout_birds":original["support"]["original_birds_with_30plus_heldout_near_steps"],
       "original_v43_near_only_heldout_steps":original["support"]["original_200m_heldout_vector_step_episodes"],
       "full_anonymous_v43_numerical_receipt_abs_tolerance":1e-12,
       "source_previous_results_v29_to_v43_unchanged":True,
    }
    return pinned,errors,angles,near,far,replay

def signed_score(matrix,resamples,contrast_list=CONTRASTS):
    if not len(matrix) or not np.isfinite(matrix).all():
        raise ValueError("Original future MSE per bird missing/nonfinite")
    output={}
    for label,left,right in contrast_list:
        effect=matrix[:,left]-matrix[:,right]
        nplus=int(np.sum(effect>0));nnon=int(np.sum(effect!=0))
        output[label]={
            "equal_bird_mean_MSE_gain":float(effect.mean()),
            "whole_bird_paired_bootstrap_95":list(map(float,
                     np.quantile(effect[resamples].mean(axis=1),[.025,.975]))),
            "positive_original_birds":nplus,
            "negative_original_birds":int(np.sum(effect<0)),
            "nonzero_original_birds":nnon,
            "one_sided_positive_sign_p":past.sign_tail(nplus,nnon)
        }
    return output

def target_indices(pinned,errs,near,far):
    if len(errs)!=len(near) or len(near)!=len(far):
        raise ValueError("v43 original complete source episode/neighbor masks mismatch")
    mask=np.isfinite(errs).all(axis=1)&near&far
    bybird=collections.defaultdict(list)
    for i in np.flatnonzero(mask):
        bybird[int(pinned["bird"][i])].append(int(i))
    eligible={b:np.array(ix,dtype=int) for b,ix in bybird.items()
              if len(ix)>=MIN_BIRD_STEPS}
    all_index=np.concatenate(list(eligible.values())) if eligible else np.array([],dtype=int)
    years=sorted({int(str(pinned["start"][i])[:4]) for i in all_index})
    months=sorted({str(pinned["start"][i])[:7] for i in all_index})
    support={
       "both_near_200m_and_far_1km_available_before_bird_gate":int(np.sum(mask)),
       "whole_birds_with_any_BOTH_observed_heldout_step":len(bybird),
       "whole_birds_with_30plus_BOTH_observed_heldout_steps":len(eligible),
       "original_heldout_BOTH_near_far_step_episodes_after_bird_gate":len(all_index),
       "source_UTC_calendar_months":len(months),
       "source_UTC_years":years,
       "required_min_birds":MIN_BIRDS,
       "required_min_future_steps":MIN_ORIGINAL_FUTURE_STEPS,
       "required_min_months":MIN_CALENDAR_MONTHS,
       "required_min_years":MIN_YEARS,
       "all_four_original_v43_models_same_matched_episode_indices":True,
       "all_source_matched_near_far_heading_available_by_forecast_start":True,
       "source_original_far_coverage_confounded_v43_near_only_result":True}
    return eligible,all_index,months,years,support

def matched_cohort_score(pinned,errors,angles,near,far):
    eligible,all_index,months,years,support=target_indices(
        pinned,errors,near,far)
    if (len(eligible)<MIN_BIRDS or len(all_index)<MIN_ORIGINAL_FUTURE_STEPS or
        len(months)<MIN_CALENDAR_MONTHS or len(years)<MIN_YEARS):
        return {
           "status":"NOT_ADMITTED_BALANCED_NEAR_FAR_ORIGINAL_HELDOUT_SUPPORT",
           "matched_source_eligibility":support,
           "any_directional_MSE_or_angular_effect_exported":False}
    birds=sorted(eligible)
    mat=np.array([errors[eligible[b]].mean(axis=0) for b in birds])
    bstrap=np.random.default_rng(SEED).integers(0,len(birds),
                                             size=(BOOTS,len(birds)))
    contrasts=signed_score(mat,bstrap)
    ang_elig={}
    for bird in birds:
        good=eligible[bird][np.isfinite(angles[eligible[bird],0])]
        if len(good)>=MIN_ANGLE_STEPS_PER_BIRD:
            ang_elig[bird]=good
    angular_support={
       "source_birds_with_20plus_moving_future_steps":len(ang_elig),
       "true_moving_gps_50m_plus_future_steps":sum(len(x) for x in ang_elig.values()),
       "all_models_same_source_moving_targets":True,
       "fixed_future_true_displacement_min_m":50}
    if (len(ang_elig)<MIN_ANGLE_BIRDS or
        angular_support["true_moving_gps_50m_plus_future_steps"]<MIN_ANGULAR_TOTAL):
        angular={"status":"NOT_ADMITTED_BALANCED_NEAR_FAR_ANGULAR_SUPPORT",
            "support":angular_support,"any_angular_effect_exported":False}
    else:
        names=sorted(ang_elig)
        ma=np.array([angles[ang_elig[b]].mean(axis=0) for b in names])
        draw=np.random.default_rng(SEED).integers(0,len(names),size=(BOOTS,len(names)))
        angular={
          "status":"EXPLORATORY_BALANCED_NEAR_FAR_DIRECTION_ONLY_SCORE",
          "support":angular_support,
          "all_four_original_model_equal_bird_angular_loss":list(map(float,ma.mean(axis=0))),
          "all_fixed_angular_signs":signed_score(ma,draw)}
    annual=[]
    for year in years:
        vals=[]
        count=0
        for b in birds:
            idx=[i for i in eligible[b] if int(str(pinned["start"][i])[:4])==year]
            if idx:
                vals.append(errors[idx].mean(axis=0))
                count+=len(idx)
        if vals:
            ma=np.array(vals)
            annual.append({
              "year":year,"original_source_birds":len(vals),
              "original_BOTH_near_and_far_heldout_steps":count,
              "equal_bird_MSE_S0_S1_S2_S3":list(map(float,ma.mean(axis=0))),
              "PRIMARY_NEAR_minus_FAR_gain":float((ma[:,2]-ma[:,1]).mean()),
              "source_one_coastal_population_not_independent_years":True})
    month_effect=[]
    for month in months:
        ix=np.array([i for i in all_index if str(pinned["start"][i])[:7]==month],dtype=int)
        month_effect.append(float(np.mean(errors[ix,2]-errors[ix,1])))
    p=np.asarray(month_effect)
    bs=np.random.default_rng(SEED).integers(0,len(p),size=(BOOTS,len(p)))
    monthqa={
      "original_UTC_months":len(months),
      "equal_month_primary_NEAR_minus_FAR_gain":float(p.mean()),
      "naive_month_bootstrap95_source_shared_nonindependent":list(map(float,
                                    np.quantile(p[bs].mean(axis=1),[.025,.975]))),
      "not_same_estimand_as_equal_original_bird_primary":True}
    return {
       "status":"EXPLORATORY_ORIGINAL_BOTH_OBSERVED_NEAR_FAR_HEADING_CONTRAST",
       "matched_source_eligibility":support,
       "original_source_BOTH_heading_availability_100pct_in_matched_targets":True,
       "registered_primary_contrast":PRIMARY,
       "model_order_exactly_previous_v43":list(MODELS),
       "absolute_equal_original_bird_2D_vector_MSE_S0_S1_S2_S3":list(map(float,mat.mean(axis=0))),
       "all_fixed_signed_vector_MSE_comparisons":contrasts,
       "moving_target_angular_secondary":angular,
       "yearwise_source_descriptive":annual,
       "monthwise_source_descriptive":monthqa,
       "anonymous_original_bird_balanced_MSE":{
          f"bird_{i+1:03d}":{
            "matched_BOTH_heading_original_future_episodes":len(eligible[b]),
            "equal_bird_MSE_S0_S1_S2_S3":list(map(float,mat[i]))
          } for i,b in enumerate(birds)},
       "whole_original_bird_bootstrap_reps":BOOTS,
       "bootstrap_rng_seed":SEED,
       "post_v43_same_source_NOT_independent_confirmatory":True,
       "no_original_GPS_ID_coordinate_UTC_heading_or_tide_series_exported":True
    }

def run():
    astronomy,tideqa=tide.load_original_astronomy()
    with tempfile.TemporaryDirectory() as folder:
        gps=source.original_files_to_temp(Path(folder))
        original,errors,angles,near,far,replay=\
            replay_previous_original_before_balanced_scoring(gps,astronomy,tideqa)
    result=matched_cohort_score(original,errors,angles,near,far)
    return {
      "status":result["status"],
      "protocol":PROTOCOL,
      "source":"same exact original Zenodo 10053970 v4 and RWS astronomical 7yrs as v43",
      "replayed_prior_v41_v42_v33_v39_v40_v43_full_source_and_score_receipt":replay,
      "prior_model_coefficients_and_full_training_cohort_UNCHANGED":True,
      "original_model_outcome":"heldout next-recorded-GPS-step asinh E/N velocity vector (not free-running future location)",
      "registered_primary":"(S0−S1 NEAR gain)−(S0−S2 FAR gain)=S2−S1",
      "matched_future_episode_score":result,
      "no_original_animal_GPS_ID_coordinates_UTC_or_RWS_tide_exported":True,
      "prior_v29_to_v43_GitHub_models_source_and_results_unchanged":True,
      "cautions":[
        "This is after seeing v43 model rankings on the same original study, not independent field confirmation",
        "Both near and far available is a selected subset; not randomly assigned or representative of all wild bird movement",
        "Far and near bird identities, counts, landcover, wake, wind, movement corridors and GPS source duty remain different",
        "Whole-bird bootstrap and per-month diagnostics are not independent ecosystems",
        "A 2D near-heading gain does not identify direct social force or 3D Reynolds alignment",
        "Future GPS target conditional on next fix 5-30min later, its actual interval not in source predictors",
        "Any result concerning shared direction cannot be labeled actual prey accessibility or cognitive learning"]}
def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--out",type=Path,
         default=Path("validation_v44/results/original_both_near_far_heading_v44.json"))
    args=a.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
                                    prefix=".v44-",delete=False) as f:
        f.write(payload);temporary=Path(f.name)
    os.replace(temporary,args.out)
    print("V44_COMPLETE_OLD_V43_REPLAY",json.dumps(
        result["replayed_prior_v41_v42_v33_v39_v40_v43_full_source_and_score_receipt"],sort_keys=True))
    obs=result["matched_future_episode_score"]
    print("V44_BALANCED_SOURCE_SUPPORT",json.dumps(obs["matched_source_eligibility"],sort_keys=True))
    print("V44_STATUS",result["status"])
    if obs.get("all_fixed_signed_vector_MSE_comparisons"):
        print("V44_MATCHED_ABSOLUTE_MSE",json.dumps(
            obs["absolute_equal_original_bird_2D_vector_MSE_S0_S1_S2_S3"]))
        print("V44_ALL_FIXED_MATCHED_CONTRASTS",json.dumps(
            obs["all_fixed_signed_vector_MSE_comparisons"],sort_keys=True))
        print("V44_ANGULAR",json.dumps(obs["moving_target_angular_secondary"],sort_keys=True))
        print("V44_ANNUAL",json.dumps(obs["yearwise_source_descriptive"],sort_keys=True))
    else:print("V44_NO_NEW_MATCHED_SOCIAL_SCORE",json.dumps(obs,sort_keys=True))
    print("V44_FULL_SOURCE_SAFE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
