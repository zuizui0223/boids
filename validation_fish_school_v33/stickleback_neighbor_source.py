"""v33 all-original 84 EIDC files, 12 author shoals, neighbor-map diagnostics.

Only original fish native source processed on GitHub runner. Raw fish XY and
future trajectory time-series never uploaded to repository or artifacts.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from validation_fish_school_v26.eidc_source_only import SourceStop as EIDCStop
from validation_fish_school_v26.recording_age_forecast import read_source
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v32.stickleback_12_shoal import (
    verify_crosswalk_bytes,verified_directory_index,source_fetch_file
)
from validation_fish_school_v33.neighbor_panels import original_panels
from validation_fish_school_v33.neighbor_shoal_holdout import file_moments,source_group_holdout,save

FROZEN_2021_N_NATIVE_ROWS=3147771
FROZEN_2021_ELIGIBLE_GROUP_TIMES=570360
FROZEN_2021_N_DISCARDED_GROUP_TIMES=57968
FROZEN_2021_N_FISH_TIME_ROWS=4562880
FROZEN_EXAMPLE_GROUP_COUNTS={"01.txt":6966,"02.txt":8015,"105.txt":5567}
OUTPUT=Path("validation_fish_school_v33/results/stickleback_84_trials_near_far_rotated_12_shoals.json")


def run():
    groupmap=verify_crosswalk_bytes()
    index=verified_directory_index()
    if set(index)!=set(groupmap) or len(index)!=84:
        raise SourceStop("V33_FROZEN_EIDC_INDEX_AUTHOR_SHOAL_MAP_NOT_EXACT_84")
    allfiles=sorted(index,key=lambda x:int(x[:-4]))
    facts=[]
    moments={}
    for i,name in enumerate(allfiles):
        body,digest,number_retries=source_fetch_file(name,index[name])
        clock,xy=read_source(body)
        now=original_panels(clock,xy,name)
        if name in FROZEN_EXAMPLE_GROUP_COUNTS and (
            now["n_original_eligible_group_times"]!=FROZEN_EXAMPLE_GROUP_COUNTS[name]):
            raise SourceStop("V33_ORIGINAL_V32_EXAMPLE_SOURCE_COHORT_CHANGED_"+name)
        # No animal source position, time, or future response rows stored.
        moments[name]=file_moments(now)
        facts.append({
           "original_source_filename":name,
           "original_author_2021_Group_ID":groupmap[name],
           "original_published_EIDC_byte_count":index[name],
           "original_fetched_2021_source_SHA256":digest,
           "original_known_independent_SHA256_pin_replayed":name in PINS,
           "n_original_native_fish_tracking_frames":now["n_source_rows"],
           "n_original_eligible_group_times":now["n_original_eligible_group_times"],
           "n_fish_time_paired_focal_prediction_rows":now["n_original_test_fish_frame_rows"],
           "original_eligible_timestamp_rows_removed_for_NA_or_clock":now["n_discarded_original_source_group_times"],
           "n_file_source_acquisition_retries":number_retries
        })
        del body,clock,xy,now
        if (i+1)%12==0 or (i+1)==84:
            print(json.dumps({
                "stage":"V33_ORIGINAL_2021_FILE_SOURCE_GATE",
                "n_original_2021_fish_files_authenticated":i+1,
                "n_original_biological_shoals_with_files":len({z["original_author_2021_Group_ID"] for z in facts}),
                "no_original_animal_positions_uploaded":True}),flush=True)
    if len(moments)!=84 or len(facts)!=84 or set(groupmap)!=set(moments):
        raise SourceStop("V33_ALL_84_ORIGINAL_SOURCE_NOT_ADMITTED")
    nNative=sum(x["n_original_native_fish_tracking_frames"] for x in facts)
    nEligible=sum(x["n_original_eligible_group_times"] for x in facts)
    nDiscard=sum(x["original_eligible_timestamp_rows_removed_for_NA_or_clock"] for x in facts)
    nFish=sum(x["n_fish_time_paired_focal_prediction_rows"] for x in facts)
    if (nNative!=FROZEN_2021_N_NATIVE_ROWS or
        nEligible!=FROZEN_2021_ELIGIBLE_GROUP_TIMES or
        nDiscard!=FROZEN_2021_N_DISCARDED_GROUP_TIMES or
        nFish!=FROZEN_2021_N_FISH_TIME_ROWS):
        raise SourceStop("V33_ORIGINAL_2021_ALL_84_V32_COHORT_REPLAY_MISMATCH")
    meta={
       "source":"MacGregor & Ioannou 2021 original EIDC 84 fish tracks",
       "original_EIDC_DOI":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
       "author_Zenodo_2021_summary_source":"5490572 MacGregorIoannou_Data.csv source SHA256 f642200bfcd0741e80969981b0a7358462f63ac816bd93dba1b95983855ea3f3",
       "original_group_count":12,
       "original_video_count":84,
       "n_native_tracking_rows":nNative,
       "n_eligible_original_shoal_time_rows":nEligible,
       "n_source_fish_time_prediction_rows":nFish,
       "n_original_time_rows_dropped_source_NA_clock":nDiscard,
       "per_original_EIDC_file_authentication_and_nonautonomous_group_id":facts,
       "all_84_original_provider_directory_sizes_verified":True,
       "source_original_known_3_SHA256_pins_verified":True,
       "no_original_individual_XY_or_Y_uploaded":True,
    }
    out=source_group_holdout(moments,groupmap,meta)
    if (out["n_original_EIDC_trial_files"]!=84 or
        out["n_original_biological_shoal_holdouts"]!=12):
        raise SourceStop("V33_ORIGINAL_GROUP_HELDOUT_NOT_12")
    return out


def main():
    try:
        result=run()
    except (SourceStop,EIDCStop,OSError,ValueError,IndexError,KeyError) as exc:
        result={"status":"V33_ORIGINAL_SOURCE_OR_MODEL_REPLAY_STOP",
                "reason":str(exc),
                "new_original_near_neighbor_biological_result":None,
                "original_fish_XY_redistributed":False}
    save(OUTPUT,result)
    print(json.dumps({
       "status":result["status"],
       "reason":result.get("reason"),
       "n_original_source_files":result.get("n_original_EIDC_trial_files"),
       "n_original_shoal_holdouts":result.get("n_original_biological_shoal_holdouts"),
       "source_group_result":result.get("source_original_group_result")
    },sort_keys=True),flush=True)

if __name__=="__main__":main()
