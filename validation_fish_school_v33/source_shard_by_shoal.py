"""v33b unchanged original v33 84-trial source panels: GROUP-SHARDED only.

Each original author's 12 biological groups is assigned to one independent
short GH Actions job. Outputs AGGREGATE sufficient statistics, not raw fish XY.
No per-group model fit, future velocity score or changed ecological predictor.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v26.recording_age_forecast import read_source
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v32.stickleback_12_shoal import (
    verify_crosswalk_bytes,verified_directory_index,source_fetch_file
)
from validation_fish_school_v33.neighbor_panels import original_panels,PANELS
from validation_fish_school_v33.neighbor_shoal_holdout import file_moments
from validation_fish_school_v33.stickleback_neighbor_source import (
    FROZEN_2021_N_NATIVE_ROWS,FROZEN_2021_ELIGIBLE_GROUP_TIMES,
    FROZEN_2021_N_DISCARDED_GROUP_TIMES,FROZEN_2021_N_FISH_TIME_ROWS,
    FROZEN_EXAMPLE_GROUP_COUNTS
)

MOMENT_KEYS=("n","sx","sxx","sxy","sy","syy")
SCIENTIFIC_FREEZE="docs/V33_TOPOLOGICAL_NEAR_FAR_POSITION_ASSIGNMENT_FROZEN.md"
RECOVERY_FREEZE="docs/V33B_SHARDED_ORIGINAL_SOURCE_EXECUTION_AMENDMENT.md"

def group_shard(group):
    if str(group) not in [str(i) for i in range(1,13)]:
        raise SourceStop("V33B_UNREGISTERED_ORIGINAL_SHOAL_ID")
    g=str(group)
    original_groupmap=verify_crosswalk_bytes()
    original_index=verified_directory_index()
    if len(original_groupmap)!=84 or set(original_groupmap)!=set(original_index):
        raise SourceStop("V33B_ORIGINAL_84_SOURCE_GROUP_MAP_CHANGED")
    original_files=sorted((n for n in original_groupmap if original_groupmap[n]==g),
                           key=lambda x:int(x[:-4]))
    if not 3<=len(original_files)<=12:
        raise SourceStop("V33B_ORIGINAL_GROUP_BAD_TRIAL_COUNT")
    files={}
    for idx,name in enumerate(original_files):
        raw,sha,retries=source_fetch_file(name,original_index[name])
        frame,pos=read_source(raw)
        source=original_panels(frame,pos,name)
        if name in FROZEN_EXAMPLE_GROUP_COUNTS and source[
            "n_original_eligible_group_times"]!=FROZEN_EXAMPLE_GROUP_COUNTS[name]:
            raise SourceStop("V33B_ORIGINAL_FROZEN_THREE_FILE_COHORT_CHANGED_"+name)
        moments=file_moments(source)
        source_sha=hashlib.sha256(raw).hexdigest()
        if sha!=source_sha:
            raise SourceStop("V33B_ORIGINAL_SOURCE_SHA256_INTERNAL_MISMATCH")
        record={
            "source_original_EIDC_filename":name,
            "original_author_Group":g,
            "source_published_original_EIDC_bytes":original_index[name],
            "original_authenticated_SHA256":sha,
            "known_three_original_SHA256_pin_verified":name in PINS,
            "original_source_native_position_rows":source["n_source_rows"],
            "n_original_source_valid_group_times":source["n_original_eligible_group_times"],
            "n_original_source_fish_frame_rows":source["n_original_test_fish_frame_rows"],
            "n_original_source_discarded_group_times":source["n_discarded_original_source_group_times"],
            "source_download_retry_count":retries,
            "source_sufficient_statistics":{
              k:{moment:(int(z[moment]) if moment=="n" else
                          np.asarray(z[moment],dtype=float).tolist())
                 for moment in MOMENT_KEYS}
              for k,z in moments.items()
            }
        }
        if set(record["source_sufficient_statistics"])!=set(PANELS):
            raise SourceStop("V33B_FROZEN_SIX_PANEL_MOMENTS_CHANGED")
        files[name]=record
        del raw,frame,pos,source,moments
        print(json.dumps({"stage":"ORIGINAL_SHOAL_SOURCE_ONLY_SIX_PANEL_MOMENTS",
                "group":g,"original_group_trial_files_processed":idx+1,
                "n_original_source_trial_files_in_group":len(original_files),
                "unprocessed_individual_fish_XY_not_exported":True}),flush=True)
    return {
      "status":"V33B_ORIGINAL_AUTHOR_SHOAL_SOURCE_SUFFICIENT_STATISTICS_ONLY",
      "original_biological_shoal_ID":g,
      "source_study":"MacGregor & Ioannou 2021 original EIDC 84 videos",
      "n_original_trial_files_in_shoal":len(original_files),
      "original_author_84_to_12_Git_blob":"57ea77c604414cb484f4abd1dd6637eecb2fdf90",
      "scientific_frozen_protocol":SCIENTIFIC_FREEZE,
      "execution_only_sharding_protocol":RECOVERY_FREEZE,
      "source_canon_model_panels":list(PANELS),
      "source_full_84_cohort_reference":{
         "n_original_tracking_rows":FROZEN_2021_N_NATIVE_ROWS,
         "n_original_valid_group_times":FROZEN_2021_ELIGIBLE_GROUP_TIMES,
         "n_original_removed_group_times":FROZEN_2021_N_DISCARDED_GROUP_TIMES,
         "n_original_fish_frame_rows":FROZEN_2021_N_FISH_TIME_ROWS},
      "source_fish_trajectories_or_original_Y_exported":False,
      "source_original_aggregate_only_to_ephemeral_GH_artifact":True,
      "original_shoal_source_file_moments":files
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--group",required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    try:out=group_shard(args.group)
    except (SourceStop,OSError,ValueError,KeyError,IndexError,TypeError) as ex:
        out={
          "status":"V33B_SOURCE_SHARD_STOP",
          "original_biological_shoal_ID":args.group,
          "source_stop_reason":str(ex),
          "new_original_fish_behavior_effect":None}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,sort_keys=True,separators=(",",":"))+"\n",
                        encoding="utf8")
    print(json.dumps({"stage":"V33B_ORIGINAL_GROUP_SHARD_COMPLETE",
       "group":args.group,"status":out["status"],
       "n_original_source_files":out.get("n_original_trial_files_in_shoal"),
       "source_stop_reason":out.get("source_stop_reason")}),flush=True)
    if out["status"]!="V33B_ORIGINAL_AUTHOR_SHOAL_SOURCE_SUFFICIENT_STATISTICS_ONLY":
        raise SystemExit(1)

if __name__=="__main__":main()
