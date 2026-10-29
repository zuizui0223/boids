#!/usr/bin/env python3
"""v28-C1 original noctule bat heldout-ID RSF environmental/turbine predictor.

Strict SOURCE use-versus-generated-availability within flight, NOT actual
101 destination choice or causal wind avoidance. Entire bat ID held out;
original tracks are repeated within bats, never IID observations. NO UTM
coordinates, original GPS height or bat interaction forces are read.
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
from sklearn.metrics import roc_auc_score, log_loss
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import original_source_manifest as z
import three_file_source_gate as original

SOURCE_FILE="Model_dataset_RSFFlight_Complete_EPSG25833.csv"
SOURCE_SHA256="76f92b1442eb4350ee6d83ede83b5e43fda4b9f3997e3fd9a3618a44f2470375"
SOURCE_ROWS=48774
SOURCE_BATS=60
SOURCE_TRACKS=107
SOURCE_TRUE=8129
SOURCE_FALSE=40645
MIN_TRUE_PER_BAT=10
MIN_FALSE_PER_BAT=40
CATEGORICAL=("clc2_20m","forestornot")
NUMERIC=("DistanceAssumedRoostsInKm","mindist_WKA_inKm")
META=("batid","trackid","case_","response_rvso","field_period","sex","age_class")
C_VALUE=1.0
MAX_ITER=400
N_FOLDS=5
RANDOM_SEED=20261029
BOOT_REPS=10000


def bat_fold(bat_id:str)->int:
    return int(hashlib.sha256(bat_id.encode("utf-8")).hexdigest(),16)%N_FOLDS


def source_table(path:Path)->tuple[pd.DataFrame,dict]:
    cols=list((*META,*CATEGORICAL,*NUMERIC))
    source_types={v:"string" for v in (*META,*CATEGORICAL)}
    df=pd.read_csv(path,usecols=cols,dtype=source_types,low_memory=False)
    if len(df)!=SOURCE_ROWS or set(df.columns)!=set(cols):
        raise ValueError("Original bat RSF table size or source predictor schema changed")
    if df[list(META)].isna().any().any() or df[list(CATEGORICAL)].isna().any().any():
        raise ValueError("Original ID/trip or categorical field missing")
    if set(df["case_"])!={"TRUE","FALSE"} or not (
        (df["case_"]=="TRUE").sum()==SOURCE_TRUE and
        (df["case_"]=="FALSE").sum()==SOURCE_FALSE):
        raise ValueError("Original case source categories changed")
    if not (
        ((df["case_"]=="TRUE") & (df["response_rvso"]=="1") |
         (df["case_"]=="FALSE") & (df["response_rvso"]=="0")).all()):
        raise ValueError("Original case_ vs independently encoded source response disagree")
    for v in NUMERIC:
        numeric=pd.to_numeric(df[v],errors="raise").to_numpy(dtype=float)
        if not np.isfinite(numeric).all() or (numeric<0).any():
            raise ValueError("Original source numeric km field changed: "+v)
        df[v]=numeric
    # Only original SOURCE cat levels from prior source-only audit admitted.
    if set(df["clc2_20m"])!={
        "forest","agricultural areas","meadows","water","wetland",
        "shrubs and bushes","city area"}:
        raise ValueError("Original 7-category land cover altered")
    if set(df["forestornot"])!={"forest","others"}:
        raise ValueError("Original binary forest category altered")
    df["_bat"]=df["batid"].astype(str)
    df["_track"]=df["trackid"].astype(str)
    df["_y"]=(df["case_"]=="TRUE").astype(int)
    if df["_bat"].nunique()!=SOURCE_BATS:
        raise ValueError("Original source 60 independent bat tokens changed")
    if df["_track"].nunique()!=SOURCE_TRACKS:
        raise ValueError("Original source 107 separate flight IDs changed")
    if (df.groupby("_track")["_bat"].nunique()!=1).any():
        raise ValueError("Original track ID spans multiple different original bats")
    bybat=df.groupby("_bat")["_y"].agg(["sum","size"])
    if (bybat["sum"]<MIN_TRUE_PER_BAT).any() or (
        (bybat["size"]-bybat["sum"])<MIN_FALSE_PER_BAT).any():
        raise ValueError("Original bat does not provide both source labels")
    source_tracks=df.groupby(["_bat","_track"])["_y"].agg(["sum","size"])
    if (source_tracks["sum"]<1).any() or (
        (source_tracks["size"]-source_tracks["sum"])<1).any():
        raise ValueError("Original flight lacks used or available pseudo-locations")
    if df.groupby("_bat")["sex"].nunique().max()>1 or (
        df.groupby("_bat")["age_class"].nunique().max()>1):
        raise ValueError("Original bat sex or age changes under fixed ID")
    return df,{
        "source_RSF_original_rows":len(df),
        "original_used_GPS_model_rows":int(df["_y"].sum()),
        "original_generated_random_model_rows":int((1-df["_y"]).sum()),
        "source_independent_bats":df["_bat"].nunique(),
        "source_flight_tracks":df["_track"].nunique(),
        "source_field_periods":{
            str(k):int(v) for k,v in df["field_period"].value_counts().items()},
        "original_bats_with_3_or_more_tracks":int(
            (df.groupby("_bat")["_track"].nunique()>=3).sum()),
        "original_repeated_private_history_gate_passed":False,
        "source_UTM_GPS_coordinates_or_height_parsed":False,
        "original_bat_ID_and_flight_ID_values_exported":False
    }


def build_design(training:pd.DataFrame,testing:pd.DataFrame,
                 model:int)->tuple[np.ndarray,np.ndarray]:
    if model not in (0,1,2):
        raise ValueError("Unknown preregistered bat RSF model")
    encoder=OneHotEncoder(handle_unknown="ignore",sparse_output=False)
    tr_cat=encoder.fit_transform(training[list(CATEGORICAL)].astype(str))
    te_cat=encoder.transform(testing[list(CATEGORICAL)].astype(str))
    numeric_names=NUMERIC[:1] if model==0 else NUMERIC
    tr_raw=np.log1p(training[list(numeric_names)].to_numpy(dtype=float))
    te_raw=np.log1p(testing[list(numeric_names)].to_numpy(dtype=float))
    scale=StandardScaler()
    tr=scale.fit_transform(tr_raw)
    te=scale.transform(te_raw)
    xtr=np.column_stack([tr_cat,tr])
    xte=np.column_stack([te_cat,te])
    if model==2:
        xtr=np.column_stack([
           xtr,
           (training["forestornot"].to_numpy()=="forest").astype(float)*tr[:,1],
           tr[:,0]*tr[:,1]])
        xte=np.column_stack([
           xte,
           (testing["forestornot"].to_numpy()=="forest").astype(float)*te[:,1],
           te[:,0]*te[:,1]])
    return xtr,xte


def original_training_weights(train:pd.DataFrame)->np.ndarray:
    # Every bat equal weight; then every original trip within bat equal;
    # then used vs generated points within each trip each half weight.
    bat_trip_count=train.groupby("_bat")["_track"].transform("nunique")
    trip_case_size=train.groupby(["_bat","_track","_y"])["_y"].transform("size")
    return (.5/(bat_trip_count.to_numpy(float)*trip_case_size.to_numpy(float)))


def fit_predict(train:pd.DataFrame,test:pd.DataFrame,model:int)->np.ndarray:
    features,heldout=build_design(train,test,model)
    labels=train["_y"].to_numpy(dtype=int)
    w=original_training_weights(train)
    if set(labels)!={0,1}:
        raise ValueError("Original training sample missing TRUE/FALSE")
    clf=LogisticRegression(C=C_VALUE,penalty="l2",fit_intercept=True,
                           solver="liblinear",max_iter=MAX_ITER,
                           random_state=RANDOM_SEED)
    clf.fit(features,labels,sample_weight=w)
    return clf.decision_function(heldout)


def pairwise_source_accuracy(y:np.ndarray,scores:np.ndarray)->float:
    return float(roc_auc_score(y,scores))


def balanced_source_logloss(y:np.ndarray,scores:np.ndarray)->float:
    # softplus(-s) for TRUE and softplus(s) for FALSE;
    # source sample rate 1:5 is not real animal location prior.
    observed=scores[y==1]
    random=scores[y==0]
    if not len(observed) or not len(random):
        raise ValueError("Original source flight has no true/random comparison")
    return float(.5*np.logaddexp(0.,-observed).mean() +
                 .5*np.logaddexp(0.,random).mean())


def score_heldout_bats(test:pd.DataFrame,predictions:dict)->dict:
    if any(len(p)!=len(test) for p in predictions.values()):
        raise ValueError("Heldout original labels and predictor length mismatch")
    bybat=collections.defaultdict(list)
    for (_,trackid),indices in test.groupby(["_bat","_track"]).indices.items():
        local=test.iloc[indices]
        bat=str(local["_bat"].iloc[0])
        y=local["_y"].to_numpy(int)
        scores={}
        for name,x in predictions.items():
            scores[name]={
                "AUC":pairwise_source_accuracy(y,x[indices]),
                "balanced_log_loss":balanced_source_logloss(y,x[indices])}
        bybat[bat].append({
            "track":trackid,
            "source_period":str(local["field_period"].iloc[0]),
            "metrics":scores
        })
    output={}
    for bat,flights in bybat.items():
        def means(model,metric):
            return float(np.mean([x["metrics"][model][metric] for x in flights]))
        output[bat]={
           "source_n_original_flights":len(flights),
           "original_field_periods":sorted(set(x["source_period"] for x in flights)),
           "source_sex":str(test.loc[test["_bat"]==bat,"sex"].iloc[0]),
           "source_age_class":str(test.loc[test["_bat"]==bat,"age_class"].iloc[0]),
           "AUC_MN":.5,
           "AUC_M0":means("M0","AUC"),
           "AUC_M1":means("M1","AUC"),
           "AUC_M2":means("M2","AUC"),
           "L_MN":float(np.log(2.)),
           "L_M0":means("M0","balanced_log_loss"),
           "L_M1":means("M1","balanced_log_loss"),
           "L_M2":means("M2","balanced_log_loss"),
        }
    return output


def all_bat_holdouts(df:pd.DataFrame)->tuple[dict,dict]:
    folds=df["_bat"].map(bat_fold).to_numpy()
    result={}
    support={}
    for f in range(N_FOLDS):
        train=df.iloc[np.flatnonzero(folds!=f)].copy()
        test=df.iloc[np.flatnonzero(folds==f)].copy()
        if test.empty or train.empty:
            raise ValueError("Fixed original bat fold empty")
        if set(train["_bat"]) & set(test["_bat"]):
            raise ValueError("Original bat ID appeared in both train and test")
        models={f"M{model}":fit_predict(train,test,model)
                for model in (0,1,2)}
        per=score_heldout_bats(test,models)
        if set(result) & set(per):
            raise ValueError("Original bat scored in multiple folds")
        result.update(per)
        support[str(f)]={
           "source_train_bat_ID_count":train["_bat"].nunique(),
           "source_holdout_bat_ID_count":test["_bat"].nunique(),
           "source_heldout_flights":test["_track"].nunique(),
           "source_heldout_model_rows":len(test),
           "source_any_bat_ID_train_test_overlap":False,
           "heldout_bat_ID_used_to_fit_landcover_or_turbine_coefficients":False}
    if len(result)!=SOURCE_BATS:
        raise ValueError("Not all 60 original bat IDs independently evaluated")
    return result,support


def summarize(original_bats:dict)->dict:
    keys=sorted(original_bats)
    if len(keys)!=SOURCE_BATS:
        raise ValueError("Unexpected source independent bat denominator")
    tab=np.asarray([[original_bats[x][f"L_{name}"] for name in
                    ("MN","M0","M1","M2")] for x in keys])
    auc=np.asarray([[original_bats[x][f"AUC_{name}"] for name in
                    ("MN","M0","M1","M2")] for x in keys])
    effects={
      "primary_wind_turbine_increment_M0_minus_M1":tab[:,1]-tab[:,2],
      "secondary_landcover_roost_MN_minus_M0":tab[:,0]-tab[:,1],
      "secondary_wind_forest_roost_interaction_M1_minus_M2":tab[:,2]-tab[:,3],
      "secondary_turbine_AUC_M1_minus_M0":auc[:,2]-auc[:,1],
      "secondary_landcover_AUC_M0_minus_null":auc[:,1]-.5,
    }
    rng=np.random.default_rng(RANDOM_SEED)
    indices=rng.integers(0,len(keys),size=(BOOT_REPS,len(keys)))
    contrasts={}
    for name,gain in effects.items():
        lo,hi=np.quantile(gain[indices].mean(axis=1),[.025,.975])
        contrasts[name]={
            "mean_bat_equal_gain":float(gain.mean()),
            "bat_IDs_with_positive_gain":int((gain>0).sum()),
            "n_independent_bats":len(keys),
            "bat_cluster_bootstrap_95_percentile":[float(lo),float(hi)]}
    anon={}
    for i,bat in enumerate(keys,1):
        anon[f"bat_{i:03d}"]=original_bats[bat]
    return {
      "status":"EXPLORATORY_INDEPENDENT_NOCTULE_BAT_RSF_ENVIRONMENT_TRANSFER",
      "source_total_independent_bat_IDs":len(keys),
      "source_original_flights":sum(x["source_n_original_flights"] for x in original_bats.values()),
      "bat_equal_AUC_MN_M0_M1_M2":list(map(float,auc.mean(axis=0))),
      "bat_equal_balanced_logloss_MN_M0_M1_M2":list(map(float,tab.mean(axis=0))),
      "registered_outcome_contrasts":contrasts,
      "full_anonymized_bat_models":anon,
      "private_history_or_individual_three_flight_memory_assessed":False,
      "original_sampled_random_points_are_not_animals_or_true_choice_destinations":True,
      "limits":[
         "Source original rsf generated random locations; no unique step_id / original matched decision time",
         "Only 1 bat had three flight tracks: original private temporal memory hypothesis not admitted",
         "Whole 60 bats in one German field landscape, shared turbine/forest opportunity and spatial dependence",
         "No causal turbine avoidance, lifetime fitness, prey abundance, simultaneous social group networks or 3D movement calibrated."
       ]
    }


def run()->dict:
    files={x["filename"]:x for x in z.source_list(z.fetch_original())}
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/SOURCE_FILE
        receipt=original.download_verified(files[SOURCE_FILE],path)
        if receipt["independently_computed_sha256"]!=SOURCE_SHA256:
            raise ValueError("Original source SHA256 drift after B/C0 source audits")
        data,qc=source_table(path)
        per,folds=all_bat_holdouts(data)
        result=summarize(per)
    return {
       "study":"v28-C1-original-noctule-bat-2023-RSF-wind-turbine-habitat-forecast",
       "registered_before_bat_case_specific_habitat_values":
           "docs/V28_FROZEN_BAT_TURBINE_HELDOUT_PREDICTION.md",
       "source_original_DOI":"10.5281/zenodo.7535030",
       "original_bat_RSF_file_sha256":receipt["independently_computed_sha256"],
       "source_original_license":"cc-by-4.0",
       "source_original_bat_and_flight_quality":qc,
       "source_five_whole_bat_holdouts":folds,
       "status":result["status"],
       "registered_bat_habitat_result":result,
       "old_3_flight_private_history_gate_failed":True,
       "prior_v13_to_v27_endpoints_unchanged":True,
       "no_raw_bat_UTM_or_exact_original_IDs_or_turbine_locations_exported":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v28/results/bat_turbine_landcover_heldout_v28.json"))
    a=p.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V28_BAT_RSF_SOURCE_QC",json.dumps(d["source_original_bat_and_flight_quality"],sort_keys=True))
    print("V28_BAT_RSF_FOLDS",json.dumps(d["source_five_whole_bat_holdouts"],sort_keys=True))
    print("V28_BAT_RSF_STATUS",d["status"])
    print("V28_BAT_RSF_MAIN",json.dumps(d["registered_bat_habitat_result"]["registered_outcome_contrasts"],sort_keys=True))
    print("V28_BAT_RSF_ABSOLUTE",json.dumps({
         "mean_bat_AUC":d["registered_bat_habitat_result"]["bat_equal_AUC_MN_M0_M1_M2"],
         "mean_bat_balanced_logloss":d["registered_bat_habitat_result"]["bat_equal_balanced_logloss_MN_M0_M1_M2"]},sort_keys=True))
    print("V28_BAT_RSF_ALL_ANON_BATS",json.dumps(d["registered_bat_habitat_result"]["full_anonymized_bat_models"],sort_keys=True))
    print("V28_NO_SOCIAL_FORCE_OR_PRIVATE_MEMORY_FROM_RSF")
if __name__=="__main__":
    main()
