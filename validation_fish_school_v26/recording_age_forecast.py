"""v26d original EIDC stickleback exploratory recording-heldout age-of-schooling forecast.

Original 3 numbered files were selected before any v26d outcomes. Their
unknown school IDs prohibit a claim of independent school or fish-population
replication. No vocalizations, treatment effects or causal forces are inferred.
"""
from __future__ import annotations
import io
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from validation_fish_school_v26.eidc_source_only import BASE,FILE_LIMIT,fetch_bound,SourceStop
from validation_fish_school_v26.source_semantics import PINS

SOURCE_IDS=("01.txt","02.txt","105.txt")
COLUMN_NAMES=[v for fish in range(1,9) for v in (f"x.{fish}",f"x.{fish+8}")]+["frame"]
AGES=(0.,.2,.4,1.,2.)
FRAME_LAGS=(0,5,10,25,50)
FPS=25.
VELOCITY_FRAMES=5
RIDGE_ALPHA=10.
HORIZONS=("short","delayed")
BASE_MODEL="G_geometry"


def read_source(blob):
    try:
        original=pd.read_csv(io.BytesIO(blob),sep=r"\s+",na_values=["NA"])
    except Exception as exc:
        raise SourceStop("EIDC_ORIGINAL_PANDAS_TABLE_STOP") from exc
    if list(original.columns)!=COLUMN_NAMES or len(original)<3000:
        raise SourceStop("EIDC_ORIGINAL_17COL_HEADER_OR_ROWS_STOP")
    raw=original.to_numpy(dtype=float)
    frame=raw[:,-1]
    if not np.isfinite(frame).all() or not np.array_equal(np.diff(frame),np.ones(len(frame)-1)):
        raise SourceStop("EIDC_ORIGINAL_LAST_COLUMN_NATIVE_FRAME_CLOCK_STOP")
    if not np.allclose(frame,np.rint(frame),atol=1e-9,rtol=0):
        raise SourceStop("EIDC_SOURCE_NONINTEGER_FRAME")
    pos=raw[:,:16].reshape(-1,8,2)
    if np.isinf(pos).any():
        raise SourceStop("EIDC_INFINITY_NOT_MISSING_VALUE_STOP")
    return frame,pos


def build(pos):
    if pos.ndim!=3 or pos.shape[1:]!=(8,2) or len(pos)<3000:
        raise SourceStop("FISH_8_XY_SOURCE_SHAPE_STOP")
    i=np.arange(55,len(pos)-21,5,dtype=int)
    offsets=np.array([-55,-50,-30,-25,-15,-10,-5,0,5,15,20],dtype=int)
    reads=i[:,None]+offsets[None,:]
    valid=np.isfinite(pos[reads]).all(axis=(1,2,3))
    i=i[valid]
    if len(i)<200:raise SourceStop("FISH_TOO_FEW_COMPLETE_SOURCE_FRAMES_STOP")
    now=pos[i]
    vel=(pos[i]-pos[i-5])/(5/FPS)
    older=(pos[i-5]-pos[i-10])/(5/FPS)
    avg=now.mean(axis=1,keepdims=True)
    diff=now[:,None,:,:]-now[:,:,None,:]
    d2=(diff**2).sum(axis=-1)
    d2[:,np.arange(8),np.arange(8)]=np.inf
    neighbors=np.argsort(d2,axis=2)[:,:,:3]
    local_pos=np.take_along_axis(diff,neighbors[:,:,:,None],axis=2).mean(axis=2)
    local_dist=np.sqrt(np.take_along_axis(d2,neighbors,axis=2)).mean(axis=2)
    speed=np.linalg.norm(vel,axis=2,keepdims=True)
    geom=np.concatenate((now,vel,older,vel-older,speed,avg-now,
                         local_pos,local_dist[:,:,None]),axis=2)
    panels={"G_geometry":geom.reshape(-1,geom.shape[2])}
    for age,delay in zip(AGES,FRAME_LAGS):
        vs=(pos[i-delay]-pos[i-delay-5])/(5/FPS)
        global_other=(vs.sum(axis=1,keepdims=True)-vs)/7-vel
        extra=np.concatenate((geom,global_other),axis=2)
        panels[f"age_{age:g}s"]=extra.reshape(-1,extra.shape[2])
    y={
        "short":((pos[i+5]-pos[i])/(5/FPS)).reshape(-1,2),
        "delayed":((pos[i+20]-pos[i+15])/(5/FPS)).reshape(-1,2)
    }
    if not all(np.isfinite(x).all() for x in [*panels.values(),*y.values()]):
        raise SourceStop("FISH_NONFINITE_CONSTRUCTED_PREDICTOR_OR_TARGET_STOP")
    return {"X":panels,"Y":y,"n_complete_source_frames":len(i),
            "n_fish_frames":len(i)*8,
            "n_native_source_rows":len(pos),
            "n_tracking_rows_missing_any_XY":int((~np.isfinite(pos).all(axis=(1,2))).sum()),
            "all_models_same_target_cohort":True}


def fit_ridge(X,Y,X_test):
    scaler=StandardScaler().fit(X)
    fitted=Ridge(alpha=RIDGE_ALPHA).fit(scaler.transform(X),Y)
    return fitted.predict(scaler.transform(X_test))


def assess(sources):
    if sorted(sources)!=list(SOURCE_IDS):
        raise SourceStop("EXACT_THREE_FROZEN_SOURCE_FILES_REQUIRED")
    models=(BASE_MODEL,)+tuple(f"age_{x:g}s" for x in AGES)
    results=[]
    for held in SOURCE_IDS:
        row={"heldout_recording_file":held,
             "n_original_test_fish_frame_targets":sources[held]["n_fish_frames"],
             "n_original_source_complete_frames":sources[held]["n_complete_source_frames"],
             "MSE":{}}
        for horizon in HORIZONS:
            scores={}
            for model in models:
                trainX=np.concatenate([sources[f]["X"][model] for f in SOURCE_IDS if f!=held])
                trainY=np.concatenate([sources[f]["Y"][horizon] for f in SOURCE_IDS if f!=held])
                pred=fit_ridge(trainX,trainY,sources[held]["X"][model])
                scores[model]=float(np.mean((pred-sources[held]["Y"][horizon])**2))
            row["MSE"][horizon]=scores
        results.append(row)
    analysis={}
    for horizon in HORIZONS:
        means={model:float(np.mean([z["MSE"][horizon][model] for z in results])) for model in models}
        denom=means[BASE_MODEL]-means["age_0s"]
        retention={m:(float((means[BASE_MODEL]-means[m])/denom) if denom>0 else None)
                for m in models if m!=BASE_MODEL}
        comparisons={}
        for age in AGES[1:]:
            key=f"age_{age:g}s"
            diffs=[r["MSE"][horizon][key]-r["MSE"][horizon]["age_0s"] for r in results]
            comparisons[key]={"equal_recording_mean_MSE_difference":float(np.mean(diffs)),
                              "recording_level_difference":diffs,
                              "positive_files":int(sum(x>0 for x in diffs)),
                              "negative_files":int(sum(x<0 for x in diffs)),
                              "zero_files":int(sum(x==0 for x in diffs))}
        analysis[horizon]={"equal_recording_MSE":means,
             "normalized_incremental_predictive_retention_not_mutual_information":retention,
             "comparison_current_vs_aged":comparisons,
             "baseline_geometry_positive_gain":bool(denom>0)}
    return {"status":"ORIGINAL_STICKLEBACK_RECORDING_HELDOUT_EXPLORATORY_SCORE",
         "source":"MacGregor & Ioannou 2021 original EIDC stickleback DOI 10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
         "species":"Gasterosteus aculeatus",
         "n_original_source_files":3,"n_unique_shoals_known":None,
         "test_unit":"RECORDING_FILE_NOT_VERIFIED_DISTINCT_SCHOOL",
         "source_fps":FPS,"native_mse_units":"original pixels-per-second squared",
         "original_source_released_under":"Open Government Licence v3",
         "frozen_pre_result_spec":"docs/V26D_STICKLEBACK_3_RECORDING_FORECAST_FREEZE.md",
         "source_original_sha256":{name:PINS[name][0] for name in SOURCE_IDS},
         "study_shoal_mapping":"UNKNOWN",
         "fish_chorus_measured":False,"causal_fish_interaction_inferred":False,
         "individual_original_positions_redistributed":False,
         "source_files":[{"name":name,
            "n_source_rows":sources[name]["n_native_source_rows"],
            "n_complete_frame_targets":sources[name]["n_complete_source_frames"],
            "n_tracking_rows_missing":sources[name]["n_tracking_rows_missing_any_XY"]} for name in SOURCE_IDS],
         "results_by_horizon":analysis,
         "per_file_scores":results}


def run():
    cases={}
    for name in SOURCE_IDS:
        original=fetch_bound(BASE+name,FILE_LIMIT)
        expected_sha,expected_size=PINS[name]
        if len(original)!=expected_size or hashlib.sha256(original).hexdigest()!=expected_sha:
            raise SourceStop("V26D_ORIGINAL_BYTE_SOURCE_DRIFT_"+name)
        frame,pos=read_source(original)
        cases[name]=build(pos)
    return assess(cases)


def main():
    target=Path("validation_fish_school_v26/results/three_original_recording_forecast.json")
    try:result=run()
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as exc:
        result={"status":"SOURCE_OR_RECORDING_SUPPORT_STOP","reason":str(exc),
                "third_fish_species_predictive_result":None}
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"status":result["status"],"reason":result.get("reason"),
                     "results_by_horizon":result.get("results_by_horizon"),
                     "n_complete_frames":[z["n_complete_frame_targets"] for z in result.get("source_files",[])]},sort_keys=True))


if __name__=="__main__":main()
