"""Recompute original-source self/donor scores; fail closed on ledger drift.

Original source bat ID, audio rows, time stamps stay only in ephemeral memory.
The 24 source summaries reuse the same 11 original bats; not independent n24.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
from self_vs_donor_bat_source_v1 import run

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"BAT_SELF_VS_DONOR_SOURCE_EQUAL_TRAINING_LEDGER_V1.json"
BLOBS={
 "preoutput_contract_original_blob_sha":"SELF_VS_DONOR_EQUAL_FOUR_CONDITIONS_PREOUTPUT_V1.md",
 "analysis_source_code_blob_sha":"self_vs_donor_bat_source_v1.py",
 "invented_unit_tests_source_blob_sha":"test_self_vs_donor_bat_source_v1.py"
}
MODELS=("self_constant","other_constant","self_linear","other_linear")
DIFFS=("self_constant_minus_donor_constant",
       "self_linear_minus_donor_linear",
       "self_linear_minus_self_constant")

def gitblob(path):
    b=(ROOT/path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def near(a,b,tol=1e-6):
    assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol),(a,b)

def main():
    pinned=json.loads(LEDGER.read_text())
    assert pinned["schema"]==1
    for k,p in BLOBS.items():
        assert pinned[k]==gitblob(p),"ORIGINAL SOURCE OR DESIGN FILE CHANGED "+p
    now=run()
    assert now["schema"]==1
    assert now["status"]=="SOURCE_SECONDARY_SELF_VS_DONOR_EVALUATED"
    assert now["source_original_sha256"]==pinned["original_source_SHA256"]
    assert now["original_source_row_count"]==pinned["original_rows"]==12308
    assert not now["new_bat_measurements"]
    assert not now["original_source_animal_IDs_or_pulses_exported"]
    examined=0
    for window,part in now["source_model_groups"].items():
        stored=pinned["source_data_groups"][window]
        for method,response in part["source_responses"].items():
            saved=stored[method]
            for experiment,cells in response["experiments"].items():
                sample=saved[experiment]
                assert cells["status"]==sample["support"]["status"]=="SUPPORTED_ORIGINAL_SOURCE_GROUP"
                assert cells["biological_bat_count"]==sample["support"]["bats"]==7
                assert cells["source_test_bat_condition_cells"]==sample["support"]["test_cells"]==35
                assert cells["donor_bats_compared_per_test"]==6
                assert cells["one_model_source_level_training_count"]==4
                assert set(cells["models"])==set(MODELS)
                for model,x in cells["models"].items():
                    near(x["mean_bat_equal_condition_MAE_khz"],sample["MAE_khz"][model])
                assert set(cells["comparison"])==set(DIFFS)
                for key,val in cells["comparison"].items():
                    savedval=sample["comparisons"][key]
                    near(val["equal_bat_mean_error_difference_khz"],savedval["delta_MAE_khz"])
                    assert val["bats_first_model_better"]==savedval["bats_first_better"]
                    assert val["bats_second_model_better"]==savedval["bats_second_better"]
                    for x,y in zip(val["whole_bat_bootstrap_mean_95_khz"],
                                   savedval["bat_bootstrap95"]):
                        near(x,y,tol=1e-9)
                examined+=1
    assert examined==24
    assert len(now["source_model_groups"])==4
    originals=pinned["summary"]
    assert originals["source_experiment_window_summary_cells"]==24
    diffs=[cell["comparisons"]["self_linear_minus_self_constant"]["delta_MAE_khz"]
           for w in pinned["source_data_groups"].values()
           for m in w.values() for cell in m.values()]
    assert len(diffs)==24 and all(x>0 for x in diffs)
    print("BAT_SELF_VS_DONOR_24_CELLS_96_MODEL_ERRORS_MATCH_ORIGINAL_SOURCE")
    print("EQUAL_FOUR_TRAINING_CONDITIONS_SIX_DONORS_FIXED")
    print("SELF_LINEAR_WORSE_THAN_SELF_MEAN_IN_24_OF_24_REUSED_SOURCE_CELLS")
    print("SAME_11_SOURCE_BATS_NOT_24_INDEPENDENT_STUDIES")
    print("SOURCE_ORIGINAL_SHA",pinned["original_source_SHA256"])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
