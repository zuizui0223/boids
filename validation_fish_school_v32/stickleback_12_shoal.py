"""v32 original 84 EIDC trial files, exactly 12 author-ID shoals held out.

Batches source one original file at a time; original pixel tracks/response
rows are NEVER committed or uploaded. Same 200ms 14D v30 predictor.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np

from validation_fish_school_v26.eidc_source_only import (
    BASE,FILE_LIMIT,fetch_bound,parse_listing,SourceStop as EIDCSourceStop
)
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v26.recording_age_forecast import read_source
from validation_fish_school_v30.harmonized_forecast import (
    MODEL_NAMES, build_original_recording, SourceStop
)
from validation_fish_school_v32.moment_loo import (
    source_moments, group_heldout, sum_moments,
    train_only_standardized_ridge, score_file_moment,save
)

CROSSWALK=Path("docs/v31_verification/EIDC_84_ORIGINAL_FILES_TO_12_AUTHOR_SHOALS_VERIFIED.json")
GIT_BLOB_SHA="57ea77c604414cb484f4abd1dd6637eecb2fdf90"
INDEX_SHA256="270ae039d690ca4dc315416a5390b3cd3cbfa14e9dcbc1e456ec8e8302158ddc"
SOURCE_DATA_SHA256="f642200bfcd0741e80969981b0a7358462f63ac816bd93dba1b95983855ea3f3"
SOURCE_CODE_SHA256="c7095571b67376d382164bda000d40f90d737837577d272531f983a049c7e3e0"
REPLAY_PRIOR=Path("docs/v30_verification/STICKLEBACK_COMMON_MODEL_ORIGINAL_REAGGREGATION.json")
REPLAY_SOURCE_IDS=("01.txt","02.txt","105.txt")
REPLAY_N_NATIVE_GROUP_TIMES={"01.txt":6966,"02.txt":8015,"105.txt":5567}
OUTPUT=Path("validation_fish_school_v32/results/stickleback_84_trials_12_shoal_holdout.json")


def verify_crosswalk_bytes():
    if not CROSSWALK.is_file() or not REPLAY_PRIOR.is_file():
        raise SourceStop("V32_FROZEN_SOURCE_PROVENANCE_FILES_MISSING")
    blob=CROSSWALK.read_bytes()
    gitblob=hashlib.sha1(b"blob "+str(len(blob)).encode()+b"\x00"+blob).hexdigest()
    if gitblob!=GIT_BLOB_SHA:
        raise SourceStop("V32_FROZEN_84_TO_12_AUTHOR_PROVENANCE_GITBLOB_MISMATCH")
    src=json.loads(blob)
    if src.get("status")!="SOURCE_AUTHENTIC_84_EIDC_RECORDING_TO_12_ORIGINAL_SHOAL_ID_ADMITTED":
        raise SourceStop("V32_ORIGINAL_AUTHOR_CROSSWALK_NOT_ADMITTED")
    if (src.get("original_zenodo_source_data_csv_SHA256")!=SOURCE_DATA_SHA256 or
        src.get("original_zenodo_source_code_R_SHA256")!=SOURCE_CODE_SHA256 or
        src.get("n_original_recording_files")!=84 or src.get("n_distinct_original_shoals")!=12):
        raise SourceStop("V32_ORIGINAL_AUTHOR_ZENODO_SOURCE_VERSION_CHANGED")
    m=src.get("original_recording_to_shoal",{})
    if not isinstance(m,dict) or len(m)!=84 or len(set(m.values()))!=12:
        raise SourceStop("V32_SOURCE_ORIGINAL_AUTHOR_GROUP_COUNT_STOP")
    if [m.get(n) for n in REPLAY_SOURCE_IDS]!=["4","2","11"]:
        raise SourceStop("V32_ORIGINAL_AUTHENTICATED_THREE_FILE_GROUPS_NOT_REPLAYED")
    return m


def verified_directory_index():
    raw=fetch_bound(BASE,2*1024*1024)
    if hashlib.sha256(raw).hexdigest()!=INDEX_SHA256:
        raise SourceStop("V32_ORIGINAL_EIDC_DIRECTORY_MANIFEST_SHA256_DRIFT")
    files=parse_listing(raw)
    if len(files)!=84:
        raise SourceStop("V32_EIDC_NO_LONGER_HAS_84_ORIGINAL_SOURCE_RECORDINGS")
    return files


def source_fetch_file(name,provider_size):
    # Source-only bounded retry of SAME original EIDC published URL.
    # Never use a replacement source or alter file/admission model after MSE.
    for trial in range(2):
        try:
            body=fetch_bound(BASE+name,FILE_LIMIT)
        except (EIDCSourceStop,OSError) as exc:
            if trial==1:raise SourceStop("V32_SOURCE_DOWNLOAD_TRANSPORT_STOP_"+name) from exc
            continue
        if len(body)!=provider_size:
            if trial==1:raise SourceStop("V32_EIDC_ORIGINAL_PROVIDER_SIZE_STOP_"+name)
            continue
        digest=hashlib.sha256(body).hexdigest()
        if name in PINS and (len(body)!=PINS[name][1] or digest!=PINS[name][0]):
            raise SourceStop("V32_PUBLISHED_THREE_SOURCE_SHA256_PIN_STOP_"+name)
        return body,digest,trial
    raise SourceStop("V32_ORIGINAL_SOURCE_DOWNLOAD_STOP_"+name)


def prior_three_file_moment_replay(cases):
    if set(cases)!=set(REPLAY_SOURCE_IDS):
        raise SourceStop("V32_ORIGINAL_THREE_FILE_REPLAY_TRIALS_NOT_PRESENT")
    baseline=json.loads(REPLAY_PRIOR.read_text(encoding="utf-8"))
    previous=baseline["source_numeric_results_reaggregated"]
    scores={k:{"short":[],"delayed":[]} for k in MODEL_NAMES}
    for held in REPLAY_SOURCE_IDS:
        others=[x for x in REPLAY_SOURCE_IDS if x!=held]
        for model in MODEL_NAMES:
            train=sum_moments([cases[k][model] for k in others])
            B,a=train_only_standardized_ridge(train)
            y=score_file_moment(cases[held][model],B,a)
            for h in ("short","delayed"):
                scores[model][h].append(y[h])
    observed={}
    for h in ("short","delayed"):
        observed[h]={}
        for model in MODEL_NAMES:
            value=float(np.mean(scores[model][h]))
            expected=float(previous[h]["equal_original_file_mean_MSE"][model])
            if abs(value-expected)>0.01:
                raise SourceStop("V32_ORIGINAL_V30_BACKEND_MSE_REPLAY_STOP_"+model+"_"+h)
            observed[h][model]=value
    return {
      "status":"EXACT_V30_ORIGINAL_THREE_FILE_BACKEND_REPLAY_PASS",
      "target_old_original_file_holdouts":list(REPLAY_SOURCE_IDS),
      "all_six_models_both_future_horizons_equal_file_MSE_within_0_01":True,
      "recomputed_mse":observed,
      "NOT_new_12_shoal_result":True
    }


def run():
    crosswalk=verify_crosswalk_bytes()
    index=verified_directory_index()
    if set(index)!=set(crosswalk):
        raise SourceStop("V32_ORIGINAL_AUTHOR_JOIN_84_EIDC_FILENAMES_DIFFER")
    origin=sorted(index,key=lambda x:int(x[:-4]))
    # Source authentication/replay three pre-pinned prior files FIRST.
    # This order is source-independent; ALL remaining 81 files are required.
    ordering=list(REPLAY_SOURCE_IDS)+[name for name in origin if name not in REPLAY_SOURCE_IDS]
    facts={}
    source_mom={}
    backend_replay=None
    for i,name in enumerate(ordering):
        raw,digest,retries=source_fetch_file(name,index[name])
        native_frame,native_xy=read_source(raw)
        src=build_original_recording(native_frame,native_xy,25,name)
        # Immediately reduce raw source to train-only model moments;
        # do NOT retain original source XY in the 84-file ledger.
        source_mom[name]=source_moments(src)
        facts[name]={
          "name":name,
          "original_author_shoal_ID":crosswalk[name],
          "original_EIDC_published_byte_size":index[name],
          "source_SHA256_recomputed":digest,
          "source_provider_MD5_published_for_this_TXT":False,
          "original_source_download_retries_before_exact_size":retries,
          "n_native_source_position_rows":src["n_source_rows"],
          "n_candidate_group_times":src["n_original_candidate_group_times"],
          "n_eligible_original_group_times":src["n_original_eligible_group_times"],
          "n_original_fish_frame_test_rows":src["n_original_eligible_fish_frames"],
          "n_missing_or_invalid_source_timestamps":src["n_original_rows_excluded_nonfinite_or_noncontiguous"]
        }
        if name in REPLAY_N_NATIVE_GROUP_TIMES and (
            src["n_original_eligible_group_times"]!=REPLAY_N_NATIVE_GROUP_TIMES[name]):
            raise SourceStop("V32_ORIGINAL_V30_THREE_PREVIOUS_SOURCE_COHORT_DRIFT_"+name)
        del raw,native_frame,native_xy,src
        if i==len(REPLAY_SOURCE_IDS)-1:
            backend_replay=prior_three_file_moment_replay(source_mom)
            print(json.dumps({"stage":"ORIGINAL_THREE_FILE_BACKEND_REPLAY",
                              "status":backend_replay["status"]}),flush=True)
        if (i+1)%12==0 or i+1==84:
            print(json.dumps({"stage":"SOURCE_ONLY_PROGRESS",
                   "n_original_trajectories_authenticated":i+1,
                   "n_groups_identified":len({facts[x]["original_author_shoal_ID"] for x in facts}),
                   "all_samples_finite_at_all_input_output_times":True}),flush=True)
    if len(facts)!=84 or backend_replay is None:
        raise SourceStop("V32_NOT_ALL_84_AUTHENTICATED")
    metadata={
       "original_EIDC_directory_sha256":INDEX_SHA256,
       "source_2021_author_zenodo_Dryad_summary_sha256":SOURCE_DATA_SHA256,
       "source_2021_original_author_R_code_sha256":SOURCE_CODE_SHA256,
       "original_provenance_crosswalk_git_blob_sha":GIT_BLOB_SHA,
       "source_replay_three_file_backend":backend_replay,
       "per_original_84_trials_source_authentication":[facts[name] for name in origin],
       "no_source_animal_XY_or_Y_exported":True,
       "note_other_81_original_source_files":"Provider index exposes file size but not individual published per-TXT MD5; runner computed SHA256 and verified published EIDC size",
       "n_original_source_files":84,
       "n_original_shoals":12
    }
    answer=group_heldout(source_mom,crosswalk,metadata)
    # Independent summary exact source provenance and science checks.
    if answer["n_original_trial_files"]!=84 or answer["n_original_heldout_biological_shoals"]!=12:
        raise SourceStop("V32_ORIGINAL_HOLDOUT_GROUP_COUNT_MISMATCH")
    return answer


def main():
    try:result=run()
    except (SourceStop,EIDCSourceStop,OSError,ValueError,KeyError,IndexError) as ex:
        result={"status":"SOURCE_OR_GROUP_HOLDOUT_STOP",
                "reason":str(ex),"v32_original_twelve_shoal_effect":None,
                "no_raw_fish_source_shared":True}
    save(OUTPUT,result)
    print(json.dumps({"status":result["status"],"reason":result.get("reason"),
       "n_original_shoals":result.get("n_original_heldout_biological_shoals"),
       "n_trial_files":result.get("n_original_trial_files"),
       "results_by_horizon":result.get("results_by_horizon")},sort_keys=True),flush=True)


if __name__=="__main__":main()
