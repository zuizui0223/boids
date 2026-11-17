#!/usr/bin/env python3
"""v10g post-result source-attribute equality leak diagnostic, NOT ecology.

Uses checksum-verified Scrafford original. Tests whether the joint equality
of road/stream (and traffic) start/end measurements identifies "used" rows,
even in >100-m steps and with nonzero values. A source-label diagnostic can
NOT establish actual behavioral state maintenance.
"""
from __future__ import annotations
import collections
import json
import math
import sys
from pathlib import Path
import hashlib
import numpy as np
from scipy.optimize import minimize_scalar
from field_v10c import source, build, group_admit

def eq_masks(d,eps=1e-10):
    rd=np.abs(d["road_end"]-d["road_start"])<=eps
    sd=np.abs(d["stream_end"]-d["stream_start"])<=eps
    td=np.abs(d["traffic_end"]-d["traffic_start"])<=eps
    nonzero=(d["road_start"]>0)&(d["stream_start"]>0)
    return {"road":rd,"stream":sd,"traffic":td,
            "road_stream":rd&sd,
            "road_stream_nonzero":rd&sd&nonzero,
            "road_stream_traffic":rd&sd&td}

def estimate_beta(n_equal,n_group,used_equal,weights):
    # Conditional softmax for one binary indicator per candidate.
    # Evaluate within-group likelihood with whole-animal equal weights.
    def fun(beta):
        z=np.logaddexp(np.log(np.maximum(n_group-n_equal,1e-30)),np.log(np.maximum(n_equal,1e-30))+beta)
        return float(weights @ (z-beta*used_equal)+0.02*beta**2/2)
    r=minimize_scalar(fun,method="bounded",bounds=(-3,12),options={"xatol":1e-9})
    if not r.success or not np.isfinite(r.x):raise ValueError("FIT_FAILED")
    return float(r.x)

def one_fold_model(d,groups,eq):
    # 5 whole-source animal folds, no used/available record leakage.
    animals=np.array([k[1] for k,_ in groups],dtype=object)
    ids=sorted(set(animals),key=lambda x:hashlib.sha256(x.encode()).hexdigest())
    fold={a:i%5 for i,a in enumerate(ids)}
    n=np.array([len(idx) for _,idx in groups],dtype=int)
    m=np.array([int(np.sum(eq[idx])) for _,idx in groups],dtype=int)
    is_used=np.array([int(np.flatnonzero(d["used"][idx]==1)[0]) for _,idx in groups])
    u=np.array([int(eq[idx[pos]]) for (_,idx),pos in zip(groups,is_used)])
    losses={a:[] for a in ids}
    baseline={a:[] for a in ids}
    betas=[]
    for fi in range(5):
        tr=np.flatnonzero(np.array([fold[a]!=fi for a in animals]))
        te=np.flatnonzero(np.array([fold[a]==fi for a in animals]))
        counts=collections.Counter(animals[tr])
        w=np.array([1/(len(counts)*counts[a]) for a in animals[tr]],dtype=float)
        b=estimate_beta(m[tr],n[tr],u[tr],w)
        betas.append(b)
        # Same mathematical denominator as fitted conditional logit.
        z=np.logaddexp(np.log(np.maximum(n[te]-m[te],1e-30)),
                       np.log(np.maximum(m[te],1e-30))+b)
        ll=z-b*u[te]
        for aa in set(animals[te]):
            mask=animals[te]==aa
            losses[aa].extend(ll[mask].tolist())
            baseline[aa].extend(np.log(n[te][mask]).tolist())
    gains=np.array([np.mean(baseline[a])-np.mean(losses[a]) for a in ids])
    rng=np.random.default_rng(20261117)
    bt=rng.choice(gains,size=(10000,len(gains)),replace=True).mean(1)
    return {"n_source_animals":len(ids),"source_groups":len(groups),
       "baseline_uniform_source_choice_logloss":float(np.mean([np.mean(baseline[a]) for a in ids])),
       "equality_only_logloss":float(np.mean([np.mean(losses[a]) for a in ids])),
       "mean_nats_per_group_uniform_minus_equality_only":float(gains.mean()),
       "whole_animal_bootstrap95":list(map(float,np.quantile(bt,[.025,.975]))),
       "positive_animals":int(np.sum(gains>0)),
       "beta_by_holdout_fold":betas,
       "diagnostic_only":True}

def calc(d,groups):
    used=d["used"]==1
    eq=eq_masks(d)
    sl=d["sl"]
    result={
      "schema":"ecostate.v10g.used_vs_available_source_attribute_equality",
      "status":"POSTRESULT_SOURCE_LABEL_LEAK_DIAGNOSTIC_ONLY",
      "evidence_class":"postresult_no_new_wild_behaviour_claim",
      "original_source_sha256":"979a362af1acaff069a7c53dfabf5284eb68d0c448899858ae18be999513b1bd",
      "source_rows":len(used),"source_groups":len(groups),
      "case_classes":{},"per_sheet":{},"label_discrimination":{},
      "claim_ceiling":"Equal start/end covariates in observed rows can reflect source preparation, spatial field discretization, repeated original measurements, or real behavior. An equality-only heldout score is source-label information, not animal-state maintenance."}
    for flag,mask in [("used",used),("available",~used),("used_long_gt100m",used&(sl>100)),("available_long_gt100m",(~used)&(sl>100))]:
        val={"rows":int(mask.sum()),"median_step_length_m":float(np.median(sl[mask]))}
        for name,q in eq.items():val[name]=float(np.mean(q[mask]))
        result["case_classes"][flag]=val
    for sheet in sorted(np.unique(d["sheet"])):
        s=d["sheet"]==sheet
        result["per_sheet"][str(int(sheet))]={}
        for n,m in [("used",used&s),("available",(~used)&s)]:
            result["per_sheet"][str(int(sheet))][n]={"rows":int(np.sum(m)),
                "both_nonzero_equal":float(np.mean(eq["road_stream_nonzero"][m])),
                "triple_equal":float(np.mean(eq["road_stream_traffic"][m]))}
    # group-level marker ability and observed status within source-matched sets.
    idx_used=np.array([int(np.flatnonzero(d["used"][idx]==1)[0]) for _,idx in groups])
    ns=np.array([int(np.sum(eq["road_stream"][idx])) for _,idx in groups])
    uu=np.array([bool(eq["road_stream"][idx[j]]) for (_,idx),j in zip(groups,idx_used)])
    result["label_discrimination"]={
      "groups_with_any_equal_candidate":int(np.sum(ns>0)),
      "groups_with_exactly_one_equal_candidate":int(np.sum(ns==1)),
      "exactly_one_equal_and_it_is_used":int(np.sum((ns==1)&uu)),
      "used_equal_fraction":float(np.mean(uu)),
      "mean_equal_alternatives_per_group":float(np.mean(ns-uu)),
      "source_uniform_probability":float(np.mean([1/len(idx) for _,idx in groups])),
      "two_attribute_equality_only":one_fold_model(d,groups,eq["road_stream"])}
    return result

def main(path):
    result={"status":"SOURCE_OR_MODEL_STOP","evidence_class":"postresult_no_new_wild_behaviour_claim"}
    try:
        temp,p=source()
        try:d,qc=build(p)
        finally:temp.cleanup()
        groups,qc=group_admit(d,qc)
        result=calc(d,groups)
        result["source_qc"]=qc
    except Exception as e:
        result["reason"]=str(e)[:1200]
    out=Path(path);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("V10G_LABEL_AUDIT",result["status"])
    if result["status"]=="POSTRESULT_SOURCE_LABEL_LEAK_DIAGNOSTIC_ONLY":
        print("V10G_CASES",json.dumps(result["case_classes"],separators=(",",":")))
        print("V10G_EQU_LABEL",json.dumps(result["label_discrimination"],separators=(",",":")))
    else:print("SOURCE_STOP",result.get("reason"))
if __name__=="__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "ecostate_v10/results/wolverine_source_label_leak_v10g.json")
