#!/usr/bin/env python3
"""v28-A independent original Zenodo ungulate GPS vs camera station source bytes.

Download official Zenodo original 2023 RSF and IDM source CSV plus author
scripts, require original MD5, compute SHA256, inspect CSV *HEADERS ONLY*.
Never inspect animal IDs, animal GPS fixes, available-point labels,
environmental values, camera detections, model coefficients or outcomes.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path

import source_manifests as zenodo

RECORD=7766936
DOI="10.5281/zenodo.7766936"
URL="https://zenodo.org/api/records/"+str(RECORD)
SOURCE_TARGETS=(
    "RSFapproach_data.csv","IDMapproach_data.csv",
    "RSFapproach_code.R","IDMapproach_code.R"
)
MAX_FILE=50_000_000
MAX_TOTAL=100_000_000
UA="boids-v28-original-Doñana-ungulate-GPS-camera-source-only/1.0"
MAX_HEADER=100000


def published_source():
    d=zenodo.read_original_json(URL)
    if int(d.get("id",-1))!=RECORD:
        raise ValueError("Official Zenodo record mismatch")
    files=zenodo.safe_original_files_zenodo(d)
    meta=d.get("metadata") or {}
    return {
        "source_DOI":d.get("doi"),
        "source_license":meta.get("license"),
        "source_title":meta.get("title"),
        "original_published_files":files,
        "original_source_file_size_class":zenodo.classify_aggregate(files),
        "original_source_record_ID":RECORD,
    }

def require_file(metadata,name):
    candidates=[f for f in metadata["original_published_files"]
                if f["original_filename"]==name]
    if len(candidates)!=1:raise ValueError("Missing or duplicated original source file")
    f=candidates[0]
    size=f.get("provider_bytes")
    checksum=str(f.get("provider_MD5_or_checksum") or "").lower()
    url=f.get("content_url")
    if not isinstance(size,int) or size<=0 or size>MAX_FILE:
        raise ValueError("Original provider file size unsupported")
    if not checksum.startswith("md5:") or len(checksum)!=36:
        raise ValueError("Original Zenodo source MD5 missing")
    if not isinstance(url,str) or not url.startswith("https://zenodo.org/"):
        raise ValueError("Original source not from published Zenodo host")
    return {"name":name,"size":size,"md5":checksum[4:],"url":url}

def original_file_digest(spec,path):
    md=hashlib.md5();sh=hashlib.sha256();total=0
    req=urllib.request.Request(spec["url"],headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=95) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("Untrusted original file redirect")
        with path.open("wb") as dest:
            for chunk in iter(lambda:response.read(256*1024),b""):
                total+=len(chunk)
                if total>MAX_FILE:raise ValueError("Original file cap exceeded")
                md.update(chunk);sh.update(chunk);dest.write(chunk)
    if total!=spec["size"] or md.hexdigest()!=spec["md5"]:
        raise ValueError("Original Zenodo source byte count or provider MD5 mismatch")
    return {
        "status":"ORIGINAL_ZENODO_SOURCE_FULL_BYTES_AND_MD5_VERIFIED",
        "source_file":spec["name"],
        "source_bytes":total,"original_MD5":md.hexdigest(),
        "independently_computed_SHA256":sh.hexdigest(),
        "original_animal_or_environment_response_opened":False,
    }

def only_csv_header(path):
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as raw:
        line=raw.readline(MAX_HEADER+1)
        if len(line)>MAX_HEADER or not line:raise ValueError("Missing source CSV header")
        fields=next(csv.reader([line]))
        if len(fields)>120 or len(fields)!=len(set(fields)):
            raise ValueError("Invalid original CSV schema")
        physical_lines=sum(1 for _ in raw)
    return {
        "status":"SOURCE_COLUMN_NAMES_AND_PHYSICAL_LINE_COUNT_ONLY",
        "original_column_names":fields,
        "source_header_count":len(fields),
        "physical_data_lines_after_header":physical_lines,
        "original_GPS_or_available_habitat_numerics_read":False,
        "original_camera_trap_detections_read":False,
        "original_individual_animal_IDs_read":False,
    }

def run():
    out={
        "study":"v28-independent-2023-Doñana-17-GPS-ungulates-60-camera-stations",
        "source_DOI":DOI,
        "source_status":"NOT_ADMITTED_ORIGINAL_ZENODO_RECORD_UNAVAILABLE",
        "official_source":None,
        "source_file_integrity":{},
        "original_file_headers":{},
        "no_biological_habitat_choice_or_detection_model_fitted":True,
        "previous_v13_to_v27_empirical_results_unchanged":True,
    }
    try:meta=published_source()
    except Exception as e:
        out["source_error"]=type(e).__name__+": "+str(e)[:180]
        return out
    out["official_source"]=meta
    if meta["source_DOI"]!=DOI:
        out["source_status"]="NOT_ADMITTED_SOURCE_DOI_CHANGED"
        return out
    try:
        selected=[require_file(meta,name) for name in SOURCE_TARGETS]
        if sum(x["size"] for x in selected)>MAX_TOTAL:
            raise ValueError("Original source total cap exceeded")
    except Exception as e:
        out["source_status"]="NOT_ADMITTED_SOURCE_SIZE_OR_FILE_IDENTITY"
        out["source_error"]=type(e).__name__+": "+str(e)[:160]
        return out
    with tempfile.TemporaryDirectory() as folder:
        for f in selected:
            path=Path(folder)/f["name"]
            try:
                digest=original_file_digest(f,path)
                out["source_file_integrity"][f["name"]]=digest
                if f["name"].endswith(".csv"):
                    out["original_file_headers"][f["name"]]=only_csv_header(path)
            except Exception as e:
                out["source_file_integrity"][f["name"]]={
                    "status":"NOT_ADMITTED_SOURCE_BYTES_OR_SCHEMA",
                    "error":type(e).__name__+": "+str(e)[:140]}
    if all(x.get("status")=="ORIGINAL_ZENODO_SOURCE_FULL_BYTES_AND_MD5_VERIFIED"
           for x in out["source_file_integrity"].values()) and len(out["original_file_headers"])==2:
        out["source_status"]="ORIGINAL_UNGULATE_GPS_AND_CAMERA_DATA_SOURCE_BYTES_AND_HEADER_VERIFIED"
    else:
        out["source_status"]="NOT_ADMITTED_INCOMPLETE_ORIGINAL_SOURCE_BYTES"
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
       "validation_v28/results/ungulate_GPS_camera_Zenodo_source_v28.json"))
    args=p.parse_args()
    data=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V28_ORIGINAL_SOURCE_RECEIPT",json.dumps(data,sort_keys=True))
    print("V28_NO_UNGULATE_CAMERA_OR_GPS_ECOLOGICAL_EFFECT_FITTED")
if __name__=="__main__":
    main()
