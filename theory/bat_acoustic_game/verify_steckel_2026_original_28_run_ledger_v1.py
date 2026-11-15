"""Compare all 28 official author virtual-3D metrics against pinned ledger.

Re-download ONLY source_data/run_table.json + experiments.json by original
Zenodo byte ranges; authenticate SHA/CRC and source original experiment IDs.
Does not run author's optimizer or inspect neural weights/echo datasets.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
from steckel_2026_original_28_run_comparison_v1 import run as source_run

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"STECKEL_2026_ORIGINAL_28_RUN_SOURCE_NUMERIC_LEDGER_V1.json"
BLOBS=(
 "steckel_2026_original_28_run_comparison_v1.py",
 "STECKEL_2026_ORIGINAL_3D_OBSERVABILITY_SOURCE_RESULT_CONTRACT_V1.md",
 "test_steckel_2026_original_28_run_comparison_v1.py"
)
def gitblob(p):
    b=(ROOT/p).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def equal(a,b,what):
    if a is None or b is None:
        assert a is b,(what,a,b)
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(what,a,b)
    else:assert a==b,(what,a,b)

def main():
    pinned=json.loads(LEDGER.read_text())
    assert pinned["schema"]==1 and pinned["original_runs_count"]==28
    for f in BLOBS:
        assert pinned["code_blob_sha"][f]==gitblob(f),"SCRIPT_OR_SCIENCE_CONTRACT_CHANGED "+f
    original=source_run()
    assert original["schema"]==1
    assert original["status"]=="ORIGINAL_AUTHOR_28_SIMULATED_3D_MOVEMENT_RUNS_ALL_JOINED"
    assert original["source_metrics_original_sha256"]==pinned["original_source_file_sha256"]["source_data/run_table.json"]
    assert original["source_experiment_index_original_sha256"]==pinned["original_source_file_sha256"]["experiments.json"]
    assert not original["new_field_or_lab_bat_measurements"]
    assert not original["authentic_original_bat3d_Python_model_executed"]
    assert not original["individual_live_bat_3D_tracks_read"]
    assert not original["author_original_28_numeric_run_count"]!=28
    assert len(original["author_all_original_run_results"])==28
    for recorded in pinned["per_run_original_author_metrics"]:
        key=recorded["name"];original_entry=original["author_all_original_run_results"][key]
        equal(original_entry["author_experiment"],recorded["exp"],key+"/experiment")
        equal(original_entry["source_evaluation_n"],recorded["source_n"],key+"/n")
        equal(original_entry["original_train_step"],recorded["training_step"],key+"/step")
        assert set(original_entry["author_original_scalar_metrics"])==set(recorded["metrics"])
        for metric,val in recorded["metrics"].items():
            equal(original_entry["author_original_scalar_metrics"][metric],val,key+"/"+metric)
    assert sorted(original["author_all_original_run_results"])==sorted(x["name"] for x in pinned["per_run_original_author_metrics"])
    def compare(name,key1,key0,metric):
        a=original["author_all_original_run_results"]
        d=a[key1]["author_original_scalar_metrics"][metric]-a[key0]["author_original_scalar_metrics"][metric]
        equal(pinned["source_condition_descriptive_differences"][name][metric+"_diff"],d,name)
    compare("main_vs_shuffled","smooth_ctrl_shuffle","smooth_online_b64","az")
    compare("main_vs_shuffled","smooth_ctrl_shuffle","smooth_online_b64","el")
    compare("main_vs_no_prediction","smooth_ctrl_nomotion","smooth_online_b64","az")
    compare("main_vs_no_prediction","smooth_ctrl_nomotion","smooth_online_b64","el")
    compare("fixed_head_vs_main","smooth_ctrl_fixedhead","smooth_online_b64","az")
    compare("fixed_head_vs_main","smooth_ctrl_fixedhead","smooth_online_b64","el")
    compare("pan_only_vs_pan_tilt","smooth_axis_pan","smooth_axis_pantilt","az")
    compare("pan_only_vs_pan_tilt","smooth_axis_pan","smooth_axis_pantilt","el")
    compare("sparse_vs_specular_room","smooth_room","smooth_sparse","az")
    compare("sparse_vs_specular_room","smooth_room","smooth_sparse","el")
    compare("memory_512_vs_64","smooth_online_b512","smooth_online_b64","az")
    compare("memory_512_vs_64","smooth_online_b512","smooth_online_b64","el")
    s=original["author_all_original_run_results"]
    equal(pinned["source_condition_descriptive_differences"]["pan_only_vs_pan_tilt"]["el_ratio"],
          s["smooth_axis_pan"]["author_original_scalar_metrics"]["el"]/s["smooth_axis_pantilt"]["author_original_scalar_metrics"]["el"],
          "pan_only_vs_pan_tilt el_ratio")
    print("ORIGINAL_AUTHOR_28_SOURCE_RUNS_ALL_6_METRICS_AND_N_STEP_MATCH")
    print("ORIGINAL_AUTHOR_COMPARE_ALL_PREDEFINED_AXES_CONTROLS_MEMORY_SPECULAR_SOURCE_METRICS_MATCH")
    print("PUBLISHER_SOURCE_SHA_AND_RESEARCH_CONTRACT_SAME")
    print("SIMULATED_BAT3D_SOURCE_ONLY_NO_NEW_BATS_NO_ORIGINAL_PYTHON_OPTIMIZER_RUN")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
