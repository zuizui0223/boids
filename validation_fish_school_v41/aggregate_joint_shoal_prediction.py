"""v41 ORIGINAL 84 EIDC fish / 12 genuine published 2021 biological shoals:
source-verified joint speed × prior-turn contextual predictive information.

Replay v40 marginal heldout result independently before admitting v41 joint
effects; train SAME four original v33 models on unstratified other 11 groups.
No real-fish motion Y/X coordinates or time-series rehosted.
"""
from __future__ import annotations
import argparse,json,re,tempfile
from pathlib import Path
import numpy as np

from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v32.stickleback_12_shoal import verify_crosswalk_bytes,verified_directory_index
from validation_fish_school_v32.moment_loo import (
    sum_moments,train_only_standardized_ridge,score_file_moment,bootstrap_group_differences)
from validation_fish_school_v40.source_speed_turn_strata import (
    MODELS,CATEGORIES as V40_CATEGORIES)
from validation_fish_school_v40.aggregate_speed_turn_original_shoals import (
    aggregate as v40_source_and_model_replay,
    restored_source_file,parse_moment,REFERENCE_V33,
    _delta as existing_v40_delta,
    SOURCE_FREEZE as V40_SCIENCE_FREEZE
)
from validation_fish_school_v41.joint_speed_turn_bins import (
    ALL_CATEGORIES,JOINT_CATEGORIES)
from validation_fish_school_v41.original_shoal_joint_shard import (
    SOURCE_FREEZE,GROUPMAP_BLOB)

HORIZONS=("short","delayed")
METRICS=("local_beyond_GLOBAL","true_neighbor_identity_vs_ROT1")
SHOALS=tuple(str(i) for i in range(1,13))
FIXED_2021_COUNTS={"native_rows":3147771,"original_eligible_group_times":570360,
                   "original_eligible_fish_time_rows":4562880,"dropped_group_times":57968}
EXPECTED_V40_MARGINAL={
"short":{
 "speed_low":(0.006705707648314677,0.006449467674797226),
 "speed_high":(0.010520597612197676,0.010157530970276385),
 "turn_low":(0.006029617751334138,0.005875953950650104),
 "turn_high":(0.010103966640570316,0.009713036931093893)},
"delayed":{
 "speed_low":(0.017018219368955926,0.016419983402630085),
 "speed_high":(0.01704823103853475,0.01657890804967874),
 "turn_low":(0.015406432501988846,0.015005227131186016),
 "turn_high":(0.018166361167215258,0.01753024332737711)}
}
CONDITIONAL_COMPARISONS={
 "TURN_EFFECT_WITHIN_LOW_SPEED":("SLOW_THIGH","SLOW_TLOW"),
 "TURN_EFFECT_WITHIN_HIGH_SPEED":("SHIGH_THIGH","SHIGH_TLOW"),
 "SPEED_EFFECT_WITHIN_LOW_TURN":("SHIGH_TLOW","SLOW_TLOW"),
 "SPEED_EFFECT_WITHIN_HIGH_TURN":("SHIGH_THIGH","SLOW_THIGH")
}
ORDERED_ENDPTS=tuple(CONDITIONAL_COMPARISONS)+("SPEEDxTURN_DIFF_IN_DIFF",)

def bounded_original_shards(source_dir):
    files=sorted(source_dir.glob("group_*.json"))
    if len(files)!=12:
        raise SourceStop("V41_NOT_TWELVE_ORIGINAL_AUTHOR_SHOAL_SHARDS")
    author=verify_crosswalk_bytes()
    published_index=verified_directory_index()
    if len(author)!=84 or set(author)!=set(published_index):
        raise SourceStop("V41_ORIGINAL_84_GROUP_OR_PUBLISHED_INDEX_MISMATCH")
    all_data={}
    groups={}
    old_wrappers={}
    audit=[]
    for f in files:
        record=json.loads(f.read_text(encoding="utf8"))
        group=record.get("original_group_ID")
        if (record.get("status")!="V41_ORIGINAL_SOURCE_NINE_STRATA_SUMMARY_MOMENTS_AUTHENTICATED" or
            group not in SHOALS or group in groups or
            record.get("frozen_original_trial_to_shoal_mapping_git_blob")!=GROUPMAP_BLOB or
            record.get("frozen_after_v40_marginals_but_before_joint_outcomes")!=SOURCE_FREEZE or
            record.get("source_original_models")!=list(MODELS) or
            record.get("source_nine_joint_and_marginal_stratum_names")!=list(ALL_CATEGORIES) or
            record.get("no_individual_animal_XY_Y_or_source_fish_frame_times_redistributed") is not True or
            record.get("no_predictive_effect_measured_inside_source_shard") is not True):
            raise SourceStop("V41_ORIGINAL_SHARD_SCIENCE_OR_SOURCE_STATUS_CHANGED")
        group_members={n for n in author if author[n]==group}
        src=record.get("original_source_files",{})
        if set(src)!=group_members or len(src)!=record.get("n_original_shoal_recording_files"):
            raise SourceStop("V41_ORIGINAL_AUTHOR_GROUP_HAS_MISSING_OR_EXTRA_FILES")
        groups[group]=record
        v40_facts={}
        for name,item in src.items():
            if name in all_data or item.get("original_author_source_file_ID")!=name or item.get("original_author_biological_group_ID")!=group:
                raise SourceStop("V41_SOURCE_ORIGINAL_DUPLICATE_OR_WRONG_GROUP")
            size=item.get("original_official_EIDC_source_file_size")
            sha=item.get("original_recomputed_source_SHA256")
            if size!=published_index[name] or not isinstance(sha,str) or not re.fullmatch(r"[a-f0-9]{64}",sha):
                raise SourceStop("V41_ORIGINAL_AUTHOR_SOURCE_SIZE_HASH_NOT_AUTHENTIC")
            if item.get("original_3_previous_independent_source_hashes_pinned") is not (name in ("01.txt","02.txt","105.txt")):
                raise SourceStop("V41_ORIGINAL_AUTHENTICATED_3_SOURCE_HASH_PIN_FLAG_INVALID")
            raw=item.get("source_9_strata_original_Ridge_sufficient_statistics_ONLY",{})
            if set(raw)!=set(ALL_CATEGORIES):
                raise SourceStop("V41_ORIGINAL_NINE_STRATA_CHANGED")
            firstfive={k:raw[k] for k in V40_CATEGORIES}
            fixture={
               "stratum_source_moment_sufficient_statistics_only":firstfive
            }
            old=restored_source_file(fixture)
            four={cat:{model:parse_moment(raw[cat][model],model)
                          for model in MODELS}
                  for cat in JOINT_CATEGORIES}
            for cat in JOINT_CATEGORIES:
                if set(raw[cat])!=set(MODELS) or len({m["n"] for m in four[cat].values()})!=1:
                    raise SourceStop("V41_SOURCE_MOMENT_MODEL_OR_SAME_Y_COUNT_CHANGED")
                reference=four[cat]["G_geometry"]
                for model in MODELS[1:]:
                    z=four[cat][model]
                    if not np.allclose(z["sy"],reference["sy"],rtol=1e-12,atol=1e-3) or not np.allclose(z["syy"],reference["syy"],rtol=1e-12,atol=.1):
                        raise SourceStop("V41_SOURCE_FISH_Y_FUTURE_NOT_MATCHED_IN_JOINT_CATEGORY")
            for turn,parts in [("turn_low",("SLOW_TLOW","SHIGH_TLOW")),
                              ("turn_high",("SLOW_THIGH","SHIGH_THIGH"))]:
                for model in MODELS:
                    merged=sum_moments([four[p][model] for p in parts])
                    target=old[turn][model]
                    if merged["n"]!=target["n"]:
                        raise SourceStop("V41_OWN_TURN_SOURCE_JOINT_LOW_HIGH_COUNTS_CHANGED")
                    for k in ("sx","sxx","sxy","sy","syy"):
                        if not np.allclose(merged[k],target[k],rtol=1e-9,atol=1e-3):
                            raise SourceStop("V41_OWN_TURN_SOURCE_JOINT_MOMENTS_DIFFER_"+k)
            original_count=item.get("source_eligible_original_fish_rows")
            turn_undefined=item.get("n_original_heading_undefined_rows")
            if (original_count!=old["ALL"]["G_geometry"]["n"] or
                original_count!=8*item.get("source_eligible_group_times") or
                original_count-turn_undefined!=sum(four[k]["G_geometry"]["n"] for k in JOINT_CATEGORIES)):
                raise SourceStop("V41_ORIGINAL_SOURCE_TOTAL_JOINT_AND_200MS_COHORT_DRIFT")
            reported=item.get("original_4_joint_categories_sample_counts",{})
            if any(reported.get(k)!=four[k]["G_geometry"]["n"] for k in JOINT_CATEGORIES):
                raise SourceStop("V41_SOURCE_ORIGINAL_SAFETY_COUNTS_NOT_MATCHED")
            original_marg=item.get("original_previous_v40_marginal_category_sample_counts",{})
            if any(original_marg.get(k)!=old[k]["G_geometry"]["n"] for k in V40_CATEGORIES):
                raise SourceStop("V41_ORIGINAL_V40_MARGINAL_SOURCE_FISH_COUNTS_DRIFT")
            all_data[name]={"marginals":old,"joint":four}
            audit.append({
               "original_author_file_ID":name,
               "original_author_true_shoal_group_ID":group,
               "original_author_source_file_size":size,
               "original_fish_source_sha256":sha,
               "n_original_fish_frame_records":original_count,
               "original_undefined_200ms_turn_frames":turn_undefined,
               "n_joint_groups":{k:reported[k] for k in JOINT_CATEGORIES},
               "original_source_XY_Y_not_redistributed":True})
            v40_facts[name]={
              "original_2021_author_file":name,
              "original_2021_author_biological_shoal_ID":group,
              "original_EIDC_bytes_official":size,
              "original_EIDC_SHA256_newly_recomputed":sha,
              "original_3_prior_source_SHA256_pins_pass":item["original_3_previous_independent_source_hashes_pinned"],
              "original_source_native_time_rows":item["source_native_frame_count"],
              "original_eligible_group_times":item["source_eligible_group_times"],
              "original_group_time_rows_dropped_for_source_NA_or_clock":item["source_200ms_NA_and_clock_excluded_group_times"],
              "original_source_focal_fish_frame_rows":original_count,
              "n_source_turn_undefined_heading_rows":turn_undefined,
              "source_current_speed_and_turn_metadata_not_target_values":{
                "n_original_turn_well_defined_rows":original_count-turn_undefined
              },
              "stratum_source_moment_sufficient_statistics_only":firstfive
            }
        old_wrappers[group]={
          "status":"V40_ALL_ORIGINAL_AUTHOR_GROUP_FILES_AUTHENTICATED_STRATA_MOMENT_ONLY",
          "original_2021_true_group":group,
          "original_experimental_group_map_git_blob":GROUPMAP_BLOB,
          "source_original_science_freeze":V40_SCIENCE_FREEZE,
          "original_fish_Y_XY_or_kinematic_timeseries_redistributed":False,
          "new_original_near_neighbor_group_effect_not_yet_scored":True,
          "fixed_source_model_names":list(MODELS),
          "fixed_test_strata_names":list(V40_CATEGORIES),
          "n_original_file_records":len(v40_facts),
          "source_original_file_records":v40_facts
        }
    if set(groups)!=set(SHOALS) or set(all_data)!=set(author) or len(all_data)!=84:
        raise SourceStop("V41_12_ORIGINAL_GROUPS_84_SOURCE_NOT_COMPLETE")
    totals={
       "native_rows":sum(it["source_native_frame_count"] for g in groups.values()
                        for it in g["original_source_files"].values()),
       "original_eligible_group_times":sum(it["source_eligible_group_times"] for g in groups.values()
                        for it in g["original_source_files"].values()),
       "original_eligible_fish_time_rows":sum(it["source_eligible_original_fish_rows"] for g in groups.values()
                        for it in g["original_source_files"].values()),
       "dropped_group_times":sum(it["source_200ms_NA_and_clock_excluded_group_times"] for g in groups.values()
                        for it in g["original_source_files"].values())
    }
    if totals!=FIXED_2021_COUNTS:
        raise SourceStop("V41_2021_SOURCE_V33_V40_84_TRACK_COHORT_DRIFT")
    with tempfile.TemporaryDirectory(prefix="v41_previous_source_v40_") as td:
        for group,body in old_wrappers.items():
            Path(td,f"group_{group}.json").write_text(json.dumps(body,sort_keys=True),
                                                      encoding="utf8")
        previous=v40_source_and_model_replay(Path(td))
    if previous.get("status")!="V40_ORIGINAL_AUTHOR_12_SHOAL_FROZEN_V33_STRATIFIED_TEST_ONLY":
        raise SourceStop("V41_UNCHANGED_V40_V33_REFERENCE_MODEL_NOT_REPLAYED")
    for h in HORIZONS:
        old=previous["source_original_12_shoal_MODERATION_results"][h]
        for model in MODELS:
            if abs(old["original_12_shoal_equal_MSE_all_source"][model]-REFERENCE_V33[h][model])>.05:
                raise SourceStop("V41_PREVIOUS_ORIGINAL_FULL_V33_MSE_REPLAY_STOP")
        for cat in V40_CATEGORIES[1:]:
            for i,metric in enumerate(METRICS):
                actual=old["category_specific_original_12_shoal_incremental_predictive_gains"][cat][metric]["original_12_group_equal_mean_relative_MSE_gain"]
                if abs(actual-EXPECTED_V40_MARGINAL[h][cat][i])>1e-5:
                    raise SourceStop("V41_SOURCE_ORIGINAL_V40_PREKNOWN_MARGINAL_BENCHMARK_STOP_"+h+cat+metric)
    source_receipt={
      "source_published_EIDC_DOI":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
      "original_84_files_n":84,"original_independent_shoals_n":12,
      "n_original_source_4_joint_category_rows":{c:int(sum(
           z["joint"][c]["G_geometry"]["n"] for z in all_data.values()))
                   for c in JOINT_CATEGORIES},
      "n_original_source_turn_undefined_rows":int(sum(x["original_undefined_200ms_turn_frames"] for x in audit)),
      "frozen_source_2021_cohort_totals":totals,
      "v40_all_original_12_shoal_G_GLOBAL_NEAR_ROT_REPLAY_PASS":True,
      "v40_four_speed_turn_marginals_both_horizons_replayed":True,
      "original_all_84_source_SHA256_size_and_joint_frame_counts":sorted(
        audit,key=lambda q:int(q["original_author_file_ID"][:-4])),
      "original_individual_fish_XY_Y_and_timeseries_NOT_exported":True
    }
    return score_joint(all_data,author,source_receipt)


def score_joint(all_data,author,source):
    folds=[]
    for held in SHOALS:
        train=sorted((f for f in author if author[f]!=held),key=lambda x:int(x[:-4]))
        test=sorted((f for f in author if author[f]==held),key=lambda x:int(x[:-4]))
        if held in {author[f] for f in train} or len({author[f] for f in train})!=11:
            raise SourceStop("V41_ORIGINAL_SOURCE_SAME_BIOLOGICAL_SHOAL_LEAKAGE")
        fold={
          "original_biological_shoal_test_ID":held,
          "n_source_original_test_recordings":len(test),
          "original_source_test_file_names":test,
          "n_original_training_shoals":11,
          "original_train_test_true_shoal_overlap":False,
          "joint_category_file_equal_group_MSE":{c:{} for c in JOINT_CATEGORIES}
        }
        for model in MODELS:
            training=sum_moments([all_data[n]["marginals"]["ALL"][model] for n in train])
            coef,bias=train_only_standardized_ridge(training)
            for cat in JOINT_CATEGORIES:
                testscore=[score_file_moment(all_data[n]["joint"][cat][model],coef,bias)
                           for n in test]
                fold["joint_category_file_equal_group_MSE"][cat][model]={
                  horizon:float(np.mean([z[horizon] for z in testscore]))
                  for horizon in HORIZONS
                }
        folds.append(fold)
    return summarize_joint(folds,source)


def summarize_joint(folds,source):
    if len(folds)!=12 or [x["original_biological_shoal_test_ID"] for x in folds]!=list(SHOALS):
        raise SourceStop("V41_ORIGINAL_TWELVE_HOLDOUT_SHOAL_COUNT_NOT_MATCHED")
    resp={}
    for hi,h in enumerate(HORIZONS):
        cellpoints={cat:{} for cat in JOINT_CATEGORIES}
        for cat in JOINT_CATEGORIES:
            for metric in METRICS:
                arr=[]
                for f in folds:
                    score={model:f["joint_category_file_equal_group_MSE"][cat][model][h]
                           for model in MODELS}
                    arr.append(existing_v40_delta(score,metric))
                v=np.asarray(arr,dtype=float)
                cellpoints[cat][metric]={
                    "equal_12_original_shoal_MSE_relative_improvement":float(np.mean(v)),
                    "positive_original_shoals":int(np.sum(v>0)),
                    "negative_original_shoals":int(np.sum(v<0)),
                    "original_12_shoal_IDs_and_local_improvements":[
                       {"group":f["original_biological_shoal_test_ID"],
                        "value":float(d)} for f,d in zip(folds,v)]
                }
        effects={}
        for ei,name in enumerate(ORDERED_ENDPTS):
            effects[name]={}
            for mi,metric in enumerate(METRICS):
                cells={cat:np.asarray([z["value"] for z in cellpoints[cat][metric]["original_12_shoal_IDs_and_local_improvements"]]) for cat in JOINT_CATEGORIES}
                if name=="SPEEDxTURN_DIFF_IN_DIFF":
                    diff=(cells["SHIGH_THIGH"]-cells["SHIGH_TLOW"])-(cells["SLOW_THIGH"]-cells["SLOW_TLOW"])
                else:
                    high,low=CONDITIONAL_COMPARISONS[name]
                    diff=cells[high]-cells[low]
                if diff.shape!=(12,) or not np.isfinite(diff).all():
                    raise SourceStop("V41_ORIGINAL_JOINT_MODERATION_SHAPE_OR_FINITE_STOP")
                mu=float(np.mean(diff))
                boot=bootstrap_group_differences(diff,seed=20261124+50*hi+10*ei+mi)
                effects[name][metric]={
                  "source_effect_type":"Descriptive within-study 12 biological shoal heldout paired MSE-prediction differences",
                  "equal_original_12_shoal_mean_relative_GAIN_difference":mu,
                  "positive_original_shoals":int(np.sum(diff>0)),
                  "negative_original_shoals":int(np.sum(diff<0)),
                  "descriptive_5000_original_group_bootstrap_95pct":boot,
                  "small_mean_below_frozen_0_001_ratio_threshold":bool(abs(mu)<.001),
                  "original_12_shoal_ID_signed_differences":[
                     {"group_ID":f["original_biological_shoal_test_ID"],"difference":float(v)}
                      for f,v in zip(folds,diff)]
                }
        resp[h]={
          "four_original_joint_test_strata":cellpoints,
          "speed_and_turn_conditional_outcomes":effects,
          "same_unstratified_11_shoal_training_for_every_joint_test_category":True,
          "no_original_fish_response_Y_or_future_in_stratum_assignment":True
        }
    return {
      "status":"V41_ORIGINAL_84_TRACKS_12_SHOAL_POSTV40_JOINT_SPEED_TURN_EXPLORATORY_RESULT",
      "scientific_pre_original_joint_source_outcome_freeze":SOURCE_FREEZE,
      "original_84_true_group_source_provenance":source,
      "true_original_biological_shoal_test_fold_count":12,
      "original_EIDC_tracking_files":84,
      "joint_speed_and_turn_test_stratum_names":list(JOINT_CATEGORIES),
      "current_own_speed_and_previous_200ms_turn_only_exposure":True,
      "not_a_randomized_2026_VR_treatment_or_causal_fish_following":True,
      "not_independent_from_v40_original_source":True,
      "no_original_animal_XY_or_future_target_rows_or_calls_redistributed":True,
      "source_12_true_shoal_joint_prediction_model_MSE":folds,
      "original_joint_speed_and_turn_predictions_by_future_horizon":resp
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--shards",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    try:answer=bounded_original_shards(args.shards)
    except (SourceStop,OSError,ValueError,KeyError,IndexError,TypeError) as ex:
        answer={
          "status":"V41_ORIGINAL_SOURCE_OR_JOINT_GROUP_HOLDOUT_STOP",
          "reason":str(ex),
          "original_COHORT_C1_C2_test_estimate":None,
          "raw_original_fish_XY_Y_redistributed":False
        }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(answer,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({
       "status":answer["status"],
       "reason":answer.get("reason"),
       "n_original_2021_source_files":answer.get("original_EIDC_tracking_files"),
       "n_original_2021_shoals":answer.get("true_original_biological_shoal_test_fold_count"),
       "joint_horizon_results":answer.get("original_joint_speed_and_turn_predictions_by_future_horizon")
    },sort_keys=True),flush=True)
    if answer["status"]!="V41_ORIGINAL_84_TRACKS_12_SHOAL_POSTV40_JOINT_SPEED_TURN_EXPLORATORY_RESULT":
        raise SystemExit(1)

if __name__=="__main__":main()
