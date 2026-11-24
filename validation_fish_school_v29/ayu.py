"""v29 original Niizato ayu 7 files, common 200ms physical velocity interval."""
from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v9"))
from ayu_source_gate import FILES,PIN,blobsha
from ayu_global_local import source_data,STRIDE,LAG,DELAY_END
from validation_fish_school_v29.harmonized_group import (
    harmonized_group_correlation,aggregate,save,SourceStop)

def run(root):
    home=Path(root)
    if not (home/".git").is_dir():
        raise SourceStop("V29_ORIGINAL_AYU_PINNED_GIT_REQUIRED")
    base=home/"Compute_IIT/fish_revised"
    for name,(sha,n) in FILES.items():
        b=(base/name).read_bytes()
        if len(b)!=n or blobsha(b)!=sha:
            raise SourceStop("V29_ORIGINAL_AYU_GIT_BLOB_STOP")
    records=[]
    for name,(sha,n) in FILES.items():
        _,_,pos=source_data(base/name,sha,n)
        t=np.arange(2*LAG,len(pos)-DELAY_END,STRIDE)
        t=t[t>=66]
        m=harmonized_group_correlation(pos,t,30.)
        records.append({"original_file":name,"original_author_Git_blob_SHA":sha,**m})
    return aggregate("ayu",records,7,{
        "source":"Niizato et al. Scientific Reports 2024 seven original 10-ayu TXT",
        "source_pinned_original_commit":PIN,
        "original_author_Git_blobs_verified":True,
        "original_v27_source_roster":"replayed t>=66",
        "native_source_hz":30})

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    x=p.parse_args()
    try:obj=run(x.root)
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as exc:
        obj={"status":"SOURCE_OR_COHORT_STOP","reason":str(exc),"field_result":None}
    save("validation_fish_school_v29/results/ayu_harmonized.json",obj)
    print(json.dumps(obj,sort_keys=True))
if __name__=="__main__":main()
