"""v27 EIDC stickleback exact v26d three source-file cohort, source-only new metric."""
from __future__ import annotations
import hashlib,json
import numpy as np
from validation_fish_school_v26.eidc_source_only import BASE,FILE_LIMIT,fetch_bound
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v26.recording_age_forecast import SOURCE_IDS,read_source,build
from validation_fish_school_v27.group_velocity_correlation import (
    exact_group_correlation,record_result,save,SourceStop
)
FROZEN_COUNTS=(6966,8015,5567)

def run():
    out=[]
    for k,name in enumerate(SOURCE_IDS):
        raw=fetch_bound(BASE+name,FILE_LIMIT)
        sha,size=PINS[name]
        if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=sha:
            raise SourceStop("V27_STICKLEBACK_SOURCE_HASH_STOP")
        frame,pos=read_source(raw)
        original=build(pos)
        idx=np.arange(55,len(pos)-21,5,dtype=int)
        offsets=np.array([-55,-50,-30,-25,-15,-10,-5,0,5,15,20],dtype=int)
        idx=idx[np.isfinite(pos[idx[:,None]+offsets[None,:]]).all(axis=(1,2,3))]
        if len(idx)!=FROZEN_COUNTS[k] or len(idx)!=original["n_complete_source_frames"]:
            raise SourceStop("V27_STICKLEBACK_V26D_COHORT_REPLAY_STOP")
        r=exact_group_correlation(pos,idx,25.,5)
        out.append({"original_file":name,"original_SHA256":sha,**r})
    return record_result("stickleback",out,{
       "source":"MacGregor Ioannou 2021 EIDC DOI 10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
       "cohort":"exact v26d three source-file time rosters",
       "n_original_source_files":3,
       "n_independent_original_school_IDs":"NOT_KNOWN",
       "original_sha256_reauthenticated":True,
       "native_fps":25})

def main():
    try:r=run()
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as ex:
        r={"status":"SOURCE_OR_COHORT_STOP","reason":str(ex),
           "original_fish_correlation_result":None}
    save("validation_fish_school_v27/results/stickleback_group_correlation.json",r)
    print(json.dumps(r,sort_keys=True))

if __name__=="__main__":main()
