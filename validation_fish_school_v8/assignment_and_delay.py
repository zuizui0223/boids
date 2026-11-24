"""v8 exact-source six-school velocity-assignment counterfactual & delayed forecast.

EXPLORATORY continuation after source v5-v7 effects. No fish calls.
Primary: true neighbor velocity-position pairing vs permutations preserving all
other-fish instantaneous velocities for each focal fish. Separate delayed
0.5..0.7 s prediction reduces overlap with hypothetical +/-10-frame
symmetric filter, but does not establish prospective source processing.
"""
from __future__ import annotations
import json, math, sys, tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v7"))
from forecast_transfer import (
    read_json,ZENODO,RECORDINGS,download_and_audit,SourceStop,
    source_csv,make_trial,fit_ridge,PERCEPTION_CM,SPEED_DIFF_LAG,
    GHOST_LAG,DT_FUTURE,STRIDE,FPS,N_FISH
)
from local_global import panels
FROZEN_GGLOBAL=(12.140563,10.616998,10.129958,10.587340,11.955914,12.687114)
FROZEN_BOTH=(12.114212,10.583004,10.121057,10.555843,11.875855,12.675138)
ROTATIONS=(1,3)
DELAY_START_FRAMES=25
DELAY_END_FRAMES=35
SEED=20261120

def original_indices(frame,positions):
    n=len(frame)
    idx=np.arange(GHOST_LAG+2*SPEED_DIFF_LAG,n-DT_FUTURE,STRIDE,dtype=int)
    offsets=np.array([-GHOST_LAG-2*SPEED_DIFF_LAG,-GHOST_LAG-SPEED_DIFF_LAG,
        -GHOST_LAG,-2*SPEED_DIFF_LAG,-SPEED_DIFF_LAG,0,DT_FUTURE])
    picks=idx[:,None]+offsets[None,:]
    v=np.isfinite(positions[picks]).all(axis=(1,2,3))
    v &= (np.diff(frame[picks],axis=1)==np.diff(offsets)[None,:]).all(axis=1)
    return idx[v]

def local_vectors(position,frame,idx):
    at=position[idx]
    vel=(position[idx]-position[idx-SPEED_DIFF_LAG])/(SPEED_DIFF_LAG/FPS)
    offset=at[:,None,:,:]-at[:,:,None,:]  # focal i vs neighbor j => j-i
    r2=(offset**2).sum(axis=-1)
    mask=(r2<PERCEPTION_CM**2) & (~np.eye(N_FISH,dtype=bool)[None,:,:])
    dvel=vel[:,None,:,:]-vel[:,:,None,:]
    counts=mask.sum(axis=-1)
    align=(mask[:,:,:,None]*dvel).sum(axis=2)/np.maximum(counts,1)[:,:,None]
    return vel,mask,align,counts

def rotate_other_velocities(vel,mask,rotation):
    """For each focal, rotate ONLY the seven other fish velocities across
    other-fish positions. The same seven-vector multiset, school-wide mean,
    focal own history, spatial geometry and target are exactly unchanged.
    The rearrangement is a diagnostic, NOT a physically realizable treatment.
    """
    if rotation not in ROTATIONS:raise ValueError("Frozen rotation not allowed")
    if vel.ndim!=3 or vel.shape[1:]!=(N_FISH,2):
        raise SourceStop("PERMUTATION_SCHEMA_STOP")
    if mask.shape!=(len(vel),N_FISH,N_FISH):
        raise SourceStop("PERMUTATION_MASK_STOP")
    out=np.zeros_like(vel)
    for focal in range(N_FISH):
        other=np.array([j for j in range(N_FISH) if j!=focal],dtype=int)
        native=vel[:,other,:]
        perm=np.roll(native,rotation,axis=1)
        if not np.allclose(native.sum(axis=1),perm.sum(axis=1),rtol=0,atol=1e-8):
            raise SourceStop("FRAMEWISE_GLOBAL_VELOCITY_CHANGED")
        count=mask[:,focal,other].sum(axis=1)
        difference=perm-vel[:,focal:focal+1,:]
        out[:,focal,:]=(mask[:,focal,other,None]*difference).sum(axis=1)/np.maximum(count,1)[:,None]
    return out

def build(frame,pos,idx,v5):
    if len(idx)*N_FISH!=len(v5["Y"]):
        raise SourceStop("V5_SOURCE_COHORT_INDEX_MISMATCH")
    p=panels(v5)
    velocity,mask,local,count=local_vectors(pos,frame,idx)
    true_local=v5["X"]["boids"][:,15:17]
    if not np.allclose(local.reshape(-1,2),true_local,rtol=0,atol=1e-8):
        raise SourceStop("V5_REAL_LOCAL_ALIGNMENT_REPLAY_FAILED")
    result={
      "global":p["geometry_global"],
      "global_true":p["geometry_global_local"],
    }
    for rotation in ROTATIONS:
        perm=rotate_other_velocities(velocity,mask,rotation).reshape(-1,2)
        result[f"global_rot{rotation}"]=np.concatenate((p["geometry_global"],perm),axis=1)
        if not np.array_equal(result[f"global_rot{rotation}"][:,:-2],p["geometry_global"]):
            raise SourceStop("GLOBAL_OR_GEOMETRY_CHANGED_BY_ROTATION")
    if len(np.unique(frame))!=len(frame):raise SourceStop("DUPLICATE_ORIGINAL_FRAME")
    ok=(idx+DELAY_END_FRAMES<len(frame))
    ix=idx[ok];old=pos
    ok2=np.isfinite(old[ix+DELAY_START_FRAMES]).all(axis=(1,2))
    ok2 &= np.isfinite(old[ix+DELAY_END_FRAMES]).all(axis=(1,2))
    ok2 &= (frame[ix+DELAY_START_FRAMES]-frame[ix]==DELAY_START_FRAMES)
    ok2 &= (frame[ix+DELAY_END_FRAMES]-frame[ix+DELAY_START_FRAMES]==
            DELAY_END_FRAMES-DELAY_START_FRAMES)
    # Note: original indices remain unchanged in primary 0.2s task.
    which=np.flatnonzero(ok)[ok2]
    if len(which)<3000:raise SourceStop("DELAYED_TARGET_INSUFFICIENT")
    ix2=idx[which]
    ylate=((old[ix2+DELAY_END_FRAMES]-old[ix2+DELAY_START_FRAMES])/
           ((DELAY_END_FRAMES-DELAY_START_FRAMES)/FPS)).reshape(-1,2)
    if not np.isfinite(ylate).all():raise SourceStop("NONFINITE_DELAYED_TARGET")
    rows=(which[:,None]*N_FISH+np.arange(N_FISH)[None,:]).ravel()
    delayed_x={key:value[rows] for key,value in result.items()}
    return {"X":result,"Y":v5["Y"],
            "delayed_X":delayed_x,"delayed_Y":ylate,
            "n_original_indices":len(idx),"n_delayed_indices":len(ix2),
            "neighbor_count_summary":{
                "mean":float(count.mean()),"fraction_all_other_7":float((count==7).mean()),
                "fraction_0_3":float((count<=3).mean()),
                "fraction_4_6":float(((count>=4)&(count<=6)).mean())}}

def estimate(samples):
    if sorted(samples)!=list(range(6)):raise SourceStop("SIX_RECORDINGS_REQUIRED")
    response=[]
    for trial in range(6):
        row={"heldout_recording":trial,"n_original_targets":len(samples[trial]["Y"]),
             "n_delay_targets":len(samples[trial]["delayed_Y"]),
             "neighbor_count_summary":samples[trial]["neighbor_count_summary"],
             "MSE_short":{},"MSE_delayed":{}}
        for key in ("global","global_true","global_rot1","global_rot3"):
            x=np.concatenate([samples[k]["X"][key] for k in range(6) if k!=trial])
            y=np.concatenate([samples[k]["Y"] for k in range(6) if k!=trial])
            pred=fit_ridge(x,y,samples[trial]["X"][key])
            row["MSE_short"][key]=float(np.mean((samples[trial]["Y"]-pred)**2))
        # Freeze the old real source v7 scores before opening novel contrasts.
        if (abs(row["MSE_short"]["global"]-FROZEN_GGLOBAL[trial])>6e-5
            or abs(row["MSE_short"]["global_true"]-FROZEN_BOTH[trial])>6e-5):
            raise SourceStop("V7_ORIGINAL_SOURCE_NUMERIC_REPLAY_STOP")
        for key in ("global","global_true","global_rot1"):
            x=np.concatenate([samples[k]["delayed_X"][key] for k in range(6) if k!=trial])
            y=np.concatenate([samples[k]["delayed_Y"] for k in range(6) if k!=trial])
            pred=fit_ridge(x,y,samples[trial]["delayed_X"][key])
            row["MSE_delayed"][key]=float(np.mean((samples[trial]["delayed_Y"]-pred)**2))
        s,d=row["MSE_short"],row["MSE_delayed"]
        row["contrasts"]={
          "real_local_beyond_global_short":s["global"]-s["global_true"],
          "true_vs_rot1_short":s["global_rot1"]-s["global_true"],
          "true_vs_rot3_short":s["global_rot3"]-s["global_true"],
          "real_local_beyond_global_delayed":d["global"]-d["global_true"],
          "true_vs_rot1_delayed":d["global_rot1"]-d["global_true"],
        }
        response.append(row)
    rng=np.random.default_rng(SEED)
    results={}
    for k in response[0]["contrasts"]:
        vals=np.array([row["contrasts"][k] for row in response],float)
        repl=np.mean(vals[rng.integers(0,6,size=(5000,6))],axis=1)
        n=int((vals>0).sum())
        results[k]={"mean_equal_recording_MSE_difference":float(vals.mean()),
            "positive_recordings":n,
            "one_sided_sign_p_only_if_recordings_independent":sum(math.comb(6,i) for i in range(n,7))/64.,
            "descriptive_95pct_whole_recording_bootstrap":np.quantile(repl,[.025,.975]).tolist()}
    return {"version":"v8_observed_school_velocity_assignments_and_delay",
       "status":"ORIGINAL_2024_FISH_SCHOOL_V8_SCORED",
       "original_source_all_six_MD5_verified":True,
       "v7_original_trial_global_true_replayed":True,
       "rotation_scheme":"for each focal/time, cyclically rotate other 7 velocities among those 7 fixed positions; preserve their exact instantaneous multiset and mean",
       "fixed_rotations":list(ROTATIONS),"future_short_seconds":DT_FUTURE/FPS,
       "delayed_target_start_seconds":DELAY_START_FRAMES/FPS,
       "delayed_target_end_seconds":DELAY_END_FRAMES/FPS,
       "max_symmetric_gaussian_source_support_frames_if_prepublished":10,
       "delayed_task_not_guaranteed_realtime_due_to_original_source_interpolation":True,
       "trial_unit":"recording, not independent school populations",
       "results":response,"comparisons":results,
       "source_kinematics_redistributed":False,
       "ecological_claim":"diagnostic predictive information, not an experimentally perturbed or proven fish social force"}

def run():
    meta=read_json(ZENODO)
    files={f.get("key"):f for f in meta.get("files",[]) if isinstance(f,dict)}
    if not set(RECORDINGS).issubset(files):raise SourceStop("ORIGINAL_SIX_SOURCE_MEMBERS_CHANGED")
    with tempfile.TemporaryDirectory(prefix="v8_school_") as directory:
        files_checked=[]
        for f in RECORDINGS:
            files_checked.append(download_and_audit(files[f],Path(directory)/f))
        by_trial={}
        for k,f in enumerate(RECORDINGS):
            frame,pos=source_csv(Path(directory)/f)
            v5=make_trial(frame,pos,k)
            idx=original_indices(frame,pos)
            by_trial[k]=build(frame,pos,idx,v5)
        out=estimate(by_trial)
        out["source_SHA256"]=[z["sha256"] for z in files_checked]
        return out

def main():
    try:out=run()
    except (SourceStop,OSError,ValueError,IndexError) as e:
        out={"status":"SOURCE_OR_NUMERIC_REPLAY_STOP","reason":str(e),
             "new_empirical_effect":"NOT_ESTIMATED"}
    p=Path("validation_fish_school_v8/results/assignment_and_delay.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":out["status"],"reason":out.get("reason"),
       "comparisons":out.get("comparisons"),
       "neighbor_counts":[r["neighbor_count_summary"] for r in out.get("results",[])]}))
if __name__=="__main__":main()
