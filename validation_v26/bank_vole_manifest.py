#!/usr/bin/env python3
"""v26-D original 2023 bank vole Zenodo case-control manifest ONLY.

No source animal tracking, step cases, habitat values or social contact data.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import source_manifests as common

RECORD=10101651
DOI="10.5281/zenodo.10101651"
API=f"https://zenodo.org/api/records/{RECORD}"

def run()->dict:
    doc={
        "study":"v26-original-bank-vole-simultaneous-interaction-step-selection-source",
        "expected_record":RECORD,
        "expected_DOI":DOI,
        "status":"NOT_ADMITTED_ORIGINAL_ZENODO_METADATA_UNAVAILABLE",
        "metadata":None,
        "source_step_or_social_outcome_opened":False,
        "previous_v13_v25_endpoints_unchanged":True,
    }
    try:
        original=common.read_original_json(API)
        if int(original.get("id",-1))!=RECORD:
            raise ValueError("Original bank vole Zenodo ID wrong")
        files=common.safe_original_files_zenodo(original)
        md=original.get("metadata") or {}
        info=common.classify_aggregate(files)
        doc.update({
            "status":"ORIGINAL_BANK_VOLE_SOURCE_MANIFEST_ONLY",
            "metadata":{
                "published_doi":original.get("doi"),
                "published_title":md.get("title"),
                "original_license":md.get("license"),
                "original_file_list":files,
                "files_size_gate":info,
                "provider_created":original.get("created"),
                "source_is_original_field_case_control_not_new_independent_GPS_study":True,
            },
        })
    except Exception as e:
        doc["source_error"]=type(e).__name__+": "+str(e)[:170]
    return doc

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
      "validation_v26/results/bank_vole_original_manifest_v26.json"))
    args=p.parse_args()
    doc=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(doc,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V26_BANK_VOLE_ORIGINAL_SOURCE",json.dumps(doc,sort_keys=True))
    print("V26_NO_VOLe_HABITAT_OR_SOCIAL_EFFECT_FITTED")
if __name__=="__main__":
    main()
