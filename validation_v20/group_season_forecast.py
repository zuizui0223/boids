#!/usr/bin/env python3
"""v20-B: frozen actual wild guineafowl source-derived next-season group prediction.

Source: Papageorgiou & Farine 2020 eLife 59902, original pinned 2717-byte Rdata.
No raw Movebank GPS access, no individual-bird IDs, no prey or climate
measurements, no social forces. Original season labels C,D,E,F,G.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import source_gate as source

ORIGINAL_SHA256="c6a534993e99f2cb324e9691ff7ec58095bf7cd7e82d7a38721f3575097cbb55"
REGISTERED_OBJECT="sDCEFGnu"
SEASON_ORDER=("C","D","E","F","G")
RESPONSE_NAMES=("fidelity","AREA_SQM","speed_km_day")
ORIGINAL_GROUP_SEASON_ROWS=45
ORIGINAL_GROUPS=21
MIN_EVALUATION_GROUPS=8
MIN_EVALUATION_CELLS=12
MIN_EXTERNAL_HISTORY_GROUPS=3
SHRINK_KAPPA=2.
BOOT_RESAMPLES=10_000
BOOT_SEED=20261028


def canonical_id(item)->str:
    if item is None or pd.isna(item):
        raise ValueError("Empty original group ID")
    return str(item).strip()


def registered_source(data:pd.DataFrame)->pd.DataFrame:
    if len(data)!=ORIGINAL_GROUP_SEASON_ROWS:
        raise ValueError("Original seasonal source row count drifted")
    if not {"ID","SEASON",*RESPONSE_NAMES}.issubset(data.columns):
        raise ValueError("Original source response identity schema changed")
    if data[["ID","SEASON"]].isna().any().any():
        raise ValueError("Original group-season keys have missingness")
    df=data.copy()
    df["_id"]=[canonical_id(v) for v in df["ID"]]
    df["_season"]=[str(v) for v in df["SEASON"]]
    if set(df["_season"])!=set(SEASON_ORDER):
        raise ValueError("Original seasonal category codes changed")
    df["_order"]=[SEASON_ORDER.index(t) for t in df["_season"]]
    if df[["_id","_season"]].duplicated().any():
        raise ValueError("Duplicated group-season grain")
    if df["_id"].nunique()!=ORIGINAL_GROUPS:
        raise ValueError("Original independent group IDs changed")
    return df


def eligible_targets(data:pd.DataFrame)->list[tuple[str,str]]:
    """Pure ID / season support, never inspect ecological response values."""
    groups={g:list(q["_order"].to_numpy())
            for g,q in data.groupby("_id",sort=True)}
    eligible=[]
    for group,q in data.groupby("_id",sort=True):
        for season_idx in sorted(q["_order"]):
            own=sum(t<season_idx for t in groups[group])
            others=sum(any(t<season_idx for t in years)
                       for g,years in groups.items() if g!=group)
            if own>=1 and others>=MIN_EXTERNAL_HISTORY_GROUPS:
                eligible.append((group,SEASON_ORDER[season_idx]))
    return eligible


def transformed_source(data:pd.DataFrame,response:str)->pd.DataFrame:
    if response not in RESPONSE_NAMES:
        raise ValueError("Unregistered future-space-use indicator")
    df=data.copy()
    raw=pd.to_numeric(df[response],errors="raise").astype(float)
    if not np.isfinite(raw.to_numpy()).all():
        raise ValueError("Original source has nonfinite ecological response")
    if response=="fidelity":
        if ((raw<0)|(raw>1)).any():
            raise ValueError("Source fidelity not a bounded 0..1 space-use indicator")
        df["_y"]=raw
    else:
        if (raw<=0).any():
            raise ValueError("Registered positive-only ecological log input violated")
        df["_y"]=np.log(raw)
    return df


def predictions(data:pd.DataFrame,rows:list[tuple[str,str]])->list[dict]:
    """All model inputs come from strictly earlier original source seasons."""
    target_map={(row["_id"],row["_season"]):row
                for _,row in data.iterrows()}
    forecasts=[]
    for group,season in rows:
        k=SEASON_ORDER.index(season)
        past=data[data["_order"]<k]
        own=past[past["_id"]==group]
        ext=past[past["_id"]!=group]
        external=ext.groupby("_id",sort=True)["_y"].mean()
        if len(own)<1 or len(external)<MIN_EXTERNAL_HISTORY_GROUPS:
            raise ValueError("Outcome-independent target gate changed")
        m0=float(external.mean()) # Equal past-observed source groups, NOT rows.
        m1=float(own["_y"].mean())
        weight=len(own)/(len(own)+SHRINK_KAPPA)
        m2=(1-weight)*m0+weight*m1
        y=float(target_map[group,season]["_y"])
        forecasts.append({
            "group":group,"season":season,
            "n_group_previous_seasons":len(own),
            "n_other_prior_groups":len(external),
            "error_M0":(y-m0)**2,
            "error_M1":(y-m1)**2,
            "error_M2":(y-m2)**2,
        })
    return forecasts


def summarize(records:list[dict],response:str)->dict:
    bygroup=collections.defaultdict(list)
    for row in records:bygroup[row["group"]].append(row)
    groups=sorted(bygroup)
    if len(groups)<MIN_EVALUATION_GROUPS or len(records)<MIN_EVALUATION_CELLS:
        return {"status":"NOT_ADMITTED_INSUFFICIENT_FUTURE_GROUP_SEASONS",
                "groups":len(groups),"future_group_season_cells":len(records)}
    per_group={}
    for ix,group in enumerate(groups,1):
        r=bygroup[group]
        errs=np.array([[t[f"error_M{i}"] for i in range(3)] for t in r])
        means=errs.mean(axis=0)
        per_group[f"cluster_{ix:02d}"]={
            "future_seasons_scored":len(r),
            "n_historic_seasons_at_targets":sorted(set(t["n_group_previous_seasons"] for t in r)),
            "mse_M0_external_M1_own_M2_shrunk":list(map(float,means)),
            "gain_M0_minus_M2":float(means[0]-means[2]),
            "gain_M0_minus_M1":float(means[0]-means[1]),
            "gain_M1_minus_M2":float(means[1]-means[2]),
        }
    means=np.array([r["mse_M0_external_M1_own_M2_shrunk"]
                    for r in per_group.values()])
    effect_02=means[:,0]-means[:,2]
    effect_01=means[:,0]-means[:,1]
    effect_12=means[:,1]-means[:,2]
    rng=np.random.default_rng(BOOT_SEED)
    draws=rng.integers(0,len(groups),size=(BOOT_RESAMPLES,len(groups)))
    def statistical_summary(gain):
        vals=gain[draws].mean(axis=1)
        return {"group_equal_mean_gain":float(gain.mean()),
                "positive_group_count":int((gain>0).sum()),
                "n_original_groups":len(groups),
                "group_bootstrap_95_percentile_interval":list(map(float,
                        np.quantile(vals,[.025,.975])))}
    absolute=means.mean(axis=0)
    return {
        "status":"EXPLORATORY_SOURCE_DERIVED_WILD_GROUP_NEXT_SEASON_FORECAST",
        "source_measure":response,
        "n_independent_group_clusters":len(groups),
        "n_heldout_future_group_season_targets":len(records),
        "mean_MSE_M0_external_M1_own_M2_shrunk":list(map(float,absolute)),
        "primary_increment_shrink_vs_external_M0_minus_M2":
            statistical_summary(effect_02),
        "secondary_raw_history_M0_minus_M1":
            statistical_summary(effect_01),
        "secondary_shrink_vs_unpooled_M1_minus_M2":
            statistical_summary(effect_12),
        "per_group_anonymized":per_group,
        "limitations":[
            "Original source is a derived seasonal group-level table, not raw GPS",
            "Previous social group observations are NOT individual bird memory",
            "M0 uses strictly earlier other groups, not measured environmental/climate covariates",
            "No contemporary other-group observations, future seasons or target responses enter models",
            "No original GPS, 3D altitude, prey resources, socially directed following or Boids coefficients"]
    }


def run()->dict:
    import pyreadr
    with tempfile.TemporaryDirectory() as temp:
        filename=Path(temp)/"official_source.Rdata"
        integrity=source.download_pinned(filename)
        if integrity["sha256"]!=ORIGINAL_SHA256:
            raise ValueError("Original source pinned SHA256 changed after source-only admission")
        objs=pyreadr.read_r(str(filename))
        if REGISTERED_OBJECT not in objs:
            raise ValueError("No preregistered author-derived group-season table")
        frame=registered_source(objs[REGISTERED_OBJECT])
        support=eligible_targets(frame) # before target response opened
        group_count=len(set(g for g,_ in support))
        admission={"eligible_future_group_season_targets":len(support),
                   "eligible_distinct_original_groups":group_count,
                   "original_total_group_season_rows":len(frame),
                   "original_total_groups":frame["_id"].nunique(),
                   "source_support_gate_passed":group_count>=MIN_EVALUATION_GROUPS and
                                              len(support)>=MIN_EVALUATION_CELLS}
        if not admission["source_support_gate_passed"]:
            results={"status":"NOT_ADMITTED_SOURCE_HISTORY_SUPPORT",
                     "any_outcome_score_computed":False}
        else:
            results={}
            for response in RESPONSE_NAMES:
                try:
                    d=transformed_source(frame,response)
                    records=predictions(d,support)
                    results[response]=summarize(records,response)
                except Exception as e:
                    results[response]={"status":"NOT_ADMITTED_SOURCE_DOMAIN",
                        "error":type(e).__name__+": "+str(e)[:120],
                        "any_outcome_score_computed":False}
    return {
        "study":"v20B-wild-guineafowl-source-derived-future-group-season-fidelity",
        "status":"SOURCE_AWARE_FORECAST_FINISHED__NO_INDIVIDUAL_MEMORY_CLAIM",
        "original_source_integrity":integrity,
        "registered_contract":"docs/V20_FROZEN_GROUP_SEASON_FIDELITY_FORECAST.md",
        "source_only_group_season_admission":admission,
        "model_policy":{"prior_seasons_only":list(SEASON_ORDER),
                        "min_other_groups_in_prior_seasons":MIN_EXTERNAL_HISTORY_GROUPS,
                        "fixed_shrink_kappa":SHRINK_KAPPA,
                        "same_future_group_season_cells_across_models":True,
                        "clustered_bootstrap_resamples":BOOT_RESAMPLES,
                        "clustered_bootstrap_seed":BOOT_SEED,
                        "registered_main_response":"fidelity",
                        "registered_secondary_responses":["AREA_SQM","speed_km_day"]},
        "registered_outcomes":results,
        "all_prior_v13_v15_v16_v17_v18_v19_endpoints_unchanged":True,
        "raw_animal_GPS_locations_or_original_response_rows_exported":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,
        default=Path("validation_v20/results/forward_group_fidelity_v20.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V20_FORECAST_SOURCE",json.dumps(result["original_source_integrity"],sort_keys=True))
    print("V20_FORECAST_ADMISSION",json.dumps(result["source_only_group_season_admission"],sort_keys=True))
    print("V20_WILD_GROUP_RESULTS",json.dumps(result["registered_outcomes"],sort_keys=True))
    print("V20_DERIVED_GROUP_LEVEL_NOT_RAW_GPS_OR_COGNITIVE_MEMORY")
if __name__=="__main__":
    main()
