"""v32 exact streaming sufficient-statistic Ridge under 12 original shoal holdouts.

Works on ORIGINAL source files separately, no animal trajectory persistence.
Numerically equivalent to sklearn StandardScaler + Ridge(alpha=10,
fit_intercept=True) for the same source rows, validated on synthetic truth.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from validation_fish_school_v30.harmonized_forecast import (
    MODEL_NAMES, HORIZONS, AGES_SECONDS, RIDGE_ALPHA, FEAT_DIM
)
from validation_fish_school_v30.harmonized_forecast import SourceStop

SEED=20261124
NBOOT=5000


def file_moment(x,y):
    x=np.asarray(x,dtype=np.float64)
    y=np.asarray(y,dtype=np.float64)
    if x.ndim!=2 or y.ndim!=2 or y.shape!=(len(x),4) or len(x)<1000:
        raise SourceStop("V32_ORIGINAL_FILE_MOMENT_DIMENSION_STOP")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise SourceStop("V32_ORIGINAL_FILE_NONFINITE_MOMENT_STOP")
    return {
        "n":int(len(x)),
        "sx":np.sum(x,axis=0,dtype=np.float64),
        "sxx":x.T@x,
        "sxy":x.T@y,
        "sy":np.sum(y,axis=0,dtype=np.float64),
        "syy":np.sum(y*y,axis=0,dtype=np.float64)
    }


def sum_moments(moments):
    if not moments:raise SourceStop("V32_EMPTY_TRAIN_OR_TEST_SHOAL_MOMENTS")
    out={key:np.array(moments[0][key],copy=True) if key!="n" else int(moments[0]["n"])
         for key in ("n","sx","sxx","sxy","sy","syy")}
    for m in moments[1:]:
        if m["sx"].shape!=out["sx"].shape or m["sxy"].shape!=out["sxy"].shape:
            raise SourceStop("V32_TRAIN_FILES_DIFFERENT_COMMON_FEATURE_DIMENSION")
        for key in out:
            out[key]+=m[key]
    if out["n"]<1000:raise SourceStop("V32_TRAIN_SHOAL_SUPPORT_TOO_SMALL")
    return out


def train_only_standardized_ridge(train,alpha=RIDGE_ALPHA):
    """Exact train-only population StandardScaler plus intercept Ridge(alpha)."""
    if alpha!=10.:raise SourceStop("V32_RIDGE_ALPHA_TUNING_NOT_ALLOWED")
    n=train["n"]
    sx=train["sx"]
    sy=train["sy"]
    xx=train["sxx"]
    xy=train["sxy"]
    mu=sx/n
    ym=sy/n
    var=np.diag(xx)/n-mu**2
    if np.any(var< -1e-8*np.maximum(1.,np.abs(np.diag(xx)/n))):
        raise SourceStop("V32_SOURCE_MOMENT_NUMERIC_VARIANCE_INVALID")
    scale=np.sqrt(np.maximum(var,0))
    scale=np.where(scale<=1e-14,1.,scale)
    cxx=xx-n*np.outer(mu,mu)
    cxy=xy-n*np.outer(mu,ym)
    gram=(cxx/scale[:,None])/scale[None,:]
    gram=(gram+gram.T)*.5
    rhs=cxy/scale[:,None]
    beta=np.linalg.solve(gram+alpha*np.eye(len(mu)),rhs)
    B=beta/scale[:,None]
    bias=ym-mu@B
    if not np.isfinite(B).all() or not np.isfinite(bias).all():
        raise SourceStop("V32_TRAIN_ONLY_RIDGE_NONFINITE_COEFF_STOP")
    return B,bias


def score_file_moment(test,coeff,bias):
    """Four response-coordinate SSE on heldout file without storing original Y."""
    n=test["n"]
    sx,sy=test["sx"],test["sy"]
    meanx,meany=sx/n,sy/n
    centered_xx=test["sxx"]-np.outer(sx,sx)/n
    centered_xy=test["sxy"]-np.outer(sx,sy)/n
    centered_yy=test["syy"]-(sy*sy)/n
    # Exact SSE decomposition with train coefficients and heldout mean error.
    centered_model=np.sum(coeff*(centered_xx@coeff),axis=0)
    crossed=np.sum(coeff*centered_xy,axis=0)
    offset_diff=meany-(meanx@coeff+bias)
    sse=centered_yy+centered_model-2*crossed+n*offset_diff**2
    if not np.isfinite(sse).all() or np.any(sse< -1e-5*np.maximum(test["syy"],1)):
        raise SourceStop("V32_SOURCE_MOMENT_SSE_PRECISION_STOP")
    sse=np.maximum(sse,0)
    return {
        "short":float(np.sum(sse[:2])/(2*n)),
        "delayed":float(np.sum(sse[2:])/(2*n))
    }


def source_moments(source):
    if set(source["X"])!=set(MODEL_NAMES) or source["Y"].shape[1]!=4:
        raise SourceStop("V32_ORIGINAL_COMMON_V30_MODEL_KEYS_STOP")
    return {k:file_moment(source["X"][k],source["Y"]) for k in MODEL_NAMES}


def group_heldout(source_files,groupmap,metadata):
    """All files of original group held out from ALL train-only source moments."""
    names=set(source_files)
    if names!=set(groupmap) or len(names)!=84:
        raise SourceStop("V32_ALL_84_ORIGINAL_SOURCE_FILE_MOMENTS_REQUIRED")
    gids=sorted(set(groupmap.values()),key=lambda z:int(z))
    if len(gids)!=12 or gids!=[str(i) for i in range(1,13)]:
        raise SourceStop("V32_ALL_TWELVE_ORIGINAL_GROUP_ID_REQUIRED")
    source_count_per_group={g:sum(v==g for v in groupmap.values()) for g in gids}
    if min(source_count_per_group.values())<3:
        raise SourceStop("V32_SHOAL_MINIMUM_ORIGINAL_TRIALS_STOP")
    if sum(source_count_per_group.values())!=84:
        raise SourceStop("V32_ORIGINAL_AUTHOR_GROUP_MEMBERSHIP_DUPLICATED")
    for name,data in source_files.items():
        if set(data)!=set(MODEL_NAMES):
            raise SourceStop("V32_COMMON_MODEL_MOMENT_SCHEMA_CHANGED")
    fold=[]
    for heldgroup in gids:
        training_names=[name for name in sorted(names) if groupmap[name]!=heldgroup]
        held_names=[name for name in sorted(names) if groupmap[name]==heldgroup]
        if not training_names or not held_names:
            raise SourceStop("V32_ORIGINAL_TRAIN_TEST_GROUP_NOT_PARTITIONED")
        train_ids=set(groupmap[x] for x in training_names)
        if heldgroup in train_ids or len(train_ids)!=11:
            raise SourceStop("V32_FOCAL_ORIGINAL_BIOLOGICAL_SHOAL_LEAKAGE")
        group={
          "original_heldout_shoal_ID":heldgroup,
          "n_original_trial_files_heldout":len(held_names),
          "original_test_file_IDs":held_names,
          "n_source_train_shoals":len(train_ids),
          "n_source_train_trial_files":len(training_names),
          "train_shoal_IDs":sorted(train_ids,key=int),
          "train_test_shoal_overlap":False,
          "MSE":{}
        }
        for k in MODEL_NAMES:
            pooled=sum_moments([source_files[n][k] for n in training_names])
            coef,bias=train_only_standardized_ridge(pooled)
            file_scores=[score_file_moment(source_files[n][k],coef,bias) for n in held_names]
            group["MSE"][k]={h:float(np.mean([s[h] for s in file_scores])) for h in HORIZONS}
        fold.append(group)
    return summarize_group_holdouts(fold,metadata)


def bootstrap_group_differences(arr,seed=SEED):
    x=np.asarray(arr,dtype=float)
    if x.shape!=(12,) or not np.isfinite(x).all():
        raise SourceStop("V32_BOOTSTRAP_MUST_USE_EXACT_12_ORIGINAL_SHOALS")
    rng=np.random.default_rng(seed)
    ids=rng.integers(0,len(x),(NBOOT,len(x)))
    sample=x[ids].mean(axis=1)
    low,high=np.quantile(sample,[.025,.975])
    return [float(low),float(high)]


def _average_rank(x):
    # scipy-free fixed standard average-tie rank: no source effect tuning.
    x=np.asarray(x,dtype=float)
    order=np.argsort(x,kind="stable")
    out=np.empty(len(x),dtype=float)
    i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[order[j]]==x[order[i]]:j+=1
        out[order[i:j]]=(i+1+j)/2
        i=j
    return out


def spearman_descriptive(x,y):
    if len(x)!=len(y) or len(x)<8: return None
    a,b=_average_rank(x),_average_rank(y)
    aa=a-a.mean();bb=b-b.mean()
    denom=np.linalg.norm(aa)*np.linalg.norm(bb)
    return float((aa@bb)/denom) if denom>0 else None


def summarize_group_holdouts(fold,metadata):
    gids=[r["original_heldout_shoal_ID"] for r in fold]
    if len(gids)!=12 or len(set(gids))!=12:
        raise SourceStop("V32_EXPECTED_12_ORIGINAL_HELDOUT_SHOALS")
    analysis={}
    for h_idx,h in enumerate(HORIZONS):
        m={key:float(np.mean([r["MSE"][key][h] for r in fold])) for key in MODEL_NAMES}
        den=m["G_geometry"]-m["age_0s"]
        ret={key:(float((m["G_geometry"]-m[key])/den) if den>0 else None)
             for key in MODEL_NAMES if key!="G_geometry"}
        diffs={}
        for age_i,age in enumerate(AGES_SECONDS[1:]):
            key=f"age_{age:g}s"
            signed=np.array([r["MSE"][key][h]-r["MSE"]["age_0s"][h] for r in fold])
            diffs[key]={
              "original_shoal_positive":int(np.sum(signed>0)),
              "original_shoal_negative":int(np.sum(signed<0)),
              "original_shoal_exact_zero":int(np.sum(signed==0)),
              "original_shoal_IDs_and_aged_minus_present_MSE":[
                   {"group":g,"delta":float(v)} for g,v in zip(gids,signed)],
              "equal_12_shoal_mean_delta_MSE":float(np.mean(signed)),
              "descriptive_5000_whole_shoal_bootstrap_95pct_delta":bootstrap_group_differences(
                  signed,seed=SEED+h_idx*10+age_i),
              "uncertainty_unit":"12 original biological shoal IDs; cross-validated folds share training shoals"
            }
        first=None
        for age in AGES_SECONDS[1:]:
            v=ret[f"age_{age:g}s"]
            if v is not None and v<=.5: first=age;break
        pergroup=[]
        for r in fold:
            b=r["MSE"]["G_geometry"][h]
            c=r["MSE"]["age_0s"][h]
            t=r["MSE"]["age_0.2s"][h]
            group_strength=(b-c)/b if b>0 else None
            group_retention=(b-t)/(b-c) if b>c else None
            pergroup.append({
              "group_ID":r["original_heldout_shoal_ID"],
              "n_original_files":r["n_original_trial_files_heldout"],
              "current_group_strength_rel_MSE_reduction":group_strength,
              "age_0.2s_retention_if_positive_denominator":group_retention,
              "current_group_positive_MSE_gain":bool(b>c)
            })
        eligible=[z for z in pergroup if z["age_0.2s_retention_if_positive_denominator"] is not None
                   and z["current_group_strength_rel_MSE_reduction"] is not None]
        assoc=spearman_descriptive(
            [z["current_group_strength_rel_MSE_reduction"] for z in eligible],
            [z["age_0.2s_retention_if_positive_denominator"] for z in eligible])
        analysis[h]={
            "equal_original_shoal_mean_MSE":m,
            "group_current_velocity_relative_MSE_reduction":float(1-m["age_0s"]/m["G_geometry"]),
            "original_shoal_normalized_incremental_retention":ret,
            "first_sampled_group_age_at_or_below_half_retention_seconds":first,
            "all_source_shoal_aged_minus_current_contrasts":diffs,
            "within_species_strength_retention_association":{
                "hypothesis":"negative Spearman rank: stronger current group prediction has shorter-lasting old group benefits",
                "n_eligible_original_biological_shoals":len(eligible),
                "n_shoals_undefined_retention_nonpositive_current_gain":12-len(eligible),
                "descriptive_spearman":assoc,
                "hypothesis_negative_direction_supported":(bool(assoc<0) if assoc is not None else None),
                "original_shoal_level_points":pergroup,
                "status":"EXPLORATORY_SAME_SOURCE_12_SHOALS_NO_POPULATION_P"
            }
        }
    return {
        "status":"V32_ALL_84_ORIGINAL_EIDC_TRIALS_TWELVE_SHOAL_HELDOUT_FORECAST",
        "study":"MacGregor Ioannou 2021 EIDC Gasterosteus aculeatus",
        "original_trajectory_EIDC_DOI":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
        "original_author_trial_group_metadata":"Zenodo 5490572 MacGregorIoannou_Data.csv author Group, Trial; code Zenodo 5458081",
        "frozen_study_protocol":"docs/V32_TWELVE_SHOAL_FULL_84_TRIAL_FORECAST_FREEZE.md",
        "n_original_trial_files":84,"n_original_heldout_biological_shoals":12,
        "source_metadata":metadata,
        "source_group_holdout_results":fold,
        "results_by_horizon":analysis,
        "physical_200ms_speed_window_s":.2,
        "original_age_levels_seconds":list(AGES_SECONDS),
        "original_future_horizons_s":{"short":[0,.2],"delayed":[.6,.8]},
        "physical_original_units":"source pixels/sec squared MSE; do not pool across fish species",
        "original_source_positions_or_time_series_redistributed":False,
        "fish_acoustic_calls_or_causal_social_transfer_observed":False,
        "within_species_meta_inference_limit":"12 true biological shoals with shared source study, repeated trials and overlapping training folds, not independent populations or fish vocal interaction"
    }


def save(path,data):
    p=Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
