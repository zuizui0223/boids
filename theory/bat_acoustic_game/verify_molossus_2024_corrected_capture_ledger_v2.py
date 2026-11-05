"""Fail closed on source provenance and all original 2024 corrected bat records.

Recompute source original publisher supplement and all ten/nine bat heldout
results. Persist only pinned aggregate. Old 197566-exposure V1 invalid.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
from molossus_2024_source_capture_LOBO_corrected_v2 import run

ROOT=Path(__file__).resolve().parent
PIN=ROOT/"MOLOSSUS_2024_CORRECTED_CAPTURE_SOURCE_RESULTS_LEDGER_V2.json"
BLOBS={
 "verified_correction_source_code_git_blob_SHA":"molossus_2024_source_capture_LOBO_corrected_v2.py",
 "correction_preoutput_contract_git_blob_SHA":"MOLOSSUS_2024_CAPTURE_CORRECTED_EXPOSURE_V2_PREOUTPUT.md",
 "invented_tests_git_blob_SHA":"test_molossus_2024_capture_corrected_v2.py",
 "original_grain_audit_git_blob_SHA":"molossus_2024_exposure_grain_audit_v1.py"
}
def gitblob(path):
    b=(ROOT/path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def approx(a,b,tol=1e-12):
    assert math.isclose(float(a),float(b),rel_tol=1e-11,abs_tol=tol),(a,b)
def check_density(a,b):
    assert len(a)==len(b)==4
    for x,y in zip(a,b):
        assert x["density_bin"]==y["density_bin"]
        for k in ("rows","individual_bats","five_second_exposure","attacks","captures"):
            assert x[k]==y[k],(k,x[k],y[k])
        for k in ("capture_rate_per_5s","attacks_per_5s","capture_per_attack"):
            if k in x and x[k] is not None:approx(x[k],y[k])
def check_results(a,b):
    assert a["original_bat_independent_fold_count"]==b["original_bat_independent_fold_count"]
    assert a["n_original_5s_windows_total"]==b["n_original_5s_windows_total"]
    for m in ("M0","M1","M2"):
        s=a["source_model_scores"][m];t=b["source_model_scores"][m]
        assert s["source_model_evaluated_original_bats"]==t["source_model_evaluated_original_bats"]
        for metric in ("equal_bat_mean_capture_deviance_per_5s",
                       "median_source_bat_capture_deviance_per_5s",
                       "equal_bat_mean_capture_MAE_per_5s"):
            approx(s[metric],t[metric])
    for k in ("M1_minus_M0","M2_minus_M0","M2_minus_M1"):
        s=a["paired_bat_comparisons"][k];t=b["paired_bat_comparisons"][k]
        for metric in ("mean_bat_deviance_difference_per_5s",
                       "median_bat_deviance_difference_per_5s"):
            approx(s[metric],t[metric])
        for metric in ("source_bats_first_better","source_bats_second_better","source_bats_equal"):
            assert s[metric]==t[metric]
        for u,v in zip(s["whole_bat_bootstrap_95"],t["whole_bat_bootstrap_95"]):
            approx(u,v)
def main():
    freeze=json.loads(PIN.read_text())
    assert freeze["schema"]==2 and not freeze["new_bat_measurements"]
    for key,path in BLOBS.items():
        assert freeze[key]==gitblob(path),"SOURCE_CODE_OR_CONTRACT_CHANGED_"+path
    current=run()
    assert current["status"]=="CORRECTED_ORIGINAL_MOLOSSUS_2024_5S_SOURCE_BAT_LOBO"
    assert current["original_XLSX_SHA256"]==freeze["original_source_XLSX_SHA256"]
    assert current["original_PMC_supplement_zip_sha256"]==freeze["original_supplement_zip_SHA256"]
    assert current["source_data_quality"]==freeze["original_source_meta"]
    assert current["quarantined_prior_v1_due_to_wrong_exposure"]
    assert not current["new_animal_measurements"]
    assert current["no_original_bat_IDs_source_rows_or_sensitive_locations_released"]
    for source,pinned in (("primary_all_ten_source_bats","primary_all_10_original_bats"),
                          ("sensitivity_nine_source_time_consecutive_bats","sensitivity_9_complete_secgroup_bats")):
        a=current[source];b=freeze["cohorts"][pinned]
        assert a["source_original_bats"]==b["original_bats"]
        assert a["source_original_5s_rows"]==b["original_observed_5sec_rows"]
        check_density(a["density_exposure_support"],b["source_density_aggregate"])
        check_results(a["bat_LOBO_result"],b["source_bat_equal_holdout"])
    print("ORIGINAL_MOLOSSUS_10_AND_9_BAT_3_MODEL_SCORES_EXACTLY_REPLAYED")
    print("ORIGINAL_SOURCE_4299_OBSERVED_5S_WINDOWS_NOT_197566_INVALID")
    print("ORIGINAL_SOURCE_SHA",current["original_XLSX_SHA256"])
    print("SOURCE_NONCAUSAL_PUBLISHED_FORAGING_TRADEOFF_PRIOR_ART_PRESERVED")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
