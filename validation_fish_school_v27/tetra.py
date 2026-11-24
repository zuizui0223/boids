"""v27 Puy original 6 records: whole-school velocity correlation, no motion forecast."""
from __future__ import annotations
import sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for d in ("validation_fish_school_v5","validation_fish_school_v8"):
    sys.path.insert(0,str(ROOT/d))
from source_inventory import read_json,ZENODO
from trajectory_source_gate import RECORDINGS,download_and_audit
from forecast_transfer import source_csv,make_trial
from assignment_and_delay import original_indices
from validation_fish_school_v27.group_velocity_correlation import (
    exact_group_correlation,record_result,save,SourceStop
)

def run():
    meta=read_json(ZENODO)
    files={x.get("key"):x for x in meta.get("files",[]) if isinstance(x,dict)}
    if not set(RECORDINGS).issubset(files):
        raise SourceStop("V27_TETRA_SOURCE_FILE_LIST_STOP")
    with tempfile.TemporaryDirectory(prefix="v27_puy_") as d:
        original={name:download_and_audit(files[name],Path(d)/name)
                  for name in RECORDINGS}
        results=[]
        for i,name in enumerate(RECORDINGS):
            frame,pos=source_csv(Path(d)/name)
            v5=make_trial(frame,pos,i)
            idx=original_indices(frame,pos)
            if len(idx)*8!=len(v5["Y"]):
                raise SourceStop("V27_TETRA_V24_SOURCE_TIME_ROSTER_STOP")
            r=exact_group_correlation(pos,idx,50.,5)
            results.append({"original_file":name,
                "source_SHA256":original[name]["sha256"],**r})
        return record_result("tetra",results,{
            "source":"Puy et al. 2024 PNAS, Zenodo 10890112",
            "all_six_original_provider_md5_verified":True,
            "cohort":"original v24 Puy short source time roster",
            "n_original_source_files":6,
            "native_fps":50})

def main():
    try:r=run()
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as ex:
        r={"status":"SOURCE_OR_COHORT_STOP","reason":str(ex),
           "original_fish_correlation_result":None}
    save("validation_fish_school_v27/results/tetra_group_correlation.json",r)
    print(__import__("json").dumps(r,sort_keys=True))

if __name__=="__main__":main()
