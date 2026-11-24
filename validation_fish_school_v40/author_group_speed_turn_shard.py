"""v40 source-only 12 original AUTHOR shoal shards: frozen v33 models,
same Y and G, heldout test speed/turn categories computed before future Y.
Per-file summary moments only; no animal tracks, time series or future Y copied.
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
from validation_fish_school_v40.source_speed_turn_strata import (
   source_trial_stratified_moments,MODELS,CATEGORIES)

SOURCE_FREEZE="docs/V40_STICKLEBACK_84_TRIAL_12_SHOAL_SPEED_TURN_MAPPED_NEIGHBOR_INFO_FREEZE.md"
FROZEN_GROUPMAP_BLOB="57ea77c604414cb484f4abd1dd6637eecb2fdf90"
MOM_KEYS=("n","sx","sxx","sxy","sy","syy")


def to_safe_json_moments(original):
    return {cat:{
         model:{key:(int(item[key]) if key=="n" else np.asarray(item[key],dtype=float).tolist())
                for key in MOM_KEYS}
         for model,item in original[cat].items()
      } for cat in CATEGORIES}


def one_published_original_group(group):
    g=str(group)
    if g not in tuple(str(k) for k in range(1,13)):
        raise SourceStop("V40_UNKNOWN_ORIGINAL_TRUE_SHOAL_ID")
    m=verify_crosswalk_bytes()
    directory=verified_directory_index()
    if len(m)!=84 or len(directory)!=84 or set(m)!=set(directory):
        raise SourceStop("V40_AUTHOR_ORIGINAL_84_FILES_NOT_REPRODUCED")
    expected=sorted((n for n in m if m[n]==g),key=lambda x:int(x[:-4]))
    if not 3<=len(expected)<=12:
        raise SourceStop("V40_ORIGINAL_GROUP_FILE_NUMBER_OUTSIDE_AUTHOR_RANGE")
    original={}
    for j,name in enumerate(expected):
        raw,sha,retry=source_fetch_file(name,directory[name])
        if hashlib.sha256(raw).hexdigest()!=sha:
            raise SourceStop("V40_ORIGINAL_EIDC_FILE_HASH_NOT_STABLE")
        f,p=read_source(raw)
        src=original_panels(f,p,name)
        if name in FROZEN_EXAMPLE_GROUP_COUNTS and src["n_original_eligible_group_times"]!=FROZEN_EXAMPLE_GROUP_COUNTS[name]:
            raise SourceStop("V40_PRIOR_V33_ORIGINAL_COHORT_DRIFT_"+name)
        derived=source_trial_stratified_moments(src)
        data={
           "original_2021_author_file":name,"original_2021_author_biological_shoal_ID":g,
           "original_EIDC_bytes_official":directory[name],
           "original_EIDC_SHA256_newly_recomputed":sha,
           "original_3_prior_source_SHA256_pins_pass":name in PINS,
           "original_source_native_time_rows":src["n_source_rows"],
           "original_eligible_group_times":src["n_original_eligible_group_times"],
           "original_group_time_rows_dropped_for_source_NA_or_clock":src["n_discarded_original_source_group_times"],
           "original_source_focal_fish_frame_rows":src["n_original_test_fish_frame_rows"],
           "n_source_turn_undefined_heading_rows":derived["n_original_turn_undefined_speed_product_rows"],
           "source_current_speed_and_turn_metadata_not_target_values":{
              k:derived[k] for k in (
                "n_original_turn_well_defined_rows","n_speed_low_fish_frame_rows",
                "n_speed_high_fish_frame_rows","n_turn_low_fish_frame_rows",
                "n_turn_high_fish_frame_rows",
                "mean_current_focal_speed_source_units_per_s",
                "source_focal_speed_median",
                "median_defined_angular_change_rad_over_200ms"
              )
           },
           "stratum_source_moment_sufficient_statistics_only":to_safe_json_moments(derived["moments"])
        }
        original[name]=data
        del raw,f,p,src,derived
        print(json.dumps({"status":"V40_ORIGINAL_AUTHOR_SHOAL_SOURCE_ONLY_MOMENTS",
             "true_group":g,"n_original_files_verified":j+1,
             "n_original_group_files":len(expected),
             "original_fish_XY_or_future_Y_redistributed":False}),flush=True)
    return {
       "status":"V40_ALL_ORIGINAL_AUTHOR_GROUP_FILES_AUTHENTICATED_STRATA_MOMENT_ONLY",
       "original_2021_true_group":g,
       "original_experimental_group_map_git_blob":FROZEN_GROUPMAP_BLOB,
       "source_original_science_freeze":SOURCE_FREEZE,
       "n_original_file_records":len(original),
       "fixed_source_model_names":list(MODELS),
       "fixed_test_strata_names":list(CATEGORIES),
       "original_fish_Y_XY_or_kinematic_timeseries_redistributed":False,
       "new_original_near_neighbor_group_effect_not_yet_scored":True,
       "source_original_file_records":original
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--group",required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    try:d=one_published_original_group(args.group)
    except (SourceStop,KeyError,IndexError,ValueError,OSError) as ex:
        d={"status":"V40_SOURCE_OR_KINEMATIC_STRATA_STOP",
           "group":str(args.group),"source_stop_reason":str(ex),
           "new_original_biological_result":None}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,sort_keys=True,separators=(",",":"))+"\n",encoding="utf8")
    print(json.dumps({"stage":"V40_AUTHOR_SHOAL_SOURCE_SHARD_FINAL",
                      "group":args.group,"status":d["status"],
                      "n_original_files":d.get("n_original_file_records"),
                      "reason":d.get("source_stop_reason")}),flush=True)
    if d["status"]!="V40_ALL_ORIGINAL_AUTHOR_GROUP_FILES_AUTHENTICATED_STRATA_MOMENT_ONLY":
        raise SystemExit(1)

if __name__=="__main__":main()
