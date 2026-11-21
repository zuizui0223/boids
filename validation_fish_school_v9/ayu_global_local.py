"""v9c independent ayu schooling source: whole-recording global versus k=3 local forecast.

Original Niizato et al 2024 P. altivelis 7 sessions, original repo pinned.
MATLAB author x=D(:,3:12), y=D(:,13:22), metadata time column 2.
Original source is 30fps (frame-index / elapsed-time crosscheck), not the
20Hz downstream sample used in the original article's IIT analysis.
No original coordinates redistributed, no synchronized fish calls.
"""
from __future__ import annotations
import json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v9"))
from forecast_transfer import fit_ridge,SourceStop
from ayu_source_gate import FILES,PIN,blobsha
FPS=30.
N=10
NEIGHBORS=3
STRIDE=6
LAG=3
T_FUTURE=6
DELAY_START=15
DELAY_END=21
SOURCE_ROW_LIMIT_MIN=6000
SEED=20261120

def source_data(path,sha,size):
    b=Path(path).read_bytes()
    if len(b)!=size or blobsha(b)!=sha:raise SourceStop("ORIGINAL_AYU_GIT_SHA_STOP")
    D=np.loadtxt(path,dtype=np.float64)
    if D.ndim!=2 or D.shape[1]!=22 or len(D)<SOURCE_ROW_LIMIT_MIN:
        raise SourceStop("AUTHORS_22_COL_OR_ROWS_STOP")
    if not np.isfinite(D).all():raise SourceStop("ORIGINAL_MISSING_VALUES_STOP")
    frame=D[:,0]
    time=D[:,1]
    if not np.all(np.diff(frame)==1):raise SourceStop("ORIGINAL_NONCONTIGUOUS_FRAME_STOP")
    # The source elapsed time is rounded to 0.01s and steps alternate .03 and .04.
    drift=np.abs((time-time[0])-(frame-frame[0])/FPS)
    if np.max(drift)>.035:raise SourceStop("ORIGINAL_30FPS_NATIVE_UTC_TIME_STOP")
    pos=np.stack((D[:,2:12],D[:,12:22]),axis=-1)
    if pos.shape!=(len(D),N,2):raise SourceStop("AUTHOR_X_Y_MAPPING_STOP")
    return frame,time,pos

def features(pos):
    if pos.ndim!=3 or pos.shape[1:]!=(N,2):raise SourceStop("AYU_FISH_STATE_SCHEMA_STOP")
    nt=len(pos)
    idx=np.arange(2*LAG,nt-DELAY_END,STRIDE)
    if len(idx)<500:raise SourceStop("NOT_ENOUGH_KINEMATIC_EVENTS")
    now=pos[idx]
    vel=(pos[idx]-pos[idx-LAG])/(LAG/FPS)
    older=(pos[idx-LAG]-pos[idx-2*LAG])/(LAG/FPS)
    speed=np.linalg.norm(vel,axis=2)
    target=(pos[idx+T_FUTURE]-pos[idx])/(T_FUTURE/FPS)
    later=(pos[idx+DELAY_END]-pos[idx+DELAY_START])/((DELAY_END-DELAY_START)/FPS)
    offset=now[:,None,:,:]-now[:,:,None,:]  # j-i
    distances2=(offset**2).sum(axis=-1)
    distances2[:,np.arange(N),np.arange(N)]=np.inf
    nn=np.argsort(distances2,axis=2)[:,:,:NEIGHBORS]
    local_pos=np.take_along_axis(offset,nn[:,:,:,None],axis=2).mean(axis=2)
    local_d=np.sqrt(np.take_along_axis(distances2,nn,axis=2)).mean(axis=2)
    group_offset=now.mean(axis=1,keepdims=True)-now
    own=np.concatenate((now,vel,older,vel-older,speed[:,:,None]),axis=2)
    geometry=np.concatenate((own,local_pos,local_d[:,:,None],group_offset),axis=2)
    velocity_difference=vel[:,None,:,:]-vel[:,:,None,:]  # v_j-v_i
    local=np.take_along_axis(velocity_difference,nn[:,:,:,None],axis=2).mean(axis=2)
    global_mean=((vel.sum(axis=1,keepdims=True)-N*vel)/(N-1))
    # Source-locked negative control: rotate the other nine fish velocity
    # vectors among fixed nine positions for each focal fish separately.
    # This preserves global_mean AND original geometry for every focal time.
    perm=np.zeros_like(local)
    for i in range(N):
        other=np.array([j for j in range(N) if j!=i])
        original=vel[:,other,:]
        rotated=np.roll(original,1,axis=1)
        if not np.allclose(rotated.sum(axis=1),original.sum(axis=1),atol=1e-8,rtol=0):
            raise SourceStop("ORIGINAL_GLOBAL_OTHER_SPEED_NOT_PRESERVED")
        local_ids=nn[:,i,:]
        ranks=local_ids-(local_ids>i).astype(int)
        selected=np.take_along_axis(rotated,ranks[:,:,None],axis=1)
        perm[:,i,:]=selected.mean(axis=1)-vel[:,i,:]
    panels={
       "G_geometry":geometry,
       "G_global":np.concatenate((geometry,global_mean),axis=2),
       "G_local3":np.concatenate((geometry,local),axis=2),
       "G_both":np.concatenate((geometry,global_mean,local),axis=2),
       "G_global_ghost3":np.concatenate((geometry,global_mean,perm),axis=2)
    }
    y={"short":target.reshape(-1,2),"delayed":later.reshape(-1,2)}
    X={k:v.reshape(-1,v.shape[-1]) for k,v in panels.items()}
    if not all(np.isfinite(v).all() for v in [*X.values(),*y.values()]):
        raise SourceStop("NONFINITE_AYU_OUTCOMES_OR_FEATURES")
    return {"X":X,"Y":y,"source_rows":len(pos),"n_eligible_fish_frame":len(idx)*N,
            "mean_nearest3_distance_original_units":float(local_d.mean()),
            "mean_group_radius_original_units":float(np.linalg.norm(group_offset,axis=2).mean()),
            "mean_local_global_velocity_difference":float(np.linalg.norm(local-global_mean,axis=2).mean())}

def assess(trials):
    if len(trials)!=7 or sorted(trials)!=list(range(7)):raise SourceStop("SEVEN_INDEPENDENT_RECORDING_FILES_REQUIRED")
    models=("G_geometry","G_global","G_local3","G_both","G_global_ghost3")
    out=[]
    for held in range(7):
        row={"heldout_recording":held,"source_rows":trials[held]["source_rows"],
             "scored_original_fish_frames":trials[held]["n_eligible_fish_frame"],
             "MSE":{}}
        for horizon in ("short","delayed"):
            per={}
            for model in models:
                xs=np.concatenate([trials[i]["X"][model] for i in range(7) if i!=held])
                ys=np.concatenate([trials[i]["Y"][horizon] for i in range(7) if i!=held])
                pred=fit_ridge(xs,ys,trials[held]["X"][model])
                per[model]=float(np.mean((trials[held]["Y"][horizon]-pred)**2))
            row["MSE"][horizon]=per
        out.append(row)
    comps={}
    rng=np.random.default_rng(SEED)
    for horizon in ("short","delayed"):
        f=lambda x:x["MSE"][horizon]
        contrasts={
            "global_beyond_geometry":np.array([f(x)["G_geometry"]-f(x)["G_global"] for x in out]),
            "local3_beyond_global":np.array([f(x)["G_global"]-f(x)["G_both"] for x in out]),
            "global_beyond_local3":np.array([f(x)["G_local3"]-f(x)["G_both"] for x in out]),
            "correct_local3_vs_rotated_others":np.array([f(x)["G_global_ghost3"]-f(x)["G_both"] for x in out])
        }
        comps[horizon]={}
        for k,z in contrasts.items():
            positive=int((z>0).sum())
            draws=np.mean(z[rng.integers(0,7,size=(5000,7))],axis=1)
            base=np.array([f(x)["G_global"] for x in out])
            comps[horizon][k]={
                "recording_equal_mean_delta_MSE_source_units_per_s_squared":float(np.mean(z)),
                "recording_equal_fraction_of_global_baseline_mean_MSE":float(np.mean(z)/np.mean(base)),
                "positive_recordings":positive,
                "exact_one_sided_sign_p_if_independent":sum(math.comb(7,i) for i in range(positive,8))/128,
                "descriptive_seven_recording_95pct":np.quantile(draws,[.025,.975]).tolist()}
    return {"status":"ORIGINAL_INDEPENDENT_AYU_SEVEN_RECORDINGS_SCORED",
      "original_fish_species":"Plecoglossus altivelis",
      "study":"Niizato et al. 2024 Scientific Reports",
      "n_recordings":7,"fish_per_recording":N,
      "original_native_fps_verified":FPS,"original_author_columns":"X=source columns 3-12, Y=13-22",
      "k_nearest_neighbors":NEIGHBORS,"future_short_seconds":T_FUTURE/FPS,
      "delayed_window_seconds":[DELAY_START/FPS,DELAY_END/FPS],
      "test_split":"one original recording completely held out",
      "source_units":"unknown numeric coordinate units: compare relative within-species gains only",
      "trial_results":out,"comparisons":comps,
      "interpretation_boundary":"retrospective predictive comparisons; no causal Boids force, no paired fish sounds; trials may not be independent populations"}
def run(root):
    base=Path(root)/"Compute_IIT/fish_revised"
    # Pin all source bytes BEFORE opening any biological target values.
    for name,(sha,size) in FILES.items():
        b=(base/name).read_bytes()
        if len(b)!=size or blobsha(b)!=sha:raise SourceStop("SOURCE_PUBLISHED_BLOB_CHANGED")
    d={}
    for i,(name,(sha,size)) in enumerate(FILES.items()):
        frames,tm,pos=source_data(base/name,sha,size)
        d[i]=features(pos)
    result=assess(d);result["pinned_upstream_commit"]=PIN
    result["source_original_files"]=list(FILES)
    result["original_coordinates_redistributed"]=False
    return result
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    a=p.parse_args()
    try:res=run(a.root)
    except (SourceStop,OSError,ValueError,IndexError) as e:
        res={"status":"SOURCE_OR_NUMERIC_MODEL_STOP","reason":str(e),
             "observed_fish_predictive_effect":"NOT_ESTIMATED"}
    path=Path("validation_fish_school_v9/results/ayu_seven_trial_forecast.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":res["status"],"reason":res.get("reason"),
      "comparisons":res.get("comparisons"),
      "source_rows":[t["source_rows"] for t in res.get("trial_results",[])]}))
if __name__=="__main__":main()
