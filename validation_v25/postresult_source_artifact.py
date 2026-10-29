#!/usr/bin/env python3
"""v25-E explicitly after-outcome 2023 USGS source construction diagnosis.

No fitted models, no change to original v25-C source STOP or v25-D1 results.
Only aggregate geometry of authors' used TRUE and aggregated available FALSE
habitat profiles, including source-only no-fitted sum/norm/max label probes.
"""
from __future__ import annotations
import argparse
import collections
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

import usgs_step_manifest_gate as usgs
import usgs_step_schema_gate as source
import retrospective_habitat_profiles as old

SOURCE_FILE=old.ORIGINAL_SOURCE_FILE
SOURCE_SHA256=old.ORIGINAL_SOURCE_SHA256
EXPECTED_PAIRS=old.ORIGINAL_PAIRS
ENV=old.ENV
ORIGINAL_C_STOP="NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE"
SOURCE_D_PRIMARY_GAIN=0.0058554394644328165
D_PERFECT_PAIRED_RANKING=1.0


def numeric_simple_probe(a:np.ndarray,b:np.ndarray)->dict:
    if len(a)!=len(b) or a.ndim!=2 or b.ndim!=2 or a.shape[1]!=len(ENV):
        raise ValueError("Original matched source data shape changed")
    n=len(a)
    if n!=EXPECTED_PAIRS:
        raise ValueError("Original number of paired TRUE/FALSE rows changed")
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("Source contains nonfinite raw habitat values")
    if a.min()<0 or b.min()<0 or a.max()>100 or b.max()>100:
        raise ValueError("Original source percentage-scale gate changed")
    sum_true=a.sum(axis=1)
    sum_false=b.sum(axis=1)
    norm_true=np.linalg.norm(a,axis=1)
    norm_false=np.linalg.norm(b,axis=1)
    peak_true=a.max(axis=1)
    peak_false=b.max(axis=1)
    nnz_true=np.sum(a>0,axis=1)
    nnz_false=np.sum(b>0,axis=1)
    def stats(v):
        return {
            "minimum":float(v.min()),"median":float(np.median(v)),
            "maximum":float(v.max()),"mean":float(v.mean()),
            "n_exact_zero":int(np.sum(v==0)),
            "n_exact_100":int(np.sum(v==100)),
            "n_within_99_to_101":int(np.sum((v>=99)&(v<=101)))
        }
    def score(v1,v2):
        delta=v1-v2
        return {
            "fraction_TRUE_ranked_above_FALSE_by_naive_source_invariant":
                float(np.mean((delta>0)+.5*(delta==0))),
            "TRUE_greater_count":int(np.sum(delta>0)),
            "FALSE_greater_count":int(np.sum(delta<0)),
            "equal_count":int(np.sum(delta==0)),
        }
    dif=a-b
    per_col={}
    for i,col in enumerate(ENV):
        d=dif[:,i]
        per_col[col]={
            "source_TRUE_minus_FALSE_mean_percentage_points":float(d.mean()),
            "source_TRUE_minus_FALSE_positive_pair_count":int(np.sum(d>0)),
            "source_TRUE_minus_FALSE_negative_pair_count":int(np.sum(d<0)),
            "source_TRUE_minus_FALSE_exact_tie_count":int(np.sum(d==0)),
            "original_TRUE_raw_max":float(a[:,i].max()),
            "original_FALSE_raw_max":float(b[:,i].max()),
        }
    return {
      "status":"POST_OUTCOME_SOURCE_CONSTRUCTION_DIAGNOSTIC_NOT_INDEPENDENT_VALIDATION",
      "n_original_paired_case_TRUE_FALSE_sources":n,
      "source_original_habitat_field_count":len(ENV),
      "original_TRUE_raw_seven_col_sum":stats(sum_true),
      "original_FALSE_raw_seven_col_sum":stats(sum_false),
      "original_TRUE_raw_L2_norm":stats(norm_true),
      "original_FALSE_raw_L2_norm":stats(norm_false),
      "original_TRUE_raw_single_largest_habitat_value":stats(peak_true),
      "original_FALSE_raw_single_largest_habitat_value":stats(peak_false),
      "source_TRUE_nonzero_habitat_columns":stats(nnz_true),
      "source_FALSE_nonzero_habitat_columns":stats(nnz_false),
      "source_naive_NO_FIT_sum_ranking":score(sum_true,sum_false),
      "source_naive_NO_FIT_concentration_norm_ranking":score(norm_true,norm_false),
      "source_naive_NO_FIT_largest_category_ranking":score(peak_true,peak_false),
      "source_raw_each_habitat_dimension_difference":per_col,
      "source_animal_ID_or_exact_GPS_datetime_values_exported":False,
      "fitted_prediction_models_or_coefficients_changed":False,
      "any_new_confirmatory_ecological_hypothesis_test":False,
    }


def run()->dict:
    item=None
    for url in usgs.ENDPOINTS:
        try:
            item=usgs.original_item(usgs.original_json(url))
            break
        except Exception:continue
    out={
      "study":"v25-E-after-outcome-waterfowl-original-TRUE-FALSE-generated-source-artifact-audit",
      "source_DOI":usgs.SOURCE_DOI,
      "status":"NOT_ADMITTED_ORIGINAL_PROVIDER_SOURCE_UNAVAILABLE",
      "original_source_receipt":None,
      "original_case_pair_source_geometry":None,
      "original_v25C_source_stop_unchanged":ORIGINAL_C_STOP,
      "original_v25D_observed_primary_M1_minus_M3_unchanged":SOURCE_D_PRIMARY_GAIN,
      "original_v25D_all_three_trained_rank_fraction_unchanged":D_PERFECT_PAIRED_RANKING,
      "this_audit_was_registered_AFTER_v25D_original_effect_opened":True,
      "new_biological_memory_or_Boids_force_result_claimed":False}
    if item is None:return out
    f=source.select_files(item)[SOURCE_FILE]
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/SOURCE_FILE
        original=source.fetch_verified(SOURCE_FILE,f,path)
        if original["original_independent_sha256"]!=SOURCE_SHA256:
            raise ValueError("Source changed since original score")
        raw=pd.read_csv(path,dtype={
            "birdyear":"string","timestamp":"string","case":"string",
        },low_memory=False)
        if len(raw)!=old.ORIGINAL_ROWS or tuple(raw.columns)!=old.COLUMNS:
            raise ValueError("Original source schema changed")
        key=["birdyear","timestamp"]
        true=raw.loc[raw["case"]=="TRUE",key+list(ENV)].set_index(key).sort_index()
        false=raw.loc[raw["case"]=="FALSE",key+list(ENV)].set_index(key).sort_index()
        if not true.index.equals(false.index):
            raise ValueError("Original TRUE/FALSE source keys do not match")
        profiles=numeric_simple_probe(true.to_numpy(float),false.to_numpy(float))
    out["original_source_receipt"]=original
    out["original_case_pair_source_geometry"]=profiles
    out["status"]=profiles["status"]
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v25/results/postresult_source_artifact_v25E.json"))
    args=p.parse_args()
    r=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V25E_POST_OUTCOME_DIAGNOSTICS",json.dumps(r,sort_keys=True))
    print("V25E_NOT_AN_INDEPENDENT_CONFIRMATION_OR_BIOLOGICAL_MEMORY_RESULT")
if __name__=="__main__":
    main()
