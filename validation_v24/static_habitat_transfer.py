#!/usr/bin/env python3
"""v24-S original USGS brood-heldout STATIC sampled habitat choice forecast.

Separate from v24 future-history primary (NOT_ADMITTED because original
chosen wetlands have no visit date/age). Original used=1 and generated
available=0 from within 2.4 km of radio brood's nest. All 185 original
broods held out in fixed SHA256 groups. AUC and pseudo-choice log loss
are BROOD averaged; not genuine timestamped animal choice-set likelihood.
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
from scipy.special import logsumexp
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import sciencebase_source_gate as usgs
import source_file_schema_gate as original

SOURCE_FILE = "Duckling_Habitat_Selection_Dataset.csv"
SOURCE_SHA256 = "e4ac32416e2f013efcca8e40b9916e73c72e2e1891a09f78d865524ee16ea036"
CATEGORICAL = ("Wetland Type", "Dominant Veg Category")
NUMERIC = ("Percent Veg of Unit", "Salinity Concentration", "Wetland Area")
SOURCE_YEARS = ("2016", "2017", "2018", "2019")
EXPECTED_BROODS = 185
EXPECTED_USED = 2069
EXPECTED_AVAIL = 74000
EXPECTED_AVAILABLE_PER_BROOD = 400
N_FOLDS = 5
C_VALUE = 1.
MAX_ITER = 400
BOOT_REPS = 10000
BOOT_SEED = 20261029
PSEUDOCHOICE_CANDIDATES = EXPECTED_AVAILABLE_PER_BROOD + 1
ORIGINAL_FUTURE_HISTORY_STATUS = (
    "NOT_ADMITTED_NO_DATED_WETLAND_CHOICE_OR_MATCHED_TEMPORAL_AVAILABILITY"
)


def fold_for_brood(brood: str) -> int:
    return int(hashlib.sha256(brood.encode("utf-8")).hexdigest(), 16) % N_FOLDS


def read_original_static_source(path: Path) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(path, dtype={
        "Brood ID": "string", "Wetland ID": "string", "Year": "string",
        "Species": "string", "Wetland Type": "string",
        "Dominant Veg Category": "string",
        "Water Map Time Period": "string",
    }, low_memory=False)
    required = {
        "Species", "Used", "Weight", "Brood ID", "Wetland ID",
        "Wetland Type", "Dominant Veg Category",
        "Percent Veg of Unit", "Salinity Concentration",
        "Wetland Area", "Year", "Water Map Time Period",
    }
    if set(df.columns) != required:
        raise ValueError("Source CSV contains unexpected columns")
    if df["Brood ID"].isna().any() or df["Species"].isna().any() or df["Year"].isna().any():
        raise ValueError("Original brood, species or year ID is missing")
    values = pd.to_numeric(df["Used"], errors="raise")
    if not values.isin([0, 1]).all():
        raise ValueError("Original source Used is not binary")
    df["_label"] = values.to_numpy().astype(np.int8)
    df["_brood"] = df["Brood ID"].astype(str)
    df["_year"] = df["Year"].astype(str)
    df["_species"] = df["Species"].astype(str)
    counts = df.groupby("_brood", sort=True)["_label"].agg(
        total="size", used="sum")
    counts["available"] = counts["total"] - counts["used"]
    if len(counts) != EXPECTED_BROODS:
        raise ValueError("Original number of radio brood clusters changed")
    if int(df["_label"].sum()) != EXPECTED_USED or (
            int((1-df["_label"]).sum()) != EXPECTED_AVAIL):
        raise ValueError("Original number of used/available samples changed")
    if (counts["used"] < 1).any() or (
            counts["available"] != EXPECTED_AVAILABLE_PER_BROOD).any():
        raise ValueError("Source brood available pool does not match source admission")
    if df.groupby("_brood")["_year"].nunique().max() != 1 or (
            df.groupby("_brood")["_species"].nunique().max() != 1):
        raise ValueError("Brood has changing source year or species")
    if set(df["_year"]) != set(SOURCE_YEARS):
        raise ValueError("Original 2016–2019 source years changed")
    # Wetland identity is unavailable in generated sources. No visit time
    # is present. We do not construct any false dated choice event.
    original_avail_ids = df.loc[df["_label"] == 0, "Wetland ID"]
    if not original_avail_ids.isna().all():
        raise ValueError("Original generated available point wetland ID support changed")
    return df, {
        "source_broods": len(counts),
        "source_used_location_rows": int(df["_label"].sum()),
        "source_generated_available_locations": int((1-df["_label"]).sum()),
        "original_available_points_per_brood": EXPECTED_AVAILABLE_PER_BROOD,
        "original_species_count": df["_species"].nunique(),
        "original_year_labels": list(SOURCE_YEARS),
        "source_brood_ids_with_1_or_more_used": int((counts["used"]>0).sum()),
        "source_original_dated_wetland_visits_available": False,
        "source_observed_animal_raw_GPS_coordinates": False,
        "response_or_original_brood_identifiers_exported": False,
    }


def numeric_source_values(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    columns = []
    missings = []
    for col in NUMERIC:
        raw = df[col]
        num = pd.to_numeric(raw, errors="coerce")
        # Source parser may interpret blank/NA as missing; but other
        # nonnumeric tokens are outside preregistered source contract.
        bad = raw.notna() & num.isna()
        if bad.any():
            raise ValueError("Uninterpretable numeric source field "+col)
        n = num.to_numpy(dtype=float)
        valid = n[np.isfinite(n)]
        if len(valid)==0:
            raise ValueError("Original numeric source is wholly absent "+col)
        if col == "Percent Veg of Unit" and (
                valid.min() < 0 or valid.max() > 100):
            raise ValueError("Percent vegetation source outside [0,100]")
        if col in ("Salinity Concentration", "Wetland Area") and valid.min() < 0:
            raise ValueError("Nonnegative source field violated "+col)
        missings.append(~np.isfinite(n))
        if col == "Percent Veg of Unit":
            n = n / 100.
        else:
            n = np.log1p(n)
        columns.append(n)
    return np.column_stack(columns), np.column_stack(missings).astype(float)


def build_features(train: pd.DataFrame, test: pd.DataFrame,
                   species_interactions: bool = False) -> tuple[np.ndarray,np.ndarray]:
    if not all(col in train for col in (*CATEGORICAL,*NUMERIC)):
        raise ValueError("Original preregistered habitat covariates missing")
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    train_cat = enc.fit_transform(
        train[list(CATEGORICAL)].fillna("MISSING").astype(str))
    test_cat = enc.transform(
        test[list(CATEGORICAL)].fillna("MISSING").astype(str))
    train_num, train_na = numeric_source_values(train)
    test_num, test_na = numeric_source_values(test)
    medians = np.nanmedian(train_num, axis=0)
    if not np.isfinite(medians).all():
        raise ValueError("No imputation median in original training brood cohort")
    train_num = np.where(np.isfinite(train_num), train_num, medians)
    test_num = np.where(np.isfinite(test_num), test_num, medians)
    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(train_num)
    test_scaled = scaler.transform(test_num)
    xtrain = np.column_stack([train_cat, train_scaled, train_na])
    xtest = np.column_stack([test_cat, test_scaled, test_na])
    if not species_interactions:
        return xtrain, xtest
    # The main species indicator is constant within each source brood and
    # cannot help rank that brood's used and available points by itself.
    sp = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    sptrain = sp.fit_transform(train[["_species"]])
    sptest = sp.transform(test[["_species"]])
    interactions_train = (xtrain[:,None,:] * sptrain[:,:,None]).reshape(len(train),-1)
    interactions_test = (xtest[:,None,:] * sptest[:,:,None]).reshape(len(test),-1)
    return (np.column_stack([xtrain,interactions_train]),
            np.column_stack([xtest,interactions_test]))


def training_brood_weights(df: pd.DataFrame) -> np.ndarray:
    count = df.groupby(["_brood","_label"])["_label"].transform("size")
    return (.5 / count.to_numpy(dtype=float))


def fit_predict(train: pd.DataFrame, test: pd.DataFrame,
                interactions=False) -> np.ndarray:
    xtrain,xtest = build_features(train,test,interactions)
    labels=train["_label"].to_numpy(dtype=int)
    if len(set(labels))!=2:
        raise ValueError("Source training missing use or available class")
    model=LogisticRegression(C=C_VALUE,solver="liblinear",max_iter=MAX_ITER,
                             random_state=BOOT_SEED,fit_intercept=True)
    model.fit(xtrain,labels,sample_weight=training_brood_weights(train))
    return model.decision_function(xtest)


def per_brood_metrics(test: pd.DataFrame,
                      predictors: dict[str,np.ndarray]) -> dict[str,dict]:
    if any(len(v)!=len(test) for v in predictors.values()):
        raise ValueError("Model score/test source row mismatch")
    out={}
    for brood,idx in test.groupby("_brood").indices.items():
        label = test.iloc[idx]["_label"].to_numpy(dtype=int)
        nused=int(label.sum());navail=len(label)-nused
        if nused<1 or navail!=EXPECTED_AVAILABLE_PER_BROOD:
            raise ValueError("Original brood pseudo-choice support has changed")
        entry={
            "n_used_source_points":nused,"n_generated_available_source_points":navail,
            "source_year":str(test.iloc[idx]["_year"].iloc[0]),
            "source_species":str(test.iloc[idx]["_species"].iloc[0]),
            "M0_auc_uniform":.5,
            "M0_logloss_uniform":float(math.log(navail+1)),
        }
        for name,values in predictors.items():
            sc=values[idx]
            # AUC over every original used×sampled available pair in one
            # brood. Never aggregate by pseudo-independent GPS points.
            entry[name+"_brood_used_available_auc"]=float(
                roc_auc_score(label,sc))
            used=sc[label==1]
            available=sc[label==0]
            # each used point is a pseudo-choice among itself + the same
            # brood's originally sampled 400 available points.
            avail_logsum=logsumexp(available)
            losses=np.logaddexp(used,avail_logsum)-used
            entry[name+"_pseudochoice_logloss"]=float(losses.mean())
        out[brood]=entry
    return out


def fixed_five_fold(df: pd.DataFrame) -> tuple[dict,dict]:
    fold=df["_brood"].map(fold_for_brood).to_numpy()
    assigned={b:fold_for_brood(b) for b in df["_brood"].unique()}
    output={}
    support={}
    for heldout in range(N_FOLDS):
        train=df.loc[fold!=heldout].copy()
        test=df.loc[fold==heldout].copy()
        if train.empty or test.empty:
            raise ValueError("Original fixed fold lacks brood source data")
        if set(train["_brood"]) & set(test["_brood"]):
            raise ValueError("Original brood ID leaked between training/test")
        m1=fit_predict(train,test,interactions=False)
        m2=fit_predict(train,test,interactions=True)
        predicted=per_brood_metrics(test,{"M1":m1,"M2":m2})
        if set(output).intersection(predicted):
            raise ValueError("A brood was already evaluated in a different fold")
        output.update(predicted)
        support[str(heldout)]={
            "original_train_broods":train["_brood"].nunique(),
            "original_test_broods":test["_brood"].nunique(),
            "original_test_source_rows":len(test),
            "trained_on_test_brood_rows":False,
        }
    if set(output)!=set(assigned) or len(output)!=EXPECTED_BROODS:
        raise ValueError("Not all original source broods received a heldout score")
    for brood,val in output.items():
        val["holdout_fold_from_source_ID_only"]=assigned[brood]
    return output,support


def leave_one_year_out(df: pd.DataFrame) -> dict:
    scores={}
    for year in SOURCE_YEARS:
        train=df[df["_year"]!=year].copy()
        test=df[df["_year"]==year].copy()
        if test.empty or train.empty:
            raise ValueError("Missing original year to hold out")
        m1=fit_predict(train,test,False)
        m2=fit_predict(train,test,True)
        per=per_brood_metrics(test,{"M1":m1,"M2":m2})
        scores[year]={
            "source_independent_test_broods":len(per),
            "auc_M0_uniform":0.5,
            "mean_M1_auc":float(np.mean([
                val["M1_brood_used_available_auc"] for val in per.values()])),
            "mean_M2_auc":float(np.mean([
                val["M2_brood_used_available_auc"] for val in per.values()])),
            "mean_M1_pseudochoice_logloss":float(np.mean([
                val["M1_pseudochoice_logloss"] for val in per.values()])),
            "mean_M2_pseudochoice_logloss":float(np.mean([
                val["M2_pseudochoice_logloss"] for val in per.values()])),
            "source_heldout_year_only_previously_outcome_unseen":True,
        }
    return scores


def aggregate_per_brood(per:dict)->dict:
    broods=sorted(per)
    if len(broods)!=EXPECTED_BROODS:
        raise ValueError("Original brood total changed at aggregation")
    a=np.asarray([[
        per[b]["M1_brood_used_available_auc"],
        per[b]["M2_brood_used_available_auc"],
        per[b]["M1_pseudochoice_logloss"],
        per[b]["M2_pseudochoice_logloss"]] for b in broods])
    rng=np.random.default_rng(BOOT_SEED)
    inds=rng.integers(0,len(broods),size=(BOOT_REPS,len(broods)))
    effects={
        "primary_M1_auc_minus_uniform_half":a[:,0]-.5,
        "secondary_M1_pseudochoice_logloss_saved_vs_uniform":
            np.log(PSEUDOCHOICE_CANDIDATES)-a[:,2],
        "secondary_M2_species_interaction_AUC_minus_M1":a[:,1]-a[:,0],
        "secondary_M2_species_interaction_logloss_saved_vs_M1":a[:,2]-a[:,3],
    }
    contrasts={}
    for name,gains in effects.items():
        lo,hi=np.quantile(gains[inds].mean(axis=1),[.025,.975])
        contrasts[name]={
            "original_independent_broods":len(gains),
            "equal_brood_mean_gain":float(np.mean(gains)),
            "broods_with_positive_gain":int(np.sum(gains>0)),
            "source_brood_bootstrap_95_percentile":[float(lo),float(hi)],
        }
    avg={
       "M0_uniform_auc":0.5,
       "M1_environment_auc":float(a[:,0].mean()),
       "M2_environment_plus_species_auc":float(a[:,1].mean()),
       "M0_uniform_pseudochoice_logloss":float(np.log(PSEUDOCHOICE_CANDIDATES)),
       "M1_environment_pseudochoice_logloss":float(a[:,2].mean()),
       "M2_environment_plus_species_pseudochoice_logloss":float(a[:,3].mean())
    }
    anonymized={}
    for i,b in enumerate(broods,1):
        anonymized[f"source_brood_{i:03d}"]=per[b]
    return {
        "status":"EXPLORATORY_ORIGINAL_USGS_STATIC_HABITAT_PSEUDOCHOICE_BROOD_TRANSFER",
        "original_independent_brood_count":len(broods),
        "sampled_available_candidates_per_brood":EXPECTED_AVAILABLE_PER_BROOD,
        "original_pseudoused_points":int(sum(x["n_used_source_points"] for x in per.values())),
        "environmental_model_attributes":list((*CATEGORICAL,*NUMERIC)),
        "absolute_brood_equal_metrics":avg,
        "original_registered_contrasts":contrasts,
        "per_brood_anonymized":anonymized,
        "note":"Static matched sampled 401-candidate pseudo-choice, NOT dated wetland visits or a true 401-wetland alternative set",
    }


def run() -> dict:
    item=usgs.extract_item_metadata(usgs.bounded_json(
        usgs.SCIENCEBASE_ITEM_URLS[0]))
    files=original.select_original_files(item)
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/SOURCE_FILE
        pin=original.download_exact(files[SOURCE_FILE],path)
        if pin["independent_sha256"]!=SOURCE_SHA256:
            raise ValueError("Previously frozen original source SHA256 drift")
        df,sourceqc=read_original_static_source(path)
        # At this point numeric habitat inputs may be read and model fitted.
        # This happens strictly after separate protocol file was committed.
        group_results,folds=fixed_five_fold(df)
        temporal_year=leave_one_year_out(df)
        result=aggregate_per_brood(group_results)
    return {
        "study":"v24-S-independent-original-2026-Suisun-radio-brood-static-wetland-preference",
        "source_original_USGS_DOI":usgs.SOURCE_DOI,
        "source_original_sciencebase_id":usgs.SOURCE_ITEM,
        "source_original_SHA256":pin["independent_sha256"],
        "registered_before_habitat_numeric_outcomes":
            "docs/V24_FROZEN_BROOD_HELDOUT_STATIC_HABITAT_CHOICE.md",
        "original_v24_future_visit_history_status":ORIGINAL_FUTURE_HISTORY_STATUS,
        "source_original_brood_data_structure":sourceqc,
        "frozen_five_fold_id_only_support":folds,
        "registered_leave_one_year_out_results":temporal_year,
        "status":result["status"],
        "observed_source_habitat_result":result,
        "source_generated_available_locations_not_true_visited_controls":True,
        "source_time_series_individual_choice_not_identified":True,
        "source_original_nest_coordinates_or_habitat_rows_redistributed":False,
        "prior_v13_to_v23_frozen_outcomes_unchanged":True,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,
        default=Path("validation_v24/results/static_brood_habitat_preference_v24.json"))
    args=parser.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V24_STATIC_SOURCE_QC",json.dumps(result["source_original_brood_data_structure"],sort_keys=True))
    print("V24_STATIC_FIVE_FOLD",json.dumps(result["frozen_five_fold_id_only_support"],sort_keys=True))
    print("V24_STATIC_BROOD_PRIMARY",json.dumps(result["observed_source_habitat_result"]["original_registered_contrasts"],sort_keys=True))
    print("V24_STATIC_BROOD_MSE_AUC",json.dumps(result["observed_source_habitat_result"]["absolute_brood_equal_metrics"],sort_keys=True))
    print("V24_STATIC_HELDOUT_YEAR",json.dumps(result["registered_leave_one_year_out_results"],sort_keys=True))
    print("V24_STATIC_ANON_BROODS",json.dumps(result["observed_source_habitat_result"]["per_brood_anonymized"],sort_keys=True))
    print("V24_NO_FUTURE_HISTORY_INFERENCE")

if __name__=="__main__":
    main()
