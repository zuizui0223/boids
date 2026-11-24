"""v22 source-backed Puy 2024 tetra: 0s versus t−2s OTHER-school velocity.

NO ORIGINAL RAW TRAJECTORY DISTRIBUTION. Only aggregate heldout MSEs.
"""
from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v7"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v8"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v22"))
from forecast_transfer import (
    read_json,ZENODO,RECORDINGS,download_and_audit,SourceStop,source_csv,
    make_trial,FPS,N_FISH,SPEED_DIFF_LAG,GHOST_LAG
)
from local_global import panels
from assignment_and_delay import original_indices, FROZEN_GGLOBAL
from comparison import relative_other_mean,locked_panels,make_source_panels,assess,HORIZONS


def tetra_one(frame,pos,v5,sha256):
    idx=original_indices(frame,pos)
    if len(idx)*N_FISH != len(v5["Y"]):
        raise SourceStop("TETRA_V22_ORIGINAL_INDEX_COHORT_STOP")
    native=panels(v5)
    geometry=native["geometry"]
    locked_current=native["geometry_global"]
    now=(pos[idx]-pos[idx-SPEED_DIFF_LAG])/(SPEED_DIFF_LAG/FPS)
    past=(pos[idx-GHOST_LAG]-pos[idx-GHOST_LAG-SPEED_DIFF_LAG])/(SPEED_DIFF_LAG/FPS)
    expected_own=v5["X"]["self"][:,2:4].reshape(-1,N_FISH,2)
    if not np.allclose(expected_own,now,rtol=0,atol=1e-8):
        raise SourceStop("PUBLISHED_SOURCE_CURRENT_SELF_VELOCITY_REPLAY_STOP")
    cur=relative_other_mean(now,now)
    stale=relative_other_mean(past,now)
    base=locked_panels(geometry,locked_current,cur,stale)

    # Delayed 0.5–0.7s exactly follows v8 source-cohort filter.
    start,end=25,35
    keep=(idx+end<len(frame))
    ix=idx[keep]
    if not len(ix):raise SourceStop("DELAYED_EMPTY_COHORT")
    ok=np.isfinite(pos[ix+start]).all(axis=(1,2))
    ok &= np.isfinite(pos[ix+end]).all(axis=(1,2))
    ok &= (frame[ix+start]-frame[ix]==start)
    ok &= (frame[ix+end]-frame[ix+start]==end-start)
    which=np.flatnonzero(keep)[ok]
    if len(which)<3000:raise SourceStop("DELAYED_COHORT_INSUFFICIENT")
    goodidx=idx[which]
    ylate=((pos[goodidx+end]-pos[goodidx+start])/
           ((end-start)/FPS)).reshape(-1,2)
    rows=(which[:,None]*N_FISH+np.arange(N_FISH)[None,:]).ravel()
    short={"short":base,"delayed":{k:v[rows] for k,v in base.items()}}
    y={"short":v5["Y"],"delayed":ylate}
    return make_source_panels(short,y,
        {"native_frames":len(frame),"eligible_short_target_fish_frames":len(v5["Y"]),
         "eligible_delayed_target_fish_frames":len(ylate),
         "source_sha256":sha256},
        {"published_native_FPS":FPS,"stale_OTHER_velocity_lag_source_frames":GHOST_LAG,
         "same_focal_current_and_geometry_in_all_models":True,
         "original_v7_feature_arrays_exact_replayed":True,
         "no_future_trajectory_inputs":True})


def run():
    original_metadata=read_json(ZENODO)
    filemap={x.get("key"):x for x in original_metadata.get("files",[]) if isinstance(x,dict)}
    if not set(RECORDINGS).issubset(filemap):
        raise SourceStop("PUBLISHED_ZENODO_SIX_FILES_MISSING")
    with tempfile.TemporaryDirectory(prefix="boids_v22_puy_") as d:
        receipts={}
        # Authenticate ALL files before opening any biological outcomes.
        for name in RECORDINGS:
            receipts[name]=download_and_audit(filemap[name],Path(d)/name)
        by_file={}
        for held,name in enumerate(RECORDINGS):
            frame,pos=source_csv(Path(d)/name)
            v5=make_trial(frame,pos,held)
            by_file[held]=tetra_one(frame,pos,v5,receipts[name]["sha256"])
        out=assess(by_file,"Puy et al. 2024 PNAS black neon tetra 8-fish six source recordings",
                   expected=6,anchor=FROZEN_GGLOBAL)
        out["source_author_metadata"]="Zenodo record 10890112, original six provider MD5"
        out["original_provider_MD5_verified"]=True
        out["source_sha256"]=[receipts[n]["sha256"] for n in RECORDINGS]
        out["n_fish_per_recording"]=N_FISH
        out["native_fps"]=FPS
        out["coordinate_units"]="(cm/s)^2 for velocity MSE"
        out["original_source_file_names"]=list(RECORDINGS)
        return out


def main():
    try:out=run()
    except (SourceStop,ValueError,OSError,IndexError,KeyError) as exc:
        out={"status":"SOURCE_OR_REPLAY_STOP","reason":str(exc),"v22_empirical_score":None}
    path=Path("validation_fish_school_v22/results/tetra_current_vs_stale.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],"reason":out.get("reason"),
                      "comparisons":out.get("comparisons")},sort_keys=True))
if __name__=="__main__": main()
