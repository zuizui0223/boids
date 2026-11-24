"""v29 Puy original tetra 6 recordings, frozen v27 roster, common 200ms speed."""
from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in ("validation_fish_school_v5","validation_fish_school_v8"):
    sys.path.insert(0,str(ROOT/p))
from source_inventory import read_json,ZENODO
from trajectory_source_gate import RECORDINGS,download_and_audit
from forecast_transfer import source_csv,make_trial
from assignment_and_delay import original_indices
from validation_fish_school_v29.harmonized_group import (
   harmonized_group_correlation,aggregate,save,SourceStop)

def run():
    metadata=read_json(ZENODO)
    table={a.get("key"):a for a in metadata.get("files",[]) if isinstance(a,dict)}
    if not set(RECORDINGS).issubset(table):raise SourceStop("V29_PUY_SOURCE_MANIFEST_STOP")
    with tempfile.TemporaryDirectory(prefix="v29_original_Puy_") as d:
        receipts={n:download_and_audit(table[n],Path(d)/n) for n in RECORDINGS}
        rec=[]
        for i,name in enumerate(RECORDINGS):
            frame,pos=source_csv(Path(d)/name)
            old=make_trial(frame,pos,i)
            idx=original_indices(frame,pos)
            if len(idx)*8!=len(old["Y"]):
                raise SourceStop("V29_PUY_PREVIOUS_COHORT_REPLAY_STOP")
            cor=harmonized_group_correlation(pos,idx,50.)
            rec.append({"original_file":name,
                        "source_sha256":receipts[name]["sha256"],**cor})
        return aggregate("tetra",rec,6,{
           "source":"Puy et al. PNAS 2024 original Zenodo six 8-fish source files",
           "all_original_provider_MD5_verified":True,
           "original_v27_fixed_source_index":"replayed",
           "native_source_hz":50})

def main():
    try:obj=run()
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as exc:
        obj={"status":"SOURCE_OR_COHORT_STOP","reason":str(exc),"field_result":None}
    save("validation_fish_school_v29/results/tetra_harmonized.json",obj)
    print(json.dumps(obj,sort_keys=True))
if __name__=="__main__":main()
