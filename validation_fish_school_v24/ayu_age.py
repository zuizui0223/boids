"""v24 original Niizato ayu seven source recordings; temporal age curve.

No sound data. Only source-pinned original movement recording scores exported.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
for p in ("validation_fish_school_v5","validation_fish_school_v9",
          "validation_fish_school_v22","validation_fish_school_v24"):
    sys.path.insert(0,str(ROOT/p))
from forecast_transfer import SourceStop
from ayu_source_gate import FILES,PIN,blobsha
from ayu_global_local import source_data,FPS,STRIDE,LAG,DELAY_END
from ayu import ayu_one
from age_curve import source_age_panels,assess,save_result


def run(root):
    origin=Path(root)
    if not (origin/".git").is_dir():
        raise SourceStop("V24_AYU_PINNED_GIT_CHECKOUT_REQUIRED")
    base=origin/"Compute_IIT/fish_revised"
    # The workflow hard-pins the exact author Git commit and locally checks
    # each of the seven source Git blob SHA1 values before any model outcomes.
    for name,(sha,size) in FILES.items():
        b=(base/name).read_bytes()
        if len(b)!=size or blobsha(b)!=sha:
            raise SourceStop("V24_ORIGINAL_AYU_GIT_BYTES_CHANGED")
    samples={}
    for i,(name,(sha,size)) in enumerate(FILES.items()):
        p=base/name
        _,_,pos=source_data(p,sha,size)
        v22=ayu_one(p,sha,size)
        t=np.arange(2*LAG,len(pos)-DELAY_END,STRIDE,dtype=np.int64)
        t=t[t>=66]
        if len(t)*pos.shape[1]!=len(v22["Y"]["short"]):
            raise SourceStop("V24_AYU_V22_EXACT_SHORT_COHORT_STOP")
        samples[i]=source_age_panels(v22,pos,t,FPS,LAG)
    result=assess(samples,"ayu")
    result["source_pin_original_upstream_commit"]=PIN
    result["all_seven_original_Git_blobs_verified"]=True
    result["published_original_recording_filenames"]=list(FILES)
    result["native_original_hz"]=FPS
    result["source_mse_units"]="original numeric XY units/s squared, physical scale unknown"
    return result


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    args=p.parse_args()
    try:ans=run(args.root)
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as e:
        ans={"status":"SOURCE_OR_REPLAY_STOP","reason":str(e),
             "v24_original_fish_prediction":None}
    save_result("validation_fish_school_v24/results/ayu_age_curve.json",ans)
    print(json.dumps({"status":ans["status"],"reason":ans.get("reason"),
                      "results_by_horizon":ans.get("results_by_horizon")},sort_keys=True))


if __name__=="__main__":main()
