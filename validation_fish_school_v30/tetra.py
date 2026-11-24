"""v30 original source Puy tetra: fully common physical 200ms movement model."""
from __future__ import annotations
import json,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
from source_inventory import read_json,ZENODO
from trajectory_source_gate import RECORDINGS,download_and_audit,SourceStop as OriginalSourceStop
from forecast_transfer import source_csv
from validation_fish_school_v30.harmonized_forecast import (
    build_original_recording,evaluate_source_files,save,SourceStop)

def run():
    meta=read_json(ZENODO)
    available={f.get("key"):f for f in meta.get("files",[]) if isinstance(f,dict)}
    if len(RECORDINGS)!=6 or not set(RECORDINGS).issubset(available):
        raise SourceStop("V30_PUY_ZENODO_SOURCE_MANIFEST_STOP")
    with tempfile.TemporaryDirectory(prefix="v30_puy_original_") as directory:
        # Every provider original file authenticated BEFORE opening any positions.
        checks={name:download_and_audit(available[name],Path(directory)/name)
                for name in RECORDINGS}
        cases={}
        for name in RECORDINGS:
            frame,pos=source_csv(Path(directory)/name)
            cases[name]=build_original_recording(frame,pos,50,name)
        out=evaluate_source_files(cases,"tetra",6,
                "Puy et al. 2024 PNAS 8 black neon tetra, Zenodo 10890112")
        out["source_authentication"]={"all_original_provider_MD5_pass":True,
             "per_original_file_SHA256":{name:checks[name]["sha256"] for name in RECORDINGS},
             "original_file_names":list(RECORDINGS),
             "original_numeric_units":"cm/sec and (cm/sec)^2 MSE"}
        return out

def main():
    try:out=run()
    except (SourceStop,OriginalSourceStop,OSError,ValueError,IndexError,KeyError) as e:
        out={"status":"SOURCE_OR_MODEL_STOP","reason":str(e),"new_observed_fish_result":None}
    save("validation_fish_school_v30/results/tetra_common_model.json",out)
    print(json.dumps({"status":out["status"],"reason":out.get("reason"),
                      "results_by_horizon":out.get("results_by_horizon"),
                      "source_file_cohorts":out.get("original_source_cohort")},sort_keys=True))
if __name__=="__main__":main()
