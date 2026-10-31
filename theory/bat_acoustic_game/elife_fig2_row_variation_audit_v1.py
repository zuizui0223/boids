"""Source-variability diagnostic for ALREADY-OPENED 2020 Fig 2 simulator output.

Descriptive only: no independent biological sample size, p-values or CIs.
"""
from __future__ import annotations
from collections import defaultdict
import json
import math
from pathlib import Path
from statistics import mean, stdev
from elife_fig2_source_analysis_v1 import read_source,INPUTS

OUT=Path(__file__).resolve().parent/"ELIFE_FIG2_ROW_VARIATION_AUDIT_V1.json"
FIELDS=("NumberOfCatches","fb_FA_rate","TotalInterferenceRatio")
SIZES=(2,3,5,7,10,20)

def run():
    src,_=read_source(INPUTS["filter_bank"])
    aa=INPUTS["filter_bank"]["arms"]
    groups=defaultdict(list)
    for row in src:groups[(row["group_size"],row["arm"])].append(row["values"])
    rows=[]
    for n in SIZES:
        group={"group_size":n,"source_rows_no_JAR":len(groups[(n,aa[0])]),
               "source_rows_JAR":len(groups[(n,aa[1])]),"metrics":{}}
        if min(group["source_rows_no_JAR"],group["source_rows_JAR"])!=20:
            raise ValueError("SOURCE_GROUP_COUNT_CHANGED")
        for key in FIELDS:
            a=[p[key] for p in groups[(n,aa[0])] if p[key] is not None]
            b=[p[key] for p in groups[(n,aa[1])] if p[key] is not None]
            if len(a)!=20 or len(b)!=20:raise ValueError("NONFINITE_SCORE")
            m0,m1=mean(a),mean(b)
            sd0,sd1=stdev(a),stdev(b)
            pooled=math.sqrt((sd0*sd0+sd1*sd1)/2)
            group["metrics"][key]={
              "source_mean_no_JAR":m0,"source_mean_JAR":m1,
              "source_SD_no_JAR":sd0,"source_SD_JAR":sd1,
              "delta_mean":m1-m0,
              "absolute_delta_over_pooled_source_SD":abs(m1-m0)/pooled if pooled>0 else None
            }
        rows.append(group)
    return {"schema":1,"status":"POST_OUTCOME_DESCRIPTIVE_SIMULATION_ROW_VARIABILITY",
            "source_sha256":INPUTS["filter_bank"]["sha256"],
            "simulation_rows_not_independent_bats":True,
            "does_not_assume_simulation_seeds_independent":True,
            "no_statistical_significance_or_equivalence":True,
            "results":rows}

def main():
    o=run()
    OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
    for row in o["results"]:
        print("VARIABILITY",row["group_size"]," ".join(
          f"{k}:delta={v['delta_mean']:.7g}:pooled_SD_standardized={v['absolute_delta_over_pooled_source_SD']:.4f}"
          for k,v in row["metrics"].items()))
    print("RESULT_JSON",str(OUT))
    return 0

if __name__=="__main__":raise SystemExit(main())
