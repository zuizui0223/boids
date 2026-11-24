"""v5d field fish-school heldout-trial forecast: preregistered before source numerical outcomes.
Source Puy et al 2024, Zenodo 10890112. No vocalization or fish-Boids causality claimed.
Each test trial entirely absent from all training, scaling and coefficient fitting.
"""
from __future__ import annotations
import json,math,tempfile
from pathlib import Path
from urllib import error
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from source_inventory import read_json,ZENODO
from trajectory_source_gate import RECORDINGS,download_and_audit,SourceStop

FPS=50.;PX_PER_100CM=2745.;DT_FUTURE=10;STRIDE=10
SPEED_DIFF_LAG=5;GHOST_LAG=100
PERCEPTION_CM=25.;SEPARATION_CM=8.;RIDGE_ALPHA=10.
SEED=20261120;N_FISH=8
EXPECTED=["Time [frame]"]+[f"{axis}_{i} [px]" for i in range(8) for axis in ("X","Y")]
MODES=("self","boids","speed_selective","stale_school")
def source_csv(path):
    df=pd.read_csv(path)
    if list(df.columns)!=EXPECTED:raise SourceStop("UNRECOGNIZED_CSV_17COL_SCHEMA")
    if len(df)<3000:raise SourceStop("NOT_ENOUGH_FRAMES")
    values=df.to_numpy(dtype=np.float64)
    frame=values[:,0];pos=values[:,1:].reshape(-1,8,2)*(100./PX_PER_100CM)
    if not np.isfinite(frame).all() or np.unique(frame).size!=len(frame):
        raise SourceStop("MISSING_OR_NONUNIQUE_FRAME_IDS")
    if not np.all(np.diff(frame)>0):raise SourceStop("UNSORTED_FRAME_IDS")
    return frame,pos
def group_vectors(pos,vel):
    # pos/vel [K,8,2]; spatial and time membership known at t
    d=pos[:,None,:,:]-pos[:,:,None,:] # j-i
    n=len(pos);ids=np.arange(8);r2=np.sum(d*d,axis=-1)
    r=np.sqrt(r2);nonself=(ids[None,:,None]!=ids[None,None,:])
    neighborhood=(r<PERCEPTION_CM)&nonself
    avoid=(r<SEPARATION_CM)&nonself
    c=neighborhood.sum(axis=-1);den=np.maximum(c,1)
    sep=-np.sum(np.where(avoid[:,:,:,None],d/np.maximum(r2[:,:,:,None],1e-6),0.),axis=2)
    coh=np.sum(neighborhood[:,:,:,None]*d,axis=2)/den[:,:,None]
    dif=vel[:,None,:,:]-vel[:,:,None,:] # j-i velocity
    align=np.sum(neighborhood[:,:,:,None]*dif,axis=2)/den[:,:,None]
    speed=np.linalg.norm(vel,axis=2)
    faster=neighborhood&(speed[:,None,:]>speed[:,:,None])
    fc=faster.sum(axis=-1)
    fast=np.sum(faster[:,:,:,None]*dif,axis=2)/np.maximum(fc,1)[:,:,None]
    return np.concatenate((sep,align,coh,c[:,:,None]/7.,fast,fc[:,:,None]/7.),axis=-1)
def make_trial(frame,position,trial):
    n=len(frame)
    # full 2-sec history for negative-control plus 0.2-sec test target
    idx=np.arange(GHOST_LAG+2*SPEED_DIFF_LAG,n-DT_FUTURE,STRIDE,dtype=int)
    # strict source frame IDs: t-110,t-105,t-100,t-10,t-5,t,t+10
    picks=np.stack([idx-GHOST_LAG-2*SPEED_DIFF_LAG,
                    idx-GHOST_LAG-SPEED_DIFF_LAG,idx-GHOST_LAG,
                    idx-2*SPEED_DIFF_LAG,idx-SPEED_DIFF_LAG,
                    idx,idx+DT_FUTURE],axis=1)
    valid=np.isfinite(position[picks]).all(axis=(1,2,3))
    valid &= (np.diff(frame[picks],axis=1)==np.diff(
          np.array([-GHOST_LAG-2*SPEED_DIFF_LAG,
                    -GHOST_LAG-SPEED_DIFF_LAG,-GHOST_LAG,
                    -2*SPEED_DIFF_LAG,-SPEED_DIFF_LAG,0,DT_FUTURE]))[None,:]).all(axis=1)
    idx=idx[valid]
    if len(idx)<3000 or len(idx)<.6*len(valid):
        raise SourceStop("SOURCE_TIME_OR_GPS_SUPPORT_STOP trial="+str(trial))
    at=position[idx];prev=position[idx-SPEED_DIFF_LAG];old=position[idx-2*SPEED_DIFF_LAG]
    vel=(at-prev)/(SPEED_DIFF_LAG/FPS)
    older=(prev-old)/(SPEED_DIFF_LAG/FPS)
    pastpos=position[idx-GHOST_LAG]
    pastvel=(pastpos-position[idx-GHOST_LAG-SPEED_DIFF_LAG])/(SPEED_DIFF_LAG/FPS)
    target=(position[idx+DT_FUTURE]-at)/(DT_FUTURE/FPS)
    speed=np.linalg.norm(vel,axis=2)
    # own movement and wall/state: raw 100 cm squared tank.
    wall=np.stack([at[:,:,0],100.-at[:,:,0],at[:,:,1],100.-at[:,:,1]],axis=-1)
    own=np.concatenate((at,vel,older,(vel-older),speed[:,:,None],wall),axis=-1)
    social=group_vectors(at,vel)
    ghost=group_vectors(pastpos,pastvel)
    X0=own.reshape(-1,own.shape[-1])
    X1=np.concatenate([own,social[:,:,:7]],axis=-1).reshape(-1,own.shape[-1]+7)
    X2=np.concatenate([own,social],axis=-1).reshape(-1,own.shape[-1]+social.shape[-1])
    Xghost=np.concatenate([own,ghost[:,:,:7]],axis=-1).reshape(-1,own.shape[-1]+7)
    Y=target.reshape(-1,2)
    if not all(np.isfinite(x).all() for x in (X0,X1,X2,Xghost,Y)):
        raise SourceStop("NONFINITE_MODEL_DATA")
    return {"trial":trial,"source_frames":n,"source_eligible_target_frames":len(idx),
            "observations":len(Y),"X":{"self":X0,"boids":X1,
               "speed_selective":X2,"stale_school":Xghost},"Y":Y}
def fit_ridge(train_x,train_y,test_x):
    scale=StandardScaler().fit(train_x)
    model=Ridge(alpha=RIDGE_ALPHA).fit(scale.transform(train_x),train_y)
    return model.predict(scale.transform(test_x))
def assess(trials):
    names=sorted(trials)
    if len(trials)!=6 or names!=list(range(6)):
        raise SourceStop("SIX_8FISH_TRIALS_REQUIRED")
    results=[]
    for held in names:
        train=[trials[j] for j in names if j!=held];test=trials[held]
        out={"heldout_trial":held,"n_source_frames":test["source_frames"],
             "n_eval_positions":test["observations"],"score_mse":{}}
        for mode in MODES:
            x=np.concatenate([t["X"][mode] for t in train]);y=np.concatenate([t["Y"] for t in train])
            pred=fit_ridge(x,y,test["X"][mode])
            # equally weight both velocity components; no per-fish p values
            out["score_mse"][mode]=float(np.mean((test["Y"]-pred)**2))
        out["gain_M0_to_M1"]=out["score_mse"]["self"]-out["score_mse"]["boids"]
        out["gain_M1_to_M2"]=out["score_mse"]["boids"]-out["score_mse"]["speed_selective"]
        out["gain_ghost_to_current"]=out["score_mse"]["stale_school"]-out["score_mse"]["boids"]
        results.append(out)
    rng=np.random.default_rng(SEED)
    ans={"status":"ORIGINAL_2024_EIGHT_FISH_TRIAL_HELDOUT_EVALUATED",
         "n_source_trials":6,"n_independent_holdout_trials":6,
         "spatial_scale_cm_per_px":100./PX_PER_100CM,
         "fps_published":FPS,"horizon_seconds":DT_FUTURE/FPS,
         "feature_radius_cm":PERCEPTION_CM,"avoidance_radius_cm":SEPARATION_CM,
         "alpha_fixed":RIDGE_ALPHA,"n_bootstrap":5000,
         "test_unit":"recording_trial_not_frame_or_individual",
         "trials":results,"uncertainty":{}}
    for key in ("gain_M0_to_M1","gain_M1_to_M2","gain_ghost_to_current"):
        vals=np.array([x[key] for x in results]);pos=int((vals>0).sum())
        reps=np.mean(vals[rng.integers(0,len(vals),size=(5000,len(vals)))],axis=1)
        exact=sum(math.comb(6,j) for j in range(pos,7))/(2**6)
        ans["uncertainty"][key]={"trial_equal_mean_MSE_reduction":float(vals.mean()),
            "positive_trials":pos,"exact_one_sided_sign_p":exact,
            "bootstrap_trial_CI95_descriptive":np.quantile(reps,[.025,.975]).tolist()}
    ans["interpretation"]="retrospective next-velocity group-transfer, NOT causal fish force or field chorus"
    return ans
def run():
    j=read_json(ZENODO)
    files={f.get("key"):f for f in j.get("files",[]) if isinstance(f,dict)}
    if not set(RECORDINGS).issubset(files):raise SourceStop("SIX_ORIGINAL_FILES_MISSING")
    with tempfile.TemporaryDirectory(prefix="original_fish_8_") as d:
        receipts=[]
        for i,name in enumerate(RECORDINGS):
            path=Path(d)/name
            receipts.append(download_and_audit(files[name],path))
        # All six original byte hashes authenticated BEFORE any behavioral scores
        trials={}
        for i,name in enumerate(RECORDINGS):
            frame,pos=source_csv(Path(d)/name)
            trials[i]=make_trial(frame,pos,i)
        result=assess(trials)
        result["source_provider_MD5_all_six_verified"]=True
        result["original_file_sha256"]=[r["sha256"] for r in receipts]
        result["source_numeric_values_redistributed"]=False
        return result
def main():
    try:res=run()
    except (SourceStop,OSError,ValueError) as ex:
        res={"status":"SOURCE_OR_MODEL_SUPPORT_STOP","reason":str(ex),
             "ecological_effect":"NOT_ESTIMATED"}
    path=Path("validation_fish_school_v5/results/2024_field_trial_holdout.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":res["status"],"reason":res.get("reason"),
      "uncertainty":res.get("uncertainty"),"trials":[{"heldout_trial":x["heldout_trial"],
      "M0":x["score_mse"]["self"],"M1":x["score_mse"]["boids"],
      "M2":x["score_mse"]["speed_selective"]} for x in res.get("trials",[])]}))
if __name__=="__main__":main()
