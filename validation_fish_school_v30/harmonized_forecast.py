"""v30 exact-source common-200ms original fish movement heldout forecast.

Source-specific original datasets; identical 14D focal/current geometry, 200ms
own and other-fish velocity windows, 200ms/600-800ms future velocity targets
and recording-file holdouts in all 3 taxa. No acoustic/casual social claim.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

SPEED_SECONDS = 0.2
AGES_SECONDS = (0., 0.2, 0.4, 1., 2.)
SOURCE_FPS = (25, 30, 50)
RIDGE_ALPHA = 10.
MODEL_NAMES = ("G_geometry",) + tuple(f"age_{a:g}s" for a in AGES_SECONDS)
HORIZONS = ("short", "delayed")
FEAT_DIM = 14


class SourceStop(Exception):
    pass


def build_original_recording(frame, pos, fps, original_file_name="SOURCE"):
    """One recording; no resampling/interpolation; original native time cohort.

    Future target frames are used only for shared admission/response Y.
    All age-dependent predictor frames are <= current source frame.
    Original coordinate units differ by study and are NOT pooled.
    """
    a = np.asarray(pos, dtype=np.float64)
    f = np.asarray(frame, dtype=np.float64)
    if fps not in SOURCE_FPS or a.ndim != 3 or a.shape[-1] != 2 or a.shape[1] not in (8,10):
        raise SourceStop("V30_ORIGINAL_FISH_COORDINATE_AND_FPS_SCHEMA_STOP")
    if a.shape[0] != len(f) or len(f) < 4000 or not np.isfinite(f).all() or not np.all(np.diff(f)>0):
        raise SourceStop("V30_ORIGINAL_FRAMES_OR_ROW_COUNT_STOP")
    if not np.allclose(f,np.round(f),atol=1e-8,rtol=0):
        raise SourceStop("V30_ORIGINAL_FRAME_NON_INTEGER_STOP")
    s = int(round(fps * SPEED_SECONDS))
    if abs(s / fps - SPEED_SECONDS) > 1e-12:
        raise SourceStop("V30_NATIVE_SPEED_WINDOW_NOT_EXACT_200MS")
    ages = [int(round(t * fps)) for t in AGES_SECONDS]
    if any(abs(i/fps-t)>1e-12 for i,t in zip(ages,AGES_SECONDS)):
        raise SourceStop("V30_AGED_GROUP_TIME_NOT_IN_NATIVE_SOURCE")
    if ages != [0,s,2*s,5*s,10*s]:
        raise SourceStop("V30_FROZEN_AGE_GRID_DRIFT")
    offsets = np.array([-11*s,-10*s,-6*s,-5*s,-3*s,-2*s,-s,0,s,3*s,4*s],dtype=int)
    candidates = np.arange(11*s,len(f)-4*s,s,dtype=int)
    if len(candidates)<500:
        raise SourceStop("V30_INSUFFICIENT_ORIGINAL_2_2SECOND_HISTORY")
    required = candidates[:,None] + offsets[None,:]
    # All eight/ten source fish available at every required predictor/response
    # original timestamp, identical heldout row set for all six panels.
    clean = np.isfinite(a[required]).all(axis=(1,2,3))
    chronological = ((f[required]-f[candidates,None])==offsets[None,:]).all(axis=1)
    eligible = candidates[clean & chronological]
    if len(eligible)<300:
        raise SourceStop("V30_ORIGINAL_SOURCE_COMPLETE_COHORT_TOO_FEW")
    nfish=a.shape[1]
    at=a[eligible]
    vel=(at-a[eligible-s])/SPEED_SECONDS
    prev=(a[eligible-s]-a[eligible-2*s])/SPEED_SECONDS
    speed=np.linalg.norm(vel,axis=-1,keepdims=True)
    centroid=at.mean(axis=1,keepdims=True)-at
    offset=at[:,None,:,:]-at[:,:,None,:] # j-i for focal i
    distances2=np.sum(offset**2,axis=-1)
    ids=np.arange(nfish)
    distances2[:,ids,ids]=np.inf
    nearest=np.argsort(distances2,axis=2)[:,:,:3]
    three_pos=np.take_along_axis(offset,nearest[:,:,:,None],axis=2).mean(axis=2)
    three_dist=np.sqrt(np.take_along_axis(distances2,nearest,axis=2)).mean(axis=2)
    G=np.concatenate((at,vel,prev,vel-prev,speed,centroid,three_pos,
                      three_dist[:,:,None]),axis=-1)
    if G.shape[-1]!=FEAT_DIM:
        raise SourceStop("V30_COMMON_SOURCE_G_FEATURE_DIM_STOP")
    X={"G_geometry":G.reshape(-1,FEAT_DIM)}
    for age,lag in zip(AGES_SECONDS,ages):
        vother=(a[eligible-lag]-a[eligible-lag-s])/SPEED_SECONDS
        # Exclude focal fish from other mean, subtract CURRENT focal velocity.
        rel=((vother.sum(axis=1,keepdims=True)-vother)/(nfish-1))-vel
        z=np.concatenate((G,rel),axis=-1)
        key=f"age_{age:g}s"
        X[key]=z.reshape(-1,FEAT_DIM+2)
        if not np.array_equal(X[key][:,:FEAT_DIM],X["G_geometry"]):
            raise SourceStop("V30_FOCAL_GEOMETRY_CHANGED_ACROSS_GROUP_AGE")
    Yshort=((a[eligible+s]-at)/SPEED_SECONDS).reshape(-1,2)
    Ydelayed=((a[eligible+4*s]-a[eligible+3*s])/SPEED_SECONDS).reshape(-1,2)
    Y=np.concatenate((Yshort,Ydelayed),axis=1)
    if set(X)!=set(MODEL_NAMES):
        raise SourceStop("V30_MODEL_KEY_DRIFT_" + "_".join(sorted(X)))
    for key,values in X.items():
        if not np.isfinite(values).all():
            raise SourceStop("V30_NONFINITE_PREDICTOR_" + key)
    if not np.isfinite(Y).all():
        raise SourceStop("V30_NONFINITE_FUTURE_TARGET_AFTER_FIXED_SOURCE_COHORT")
    if not all(len(v)==len(Y) for v in X.values()):
        raise SourceStop("V30_SHARED_TARGET_SUPPORT_MISMATCH")
    return {
      "X":X,"Y":Y,"source_file":original_file_name,
      "n_source_rows":len(f),"n_original_candidate_group_times":len(candidates),
      "n_original_eligible_group_times":len(eligible),
      "n_original_eligible_fish_frames":len(Y),
      "n_original_rows_excluded_nonfinite_or_noncontiguous":int(len(candidates)-len(eligible)),
      "original_fps":fps,"original_fish_per_recording":nfish,
      "source_speed_difference_frames":s,
      "source_age_frames":ages,
      "source_future_short_end_frames":s,
      "source_future_delayed_start_end_frames":[3*s,4*s],
      "original_animal_XY_or_timestamp_values_exported":False
    }


def predict_train_file_only(train_X,train_Y,heldout_X):
    scaler=StandardScaler().fit(train_X)
    model=Ridge(alpha=RIDGE_ALPHA).fit(scaler.transform(train_X),train_Y)
    return model.predict(scaler.transform(heldout_X))


def evaluate_source_files(recordings,study,minimum_files,source_descriptor):
    names=list(recordings)
    if len(names)!=minimum_files or len(set(names))!=minimum_files:
        raise SourceStop("V30_SOURCE_STUDY_WRONG_FIXED_RECORDING_COUNT")
    if study not in ("tetra","ayu","stickleback"):
        raise SourceStop("V30_UNRECOGNIZED_THIRD_STUDY")
    if any(set(d["X"])!=set(MODEL_NAMES) for d in recordings.values()):
        raise SourceStop("V30_NON_FROZEN_MODEL_GRID")
    results=[]
    for held in names:
        other=[x for x in names if x!=held]
        record=recordings[held]
        out={"heldout_source_file":held,
             "n_source_test_group_times":record["n_original_eligible_group_times"],
             "n_source_test_fish_frames":record["n_original_eligible_fish_frames"],
             "MSE":{}}
        ytest=record["Y"]
        for model in MODEL_NAMES:
            train_x=np.concatenate([recordings[k]["X"][model] for k in other])
            train_y=np.concatenate([recordings[k]["Y"] for k in other])
            predicted=predict_train_file_only(train_x,train_y,record["X"][model])
            if predicted.shape != ytest.shape:
                raise SourceStop("V30_FUTURE_HORIZON_VECTOR_DIMENSIONS_WRONG")
            out["MSE"][model]={
                "short":float(np.mean((predicted[:,:2]-ytest[:,:2])**2)),
                "delayed":float(np.mean((predicted[:,2:]-ytest[:,2:])**2))
            }
        if not all(np.isfinite([out["MSE"][k][h] for k in MODEL_NAMES for h in HORIZONS])):
            raise SourceStop("V30_PREDICTION_NONFINITE")
        results.append(out)
    grouped={}
    for horizon in HORIZONS:
        source_means={model:float(np.mean([r["MSE"][model][horizon] for r in results]))
                      for model in MODEL_NAMES}
        base=source_means["G_geometry"]
        present=source_means["age_0s"]
        denom=base-present
        I={model:(float((base-source_means[model])/denom) if denom>0 else None)
           for model in MODEL_NAMES if model!="G_geometry"}
        contrasts={}
        for age in AGES_SECONDS[1:]:
            label=f"age_{age:g}s"
            per=[r["MSE"][label][horizon]-r["MSE"]["age_0s"][horizon] for r in results]
            contrasts[label]={
                "equal_source_file_mean_delta_MSE_aged_minus_current":float(np.mean(per)),
                "per_heldout_file_delta_MSE_aged_minus_current":per,
                "positive_files":sum(v>0 for v in per),
                "negative_files":sum(v<0 for v in per),
                "exact_zero_files":sum(v==0 for v in per)
            }
        first=None
        for age in AGES_SECONDS[1:]:
            q=I[f"age_{age:g}s"]
            if q is not None and q<=0.5:
                first=age;break
        grouped[horizon]={
            "equal_original_file_mean_MSE":source_means,
            "incremental_predictive_retention_not_information_transfer":I,
            "mean_current_group_gain_MSE_beyond_focal_geometry":float(denom),
            "first_sampled_age_with_at_most_half_retention_s":first,
            "current_vs_age_file_contrasts":contrasts,
            "normalized_retention_defined":bool(denom>0)
        }
    return {
        "status":"V30_ORIGINAL_THREE_SOURCE_COMMON_MODEL_RECORDING_HELDOUT_SCORED",
        "study":study,"original_source_study":source_descriptor,
        "n_original_files":len(names),
        "fish_per_original_file":recordings[names[0]]["original_fish_per_recording"],
        "native_fps":recordings[names[0]]["original_fps"],
        "physical_source_speed_window_s":SPEED_SECONDS,
        "same_source_model_geometry_dim":FEAT_DIM,
        "same_source_age_grid_s":list(AGES_SECONDS),
        "same_source_outcome_horizons_seconds":{"short":[0.,.2],"delayed":[.6,.8]},
        "standardization_train_files_only":True,"fixed_ridge_alpha":RIDGE_ALPHA,
        "source_file_holdout_not_confirmed_distinct_biological_shoal":True,
        "source_original_individual_XY_redistributed":False,
        "observed_fish_calls":False,"social_causal_effect_identified":False,
        "original_source_cohort":{"files":[{
            "name":name,
            "n_source_rows":recordings[name]["n_source_rows"],
            "n_candidate_group_times":recordings[name]["n_original_candidate_group_times"],
            "n_eligible_group_times":recordings[name]["n_original_eligible_group_times"],
            "n_eligible_fish_frames":recordings[name]["n_original_eligible_fish_frames"],
            "n_removed_source_times":recordings[name]["n_original_rows_excluded_nonfinite_or_noncontiguous"],
            } for name in names]},
        "results_by_horizon":grouped,
        "source_file_heldout_results":results,
        "claim_ceiling":"same physical 200ms predictor and 200ms/600-800ms source-conditional future-velocity forecast; not schooling social causality, memory or fish chorus"
    }


def save(path,data):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf8")
