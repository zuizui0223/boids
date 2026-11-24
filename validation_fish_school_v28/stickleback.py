"""v28 third-taxon EIDC stickleback three preselected original FILES only.

Not verified independent shoals. No fish future target model or calls.
"""
from __future__ import annotations
import json,hashlib
from validation_fish_school_v26.eidc_source_only import BASE,FILE_LIMIT,fetch_bound
from validation_fish_school_v26.source_semantics import PINS
from validation_fish_school_v26.recording_age_forecast import SOURCE_IDS,read_source,build
from validation_fish_school_v28.conditional_residual import source_panels,assess,save,SourceStop

FROZEN_COUNTS=(6966,8015,5567)

def run():
    cases={}
    for j,name in enumerate(SOURCE_IDS):
        raw=fetch_bound(BASE+name,FILE_LIMIT)
        sha,size=PINS[name]
        if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=sha:
            raise SourceStop("V28_EIDC_ORIGINAL_SHA_STOP")
        f,pos=read_source(raw)
        source=build(pos)
        if source["n_complete_source_frames"]!=FROZEN_COUNTS[j]:
            raise SourceStop("V28_EIDC_V26D_COHORT_REPLAY_STOP")
        cases[name]=source_panels(source["X"],geometry="G_geometry")
    return assess(cases,"stickleback",{
        "source":"MacGregor Ioannou 2021 EIDC original three preselected stickleback 8-fish files",
        "source_files":list(SOURCE_IDS),
        "source_schools":"UNVERIFIED",
        "native_fps":25,
        "original_sha256":{name:PINS[name][0] for name in SOURCE_IDS},
        "frozen_complete_native_source_times":list(FROZEN_COUNTS),
        "target_fish_future_velocities_used":False})

def main():
    try:obj=run()
    except (SourceStop,ValueError,IndexError,KeyError,OSError) as ex:
        obj={"status":"SOURCE_OR_NUISANCE_SUPPORT_STOP","reason":str(ex),"field_effect":None}
    save("validation_fish_school_v28/results/stickleback_conditional_residual.json",obj)
    print(json.dumps(obj,sort_keys=True))
if __name__=="__main__":main()
