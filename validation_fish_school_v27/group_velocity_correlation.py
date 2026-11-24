"""v27 original-source collective-mean-velocity temporal autocorrelation.

Observed group-state descriptive test. NO future fish prediction, raw fish
time-series export, social-causal, acoustic or information-flow claim.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

AGES=(.2,1.,2.)

class SourceStop(Exception): pass


def exact_group_correlation(pos, indices, fps, speed_frames):
    arr=np.asarray(pos,dtype=np.float64)
    idx=np.asarray(indices,dtype=np.int64)
    if arr.ndim!=3 or arr.shape[2]!=2 or arr.shape[1]<3 or len(idx)<200:
        raise SourceStop("CORR_ORIGINAL_FISH_COORDINATE_COHORT_STOP")
    if not np.all(np.diff(idx)>0):
        raise SourceStop("CORR_SOURCE_INDEX_MONOTONIC_STOP")
    if fps not in (25.,30.,50.) or speed_frames not in (3,5):
        raise SourceStop("CORR_FROZEN_SOURCE_CLOCK_STOP")
    steps=[int(round(age*fps)) for age in AGES]
    if any(abs(t-age*fps)>1e-8 for t,age in zip(steps,AGES)):
        raise SourceStop("CORR_NONINTEGRAL_AGE_STOP")
    if np.min(idx)-max(steps)-speed_frames<0 or np.max(idx)>=len(arr):
        raise SourceStop("CORR_ORIGINAL_TIMESTAMP_OUT_OF_BOUNDS")
    den=speed_frames/fps
    now=((arr[idx]-arr[idx-speed_frames])/den).mean(axis=1)
    if not np.isfinite(now).all():
        raise SourceStop("CORR_CURRENT_SCHOOL_STATE_NONFINITE")
    correlations={}
    for age,step in zip(AGES,steps):
        past=((arr[idx-step]-arr[idx-step-speed_frames])/den).mean(axis=1)
        if not np.isfinite(past).all():
            raise SourceStop("CORR_STALE_SCHOOL_STATE_NONFINITE")
        centered_now=now-now.mean(axis=0,keepdims=True)
        centered_past=past-past.mean(axis=0,keepdims=True)
        denominator=float(np.linalg.norm(centered_now)*np.linalg.norm(centered_past))
        if not denominator>1e-10:
            raise SourceStop("CORR_ZERO_GROUP_STATE_VARIABILITY")
        score=float((centered_now*centered_past).sum()/denominator)
        if not np.isfinite(score) or abs(score)>1+1e-10:
            raise SourceStop("CORR_NUMERIC_BOUND_STOP")
        correlations[f"age_{age:g}s"]=score
    return {"correlations":correlations,"n_source_group_times":int(len(idx)),
            "n_native_fish_per_group":int(arr.shape[1]),
            "original_fps":fps,
            "current_velocity_interval_frames":speed_frames,
            "new_fish_movement_prediction_computed":False,
            "original_fish_position_time_series_exported":False}


def record_result(study,files,source_metadata):
    if not files or any("correlations" not in x for x in files):
        raise SourceStop("CORR_NO_ORIGINAL_FILE_SCORES")
    means={label:float(np.mean([row["correlations"][label] for row in files]))
           for label in (f"age_{age:g}s" for age in AGES)}
    return {"status":"V27_ORIGINAL_SCHOOL_MEAN_VELOCITY_CORRELATION_SCORED",
       "study":study,"records":files,"n_original_files":len(files),
       "equal_file_mean_correlation":means,
       "source":source_metadata,
       "original_fish_XY_redistributed":False,
       "new_fish_future_velocity_fit":False,
       "distinct_school_IDs_verified":False,
       "claim_ceiling":"within-source group-velocity persistence, not causal fish social transfer or acoustic feedback"}


def save(path,obj):
    target=Path(path)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
