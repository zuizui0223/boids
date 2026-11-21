"""v7 motor-field forecast: local Boids alignment vs shared whole-school mean velocity.

Exploratory after original v5/v6 outcomes; six 2024 8-fish recording trials,
exact v5 GPS/timeline cohort, no new fish or fish vocal data.
"""
from __future__ import annotations
import json,math,sys,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
from forecast_transfer import (read_json,ZENODO,RECORDINGS,download_and_audit,
     SourceStop,source_csv,make_trial,fit_ridge,PERCEPTION_CM,RIDGE_ALPHA,N_FISH)
FROZEN_M0=(15.271002142868323,13.191108071824212,12.427786463885495,
           13.0637902434925,13.705233980305321,15.75942564804181)
FROZEN_FULL=(12.115603785844542,10.581968924730777,10.120566696875384,
             10.5597446908978,11.879668260955281,12.682022681554074)
FROZEN_SPATIAL=(15.14133,13.03683,12.26727,12.88236,13.56780,15.51668)
SEED=20261120

def panels(v5):
    x0=v5["X"]["self"]
    oldfull=v5["X"]["boids"]
    oldghost=v5["X"]["stale_school"]
    if x0.shape[1]!=13 or oldfull.shape[1]!=20 or oldghost.shape[1]!=20:
        raise SourceStop("V5_FEATURE_SCHEMA_DRIFT")
    if len(x0) % N_FISH:raise SourceStop("SOURCE_ID_SHAPE_DRIFT")
    s=oldfull[:,13:20]
    spatial=s[:,[0,1,4,5,6]]
    local=s[:,[2,3]]
    lagged=oldghost[:,15:17]
    velocities=x0[:,2:4].reshape(-1,N_FISH,2)
    # Neighbor-global velocity contrast: the mean of OTHER seven fish
    # minus the focal velocity, never future target and no fit on test.
    total=velocities.sum(axis=1,keepdims=True)
    global_align=((total-N_FISH*velocities)/(N_FISH-1)).reshape(-1,2)
    if global_align.shape!=local.shape:raise SourceStop("GLOBAL_FEATURE_SHAPE_STOP")
    out={
     "own":x0,
     "geometry":np.concatenate((x0,spatial),axis=1),
     "geometry_global":np.concatenate((x0,spatial,global_align),axis=1),
     "geometry_local":oldfull,
     "geometry_global_local":np.concatenate((x0,spatial,global_align,local),axis=1),
     "geometry_stale_local":np.concatenate((x0,spatial,lagged),axis=1)
    }
    if not np.array_equal(out["geometry_local"],oldfull):
        raise SourceStop("ORIGINAL_V5_FULL_FEATURE_REPLAY_STOP")
    return out

def replay_one(score,held):
    for name,original,tol in (("own",FROZEN_M0,2e-5),
                              ("geometry_local",FROZEN_FULL,2e-5),
                              ("geometry",FROZEN_SPATIAL,6e-5)):
        if not np.isclose(score[name],original[held],atol=tol,rtol=0):
            raise SourceStop(f"PREVIOUS_SOURCE_SCORE_REPLAY_STOP_{name}_{held}")

def assess(sources):
    if sorted(sources)!=list(range(6)):raise SourceStop("SIX_RECORDINGS_REQUIRED")
    X={i:panels(sources[i]) for i in range(6)}
    out=[]
    for held in range(6):
        scores={}
        for model in X[held]:
            xs=np.concatenate([X[i][model] for i in range(6) if i!=held])
            ys=np.concatenate([sources[i]["Y"] for i in range(6) if i!=held])
            pred=fit_ridge(xs,ys,X[held][model])
            scores[model]=float(np.mean((sources[held]["Y"]-pred)**2))
        replay_one(scores,held)
        out.append({"heldout_recording":held,"n_fish_frame_targets":len(sources[held]["Y"]),
                    "MSE":scores,"comparisons":{
                     "global_gain_over_spatial":scores["geometry"]-scores["geometry_global"],
                     "local_gain_over_spatial":scores["geometry"]-scores["geometry_local"],
                     "local_unique_over_global":scores["geometry_global"]-scores["geometry_global_local"],
                     "global_unique_over_local":scores["geometry_local"]-scores["geometry_global_local"],
                     "current_local_vs_stale_local":scores["geometry_stale_local"]-scores["geometry_local"]}})
    rng=np.random.default_rng(SEED)
    comps={}
    for key in out[0]["comparisons"]:
        z=np.array([o["comparisons"][key] for o in out],float)
        repl=np.mean(z[rng.integers(0,6,size=(5000,6))],axis=1)
        signs=int((z>0).sum())
        comps[key]={"recording_equal_MSE_gain":float(z.mean()),
          "positive_recordings":signs,
          "exact_one_sided_sign_p_if_independent":sum(math.comb(6,j) for j in range(signs,7))/64,
          "descriptive_whole_recording_95pct":np.quantile(repl,[.025,.975]).tolist()}
    return {"status":"ORIGINAL_2024_FISH_SCHOOL_GLOBAL_VS_LOCAL_SCORED",
            "original_source_MD5_verified":True,
            "frozen_v5_v6_scores_reproduced":True,
            "original_recordings":6,"fish_per_recording":8,
            "future_horizon_seconds":.2,
            "source_trial_scores":out,
            "comparisons":comps,
            "scientific_claim_ceiling":"Retrospective local vs global predictive information; NOT local causal Boids force or synchronized calling data"}

def run():
    meta=read_json(ZENODO)
    filemap={f.get("key"):f for f in meta.get("files",[]) if isinstance(f,dict)}
    if not set(RECORDINGS).issubset(filemap):
        raise SourceStop("ORIGINAL_SOURCE_MEMBERS_STOP")
    with tempfile.TemporaryDirectory(prefix="fish_v7_") as d:
        receipts=[]
        for name in RECORDINGS:
            receipts.append(download_and_audit(filemap[name],Path(d)/name))
        samples={}
        for i,name in enumerate(RECORDINGS):
            frame,pos=source_csv(Path(d)/name)
            samples[i]=make_trial(frame,pos,i)
        res=assess(samples)
        res["source_sha256"]=[x["sha256"] for x in receipts]
        res["raw_positions_redistributed"]=False
        return res
def main():
    try:res=run()
    except (SourceStop,ValueError,OSError) as e:
        res={"status":"SOURCE_OR_MODEL_SUPPORT_STOP","reason":str(e),
             "observed_field_effect":"NOT_EVALUATED"}
    p=Path("validation_fish_school_v7/results/global_vs_local_original.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":res["status"],"reason":res.get("reason"),
       "comparisons":res.get("comparisons")}))
if __name__=="__main__":main()
