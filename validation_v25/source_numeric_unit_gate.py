#!/usr/bin/env python3
"""v25-D0 source-only original numeric unit/range audit; NO habitat effect.

Read only the seven original environmental numeric columns, without
case TRUE/FALSE, birdyear, timestamp, species or matched pair identity.
Prespecified source transformation: every field /100 if all raw fields
lie [0,100] and any >1, identity if all within [0,1]; otherwise STOP.
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

import usgs_step_manifest_gate as usgs
import usgs_step_schema_gate as source

SOURCE_FILE="Data Release P9ELSUHN.csv"
SOURCE_SHA256="1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15"
ENV=("Corn","Field","Other","Protected","Rice","Urban","Wetland")
EXPECTED_ROWS=380578

def characterize_raw_numeric_only(frame:pd.DataFrame)->dict:
    if set(frame.columns)!=set(ENV) or len(frame)!=EXPECTED_ROWS:
        raise ValueError("Original source habitat/row schema changed")
    fields={}
    any_over_one=False
    all_finite_and_0_to_100=True
    for name in ENV:
        col=pd.to_numeric(frame[name],errors="coerce").to_numpy(dtype=float)
        finite=np.isfinite(col)
        bad=int((~finite).sum())
        lo=float(np.min(col[finite])) if finite.any() else None
        hi=float(np.max(col[finite])) if finite.any() else None
        negative=int(np.sum(finite & (col<0)))
        above1=int(np.sum(finite & (col>1)))
        above100=int(np.sum(finite & (col>100)))
        all_finite_and_0_to_100 &= (
            bad==0 and negative==0 and above100==0)
        any_over_one |= above1>0
        fields[name]={
          "physical_source_rows":len(col),
          "nonfinite_or_missing_original_values":bad,
          "raw_numeric_minimum":lo,
          "raw_numeric_maximum":hi,
          "negative_count":negative,
          "values_above_1_count":above1,
          "values_above_100_count":above100,
          "values_exact_zero_count":int(np.sum(finite & (col==0))),
          "values_exact_one_count":int(np.sum(finite & (col==1))),
          "values_exact_hundred_count":int(np.sum(finite & (col==100))),
          "rounded_unique_numeric_count":int(len(np.unique(col[finite]))),
        }
    if not all_finite_and_0_to_100:
        status="NOT_ADMITTED_ORIGINAL_NUMERIC_RANGE_OR_MISSINGNESS"
        division=None
    else:
        division=100 if any_over_one else 1
        status="SOURCE_PERCENTAGE_UNIT_RULE_VERIFIED_NO_EFFECT"
    return {
      "study":"v25-D0-original-USGS-2023-environmental-unit-only",
      "status":status,
      "original_source_rows":len(frame),
      "analyzed_only_columns":list(ENV),
      "field_aggregate_raw_domain":fields,
      "prespecified_all_field_scale_divisor":division,
      "original_source_case_used_available_values_read":False,
      "original_birdyear_or_timestamp_ID_values_read":False,
      "any_source_habitat_prediction_or_coefficients_computed":False,
      "original_used_and_generated_avail_profiles_not_independent_animal_choices":True,
      "v25_C_original_fail_closed_status_unchanged":
         "NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE",
    }

def run()->dict:
    item=None
    for url in usgs.ENDPOINTS:
        try:
            item=usgs.original_item(usgs.original_json(url))
            break
        except Exception:continue
    out={
      "study":"v25-D0-original-USGS-environmental-unit-only",
      "status":"NOT_ADMITTED_ORIGINAL_USGS_SOURCE_UNAVAILABLE",
      "source_DOI":usgs.SOURCE_DOI,
      "original_source_receipt":None,
      "domain_audit":None,
      "any_habitat_ranking_effect_computed":False,
    }
    if item is None:return out
    original_file=source.select_files(item)[SOURCE_FILE]
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/SOURCE_FILE
        receipt=source.fetch_verified(SOURCE_FILE,original_file,path)
        if receipt["original_independent_sha256"]!=SOURCE_SHA256:
            raise ValueError("Previously frozen source hash changed")
        out["original_source_receipt"]=receipt
        # usecols guarantees no parsing of original case, birdyear or
        # timestamp response/source identity columns.
        numeric=pd.read_csv(path,usecols=list(ENV),low_memory=False)
        audit=characterize_raw_numeric_only(numeric)
        out["domain_audit"]=audit
        out["status"]=audit["status"]
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
       "validation_v25/results/original_habitat_unit_domain_v25.json"))
    a=p.parse_args()
    out=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V25D_SOURCE_ONLY_HABITAT_DOMAIN",json.dumps(out,sort_keys=True))
    print("V25D_NO_GROUP_BY_USED_OR_AVAILABLE_AND_NO_EFFECT_FITTED")
if __name__=="__main__":
    main()
