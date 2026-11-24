"""v30 original MacGregor stickleback: three preselected EIDC source FILES.

The three file IDs are NOT authenticated as three independent biological shoals.
"""
from __future__ import annotations
import hashlib,json
from validation_fish_school_v26.eidc_source_only import BASE,FILE_LIMIT,fetch_bound,SourceStop as EIDCSourceStop
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v26.recording_age_forecast import SOURCE_IDS,read_source
from validation_fish_school_v30.harmonized_forecast import (
    build_original_recording,evaluate_source_files,save,SourceStop)


def run():
    if len(SOURCE_IDS)!=3 or tuple(SOURCE_IDS)!=("01.txt","02.txt","105.txt"):
        raise SourceStop("V30_PRESELECTED_EIDC_SOURCE_FROZEN_FILE_DRIFT")
    # Check all published source bytes and original SHA256 before opening XY.
    raw={}
    for name in SOURCE_IDS:
        b=fetch_bound(BASE+name,FILE_LIMIT)
        sha,size=PINS[name]
        if len(b)!=size or hashlib.sha256(b).hexdigest()!=sha:
            raise SourceStop("V30_EIDC_ORIGINAL_SHA256_SIZE_STOP_"+name)
        raw[name]=b
    cases={}
    for name in SOURCE_IDS:
        frame,pos=read_source(raw[name])
        cases[name]=build_original_recording(frame,pos,25,name)
    out=evaluate_source_files(cases,"stickleback",3,
        "MacGregor & Ioannou 2021 EIDC Gasterosteus aculeatus eight-fish recording")
    out["source_authentication"]={
      "original_DOI":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
      "all_three_original_SHA256_and_size_verified":True,
      "original_source_SHA256":{name:PINS[name][0] for name in SOURCE_IDS},
      "native_25fps_last_frame_column_verified":True,
      "original_NA_tracking_excluded_not_interpolated":True,
      "source_license":"Open Government Licence v3",
      "original_numbered_files_to_12_biological_shoals":"UNKNOWN",
      "original_numeric_units":"source pixel/sec and squared pixel/sec MSE"}
    return out


def main():
    try:out=run()
    except (SourceStop,EIDCSourceStop,OSError,ValueError,IndexError,KeyError) as e:
        out={"status":"SOURCE_OR_MODEL_STOP","reason":str(e),"new_observed_fish_result":None}
    save("validation_fish_school_v30/results/stickleback_common_model.json",out)
    print(json.dumps({"status":out["status"],"reason":out.get("reason"),
                      "results_by_horizon":out.get("results_by_horizon"),
                      "source_file_cohorts":out.get("original_source_cohort")},sort_keys=True))
if __name__=="__main__":main()
