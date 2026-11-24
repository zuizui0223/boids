"""v33b deterministic merger of 12 source-only original-shoal moment shards.

Original scientific test exactly v33, only source acquisition/execution sharded.
No fish movements, targets or group effect values in shard source reports.
"""
from __future__ import annotations
import argparse
import json
import hashlib
from pathlib import Path
import numpy as np

from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v32.stickleback_12_shoal import (
    verify_crosswalk_bytes, verified_directory_index
)
from validation_fish_school_v33.neighbor_panels import PANELS
from validation_fish_school_v33.neighbor_shoal_holdout import (
    source_group_holdout,save
)
from validation_fish_school_v33.source_shard_by_shoal import (
    MOMENT_KEYS,SCIENTIFIC_FREEZE,RECOVERY_FREEZE
)
from validation_fish_school_v33.stickleback_neighbor_source import (
    FROZEN_2021_N_NATIVE_ROWS,FROZEN_2021_ELIGIBLE_GROUP_TIMES,
    FROZEN_2021_N_DISCARDED_GROUP_TIMES,FROZEN_2021_N_FISH_TIME_ROWS,
    FROZEN_EXAMPLE_GROUP_COUNTS
)

STATUS="V33B_ORIGINAL_AUTHOR_SHOAL_SOURCE_SUFFICIENT_STATISTICS_ONLY"
FROZEN_MAP_SHA="57ea77c604414cb484f4abd1dd6637eecb2fdf90"
SHOALS=tuple(str(i) for i in range(1,13))


def restore_file_moments(blob):
    if not isinstance(blob,dict) or set(blob)!=set(PANELS):
        raise SourceStop("V33B_SHARD_SCIENCE_PANEL_NAMES_CHANGED")
    momentpanels={}
    for panel in PANELS:
        raw=blob[panel]
        if not isinstance(raw,dict) or set(raw)!=set(MOMENT_KEYS):
            raise SourceStop("V33B_SHARD_MOMENT_KEYS_CHANGED")
        n=raw["n"]
        if type(n)!=int or n<1000:
            raise SourceStop("V33B_SOURCE_MOMENT_SAMPLE_COUNT_NOT_INTEGER")
        p=14 if panel=="G_geometry" else 16 if panel=="GLOBAL" else 18
        dims={"sx":(p,),"sxx":(p,p),"sxy":(p,4),"sy":(4,),"syy":(4,)}
        vals={"n":n}
        for k,shape in dims.items():
            v=np.asarray(raw[k],dtype=np.float64)
            if v.shape!=shape or not np.isfinite(v).all():
                raise SourceStop("V33B_SHARD_MOMENT_DIMENSIONS_OR_NONFINITE_"+panel+"_"+k)
            vals[k]=v
        if not np.allclose(vals["sxx"],vals["sxx"].T,atol=1e-4,rtol=1e-9):
            raise SourceStop("V33B_AGGREGATE_SXX_NON_SYMMETRIC")
        momentpanels[panel]=vals
    requiredY=momentpanels["G_geometry"]
    for panel in PANELS[1:]:
        chk=momentpanels[panel]
        if chk["n"]!=requiredY["n"] or not np.allclose(chk["sy"],requiredY["sy"],rtol=1e-12,atol=1e-4) or not np.allclose(chk["syy"],requiredY["syy"],rtol=1e-12,atol=1e-1):
            raise SourceStop("V33B_ORIGINAL_SAME_TARGET_COHORT_INCONSISTENT")
    return momentpanels


def aggregate_all(shard_directory):
    groupmap=verify_crosswalk_bytes()
    index=verified_directory_index()
    if len(groupmap)!=84 or len(index)!=84 or set(groupmap)!=set(index):
        raise SourceStop("V33B_ORIGINAL_EIDC_AUTHOR_MAP_MANIFEST_STOP")
    shard_paths=list(shard_directory.glob("group_*.json"))
    if len(shard_paths)!=12:
        raise SourceStop("V33B_REQUIRED_EXACTLY_12_ORIGINAL_SOURCE_GROUP_ARTIFACTS")
    parsed={}
    for p in shard_paths:
        v=json.loads(p.read_text(encoding="utf8"))
        group=v.get("original_biological_shoal_ID")
        if group not in SHOALS or group in parsed or v.get("status")!=STATUS:
            raise SourceStop("V33B_SHOAL_ARTIFACT_SOURCE_STOP_OR_DUPLICATED")
        if v.get("original_author_84_to_12_Git_blob")!=FROZEN_MAP_SHA or v.get("scientific_frozen_protocol")!=SCIENTIFIC_FREEZE or v.get("execution_only_sharding_protocol")!=RECOVERY_FREEZE:
            raise SourceStop("V33B_SCIENCE_AND_SOURCE_FREEZE_MISMATCH")
        if v.get("source_canon_model_panels")!=list(PANELS) or v.get("source_fish_trajectories_or_original_Y_exported") is not False:
            raise SourceStop("V33B_SOURCE_PANEL_OR_ANIMAL_XY_NON_DISTRIBUTION_STOP")
        parsed[group]=v
    if set(parsed)!=set(SHOALS):
        raise SourceStop("V33B_SOURCE_SHARD_ORIGINAL_12_GROUP_MEMBERSHIP_STOP")

    files={}
    facts=[]
    for group in SHOALS:
        data=parsed[group]
        members={n for n,g in groupmap.items() if g==group}
        fragment=data.get("original_shoal_source_file_moments",{})
        if (not isinstance(fragment,dict) or set(fragment)!=members or
                data.get("n_original_trial_files_in_shoal")!=len(members)):
            raise SourceStop("V33B_SOURCE_GROUP_ARTIFACT_MISSING_OR_EXTRA_ORIGINAL_TRIALS")
        for name in sorted(members,key=lambda z:int(z[:-4])):
            if name in files:
                raise SourceStop("V33B_SOURCE_FILE_DOULE_IMPORTED_IN_TWO_GROUPS")
            row=fragment[name]
            if (row.get("source_original_EIDC_filename")!=name or
                row.get("original_author_Group")!=group or
                row.get("source_published_original_EIDC_bytes")!=index[name] or
                not isinstance(row.get("original_authenticated_SHA256"),str) or
                len(row["original_authenticated_SHA256"])!=64):
                raise SourceStop("V33B_SOURCE_EIDC_ORIGINAL_BYTES_GROUP_ID_OR_DIGEST_STOP")
            digest=row["original_authenticated_SHA256"]
            if not all(c in "0123456789abcdef" for c in digest):
                raise SourceStop("V33B_SOURCE_SHA256_DIGEST_BAD_HEX")
            if name in PINS and (digest!=PINS[name][0] or
                                 index[name]!=PINS[name][1]):
                raise SourceStop("V33B_SOURCE_PRIOR_THREE_ORIGINAL_DIGEST_STOP_"+name)
            if row.get("known_three_original_SHA256_pin_verified") is not (name in PINS):
                raise SourceStop("V33B_SOURCE_THREE_PIN_VERIFICATION_FLAG_STOP")
            m=restore_file_moments(row["source_sufficient_statistics"])
            if row["n_original_source_fish_frame_rows"]!=m["G_geometry"]["n"] or row["n_original_source_fish_frame_rows"]!=row["n_original_source_valid_group_times"]*8:
                raise SourceStop("V33B_SOURCE_ORIGINAL_8_FISH_ROW_COHORT_CHANGED")
            if name in FROZEN_EXAMPLE_GROUP_COUNTS and row["n_original_source_valid_group_times"]!=FROZEN_EXAMPLE_GROUP_COUNTS[name]:
                raise SourceStop("V33B_FROZEN_THREE_ORIGINAL_ELIGIBLE_TIMES_CHANGED")
            files[name]=m
            facts.append({k:row[k] for k in (
                "source_original_EIDC_filename",
                "original_author_Group",
                "source_published_original_EIDC_bytes",
                "original_authenticated_SHA256",
                "known_three_original_SHA256_pin_verified",
                "original_source_native_position_rows",
                "n_original_source_valid_group_times",
                "n_original_source_fish_frame_rows",
                "n_original_source_discarded_group_times",
                "source_download_retry_count"
            )})
    if set(files)!=set(groupmap) or len(facts)!=84:
        raise SourceStop("V33B_NOT_ALL_84_SOURCE_FILES_INCLUDED")
    sums={
        "native_rows":sum(x["original_source_native_position_rows"] for x in facts),
        "eligible_group_times":sum(x["n_original_source_valid_group_times"] for x in facts),
        "focal_fish_time_rows":sum(x["n_original_source_fish_frame_rows"] for x in facts),
        "removed_source_group_times":sum(x["n_original_source_discarded_group_times"] for x in facts)
    }
    if sums!={"native_rows":FROZEN_2021_N_NATIVE_ROWS,
              "eligible_group_times":FROZEN_2021_ELIGIBLE_GROUP_TIMES,
              "focal_fish_time_rows":FROZEN_2021_N_FISH_TIME_ROWS,
              "removed_source_group_times":FROZEN_2021_N_DISCARDED_GROUP_TIMES}:
        raise SourceStop("V33B_V32_ORIGINAL_ALL_84_SOURCE_COHORT_TOTALS_DRIFT")

    meta={
       "source":"MacGregor & Ioannou 2021 original EIDC 84 native trials",
       "original_EIDC_DOI":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
       "original_84_frozen_index":"270ae039d690ca4dc315416a5390b3cd3cbfa14e9dcbc1e456ec8e8302158ddc",
       "source_2021_author_trial_group_IDs":"Zenodo 5490572 original Trial and Group; verified original 84-to-12 Git blob "+FROZEN_MAP_SHA,
       "parallel_source_shoal_shards":12,
       "original_EIDC_individual_source_files":84,
       "original_aggregate_cohort_counts":sums,
       "per_original_file_source_authentication_without_raw_tracks":sorted(facts,key=lambda x:int(x["source_original_EIDC_filename"][:-4])),
       "all_source_original_published_sizes_verified":True,
       "known_three_original_SHA256_pins_replayed":True,
       "unknown_other_81_original_MD5_not_claimed":True,
       "source_upload_no_individual_raw_fish_XY_or_future_trajectory":True,
       "ephemeral_original_sufficient_statistic_shards_only":True
    }
    out=source_group_holdout(files,groupmap,meta)
    if out["n_original_EIDC_trial_files"]!=84 or out["n_original_biological_shoal_holdouts"]!=12:
        raise SourceStop("V33B_ORIGINAL_BIOLOGICAL_SHOAL_FOLDS_INCOMPLETE")
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--shards",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    try: result=aggregate_all(args.shards)
    except (SourceStop,OSError,ValueError,KeyError,IndexError,TypeError) as ex:
        result={"status":"V33B_SOURCE_COHORT_OR_GROUP_MODEL_STOP",
            "reason":str(ex),"new_original_near_neighbor_results":None,
            "no_original_individual_fish_XY_redistributed":True}
    save(args.out,result)
    print(json.dumps({
       "status":result["status"],
       "reason":result.get("reason"),
       "n_source_trial_files":result.get("n_original_EIDC_trial_files"),
       "n_independent_original_shoal_holdouts":result.get("n_original_biological_shoal_holdouts"),
       "original_source_group_results":result.get("source_original_group_result")
    },sort_keys=True),flush=True)
    if result["status"]!="V33_ORIGINAL_84_RECORDINGS_12_SHOALS_LOCAL_VERSUS_GLOBAL_HOLDOUT":
        raise SystemExit(1)

if __name__=="__main__":main()
