"""Fail-closed replay of published IF/TF source evidence ledger, only aggregates.

Fetches ONLY the already-public original Figshare table during GitHub Actions;
never commits bat IDs, source rows, or exact stimulus timestamps.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path

from published_IF_TF_convention_v1 import run as original_if_tf
from IF_TF_temporal_window_sensitivity_v1 import run as time_window_if_tf
from IF_TF_source_timing_audit_v1 import run as source_time_structure

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"IF_TF_SOURCE_TIME_PHYSICAL_CONVENTION_LEDGER_V1.json"
BLOBS={
    "IF_TF_SOURCE_MAIN_SOURCE_GITBLOB":"published_IF_TF_convention_v1.py",
    "SOURCE_WINDOW_SCRIPT_GITBLOB":"IF_TF_temporal_window_sensitivity_v1.py",
    "SOURCE_TIME_DESIGN_SCRIPT_GITBLOB":"IF_TF_source_timing_audit_v1.py",
    "PREOUTPUT_CONTRACT_GITBLOB":"PUBLISHED_IF_TF_PHYSICAL_CONVENTION_PREOUTPUT_V1.md",
    "POSTOUTCOME_TIME_WINDOW_DESIGN_GITBLOB":"IF_TF_TEMPORAL_SENSITIVITY_POSTOUTCOME_DESIGN_V1.md",
}

def git_blob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def eq(a,b):
    if a is None or b is None:
        assert a is b,(a,b)
    else:
        assert math.isclose(float(a),float(b),abs_tol=1e-10,rel_tol=1e-10),(a,b)

def audit_cell(record,stored,experiment):
    assert record["n_bats"]==stored["n_bats"]==7,(experiment,record.get("n_bats"))
    assert record["n_bat_condition_cells"]==stored["n_bat_condition_cells"]==35
    assert record["source_bats_favor_fixed_start"]==stored["start_favored_bats"]
    assert record["source_bats_favor_fixed_bandwidth"]==stored["bandwidth_favored_bats"]
    eq(record["mean_D_bandwidth_minus_start_khz"],stored["D_bandwidth_minus_start_khz"])
    for x,y in zip(record["mean_D_whole_bat_bootstrap95_khz"],stored["whole_bat_bootstrap_95_khz"]):
        eq(x,y)


def main():
    ledger=json.loads(LEDGER.read_text())
    for key,filename in BLOBS.items():
        assert ledger[key]==git_blob(ROOT/filename),(key,"blob changed")
    original=original_if_tf()
    timing=source_time_structure()
    sensitivity=time_window_if_tf()
    expectedsha=ledger["source_file_sha256"]
    assert ledger["schema"]==1
    assert original["source"]["sha256"]==sensitivity["source_sha256"]==timing["source_sha256"]==expectedsha
    assert not original["new_bat_observations"]
    assert not sensitivity["new_bat_measurements"]
    assert not timing["new_bat_measurements"]
    assert original["source_quality"]["rows_inspected"]==timing["result"]["source_original_rows"]==sensitivity["source_original_rows"]==ledger["source_original_rows"]==12308
    assert timing["result"]["source_bats_total_unique"]==ledger["source_unique_original_bat_ID_labels"]==11
    assert timing["result"]["source_bats_by_experiment"]==ledger["source_experiment_bat_ID_counts"]
    assert timing["result"]["source_bat_overlaps_by_experiment"]==ledger["source_experiment_cross_ID_intersections"]
    sourcecontexts=timing["result"]["supported_context_time_range_diagnostics"]
    assert sum(x["all_OFF_before_ON"] for x in sourcecontexts.values())==ledger["source_contexts_with_OFF_before_ON"]==105
    assert sum(x.get("time_ranges_overlapping",0) for x in sourcecontexts.values())==ledger["source_contexts_with_nonchronological_overlap"]==0

    full=ledger["analyses"]["full"]
    srcview={"median":original["medians_primary"],"mean":original["means_sensitivity"]}
    for method,view in srcview.items():
        for e,expected in full[method].items():
            audit_cell(view["experiments"][e],expected,"full-"+method+"-"+e)
    for name,output in sensitivity["windows"].items():
        block=ledger["analyses"][name]
        assert block["rows"]==output["retained_original_source_rows"],(name,"source rows changed")
        for method,source_key in (("median","medians"),("mean","means_sensitivity")):
            for e,expected in block[method].items():
                audit_cell(output[source_key]["experiments"][e],expected,name+"-"+method+"-"+e)

    for e,expected in ledger["original_experiment_source_full_median_absolute_errors_khz"].items():
        row=original["medians_primary"]["experiments"][e]
        eq(row["equal_bat_mean_absolute_error_fixed_start_khz"],expected["start"])
        eq(row["equal_bat_mean_absolute_error_fixed_bandwidth_khz"],expected["bandwidth"])
        eq(row["equal_bat_mean_delta_IF_khz"],expected["mean_deltaIF"])
        eq(row["equal_bat_mean_delta_TF_khz"],expected["mean_deltaTF"])

    print("IF_TF_ALL_24_SOURCE_CASES_FRESH_REPLAY_MATCH",4*2*3)
    print("ORIGINAL_SOURCE_SHA",expectedsha)
    print("CHRONOLOGY_ALL_105_CONTEXTS_OFF_BEFORE_ON")
    print("BIOLOGICAL_UNITS_11_UNIQUE_SOURCE_BATS")
    print("SECONDARY_SOURCE_ONLY_NO_CAUSAL_OR_NEW_ANIMAL_CLAIM")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
