"""v41 original EIDC 2021 source files: one exact author shoal per GH job.

Same original source authenticators and v33 original panels/v40 marginal
categorization. Serialize only 9-category per-file aggregate Ridge moments;
never output fish XY, time series or target future velocity row.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v26.recording_age_forecast import read_source
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v32.stickleback_12_shoal import (
    verify_crosswalk_bytes,verified_directory_index,source_fetch_file)
from validation_fish_school_v33.neighbor_panels import original_panels
from validation_fish_school_v33.stickleback_neighbor_source import FROZEN_EXAMPLE_GROUP_COUNTS
from validation_fish_school_v40.source_speed_turn_strata import MODELS
from validation_fish_school_v40.author_group_speed_turn_shard import MOM_KEYS
from validation_fish_school_v41.joint_speed_turn_bins import (
    original_joint_speed_turn_source_moments,ALL_CATEGORIES
)

SOURCE_FREEZE="docs/V41_POST_V40_ORIGINAL_JOINT_SPEED_TURN_STRATA_FREEZE.md"
GROUPMAP_BLOB="57ea77c604414cb484f4abd1dd6637eecb2fdf90"

def moment_json(x):
    return {key:(int(x[key]) if key=="n" else np.asarray(x[key],dtype=float).tolist())
            for key in MOM_KEYS}

def one_published_original_group(g):
    group=str(g)
    if group not in tuple(str(i) for i in range(1,13)):
        raise SourceStop("V41_ORIGINAL_SHOAL_ID_NOT_IN_PUBLISHED_GROUPS")
    mapping=verify_crosswalk_bytes()
    index=verified_directory_index()
    if len(mapping)!=84 or len(index)!=84 or set(mapping)!=set(index):
        raise SourceStop("V41_ORIGINAL_EIDC_84_AUTHOR_TRIAL_IDENTITY_CHANGED")
    names=sorted((f for f in mapping if mapping[f]==group),key=lambda x:int(x[:-4]))
    if not 3<=len(names)<=12:
        raise SourceStop("V41_UNEXPECTED_ORIGINAL_SHOAL_TRIAL_COUNT")
    out={}
    for j,name in enumerate(names):
        raw,sha,retries=source_fetch_file(name,index[name])
        if hashlib.sha256(raw).hexdigest()!=sha:
            raise SourceStop("V41_ORIGINAL_SOURCE_SHA256_CHANGED_DURING_ANALYSIS")
        frame,positions=read_source(raw)
        original=original_panels(frame,positions,name)
        if name in FROZEN_EXAMPLE_GROUP_COUNTS and (
                original["n_original_eligible_group_times"]!=FROZEN_EXAMPLE_GROUP_COUNTS[name]):
            raise SourceStop("V41_ORIGINAL_PREVIOUS_200MS_FROZEN_COHORT_CHANGED")
        classified=original_joint_speed_turn_source_moments(original)
        all_stats=classified["stratum_sufficient_statistics"]
        if set(all_stats)!=set(ALL_CATEGORIES) or any(set(v)!=set(MODELS) for v in all_stats.values()):
            raise SourceStop("V41_NINE_SOURCE_STRATA_FOUR_FROZEN_MODELS_CHANGED")
        receipt={
         "original_author_source_file_ID":name,
         "original_author_biological_group_ID":group,
         "original_official_EIDC_source_file_size":index[name],
         "original_recomputed_source_SHA256":sha,
         "original_3_previous_independent_source_hashes_pinned":name in PINS,
         "source_native_frame_count":original["n_source_rows"],
         "source_eligible_group_times":original["n_original_eligible_group_times"],
         "source_eligible_original_fish_rows":original["n_original_test_fish_frame_rows"],
         "source_200ms_NA_and_clock_excluded_group_times":original["n_discarded_original_source_group_times"],
         "n_original_heading_undefined_rows":classified["source_original_turning_undefined_rows"],
         "original_4_joint_categories_sample_counts":classified["source_original_4_joint_categories_rows"],
         "original_previous_v40_marginal_category_sample_counts":classified["original_v40_marginal_category_counts"],
         "original_model_output_never_fitted_inside_source_shard":True,
         "source_9_strata_original_Ridge_sufficient_statistics_ONLY":{
            cat:{model:moment_json(all_stats[cat][model]) for model in MODELS}
            for cat in ALL_CATEGORIES}
        }
        out[name]=receipt
        del raw,frame,positions,original,classified,all_stats
        print(json.dumps({"stage":"V41_ORIGINAL_SOURCE_AUTHOR_GROUP",
              "original_2021_group":group,"source_files_done":j+1,
              "n_original_published_files_in_group":len(names),
              "individual_raw_fish_positions_or_Y_not_exported":True}),flush=True)
    return {
      "status":"V41_ORIGINAL_SOURCE_NINE_STRATA_SUMMARY_MOMENTS_AUTHENTICATED",
      "original_group_ID":group,
      "source_2021_original_EIDC_DOI":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
      "frozen_original_trial_to_shoal_mapping_git_blob":GROUPMAP_BLOB,
      "frozen_after_v40_marginals_but_before_joint_outcomes":SOURCE_FREEZE,
      "source_original_models":list(MODELS),
      "source_nine_joint_and_marginal_stratum_names":list(ALL_CATEGORIES),
      "n_original_shoal_recording_files":len(out),
      "no_individual_animal_XY_Y_or_source_fish_frame_times_redistributed":True,
      "no_predictive_effect_measured_inside_source_shard":True,
      "original_source_files":out
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--group",required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    try:result=one_published_original_group(a.group)
    except (SourceStop,OSError,KeyError,ValueError,IndexError,TypeError) as e:
        result={"status":"V41_ORIGINAL_SOURCE_OR_JOINT_SUPPORT_STOP",
                "original_group_ID":str(a.group),
                "source_STOP_reason":str(e),
                "new_original_biological_prediction_result":None}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf8")
    print(json.dumps({"stage":"V41_ORIGINAL_GROUP_SOURCE_ONLY_FINAL",
             "group":a.group,"status":result["status"],
             "n_original_files":result.get("n_original_shoal_recording_files"),
             "error":result.get("source_STOP_reason")}),flush=True)
    if result["status"]!="V41_ORIGINAL_SOURCE_NINE_STRATA_SUMMARY_MOMENTS_AUTHENTICATED":
        raise SystemExit(1)

if __name__=="__main__":main()
