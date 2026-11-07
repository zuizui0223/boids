"""Exploratory POINT-ESTIMATE Pareto classification of published 2020 simulations.

This is an exact deterministic transformation of ALREADY-OPENED Fig.2
source-output group means, not an additional independent experiment.
"""
from __future__ import annotations
import json
from pathlib import Path
from elife_fig2_source_analysis_v1 import run as load_fig2

OUT=Path(__file__).resolve().parent/"ELIFE_FIG2_FACETED_PAYOFF_V1.json"
EPS=1e-10

def sign(v):
    if v is None: return None
    return 1 if v>EPS else -1 if v<-EPS else 0

def classify(delta_catches,delta_false_alarm):
    c=sign(delta_catches)
    f=sign(delta_false_alarm)
    if c is None or f is None:return "NOT_ESTIMABLE"
    if c>=0 and f<=0 and (c>0 or f<0):
        return "JAR_PARETO_FAVOURABLE_POINT_ESTIMATE"
    if c<=0 and f>=0 and (c<0 or f>0):
        return "NO_JAR_PARETO_FAVOURABLE_POINT_ESTIMATE"
    if c==0 and f==0:return "EQUAL_POINT_ESTIMATE"
    return "TRADEOFF_POINT_ESTIMATE"

def calculate():
    src=load_fig2()
    assert src["status"]=="SECONDARY_PUBLISHED_SIMULATION_OUTPUT_REANALYSIS"
    cells=src["results"]["filter_bank"]["groups"]
    out=[]
    for row in cells:
        x=row["metric_summaries"]
        dc=x["NumberOfCatches"]["JAR_minus_noJAR"]
        df=x["fb_FA_rate"]["JAR_minus_noJAR"]
        dm=x["TotalInterferenceRatio"]["JAR_minus_noJAR"]
        out.append({
           "bat_count":row["number_of_bats"],
           "source_rows_per_arm":row["JAR_row_count"],
           "delta_capture_per_simulation_row":dc,
           "delta_filterbank_false_alarm_rate":df,
           "delta_total_interference_ratio":dm,
           "observed_direction_of_interference":sign(dm),
           "observed_direction_of_false_alarm":sign(df),
           "observed_direction_of_capture":sign(dc),
           "two_outcome_point_estimate_class":classify(dc,df)})
    counts={k:sum(x["two_outcome_point_estimate_class"]==k for x in out) for k in sorted(
        set(x["two_outcome_point_estimate_class"] for x in out))}
    return {"schema":1,
      "status":"EXPLORATORY_ALREADY_PUBLISHED_MODEL_OUTPUT_POINT_ESTIMATE_ONLY",
      "source":"Mazar & Yovel (2020), eLife 9:e55539; Figure 2 FilterBank source-output csv",
      "source_file_sha256":src["results"]["filter_bank"]["source"]["source_sha"],
      "independent_model_reproduction":False,
      "biological_animal_replicates":0,
      "no_significance_or_equivalence_claim":True,
      "criterion":"JAR improves catches and decreases false alarm (weak Pareto) versus vice versa; no utility weights inferred",
      "group_size_cells":out,
      "class_counts":counts,
      "raw_interference_ratio_decreased_all_groups":all(r["delta_total_interference_ratio"]<0 for r in out),
      "false_alarm_rate_increased_cells":sum(r["delta_filterbank_false_alarm_rate"]>0 for r in out),
      "finite_source_cell_support":"20 original modeled-output rows per JAR condition and group size",
      "limitations":[
          "original model outcomes have already been published and reanalysed",
          "the Figure 2 row labels do not prove paired random seeds",
          "unknown simulation output and agent independence",
          "JAR programme has no calibrated energetic cost or capture unit normalization",
          "spectrum-, habitat- and prey-dependent utility changes remain unknown",
          "2026 group-flight potential misdetections are different estimands"
      ]}

def main():
    obj=calculate()
    OUT.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print("POINT_ESTIMATE_CLASS_COUNTS",obj["class_counts"])
    print("MASKING_DECREASE_ALL_GROUPS",obj["raw_interference_ratio_decreased_all_groups"])
    print("FALSE_ALARM_INCREASE_COUNT",obj["false_alarm_rate_increased_cells"])
    for row in obj["group_size_cells"]:
        print("SOURCE_POINT",row["bat_count"],row["two_outcome_point_estimate_class"],
            "catch",round(row["delta_capture_per_simulation_row"],7),
            "fa",round(row["delta_filterbank_false_alarm_rate"],7),
            "mask",round(row["delta_total_interference_ratio"],7))
    print("RESULT_JSON",str(OUT))

if __name__=="__main__":main()
