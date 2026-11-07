"""Source-structural figure CSV audit, no response columns read.

The source table has been publicly released since 2020; the analysis has prior-art
exposure. This gate fixes what strata can be compared before new numerical scores.
"""
from __future__ import annotations
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
from source_gate_v2 import get_bytes
from original_model_preflight_v5 import ELIFE_DATA

OUT=Path(__file__).resolve().parent/"elife_figure_schema_v6.json"
RESPONSES=("NumberOfCatches","NumberOfDetections","NumberOfPulses",
    "NumberOfInreferencesFromDirectCalls","NumberOfInreferencesFromMasking",
    "NumberOfInterfernces","NumberOfFalseAlarms","FalseAlarmRate",
    "MissedPrey","NumberOfPreysDetected")

def inspect(name,url):
    out={"name":name,"url":url,"status":"NOT_ATTEMPTED"}
    try:
        raw,_=get_bytes(url,5*1024*1024)
        rdr=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        cols=rdr.fieldnames or []
        out["sha256"]=hashlib.sha256(raw).hexdigest()
        out["columns"]=cols
        out["column_count"]=len(cols)
        keys=[k for k in cols if not any(c in k.lower() for c in
             ("catch","detect","interferen","maskingratio","falsealarm","missed",
              "soundlevel","time","score","fitness","pulsecount","preyhun"))]
        counters={k:collections.Counter() for k in keys}
        num=0
        for row in rdr:
            num+=1
            for k in keys:counters[k][(row[k] or "").strip()]+=1
        out["rows"]=num
        out["low_cardinality_source_columns"]={k:{"n_distinct":len(v),
            "values":dict(v.most_common(25)) if len(v)<=25 else
                dict(v.most_common(5))} for k,v in counters.items() if len(v)<=25}
        out["field_names_potential_treatment"]=[c for c in cols if any(x in c.lower()
            for x in ("jar","treatment","frequency","receiver","mode","jamming"))]
        out["status"]="SOURCE_SCHEMA_IDENTIFIED"
    except Exception as e:
        out.update(status="STOP_SOURCE_OR_FORMAT",error=type(e).__name__+":"+str(e)[:180])
    return out

def main():
    result={"schema":6,"status":"SOURCE_ONLY_TREATMENT_SCHEMA",
           "numeric_response_opened_in_this_gate":False,
           "not_independent_of_published_2020_results":True,
           "dataset":{name:inspect(name,url) for name,url in ELIFE_DATA.items()}}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for k,v in result["dataset"].items():
        print("SOURCE_TABLE",k,v["status"],"n",v.get("rows"),"sha256",v.get("sha256"))
        print("COLUMNS",k,json.dumps(v.get("columns",[])))
        print("TREATMENT_FIELDS",k,json.dumps(v.get("field_names_potential_treatment",[])))
        print("LOW_CARDINALITY",k,json.dumps(v.get("low_cardinality_source_columns",{})))
    return 0

if __name__=="__main__":raise SystemExit(main())
