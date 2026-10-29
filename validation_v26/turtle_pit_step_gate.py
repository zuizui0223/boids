#!/usr/bin/env python3
"""v26-C1 original marine turtle PIT×step×time SOURCE structure only.

No original chlorophyll, depth, protected status, step length/angle or any
model responses. The original CSV has NO case/used/available column, and
the original FGDC download failed provider MD5: do not invent used labels.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import re
import tempfile
from pathlib import Path

import turtle_header_gate as source
import source_manifests as manifest

PINNED_SHA256="eef4d2dd16c97cd0d8722ed1cac8a031cf3dd336404b2e8e4c085cb2fadd4ec0"
EXPECTED_SOURCE_ROWS=420365
EXPECTED_SOURCE_FIELDS=(
    "orgnl_pit","step_id","step_length","log_step_length","turn_angle",
    "cos_turn_angle","start_time","end_time","protected_status",
    "water_depth","chlorophyll")
ID_FIELDS=("orgnl_pit","step_id","start_time","end_time")
DAY_PARSE_FORMATS=(
    "%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M:%S","%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M","%Y-%m-%d"
)
MAX_SOURCE_ROWS=500000

def token_shape(value:str)->str:
    s=str(value).strip()[:44]
    return "".join("D" if c.isdigit() else "A" if c.isalpha() else c for c in s)

def parse_calendar_day(value:str):
    s=str(value).strip()
    if not s:return None
    for fmt in DAY_PARSE_FORMATS:
        try:return dt.datetime.strptime(s,fmt).date()
        except ValueError:continue
    try:return dt.datetime.fromisoformat(s.replace("Z","+00:00")).date()
    except ValueError:return None

def count_distribution(cnt:collections.Counter,max_keys=30)->dict:
    dist=collections.Counter(cnt.values())
    return {str(k):int(v) for k,v in sorted(dist.items())[:max_keys]}

def source_ids_only(path:Path)->dict:
    pit_rows=collections.Counter()
    pit_steps=collections.Counter()
    pit_start_end=collections.Counter()
    source_pit_days=collections.defaultdict(set)
    source_step_shapes=collections.Counter()
    source_start_shapes=collections.Counter()
    source_end_shapes=collections.Counter()
    source_case_tokens=collections.Counter()
    missing=collections.Counter()
    unique_pit_step_fields=collections.Counter()
    date_parsed=0
    rows=0
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as f:
        reader=csv.DictReader(f)
        header=tuple(reader.fieldnames or ())
        if header!=EXPECTED_SOURCE_FIELDS:
            raise ValueError("Original turtle source 11-column header changed")
        for row in reader:
            rows+=1
            if rows>MAX_SOURCE_ROWS:
                raise ValueError("Exceeded original source row count cap")
            v={key:(row.get(key) or "").strip() for key in ID_FIELDS}
            for field,val in v.items():
                if not val or val.upper() in ("NA","NULL","NAN"):
                    missing[field]+=1
            pit,step,start,end=(v[k] for k in ID_FIELDS)
            if not pit or not step or not start or not end:
                continue
            pit_rows[pit]+=1
            pit_steps[(pit,step)]+=1
            pit_start_end[(pit,start,end)]+=1
            unique_pit_step_fields[(pit,step,start,end)]+=1
            source_step_shapes[token_shape(step)]+=1
            source_start_shapes[token_shape(start)]+=1
            source_end_shapes[token_shape(end)]+=1
            if re.search(r"(?:used|avail|random|case)",step,re.I):
                # Do NOT infer which step was biologically chosen from a token
                source_case_tokens["case_like_in_step_id"]+=1
            day1=parse_calendar_day(start)
            day2=parse_calendar_day(end)
            if day1 is not None and day2 is not None:
                date_parsed+=1
                source_pit_days[pit].add(day1)
                source_pit_days[pit].add(day2)
    if rows!=EXPECTED_SOURCE_ROWS:
        raise ValueError("Original turtle source row count changed")
    return {
        "status":"ORIGINAL_TURTLE_PIT_STEP_TIME_GRAIN_SOURCE_ONLY",
        "source_original_rows":rows,
        "source_original_columns":list(header),
        "n_distinct_original_PIT_tokens":len(pit_rows),
        "n_unique_PIT_by_step_id_keys":len(pit_steps),
        "n_unique_PIT_start_end_pair_keys":len(pit_start_end),
        "n_unique_PIT_step_start_end_keys":len(unique_pit_step_fields),
        "source_original_PIT_rows_count_distribution":count_distribution(pit_rows),
        "source_original_PIT_step_id_group_size_distribution":count_distribution(pit_steps),
        "source_original_PIT_start_end_group_size_distribution":count_distribution(pit_start_end),
        "source_original_full_step_key_group_size_distribution":
            count_distribution(unique_pit_step_fields),
        "original_step_id_token_shapes":dict(source_step_shapes.most_common(15)),
        "original_start_time_token_shapes":dict(source_start_shapes.most_common(15)),
        "original_end_time_token_shapes":dict(source_end_shapes.most_common(15)),
        "original_missing_ID_step_time_tokens":dict(missing),
        "rows_with_both_original_calendar_dates_parsed":date_parsed,
        "original_PITs_with_at_least_3_distinct_calendar_dates":
            sum(len(v)>=3 for v in source_pit_days.values()),
        "original_PITs_with_at_least_10_distinct_calendar_dates":
            sum(len(v)>=10 for v in source_pit_days.values()),
        "source_step_id_contains_any_case_like_tokens":
            source_case_tokens.get("case_like_in_step_id",0),
        "original_explicit_used_available_source_column_present":False,
        "original_FGDC_dictionary_source_MD5_verified":False,
        "source_generated_available_step_origin_verified":False,
        "source_used_step_label_identifiable_from_original_author_dictionary":False,
        "source_prequential_choice_model_admitted":False,
        "original_PIT_IDs_or_exact_times_exported":False,
        "original_step_lengths_angles_depth_chlorophyll_or_MPA_values_read":False,
        "no_animal_movement_or_habitat_choice_predictions_scored":True,
    }

def run()->dict:
    meta=manifest.turtle_manifest()
    result={
       "study":"v26-source-turtle-PIT-step-time-no-case-label",
       "source_DOI":manifest.TURTLE_DOI,
       "source_item_id":manifest.TURTLE_ITEM,
       "status":"NOT_ADMITTED_TURTLE_ORIGINAL_SOURCE_UNAVAILABLE",
       "source_original_full_SHA256":None,
       "source_original_ID_time_grain":None,
       "actual_used_available_choice_model_fitted":False,
       "prior_v13_to_v25_frozen_endpoints_unchanged":True,
    }
    try:
        spec=source.exact_file_in_manifest(meta)
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/source.SOURCE_NAME
            integrity=source.original_download(spec,path)
            if integrity["independently_computed_sha256"]!=PINNED_SHA256:
                raise ValueError("Frozen original turtle source SHA256 changed")
            profile=source_ids_only(path)
        result.update({
          "status":"SOURCE_TURTLE_GRAIN_VERIFIED_CHOICE_NOT_ADMITTED_NO_VERIFIED_LABEL",
          "source_original_full_SHA256":integrity["independently_computed_sha256"],
          "source_original_ID_time_grain":profile,
        })
    except Exception as e:
        result["status"]="NOT_ADMITTED_ORIGINAL_TURTLE_ID_TIME_STRUCTURE"
        result["source_error"]=type(e).__name__+": "+str(e)[:160]
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
       "validation_v26/results/turtle_pit_step_time_v26.json"))
    a=p.parse_args()
    r=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V26_TURTLE_PIT_STEP_GRAIN",json.dumps(r,sort_keys=True))
    print("V26_NO_USED_AVAILABLE_TURTLE_ECOLOGY_MODEL_FITTED")
if __name__=="__main__":
    main()
