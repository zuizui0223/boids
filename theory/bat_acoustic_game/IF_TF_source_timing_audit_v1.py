"""Post-outcome source DESIGN audit only; no IF/TF/acoustic outcomes opened.

Source-pinned Figshare 2026 Data_jamming.csv; source timing and bat/experiment
overlap determine interpretation limits of existing secondary IF/TF results.
Never export source bat IDs, exact times, or original rows.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import csv,hashlib,io,json,math

from source_gate_v2 import FIGSHARE_API,get_bytes

SOURCE_SHA="2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367"
SOURCE_NAME="Data_jamming.csv"
EXPS=("IPIlow","IPIhigh","SPLlow")
OUT=Path(__file__).resolve().parent/"IF_TF_SOURCE_TIMING_AND_COHORT_AUDIT_V1.json"


def finite(s):
    try:
        x=float(s)
        return x if math.isfinite(x) else None
    except (ValueError,TypeError):
        return None

def percentiles(arr):
    if not arr:return None
    s=sorted(arr)
    def q(p):
        t=(len(s)-1)*p
        i=int(t);j=min(len(s)-1,i+1)
        return s[i]*(1-(t-i))+s[j]*(t-i)
    return {"min":q(0),"q25":q(.25),"median":q(.5),"q75":q(.75),"max":q(1)}

def get_rows():
    meta,_=get_bytes(FIGSHARE_API,2*1024*1024)
    files=[a for a in json.loads(meta).get("files",[]) if a.get("name")==SOURCE_NAME]
    if len(files)!=1:
        raise ValueError("STOP_ORIGINAL_SOURCE_FILE_NONUNIQUE")
    raw,_=get_bytes(files[0]["download_url"],3*1024*1024)
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=SOURCE_SHA:raise ValueError("STOP_ORIGINAL_SOURCE_SHA_MISMATCH")
    r=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    must={"ID","Experiment","Condition","Var","jammingTF","isON","Time","time"}
    if not must.issubset(r.fieldnames or []):
        raise ValueError("STOP_REQUIRED_SOURCE_TIME_COLUMNS_MISSING")
    return r,sha


def audit(rows):
    timebins=defaultdict(list)
    sourcebat={e:set() for e in EXPS}
    states=Counter()
    contexts=defaultdict(lambda:{"0":[],"1":[]})
    total=0
    invalid=Counter()
    for row in rows:
        total+=1
        e=(row.get("Experiment") or "").strip()
        if e not in EXPS:invalid["unexpected_experiment"]+=1;continue
        on=(row.get("isON") or "").strip()
        if on not in ("0","1"):invalid["unexpected_ON_state"]+=1;continue
        i=(row.get("ID") or "").strip()
        if not i:invalid["missing_source_ID"]+=1;continue
        sourcebat[e].add(i)
        states[(e,on)]+=1
        t=finite(row.get("time"))
        if t is None:
            invalid["missing_relative_time"]+=1
            continue
        timebins[(e,on)].append(t)
        key=(i,e,(row.get("Condition") or "").strip(),
             (row.get("Var") or "").strip(),
             (row.get("jammingTF") or "").strip())
        contexts[key][on].append(t)
    time_summary=[]
    for (e,on),values in sorted(timebins.items()):
        time_summary.append({"experiment":e,"state":on,
                "n_original_rows_with_finite_relative_time":len(values),
                "relative_time_seconds":percentiles(values),
                "fraction_below_zero":sum(t<0 for t in values)/len(values),
                "fraction_equal_zero":sum(t==0 for t in values)/len(values),
                "fraction_above_zero":sum(t>0 for t in values)/len(values)})
    source_counts={e:len(sourcebat[e]) for e in EXPS}
    overlap={f"{a}&{b}":len(sourcebat[a]&sourcebat[b])
             for k,a in enumerate(EXPS) for b in EXPS[k+1:]}
    context_counts=defaultdict(Counter)
    for (i,e,c,var,jtf),tw in contexts.items():
        if min(len(tw["0"]),len(tw["1"]))<4:
            continue
        off_min,off_max=min(tw["0"]),max(tw["0"])
        on_min,on_max=min(tw["1"]),max(tw["1"])
        overlap_bool=max(off_min,on_min)<=min(off_max,on_max)
        context_counts[e]["supported_ON_OFF_contexts"]+=1
        context_counts[e]["time_ranges_overlapping" if overlap_bool else "time_ranges_disjoint"]+=1
        if off_max<on_min:
            context_counts[e]["all_OFF_before_ON"]+=1
        elif on_max<off_min:
            context_counts[e]["all_ON_before_OFF"]+=1
    return {"source_original_rows":total,
            "source_bats_total_unique":len(set().union(*sourcebat.values())),
            "source_bats_by_experiment":source_counts,
            "source_bat_overlaps_by_experiment":overlap,
            "source_ON_OFF_rows":[{"experiment":e,"state":on,"rows":n}
                                  for (e,on),n in sorted(states.items())],
            "source_relative_time_summary":time_summary,
            "supported_context_time_range_diagnostics":{e:dict(context_counts[e]) for e in EXPS},
            "invalid_source_structure":dict(invalid)}


def run():
    rows,sha=get_rows()
    a=audit(rows)
    return {"schema":1,"status":"POST_OUTCOME_SOURCE_TIME_STRUCTURE_ONLY",
            "source_sha256":sha,"source":"10.6084/m9.figshare.30937379",
            "new_bat_measurements":False,"source_IF_TF_values_opened_in_this_audit":False,
            "no_original_bat_IDs_or_original_rows_exported":True,
            "source_time_definition":"relative stimulus time from published ReadMe, seconds",
            "time_overlap_is_not_experimental_causality_test":True,
            "result":a}
def main():
    try:
        obj=run()
    except Exception as ex:
        obj={"schema":1,"status":"STOP_SOURCE_SCHEMA_OR_ACCESS",
             "reason":type(ex).__name__+":"+str(ex)[:250],
             "source_IF_TF_values_opened_in_this_audit":False,
             "new_bat_measurements":False}
    OUT.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print("SOURCE_TIME_AUDIT",obj["status"])
    if obj["status"].startswith("STOP"):
        print("STOP",obj["reason"]);return 3
    d=obj["result"]
    print("BATS",d["source_bats_total_unique"],d["source_bats_by_experiment"])
    print("BAT_EXPERIMENT_OVERLAP",d["source_bat_overlaps_by_experiment"])
    print("CONTEXT_TIMES",d["supported_context_time_range_diagnostics"])
    for x in d["source_relative_time_summary"]:
        print("SOURCE_TIME",x["experiment"],x["state"],x["n_original_rows_with_finite_relative_time"],
              x["relative_time_seconds"],"fraction_before_zero",x["fraction_below_zero"])
    return 0
if __name__=="__main__":
    raise SystemExit(main())
