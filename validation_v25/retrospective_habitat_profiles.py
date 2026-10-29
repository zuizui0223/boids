#!/usr/bin/env python3
"""v25-C frozen USGS original *paired aggregate habitat-profile* prediction.

NOT 101 discrete alternatives, NOT ex-ante step choice. Uses original
case TRUE-vs-FALSE pair (original FALSE is an author-created availability
profile summary), no source start-coordinate or GPS random alternative
locations. All birds held out by birdyear token. Personal historical
environmental differences are updated ONLY after scoring earlier steps.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

import usgs_step_manifest_gate as usgs
import usgs_step_schema_gate as schema

ORIGINAL_SOURCE_FILE="Data Release P9ELSUHN.csv"
ORIGINAL_SOURCE_SHA256="1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15"
ORIGINAL_ROWS=380578
ORIGINAL_PAIRS=190289
ORIGINAL_BIRDYEAR_IDS=493
COLUMNS=("birdyear","timestamp","species","case","season","photoperiod",
         "Corn","Field","Other","Protected","Rice","Urban","Wetland")
ENV=("Corn","Field","Other","Protected","Rice","Urban","Wetland")
SOURCE_TAXA=("GWFG","LSGO","MALL","NOPI")
SOURCE_SEASONS=("Breeding","Early Winter","Late Winter")
SOURCE_PHOTOPERIOD=("day","night")
N_FOLDS=5
MIN_OWN_EARLIER_PAIRED_EVENTS=3
MIN_EVALUATED_BIRDYEAR=100
MIN_EVALUATED_PAIRS=1000
C=1.0
MAX_ITER=400
RANDOM_SEED=20261029
SHRINK_KAPPA=2.0
BOOTSTRAP_RESAMPLES=10000
M0_LOGLOSS=float(math.log(2.))


def birdyear_fold(birdyear: str) -> int:
    h=hashlib.sha256(birdyear.encode("utf-8")).digest()
    return int.from_bytes(h,"big")%N_FOLDS


def original_source_paired_profile(path:Path)->tuple[pd.DataFrame,dict]:
    df=pd.read_csv(path,dtype={
        "birdyear":"string","timestamp":"string","species":"string",
        "case":"string","season":"string","photoperiod":"string",
    },low_memory=False)
    if tuple(df.columns)!=COLUMNS or len(df)!=ORIGINAL_ROWS:
        raise ValueError("Original source 13-column/380578 row contract changed")
    if df[list(COLUMNS[:6])].isna().any().any():
        raise ValueError("Original source categorical/ID/time missing")
    if set(df["case"])!={"TRUE","FALSE"}:
        raise ValueError("Original case labels changed")
    if set(df["species"])!=set(SOURCE_TAXA):
        raise ValueError("Original source taxa labels changed")
    if set(df["season"])!=set(SOURCE_SEASONS):
        raise ValueError("Original source seasons changed")
    if set(df["photoperiod"])!=set(SOURCE_PHOTOPERIOD):
        raise ValueError("Original source day/night classes changed")
    # Only now (AFTER separate pre-outcome contract) inspect numeric source
    # environmental profile values on case TRUE and source FALSE profiles.
    for name in ENV:
        vals=pd.to_numeric(df[name],errors="raise").to_numpy(float)
        if (not np.isfinite(vals).all()
            or vals.min()<0 or vals.max()>1):
            raise ValueError("Original numeric habitat composition domain violated: "+name)
        df[name]=vals
    if df.duplicated(["birdyear","timestamp","case"]).any():
        raise ValueError("Original repeated case within source stratum")
    group=df.groupby(["birdyear","timestamp"],sort=False)["case"].agg(
        rows="size",n_true=lambda x:(x=="TRUE").sum())
    if (len(group)!=ORIGINAL_PAIRS or
        not (group["rows"]==2).all() or
        not (group["n_true"]==1).all()):
        raise ValueError("Original one TRUE and one FALSE per matched source pair no longer holds")
    left=df[df["case"]=="TRUE"].set_index(["birdyear","timestamp"]).sort_index()
    right=df[df["case"]=="FALSE"].set_index(["birdyear","timestamp"]).sort_index()
    if not left.index.equals(right.index):
        raise ValueError("Matched source TRUE/FALSE birdyear and time keys differ")
    for meta in ("species","season","photoperiod"):
        if not (left[meta].to_numpy()==right[meta].to_numpy()).all():
            raise ValueError("Source pair TRUE/FALSE context disagrees: "+meta)
    d=left[list(ENV)].to_numpy(float)-right[list(ENV)].to_numpy(float)
    timestamps=pd.to_datetime(left.index.get_level_values("timestamp"),
                              format="%m/%d/%Y %H:%M",errors="raise")
    pairs=pd.DataFrame({
        "birdyear":left.index.get_level_values("birdyear").astype(str),
        "timestamp":timestamps,
        "year":timestamps.year.to_numpy(),
        "species":left["species"].to_numpy(dtype=str),
        "season":left["season"].to_numpy(dtype=str),
        "photoperiod":left["photoperiod"].to_numpy(dtype=str),
    })
    for ix,key in enumerate(ENV):
        pairs["d_"+key]=d[:,ix]
    if pairs["birdyear"].nunique()!=ORIGINAL_BIRDYEAR_IDS:
        raise ValueError("Original source 493 birdyear IDs changed")
    pair_years=pairs.groupby("birdyear")["year"].nunique()
    return pairs,{
        "source_rows":len(df),
        "source_matched_TRUE_FALSE_profile_pairs":len(pairs),
        "source_birdyear_tokens":pairs["birdyear"].nunique(),
        "source_year_counts_by_used_profile_pair":{
           str(y):int(v) for y,v in pairs["year"].value_counts().sort_index().items()},
        "source_taxon_pair_counts":{
           str(y):int(v) for y,v in pairs["species"].value_counts().sort_index().items()},
        "source_season_pair_counts":{
           str(y):int(v) for y,v in pairs["season"].value_counts().sort_index().items()},
        "source_photoperiod_pair_counts":{
           str(y):int(v) for y,v in pairs["photoperiod"].value_counts().sort_index().items()},
        "birdyears_with_more_than_one_calendar_year":int((pair_years>1).sum()),
        "actual_100_random_candidate_destinations_available":False,
        "source_TRUE_FALSE_is_retroactive_aggregated_comparison":True,
        "original_habitat_row_values_republished":False
    }


def env_difference(pairs:pd.DataFrame)->np.ndarray:
    return pairs[["d_"+x for x in ENV]].to_numpy(float)


def individual_model_input(d:np.ndarray,taxa:np.ndarray)->np.ndarray:
    # Taxon-specific environmental slopes but no taxon-only origin bias.
    onehot=np.zeros((len(taxa),len(SOURCE_TAXA)),dtype=float)
    for j,t in enumerate(SOURCE_TAXA):
        onehot[:,j]=(taxa==t)
    interactions=(onehot[:,:,None]*d[:,None,:]).reshape(len(d),-1)
    return np.column_stack([d,interactions])


def train_equal_birdyear_logit(pairs:pd.DataFrame,individual_species:bool=False)->np.ndarray:
    d=env_difference(pairs)
    if not len(d):raise ValueError("No training pairs")
    x=individual_model_input(d,pairs["species"].to_numpy()) if individual_species else d
    count=pairs.groupby("birdyear")["birdyear"].transform("size").to_numpy(float)
    w=.5/count
    mirror=np.vstack([x,-x])
    target=np.concatenate([np.ones(len(d),dtype=int),
                           np.zeros(len(d),dtype=int)])
    source_weights=np.concatenate([w,w])
    reg=LogisticRegression(penalty="l2",C=C,fit_intercept=False,
                           solver="liblinear",max_iter=MAX_ITER,
                           random_state=RANDOM_SEED)
    reg.fit(mirror,target,sample_weight=source_weights)
    if not np.isfinite(reg.coef_).all():
        raise ValueError("Source original linear model coefficients nonfinite")
    return reg.coef_[0]


def logistic_loss(scores:np.ndarray)->np.ndarray:
    return np.logaddexp(0.,-scores)


def rank_score(scores:np.ndarray)->np.ndarray:
    return (scores>0).astype(float)+.5*(scores==0)


def test_birdyear_holdout(pairs:pd.DataFrame,global_beta:np.ndarray,
                          species_beta:np.ndarray)->list[dict]:
    # The held-out birdyear's 7 environmental features are known only for
    # evaluating the retrospective paired source aggregate TRUE/FALSE.
    # Its PRIVATE history is strictly earlier observed TRUE-FALSE profiles.
    data=pairs.sort_values(["birdyear","timestamp"]).copy()
    d=env_difference(data)
    taxon_data=data["species"].to_numpy(dtype=str)
    m1=d@global_beta
    m2=individual_model_input(d,taxon_data)@species_beta
    m3=np.full(len(data),np.nan)
    eligible=np.zeros(len(data),dtype=bool)
    norms=float(np.linalg.norm(global_beta))
    # Focal group's same-time observations NEVER update the prior before score.
    for _,indices in data.groupby("birdyear",sort=False).indices.items():
        previous=np.zeros(len(ENV),dtype=float)
        count=0
        for index in indices:
            # groupby indices are 0..N−1 positions from data frame.
            if count>=MIN_OWN_EARLIER_PAIRED_EVENTS:
                m=previous/count
                norm=float(np.linalg.norm(m))
                personal=(norms*m/(norm+1e-12)) if norm>1e-12 else np.zeros_like(m)
                fraction=count/(count+SHRINK_KAPPA)
                mixed=(1.-fraction)*global_beta+fraction*personal
                m3[index]=float(d[index]@mixed)
                eligible[index]=True
            previous+=d[index]
            count+=1
    eligible_index=np.flatnonzero(eligible)
    result=[]
    for pos in eligible_index:
        row=data.iloc[pos]
        result.append({
            "birdyear":row["birdyear"],
            "taxon":row["species"],
            "season":row["season"],
            "photoperiod":row["photoperiod"],
            "year":int(row["year"]),
            "loss_M0":M0_LOGLOSS,
            "loss_M1":float(logistic_loss(m1[pos])),
            "loss_M2":float(logistic_loss(m2[pos])),
            "loss_M3":float(logistic_loss(m3[pos])),
            "rank_M0":.5,
            "rank_M1":float(rank_score(m1[pos])),
            "rank_M2":float(rank_score(m2[pos])),
            "rank_M3":float(rank_score(m3[pos])),
        })
    return result


def all_fold_results(pairs:pd.DataFrame)->tuple[list[dict],dict]:
    source=pairs.copy()
    source["_fold"]=[birdyear_fold(x) for x in source["birdyear"]]
    all_scores=[]
    fold_qc={}
    for f in range(N_FOLDS):
        training=source[source["_fold"]!=f]
        test=source[source["_fold"]==f]
        if training.empty or test.empty:
            raise ValueError("Precommitted fold contains no birdyear")
        if set(training["birdyear"]) & set(test["birdyear"]):
            raise ValueError("Birdyear training/test identity leakage")
        beta=train_equal_birdyear_logit(training,False)
        bspecies=train_equal_birdyear_logit(training,True)
        scored=test_birdyear_holdout(test,beta,bspecies)
        all_scores.extend(scored)
        fold_qc[str(f)]={
            "source_training_birdyears":int(training["birdyear"].nunique()),
            "source_test_birdyears":int(test["birdyear"].nunique()),
            "test_source_PROFILE_pairs":int(len(test)),
            "future_test_pairs_scored_after_first_three_source_times":len(scored),
            "model_training_contains_target_birdyear":False,
            "environment_coefficients_fit_from_other_birdyears_only":True,
        }
    return all_scores,fold_qc


def cluster_stats(scores:list[dict])->dict:
    by=collections.defaultdict(list)
    for r in scores:
        by[r["birdyear"]].append(r)
    if len(by)<MIN_EVALUATED_BIRDYEAR or len(scores)<MIN_EVALUATED_PAIRS:
        return {"status":"NOT_ADMITTED_TOO_FEW_ORIGINAL_BIRDYEAR_HISTORY_TESTS",
                "source_birdyears":len(by),"test_pairs":len(scores),
                "any_habitat_effect_score_exported":False}
    per={}
    for ix,birdyear in enumerate(sorted(by),1):
        records=by[birdyear]
        means=np.mean([[x["loss_M0"],x["loss_M1"],x["loss_M2"],x["loss_M3"]]
                       for x in records],axis=0)
        ranks=np.mean([[x["rank_M0"],x["rank_M1"],x["rank_M2"],x["rank_M3"]]
                       for x in records],axis=0)
        per[f"source_birdyear_{ix:03d}"]={
            "source_test_profile_pairs":len(records),
            "original_taxon":records[0]["taxon"],
            "original_calendar_years":sorted(set(int(x["year"]) for x in records)),
            "original_seasons_present":sorted(set(x["season"] for x in records)),
            "original_photoperiods_present":sorted(set(x["photoperiod"] for x in records)),
            "mean_surrogate_logloss_M0_M1_M2_M3":list(map(float,means)),
            "mean_pair_profile_ranking_M0_M1_M2_M3":list(map(float,ranks)),
            "primary_M1_minus_M3":float(means[1]-means[3]),
            "secondary_M0_minus_M1":float(means[0]-means[1]),
            "secondary_M1_minus_M2":float(means[1]-means[2]),
        }
    table=np.array([r["mean_surrogate_logloss_M0_M1_M2_M3"]
                    for r in per.values()])
    rng=np.random.default_rng(RANDOM_SEED)
    resample=rng.integers(0,len(per),size=(BOOTSTRAP_RESAMPLES,len(per)))
    contrasts={
        "primary_private_habitat_history_M1_minus_M3":table[:,1]-table[:,3],
        "secondary_common_environment_M0_minus_M1":table[:,0]-table[:,1],
        "secondary_species_environment_M1_minus_M2":table[:,1]-table[:,2],
        "secondary_total_history_M0_minus_M3":table[:,0]-table[:,3],
    }
    out={}
    for name,gain in contrasts.items():
        lo,hi=np.quantile(gain[resample].mean(axis=1),[.025,.975])
        out[name]={
            "equal_birdyear_mean_surrogate_logloss_gain":float(gain.mean()),
            "positive_original_birdyear_tokens":int((gain>0).sum()),
            "n_original_birdyear_tokens":len(gain),
            "whole_birdyear_bootstrap_95_percentile":[float(lo),float(hi)]}
    return {
        "status":"EXPLORATORY_USGS_AGGREGATED_HABITAT_PROFILE_BIRDYEAR_TRANSFER",
        "original_independent_source_birdyear_tokens":len(per),
        "original_chronologically_later_aggregate_profile_pairs_scored":len(scores),
        "source_pair_aggregate_surrogate_not_real_two_site_choice":True,
        "source_perennial_individual_IDs_unknown":True,
        "whole_birdyear_equal_mean_surrogate_logloss_M0_M1_M2_M3":
            list(map(float,table.mean(axis=0))),
        "whole_birdyear_equal_mean_profile_ranking_M0_M1_M2_M3":
            list(map(float,np.mean([r["mean_pair_profile_ranking_M0_M1_M2_M3"]
                                    for r in per.values()],axis=0))),
        "frozen_contrasts":out,
        "source_birdyear_anonymized":per,
        "no_real_before_step_destinations_or_100_options":True,
    }


def leave_entire_calendar_year_out(pairs:pd.DataFrame)->dict:
    out={}
    for year in sorted(set(int(y) for y in pairs["year"])):
        test=pairs[pairs["year"]==year]
        train=pairs[pairs["year"]!=year]
        # Prevent a birdyear token seen in multiple calendar years from
        # leaking into training in a year-transfer diagnostic.
        holdout=set(test["birdyear"])
        train=train[~train["birdyear"].isin(holdout)]
        if test.empty or train.empty:
            out[str(year)]={"status":"NOT_ADMITTED_YEAR_SPLIT_SOURCE"}
            continue
        beta=train_equal_birdyear_logit(train,False)
        by=collections.defaultdict(list)
        for _,r in test.iterrows():
            d=np.asarray([float(r["d_"+k]) for k in ENV])
            loss=float(logistic_loss(d@beta))
            by[r["birdyear"]].append(loss)
        vals=[float(np.mean(v)) for v in by.values()]
        out[str(year)]={
            "source_test_birdyear_tokens":len(by),
            "source_test_original_profile_pairs":len(test),
            "source_train_birdyears_with_test_birdyears_excluded":
                int(train["birdyear"].nunique()),
            "source_M1_environment_only_mean_surrogate_logloss":
                float(np.mean(vals)),
            "source_M0_uniform_surrogate_logloss":M0_LOGLOSS,
            "source_model_trained_on_same_calendar_year":False,
            "source_original_100_candidates_recovered":False,
        }
    return out


def run()->dict:
    item=None;errors=[]
    for url in usgs.ENDPOINTS:
        try:
            item=usgs.original_item(usgs.original_json(url))
            break
        except Exception as e:
            errors.append({"url":url,"error":usgs.error(e)})
    receipt={
       "study":"v25-C-independent-USGS-2023-original-waterfowl-aggregate-retrospective-profile",
       "original_source_DOI":usgs.SOURCE_DOI,
       "registered_before_numeric_outcomes":
          "docs/V25_FROZEN_RETROSPECTIVE_WATERFOWL_PROFILE_PREDICTION.md",
       "status":"NOT_ADMITTED_SOURCE_UNAVAILABLE",
       "source_errors":errors,
       "source_file_integrity":None,
       "source_original_aggregate_structure":None,
       "source_year_holdout_results":None,
       "fixed_five_fold_source":None,
       "registered_prediction_result":None,
       "original_100_candidate_destinations_not_recovered":True,
       "source_Birdyear_not_certified_individuals":True,
       "no_original_animal_GPS_coordinates_or_numeric_habitat_rows_exported":True,
       "prior_v13_through_v24_frozen_endpoints_untouched":True,
    }
    if item is None:return receipt
    original_file=schema.select_files(item)[ORIGINAL_SOURCE_FILE]
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/ORIGINAL_SOURCE_FILE
        try:
            source=schema.fetch_verified(ORIGINAL_SOURCE_FILE,original_file,path)
            if source["original_independent_sha256"]!=ORIGINAL_SOURCE_SHA256:
                raise ValueError("Frozen original USGS CSV hash changed")
            pairs,qc=original_source_paired_profile(path)
            scores,folds=all_fold_results(pairs)
            result=cluster_stats(scores)
            years=leave_entire_calendar_year_out(pairs)
            receipt.update({
                "source_file_integrity":source,
                "source_original_aggregate_structure":qc,
                "source_year_holdout_results":years,
                "fixed_five_fold_source":folds,
                "registered_prediction_result":result,
                "status":result["status"]})
        except Exception as e:
            receipt["status"]="NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE"
            receipt["source_model_stop_reason"]=type(e).__name__+": "+str(e)[:250]
    return receipt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "validation_v25/results/usgs_paired_habitat_profile_model_v25.json"))
    args=parser.parse_args()
    r=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V25_C_ORIGINAL_SOURCE_HASH",json.dumps(r["source_file_integrity"],sort_keys=True))
    print("V25_C_SOURCE_PROFILE_SUPPORT",json.dumps(r["source_original_aggregate_structure"],sort_keys=True))
    print("V25_C_STATUS",r["status"])
    if r["registered_prediction_result"]:
        x=r["registered_prediction_result"]
        print("V25_C_FROZEN_EFFECTS",json.dumps(x.get("frozen_contrasts"),sort_keys=True))
        print("V25_C_MODEL_ABSOLUTE",json.dumps({
            "logloss":x.get("whole_birdyear_equal_mean_surrogate_logloss_M0_M1_M2_M3"),
            "ranking":x.get("whole_birdyear_equal_mean_profile_ranking_M0_M1_M2_M3"),
            "birdyears":x.get("original_independent_source_birdyear_tokens"),
            "pairs":x.get("original_chronologically_later_aggregate_profile_pairs_scored")},sort_keys=True))
        print("V25_C_YEAR_HOLDOUT",json.dumps(r["source_year_holdout_results"],sort_keys=True))
        print("V25_C_EVERY_ANON_BIRDYEAR",json.dumps(x.get("source_birdyear_anonymized"),sort_keys=True))
    else:
        print("V25_C_HARD_STOP",json.dumps(r.get("source_model_stop_reason"),sort_keys=True))
    print("V25_C_NOT_101_OPTIONAL_REAL_FUTURE_CHOICES_OR_COGNITIVE_MEMORY")

if __name__=="__main__":
    main()
