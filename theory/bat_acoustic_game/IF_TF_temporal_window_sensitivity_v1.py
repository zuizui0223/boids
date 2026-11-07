"""Post-outcome time-window sensitivity for original published 2026 bat IF/TF.

All original IF/TF values remain in ephemeral GitHub Actions memory.
Solely bat/expt aggregate errors are exported. Not randomized, not causal.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import csv,hashlib,io,json,math

from source_gate_v2 import get_bytes,FIGSHARE_API
from published_IF_TF_convention_v1 import (
 SHA256,EXPERIMENTS,clean_source_rows,contrast_contexts,
 bat_error_summary,summarize_group,
)

ROOT=Path(__file__).resolve().parent
DESIGN=ROOT/"IF_TF_TEMPORAL_SENSITIVITY_POSTOUTCOME_DESIGN_V1.md"
OUT=ROOT/"IF_TF_TEMPORAL_SENSITIVITY_POSTOUTCOME_V1.json"
WINDOWS={
 "near_one_second":{"off":(-1.0,0.0),"on":(0.0,1.0)},
 "symmetric_two_seconds":{"off":(-2.0,0.0),"on":(0.0,2.0)},
 "exclude_near_switch":{"off":(-2.0,-0.5),"on":(0.5,2.0)}
}


def filter_window(rows,off,on):
    """Return ephemeral original source rows only within frozen time policy."""
    excluded=Counter()
    retained=[]
    for row in rows:
        treatment=(row.get("isON") or "").strip()
        if treatment not in ("0","1"):
            excluded["non_binary_source_ON"]+=1
            continue
        value=row.get("time")
        try:
            t=float(value)
        except (TypeError,ValueError):
            excluded["non_numeric_relative_time"]+=1
            continue
        if not math.isfinite(t):
            excluded["nonfinite_relative_time"]+=1
            continue
        lower,upper=off if treatment=="0" else on
        if lower<=t<upper:
            retained.append(row)
        else:
            excluded["not_in_predeclared_window"]+=1
    return retained,dict(excluded)


def source():
    if not DESIGN.exists():
        raise ValueError("STOP_MISSING_DESIGN_FREEZE")
    x,_=get_bytes(FIGSHARE_API,2*1024*1024)
    meta=json.loads(x)
    files=[f for f in meta.get("files",[]) if f.get("name")=="Data_jamming.csv"]
    if len(files)!=1:raise ValueError("STOP_MISSING_OR_DUPLICATE_SOURCE")
    data,_=get_bytes(files[0]["download_url"],3*1024*1024)
    sha=hashlib.sha256(data).hexdigest()
    if sha!=SHA256:raise ValueError("STOP_SOURCE_CHANGED_SHA256")
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    needed={"ID","IF","TF","time","Experiment","Condition","isON","Var","jammingTF"}
    if not needed.issubset(reader.fieldnames or []):
        raise ValueError("STOP_MISSING_SOURCE_FIELDS")
    return list(reader),sha


def window_results(rows,settings):
    selected,excluded=filter_window(rows,settings["off"],settings["on"])
    by,qc=clean_source_rows(selected)
    methods={}
    for mode in ("median","mean"):
        contexts,support=contrast_contexts(by,mode)
        batlevel={(i,e):bat_error_summary(vals) for (i,e),vals in contexts.items()}
        supported={key:value for key,value in batlevel.items() if value is not None}
        summaries={e:summarize_group(supported,e) for e in EXPERIMENTS}
        for e,v in summaries.items():
            v["source_condition_support_status"]=(
                "PASS" if v["n_bats"]>=5 else "SOURCE_SUPPORT_STOP_LT_FIVE_BATS")
        methods[mode]={
            "registered_source_context_substrata_with_min_four_each":support,
            "unique_bats":len({i for i,e in supported}),
            "n_bat_experiments":len(supported),
            "experiments":summaries
        }
    return {
        "off_relative_seconds":list(settings["off"]),
        "on_relative_seconds":list(settings["on"]),
        "retained_original_source_rows":len(selected),
        "excluded_source_design_rows":excluded,
        "original_source_QC_without_IDs":qc,
        "medians":methods["median"],
        "means_sensitivity":methods["mean"],
    }


def run():
    data,sha=source()
    return {
       "schema":1,
       "status":"POST_OUTCOME_ORIGINAL_BAT_IF_TF_TIME_WINDOW_SENSITIVITY",
       "source_sha256":sha,
       "source_doi":"10.6084/m9.figshare.30937379",
       "source_original_rows":len(data),
       "original_2026_group_simulator_reproduced":False,
       "new_bat_measurements":False,
       "no_source_bat_IDs_rows_or_exact_timestamps_exported":True,
       "all_ON_after_OFF_per_source_context":True,
       "three_windows_selected_after_full_outcome_but_before_window_outcomes":True,
       "units":"kHz, source-relative seconds",
       "windows":{name:window_results(data,params)
                  for name,params in WINDOWS.items()},
       "claim_limit":"Window sensitivity is not an identified causal acoustic response and cannot establish prey-capture benefit."
    }


def main():
    try:
        result=run()
    except Exception as e:
        result={"schema":1,"status":"STOP_SOURCE_DATA_OR_LOCK",
                "error":type(e).__name__+":"+str(e)[:220],
                "new_bat_measurements":False,
                "no_source_bat_IDs_rows_or_exact_timestamps_exported":True}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("WINDOW_AUDIT",result["status"])
    if result["status"].startswith("STOP"):
        print("SOURCE_STOP",result["error"])
        return 3
    print("ORIGINAL_SHA",result["source_sha256"])
    for name,x in result["windows"].items():
        print("WINDOW",name,"source_rows",x["retained_original_source_rows"])
        for e in EXPERIMENTS:
            for method in ("medians","means_sensitivity"):
                o=x[method]["experiments"][e]
                print("MODEL",name,method,e,
                    "status",o["source_condition_support_status"],
                    "bats",o["n_bats"],
                    "bat_conditions",o.get("n_bat_condition_cells"),
                    "dIF",o.get("equal_bat_mean_delta_IF_khz"),
                    "dTF",o.get("equal_bat_mean_delta_TF_khz"),
                    "D",o.get("mean_D_bandwidth_minus_start_khz"),
                    "CI",o.get("mean_D_whole_bat_bootstrap95_khz"),
                    "start_wins",o.get("source_bats_favor_fixed_start"),
                    "band_wins",o.get("source_bats_favor_fixed_bandwidth"))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
