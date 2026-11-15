"""v157: cross-coast method-transfer to authentic 2026 Roscoff 26-sound XLSX.

Five original source-coefficient-stratified grouped period holdouts, NOT 5
independent coasts. The independent 2026 Roscoff coast differs from the
California source. PS and LPS were selected by *prevalence/source support*
in frozen v156; both are acoustic annotation labels, not verified fish species.

Models: constant; original night + genuine local water height + four tidal
coefficient categories; + same-label prior REAL recorded hour; + distinct
LPS label in same target hour. Second source-supported diagnostic also fits
the exact same models versus LPS on other source-selected 24h blocks,
matched on original tide-coefficient category and hour index. Two complete
source periods (+1/+2 among 5 of same class); high-tide flow masking may
prevent source labels, in which case all models use the same restricted
opportunities and STOP rather than replacing unknown LPS with zero.

This tests retrospective conditional acoustic information, NOT individual
fish social interaction, and not an actionable future forecast when B(t)
is only observed contemporaneously. The original source excluded 59 hours
nonrandomly by high tidal flow noise. All p-values intentionally omitted.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v139"))
from source_probe import acquire,read_xlsx_table_rows
from hourly_diagnostic import SOURCE_SHA,acol,number,key_from
from empirical_reanalysis import stratified_folds

QC=ROOT/"validation_v156/results/roscoff_original_26_soundtypes_source_gate_v156.json"
RECEIPT=ROOT/"validation_v157/results/frozen_roscoff_transfer_receipt_v157.json"
FULL=ROOT/"validation_v157/results/roscoff_original_transfer_full_v157.json"
COVARIATES=("night","measured_water_height_m","Medium","High","Very High")
MODELS=("constant","environment","own_previous_1h","real_partner")
GHOST_MODELS=MODELS+("wrong_source_day_plus1","wrong_source_day_plus2")
PENALTY_C=.25
MAXITER=400
MIN_PRIMARY_TRAIN=200
MIN_PRIMARY_TEST=40
MIN_GHOST_TRAIN=150
MIN_GHOST_TEST=25
MIN_TRAIN_POS=20
MIN_TRAIN_NEG=12
MIN_TEST_POS=2
MIN_TEST_NEG=2
MIN_PARTNER_TRAIN_POS=15
MIN_PARTNER_TEST_POS=2
MIN_SOURCE_MASK_PER_FOLD=0
CLIP=1e-6
LEVELS=("Low","Medium","High","Very High")

def source_rows():
    prior=json.loads(QC.read_text())
    if (prior["real_source_annotated_hours"]!=421
        or prior["source_flownoise_masked_hours"]!=59
        or prior["n_true_observed_previous_hour_pairs"]!=387
        or prior["n_acoustic_types_passing_all_five_grouped_holdouts"]!=24
        or prior["first_type_by_source_prevalence_for_next_exploratory_fit"]!="PS"
        or prior["second_type_by_source_prevalence_for_next_exploratory_fit"]!="LPS"):
        raise AssertionError("v156 source-only target preadmission changed")
    raw=acquire()
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=prior["original_workbook_sha256"] or digest!=SOURCE_SHA:
        raise AssertionError("New original Roscoff XLSX member SHA differs")
    tabs=read_xlsx_table_rows(raw)
    t=tabs["Table S1"]
    head=t[3]
    soundcols={acol(i):head.get(acol(i)) for i in range(16,42)}
    if len(soundcols)!=26 or len(set(soundcols.values()))!=26:
        raise AssertionError("Original named 26 acoustic labels changed")
    target=prior["first_type_by_source_prevalence_for_next_exploratory_fit"]
    partner=prior["second_type_by_source_prevalence_for_next_exploratory_fit"]
    periods=defaultdict(list)
    total_sounds=0
    for n,r in sorted(t.items()):
        if n<4:continue
        day,h=key_from(r.get("C"),r.get("D"))
        anchor=day if h>=12 else day-1
        idx=(day-anchor)*24+h-12
        if not 0<=idx<24:raise AssertionError("Original source period clock is not noon-noon")
        pid=str(int(float(r["B"])))
        count={}
        for col,name in soundcols.items():
            val=number(r.get(col))
            if val is None or val<0 or abs(round(val)-val)>1e-7:
                raise AssertionError("Original sound count not a nonnegative integer")
            count[name]=int(round(val))
        if sum(count.values())!=number(r.get("AP")) or sum(v>0 for v in count.values())!=number(r.get("AQ")):
            raise AssertionError("Original total/richness source row invalid")
        total_sounds+=sum(count.values())
        level=r.get("L")
        night=r.get("E")
        tide_m=number(r.get("J"))
        if level not in LEVELS or night not in ("Day","Night") or tide_m is None:
            raise AssertionError("Selected day-night/actual measured tide source fields missing")
        periods[pid].append({
            "source_period_id":pid,"source_anchor":anchor,"index":idx,
            "coefficient_level":level,"night":int(night=="Night"),
            "water_m":tide_m,"A":int(count[target]>0),"B":int(count[partner]>0),
            "all_source_labels_positive":{k:int(v>0) for k,v in count.items()}
        })
    if len(periods)!=20 or sum(len(v) for v in periods.values())!=421 or total_sounds!=6172:
        raise AssertionError("Original (20,421,6172) source scope changed")
    folds=stratified_folds(periods)
    byperiod={}
    level_ids=defaultdict(list)
    for pid,rows in periods.items():
        levels={row["coefficient_level"] for row in rows}
        anchors={row["source_anchor"] for row in rows}
        if len(levels)!=1 or len(anchors)!=1:
            raise AssertionError("Original 24h period source tide category or date changed")
        mapped={r["index"]:r for r in rows}
        if len(mapped)!=len(rows):
            raise AssertionError("Duplicate original source sampled hour")
        byperiod[pid]=mapped
        level_ids[next(iter(levels))].append(pid)
    mapping=make_ghost_periods(level_ids)
    eligible=[]
    for pid in sorted(byperiod,key=int):
        real=byperiod[pid]
        g1,g2=mapping[pid]
        for idx in sorted(real):
            if idx==0 or idx-1 not in real:
                continue
            row=real[idx]
            p=real[idx-1]
            if p["source_anchor"]!=row["source_anchor"] or p["index"]+1!=idx:
                raise AssertionError("Observed preceding source hour is not contiguous")
            ghost1=byperiod[g1].get(idx)
            ghost2=byperiod[g2].get(idx)
            eligible.append({
                "source_period_id":pid,"original_index_in_24h":idx,
                "fold":folds[pid],"coefficient_level":row["coefficient_level"],
                "A":row["A"],"A_previous":p["A"],"B":row["B"],
                "ghost1":ghost1["B"] if ghost1 is not None else None,
                "ghost2":ghost2["B"] if ghost2 is not None else None,
                "external":[row["night"],row["water_m"]-5.0]+
                            [int(row["coefficient_level"]==k) for k in LEVELS[1:]]
            })
    if len(eligible)!=387:
        raise AssertionError("Source gate 387 actually observed previous-hour pairs not reproduced")
    for tag in (target,partner):
        prev=next(x for x in prior["all_26_original_acoustic_type_source_support"] if x["original_type"]==tag)
        total=sum(r["A"] if tag==target else r["B"] for r in eligible)
        if total!=prev["n_soundtype_positive_with_actual_prev_hour"]:
            raise AssertionError("Selected original acoustic type source frequencies not reproduced")
    return eligible,folds,prior

def make_ghost_periods(level_period_ids):
    """Within EACH published tide-category (5 periods), pick two other source periods.
    This preserves hour of the *selected 24h sampling window*, not season
    or all of the original weather and is a diagnostic only.
    """
    if set(level_period_ids)!=set(LEVELS):raise ValueError("Original four tide levels missing")
    partners={}
    for level,pids in level_period_ids.items():
        p=sorted(pids,key=int)
        if len(p)!=5:
            raise AssertionError("Published tide-category 5 periods changed")
        for i,pid in enumerate(p):
            partners[pid]=(p[(i+1)%5],p[(i+2)%5])
            if pid in partners[pid]:
                raise AssertionError("Wrong-day ghost references itself")
    if len(partners)!=20:raise AssertionError("Need 20 source-period ghost references")
    return partners

def is_supported(train,test,with_ghost=False):
    q={"train_hours":len(train),"heldout_hours":len(test),
       "train_A_positive":sum(r["A"] for r in train),
       "heldout_A_positive":sum(r["A"] for r in test),
       "train_B_positive":sum(r["B"] for r in train),
       "heldout_B_positive":sum(r["B"] for r in test)}
    mintr=MIN_GHOST_TRAIN if with_ghost else MIN_PRIMARY_TRAIN
    minte=MIN_GHOST_TEST if with_ghost else MIN_PRIMARY_TEST
    okay=(
        len(train)>=mintr and len(test)>=minte
        and q["train_A_positive"]>=MIN_TRAIN_POS
        and q["heldout_A_positive"]>=MIN_TEST_POS
        and len(train)-q["train_A_positive"]>=MIN_TRAIN_NEG
        and len(test)-q["heldout_A_positive"]>=MIN_TEST_NEG
        and q["train_B_positive"]>=MIN_PARTNER_TRAIN_POS
        and q["heldout_B_positive"]>=MIN_PARTNER_TEST_POS
        and len(train)-q["train_B_positive"]>=MIN_TRAIN_NEG
        and len(test)-q["heldout_B_positive"]>=MIN_TEST_NEG
    )
    return okay,q

def predict_fixed(train,test,model):
    a=np.asarray([r["A"] for r in train],dtype=np.int8)
    if model=="constant":return np.full(len(test),float(a.mean()))
    def build(rows):
        a=np.asarray([r["external"] for r in rows],dtype=np.float64)
        if model=="environment":return a
        own=np.asarray([r["A_previous"] for r in rows],dtype=np.float64)
        a=np.column_stack([a,own])
        if model=="own_previous_1h":return a
        key=({"real_partner":"B","wrong_source_day_plus1":"ghost1",
              "wrong_source_day_plus2":"ghost2"})[model]
        v=np.asarray([r[key] for r in rows],dtype=np.float64)
        if not np.isfinite(v).all():
            raise AssertionError("Missing ghost sound classified as 0 or 1")
        return np.column_stack([a,v])
    xtrain=build(train)
    xtest=build(test)
    scale=StandardScaler()
    xtr=scale.fit_transform(xtrain)
    xte=scale.transform(xtest)
    clf=LogisticRegression(C=PENALTY_C,solver="lbfgs",max_iter=MAXITER,
                            tol=1e-6,random_state=20261115)
    clf.fit(xtr,a)
    return clf.predict_proba(xte)[:,1]

def losses(y,p):
    p=np.clip(np.asarray(p),CLIP,1-CLIP)
    y=np.asarray(y,dtype=float)
    ll=-y*np.log(p)-(1-y)*np.log1p(-p)
    b=(y-p)**2
    return ll,b

def cv_dataset(rows,folds,ghost=False):
    models=GHOST_MODELS if ghost else MODELS
    fold_rows=[];period_score=defaultdict(lambda:{m:[] for m in models})
    totals={m:[] for m in models}
    heldout_real_hours=0
    for fold in range(5):
        tr=[r for r in rows if r["fold"]!=fold]
        te=[r for r in rows if r["fold"]==fold]
        okay,quality=is_supported(tr,te,with_ghost=ghost)
        if not okay:
            fold_rows.append({"fold":fold,"status":"STOP_FOLD_ACOUSTIC_SOURCE_SUPPORT",
                              **quality})
            continue
        heldout_real_hours+=len(te)
        observed=np.asarray([r["A"] for r in te],dtype=float)
        pred={m:predict_fixed(tr,te,m) for m in models}
        foldlog={}
        foldbrier={}
        for name in models:
            ll,b=losses(observed,pred[name])
            totals[name].extend(ll.tolist())
            foldlog[name]=float(np.mean(ll))
            foldbrier[name]=float(np.mean(b))
            for row,score in zip(te,ll.tolist()):
                period_score[row["source_period_id"]][name].append(score)
        gains={
            "environment_over_constant":foldlog["constant"]-foldlog["environment"],
            "self_over_environment":foldlog["environment"]-foldlog["own_previous_1h"],
            "same_hour_B_over_self":foldlog["own_previous_1h"]-foldlog["real_partner"],
        }
        if ghost:
            gains.update({
                "ghost1_over_self":foldlog["own_previous_1h"]-foldlog["wrong_source_day_plus1"],
                "ghost2_over_self":foldlog["own_previous_1h"]-foldlog["wrong_source_day_plus2"],
                "real_B_over_best_ghost":min(foldlog["wrong_source_day_plus1"],
                                             foldlog["wrong_source_day_plus2"])-foldlog["real_partner"],
            })
        fold_rows.append({
            "fold":fold,"status":"EVALUATED_COMPLETE_SOURCE_PERIODS",
            **quality,
            "logloss_nats_per_retained_original_hour":{k:round(v,8) for k,v in foldlog.items()},
            "brier_score_original_hour":{k:round(v,8) for k,v in foldbrier.items()},
            "gain_nats_per_original_hour":{k:round(v,8) for k,v in gains.items()},
        })
    full_folds=len([r for r in fold_rows if r["status"]=="EVALUATED_COMPLETE_SOURCE_PERIODS"])==5
    if not full_folds:
        return {"status":"STOP_NOT_ALL_FIVE_FOLDS_SUPPORTED",
                "n_source_eligible_hours":len(rows),
                "five_original_tide_stratified_folds":fold_rows,
                "no_heldout_pooled_claim":True}
    # Each retained sample is evaluated once in its original complete 24h period holdout.
    if heldout_real_hours!=len(rows) or any(len(totals[k])!=len(rows) for k in models):
        raise AssertionError("Heldout source test did not cover identical sound-hour responses")
    logloss={k:float(np.mean(v)) for k,v in totals.items()}
    gains={
        "environment_over_constant":logloss["constant"]-logloss["environment"],
        "self_over_environment":logloss["environment"]-logloss["own_previous_1h"],
        "same_hour_B_over_self":logloss["own_previous_1h"]-logloss["real_partner"],
    }
    if ghost:
        gains.update({
            "ghost1_over_self":logloss["own_previous_1h"]-logloss["wrong_source_day_plus1"],
            "ghost2_over_self":logloss["own_previous_1h"]-logloss["wrong_source_day_plus2"],
            "real_B_over_best_ghost":min(logloss["wrong_source_day_plus1"],
                                        logloss["wrong_source_day_plus2"])-logloss["real_partner"],
        })
    byperiod={}
    for pid,series in sorted(period_score.items(),key=lambda x:int(x[0])):
        metrics={m:float(np.mean(s)) for m,s in series.items()}
        byperiod[pid]={
            "retained_real_source_hours":len(series["constant"]),
            "gain_nats_per_source_hour":{
                "environment_over_constant":round(metrics["constant"]-metrics["environment"],8),
                "self_over_environment":round(metrics["environment"]-metrics["own_previous_1h"],8),
                "same_hour_B_over_self":round(metrics["own_previous_1h"]-metrics["real_partner"],8),
                **({
                    "ghost1_over_self":round(
                        metrics["own_previous_1h"]-metrics["wrong_source_day_plus1"],8),
                    "ghost2_over_self":round(
                        metrics["own_previous_1h"]-metrics["wrong_source_day_plus2"],8),
                    "real_B_over_best_ghost":round(
                        min(metrics["wrong_source_day_plus1"],metrics["wrong_source_day_plus2"])
                        -metrics["real_partner"],8)
                } if ghost else {})
            }
        }
    return {
        "status":"EVALUATED_20_SOURCE_PERIODS_FIVEFOLD",
        "n_source_eligible_hours":len(rows),
        "n_original_periods":len(byperiod),
        "model_heldout_logloss_nats_per_original_hour":{k:round(v,8) for k,v in logloss.items()},
        "gain_nats_per_original_hour":{k:round(v,8) for k,v in gains.items()},
        "positive_folds_by_gain":{
            g:sum(z["gain_nats_per_original_hour"][g]>0 for z in fold_rows)
            for g in gains
        },
        "original_periods_with_positive_gain":{
            g:sum(z["gain_nats_per_source_hour"][g]>0 for z in byperiod.values()
                  if g in z["gain_nats_per_source_hour"])
            for g in gains
        },
        "five_original_tide_stratified_folds":fold_rows,
        "source_period_heldout_score":byperiod,
        "standard_errors_and_p_values":"NOT_COMPUTED",
    }

def run():
    rows,folds,sourceqc=source_rows()
    common=[r for r in rows if r["ghost1"] is not None and r["ghost2"] is not None]
    if not common or len(common)>len(rows):
        raise AssertionError("No source-comparable acoustic ghost opportunities")
    quality={
        "original_annotated_hours":421,
        "same_source_real_previous_hour_eligible":len(rows),
        "source_true_previous_hour_not_observed":34,
        "common_real_previous_and_two_source_class_clock_ghosts":len(common),
        "source_true_previous_lost_to_missing_ghost":len(rows)-len(common),
        "original_selected_tidal_24h_periods":20,
        "n_source_acoustic_type_labels":26,
        "original_flow_masked_hours":59,
        "day_period_folds":dict(sorted(folds.items(),key=lambda x:int(x[0]))),
        "fold_real_source_hours":dict(sorted(Counter(r["fold"] for r in rows).items())),
        "fold_ghost_comparable_source_hours":dict(sorted(Counter(r["fold"] for r in common).items())),
    }
    primary=cv_dataset(rows,folds,ghost=False)
    secondary=cv_dataset(common,folds,ghost=True)
    result={
        "version":"v157_Roscoff_original_independent_coast_acoustic_method_transfer_1",
        "Roscoff_primary_DOI":"10.1186/s12862-026-02521-z",
        "Roscoff_original_XLSX_sha256":SOURCE_SHA,
        "Roscoff_source_reread_verified_bytes":True,
        "original_v156_26_sound_type_source_gate_reproduced":True,
        "original_source_supplement_schema":"Table S1 original hour column P:AO 26 source sound types",
        "model_target_sound_label_source_rank":"PS",
        "model_partner_sound_label_source_rank":"LPS",
        "labels_are_26_acoustic_types_not_26_identified_species":True,
        "reference_study":"California Kim 2025 same observation hierarchy, different sampling grain and source cohort",
        "source_quality":quality,
        "fixed_design":{
            "five_fold_policy":"4 original noon-noon periods per fold, one source block from each of 4 original tide coefficient categories",
            "covariates":list(COVARIATES),
            "model_order_all_source_hours":list(MODELS),
            "model_order_ghost_supported":list(GHOST_MODELS),
            "train_only_standardization":True,
            "logistic_C_fixed":PENALTY_C,"maxiter_fixed":MAXITER,
            "minimum_fold_train":MIN_PRIMARY_TRAIN,
            "minimum_fold_test":MIN_PRIMARY_TEST,
            "minimum_ghost_fold_train":MIN_GHOST_TRAIN,
            "minimum_ghost_fold_test":MIN_GHOST_TEST,
            "minimum_train_positive_and_negative_for_target":[MIN_TRAIN_POS,MIN_TRAIN_NEG],
            "minimum_holdout_positive_and_negative_for_target":[MIN_TEST_POS,MIN_TEST_NEG],
            "minimum_train_and_test_partner_positive":[MIN_PARTNER_TRAIN_POS,MIN_PARTNER_TEST_POS],
            "ghost_assignment":"two OTHER source-selected 24h periods +1/+2 among five same original tide class periods, same noon-window hour; actual source sound labels only, no missing-as-zero",
            "all_comparators_scored_on_identical_observed_hours_in_each_analysis":True,
            "no_model_selection_from_v157_outcome":True,
        },
        "primary_full_true_previous_source_hours":primary,
        "secondary_same_source_ghost_comparable_hours":secondary,
        "original_audio_mask_missing_not_equated_to_zero":True,
        "conditional_samehour_other_sound_not_future_prospective":True,
        "ghost_uses_other_selected_days_not_future_available":True,
        "different_original_coastlines_in_combined_project":2,
        "two_coast_valid_meta_effects":0,
        "direct_fish_interaction":"NOT_IDENTIFIED",
        "global_tide_solar_biological_effect":"NOT_ESTIMATED",
    }
    return result

def compact_receipt(result):
    canon=json.dumps(result,ensure_ascii=True,sort_keys=True,separators=(",",":"))
    out={
        "version":result["version"],
        "source_original_workbook_SHA256_verified":True,
        "canonical_full_original_source_result_SHA256":hashlib.sha256(canon.encode()).hexdigest(),
        "canonical_full_original_source_result_bytes":len(canon.encode()),
        "source_quality":result["source_quality"],
        "fixed_design":result["fixed_design"],
        "primary":{k:v for k,v in result["primary_full_true_previous_source_hours"].items()
                   if k not in ("source_period_heldout_score",)},
        "ghost":{k:v for k,v in result["secondary_same_source_ghost_comparable_hours"].items()
                 if k not in ("source_period_heldout_score",)},
        "no_interspecific_fish_behavior_or_metametric_estimated":True,
    }
    return out

def main():
    p=argparse.ArgumentParser()
    v=p.add_mutually_exclusive_group(required=True)
    v.add_argument("--emit",action="store_true")
    v.add_argument("--check",action="store_true")
    a=p.parse_args()
    result=run()
    receipt=compact_receipt(result)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    if a.check:
        if not RECEIPT.is_file():raise AssertionError("Original v157 Roscoff source receipt absent")
        old=json.loads(RECEIPT.read_text())
        differences=[]
        def check(p,x,y):
            if len(differences)>=30:return
            if p in ("root.canonical_full_original_source_result_SHA256",
                     "root.canonical_full_original_source_result_bytes"):
                return
            if type(x)!=type(y):differences.append([p,str(type(x)),str(type(y))])
            elif isinstance(x,dict):
                if set(x)!=set(y):differences.append([p,"KEYS",sorted(x),sorted(y)])
                else:
                    for k in sorted(x):check(p+"."+str(k),x[k],y[k])
            elif isinstance(x,list):
                if len(x)!=len(y):differences.append([p,"LENGTH",len(x),len(y)])
                else:
                    for i in range(len(x)):check(p+"["+str(i)+"]",x[i],y[i])
            elif isinstance(x,float):
                if not (math.isfinite(x) and math.isfinite(y)) or abs(x-y)>1e-7:
                    differences.append([p,x,y])
            elif x!=y:differences.append([p,x,y])
        # JSON serialization may convert int fold keys to strings; compare
        # typed, canonical JSON objects for source identity.
        check("root",json.loads(json.dumps(receipt,sort_keys=True)),old)
        if differences:
            print("V157_REPLAY_DIAGNOSTIC="+json.dumps(differences,ensure_ascii=True))
            raise AssertionError("Original Roscoff source/model receipt changed")
        print("V157_ORIGINAL_ROSCOFF_SOURCE_HELDOUT_REPLAY_PASS")
    else:
        print("V157_SOURCE_RECEIPT_START")
        print(json.dumps(receipt,ensure_ascii=True,sort_keys=True,separators=(",",":")))
        print("V157_SOURCE_RECEIPT_END")
    print("V157_PUBLIC_SUMMARY="+json.dumps({
        "scope":receipt["source_quality"],
        "primary":{k:v for k,v in receipt["primary"].items() if k not in ("five_original_tide_stratified_folds",)},
        "ghost":{k:v for k,v in receipt["ghost"].items() if k not in ("five_original_tide_stratified_folds",)}
    },ensure_ascii=True,sort_keys=True))

if __name__=="__main__":main()
