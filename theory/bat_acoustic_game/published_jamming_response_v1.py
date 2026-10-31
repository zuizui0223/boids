"""Second-hand published source reanalysis under pre-response contract v1.

This source-only branch DOES NOT collect new bat measurements. Uses published
experimental TF response and preserves original bat ID privacy in outputs.
Not independent biological confirmation of the original Hase et al. paper.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import random
import re
from statistics import mean, median
from source_gate_v2 import FIGSHARE_API, get_bytes

OUT=Path(__file__).resolve().parent/"published_jamming_response_v1.json"
CONTRACT=Path(__file__).resolve().parent/"PUBLISHED_JAMMING_REANALYSIS_CONTRACT_V1.md"
FILE="Data_jamming.csv"
EXP=("IPIlow","IPIhigh","SPLlow")
NMIN=4
BATS_MIN=5
LEVEL_MIN=3

def slope(xs,ys):
    if len(xs)<3:
        raise ValueError("need three distinct levels")
    m=mean(xs); w=sum((x-m)**2 for x in xs)
    if not w: raise ValueError("zero input variance")
    y0=mean(ys)
    return sum((x-m)*(y-y0) for x,y in zip(xs,ys))/w

def percentile(s,p):
    if not s: return None
    a=sorted(s)
    h=(len(a)-1)*p
    i=int(h)
    return a[i]*(1-(h-i))+a[min(i+1,len(a)-1)]*(h-i)

def bootstrap_interval(x):
    if not x: return [None,None]
    rng=random.Random(20261031)
    n=len(x)
    draws=[mean([x[rng.randrange(n)] for _ in range(n)]) for _ in range(5000)]
    return [percentile(draws,.025),percentile(draws,.975)]

def one_sided_sign_p(k,n):
    return sum(math.comb(n,j) for j in range(k,n+1))/(2**n) if n else None

def parse_level(experiment,label):
    if experiment.startswith("IPI"):
        m=re.fullmatch(r"(\d+)ms",label.strip())
        return math.log10(int(m.group(1))) if m and int(m.group(1))>0 else None
    if experiment=="SPLlow":
        m=re.fullmatch(r"(-?\d+)dB",label.strip())
        return float(m.group(1)) if m else None
    return None

def extract_source_rows():
    m,_=get_bytes(FIGSHARE_API,2*1024*1024)
    files=[f for f in json.loads(m).get("files",[]) if f.get("name")==FILE]
    if len(files)!=1:
        raise ValueError("requires one unambiguous Data_jamming.csv")
    b,_=get_bytes(files[0]["download_url"],3*1024*1024)
    r=csv.DictReader(io.StringIO(b.decode("utf-8-sig")))
    cols=set(r.fieldnames or [])
    needed={"ID","Experiment","Condition","Var","jammingTF","isON","TF"}
    if not needed.issubset(cols):
        raise ValueError("source missing fields "+str(sorted(needed-cols)))
    out=defaultdict(lambda:{"0":[],"1":[]})
    dropped=Counter()
    total=0
    for row in r:
        total+=1
        if row["isON"] not in ("0","1"):
            dropped["invalid_isON"]+=1;continue
        try: tf=float(row["TF"])
        except (ValueError,TypeError):
            dropped["TF_non_numeric"]+=1;continue
        if not math.isfinite(tf):
            dropped["TF_nonfinite"]+=1;continue
        if row["Experiment"] not in EXP:
            dropped["other_experiment"]+=1;continue
        key=(row["ID"].strip(),row["Experiment"].strip(),row["Condition"].strip(),
             row["Var"].strip(),row["jammingTF"].strip())
        if not key[0]:
            dropped["blank_ID"]+=1;continue
        out[key][row["isON"]].append(tf)
    return out,{"sha256":hashlib.sha256(b).hexdigest(),
                "original_rows":total,"excluded_rows_by_reason":dict(dropped)}

def compute(mode="median"):
    source,meta=extract_source_rows()
    stat=median if mode=="median" else mean
    # Fold same bat-condition context Var,jammingTF strata equally, never calls.
    contexts=defaultdict(list)
    eligible_strata=0
    for (i,e,c,var,jtf),y in source.items():
        if len(y["0"])>=NMIN and len(y["1"])>=NMIN:
            delta=stat(y["1"])-stat(y["0"])
            contexts[(i,e,c)].append(float(delta))
            eligible_strata+=1
    batlevel=defaultdict(dict)
    condition_bat_shifts=defaultdict(list)
    for (i,e,c),a in contexts.items():
        parsed=parse_level(e,c)
        if parsed is None:
            continue
        v=mean(a)
        batlevel[(i,e)][c]=(parsed,v)
        condition_bat_shifts[(e,c)].append(v)
    animal_slopes={}
    for (i,e),curves in batlevel.items():
        ordered=sorted(curves.values())
        if len(ordered)>=LEVEL_MIN and len(set(x for x,y in ordered))>=LEVEL_MIN:
            animal_slopes[(i,e)]=slope([x for x,y in ordered],[y for x,y in ordered])
    summary={}
    for e in EXP:
        a=[v for (i,k),v in animal_slopes.items() if k==e]
        n=len(a)
        neg=sum(v<0 for v in a);pos=sum(v>0 for v in a)
        summary[e]={
          "source_bats_with_3plus_levels":n,
          "slope_unit":"native_TF_per_log10_ms" if "IPI" in e else "native_TF_per_dB",
          "mean_slope":mean(a) if a else None,
          "median_slope":median(a) if a else None,
          "negative_slopes":neg,
          "positive_slopes":pos,
          "zero_slopes":n-neg-pos,
          "whole_bat_mean_bootstrap_95":bootstrap_interval(a),
          "primary_expected_negative_one_sided_exact_sign_p":one_sided_sign_p(neg,n) if e=="IPIlow" and n>=BATS_MIN else None,
          "status":"SUPPORTED_SOURCE_STRUCTURE" if n>=BATS_MIN else "STOP_FEWER_THAN_5_BATS"
        }
    pairs=[(a,b) for (i,e),a in animal_slopes.items() if e=="IPIlow"
            for (j,k),b in animal_slopes.items() if i==j and k=="IPIhigh"]
    contrast=[a-b for a,b in pairs]
    condition_table=[{"experiment":e,"condition":c,
          "bat_count":len(values),
          "equal_bat_mean_shift":mean(values),
          "equal_bat_median_shift":median(values)}
          for (e,c),values in sorted(condition_bat_shifts.items())]
    return {"schema":1,"status":"ARCHIVAL_SECONDARY_SOURCE_REANALYSIS_NOT_INDEPENDENT_REPLICATION",
            "observations_are_preexisting_public_bat_sounds":True,
            "new_animal_measurements":False,
            "source_2020_simulation_not_reproduced":True,
            "method":"per-bat per-stimulus ON minus OFF "+mode+" of TF; per-bat slopes",
            "source":meta,
            "eligible_bat_context_var_jammingTF_strata":eligible_strata,
            "primary_IPIlow":summary["IPIlow"],
            "secondary_IPIhigh":summary["IPIhigh"],
            "secondary_SPLlow":summary["SPLlow"],
            "paired_high_low":{
              "same_bats":len(contrast),
              "mean_low_minus_high_slope":mean(contrast) if contrast else None,
              "median_low_minus_high_slope":median(contrast) if contrast else None,
              "not_independent_across_source_experiments":True
            },
            "condition_level_descriptive":condition_table,
            "limitations":[
              "2026 source paper already reported spectral and IPI response directions",
              "ON/OFF time-order drift not controlled by this aggregate",
              "native TF source units not inferred from numeric magnitude",
              "source 2026 group misdetection model not directly replayed",
              "no prey capture or false-alarm recovery time measured"
            ]}

def main():
    if not CONTRACT.exists():
        raise SystemExit("STOP: prior analysis contract absent")
    res=compute("median")
    base=compute("mean")
    res["sensitivity_means"]={
        "primary_IPIlow":base["primary_IPIlow"],
        "secondary_IPIhigh":base["secondary_IPIhigh"],
        "secondary_SPLlow":base["secondary_SPLlow"]
    }
    OUT.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_SOURCE_SHA",res["source"]["sha256"])
    print("STRUCTURAL_ELIGIBLE_STRATA",res["eligible_bat_context_var_jammingTF_strata"])
    for label in ("primary_IPIlow","secondary_IPIhigh","secondary_SPLlow"):
        v=res[label]
        print(label, "status",v["status"],"bats",v["source_bats_with_3plus_levels"],
              "mean",v["mean_slope"],"median",v["median_slope"],
              "negative",v["negative_slopes"],"positive",v["positive_slopes"],
              "sign_p",v["primary_expected_negative_one_sided_exact_sign_p"])
    print("PAIRED_HIGH_LOW",res["paired_high_low"])
    print("RESULT_FILE",str(OUT))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
