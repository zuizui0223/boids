"""v28 Niizato ayu seven source recordings: target-free group innovation persistence."""
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
from ayu_global_local import source_data,FPS,LAG,STRIDE,DELAY_END
from ayu import ayu_one
from age_curve import source_age_panels
from validation_fish_school_v28.conditional_residual import source_panels,assess,save

def run(root):
    root=Path(root)
    if not (root/".git").exists():
        raise SourceStop("V28_AYU_PINNED_GIT_REQUIRED")
    base=root/"Compute_IIT/fish_revised"
    for name,(sha,size) in FILES.items():
        data=(base/name).read_bytes()
        if len(data)!=size or blobsha(data)!=sha:
            raise SourceStop("V28_AYU_ORIGINAL_BLOB_AUTHENTICATION_STOP")
    groups={}
    for name,(sha,size) in FILES.items():
        path=base/name
        _,_,pos=source_data(path,sha,size)
        previous=ayu_one(path,sha,size)
        t=np.arange(2*LAG,len(pos)-DELAY_END,STRIDE,dtype=np.int64)
        t=t[t>=66]
        source=source_age_panels(previous,pos,t,FPS,LAG)
        groups[name]=source_panels(source["X"]["short"])
    return assess(groups,"ayu",{
       "source":"Niizato et al. Scientific Reports 2024 original seven 10-fish TXT",
       "original_git_commit":PIN,"all_seven_original_git_blobs_verified":True,
       "native_fps":FPS,"source_cohort":"v24 original fixed source t>=66",
       "target_fish_future_velocities_used":False})

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    args=p.parse_args()
    try:obj=run(args.root)
    except (SourceStop,ValueError,IndexError,KeyError,OSError) as ex:
        obj={"status":"SOURCE_OR_NUISANCE_SUPPORT_STOP","reason":str(ex),"field_effect":None}
    save("validation_fish_school_v28/results/ayu_conditional_residual.json",obj)
    print(json.dumps(obj,sort_keys=True))
if __name__=="__main__":main()
