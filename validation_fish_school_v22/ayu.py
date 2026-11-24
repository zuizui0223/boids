"""v22 source-backed Niizato 2024 ayu: current versus 2-second-old other-fish mean.

Original published 30fps TXT source; no fish sound data.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v9"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v22"))
from forecast_transfer import SourceStop
from ayu_source_gate import FILES,PIN,blobsha
from ayu_global_local import source_data,features,FPS,N,STRIDE,LAG,DELAY_END
from comparison import relative_other_mean,locked_panels,make_source_panels,assess

STALE_FRAMES=60
EARLIEST_COHORT=66
assert STALE_FRAMES/FPS == 2.0
assert EARLIEST_COHORT>=STALE_FRAMES+LAG


def ayu_one(path,sha,size):
    _,seconds,pos=source_data(path,sha,size)
    native=features(pos)
    idx=np.arange(2*LAG,len(pos)-DELAY_END,STRIDE)
    if len(idx)*N != len(native["Y"]["short"]):
        raise SourceStop("AYU_V9C_COHORT_REPLAY_STOP")
    selected=np.flatnonzero(idx>=EARLIEST_COHORT)
    if len(selected)<500:
        raise SourceStop("AYU_TWO_SECOND_HISTORY_INSUFFICIENT")
    at=idx[selected]
    # Same cohort for every model and horizon.
    rows=(selected[:,None]*N+np.arange(N)[None,:]).ravel()
    now=(pos[at]-pos[at-LAG])/(LAG/FPS)
    past=(pos[at-STALE_FRAMES]-pos[at-STALE_FRAMES-LAG])/(LAG/FPS)
    current=relative_other_mean(now,now)
    stale=relative_other_mean(past,now)
    geometry=native["X"]["G_geometry"][rows]
    locked=native["X"]["G_global"][rows]
    p=locked_panels(geometry,locked,current,stale)
    x={"short":p,"delayed":p}
    y={key:val[rows] for key,val in native["Y"].items()}
    raw=Path(path).read_bytes()
    return make_source_panels(x,y,
        {"original_file":path.name,"original_rows":len(pos),
         "eligible_fish_frame_targets":len(rows),
         "source_file_sha256":hashlib.sha256(raw).hexdigest(),
         "pinned_git_blob":sha},
        {"native_source_fps":FPS,"native_source_elapsed_time_checked":True,
         "original_v9c_model_geometry_and_current_exact":True,
         "stale_lag_frames":STALE_FRAMES,
         "first_eligible_source_frame":int(at[0]),
         "no_future_state_in_predictor":True})


def run(root):
    source=Path(root)
    if not (source/".git").exists():
        raise SourceStop("AYU_GIT_TREE_SOURCE_REQUIRED")
    # Git commit PIN is checked in the pinned Actions step before invoking.
    base=source/"Compute_IIT/fish_revised"
    for filename,(sha,size) in FILES.items():
        b=(base/filename).read_bytes()
        if len(b)!=size or blobsha(b)!=sha:
            raise SourceStop("AYU_ORIGINAL_GIT_BLOB_CHANGED")
    samples={}
    for i,(filename,(sha,size)) in enumerate(FILES.items()):
        samples[i]=ayu_one(base/filename,sha,size)
    result=assess(samples,"Niizato et al. 2024 Scientific Reports Plecoglossus altivelis 10-fish seven source recordings",
                  expected=7)
    result["upstream_pinned_git_commit"]=PIN
    result["original_git_blobs_verified"]=True
    result["original_source_file_names"]=list(FILES)
    result["source_sha256"]=[samples[i]["source"]["source_file_sha256"] for i in range(7)]
    result["n_fish_per_recording"]=N
    result["native_fps"]=FPS
    result["coordinate_units"]="unknown original coordinate units; MSE of native units/s squared"
    result["frozen_original_v9c_feature_rows_replayed_as_subset"]=True
    return result


def main():
    import argparse
    cli=argparse.ArgumentParser()
    cli.add_argument("--root",required=True)
    args=cli.parse_args()
    try:res=run(args.root)
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as exc:
        res={"status":"SOURCE_OR_REPLAY_STOP","reason":str(exc),"v22_empirical_score":None}
    p=Path("validation_fish_school_v22/results/ayu_current_vs_stale.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":res["status"],"reason":res.get("reason"),
                      "comparisons":res.get("comparisons")},sort_keys=True))

if __name__=="__main__": main()
