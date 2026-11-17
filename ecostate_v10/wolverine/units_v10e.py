#!/usr/bin/env python3
"""v10e POST-RESULT audit: source distance units and triangle-inequality checks.

No newly estimated selection model or biological-effect claim. The original
source and all fields are checksum-pinned by field_v10c.source(). Summaries
are over original step candidates; do not redistribute sensitive locations.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import numpy as np
from field_v10c import source, build, group_admit

def pct(a):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return {"n":0}
    q = np.quantile(a,[0,.01,.1,.5,.9,.99,1.])
    return {"n":int(len(a)), "min":float(q[0]),"q01":float(q[1]),
            "q10":float(q[2]),"median":float(q[3]),"q90":float(q[4]),
            "q99":float(q[5]),"max":float(q[6])}

def check(d, groups):
    if len(groups)==0:raise ValueError("NO_MATCHED_GROUPS")
    # Original source reports SL_m in metres. Units for the distance-to-
    # network fields are NOT stated in the Dryad field description.
    used = np.asarray(d["used"],dtype=int)==1
    if int(used.sum())!=len(groups):raise ValueError("USED_FLAG_NOT_ONE_PER_GROUP")
    out={"schema":"ecostate.v10e.wolverine_source_unit_audit",
      "evidence_class":"postresult_source_definition_integrity_diagnostic",
      "source_original_step_unit":"SL_m = metres (provider annotation)",
      "road_stream_distance_units":"NOT SPECIFIED in provider README; DO NOT ASSUME",
      "status":"UNIT_AUDIT_COMPLETED_NOT_BEHAVIOURAL_PROOF",
      "source_rows":int(len(used)),"groups":len(groups),
      "source_measures":{},"strata":{},
      "claim_ceiling":"Distance-to-feature Lipschitz comparisons require consistent units, identical spatial reference and a fixed target network. Any violation is a unit/reference diagnostic, not animal behaviour."}
    for key in ("sl","road_start","road_end","stream_start","stream_end","traffic_start","traffic_end"):
        out["source_measures"][key]=pct(d[key])
    for feature in ("road","stream"):
        delta=np.abs(d[f"{feature}_end"]-d[f"{feature}_start"])
        rawratio=delta/np.maximum(d["sl"],1e-6)
        for flagname,mask in (("used",used),("available",~used),("all",np.ones(len(used),dtype=bool))):
            n=int(mask.sum())
            out["strata"][f"{feature}_{flagname}"]={
              "n":n, "absolute_start_end_change":pct(delta[mask]),
              "change_divided_by_sl_m":pct(rawratio[mask]),
              "fraction_raw_change_gt_step_length":float((delta[mask]>d["sl"][mask]+1e-5).mean()),
              "fraction_change_exact_zero":float((delta[mask]<1e-10).mean()),
              "fraction_change_within_step_by_10pct":float((delta[mask]<=.1*d["sl"][mask]).mean())}
    for sheet in sorted(np.unique(d["sheet"])):
        mask=d["sheet"]==sheet
        out["strata"][f"sheet_{int(sheet)}"]={
          "n":int(mask.sum()),"used_rows":int(np.sum(used&mask)),
          "step_length_m":pct(d["sl"][mask]),
          "road_delta_over_step_m":pct((np.abs(d["road_end"][mask]-d["road_start"][mask])/
                                         np.maximum(d["sl"][mask],1e-6))),
          "stream_delta_over_step_m":pct((np.abs(d["stream_end"][mask]-d["stream_start"][mask])/
                                           np.maximum(d["sl"][mask],1e-6)))}
    return out

def main(out):
    result={"status":"SOURCE_OR_MODEL_STOP",
            "evidence_class":"postresult_source_definition_integrity_diagnostic"}
    try:
        tmp,path=source()
        try: d,qc=build(path)
        finally:tmp.cleanup()
        groups,qc=group_admit(d,qc)
        result=check(d,groups)
        result["source_qc"]=qc
    except Exception as e:
        result["reason"]=str(e)[:1500]
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2)+"\n")
    print("WOLVERINE_V10E",result["status"])
    if result["status"]=="UNIT_AUDIT_COMPLETED_NOT_BEHAVIOURAL_PROOF":
        brief={k:{"raw_gt_SL":result["strata"][k]["fraction_raw_change_gt_step_length"],
                  "change_ratio_median":result["strata"][k]["change_divided_by_sl_m"]["median"]}
               for k in ("road_used","road_available","stream_used","stream_available")}
        print("UNIT_AUDIT_BRIEF",json.dumps(brief,separators=(",",":")))
    else:print("SOURCE_OR_MODEL_STOP",result.get("reason"))
if __name__=="__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "ecostate_v10/results/wolverine_source_unit_v10e.json")
