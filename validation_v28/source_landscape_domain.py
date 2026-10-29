#!/usr/bin/env python3
"""v28-C0 inspect ONLY original bat landscape covariate global units/missingness.

No case_ labels, batid, trackid, GPS positions or case-wise effects.
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
import original_source_manifest as z
import three_file_source_gate as g

SOURCE_FILE="Model_dataset_RSFFlight_Complete_EPSG25833.csv"
SOURCE_SHA256="76f92b1442eb4350ee6d83ede83b5e43fda4b9f3997e3fd9a3618a44f2470375"
ROWS=48774
NUMERIC=("mindist_WKA_inKm","DistanceAssumedRoostsInKm")
CATEGORIES=("clc2_20m","forestornot")
MAX_MISSING_SHARE=0.05

def audit(data:pd.DataFrame)->dict:
    if len(data)!=ROWS or set(data.columns)!=set((*NUMERIC,*CATEGORIES)):
        raise ValueError("Original source-only four-feature/domain source drift")
    numeric={}
    eligible=True
    for name in NUMERIC:
        values=pd.to_numeric(data[name],errors="coerce").to_numpy(dtype=float)
        valid=values[np.isfinite(values)]
        missed=int((~np.isfinite(values)).sum())
        neg=int((valid<0).sum())
        eligible&=(len(valid)>0 and neg==0 and missed/len(values)<=MAX_MISSING_SHARE)
        numeric[name]={
          "source_count":len(values),
          "missing_or_nonfinite":missed,
          "negative":neg,
          "finite_minimum":float(np.min(valid)) if len(valid) else None,
          "finite_quantiles_25_50_75":list(map(float,np.quantile(valid,[.25,.5,.75]))) if len(valid) else None,
          "finite_maximum":float(np.max(valid)) if len(valid) else None,
          "measurement_unit_original":"km",
        }
    categorical={}
    for name in CATEGORIES:
        s=data[name].astype("string")
        counts=s.value_counts(dropna=False)
        missing=int(s.isna().sum())
        eligible &= missing/len(s)<=MAX_MISSING_SHARE
        categorical[name]={
           "row_count":len(s),
           "original_categories_including_null":len(counts),
           "source_missing":missing,
           "original_category_frequencies_masked":{
              ("<missing>" if pd.isna(k) else str(k)[:50]):int(v)
              for k,v in counts.items()
           },
        }
    return {
      "status":"SOURCE_COVARIATE_DOMAIN_VERIFIED_NO_BAT_PREFERENCE"
          if eligible else "NOT_ADMITTED_NUMERIC_OR_CATEGORY_SOURCE_DOMAIN",
      "original_source_model_rows":ROWS,
      "original_numeric_source_global_domains":numeric,
      "original_categorical_source_frequencies":categorical,
      "source_only_fields_read":list((*NUMERIC,*CATEGORIES)),
      "source_original_used_random_case_label_read":False,
      "source_actual_bat_ID_or_track_ID_read":False,
      "source_UTM_coordinates_or_habitat_selection_effect_read":False,
      "source_effect_or_predictive_model_fitted":False,
      "source_case_by_environment_correlations_opened":False,
    }

def run()->dict:
    source={x["filename"]:x for x in z.source_list(z.fetch_original())}
    if SOURCE_FILE not in source:raise ValueError("Pinned bat model source absent")
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/SOURCE_FILE
        receipt=g.download_verified(source[SOURCE_FILE],path)
        if receipt["independently_computed_sha256"]!=SOURCE_SHA256:
            raise ValueError("Previously published v28 bat model source SHA changed")
        data=pd.read_csv(path,usecols=list((*NUMERIC,*CATEGORIES)),
                         low_memory=False)
        info=audit(data)
    return {
      "study":"v28-C0-independent-noctule-bat-turbine-roost-forest-source-domain",
      "source_DOI":"10.5281/zenodo.7535030",
      "source_original_integrity":receipt,
      "source_domain_audit":info,
      "status":info["status"],
      "original_60_bat_107_flight_repeated_history_gate_passed":False,
      "source_ID_and_environmental_response_joint_model_not_fitted":True,
      "older_v13_v27_endpoints_unchanged":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v28/results/noctule_source_landcover_turbine_domain_v28.json"))
    args=p.parse_args()
    d=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V28_SOURCE_ONLY_ENVIRONMENT_DOMAIN",json.dumps(d,sort_keys=True))
    print("V28_NO_ACTUAL_BAT_AVOIDANCE_OR_NICHE_PREDICTION")
if __name__=="__main__":
    main()
