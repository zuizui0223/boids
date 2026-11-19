#!/usr/bin/env python3
"""v37 frozen cross-study bat movement summary prediction; no habitat joins.

Public paper-level aggregates only. Never exports original animal records,
roost locations or identifiable original coordinates.
"""
import argparse,csv,io,json,hashlib,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from original_bat_macro_source_gate import FILES,download_original

OUT=Path("validation_v37/results/bat_macro_morphology_transfer_v37.json")
SEED=20261119
B=10000

def num(x):
    try:
        n=float(str(x).strip().replace(",","."))
        return n if math.isfinite(n) else None
    except (ValueError,TypeError):return None

def parse_source():
    orig=download_original(FILES["published_meta"])
    if orig["status"]!="ORIGINAL_CSV_PINNED":
        raise RuntimeError("PINNED_MACRO_ORIGINAL_CSV_ACCESS_OR_HASH_STOP")
    text=orig.pop("_csv_text")
    sep=max((";",",","\t"),key=text.splitlines()[0].count)
    return list(csv.DictReader(io.StringIO(text),delimiter=sep)),orig["derived_sha256"]

def prepare(raw,target):
    rows=[]; excluded=Counter()
    for r in raw:
        y=num(r.get(target))
        if y is None or y<0:
            excluded["target_missing_or_nonfinite_or_negative"]+=1;continue
        st=tuple(str(r.get(x) or "").strip() for x in ("Authors","Year_pub","Journal"))
        if not st[0]:
            excluded["no_source_authorship_key"]+=1;continue
        m=num(r.get("Mass"));f=num(r.get("Forearm"))
        m=np.log1p(m) if m is not None and m>0 else None
        f=np.log1p(f) if f is not None and f>0 else None
        rows.append({"y":math.log1p(y),"paper":st,"country":(r.get("Pays") or "").strip(),
                     "species":(r.get("Species") or "").strip(),"mass":m,"forearm":f})
    group_counts=Counter(r["paper"] for r in rows)
    n_m=sum(r["mass"] is not None for r in rows)
    n_f=sum(r["forearm"] is not None for r in rows)
    groups=len(group_counts)
    countries={r["country"] for r in rows if r["country"]}
    species={r["species"] for r in rows if r["species"]}
    passed=(len(rows)>=100 and groups>=20 and len(countries)>=5 and len(species)>=8
            and n_m>=20 and n_f>=20)
    return rows,{"eligible_target_rows":len(rows),"paper_groups":groups,
                 "raw_country_labels":len(countries),"raw_species_labels":len(species),
                 "positive_mass_values":n_m,"positive_forearm_values":n_f,
                 "target_exclusion_counts":dict(excluded),
                 "frozen_structural_gate_passed":passed}

def xyz(rows,med=None):
    xx=np.array([[np.nan if r["mass"] is None else r["mass"],
                  np.nan if r["forearm"] is None else r["forearm"]]
                  for r in rows],dtype=float)
    if med is None:
        med=[]
        for j in range(2):
            vals=xx[np.isfinite(xx[:,j]),j]
            med.append(float(np.median(vals)) if len(vals) else 0.)
        med=np.asarray(med)
    missing=(~np.isfinite(xx)).astype(float)
    return np.column_stack((np.where(np.isfinite(xx),xx,med),missing)),med

def compare(train,test):
    by=Counter(r["paper"] for r in train)
    w=np.array([1/by[r["paper"]] for r in train])
    yt=np.array([r["y"] for r in train])
    yy=np.array([r["y"] for r in test])
    m0=float(np.average(yt,weights=w))
    x,med=xyz(train);xx,_=xyz(test,med=med)
    scaler=StandardScaler().fit(x)
    x=scaler.transform(x);xx=scaler.transform(xx)
    model=Ridge(alpha=10.,fit_intercept=True).fit(x,yt,sample_weight=w)
    p1=model.predict(xx)
    return float(np.mean((yy-m0)**2)),float(np.mean((yy-p1)**2))

def exact_sign(k,n):
    return float(sum(math.comb(n,i) for i in range(k,n+1))/2**n) if n else None

def boot(g):
    gains=np.array(g,dtype=float)
    if len(gains)==0:return {"status":"NO_EVALUABLE_GROUPS"}
    rng=np.random.default_rng(SEED)
    # bounded memory even when study count grows
    b=np.empty(B)
    for i in range(B):
        b[i]=rng.choice(gains,size=len(gains),replace=True).mean()
    lo,hi=np.percentile(b,[2.5,97.5])
    k=int(np.count_nonzero(gains>0))
    return {"status":"EVALUATED",
            "group_n":len(gains),"positive_group_n":k,
            "equal_group_MSE_saved":float(gains.mean()),
            "whole_group_bootstrap_95":[float(lo),float(hi)],
            "exact_one_sided_positive_sign_p":exact_sign(k,len(gains)),
            "predeclared_positive_gate_passed":bool(gains.mean()>0 and lo>0 and exact_sign(k,len(gains))<=.05)}

def by_group(rows,key,minimum_test=1,minimum_group_count=1,purge_publication=False):
    cats=defaultdict(list)
    for r in rows:
        label=r[key]
        if label:cats[label].append(r)
    qualified={label:r for label,r in cats.items() if len(r)>=minimum_test}
    if len(qualified)<minimum_group_count:
        return {"status":"STRUCTURAL_GROUP_HOLDOUT_STOP",
                "eligible_groups_with_minimum_test_records":len(qualified)}
    gains=[];baseline=[];morph=[];receipts=[]
    for label,test in sorted(qualified.items(),key=lambda x:str(x[0])):
        blocked={r["paper"] for r in test} if purge_publication else set()
        train=[r for r in rows if r[key]!=label and
               (not purge_publication or r["paper"] not in blocked)]
        if len({r["paper"] for r in train})<15:
            receipts.append({"skip":"too_few_training_papers"});continue
        loss0,loss1=compare(train,test)
        gains.append(loss0-loss1);baseline.append(loss0);morph.append(loss1)
        receipts.append({"test_n":len(test),"gain":loss0-loss1})
    result=boot(gains)
    result["models"]={"M0_baseline_equal_group_MSE":float(np.mean(baseline)) if baseline else None,
                      "M1_morph_equal_group_MSE":float(np.mean(morph)) if morph else None}
    result["tested_groups"]=len(gains)
    result["skipped_eligible_groups"]=len(qualified)-len(gains)
    if key=="paper":
        result["hashed_publication_group_gains"]=[
            {"hashed_paper_key":hashlib.sha256(str(k).encode()).hexdigest()[:12],
             "loss_reduction":g}
            for k,g in zip(sorted(qualified,key=str),gains)]
    return result

def evaluate(raw):
    result={"programme":"v37_bat_morphology_cross_source_transfer",
            "original_source_zenodo_record":5794471,
            "source_doi":"10.5061/dryad.qnk98sfhh",
            "source_paper_already_tested_in_sample_morphology_effects":True,
            "landscape_joins_not_used_due_to_v36_stop":True,
            "no_bat_GPS_coordinates_exported":True,
            "individual_movement_or_learning_causal_claim":False,
            "primary_endpoint":"Dist","published_record_not_individual_tracking_unit":True}
    all_results={}
    for target in ("Dist","MCP"):
        rows,diag=prepare(raw,target)
        entry={"support":diag,"target":"log1p("+target+")"}
        if not diag["frozen_structural_gate_passed"]:
            entry["status"]="STRUCTURAL_SUPPORT_STOP_NO_MODEL_FIT"
        else:
            entry["primary_whole_paper"]=by_group(rows,"paper")
            entry["secondary_whole_country"]=by_group(
                rows,"country",minimum_test=10,minimum_group_count=5,purge_publication=True)
            entry["secondary_raw_species"]=by_group(
                rows,"species",minimum_test=10,minimum_group_count=10,purge_publication=True)
            entry["status"]="PRIMARY_EVALUATED_FROZEN_MODELS"
        all_results[target]=entry
    result["endpoints"]=all_results
    result["primary_status"]=all_results["Dist"]["status"]
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,default=OUT)
    args=parser.parse_args()
    rows,sha=parse_source()
    result=evaluate(rows)
    result["original_pinned_meta_csv_sha256"]=sha
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for target,entry in result["endpoints"].items():
        concise={"target":target,"status":entry["status"],"support":entry["support"]}
        if "primary_whole_paper" in entry:
            for k in ("primary_whole_paper","secondary_whole_country","secondary_raw_species"):
                x=entry[k]
                concise[k]={p:q for p,q in x.items() if p not in ("hashed_publication_group_gains",)}
        print("V37_FROZEN_MACRO_TRANSFER="+json.dumps(concise,sort_keys=True))
    print("V37_NO_CAUSAL_OR_GLOBAL_UNIVERSALITY_CLAIM")
