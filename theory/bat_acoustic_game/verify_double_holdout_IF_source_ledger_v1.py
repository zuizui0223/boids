"""Re-download original public study and fail closed if 24 holdout cells drift.

No individual original bat IDs/calls, fitted per-bat parameters or raw source
records leave runtime memory. Source study outcomes already published.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
from double_holdout_IF_source_v1 import run

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"BAT_DOUBLE_HOLDOUT_IF_SOURCE_RESULTS_LEDGER_V1.json"
BLOBS={
    "preoutput_contract_blob_sha":"DOUBLE_HOLDOUT_IF_PREDICTION_PREOUTPUT_V1.md",
    "code_blob_sha":"double_holdout_IF_source_v1.py",
    "tests_blob_sha":"test_double_holdout_IF_source_v1.py"
}
METHODS=("median","mean")
EXPS=("IPIlow","IPIhigh","SPLlow")
MODELS=("zero","constant_training_mean","stimulus_linear",
        "fixed_bandwidth","trained_IF_TF_affine")
COMPARISONS=("stimulus_linear_vs_constant","stimulus_linear_vs_zero",
             "trained_TF_affine_vs_fixed_bandwidth","trained_TF_affine_vs_constant")

def gitblob(path):
    raw=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def near(a,b,tol=1e-6):
    assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol),(a,b)

def main():
    l=json.loads(LEDGER.read_text())
    assert l["schema"]==1
    for key,filename in BLOBS.items():
        assert l[key]==gitblob(ROOT/filename),"FROZEN_SOURCE_OR_TEST_BLOB_CHANGED "+key
    source=run()
    assert source["status"]=="SOURCE_DOUBLE_HOLDOUT_EVALUATED"
    assert source["source_SHA256"]==l["source_original_csv_sha256"]
    assert source["original_source_rows"]==l["source_original_rows"]==12308
    assert not source["novel_animal_measurements"] and source["individual_BAT_IDs_and_original_pulse_rows_not_exported"]
    assert set(source["cases"])==set(l["source_results_by_window_method_experiment"])
    checked=0
    for window,case in source["cases"].items():
        assert case["n_source_rows_in_policy"]==l["windows_source_row_count"][window]
        for method,group in case["source_models"].items():
            assert method in METHODS
            for experiment,result in group["experiments"].items():
                assert experiment in EXPS
                frozen=l["source_results_by_window_method_experiment"][window][method][experiment]
                counts=frozen["support"]
                assert result["status"]==counts["status"]=="EVALUATED"
                assert result["eligible_bats"]==counts["bats"]==7
                assert result["n_evaluated_original_bat_condition_folds"]==counts["folds"]==35
                assert result["training_cell_count_min_max"]==[counts["train_min"],counts["train_max"]]==[24,24]
                assert set(result["models"])==set(MODELS)
                for model,metrics in result["models"].items():
                    near(metrics["equal_bat_MAE_khz"],frozen["MAE_khz"][model])
                    assert metrics["n_unique_source_bats"]==7
                    assert metrics["n_source_bat_condition_test_pairs"]==35
                assert set(result["comparisons"])==set(COMPARISONS)
                for comparison,values in result["comparisons"].items():
                    wanted=frozen["comparisons"][comparison]
                    near(values["mean_delta_MAE_khz"],wanted["delta_MAE_khz"])
                    assert values["source_bats_for_first_model"]==wanted["bat_better"]
                    assert values["source_bats_for_second_model"]==wanted["bat_worse"]
                    for a,b in zip(values["whole_bat_bootstrap_mean_delta_95_khz"],
                                   wanted["bat_bootstrap95"]):
                        near(a,b,1e-9)
                checked+=1
    assert checked==24
    signs=[l["source_results_by_window_method_experiment"][w][m][e]["comparisons"]
           ["stimulus_linear_vs_constant"]["delta_MAE_khz"]
           for w in l["source_results_by_window_method_experiment"]
           for m in METHODS for e in EXPS]
    assert sum(x>0 for x in signs)==18 and sum(x<0 for x in signs)==6
    print("DOUBLE_HOLDOUT_FRESH_ORIGINAL_DATA_ALL_24_GROUPS_120_MODELS_MATCH")
    print("PRIMARY_SOURCE_LOW_IPI_STIMULUS_LINEAR_WORSE_THAN_BASELINE")
    print("18_OF_24_SOURCE_REUSED_SENSITIVITY_CELLS_STIMULUS_MODEL_WORSE")
    print("MODEL_INPUTS_SEPARATED_FORWARD_VS_TF_CONDITIONAL")
    print("NO_NEW_BAT_MEASUREMENT_NO_ORIGINAL_BAT_ID_RELEASE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
