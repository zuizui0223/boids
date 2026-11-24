"""v40 source-verified TRUE 12 biological shoal holdout: high/low own speed
and 200ms heading turning, original v33 six-parameter science model unchanged.

Training each fold on unstratified ALL fish tracks of the 11 OTHER shoals;
test-only original covariate strata to measure moderation, no future Y leakage.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
import numpy as np

from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v32.stickleback_12_shoal import (
    verify_crosswalk_bytes,verified_directory_index
)
from validation_fish_school_v32.moment_loo import (
    sum_moments,train_only_standardized_ridge,score_file_moment,bootstrap_group_differences
)
from validation_fish_school_v40.source_speed_turn_strata import MODELS,CATEGORIES
from validation_fish_school_v40.author_group_speed_turn_shard import (
    MOM_KEYS,SOURCE_FREEZE,FROZEN_GROUPMAP_BLOB
)

TAXON="Gasterosteus aculeatus"
SOURCE_COHORT_TOTALS={
  "native_rows":3147771,
  "original_eligible_group_times":570360,
  "original_eligible_fish_time_rows":4562880,
  "dropped_group_times":57968
}
REFERENCE_V33={
 "short":{"G_geometry":3407.0695372716254,"GLOBAL":3344.918757773203,
          "NEAR_TRUE":3315.6082454194698,"NEAR_ROT1":3343.9461236381485},
 "delayed":{"G_geometry":8925.030228272999,"GLOBAL":8479.996942316227,
          "NEAR_TRUE":8339.86764815248,"NEAR_ROT1":8475.629628302566}
}
FUTURE_HORIZONS=("short","delayed")
SHOALS=tuple(str(i) for i in range(1,13))
DELTA_NAMES=("local_beyond_GLOBAL","true_neighbor_identity_vs_ROT1")
EXPECTED_NON_CAUSAL_SOURCE_STATUS="V40_ORIGINAL_AUTHOR_12_SHOAL_FROZEN_V33_STRATIFIED_TEST_ONLY"


def parse_moment(obj,model):
    expected={"G_geometry":14,"GLOBAL":16,"NEAR_TRUE":18,"NEAR_ROT1":18}[model]
    if not isinstance(obj,dict) or set(obj)!=set(MOM_KEYS):
        raise SourceStop("V40_ORIGINAL_FILE_MOMENT_STRUCTURE_CHANGED")
    n=obj["n"]
    if type(n)!=int or n<1000:
        raise SourceStop("V40_ORIGINAL_SOURCE_STRATUM_NEEDS_AT_LEAST_1000_FISH_FRAME_ROWS")
    dims={"sx":(expected,),"sxx":(expected,expected),
          "sxy":(expected,4),"sy":(4,),"syy":(4,)}
    out={"n":n}
    for k,shape in dims.items():
        v=np.asarray(obj[k],dtype=float)
        if v.shape!=shape or not np.all(np.isfinite(v)):
            raise SourceStop("V40_SOURCE_MOMENT_NONFINITE_OR_SHAPE_"+k)
        out[k]=v
    if not np.allclose(out["sxx"],out["sxx"].T,rtol=1e-9,atol=1e-3):
        raise SourceStop("V40_ORIGINAL_SOURCE_COVARIATE_SECOND_MOMENT_NOT_SYMMETRIC")
    return out


def restored_source_file(row):
    raw=row["stratum_source_moment_sufficient_statistics_only"]
    if not isinstance(raw,dict) or tuple(raw)!=CATEGORIES:
        raise SourceStop("V40_ORIGINAL_SOURCE_CATEGORY_SET_CHANGED")
    out={}
    for category in CATEGORIES:
        if not isinstance(raw[category],dict) or tuple(raw[category])!=MODELS:
            raise SourceStop("V40_SOURCE_SCIENTIFIC_MODEL_KEYS_CHANGED")
        out[category]={model:parse_moment(raw[category][model],model) for model in MODELS}
        n={v["n"] for v in out[category].values()}
        if len(n)!=1:raise SourceStop("V40_SOURCE_ORIGINAL_SAME_Y_PANEL_SAMPLE_COUNT_MISMATCH")
        ref=out[category]["G_geometry"]
        for model in MODELS[1:]:
            v=out[category][model]
            if (not np.allclose(v["sy"],ref["sy"],rtol=1e-12,atol=1e-3) or
                not np.allclose(v["syy"],ref["syy"],rtol=1e-12,atol=.1)):
                raise SourceStop("V40_DIFFERENT_FUTURE_Y_WITHIN_SOURCE_DIAGNOSTIC")
    for model in MODELS:
        full=out["ALL"][model]
        lo=out["speed_low"][model];hi=out["speed_high"][model]
        if full["n"]!=lo["n"]+hi["n"]:
            raise SourceStop("V40_SPEED_COHORT_PARTITION_CHANGED_FROM_ORIGINAL")
        for key in ("sx","sxx","sxy","sy","syy"):
            if not np.allclose(full[key],lo[key]+hi[key],rtol=1e-9,atol=1e-3):
                raise SourceStop("V40_SOURCE_FULL_VS_SPEED_LOW_PLUS_HIGH_MOMENT_STOP")
    return out


def aggregate(shards):
    groupmap=verify_crosswalk_bytes()
    index=verified_directory_index()
    if len(groupmap)!=84 or len(index)!=84 or set(index)!=set(groupmap):
        raise SourceStop("V40_ORIGINAL_AUTHOR_84_SOURCE_FILES_NOT_VERIFIED")
    files=list(shards.glob("group_*.json"))
    if len(files)!=12:
        raise SourceStop("V40_NOT_TWELVE_ORIGINAL_SOURCE_GROUP_SUMMARY_SHARDS")
    all_data={}
    all_facts={}
    encountered=set()
    n_undefined=0
    for p in files:
        z=json.loads(p.read_text(encoding="utf8"))
        g=z.get("original_2021_true_group")
        if (z.get("status")!="V40_ALL_ORIGINAL_AUTHOR_GROUP_FILES_AUTHENTICATED_STRATA_MOMENT_ONLY" or
            g not in SHOALS or g in encountered or
            z.get("original_experimental_group_map_git_blob")!=FROZEN_GROUPMAP_BLOB or
            z.get("source_original_science_freeze")!=SOURCE_FREEZE or
            z.get("original_fish_Y_XY_or_kinematic_timeseries_redistributed") is not False or
            z.get("new_original_near_neighbor_group_effect_not_yet_scored") is not True or
            z.get("fixed_source_model_names")!=list(MODELS) or
            z.get("fixed_test_strata_names")!=list(CATEGORIES)):
            raise SourceStop("V40_SOURCE_SHARD_NOT_ORIGINAL_FROZEN_COMPLETE")
        encountered.add(g)
        orig=z.get("source_original_file_records",{})
        members={name for name in groupmap if groupmap[name]==g}
        if not isinstance(orig,dict) or set(orig)!=members or len(orig)!=z.get("n_original_file_records"):
            raise SourceStop("V40_SHOAL_SHARD_HAS_MISSING_OR_DUPLICATE_SOURCE_FILES")
        for name,record in orig.items():
            if name in all_data or record.get("original_2021_author_file")!=name or record.get("original_2021_author_biological_shoal_ID")!=g or record.get("original_EIDC_bytes_official")!=index[name]:
                raise SourceStop("V40_ORIGINAL_AUTHOR_FILE_OR_SHOAL_IDENTITY_NOT_MATCHED")
            sha=record.get("original_EIDC_SHA256_newly_recomputed")
            if not isinstance(sha,str) or not re.fullmatch("[a-f0-9]{64}",sha):
                raise SourceStop("V40_ORIGINAL_SOURCE_FILE_SHA256_NOT_PRESENT")
            if name in PINS and (sha!=PINS[name][0] or index[name]!=PINS[name][1]):
                raise SourceStop("V40_ORIGINAL_THREE_FROZEN_PINNED_SOURCE_SHA256_DRIFT_"+name)
            if record.get("original_3_prior_source_SHA256_pins_pass") is not (name in PINS):
                raise SourceStop("V40_SOURCE_SHA256_PIN_REPORT_INCONSISTENT")
            stats=restored_source_file(record)
            if record.get("original_source_focal_fish_frame_rows")!=stats["ALL"]["G_geometry"]["n"]:
                raise SourceStop("V40_ORIGINAL_FOCAL_EIGHT_FISH_FRAME_COUNT_CHANGED")
            if record.get("original_source_focal_fish_frame_rows")!=8*record["original_eligible_group_times"]:
                raise SourceStop("V40_ORIGINAL_8_FISH_SOURCE_FPS_OR_COHORT_DRIFT")
            meta=record.get("source_current_speed_and_turn_metadata_not_target_values",{})
            nturn=meta.get("n_original_turn_well_defined_rows")
            if (type(nturn)!=int or nturn+record.get("n_source_turn_undefined_heading_rows",-1)!=
                    record["original_source_focal_fish_frame_rows"]):
                raise SourceStop("V40_ZERO_SPEED_TURN_HEADING_UNDEFINED_MASK_INCONSISTENT")
            if stats["turn_low"]["G_geometry"]["n"]+stats["turn_high"]["G_geometry"]["n"]!=nturn:
                raise SourceStop("V40_TURN_HALF_PARTITIONS_MISMATCH_VALID_HEADING_COUNT")
            n_undefined+=record["n_source_turn_undefined_heading_rows"]
            all_data[name]=stats
            all_facts[name]={k:record[k] for k in (
                "original_2021_author_file","original_2021_author_biological_shoal_ID",
                "original_EIDC_bytes_official","original_EIDC_SHA256_newly_recomputed",
                "original_source_native_time_rows","original_eligible_group_times",
                "original_group_time_rows_dropped_for_source_NA_or_clock",
                "original_source_focal_fish_frame_rows","n_source_turn_undefined_heading_rows")}
    if encountered!=set(SHOALS) or set(all_data)!=set(groupmap):
        raise SourceStop("V40_SOURCE_REQUIRED_ORIGINAL_12_SHOALS_84_FILES_INCOMPLETE")
    totals={
      "native_rows":sum(x["original_source_native_time_rows"] for x in all_facts.values()),
      "original_eligible_group_times":sum(x["original_eligible_group_times"] for x in all_facts.values()),
      "original_eligible_fish_time_rows":sum(x["original_source_focal_fish_frame_rows"] for x in all_facts.values()),
      "dropped_group_times":sum(x["original_group_time_rows_dropped_for_source_NA_or_clock"] for x in all_facts.values())
    }
    if totals!=SOURCE_COHORT_TOTALS:
        raise SourceStop("V40_ORIGINAL_84_V33_COMMON_COHORT_TOTALS_CHANGED")
    source_facts={
      "original_source_EIDC_doi":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
      "original_author_Trial_Group_SHA1_blob":FROZEN_GROUPMAP_BLOB,
      "source_original_84_video_12_group_map_verified":True,
      "source_84_file_original_2021_sha256_size_eligible_counts":[
           all_facts[name] for name in sorted(all_facts,key=lambda n:int(n[:-4]))],
      "original_source_total_and_200ms_cohorts":totals,
      "n_focal_fish_frames_own_heading_undefined_in_turn_analysis":n_undefined,
      "pct_undefined_own_previous_current_heading":100*n_undefined/totals["original_eligible_fish_time_rows"],
      "original_animal_XY_future_Y_or_time_series_uploaded":False,
      "original_source_file_trial_IDs_never_confused_with_84_independent_shoals":True
    }
    return heldout(all_data,groupmap,source_facts)


def heldout(all_data,original_map,source_facts):
    foldrows=[]
    for g in SHOALS:
        trainfiles=sorted((n for n in original_map if original_map[n]!=g),key=lambda s:int(s[:-4]))
        heldfiles=sorted((n for n in original_map if original_map[n]==g),key=lambda s:int(s[:-4]))
        if len({original_map[n] for n in trainfiles})!=11 or g in {original_map[n] for n in trainfiles}:
            raise SourceStop("V40_ORIGINAL_11_TRAIN_SHOAL_FOLD_LEAKAGE")
        folds={"original_test_group_ID":g,
               "n_original_group_trial_files":len(heldfiles),
               "original_group_file_names":heldfiles,
               "source_frozen_models_train_on_ALL_SPEEDS_OTHER_11_GROUPS":True,
               "train_test_same_original_biological_group_overlap":False,
               "source_category_MSE":{}}
        for cat in CATEGORIES:
            folds["source_category_MSE"][cat]={}
        for model in MODELS:
            trainmom=sum_moments([all_data[name]["ALL"][model] for name in trainfiles])
            coef,bias=train_only_standardized_ridge(trainmom)
            for cat in CATEGORIES:
                scores=[score_file_moment(all_data[name][cat][model],coef,bias) for name in heldfiles]
                folds["source_category_MSE"][cat][model]={
                   h:float(np.mean([z[h] for z in scores])) for h in FUTURE_HORIZONS
                }
        foldrows.append(folds)
    return summarize(foldrows,source_facts)


def _delta(m,kind):
    if m["GLOBAL"]<=0:raise SourceStop("V40_ZERO_OR_NEGATIVE_GROUP_GLOBAL_REFERENCE_MSE")
    if kind=="local_beyond_GLOBAL":
        return (m["GLOBAL"]-m["NEAR_TRUE"])/m["GLOBAL"]
    if kind=="true_neighbor_identity_vs_ROT1":
        return (m["NEAR_ROT1"]-m["NEAR_TRUE"])/m["GLOBAL"]
    raise SourceStop("V40_UNREGISTERED_SPEED_TURNING_MODERATION_CONTRAST")


def summarize(foldrows,source_facts):
    if len(foldrows)!=12 or [z["original_test_group_ID"] for z in foldrows]!=list(SHOALS):
        raise SourceStop("V40_NOT_EXACT_12_REAL_SOURCE_SHOAL_HOLDOUTS")
    observed={}
    for horizon_index,h in enumerate(FUTURE_HORIZONS):
        full={model:float(np.mean([f["source_category_MSE"]["ALL"][model][h]
                for f in foldrows])) for model in MODELS}
        for model in MODELS:
            if abs(full[model]-REFERENCE_V33[h][model])>.05:
                raise SourceStop("V40_ORIGINAL_V33B_ALL_SOURCE_GLOBAL_NEAR_ROTATE_MSE_REPLAY_STOP_"+model+"_"+h)
        categories={}
        for cat in CATEGORIES[1:]:
            vals={}
            for kind in DELTA_NAMES:
                per=[]
                for f in foldrows:
                    m={model:f["source_category_MSE"][cat][model][h] for model in MODELS}
                    per.append({"group":f["original_test_group_ID"],
                                "relative_source_heldout_MSE_gain":_delta(m,kind)})
                numbers=np.array([x["relative_source_heldout_MSE_gain"] for x in per],float)
                vals[kind]={
                  "original_12_group_equal_mean_relative_MSE_gain":float(np.mean(numbers)),
                  "positive_original_groups":int(np.sum(numbers>0)),
                  "negative_original_groups":int(np.sum(numbers<0)),
                  "original_group_values":per
                }
            categories[cat]=vals
        paired={}
        for i,(axis,high,low) in enumerate((("speed","speed_high","speed_low"),
                                           ("turn","turn_high","turn_low"))):
            paired[axis]={}
            for k,kind in enumerate(DELTA_NAMES):
                highs=[z["relative_source_heldout_MSE_gain"]
                       for z in categories[high][kind]["original_group_values"]]
                lows=[z["relative_source_heldout_MSE_gain"]
                      for z in categories[low][kind]["original_group_values"]]
                d=np.asarray(highs,dtype=float)-np.asarray(lows,dtype=float)
                paired[axis][kind]={
                   "contrast":"HIGH minus LOW within independently heldout 2021 experimental shoal",
                   "equal_12_original_shoal_mean_modulation_relative_GLOBAL_MSE":float(np.mean(d)),
                   "positive_original_groups":int(np.sum(d>0)),
                   "negative_original_groups":int(np.sum(d<0)),
                   "small_abs_below_frozen_0_001_threshold":bool(abs(float(np.mean(d)))<.001),
                   "descriptive_5000_bootstrap_95pct_whole_original_shoal":bootstrap_group_differences(
                         d,seed=20261124+10*horizon_index+2*i+k),
                   "per_group_H_minus_L":[
                          {"original_shoal_ID":fold["original_test_group_ID"],
                           "difference_relative_MSE_gain":float(z)}
                          for fold,z in zip(foldrows,d)]
                }
        observed[h]={
           "source_original_v33b_ALL_sample_baseline_MSE_exact_replayed":True,
           "original_12_shoal_equal_MSE_all_source":full,
           "category_specific_original_12_shoal_incremental_predictive_gains":categories,
           "source_original_pairwise_SPEED_AND_TURN_MODERATIONS":paired,
           "source_unit":"ratio of model MSE, within study only",
           "causal_speed_or_turning_inference":False
        }
    return {
      "status":EXPECTED_NON_CAUSAL_SOURCE_STATUS,
      "original_study":"MacGregor & Ioannou 2021 Gasterosteus aculeatus original 84 TXT recordings / 12 genuine experimental shoals",
      "original_EIDC_2021_source_file_count":84,
      "original_independent_biological_shoal_ID_count":12,
      "original_future_horizons_s":{"short":[0,.2],"delayed":[.6,.8]},
      "original_own_speed_turning_categorization":"each source file stable median rank of focal G14 speed or defined absolute 0.2s heading change; no future Y used",
      "scientific_pre_outcome_freeze":SOURCE_FREEZE,
      "original_file_source_provenance":source_facts,
      "original_12_biological_shoal_heldout_MSE_by_source_covariate_categories":foldrows,
      "source_original_12_shoal_MODERATION_results":observed,
      "training_full_ALL_source_other_11_shoals_unchanged_for_all_categories":True,
      "no_fish_source_XY_future_target_timeseries_republished":True,
      "no_real_fish_perturbation_or_acoustic_source_identified":True,
      "scientific_limit":"descriptive speed and turning moderation of heldout forecast within one original source; both are observed and correlated, not randomized fish treatments, and no causal Boids force identified"
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--shards",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    try:res=aggregate(args.shards)
    except (SourceStop,KeyError,IndexError,ValueError,TypeError,OSError) as e:
        res={"status":"V40_ORIGINAL_SOURCE_OR_MODEL_REPLAY_STOP",
             "reason":str(e),
             "source_original_speed_turning_effect":None,
             "original_fish_trajectory_time_series_republished":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({
      "status":res["status"],"reason":res.get("reason"),
      "n_original_source_trials":res.get("original_EIDC_2021_source_file_count"),
      "n_original_12_shoals":res.get("original_independent_biological_shoal_ID_count"),
      "source_results":res.get("source_original_12_shoal_MODERATION_results"),
      "source_unusable_own_heading_count":res.get("original_file_source_provenance",{}).get(
           "n_focal_fish_frames_own_heading_undefined_in_turn_analysis")
    },sort_keys=True),flush=True)
    if res["status"]!=EXPECTED_NON_CAUSAL_SOURCE_STATUS:
        raise SystemExit(1)

if __name__=="__main__":main()
