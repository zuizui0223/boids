"""v24: fixed age-of-other-fish-state forecast, no change to original v22 outcomes.

This is a retrospective original fish-movement prediction. It does NOT observe
vocalization or identify a social/causal force.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v22"))
from forecast_transfer import fit_ridge,SourceStop
from comparison import relative_other_mean, paired_bootstrap

AGES=(0.,.1,.2,.5,1.,2.)
MODELS=("geometry",)+tuple(f"age_{x:g}s" for x in AGES)
HORIZONS=("short","delayed")
NBOOT=5000
SEED=20261124

ANCHORS={
 "tetra":{
  "short":{"age_0s":11.352981111900112,"age_2s":13.740122954303708},
  "delayed":{"age_0s":54.62586752465776,"age_2s":64.89291742289119}
 },
 "ayu":{
  "short":{"age_0s":6343.970137459749,"age_2s":7061.387488140268},
  "delayed":{"age_0s":25687.490647693074,"age_2s":30463.936132138184}
 }
}


def source_age_panels(base, pos, index, fps, lag_frames, delayed_rows=None):
    """Build G + age-dependent relative OTHER velocity, using v22's exact rows.

    base: v22 tetra_one/ayu_one return. index: one current native frame per
    group-state time; all indices must support 2s previous history. The focal
    current velocity is unchanged for all panels, regardless of stale other.
    """
    arr=np.asarray(pos,dtype=np.float64)
    idx=np.asarray(index,dtype=np.int64)
    if arr.ndim!=3 or arr.shape[2]!=2 or arr.shape[1]<3 or not np.isfinite(arr).all():
        raise SourceStop("V24_INVALID_SOURCE_POSITION_SCHEMA")
    if idx.ndim!=1 or len(idx)<500 or np.any(np.diff(idx)<=0):
        raise SourceStop("V24_UNSORTED_OR_SHORT_SOURCE_INDEX")
    if lag_frames not in (3,5):
        raise SourceStop("V24_VELOCITY_LAG_UNRECOGNIZED")
    if fps not in (30.,50.):
        raise SourceStop("V24_SOURCE_FPS_UNRECOGNIZED")
    steps=[int(round(a*fps)) for a in AGES]
    if any(abs(a*fps-b)>1e-8 for a,b in zip(AGES,steps)):
        raise SourceStop("V24_NONINTEGRAL_SOURCE_LAG")
    if idx.min()<max(steps)+lag_frames or idx.max()>=len(arr):
        raise SourceStop("V24_ORIGINAL_TWO_SECOND_PAST_HISTORY_STOP")
    n=arr.shape[1]
    current=(arr[idx]-arr[idx-lag_frames])/(lag_frames/fps)
    raw_g=base["X"]["short"]["geometry"]
    raw_current=base["X"]["short"]["current"]
    raw_stale=base["X"]["short"]["stale2s"]
    if raw_g.shape[0]!=len(idx)*n or raw_current.shape!=(len(idx)*n,raw_g.shape[1]+2):
        raise SourceStop("V24_V22_ORIGINAL_TARGET_ROWS_STOP")
    X={"geometry":raw_g}
    for age,step in zip(AGES,steps):
        other=(arr[idx-step]-arr[idx-step-lag_frames])/(lag_frames/fps)
        rel=relative_other_mean(other,current).reshape(-1,2)
        name=f"age_{age:g}s"
        panel=np.concatenate((raw_g,rel),axis=1)
        if age==0.:
            if not np.allclose(panel,raw_current,rtol=0,atol=1e-8):
                raise SourceStop("V24_V22_ORIGINAL_CURRENT_GLOBAL_REPLAY_STOP")
            panel=raw_current
        elif age==2.:
            if not np.allclose(panel,raw_stale,rtol=0,atol=1e-8):
                raise SourceStop("V24_V22_ORIGINAL_TWO_SECOND_GLOBAL_REPLAY_STOP")
            panel=raw_stale
        X[name]=panel
    if set(X)!=set(MODELS):
        raise SourceStop("V24_MODEL_GRID_INCORRECT")
    if not all(x.shape[0]==len(base["Y"]["short"]) for x in X.values()):
        raise SourceStop("V24_CURRENT_TARGET_MISMATCH")
    if delayed_rows is None:
        rows=np.arange(len(idx)*n)
    else:
        rows=np.asarray(delayed_rows,dtype=np.int64)
        if rows.ndim!=1 or len(rows)<1000 or rows.min()<0 or rows.max()>=len(idx)*n:
            raise SourceStop("V24_DELAYED_MASK_INVALID")
    delayed={k:v[rows] for k,v in X.items()}
    for key in ("geometry","age_0s","age_2s"):
        old_key={"geometry":"geometry","age_0s":"current","age_2s":"stale2s"}[key]
        if not np.allclose(delayed[key],base["X"]["delayed"][old_key],rtol=0,atol=1e-8):
            raise SourceStop("V24_V22_ORIGINAL_DELAYED_COHORT_REPLAY_STOP")
    if not all(len(delayed[k])==len(base["Y"]["delayed"]) for k in MODELS):
        raise SourceStop("V24_UNMATCHED_DELAYED_Y")
    return {
      "X":{"short":X,"delayed":delayed},
      "Y":base["Y"],
      "source_metadata":base["source"],
      "source_checks":base["source_checks"],
      "n_observation_short":len(base["Y"]["short"]),
      "n_observation_delayed":len(base["Y"]["delayed"]),
      "ages_seconds":list(AGES),
      "past_source_frame_lags":steps,
      "fps_original":fps,
      "no_raw_fish_track_output":True,
    }


def assess(sources, study):
    if study not in ANCHORS:raise SourceStop("V24_SOURCE_STUDY_UNKNOWN")
    target_n={"tetra":6,"ayu":7}[study]
    ids=sorted(sources)
    if ids != list(range(target_n)):
        raise SourceStop("V24_ORIGINAL_RECORDING_COUNT_STOP")
    for src in sources.values():
        if (set(src["X"])!=set(HORIZONS) or
            any(set(src["X"][h])!=set(MODELS) for h in HORIZONS) or
            src["source_checks"].get("no_future_trajectory_inputs") is False):
            raise SourceStop("V24_SOURCE_MODEL_PANEL_INTEGRITY_STOP")

    output=[]
    for held in ids:
        item={"heldout_recording":held,
              "source_short_original_targets":sources[held]["n_observation_short"],
              "source_delayed_original_targets":sources[held]["n_observation_delayed"],
              "MSE":{}}
        for h in HORIZONS:
            y=sources[held]["Y"][h]
            models={}
            for model in MODELS:
                train_x=np.concatenate([sources[i]["X"][h][model] for i in ids if i!=held])
                train_y=np.concatenate([sources[i]["Y"][h] for i in ids if i!=held])
                pred=fit_ridge(train_x,train_y,sources[held]["X"][h][model])
                models[model]=float(np.mean((pred-y)**2))
            if not np.isfinite(list(models.values())).all():
                raise SourceStop("V24_NONFINITE_MSE")
            item["MSE"][h]=models
        output.append(item)

    groups={}
    for j,h in enumerate(HORIZONS):
        model_means={m:float(np.mean([t["MSE"][h][m] for t in output])) for m in MODELS}
        # Previously published original v22 means, never rescue a mismatch.
        for model,expected in ANCHORS[study][h].items():
            if abs(model_means[model]-expected)>0.001:
                raise SourceStop("V24_V22_PRIOR_SCORES_REPLAY_STOP_"+study+"_"+h+"_"+model)
        denom=model_means["geometry"]-model_means["age_0s"]
        if denom<=0: retention={m:None for m in MODELS if m!="geometry"}
        else:retention={m:float((model_means["geometry"]-model_means[m])/denom)
                         for m in MODELS if m!="geometry"}
        first_crossing=None
        for age in AGES[1:]:
            label=f"age_{age:g}s"
            if retention[label] is not None and retention[label] <= .5:
                first_crossing=age
                break
        monotone=all(model_means[f"age_{a:g}s"]<=model_means[f"age_{b:g}s"]
                     for a,b in zip(AGES[:-1],AGES[1:]))
        contrasts={}
        for k,age in enumerate(AGES[1:]):
            m=f"age_{age:g}s"
            per=np.array([r["MSE"][h][m]-r["MSE"][h]["age_0s"] for r in output])
            baseline=np.array([r["MSE"][h][m] for r in output])
            contrasts[m]=paired_bootstrap(per,baseline,seed=SEED+100*j+k)
        groups[h]={
          "equal_recording_MSE":model_means,
          "relative_information_retention_vs_geometry":retention,
          "first_observed_lag_at_or_below_half_retention_seconds":first_crossing,
          "MSE_by_age_monotonic_nondecreasing":bool(monotone),
          "per_recording_age_minus_present_contrasts":contrasts,
          "replayed_v22_original_MSE_current_and_2s":"PASS",
        }
    return {
      "status":"V24_ORIGINAL_RETROSPECTIVE_FISH_AGE_CURVE_SCORED",
      "study":study,"n_original_recording_files":len(ids),
      "original_study_and_native_source":"Puy et al. PNAS 2024" if study=="tetra" else "Niizato et al. Scientific Reports 2024",
      "all_original_sources_authenticated":True,
      "frozen_protocol_before_effects":"docs/V24_COLLECTIVE_STATE_AGE_DECAY_FREEZE.md",
      "years_or_original_fish_independent_population_replication":"NOT_ESTABLISHED",
      "raw_fish_positions_redistributed":False,
      "observed_fish_vocalization":"NOT_AVAILABLE",
      "source_smoothing_teleological_prediction_risk":"UNRESOLVED",
      "results_by_horizon":groups,
      "per_recording_scores":output,
      "scientific_claim_ceiling":"retrospective conditional temporal specificity of shared motion, not causal fish interactions, motor coordination timescale or fish chorus",
    }


def save_result(path,result):
    p=Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
