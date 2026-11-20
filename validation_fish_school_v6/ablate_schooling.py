"""v6 frozen source-replayed neighbor-geometry vs alignment dissection.

Original Puy et al. 2024 six 8-fish 50fps source recordings. No separate
v6 training/response filters: exact v5 source cohorts and velocity target.
Scientific status: exploratory post-v5 primary outcome; not novel
experimental fish interaction, and NOT acoustic chorus evidence.
"""
from __future__ import annotations
import json, math, sys, tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
from forecast_transfer import (read_json, ZENODO, RECORDINGS, download_and_audit,
       SourceStop, source_csv, make_trial, fit_ridge, SEED, RIDGE_ALPHA,
       FPS, DT_FUTURE, PERCEPTION_CM, SEPARATION_CM)

# Frozen v5 source-exact first-run MSE from original Actions #44743721112.
FROZEN_M0=[15.271002142868323,13.191108071824212,12.427786463885495,
           13.0637902434925,13.705233980305321,15.75942564804181]
FROZEN_FULL=[12.115603785844542,10.581968924730777,10.120566696875384,
             10.5597446908978,11.879668260955281,12.682022681554074]
FROZEN_FAST=[12.014886947227891,10.518581108266755,10.062248593997717,
             10.513108903632277,11.88254988745024,12.56739437618547]
# Order of seven source M1 social fields: sep-x/sep-y, align-x/align-y,
# cohesion-x/cohesion-y, number-within-25cm.
SELECTORS={
    "own":(),
    "separation_only":(0,1),
    "cohesion_only":(4,5,6),
    "alignment_only":(2,3),
    "spatial_only":(0,1,4,5,6),
    "meanfield_no_repulsion":(2,3,4,5,6),
    "no_cohesion":(0,1,2,3,6),
    "full_boids":(0,1,2,3,4,5,6)
}
SEED_V6=20261120

def layer_matrices(v5_trial):
    own=v5_trial["X"]["self"]
    full=v5_trial["X"]["boids"]
    if full.shape[1] != own.shape[1]+7:raise SourceStop("V5_MODEL_COLUMN_SCHEMA_DRIFT")
    social=full[:,own.shape[1]:]
    if social.shape[1]!=7:raise SourceStop("V5_SOCIAL_FEATURE_DRIFT")
    out={}
    for name,select in SELECTORS.items():
        out[name]=own if not select else np.concatenate((own,social[:,select]),axis=1)
    out["faster_neighbor"]=v5_trial["X"]["speed_selective"]
    if out["faster_neighbor"].shape[1]!=own.shape[1]+10:
        raise SourceStop("V5_FASTER_NEIGHBOR_SCHEMA_DRIFT")
    # source aliases must be numerically identical; no change in old model.
    if not np.array_equal(out["full_boids"],full):
        raise SourceStop("FROZEN_FULL_FEATURES_CHANGED")
    return out

def validate_frozen(scores,held):
    for key,vals in (("own",FROZEN_M0),("full_boids",FROZEN_FULL),
                     ("faster_neighbor",FROZEN_FAST)):
        if not np.isclose(scores[key],vals[held],rtol=0,atol=2e-5):
            raise SourceStop(f"ORIGINAL_V5_SCORE_REPLAY_STOP trial={held} panel={key}")

def estimate(sources):
    if sorted(sources)!=list(range(6)):raise SourceStop("SIX_ORIGINAL_RECORDINGS_REQUIRED")
    mats={k:layer_matrices(v) for k,v in sources.items()}
    results=[]
    for held in range(6):
        test=sources[held]
        row={"heldout_original_recording":held,
             "original_test_fish_frames":int(len(test["Y"])),
             "MSE_per_model":{}}
        for mode in (*SELECTORS,"faster_neighbor"):
            train_x=np.concatenate([mats[j][mode] for j in range(6) if j!=held],axis=0)
            train_y=np.concatenate([sources[j]["Y"] for j in range(6) if j!=held],axis=0)
            pred=fit_ridge(train_x,train_y,mats[held][mode])
            row["MSE_per_model"][mode]=float(np.mean((test["Y"]-pred)**2))
        validate_frozen(row["MSE_per_model"],held)
        result=row["MSE_per_model"]
        row["gains_MSE"]={
            "own_to_spatial":result["own"]-result["spatial_only"],
            "spatial_to_alignment":result["spatial_only"]-result["full_boids"],
            "own_to_alignment":result["own"]-result["alignment_only"],
            "meanfield_to_repulsion":result["meanfield_no_repulsion"]-result["full_boids"],
            "no_cohesion_to_full":result["no_cohesion"]-result["full_boids"],
            "own_to_full_replay":result["own"]-result["full_boids"],
            "full_to_faster":result["full_boids"]-result["faster_neighbor"]
        }
        results.append(row)
    rng=np.random.default_rng(SEED_V6)
    out={"version":"v6_original_schooling_layer_ablation",
         "status":"ORIGINAL_EIGHT_FISH_V6_SIX_TRIALS_SCORED",
         "source":"Puy et al. 2024 PNAS / original Zenodo 10890112",
         "v5_original_score_replay":"PASS_2e-5",
         "original_source_MD5_six_all_verified":True,
         "trial_unit":"whole recording (may reuse fish; not six independent populations)",
         "target":"0.2s future average 2D velocity cm per second",
         "fixed_perception_cm":PERCEPTION_CM,
         "fixed_repulsion_cm":SEPARATION_CM,
         "fixed_ridge_alpha":RIDGE_ALPHA,
         "feature_modes":{k:list(v) for k,v in SELECTORS.items()},
         "scored_trial_results":results,"comparisons":{}}
    for contrast in results[0]["gains_MSE"]:
        gains=np.array([x["gains_MSE"][contrast] for x in results])
        npos=int(np.sum(gains>0))
        samples=np.mean(gains[rng.integers(0,6,size=(5000,6))],axis=1)
        out["comparisons"][contrast]={
            "recording_equal_mean_MSE_gain":float(np.mean(gains)),
            "positive_recording_trials":npos,
            "exact_sign_p_one_sided_if_trials_independent":sum(math.comb(6,j) for j in range(npos,7))/64,
            "95pct_descriptive_whole_recording_bootstrap":np.quantile(samples,[.025,.975]).tolist()}
    out["scientific_claim_ceiling"]="Independent predictive *feature information* within a single study, not unique causal forces or fish calling."
    return out

def run():
    meta=read_json(ZENODO)
    filemap={f.get("key"):f for f in meta.get("files",[]) if isinstance(f,dict)}
    if not set(RECORDINGS).issubset(filemap):
        raise SourceStop("FROZEN_SIX_SOURCE_MEMBERS_MISSING")
    with tempfile.TemporaryDirectory(prefix="fish_v6_source_") as directory:
        original=[]
        for name in RECORDINGS:
            path=Path(directory)/name
            original.append(download_and_audit(filemap[name],path))
        # Confirm ALL six provider digests before any behavioral model is fitted.
        sources={}
        for i,name in enumerate(RECORDINGS):
            frames,positions=source_csv(Path(directory)/name)
            sources[i]=make_trial(frames,positions,i)
        res=estimate(sources)
        res["original_SHA256"]=[entry["sha256"] for entry in original]
        res["raw_fish_trajectories_redistributed"]=False
        return res

def main():
    try:res=run()
    except (SourceStop,ValueError,OSError) as e:
        res={"status":"SOURCE_OR_MODEL_ADMISSION_STOP","reason":str(e),"numerical_effect":"NOT_EVALUATED"}
    path=Path("validation_fish_school_v6/results/observed_fish_motion_ablation.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":res["status"],"reason":res.get("reason"),
       "v5_source_replay":res.get("v5_original_score_replay"),
       "comparisons":res.get("comparisons")}))
if __name__=="__main__":
    main()
