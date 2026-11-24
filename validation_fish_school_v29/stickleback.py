"""v29 original stickleback 25Hz source cohort, 200ms already equals native v27."""
from __future__ import annotations
import hashlib,json
import numpy as np
from validation_fish_school_v26.eidc_source_only import BASE,FILE_LIMIT,fetch_bound,SourceStop as SourceAccessStop
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v26.recording_age_forecast import SOURCE_IDS,read_source,build
from validation_fish_school_v29.harmonized_group import (
 harmonized_group_correlation,aggregate,save,SourceStop)
COUNTS=(6966,8015,5567)

def run():
    rec=[]
    for i,name in enumerate(SOURCE_IDS):
        blob=fetch_bound(BASE+name,FILE_LIMIT)
        sha,size=PINS[name]
        if len(blob)!=size or hashlib.sha256(blob).hexdigest()!=sha:
            raise SourceStop("V29_ORIGINAL_EIDC_SHA256_MISMATCH_STOP")
        frame,pos=read_source(blob)
        ref=build(pos)
        idx=np.arange(55,len(pos)-21,5)
        offsets=np.array([-55,-50,-30,-25,-15,-10,-5,0,5,15,20],dtype=int)
        idx=idx[np.isfinite(pos[idx[:,None]+offsets[None,:]]).all(axis=(1,2,3))]
        if len(idx)!=COUNTS[i] or len(idx)!=ref["n_complete_source_frames"]:
            raise SourceStop("V29_EIDC_V26D_SOURCE_ROSTER_DRIFT")
        m=harmonized_group_correlation(pos,idx,25.)
        rec.append({"original_file":name,"source_SHA256":sha,**m})
    return aggregate("stickleback",rec,3,{
        "source":"MacGregor Ioannou 2021 EIDC three original Gasterosteus source files",
        "source_original_SHA256_verified":True,
        "source_file_count":3,
        "original_shoal_ID_crosswalk":"NOT_VERIFIED",
        "native_source_hz":25,
        "original_v26d_source_roster":"replayed 6966/8015/5567"})

def main():
    try:obj=run()
    except (SourceStop,SourceAccessStop,OSError,ValueError,IndexError,KeyError) as exc:
        obj={"status":"SOURCE_OR_COHORT_STOP","reason":str(exc),"field_result":None}
    save("validation_fish_school_v29/results/stickleback_harmonized.json",obj)
    print(json.dumps(obj,sort_keys=True))
if __name__=="__main__":main()
