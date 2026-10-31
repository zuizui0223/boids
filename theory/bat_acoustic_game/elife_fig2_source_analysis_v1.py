"""Recompute SOURCE-REPORTED 2020 eLife Fig.2 simulation row means.

Not an original MATLAB run. No original bat measurements; no simulated seed
crosswalk, so all JAR/non-JAR contrasts are unpaired and descriptive.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from statistics import mean, median
from source_gate_v2 import get_bytes
from original_model_preflight_v5 import ELIFE_DATA

OUT=Path(__file__).resolve().parent/"ELIFE_FIG2_SOURCE_COMPARISON_V1.json"
CONTRACT=Path(__file__).resolve().parent/"ELIFE_FIG2_NUMERIC_CONTRACT_V1.md"
INPUTS={
 "correlation":{"url":ELIFE_DATA["fig2_corr"],
   "sha256":"e36b0c461fc7aa448ecbd6d2fc8f724c0ac171f7ca972389f04a88cfe9c9c8b2",
   "arms":("CorrelationDetector","JAR_CorrelationDetector")},
 "filter_bank":{"url":ELIFE_DATA["fig2_filter"],
   "sha256":"285867a96b3fefd395bb998c1061496aca519cc167b18244f07b0632c50279ad",
   "arms":("FilterBank","JAR_FilterBank")},
}
SIZES=(2,3,5,7,10,20)
METRICS=("NumberOfCatches","NumberOfDetections","detections_per_pulse",
         "NumberOfInterfernces","TotalInterferenceRatio","fb_FA_rate")
SOURCE_KEYS=("NumberOfCatches","NumberOfDetections","NumberOfPulses",
             "NumberOfInterfernces","TotalInterferenceRatio")

def finite_number(s):
    try:
        v=float(s)
        return v if math.isfinite(v) else None
    except (TypeError,ValueError):return None

def read_source(metadata):
    raw,_=get_bytes(metadata["url"],5*1024*1024)
    if hashlib.sha256(raw).hexdigest()!=metadata["sha256"]:
        raise ValueError("PUBLISHER_SOURCE_SHA_MISMATCH")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    expected=set(SOURCE_KEYS)|{"ReceiverType","NumberOfBats","NumOfPreys","ExperimentName"}
    if not expected.issubset(reader.fieldnames or []):
        raise ValueError("SOURCE_FIELD_MISSING "+repr(expected-set(reader.fieldnames or [])))
    rows=[];dropped=Counter();batches=defaultdict(Counter)
    for row in reader:
        arm=row["ReceiverType"]
        n=finite_number(row["NumberOfBats"])
        prey=finite_number(row["NumOfPreys"])
        if arm not in metadata["arms"] or n not in SIZES or prey!=20:
            dropped["off_protocol_exposure"]+=1;continue
        values={k:finite_number(row.get(k)) for k in SOURCE_KEYS}
        if None in values.values():
            dropped["missing_source_metric"]+=1;continue
        values["detections_per_pulse"]=(values["NumberOfDetections"]/values["NumberOfPulses"]
                                        if values["NumberOfPulses"]>0 else None)
        values["fb_FA_rate"]=finite_number(row.get("fb_FA_rate"))
        rowout={"group_size":int(n),"arm":arm,"values":values,
                "batch":row["ExperimentName"]}
        rows.append(rowout)
        batches[(int(n),arm)][rowout["batch"]]+=1
    return rows,{"source_sha":metadata["sha256"],"rows":len(rows),
                 "dropped":dict(dropped),"batch_distinct_by_arm_group":{
                f"{n}:{arm}":len(c) for (n,arm),c in sorted(batches.items())}}

def summarize(values):
    valid=[v for v in values if v is not None]
    return {"n_finite":len(valid),"mean":mean(valid) if valid else None,
            "median":median(valid) if valid else None}

def compare_one(name,metadata):
    rows,info=read_source(metadata)
    groups=defaultdict(list)
    for row in rows:groups[(row["group_size"],row["arm"])].append(row["values"])
    if info["rows"]!=240:
        raise ValueError("SOURCE_ROW_COUNT_MISMATCH")
    out={"source":info,"receiver_family":name,"groups":[]}
    for n in SIZES:
        a,b=metadata["arms"]
        control=groups[(n,a)]
        treated=groups[(n,b)]
        if min(len(control),len(treated))<10:
            raise ValueError("INSUFFICIENT_SOURCE_GROUP "+str(n))
        metrics={}
        for metric in METRICS:
            if metric=="fb_FA_rate" and name!="filter_bank":continue
            x=summarize([row[metric] for row in control])
            y=summarize([row[metric] for row in treated])
            diff=(y["mean"]-x["mean"] if x["mean"] is not None and y["mean"] is not None else None)
            metrics[metric]={
               "without_JAR":x,"with_JAR":y,"JAR_minus_noJAR":diff,
               "relative_difference_from_control_pct":
                    100*diff/x["mean"] if diff is not None and x["mean"]!=0 else None}
        out["groups"].append({
           "number_of_bats":n,"no_JAR_row_count":len(control),"JAR_row_count":len(treated),
           "metric_summaries":metrics})
    out["balanced_groups_JAR_minus_noJAR"]={
       k:mean([row["metric_summaries"][k]["JAR_minus_noJAR"]
          for row in out["groups"] if row["metric_summaries"][k]["JAR_minus_noJAR"] is not None])
       for k in METRICS if k!="fb_FA_rate" or name=="filter_bank"}
    return out

def run():
    if not CONTRACT.exists():raise ValueError("FREEZE_CONTRACT_MISSING")
    outputs={k:compare_one(k,v) for k,v in INPUTS.items()}
    return {"schema":1,"status":"SECONDARY_PUBLISHED_SIMULATION_OUTPUT_REANALYSIS",
      "original_MATLAB_forward_run":False,"new_animal_measurements":False,
      "source_independent_biological_replication":False,
      "paired_source_seeds_identified":False,
      "source":"Mazar & Yovel (2020), eLife 9:e55539, Figure 2 original numerical output",
      "group_sizes":list(SIZES),"num_preys":20,
      "methods":"Unpaired equal-row mean differences in six pre-fixed bat-group strata; no p values",
      "results":outputs}

def main():
    try:
        result=run()
    except Exception as e:
        result={"schema":1,"status":"STOP_NO_VALID_ORIGINAL_SOURCE_COMPARISON",
                "error":type(e).__name__+":"+str(e)[:200],
                "original_MATLAB_forward_run":False,"new_animal_measurements":False}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("ELIFE_FIGURE2_STATUS",result["status"])
    for name,group in result.get("results",{}).items():
        print("SOURCE",name,group["source"])
        print("BALANCED",name,group["balanced_groups_JAR_minus_noJAR"])
        for c in group["groups"]:
            print("PER_GROUP",name,c["number_of_bats"],"no",c["no_JAR_row_count"],
             "yes",c["JAR_row_count"],
             "captures",c["metric_summaries"]["NumberOfCatches"]["JAR_minus_noJAR"],
             "detections",c["metric_summaries"]["NumberOfDetections"]["JAR_minus_noJAR"],
             "pulses_ratio",c["metric_summaries"]["detections_per_pulse"]["JAR_minus_noJAR"],
             "fb_false_alarm",(c["metric_summaries"].get("fb_FA_rate") or {}).get("JAR_minus_noJAR"),
             "raw_masking_total_ratio_change",c["metric_summaries"]["TotalInterferenceRatio"]["JAR_minus_noJAR"],
             "interference_events_change",c["metric_summaries"]["NumberOfInterfernces"]["JAR_minus_noJAR"],
             "catch_control",c["metric_summaries"]["NumberOfCatches"]["without_JAR"]["mean"],
             "catch_JAR",c["metric_summaries"]["NumberOfCatches"]["with_JAR"]["mean"],
             "fb_false_alarm_control",(c["metric_summaries"].get("fb_FA_rate") or {}).get("without_JAR",{}).get("mean"),
             "fb_false_alarm_JAR",(c["metric_summaries"].get("fb_FA_rate") or {}).get("with_JAR",{}).get("mean"))
    print("RESULT_JSON",str(OUT))
    return 0 if result["status"]!="STOP_NO_VALID_ORIGINAL_SOURCE_COMPARISON" else 3

if __name__=="__main__":raise SystemExit(main())
