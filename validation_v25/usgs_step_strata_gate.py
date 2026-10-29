#!/usr/bin/env python3
"""v25-B3 original step sample grammar from USGS 2023 CSV, SOURCE ONLY.

Inspect exact original birdyear/timestamp/species/case/season/photoperiod
categorical keys and frequencies. NO Corn/Field/Other/Protected/Rice/Urban/
Wetland numeric values, no original GPS coordinates, and no fitted ecological
response or animal movement coefficients.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import tempfile
from pathlib import Path

import usgs_step_manifest_gate as original
import usgs_step_schema_gate as schema

SOURCE_FILE="Data Release P9ELSUHN.csv"
SOURCE_SHA256="1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15"
ORIGINAL_SOURCE_ROWS=380578
EXPECTED_COLUMNS=(
    "birdyear","timestamp","species","case","season","photoperiod",
    "Corn","Field","Other","Protected","Rice","Urban","Wetland")
ENV_COLS=("Corn","Field","Other","Protected","Rice","Urban","Wetland")
METADATA_COLS=("birdyear","timestamp","species","case","season","photoperiod")
MIN_SOURCE_ID=20
MIN_ORIGINAL_STRATA=200
MIN_REPEATED_IDS=20
MIN_ORIGINAL_DATES=3


def masked_shape(s: str) -> str:
    return "".join("D" if c.isdigit() else "A" if c.isalpha() else c
                   for c in str(s).strip()[:52])


def parse_timestamp_syntax(s: str) -> bool:
    raw=str(s).strip()
    if not raw:return False
    formats=(
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S%z"
    )
    for pattern in formats:
        try:
            dt.datetime.strptime(raw,pattern)
            return True
        except ValueError:
            continue
    try:dt.datetime.fromisoformat(raw);return True
    except ValueError:return False


def source_strata_only(path:Path)->dict:
    groups=collections.defaultdict(lambda:collections.Counter())
    study_meta={}
    distinct_dates=collections.defaultdict(set)
    species=collections.Counter()
    season=collections.Counter()
    photoperiod=collections.Counter()
    label=collections.Counter()
    original_labels_not_binary=collections.Counter()
    time_shapes=collections.Counter()
    missing=collections.Counter()
    dt_parseable=rows=0
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as f:
        reader=csv.DictReader(f)
        head=tuple(reader.fieldnames or ())
        if head!=EXPECTED_COLUMNS:
            raise ValueError("Previously pinned original source 13-column header changed")
        for row in reader:
            rows+=1
            if rows>ORIGINAL_SOURCE_ROWS:
                raise ValueError("Original source rows exceed byte-frozen count")
            # Never read the seven original environmental numeric data fields.
            key={c:(row.get(c) or "").strip() for c in METADATA_COLS}
            for field,value in key.items():
                if not value or value.upper() in ("NA","NAN","NULL"):
                    missing[field]+=1
            b=key["birdyear"]
            t=key["timestamp"]
            y=key["case"]
            if not b or not t:
                continue
            dt_parseable+=int(parse_timestamp_syntax(t))
            time_shapes[masked_shape(t)]+=1
            group=(b,t)
            # Exact source category, no target-choice inference from habitats.
            if y not in ("TRUE","FALSE"):
                original_labels_not_binary[masked_shape(y)]+=1
            groups[group][y]+=1
            label[y]+=1
            species[key["species"]]+=1
            season[key["season"]]+=1
            photoperiod[key["photoperiod"]]+=1
            distinct_dates[b].add(t)
            if b in study_meta:
                if study_meta[b]!=key["species"]:
                    raise ValueError("Original bird-year changing species identity")
            else:study_meta[b]=key["species"]
    if rows!=ORIGINAL_SOURCE_ROWS:
        raise ValueError("Source original physical case row count changed")
    sz=collections.Counter()
    use_dist=collections.Counter()
    control_dist=collections.Counter()
    valid=0
    incompatible=0
    candidate_label_counts=collections.Counter()
    for counts in groups.values():
        size=sum(counts.values())
        sz[size]+=1
        use_dist[counts["TRUE"]]+=1
        control_dist[counts["FALSE"]]+=1
        if (set(counts).issubset({"TRUE","FALSE"}) and
            counts["TRUE"]==1 and counts["FALSE"]==1):
            valid+=1
            candidate_label_counts[counts["FALSE"]]+=1
        else:
            incompatible+=1
    repeat3=sum(len(x)>=3 for x in distinct_dates.values())
    eligible=(len(distinct_dates)>=MIN_SOURCE_ID and
              valid>=MIN_ORIGINAL_STRATA and
              repeat3>=MIN_REPEATED_IDS and
              not original_labels_not_binary and
              not missing["birdyear"] and not missing["timestamp"] and
              dt_parseable==rows)
    return {
        "status":("SOURCE_ORIGINAL_PAIRED_USE_AGGREGATED_AVAIL_SCHEMA_VERIFIED_NO_EFFECT"
                  if eligible else "NOT_ADMITTED_EXACT_SOURCE_CHOICE_STRATA_OR_LABELS"),
        "original_source_rows":rows,
        "original_header_source_13_columns":list(head),
        "source_birdyear_identifiers":len(distinct_dates),
        "source_timestamp_birdyear_pairs":len(groups),
        "source_birdyears_with_3_or_more_distinct_timestamp_keys":repeat3,
        "original_case_labels":dict(sorted(label.items())),
        "original_unrecognized_case_token_shapes":dict(sorted(original_labels_not_binary.items())),
        "source_missing_identity_time_case_counts":dict(sorted(missing.items())),
        "original_timestamp_token_shape_counts":dict(sorted(time_shapes.items())),
        "parseable_recorded_datetime_rows":dt_parseable,
        "source_species_categorical_row_counts":dict(sorted(species.items())),
        "source_season_categorical_row_counts":dict(sorted(season.items())),
        "source_photoperiod_categorical_row_counts":dict(sorted(photoperiod.items())),
        "original_candidate_stratum_size_distribution":dict(sorted(sz.items())),
        "original_used_count_per_stratum_distribution":dict(sorted(use_dist.items())),
        "original_available_count_per_stratum_distribution":dict(sorted(control_dist.items())),
        "exact_one_used_plus_controls_source_strata":valid,
        "incompatible_or_ambiguous_source_strata":incompatible,
        "original_paired_FALSE_aggregate_rows_per_valid_source_key":dict(sorted(candidate_label_counts.items())),
        "original_100_random_destinations_visible_as_separate_records":False,
        "expected_original_source_step_START_coordinate_columns_present":False,
        "original_case_TRUE_interpreted_as_USED":True,
        "original_case_FALSE_interpreted_as_ONE_AGGREGATED_AVAILABLE_HABITAT_ROW":True,
        "original_perennial_bird_ID_independent_of_year_verified":False,
        "original_numeric_habitat_features_opened":False,
        "movement_or_habitat_choice_predictions_computed":False,
        "original_bird_ID_values_or_exact_times_exported":False,
        "independent_prospective_kernel_training_verified":False,
    }


def run()->dict:
    official=None;attempts=[]
    for url in original.ENDPOINTS:
        try:
            official=original.original_item(original.original_json(url))
            break
        except Exception as e:
            attempts.append({"url":url,"error":original.error(e)})
    result={
        "study":"v25-B3-USGS-waterfowl-origin-step-sampled-choice-source-identity",
        "source_item_id":original.SOURCE_ID,
        "source_doi":original.SOURCE_DOI,
        "status":"NOT_ADMITTED_ORIGINAL_PROVIDER_SOURCE_UNAVAILABLE",
        "source_integrity":None,
        "source_stratum_structure":None,
        "attempts":attempts,
        "animal_habitat_coefficients_or_scores_computed":False,
        "all_v13_to_v24_results_unchanged":True,
    }
    if official is None:return result
    file=schema.select_files(official)[SOURCE_FILE]
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)/SOURCE_FILE
        try:
            source_hash=schema.fetch_verified(SOURCE_FILE,file,p)
            if source_hash["original_independent_sha256"]!=SOURCE_SHA256:
                raise ValueError("Original CSV sha256 differs from prior independent pre-outcome source gate")
            structure=source_strata_only(p)
            result.update({
                "source_integrity":source_hash,
                "source_stratum_structure":structure,
                "status":structure["status"]})
        except Exception as e:
            result["status"]="NOT_ADMITTED_ORIGINAL_SOURCE_OR_STRATA_VALIDATION"
            result["source_error"]=type(e).__name__+": "+str(e)[:220]
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v25/results/usgs_step_strata_v25.json"))
    a=p.parse_args()
    out=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V25_B3_STRATA_SOURCE",json.dumps(out,sort_keys=True))
    print("V25_B3_NO_ORIGINAL_HABITAT_NUMERIC_RESPONSE_ANALYZED")
if __name__=="__main__":
    main()
