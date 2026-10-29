#!/usr/bin/env python3
"""v25-D1 independently registered after original source unit mismatch.

ONE precommitted numeric correction: original 7 habitat integer percentages
/ 100 on ALL source rows. All 4 models, source cohorts, SHA folds, history
chronology, individual bootstrap and year-holdouts reuse the frozen v25-C
pre-outcome functions UNCHANGED. This distinct study is exploratory after
source FORMAT audit, not a claim that original v25-C analysis passed.
"""
from __future__ import annotations
import argparse
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

import retrospective_habitat_profiles as old
import source_numeric_unit_gate as unit
import usgs_step_manifest_gate as usgs
import usgs_step_schema_gate as source

SOURCE_FILE=old.ORIGINAL_SOURCE_FILE
SOURCE_SHA256=old.ORIGINAL_SOURCE_SHA256
FROZEN_NEW_PROTOCOL="docs/V25D_FROZEN_PERCENT_CORRECTED_EXPLORATORY_PROFILE.md"
FROZEN_OLD_C_STATUS="NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE"
ONLY_PERMITTED_DIVISOR=100

def unit_normalized_transient_original(raw:Path,to:Path)->dict:
    # No source category or numeric habitat effect is used to DECIDE scale:
    # all seven fields must match the exact registered 0..100 source audit.
    dtype={v:"string" for v in old.COLUMNS[:6]}
    df=pd.read_csv(raw,dtype=dtype,low_memory=False)
    if tuple(df.columns)!=old.COLUMNS or len(df)!=old.ORIGINAL_ROWS:
        raise ValueError("Original raw file structure changed")
    audit=unit.characterize_raw_numeric_only(df[list(old.ENV)])
    if (audit["status"]!="SOURCE_PERCENTAGE_UNIT_RULE_VERIFIED_NO_EFFECT"
        or audit["prespecified_all_field_scale_divisor"]!=ONLY_PERMITTED_DIVISOR):
        raise ValueError("Pinned original percentage normalization gate failed")
    for name in old.ENV:
        df[name]=pd.to_numeric(df[name],errors="raise").astype(float)/ONLY_PERMITTED_DIVISOR
    # The corrected file is an EPHEMERAL private runtime copy. It is never
    # committed or published; full original source SHA was checked already.
    df.to_csv(to,index=False)
    return {
        "status":"PREDECLARED_SOURCE_SCALE_CORRECTION_ONLY",
        "source_raw_original_rows":len(df),
        "source_fields_converted":list(old.ENV),
        "universal_divisor":ONLY_PERMITTED_DIVISOR,
        "original_source_unit_domain_verified":True,
        "original_RDS_or_original_movement_tracks_redistributed":False,
        "new_observed_effects_or_outcomes_used_to_choose_scaling":False,
    }

def run()->dict:
    d={
        "study":"v25D-independent-2023-USGS-paired-habitat-profile-source-unit-conditioned-exploratory",
        "source_original_DOI":usgs.SOURCE_DOI,
        "registered_new_protocol":FROZEN_NEW_PROTOCOL,
        "original_v25C_untouched_source_stop":FROZEN_OLD_C_STATUS,
        "source_integrity":None,
        "source_unit_correction":None,
        "source_original_profile_grain":None,
        "source_five_birdyear_folds":None,
        "source_all_year_holdouts":None,
        "new_exploratory_result":None,
        "status":"NOT_ADMITTED_SOURCE_OR_UNIT_UNVERIFIED",
        "no_original_bird_ID_exact_time_or_habitat_rows_exported":True,
        "no_real_101_alternatives_or_step_origin_recovered":True,
        "all_v13_through_v24_frozen_original_results_unchanged":True,
    }
    item=None
    for url in usgs.ENDPOINTS:
        try:
            item=usgs.original_item(usgs.original_json(url))
            break
        except Exception as e:
            d.setdefault("source_access_failures",[]).append({
                "route":url,"error":usgs.error(e)})
    if item is None:return d
    info=source.select_files(item)[SOURCE_FILE]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            original_path=Path(tmp)/SOURCE_FILE
            normalized_path=Path(tmp)/"source_percentages_normalized.csv"
            receipt=source.fetch_verified(SOURCE_FILE,info,original_path)
            if receipt["original_independent_sha256"]!=SOURCE_SHA256:
                raise ValueError("Previously frozen source SHA256 changed")
            d["source_integrity"]=receipt
            corrected=unit_normalized_transient_original(original_path,normalized_path)
            d["source_unit_correction"]=corrected
            pairs,profile=old.original_source_paired_profile(normalized_path)
            d["source_original_profile_grain"]=profile
            # All functions reused from old pre-outcome model unchanged.
            test_scores,folds=old.all_fold_results(pairs)
            d["source_five_birdyear_folds"]=folds
            comparison=old.cluster_stats(test_scores)
            if comparison["status"].startswith("NOT_ADMITTED"):
                d["status"]=comparison["status"]
                d["new_exploratory_result"]=comparison
                return d
            years=old.leave_entire_calendar_year_out(pairs)
            d["source_all_year_holdouts"]=years
            d["new_exploratory_result"]=comparison
            d["status"]="EXPLORATORY_AFTER_SOURCE_UNIT_2023_USGS_PAIRED_PROFILE_FORECAST"
    except Exception as e:
        d["status"]="NOT_ADMITTED_NEW_SOURCE_UNIT_OR_MODEL_VALIDATION"
        d["source_or_model_stop_reason"]=type(e).__name__+": "+str(e)[:250]
    return d

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
         "validation_v25/results/source_unit_corrected_paired_profile_v25D.json"))
    args=p.parse_args()
    x=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V25D_SOURCE",json.dumps(x["source_integrity"],sort_keys=True))
    print("V25D_UNIT_CORRECTION",json.dumps(x["source_unit_correction"],sort_keys=True))
    print("V25D_SOURCE_SUPPORT",json.dumps(x["source_original_profile_grain"],sort_keys=True))
    print("V25D_STATUS",x["status"])
    if x["new_exploratory_result"] and x["status"].startswith("EXPLORATORY"):
        o=x["new_exploratory_result"]
        print("V25D_FOUR_REGISTERED_CONTRASTS",json.dumps(o["frozen_contrasts"],sort_keys=True))
        print("V25D_ABSOLUTE_SCORES",json.dumps({
            "equal_birdyear_logloss":o["whole_birdyear_equal_mean_surrogate_logloss_M0_M1_M2_M3"],
            "equal_birdyear_pair_rank":o["whole_birdyear_equal_mean_profile_ranking_M0_M1_M2_M3"],
            "source_birdyears":o["original_independent_source_birdyear_tokens"],
            "scored_later_pairs":o["original_chronologically_later_aggregate_profile_pairs_scored"]
        },sort_keys=True))
        print("V25D_ALL_YEARS",json.dumps(x["source_all_year_holdouts"],sort_keys=True))
        print("V25D_ALL_ANON_BIRDYEAR",json.dumps(o["source_birdyear_anonymized"],sort_keys=True))
    else:
        print("V25D_STOP",json.dumps(x.get("source_or_model_stop_reason"),sort_keys=True))
    print("V25D_ORIGINAL_V25C_NOT_ADMITTED_IMMUTABLE")
if __name__=="__main__":
    main()
