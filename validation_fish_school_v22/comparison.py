"""v22: fixed retrospective paired global-vs-stale information test.

Source numerical outcomes from Puy (tetra) and Niizato (ayu) are not pooled.
SYNCHRONIZED CALLING NOT OBSERVED. No causal-force attribution.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"validation_fish_school_v5"))
from forecast_transfer import fit_ridge, SourceStop

SEED = 20261124
MODELS = ("geometry","current","stale2s","magnitude")
HORIZONS = ("short","delayed")
BOOTSTRAP = 5000


def relative_other_mean(other_source_velocity: np.ndarray,
                        focal_current_velocity: np.ndarray) -> np.ndarray:
    """Return (mean other v at source time) - CURRENT focal v, for each fish.

    Both arrays are [K,N,2]; source time may be current or t-2s.
    The focal's own current velocity is never substituted by past focal state.
    """
    a = np.asarray(other_source_velocity, dtype=np.float64)
    b = np.asarray(focal_current_velocity, dtype=np.float64)
    if a.shape != b.shape or a.ndim != 3 or a.shape[-1] != 2 or a.shape[1] < 3:
        raise SourceStop("GLOBAL_RELATIVE_VELOCITY_SCHEMA_STOP")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise SourceStop("NONFINITE_VELOCITY_STOP")
    n = a.shape[1]
    other = (a.sum(axis=1, keepdims=True) - a)/(n-1)
    return other - b


def locked_panels(geometry, locked_current, calculated_current, stale):
    """Source-independent no-retune construction and exact current replay gate."""
    g = np.asarray(geometry, dtype=np.float64)
    x = np.asarray(locked_current, dtype=np.float64)
    current = np.asarray(calculated_current, dtype=np.float64).reshape(-1,2)
    lag = np.asarray(stale, dtype=np.float64).reshape(-1,2)
    if g.ndim != 2 or x.shape != (len(g), g.shape[1]+2) or lag.shape != current.shape or len(g)!=len(current):
        raise SourceStop("V22_PANEL_DIMENSION_STOP")
    if not np.allclose(x[:,:g.shape[1]], g, rtol=0, atol=1e-10):
        raise SourceStop("ORIGINAL_GEOMETRY_COLUMNS_REPLAY_STOP")
    if not np.allclose(x[:,-2:], current, rtol=0, atol=1e-8):
        raise SourceStop("ORIGINAL_GLOBAL_VELOCITY_REPLAY_STOP")
    z = {"geometry": g, "current": x,
         "stale2s": np.concatenate((g,lag),axis=1),
         "magnitude": np.concatenate((g,np.linalg.norm(current,axis=1,keepdims=True)),axis=1)}
    if not all(np.isfinite(v).all() for v in z.values()):
        raise SourceStop("NONFINITE_FEATURES_STOP")
    return z


def make_source_panels(horizons, targets, source, checks):
    """Validate equal-horizon targets and model rows without copying animals."""
    for h in HORIZONS:
        if h not in horizons or h not in targets:
            raise SourceStop("MISSING_HORIZON_STOP")
        panel, y = horizons[h],np.asarray(targets[h],dtype=np.float64)
        if set(panel)!=set(MODELS) or y.ndim!=2 or y.shape[1]!=2:
            raise SourceStop("INVALID_V22_SOURCE_SCHEMA_STOP")
        if not all(np.asarray(x).ndim==2 and len(x)==len(y) for x in panel.values()):
            raise SourceStop("HORIZON_TARGET_SUPPORT_STOP")
        if len(y)<1000 or not np.isfinite(y).all():
            raise SourceStop("TARGET_NONFINITE_OR_TOO_FEW_STOP")
    return {"X":horizons,"Y":targets,"source":source,"source_checks":checks}


def paired_bootstrap(values, baseline, seed=SEED, n_reps=BOOTSTRAP):
    """Descriptive resampling of whole recordings, not of autocorrelated frames."""
    x=np.asarray(values,dtype=np.float64)
    y=np.asarray(baseline,dtype=np.float64)
    if x.ndim!=1 or y.shape!=x.shape or len(x)<2 or not (np.isfinite(x).all() and np.isfinite(y).all()):
        raise SourceStop("BOOTSTRAP_RECORDING_SCHEMA_STOP")
    rng=np.random.default_rng(seed)
    draws=np.mean(x[rng.integers(0,len(x),size=(n_reps,len(x)))],axis=1)
    return {
      "equal_recording_mean_delta_MSE":float(x.mean()),
      "relative_gain_vs_equal_recording_stale_MSE":float(x.mean()/y.mean()),
      "positive_recordings":int((x>0).sum()),
      "negative_recordings":int((x<0).sum()),
      "exact_zero_recordings":int((x==0).sum()),
      "recording_differences_MSE":[float(t) for t in x],
      "descriptive_bootstrap_recording_95pct":[float(t) for t in np.quantile(draws,[.025,.975])],
      "bootstrap_unit":"original recording only, may reuse individuals",
    }


def assess(sources, name, expected, anchor=None):
    """Run pre-frozen original complete-recording heldout fixed ridge."""
    ids=sorted(sources)
    if ids != list(range(expected)):
        raise SourceStop("V22_INCORRECT_RECORDING_ID_GATE")
    if any(sources[i].get("source_checks") is None for i in ids):
        raise SourceStop("SOURCE_AUTHENTICATION_MISSING")
    observations=[]
    for held in ids:
        row={"heldout_recording":held,"n_targets":{h:len(sources[held]["Y"][h]) for h in HORIZONS},
             "MSE":{}}
        for horizon in HORIZONS:
            results={}
            y_test=sources[held]["Y"][horizon]
            for model in MODELS:
                training_x=np.concatenate([sources[i]["X"][horizon][model] for i in ids if i!=held])
                training_y=np.concatenate([sources[i]["Y"][horizon] for i in ids if i!=held])
                pred=fit_ridge(training_x, training_y, sources[held]["X"][horizon][model])
                results[model]=float(np.mean((y_test-pred)**2))
            if anchor is not None and horizon=="short":
                if abs(results["current"]-anchor[held]) > 3e-5:
                    raise SourceStop(f"PRIOR_V7_CURRENT_SOURCE_REPLAY_STOP_RECORDING_{held}")
            if not np.isfinite(list(results.values())).all():
                raise SourceStop("NUMERIC_MSE_INVALID_STOP")
            row["MSE"][horizon]=results
        observations.append(row)
    comparisons={}
    for hi,h in enumerate(HORIZONS):
        z={k:np.array([r["MSE"][h][k] for r in observations]) for k in MODELS}
        contrasts={
          "PRIMARY_current_vs_stale2s":(z["stale2s"]-z["current"],z["stale2s"]),
          "SECONDARY_current_vs_geometry":(z["geometry"]-z["current"],z["geometry"]),
          "SECONDARY_current_vector_vs_magnitude":(z["magnitude"]-z["current"],z["magnitude"]),
        }
        info={}
        for j,(key,(delta,base)) in enumerate(contrasts.items()):
            info[key]=paired_bootstrap(delta,base,seed=SEED+100*hi+j)
            info[key]["relative_gain_vs_equal_recording_comparator_MSE"]=info[key].pop(
                "relative_gain_vs_equal_recording_stale_MSE")
        comparisons[h]={
         "equal_recording_MSE":{k:float(v.mean()) for k,v in z.items()},
         "contrasts":info}
    return {
      "status":"OBSERVED_RETROSPECTIVE_FISH_MOVEMENT_V22_SCORED",
      "study":name,
      "source_count":expected,
      "result_unit":"original file, may not be independent animals or populations",
      "models":list(MODELS),
      "horizons":{"short":"future 0.0–0.2s velocity","delayed":"future 0.5–0.7s velocity"},
      "bootstrap_replicates":BOOTSTRAP,
      "original_source_digest_check":"PASS",
      "original_fish_positions_redistributed":False,
      "original_fish_calling_observed":False,
      "current_source_feature_replay":"PASS",
      "frozen_prior_mse_replay":"PASS" if anchor is not None else "NOT_APPLICABLE_DUE_TO_FROZEN_NEW_2S_COHORT",
      "results":observations,
      "comparisons":comparisons,
      "claim_ceiling":"time-specific collective-state predictive information only; not causal alignment, audio feedback, or fully prospective due to upstream tracking processing",
    }
