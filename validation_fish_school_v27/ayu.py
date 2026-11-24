"""v27 Niizato original 7 recording ayu group-state autocorrelation only."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v9"))
from ayu_source_gate import FILES,PIN,blobsha
from ayu_global_local import source_data,STRIDE,LAG,DELAY_END
from validation_fish_school_v27.group_velocity_correlation import (
    exact_group_correlation,record_result,save,SourceStop
)

def run(root):
    base=Path(root)/"Compute_IIT/fish_revised"
    if not (Path(root)/".git").is_dir():
        raise SourceStop("V27_AYU_PINNED_AUTHOR_GIT_CHECKOUT_STOP")
    for name,(sha,size) in FILES.items():
        raw=(base/name).read_bytes()
        if len(raw)!=size or blobsha(raw)!=sha:
            raise SourceStop("V27_AYU_SOURCE_BLOB_STOP")
    result=[]
    for name,(sha,size) in FILES.items():
        _,_,pos=source_data(base/name,sha,size)
        idx=np.arange(2*LAG,len(pos)-DELAY_END,STRIDE)
        idx=idx[idx>=66]
        m=exact_group_correlation(pos,idx,30.,3)
        result.append({"original_file":name,"original_Git_blob_SHA":sha,**m})
    return record_result("ayu",result,{
        "source":"Niizato et al. 2024 Sci Rep original Git",
        "all_seven_original_Git_blobs_verified":True,
        "pinned_git_commit":PIN,
        "cohort":"v24 ayu 2-second history t>=66",
        "n_original_source_files":7,"native_fps":30})

def main():
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    args=p.parse_args()
    try:r=run(args.root)
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as ex:
        r={"status":"SOURCE_OR_COHORT_STOP","reason":str(ex),
           "original_fish_correlation_result":None}
    save("validation_fish_school_v27/results/ayu_group_correlation.json",r)
    print(json.dumps(r,sort_keys=True))

if __name__=="__main__":main()
