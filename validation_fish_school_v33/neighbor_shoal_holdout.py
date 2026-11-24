"""v33 original 84 EIDC trials/12 genuine original shoals, local3 beyond-global.

Strict source-level original trial checks and same true original group holdouts.
Uses exact v32 training-only summary-stat Ridge. Never claim causal social
force, neural memory, fish chorus or independent study-level meta effect.
"""
from __future__ import annotations
import json
import numpy as np
from pathlib import Path
from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v32.moment_loo import (
    file_moment,sum_moments,train_only_standardized_ridge,score_file_moment,
    bootstrap_group_differences
)
from validation_fish_school_v33.neighbor_panels import PANELS

TARGET_HORIZONS=("short","delayed")
CONTRAST_KEYS=(
  "NEAR_ADDITIONAL_BEYOND_GLOBAL",
  "TRUE_NEAR_VERSUS_ROTATED_ONE",
  "TRUE_NEAR_VERSUS_FAR3",
  "CURRENT_NEAR_VERSUS_AGE02_NEAR",
  "FAR3_ADDITIONAL_BEYOND_GLOBAL"
)
EXPECTED_V32={
 "short":{"G_geometry":3407.0695372716236,"GLOBAL":3344.9187577732027},
 "delayed":{"G_geometry":8925.030228272999,"GLOBAL":8479.996942316231}
}
BASELINE_ABS_MAX_ERROR=.02

def file_moments(source):
    if tuple(source["X"])!=PANELS or source["Y"].shape[1]!=4:
        raise SourceStop("V33_ORIGINAL_FROZEN_SOURCE_PANEL_SET_CHANGED")
    out={name:file_moment(source["X"][name],source["Y"]) for name in PANELS}
    if len({x["n"] for x in out.values()})!=1:
        raise SourceStop("V33_ORIGINAL_FILES_NO_SHARED_PANELS_COHORT")
    return out

def source_group_holdout(file_stats,original_groupmap,source_metadata):
    names=set(original_groupmap)
    if len(names)!=84 or set(file_stats)!=names:
        raise SourceStop("V33_ORIGINAL_84_TRIALS_NOT_ALL_SCORED")
    gids=sorted(set(original_groupmap.values()),key=int)
    if gids!=[str(i) for i in range(1,13)]:
        raise SourceStop("V33_ORIGINAL_12_AUTHOR_GROUP_IDS_NOT_MATCHED")
    if any(tuple(x)!=PANELS for x in file_stats.values()):
        raise SourceStop("V33_SOURCE_MOMENT_PANEL_ORDER_CHANGED")
    folds=[]
    for held in gids:
        testfiles=sorted((n for n in names if original_groupmap[n]==held),key=lambda n:int(n[:-4]))
        trainfiles=sorted((n for n in names if original_groupmap[n]!=held),key=lambda n:int(n[:-4]))
        trainIDs={original_groupmap[n] for n in trainfiles}
        if len(trainIDs)!=11 or held in trainIDs or not testfiles:
            raise SourceStop("V33_ORIGINAL_BIOLOGICAL_SHOAL_LEAKAGE")
        fold={
          "original_heldout_shoal_ID":held,
          "source_original_test_trial_IDs":testfiles,
          "n_source_original_heldout_trials":len(testfiles),
          "source_train_original_shoal_IDs":sorted(trainIDs,key=int),
          "train_and_test_biological_shoal_overlap":False,
          "original_equal_trial_within_shoal_MSE":{}
        }
        for panel in PANELS:
            pooled=sum_moments([file_stats[n][panel] for n in trainfiles])
            B,b=train_only_standardized_ridge(pooled)
            testscore=[score_file_moment(file_stats[n][panel],B,b) for n in testfiles]
            fold["original_equal_trial_within_shoal_MSE"][panel]={
                h:float(np.mean([v[h] for v in testscore])) for h in TARGET_HORIZONS
            }
        folds.append(fold)
    return summarize(folds,source_metadata)

def summaries_from_mse(mse):
    return {
       "NEAR_ADDITIONAL_BEYOND_GLOBAL":mse["GLOBAL"]-mse["NEAR_TRUE"],
       "TRUE_NEAR_VERSUS_ROTATED_ONE":mse["NEAR_ROT1"]-mse["NEAR_TRUE"],
       "TRUE_NEAR_VERSUS_FAR3":mse["FAR_TRUE"]-mse["NEAR_TRUE"],
       "CURRENT_NEAR_VERSUS_AGE02_NEAR":mse["NEAR_STALE_0.2S"]-mse["NEAR_TRUE"],
       "FAR3_ADDITIONAL_BEYOND_GLOBAL":mse["GLOBAL"]-mse["FAR_TRUE"]
    }

def summarize(folds,source_metadata):
    if len(folds)!=12 or sorted([z["original_heldout_shoal_ID"] for z in folds],key=int)!=[
            str(i) for i in range(1,13)]:
        raise SourceStop("V33_EXACT_ORIGINAL_12_SHOAL_TESTS_REQUIRED")
    out={}
    for h in TARGET_HORIZONS:
        m={panel:float(np.mean([f["original_equal_trial_within_shoal_MSE"][panel][h]
                                 for f in folds])) for panel in PANELS}
        for k,previous in EXPECTED_V32[h].items():
            if not abs(m[k]-previous)<=BASELINE_ABS_MAX_ERROR:
                raise SourceStop("V33_V32_ALL_84_ORIGINAL_GROUP_MSE_NUMERICAL_REPLAY_STOP_"+k+"_"+h)
        contr={}
        for k in CONTRAST_KEYS:
            arr=np.array([summaries_from_mse({
                panel:fold["original_equal_trial_within_shoal_MSE"][panel][h]
                for panel in PANELS
             })[k] for fold in folds],dtype=float)
            npos=int(np.sum(arr>0));nneg=int(np.sum(arr<0))
            equal=float(np.mean(arr))
            stat={
                "original_12_shoal_equal_mean_MSE_difference":equal,
                "relative_increment_over_GLOBAL_group_MSE":float(equal/m["GLOBAL"]),
                "positive_true_original_shoals":npos,
                "negative_true_original_shoals":nneg,
                "zero_true_original_shoals":int(np.sum(arr==0)),
                "per_original_shoal_signed_MSE_difference":[
                     {"original_shoal_ID":fold["original_heldout_shoal_ID"],
                      "original_signed_delta_MSE":float(val)}
                     for fold,val in zip(folds,arr)],
                "prespecified_direction_positive_majority_at_least_9_of_12":bool(npos>=9 and equal>0),
            }
            if k in CONTRAST_KEYS[:2]:
                stat["descriptive_5000_shoal_bootstrap_95pct_delta"]=bootstrap_group_differences(
                    arr,seed=20261124)
            contr[k]=stat
        primary={
          "near_additional_after_global_source_conditionally_positive":contr[
              "NEAR_ADDITIONAL_BEYOND_GLOBAL"]["prespecified_direction_positive_majority_at_least_9_of_12"],
          "true_current_near_position_assignment_beats_fixed_rot1":contr[
              "TRUE_NEAR_VERSUS_ROTATED_ONE"]["prespecified_direction_positive_majority_at_least_9_of_12"]
        }
        primary["both_near_and_assignment_tests_positive"]=all(primary.values())
        out[h]={
          "original_twelve_shoal_equal_MSE":m,
          "prespecified_group_fold_differences":contr,
          "primary_prediction_interpretation":primary,
          "original_v32_global_group_effect_numerically_replayed":True
        }
    return {
      "status":"V33_ORIGINAL_84_RECORDINGS_12_SHOALS_LOCAL_VERSUS_GLOBAL_HOLDOUT",
      "original_2021_study":"MacGregor & Ioannou, Gasterosteus aculeatus",
      "n_original_EIDC_trial_files":84,
      "n_original_biological_shoal_holdouts":12,
      "source_study_author_Trial_Group_map_provided":True,
      "source_original_version_frozen":"docs/V33_TOPOLOGICAL_NEAR_FAR_POSITION_ASSIGNMENT_FROZEN.md",
      "target_original_future_short_seconds":[0.,.2],
      "target_original_future_delayed_seconds":[.6,.8],
      "native_source_fps":25,"velocity_difference_window_seconds":.2,
      "original_panel_names":list(PANELS),
      "fixed_global_group_study_MSE_reference":EXPECTED_V32,
      "original_file_source_provenance":source_metadata,
      "original_true_shoal_holdout_records":folds,
      "source_original_group_result":out,
      "original_trajectory_and_future_Y_time_series_redistributed":False,
      "fish_origin_acoustics_or_causal_social_influence_identified":False,
      "scientific_claim_ceiling":"same-study 12 real shoals; observational local movement predictive contribution after common group velocity and fixed position; not social causality"
    }

def save(path,out):
    p=Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
