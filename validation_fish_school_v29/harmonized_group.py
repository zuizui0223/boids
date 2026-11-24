"""v29: same 200ms physical velocity differencing for all three fish sources.

Original source XY (no new smoothing) and v27 cohort, no future fish forecast.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

LAGS_SECONDS=(.2,1.,2.)
SPEED_WINDOW_SECONDS=.2

class SourceStop(Exception):pass


def harmonized_group_correlation(pos,times,fps):
    x=np.asarray(pos,dtype=float)
    t=np.asarray(times,dtype=np.int64)
    if fps not in (25.,30.,50.):
        raise SourceStop("V29_SOURCE_NATIVE_FPS_STOP")
    speed=int(round(fps*SPEED_WINDOW_SECONDS))
    if abs(speed/fps-SPEED_WINDOW_SECONDS)>1e-12:
        raise SourceStop("V29_COMMON_200MS_TIME_IS_NOT_INTEGER_FRAMES")
    lagframes=[int(round(l*fps)) for l in LAGS_SECONDS]
    if any(abs(k/fps-l)>1e-12 for k,l in zip(lagframes,LAGS_SECONDS)):
        raise SourceStop("V29_NONINTEGER_LAG_FRAME_STOP")
    if x.ndim!=3 or x.shape[-1]!=2 or x.shape[1]<3 or t.ndim!=1 or len(t)<200:
        raise SourceStop("V29_ORIGINAL_SOURCE_OR_COHORT_SHAPE_STOP")
    if not np.all(np.diff(t)>0) or t[0]-lagframes[-1]-speed<0 or t[-1]>=len(x):
        raise SourceStop("V29_ORIGINAL_TIME_SUPPORT_STOP")
    current=((x[t]-x[t-speed])/SPEED_WINDOW_SECONDS).mean(axis=1)
    if not np.isfinite(current).all():
        raise SourceStop("V29_ORIGINAL_CURRENT_VECTOR_MISSING")
    current=current-current.mean(axis=0)
    norm0=float(np.linalg.norm(current))
    if norm0<1e-10:raise SourceStop("V29_GROUP_SOURCE_CONSTANT_VELOCITY")
    out={}
    for lag,step in zip(LAGS_SECONDS,lagframes):
        stale=((x[t-step]-x[t-step-speed])/SPEED_WINDOW_SECONDS).mean(axis=1)
        if not np.isfinite(stale).all():
            raise SourceStop("V29_ORIGINAL_STALE_VECTOR_MISSING")
        stale=stale-stale.mean(axis=0)
        norm=float(np.linalg.norm(stale))
        if norm<1e-10:raise SourceStop("V29_GROUP_SOURCE_NO_STALE_VARIATION")
        c=float((current*stale).sum()/(norm0*norm))
        if not np.isfinite(c) or abs(c)>1+1e-10:
            raise SourceStop("V29_ORIGINAL_NUMERIC_NORMALIZED_CORRELATION_STOP")
        out[f"age_{lag:g}s"]=c
    return {"correlations":out,
            "n_original_source_group_frames":len(t),
            "speed_window_seconds":SPEED_WINDOW_SECONDS,
            "speed_window_native_frames":speed,
            "native_source_fps":fps,
            "original_XY_or_future_target_redistributed":False}


def aggregate(study,rows,expected,source):
    if len(rows)!=expected:
        raise SourceStop("V29_ORIGINAL_SOURCE_RECORDING_COUNT_STOP")
    means={f"age_{lag:g}s":float(np.mean([r["correlations"][f"age_{lag:g}s"] for r in rows]))
           for lag in LAGS_SECONDS}
    return {
      "status":"V29_ORIGINAL_HARMONIZED_200MS_SCHOOL_VELOCITY_CORRELATION",
      "study":study,"source_metadata":source,
      "n_original_files":len(rows),"source_results":rows,
      "equal_original_file_mean_C":means,
      "velocity_frame_time_seconds":SPEED_WINDOW_SECONDS,
      "original_fish_future_velocity_model_refitted":False,
      "source_individual_XY_series_redistributed":False,
      "original_school_IDs_independent_not_verified":True,
      "claim_ceiling":"source-normalized group-motion persistence, not social/cognitive or fish acoustic effect"
    }


def save(path,x):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
