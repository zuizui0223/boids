#!/usr/bin/env python3
"""v25-F case-specific source semantic correction (POST v25-D/E).

The immutable original v25-C and v25-D results remain preserved as separate
source failure and artifact-invalid ranking. This new exploratory endpoint:
  case TRUE -> exactly one nonzero observed habitat code 1 or 2 -> indicator 1
  case FALSE -> integer count across 100 generated step endpoints -> /100.
Reuse original C prediction/scoring/CI/model functions without modification.
No real 101-choice opportunities or actual future start positions are claimed.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

import usgs_step_manifest_gate as usgs
import usgs_step_schema_gate as source
import retrospective_habitat_profiles as frozen

SOURCE_FILE=frozen.ORIGINAL_SOURCE_FILE
SOURCE_SHA256=frozen.ORIGINAL_SOURCE_SHA256
SOURCE_ROWS=frozen.ORIGINAL_ROWS
ENV=frozen.ENV
EXPECTED_TRUE=frozen.ORIGINAL_PAIRS
EXPECTED_FALSE=frozen.ORIGINAL_PAIRS
DIVIDE_FALSE_BY=100.
TRUE_ALLOWED_CODES=(1.,2.)
AVAIL_ROW_SUM_LO=100.
AVAIL_ROW_SUM_HI=201.
ORIGINAL_C_STOP="NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE"
ORIGINAL_D_INVALID="INVALID_FOR_ECOLOGY__CASE_TRUE_AND_FALSE_DIFFERENT_MEASUREMENT_SCALES"
EXPLICIT_E_AUDIT="docs/V25E_POSTRESULT_SOURCE_CONSTRUCTION_AUDIT.md"
NEW_REGISTRATION="docs/V25F_FROZEN_CASE_SPECIFIC_SOURCE_UNIT_CORRECTION.md"


def correct_original_case_specific_percentage(raw:Path,out:Path)->dict:
    df=pd.read_csv(raw,dtype={k:"string" for k in frozen.COLUMNS[:6]},
                   low_memory=False)
    if tuple(df.columns)!=frozen.COLUMNS or len(df)!=SOURCE_ROWS:
        raise ValueError("Previously MD5-pinned source column/row structure changed")
    if df["case"].isna().any() or set(df["case"])!={"TRUE","FALSE"}:
        raise ValueError("Source original case label schema changed")
    used=(df["case"]=="TRUE").to_numpy()
    if int(used.sum())!=EXPECTED_TRUE or int((~used).sum())!=EXPECTED_FALSE:
        raise ValueError("Source original TRUE/FALSE paired row totals changed")
    a=df.loc[used,list(ENV)].apply(pd.to_numeric,errors="raise").to_numpy(float)
    b=df.loc[~used,list(ENV)].apply(pd.to_numeric,errors="raise").to_numpy(float)
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("Original habitat raw source has nonfinite values")
    used_nonzero=np.sum(a>0,axis=1)
    if not np.all(used_nonzero==1):
        raise ValueError("Original TRUE source no longer one nonzero category per used row")
    vals=a[a>0]
    if not np.isin(vals,TRUE_ALLOWED_CODES).all():
        raise ValueError("Original observed TRUE occurrence codes are not exactly 1 or 2")
    if (b.min()<0 or b.max()>100 or
        not np.all(np.isclose(b,np.round(b),atol=0,rtol=0))):
        raise ValueError("Original FALSE 100 generated step counts exceed integer 0..100")
    total=b.sum(axis=1)
    if (total.min()<AVAIL_ROW_SUM_LO or total.max()>AVAIL_ROW_SUM_HI):
        raise ValueError("Original FALSE source availability total changed")
    # This is the only NEW transformation. Confirm no results/individuals
    # were used to define the scale or to drop original special source rows.
    df.loc[used,list(ENV)]=(a>0).astype(float)
    df.loc[~used,list(ENV)]=b/DIVIDE_FALSE_BY
    df.to_csv(out,index=False)
    return {
        "status":"POST_SOURCE_AUDIT_CASE_SPECIFIC_ORIGINAL_UNIT_RECONCILED",
        "original_raw_source_rows":len(df),
        "original_true_used_individual_profile_rows":int(used.sum()),
        "original_true_one_nonzero_source_class_per_row":True,
        "original_used_category_nonzero_encoded_1":int(np.sum(vals==1)),
        "original_used_category_nonzero_encoded_2":int(np.sum(vals==2)),
        "original_false_aggregated_availability_profile_rows":int((~used).sum()),
        "original_false_total_100":int(np.sum(total==100)),
        "original_false_total_more_than_100":int(np.sum(total>100)),
        "original_false_100_source_generated_counts_rescaled":True,
        "true_used_is_binary_onehot_after_recode":True,
        "false_candidate_counts_divisor":DIVIDE_FALSE_BY,
        "normalized_source_rows_dropped":0,
        "old_D_all_field_100_division_IS_INVALID_FOR_ECOLOGY":True,
        "source_format_repair_was_after_outcome_audit_not_independent_confirmation":True,
        "animal_GPS_exact_time_ID_or_habitat_rows_redistributed":False,
    }


def run()->dict:
    out={
        "study":"v25F-USGS-2023-493-birdyear-source-case-specific-exploratory-retrospective-habitat",
        "source_DOI":usgs.SOURCE_DOI,
        "new_registration":NEW_REGISTRATION,
        "original_frozen_C_status":ORIGINAL_C_STOP,
        "original_D_invalid_ecological_claim":ORIGINAL_D_INVALID,
        "post_outcome_E_source_diagnostic":EXPLICIT_E_AUDIT,
        "status":"NOT_ADMITTED_ORIGINAL_SOURCE_OR_UNIT_UNVERIFIED",
        "original_file_integrity":None,
        "source_case_specific_unit_correction":None,
        "source_original_cohort":None,
        "source_whole_birdyear_folds":None,
        "source_year_holdouts":None,
        "source_corrected_exploratory_result":None,
        "no_original_raw_birdyears_exact_times_or_habitat_rows_exported":True,
        "previous_v13_to_v24_results_unchanged":True,
        "original_USGS_source_100_simulated_alternatives_not_reconstructed":True,
        "source_movement_kernel_prior_to_heldout_bird_data_NOT_independently_verified":True,
    }
    item=None
    for url in usgs.ENDPOINTS:
        try:
            item=usgs.original_item(usgs.original_json(url))
            break
        except Exception as e:
            out.setdefault("source_get_failures",[]).append({
                "url":url,"error":usgs.error(e)})
    if item is None:return out
    original_file=source.select_files(item)[SOURCE_FILE]
    try:
        with tempfile.TemporaryDirectory() as temp:
            original_path=Path(temp)/SOURCE_FILE
            normalized_path=Path(temp)/"ephemeral_corrected_case_specific.csv"
            verify=source.fetch_verified(SOURCE_FILE,original_file,original_path)
            if verify["original_independent_sha256"]!=SOURCE_SHA256:
                raise ValueError("Original source checksum drift")
            out["original_file_integrity"]=verify
            corrected=correct_original_case_specific_percentage(
                original_path,normalized_path)
            out["source_case_specific_unit_correction"]=corrected
            # Invariance: use original C code unchanged. The original C
            # registered cohort/times/folds/metrics, only source fields
            # now mean the same percentage units on TRUE and FALSE.
            pairs,original_structure=frozen.original_source_paired_profile(normalized_path)
            out["source_original_cohort"]=original_structure
            scored,folds=frozen.all_fold_results(pairs)
            out["source_whole_birdyear_folds"]=folds
            analysis=frozen.cluster_stats(scored)
            out["source_corrected_exploratory_result"]=analysis
            if analysis["status"].startswith("NOT_ADMITTED"):
                out["status"]=analysis["status"]
                return out
            out["source_year_holdouts"]=frozen.leave_entire_calendar_year_out(pairs)
            out["status"]="EXPLORATORY_POST_OUTCOME_SOURCE_CASE_CORRECTED_USGS_HABITAT_PROFILES"
    except Exception as e:
        out["status"]="NOT_ADMITTED_CASE_SOURCE_OR_MODEL_VALIDATION"
        out["stop_reason"]=type(e).__name__+": "+str(e)[:240]
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v25/results/case_corrected_paired_habitat_v25F.json"))
    a=p.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V25F_SOURCE",json.dumps(d["original_file_integrity"],sort_keys=True))
    print("V25F_CASE_UNIT",json.dumps(d["source_case_specific_unit_correction"],sort_keys=True))
    print("V25F_SOURCE_COHORT",json.dumps(d["source_original_cohort"],sort_keys=True))
    print("V25F_STATUS",d["status"])
    if d["status"].startswith("EXPLORATORY"):
        o=d["source_corrected_exploratory_result"]
        print("V25F_EFFECTS",json.dumps(o["frozen_contrasts"],sort_keys=True))
        print("V25F_MODEL_ABSOLUTE",json.dumps({
            "logloss":o["whole_birdyear_equal_mean_surrogate_logloss_M0_M1_M2_M3"],
            "rank":o["whole_birdyear_equal_mean_profile_ranking_M0_M1_M2_M3"],
            "birdyears":o["original_independent_source_birdyear_tokens"],
            "source_pairs":o["original_chronologically_later_aggregate_profile_pairs_scored"]
        },sort_keys=True))
        print("V25F_YEARS",json.dumps(d["source_year_holdouts"],sort_keys=True))
        print("V25F_ALL_ANON_BIRDYEAR",json.dumps(o["source_birdyear_anonymized"],sort_keys=True))
    else:
        print("V25F_STOP",json.dumps(d.get("stop_reason"),sort_keys=True))
    print("V25F_NO_COGNITIVE_MEMORY_OR_REAL_101_WETLAND_CHOICE_INFERENCE")
if __name__=="__main__":
    main()
