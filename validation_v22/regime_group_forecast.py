#!/usr/bin/env python3
"""v22-B frozen seasonal REGIME vs group HISTORY for wild guineafowl fidelity.

SAME wild Movebank cohort as previously opened v20, NOT new independent
biological replication. Authors' published derived group-season fidelity,
NOT raw GPS, climate magnitudes, individual private memory or causal Boids.
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

SOURCE_FILE="df_dhor.Rdata"
SOURCE_OBJECT="df"
SOURCE_SHA256="d08864e91a543403cb1e8abf1bf9ea84247543181b8d4f4464ceb03929c0fa83"
SEASONS=tuple([f"year_one_{i}" for i in range(1,7)]
              +[f"year_two_{i}" for i in range(1,6)])
CONTEXTS=("dry","intermediate","wet","wet_breeding")
SOURCE_ROWS=143
SOURCE_GROUPS=26
SOURCE_MISSING_FIDELITY=4
MIN_HIST_OTHER_GROUPS=3
MIN_HIST_OTHER_SAME_CONTEXT_GROUPS=3
MIN_GROUPS=8
MIN_FUTURE_CELLS=30
SHRINK_KAPPA=2.
BOOT_REPS=10000
BOOT_SEED=20261028


def canonical_group(x)->str:
    if pd.isna(x):raise ValueError("Original group identifier missing")
    if isinstance(x,(int,float,np.number)):
        if not math.isfinite(float(x)):
            raise ValueError("Original group non-finite")
        return str(int(x)) if float(x).is_integer() else str(x)
    return str(x).strip()


def source_frame(df:pd.DataFrame)->pd.DataFrame:
    if len(df)!=SOURCE_ROWS:raise ValueError("Original source row count changed")
    required={"groupss_","season","season_type","fidelity","days_tracked"}
    if not required.issubset(set(df.columns)):
        raise ValueError("Original source schema changed")
    if df[["groupss_","season","season_type"]].isna().any().any():
        raise ValueError("Original source group/season/regime keys missing")
    d=df.copy()
    d["_group"]=[canonical_group(v) for v in d["groupss_"]]
    d["_season"]=d["season"].astype(str)
    d["_regime"]=d["season_type"].astype(str)
    if set(d["_season"])!=set(SEASONS):
        raise ValueError("Source season chronology changed")
    if set(d["_regime"])!=set(CONTEXTS):
        raise ValueError("Original source environmental labels changed")
    if d["_group"].nunique()!=SOURCE_GROUPS:
        raise ValueError("Independent source group count changed")
    if d[["_group","_season"]].duplicated().any():
        raise ValueError("Group-season repeated records are not independent units")
    if sum(d["fidelity"].isna())!=SOURCE_MISSING_FIDELITY:
        raise ValueError("Pre-scored source-response missingness changed")
    if (d.groupby("_season")["_regime"].nunique()!=1).any():
        raise ValueError("Original shared environmental season assignment inconsistent")
    d["_ord"]=[SEASONS.index(s) for s in d["_season"]]
    return d


def eligibility(d:pd.DataFrame)->list[tuple[str,str]]:
    """Eligibility uses only original IDs, season codes & source nonmissingness."""
    observed=d[~d["fidelity"].isna()]
    result=[]
    for _,row in observed.iterrows():
        earlier=observed[observed["_ord"]<row["_ord"]]
        group=row["_group"]
        own=int((earlier["_group"]==group).sum())
        others=int(earlier.loc[earlier["_group"]!=group,"_group"].nunique())
        if own>=1 and others>=MIN_HIST_OTHER_GROUPS:
            result.append((group,row["_season"]))
    return result


def predict(d:pd.DataFrame,targets:list[tuple[str,str]])->list[dict]:
    original=d.copy()
    response=pd.to_numeric(original["fidelity"],errors="raise").astype(float)
    finite=response[~response.isna()]
    if not np.isfinite(finite).all() or ((finite<0)|(finite>1)).any():
        raise ValueError("Original site fidelity response not in 0..1")
    original["_response"]=response
    original_index={(row["_group"],row["_season"]):row
                    for _,row in original.iterrows()}
    records=[]
    for group,season in targets:
        target=original_index[(group,season)]
        before=original[(original["_ord"]<target["_ord"]) &
                        (~original["_response"].isna())]
        mine=before[before["_group"]==group]
        others=before[before["_group"]!=group]
        external=others.groupby("_group")["_response"].mean()
        if len(mine)==0 or len(external)<MIN_HIST_OTHER_GROUPS:
            raise ValueError("Source ID-only frozen future eligibility drifted")
        m0=float(external.mean())
        compatible=others[others["_regime"]==target["_regime"]]
        matching=compatible.groupby("_group")["_response"].mean()
        fallback=len(matching)<MIN_HIST_OTHER_SAME_CONTEXT_GROUPS
        me=float(matching.mean()) if not fallback else m0
        mg=float(mine["_response"].mean())
        w=len(mine)/(len(mine)+SHRINK_KAPPA)
        meg=(1-w)*me+w*mg
        y=float(target["_response"])
        records.append({
            "group":group,"season":season,"regime":target["_regime"],
            "n_own_previous_seasons":len(mine),
            "n_other_prior_groups":len(external),
            "n_other_prior_matching_regime_groups":len(matching),
            "environment_same_regime_fallback_to_M0":fallback,
            "mse_M0":(y-m0)**2,
            "mse_ME":(y-me)**2,
            "mse_MG":(y-mg)**2,
            "mse_MEG":(y-meg)**2,
        })
    return records


def group_mean_gain(rows:list[dict],key_a:str,key_b:str)->tuple[float,int,int]:
    by=collections.defaultdict(list)
    for r in rows:
        by[r["group"]].append(r[key_a]-r[key_b])
    vals=[float(np.mean(x)) for x in by.values()]
    return float(np.mean(vals)) if vals else float("nan"),len(by),len(rows)


def summarize(rows:list[dict])->dict:
    grouped=collections.defaultdict(list)
    for r in rows:grouped[r["group"]].append(r)
    if len(grouped)<MIN_GROUPS or len(rows)<MIN_FUTURE_CELLS:
        return {
            "status":"NOT_ADMITTED_FROZEN_TARGET_SUPPORT",
            "groups":len(grouped),"targets":len(rows),"any_effect_score_exported":False}
    per={}
    for i,group in enumerate(sorted(grouped),1):
        original=grouped[group]
        a=np.array([[r["mse_M0"],r["mse_ME"],r["mse_MG"],r["mse_MEG"]]
                    for r in original])
        mean=a.mean(axis=0)
        per[f"original_group_{i:02d}"]={
            "future_season_targets":len(original),
            "environments_measured_in_targets":sorted({r["regime"] for r in original}),
            "same_regime_fallbacks":sum(r["environment_same_regime_fallback_to_M0"]
                                        for r in original),
            "mean_MSE_M0_ME_MG_MEG":list(map(float,mean)),
            "G_history_increment_ME_minus_MEG":float(mean[1]-mean[3]),
            "G_environment_increment_M0_minus_ME":float(mean[0]-mean[1]),
        }
    a=np.array([v["mean_MSE_M0_ME_MG_MEG"] for v in per.values()])
    rng=np.random.default_rng(BOOT_SEED)
    draw=rng.integers(0,len(a),size=(BOOT_REPS,len(a)))
    contrasts={
        "primary_history_beyond_environment_ME_minus_MEG":a[:,1]-a[:,3],
        "secondary_environment_vs_pooled_M0_minus_ME":a[:,0]-a[:,1],
        "secondary_raw_group_vs_environment_ME_minus_MG":a[:,1]-a[:,2],
        "secondary_shrink_vs_raw_group_MG_minus_MEG":a[:,2]-a[:,3],
    }
    summaries={}
    for key,values in contrasts.items():
        n=np.quantile(values[draw].mean(axis=1),[.025,.975])
        summaries[key]={
            "equal_group_mean_gain":float(values.mean()),
            "n_independent_original_group_IDs":len(values),
            "positive_groups":int((values>0).sum()),
            "group_bootstrap_95_percentile":list(map(float,n)),
        }
    seasonal={}
    for season in SEASONS:
        subset=[r for r in rows if r["season"]==season]
        if not subset:continue
        mean,g,t=group_mean_gain(subset,"mse_ME","mse_MEG")
        environmental_gain,_,_=group_mean_gain(subset,"mse_M0","mse_ME")
        seasonal[season]={
            "future_group_season_targets":t,
            "regime":subset[0]["regime"],
            "equal_group_history_beyond_regime_gain":mean,
            "equal_group_environment_vs_pooled_gain":environmental_gain,
            "regime_fallback_cells":sum(r["environment_same_regime_fallback_to_M0"] for r in subset)
        }
    omit={}
    for season in seasonal:
        other=[r for r in rows if r["season"]!=season]
        gain,g,t=group_mean_gain(other,"mse_ME","mse_MEG")
        omit[season]={"group_mean_history_gain_without_this_season":gain,
                      "remaining_groups":g,"remaining_future_targets":t}
    return {
       "status":"EXPLORATORY_SAME_MOVEbank_POPULATION_REGIME_CONDITIONAL_FUTURE_FIDELITY",
       "source_group_ids":len(grouped),"source_future_group_season_targets":len(rows),
       "environment_regime_fallback_targets":sum(r["environment_same_regime_fallback_to_M0"] for r in rows),
       "equal_group_model_MSE_M0_ME_MG_MEG":list(map(float,a.mean(axis=0))),
       "registered_contrasts":summaries,
       "per_original_group_ANONYMIZED":per,
       "per_target_season_all":seasonal,
       "leave_one_original_season_out_a_priori_descriptive":omit,
       "same_Movebank_population_as_v20":True,
       "interpretation_limits":[
          "Only author-derived within-season group-fidelity values, not original GPS data",
          "wet/dry regimes are retrospective state labels, not weather forecasts or independently measured NDVI",
          "All groups share identical target-season regime, so whole-group bootstrap underestimates shared season-level uncertainty",
          "Same Kenyan population as prior v20; no independent biological replication",
          "No individual private-memory, prey opportunities, social contact mechanism or 3D niche estimated"
       ]
    }


def run()->dict:
    import pyreadr
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/SOURCE_FILE
        src=source.download_pinned(SOURCE_FILE,path)
        if src["sha256"]!=SOURCE_SHA256:
            raise ValueError("Source original SHA256 changed since source-only audit")
        objects=pyreadr.read_r(str(path))
        if SOURCE_OBJECT not in objects:
            raise ValueError("Original source table object name changed")
        d=source_frame(objects[SOURCE_OBJECT])
        support=eligibility(d)
        gate={
            "source_original_rows":len(d),
            "source_original_unique_groups":d["_group"].nunique(),
            "source_missing_fidelity_values":int(d["fidelity"].isna().sum()),
            "eligible_original_group_ids":len(set(x for x,_ in support)),
            "eligible_future_group_season_targets":len(support),
            "gate_minimum_groups":MIN_GROUPS,"gate_minimum_targets":MIN_FUTURE_CELLS,
            "admitted":len(set(x for x,_ in support))>=MIN_GROUPS and
                       len(support)>=MIN_FUTURE_CELLS}
        if gate["admitted"]:
            outcome=summarize(predict(d,support))
        else:
            outcome={"status":"NOT_ADMITTED_PREOUTCOME_BIRD_SEASON_SUPPORT",
                     "any_effect_score_exported":False}
    return {
      "study":"v22-wild-guineafowl-original-2021-regime-group-history-context",
      "registered_before_outcomes":"docs/V22_FROZEN_WET_DRY_CONTEXT_GROUP_PREDICTION.md",
      "source_original_author_pin":src,
      "status":outcome["status"],
      "source_only_target_gate":gate,
      "regime_is_known_condition_scenario_not_a_prerun_weather_forecast":True,
      "same_biological_Movebank_pop_as_v20":True,
      "raw_GPS_or_original_ecology_rows_exported":False,
      "prior_v13_through_v21_frozen_endpoints_unchanged":True,
      "observed_result":outcome}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v22/results/regime_group_history_forecast_v22.json"))
    a=p.parse_args()
    r=run();a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V22_PREOUTCOME_GATE",json.dumps(r["source_only_target_gate"],sort_keys=True))
    print("V22_STATUS",r["status"])
    print("V22_RESULT",json.dumps(r["observed_result"],sort_keys=True))
    print("V22_RAW_MOVEbank_GPS_NOT_ACCESSED")
if __name__=="__main__":
    main()
