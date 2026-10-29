#!/usr/bin/env python3
"""v26-B1 USGS marine turtle original CSV exact MD5 + header only.

Only column names and physical line count; never inspect source animal IDs,
step start/end timestamps, used/available labels, distance/turn, marine
protected habitat, chlorophyll, depth or original GPS coordinates.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path

import source_manifests as manifest

SOURCE_NAME="Hart et al_iSSA.csv"
SOURCE_BYTES=45_669_515
ORIGINAL_MD5="5c5f25398720a663ae332097b49bf740"
ORIGINAL_ITEM=manifest.TURTLE_ITEM
MAX_BYTES=80_000_000
UA="boids-v26-original-turtle-2020-MD5-header-only/1.0"

def exact_file_in_manifest(metadata:dict)->dict:
    if metadata["status"]!="ORIGINAL_USGS_TURTLE_MANIFEST_ACQUIRED_NO_STEP_OUTCOMES":
        raise ValueError("USGS turtle original manifest not verified")
    data=metadata.get("original_source_metadata") or {}
    matches=[f for f in data.get("files",[]) if f.get("original_filename")==SOURCE_NAME]
    if len(matches)!=1:
        raise ValueError("Original USGS turtle CSV absent or duplicated")
    f=matches[0]
    check=f.get("provider_MD5_or_checksum") or {}
    if f["provider_bytes"]!=SOURCE_BYTES or (
        str(check.get("type") or "").lower()!="md5" or
        str(check.get("value") or "").lower()!=ORIGINAL_MD5
    ):
        raise ValueError("Original turtle CSV size/MD5 changed")
    uri=f.get("download_provider_uri")
    if not isinstance(uri,str) or not uri.startswith(
      "https://www.sciencebase.gov/catalog/file/get/"+ORIGINAL_ITEM):
        raise ValueError("Original turtle CSV not from registered ScienceBase file source")
    return {"source_filename":SOURCE_NAME,
            "registered_published_bytes":SOURCE_BYTES,
            "registered_published_md5":ORIGINAL_MD5,
            "official_original_uri":uri}

def original_download(spec:dict,path:Path)->dict:
    req=urllib.request.Request(spec["official_original_uri"],headers={"User-Agent":UA})
    sha=hashlib.sha256()
    md5=hashlib.md5()
    n=0
    with urllib.request.urlopen(req,timeout=140) as stream:
        if not stream.geturl().startswith("https://"):
            raise ValueError("Insecure original data source redirect")
        header=stream.headers.get("Content-Length")
        if header and int(header)!=SOURCE_BYTES:
            raise ValueError("Source response length differs from pre-frozen metadata")
        with path.open("wb") as dest:
            for chunk in iter(lambda:stream.read(1024*1024),b""):
                n+=len(chunk)
                if n>MAX_BYTES:
                    raise ValueError("Original file exceeded bounded download")
                dest.write(chunk)
                sha.update(chunk)
                md5.update(chunk)
    if n!=SOURCE_BYTES or md5.hexdigest()!=ORIGINAL_MD5:
        raise ValueError("Original marine turtle provider MD5 or byte count mismatch")
    return {
        "status":"ORIGINAL_TURTLE_SOURCE_BYTES_MD5_SHA256_VERIFIED",
        "source_name":SOURCE_NAME,"exact_source_bytes":n,
        "published_md5_matched":True,
        "original_md5":md5.hexdigest(),
        "independently_computed_sha256":sha.hexdigest(),
        "downloaded_from_official_provider":True,
        "animal_PIT_ID_step_outcomes_or_environment_values_opened":False,
    }

def inspect_csv_header_only(path:Path)->dict:
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as f:
        first=f.readline(200_001)
        if not first or len(first)>200_000:
            raise ValueError("Original header absent or unusually long")
        names=next(csv.reader([first]))
        if len(names)>250 or len(names)!=len(set(names)) or not names:
            raise ValueError("Original duplicate/oversized field names")
        physical_lines=sum(1 for _ in f)
    return {
        "status":"ORIGINAL_TURTLE_COLUMN_NAMES_AND_PHYSICAL_LINE_COUNT_ONLY",
        "source_header_names":names,
        "n_original_columns":len(names),
        "physical_lines_after_header":physical_lines,
        "source_PIT_IDs_or_timestamps_read":False,
        "source_step_case_labels_or_group_counts_read":False,
        "source_environmental_numeric_values_read":False,
        "animal_habitat_scores_or_model_fit_computed":False,
    }

def run()->dict:
    source=manifest.turtle_manifest()
    result={
        "study":"v26B1-independent-USGS-marine-turtle-source-header",
        "source_DOI":manifest.TURTLE_DOI,
        "source_item_id":manifest.TURTLE_ITEM,
        "source_name":SOURCE_NAME,
        "source_manifest_status":source["status"],
        "source_status":"NOT_ADMITTED_ORIGINAL_SOURCE_UNAVAILABLE",
        "original_file_hashes":None,
        "header_and_physical_size":None,
        "original_telemetry_or_environment_values_used":False,
        "all_prior_v13_to_v25_results_unchanged":True,
    }
    try:
        spec=exact_file_in_manifest(source)
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/SOURCE_NAME
            integrity=original_download(spec,path)
            print("V26_ORIGINAL_TURTLE_FULL_MD5_SHA256",json.dumps(integrity,sort_keys=True),flush=True)
            result["original_file_hashes"]=integrity
            header=inspect_csv_header_only(path)
            result["header_and_physical_size"]=header
            result["source_status"]="ORIGINAL_USGS_TURTLE_HEADER_ONLY_VERIFIED"
    except Exception as e:
        result["source_status"]="NOT_ADMITTED_ORIGINAL_TURTLE_BYTES_OR_HEADER"
        result["source_failure"]=type(e).__name__+": "+str(e)[:210]
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
       "validation_v26/results/turtle_original_header_v26.json"))
    a=p.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V26_TURTLE_B1_SOURCE",json.dumps(d,sort_keys=True))
    print("V26_TURTLE_NO_BIOLOGICAL_FORECAST")
if __name__=="__main__":
    main()
