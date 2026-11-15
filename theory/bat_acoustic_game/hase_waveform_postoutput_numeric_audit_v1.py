"""Post-output NUMERICAL audit: off-grid fixture and full exact-correlation replay.

This repairs one audit-design error in the earlier v2: all selected checks were
grid aligned, so error was exactly zero by construction. The v2 source law,
4 worlds, waveforms and source timing are not modified or retuned.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import math
import source_timing_waveform_v2 as v2

OUT=Path(__file__).resolve().parent/"HASE_WAVEFORM_V2_POSTOUTPUT_NUMERIC_AUDIT_V1.json"

def blob_sha(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()

def offgrid():
    rows=[]
    anchors=(47.413,48.017,49.193)
    diffs=(.307,.713,1.013,2.037,3.053,4.079,5.091)
    for curve in v2.CURVES:
        for f0 in anchors:
            for d in diffs:
                a=v2.get_correlations(curve,f0,f0+d,force_exact=False)
                b=v2.get_correlations(curve,f0,f0+d,force_exact=True)
                row={"curve":curve,"start_khz":f0,"delta_khz":d,
                     "max_abs_error":max(abs(x-y) for x,y in zip(a,b)),
                     "classification_mismatch":sum((x>v2.CORRELATION_CUTOFF)!=(y>v2.CORRELATION_CUTOFF)
                                               for x,y in zip(a,b))}
                rows.append(row)
    return {"n_non_grid_fixtures":len(rows),
            "max_absolute_error":max(x["max_abs_error"] for x in rows),
            "n_classification_mismatch":sum(x["classification_mismatch"] for x in rows),
            "n_violate_0p025_limit":sum(x["max_abs_error"]>.025 for x in rows)}

def run():
    fix=offgrid()
    worlds=[]
    for n in (4,8):
        for scale in (.7,3.):
            times=v2.source_schedules(n,scale)
            _,arrivals=v2.source_receiver_drive(n,scale,times)
            no=v2.source_tf_traces(n,scale,times,False)
            yes=v2.source_tf_traces(n,scale,times,True)
            for shape in v2.CURVES:
                # Both paths use identical synthetic opportunities/sounds; only
                # the waveform numerical cross-correlation algorithm differs.
                binned0=v2.evaluate_world(n,scale,shape,times,arrivals,no,force_exact=False)
                binned1=v2.evaluate_world(n,scale,shape,times,arrivals,yes,force_exact=False)
                exact0=v2.evaluate_world(n,scale,shape,times,arrivals,no,force_exact=True)
                exact1=v2.evaluate_world(n,scale,shape,times,arrivals,yes,force_exact=True)
                assert binned0["focal_emissions"]==exact0["focal_emissions"]
                assert binned1["focal_emissions"]==exact1["focal_emissions"]
                assert binned0["eligible_other_bat_pulses"]==exact0["eligible_other_bat_pulses"]
                assert binned1["eligible_other_bat_pulses"]==exact1["eligible_other_bat_pulses"]
                delta_cache=binned1["lag_per_focal"]-binned0["lag_per_focal"]
                delta_exact=exact1["lag_per_focal"]-exact0["lag_per_focal"]
                worlds.append({"n":n,"scale":scale,"waveform":shape,
                    "n_focal_emissions":exact0["focal_emissions"],
                    "n_eligible_other_pulses":exact0["eligible_other_bat_pulses"],
                    "binned_lag_per_focal_no_JAR":binned0["lag_per_focal"],
                    "binned_lag_per_focal_JAR":binned1["lag_per_focal"],
                    "exact_lag_per_focal_no_JAR":exact0["lag_per_focal"],
                    "exact_lag_per_focal_JAR":exact1["lag_per_focal"],
                    "binned_delta_lag":delta_cache,"exact_delta_lag":delta_exact,
                    "difference_in_delta_lag":delta_exact-delta_cache,
                    "n_exact_lag_labels_changed_no_JAR":exact0["lag_count"]-binned0["lag_count"],
                    "n_exact_lag_labels_changed_JAR":exact1["lag_count"]-binned1["lag_count"],
                    "exact_delta_zero_lag":exact1["zero_per_focal"]-exact0["zero_per_focal"]})
    return {"schema":1,"status":"POST_OUTCOME_SOURCE_UNCHANGED_NUMERICAL_AUDIT",
            "new_animal_measurements":False,
            "source_2026_group_reproduced":False,
            "source_original_code_git_blob_sha":blob_sha(v2.__file__),
            "fix_from_v2_uninformative_grid_fixture":"Original quantization audit used frequency values exactly divisible by bin width, forcing zero error.",
            "off_grid_fixture":fix,
            "sample_size_not_biological":"12 source-inspired synthetic scenario cells",
            "worlds":worlds,
            "n_cells_cache_exact_JAR_DELTA_mismatch":sum(abs(w["difference_in_delta_lag"])>1e-12 for w in worlds),
            "max_absolute_change_in_JAR_delta":max(abs(w["difference_in_delta_lag"]) for w in worlds),
            "all_source_conditions_unchanged":True}

if __name__=="__main__":
    x=run()
    OUT.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("OFFGRID",x["off_grid_fixture"])
    print("EXACT_DIFF_CELLS",x["n_cells_cache_exact_JAR_DELTA_mismatch"],
          "MAX_DELTA_CHANGE",x["max_absolute_change_in_JAR_delta"])
    for r in x["worlds"]:
        print("EXACT_SCENE",r["n"],r["scale"],r["waveform"],
              "cached",round(r["binned_delta_lag"],6),
              "exact",round(r["exact_delta_lag"],6),
              "changed_label_counts",r["n_exact_lag_labels_changed_no_JAR"],r["n_exact_lag_labels_changed_JAR"])
