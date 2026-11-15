"""Outcome-blind schema/support audit of EXISTING Figshare experiment 30937379.

Never read TF, DUR, IF or SPL outcome values. No original animal IDs, times,
raw rows, coordinates or experimental response are published in the receipt.
This inventory does not demonstrate biological effects.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
from source_gate_v2 import FIGSHARE_API, get_bytes

OUT=Path(__file__).resolve().parent/"published_jamming_preflight_v4.json"
NAME="Data_jamming.csv"
DESIGN_COLUMNS=("ID","Var","jammingTF","Condition","isON","Experiment")
KNOWN_SCHEMA=("Time","time","IF","TF","DUR","SPL","ID","Var",
              "jammingTF","Condition","isON","Experiment")

def preflight():
    result={"schema":4,"status":"NOT_RUN","source_doi":"10.6084/m9.figshare.30937379",
            "original_response_TF_opened":False,
            "other_biological_responses_opened":False,
            "raw_bat_IDs_published":False,
            "predeclared_requirements":{
               "min_individuals_with_both_ON_OFF":5,
               "min_distinct_jamming_contexts_per_individual":2,
               "minimum_rows_per_state_per_context":4
            }}
    try:
        meta,_=get_bytes(FIGSHARE_API,2*1024*1024)
        m=json.loads(meta)
        allfiles=[f for f in m.get("files",[]) if f.get("name")==NAME]
        if len(allfiles)!=1:
            result["status"]="STOP_UNIQUE_SOURCE_FILE"
            result["matching_files"]=len(allfiles)
            return result
        f=allfiles[0]
        raw,_=get_bytes(f["download_url"],3*1024*1024)
        result["file_sha256"]=hashlib.sha256(raw).hexdigest()
        result["file_bytes"]=len(raw)
        # Read only source DESIGN columns, never biological response columns.
        reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        cols=tuple(reader.fieldnames or ())
        result["schema_columns_match"]=(cols==KNOWN_SCHEMA)
        if not set(DESIGN_COLUMNS).issubset(cols):
            result["status"]="STOP_MISSING_DESIGN_COLUMNS"
            return result
        table=defaultdict(Counter)
        label_counts=Counter()
        state_counts=Counter()
        anon_individuals=set()
        nrows=0
        for row in reader:
            nrows+=1
            individual=row["ID"].strip()
            if not individual:
                continue
            anon_individuals.add(individual)
            condition=(row["Experiment"].strip(),row["Condition"].strip(),
                       row["Var"].strip(),row["jammingTF"].strip())
            on=row["isON"].strip()
            table[(individual,condition)][on]+=1
            state_counts[on]+=1
            label_counts[(row["Experiment"].strip(),row["Condition"].strip())]+=1
        result["total_rows"]=nrows
        result["distinct_source_bat_ID_labels"]=len(anon_individuals)
        result["isON_category_row_counts"]={k:v for k,v in sorted(state_counts.items())}
        # Do not publish crosswalk of specific bat IDs.
        result["experiment_condition_row_counts"]=[
          {"experiment":k[0],"condition":k[1],"rows":n}
          for k,n in sorted(label_counts.items())]
        # Determine source encoding of true on/off (not TF outcomes).
        tags=set(state_counts)
        pairs= [("0","1"),("FALSE","TRUE"),("False","True"),("OFF","ON")]
        found=[p for p in pairs if set(p).issubset(tags)]
        result["valid_binary_ON_OFF_coding"]=bool(found)
        if not found:
            result["status"]="STOP_ON_OFF_STATE_MAPPING_NOT_VERIFIED"
            return result
        off,on=found[0]
        minrows=result["predeclared_requirements"]["minimum_rows_per_state_per_context"]
        supported=defaultdict(set)
        for (i,cond),c in table.items():
            if c[off]>=minrows and c[on]>=minrows:
                supported[i].add(cond)
        n2=sum(len(contexts)>=2 for contexts in supported.values())
        result["individuals_with_matched_ON_OFF_contexts"]=len(supported)
        result["individuals_with_two_or_more_matched_contexts"]=n2
        result["eligible_contexts_total"]=sum(len(k) for k in supported.values())
        result["status"]="PASS_SOURCE_STRUCTURE_NO_RESPONSE_OPENED" if n2>=5 else "STOP_LOW_PAIR_CONTEXT_SUPPORT"
    except Exception as e:
        result["status"]="STOP_SOURCE_ACCESS_OR_SCHEMA"
        result["error"]=type(e).__name__+":"+str(e)[:200]
    return result

def main():
    x=preflight()
    OUT.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("JAMMING_PREFLIGHT",x["status"],"source_bats",x.get("distinct_source_bat_ID_labels"),
        "matched_context_bats",x.get("individuals_with_two_or_more_matched_contexts"),
        "groups",x.get("eligible_contexts_total"))
    print("LABEL_TABLE",json.dumps(x.get("experiment_condition_row_counts",[])))
    print("ON_OFF",json.dumps(x.get("isON_category_row_counts",{})))
    print("PREFLIGHT_JSON",str(OUT))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
