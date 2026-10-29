#!/usr/bin/env python3
"""v26-A source-only original USGS turtle and Zenodo 48-species mammal manifests.

NO raw animal trajectories, matched step labels, habitat numerical values or
new predictive gains. The output is official source bytes/MD5 *metadata* and
file-size admission status only (provider hashes not independently computed).
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TURTLE_ITEM="5faab074d34eb413d5df1f41"
TURTLE_DOI="10.5066/P9UZU4GG"
MAMMAL_RECORD=15756163
MAMMAL_DOI="10.5281/zenodo.15756163"
TURTLE_API="https://www.sciencebase.gov/catalog/item/"+TURTLE_ITEM+"?format=json"
MAMMAL_API="https://zenodo.org/api/records/"+str(MAMMAL_RECORD)
CAP_METADATA_BYTES=8_000_000
CAP_ONE_DATA_FILE=250_000_000
CAP_ALL_DATA_FILES=400_000_000
UA="boids-v26-original-turtle-mammal-source-only-metadata/1.0"
TURTLE_ALTERNATE_URLS=(
    TURTLE_API,
    "https://www.sciencebase.gov/catalog/item/"+TURTLE_ITEM,
    "https://api.sciencebase.gov/catalog/item/"+TURTLE_ITEM
)
ALLOWED_HOSTS={"www.sciencebase.gov","api.sciencebase.gov","sciencebase.gov","zenodo.org"}

def read_original_json(url:str)->dict:
    if urllib.parse.urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("Untrusted original source metadata host")
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=42) as stream:
        final=urllib.parse.urlparse(stream.geturl())
        if final.scheme!="https" or final.hostname not in ALLOWED_HOSTS:
            raise ValueError("Redirect outside original source provider")
        raw=stream.read(CAP_METADATA_BYTES+1)
    if len(raw)>CAP_METADATA_BYTES:
        raise ValueError("Original source provider metadata too large")
    doc=json.loads(raw)
    if not isinstance(doc,dict):
        raise ValueError("Source provider did not return an object")
    return doc

def error_summary(e:Exception)->str:
    if isinstance(e,urllib.error.HTTPError):
        return "HTTP_"+str(e.code)
    if isinstance(e,urllib.error.URLError):
        return "NETWORK_"+type(e.reason).__name__
    return type(e).__name__+": "+str(e)[:140]

def safe_original_files_usgs(obj:dict)->list[dict]:
    seen=set()
    arr=[]
    for f in obj.get("files") or []:
        if not isinstance(f,dict):continue
        name=f.get("name")
        if not isinstance(name,str) or not name:continue
        if name in seen:raise ValueError("Duplicate original provider filename")
        seen.add(name)
        ch=f.get("checksum") or {}
        arr.append({
            "original_filename":name,
            "provider_bytes":f.get("size"),
            "content_type":f.get("contentType"),
            "provider_MD5_or_checksum":ch,
            "download_provider_uri":f.get("downloadUri") or f.get("url"),
            "file_field_keys":sorted(f.keys()),
        })
    return arr

def safe_original_files_zenodo(obj:dict)->list[dict]:
    files=obj.get("files") or []
    if isinstance(files,dict):
        files=list((files.get("entries") or {}).values())
    if not isinstance(files,list):
        raise ValueError("Unexpected Zenodo file list")
    seen=set()
    out=[]
    for f in files:
        if not isinstance(f,dict):continue
        name=f.get("key") or f.get("filename")
        if not isinstance(name,str) or not name:continue
        if name in seen:raise ValueError("Duplicate published Zenodo filename")
        seen.add(name)
        links=f.get("links") or {}
        out.append({
            "original_filename":name,
            "provider_bytes":f.get("size"),
            "provider_MD5_or_checksum":f.get("checksum"),
            "content_url":links.get("content") or links.get("self"),
            "file_field_keys":sorted(f.keys()),
        })
    return out

def classify_aggregate(files:list[dict])->dict:
    potential=[f for f in files
      if str(f["original_filename"]).lower().endswith(
         (".csv",".txt",".zip",".rds",".rdata",".gpkg",".parquet",".feather",".xlsx",".gz",".7z",".dbf"))]
    known=[f for f in potential if isinstance(f["provider_bytes"],int) and
           f["provider_bytes"]>0]
    sizes=[f["provider_bytes"] for f in known]
    eligible=[f for f in known if f["provider_bytes"]<=CAP_ONE_DATA_FILE]
    return {
        "source_original_attachment_count":len(files),
        "structured_original_file_candidate_count":len(potential),
        "source_candidate_declared_positive_bytes_count":len(known),
        "aggregate_candidate_structured_bytes_if_all_complete":sum(sizes),
        "source_files_above_predeclared_250MB":[
            f["original_filename"] for f in known if f["provider_bytes"]>CAP_ONE_DATA_FILE],
        "bounded_candidate_original_files":[
            f["original_filename"] for f in eligible],
        "aggregate_size_allowed_if_all_bounded":sum(
            f["provider_bytes"] for f in eligible)<=CAP_ALL_DATA_FILES,
        "no_original_animal_or_environmental_rows_accessed":True,
    }

def turtle_manifest()->dict:
    result={
        "source_name":"USGS-2020-original-marine-turtle-step-selection",
        "expected_DOI":TURTLE_DOI,
        "original_item_id":TURTLE_ITEM,
        "status":"NOT_ADMITTED_ORIGINAL_USGS_METADATA_UNAVAILABLE",
        "original_source_metadata":None,
        "attempts":[],
    }
    obj=None
    for url in TURTLE_ALTERNATE_URLS:
        try:
            obj=read_original_json(url)
            if str(obj.get("id"))!=TURTLE_ITEM:
                raise ValueError("Original USGS item ID changed")
            if "turtle" not in str(obj.get("title") or "").lower():
                raise ValueError("Unexpected original turtle source title")
            identifiers=json.dumps(obj.get("identifiers") or []).lower()
            if "10.5066/" in identifiers and TURTLE_DOI.lower() not in identifiers:
                raise ValueError("USGS original item DOI mismatched")
            result["attempts"].append({"url":url,"status":"SOURCE_METADATA_ID_VERIFIED"})
            break
        except Exception as e:
            result["attempts"].append({"url":url,"status":error_summary(e)})
            obj=None
    if obj is None:return result
    files=safe_original_files_usgs(obj)
    result["original_source_metadata"]={
        "title":obj.get("title"),
        "published_identifiers":obj.get("identifiers"),
        "license":obj.get("rights") or obj.get("license"),
        "published_dates":obj.get("dates"),
        "files":files,
        "source_file_sizing":classify_aggregate(files),
        "original_metadata_field_names":sorted(obj.keys()),
        "has_children":obj.get("hasChildren"),
    }
    result["status"]=("ORIGINAL_USGS_TURTLE_MANIFEST_ACQUIRED_NO_STEP_OUTCOMES"
                      if files else "NOT_ADMITTED_PARENT_NO_ORIGINAL_FILES")
    return result

def mammal_manifest()->dict:
    result={
        "source_name":"Zenodo-2026-48-terrestrial-mammal-species-1344-tracks",
        "expected_DOI":MAMMAL_DOI,
        "original_record_id":MAMMAL_RECORD,
        "status":"NOT_ADMITTED_ORIGINAL_ZENODO_METADATA_UNAVAILABLE",
        "original_source_metadata":None,
        "attempts":[],
    }
    try:
        doc=read_original_json(MAMMAL_API)
        if int(doc.get("id",-1))!=MAMMAL_RECORD:
            raise ValueError("Zenodo original record differs")
        files=safe_original_files_zenodo(doc)
        md=doc.get("metadata") or {}
        result["original_source_metadata"]={
            "title":md.get("title"),
            "license":md.get("license"),
            "published_doi":doc.get("doi"),
            "published_date":doc.get("created"),
            "files":files,
            "source_file_sizing":classify_aggregate(files),
            "record_field_names":sorted(doc.keys()),
        }
        result["status"]="ORIGINAL_ZENODO_MAMMAL_MANIFEST_ACQUIRED_NO_STEP_OUTCOMES"
    except Exception as e:
        result["attempts"].append({"url":MAMMAL_API,"status":error_summary(e)})
    return result

def run()->dict:
    t=turtle_manifest()
    m=mammal_manifest()
    return {
        "study":"v26-original-independent-turtle-and-global-mammal-source-discovery",
        "pinned_source_contract":"docs/V26_INDEPENDENT_TURTLE_AND_MAMMAL_SOURCE_CONTRACT.md",
        "turtle":t,
        "mammal":m,
        "source_movement_model_fit_attempted":False,
        "original_GPS_coordinates_step_cases_and_habitat_values_read":False,
        "new_biological_predictive_effect_reported":False,
        "v13_to_v25_previous_results_untouched":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
       "validation_v26/results/source_manifests_v26.json"))
    a=p.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V26_TURTLE_SOURCE",json.dumps(d["turtle"],sort_keys=True))
    print("V26_MAMMAL_SOURCE",json.dumps(d["mammal"],sort_keys=True))
    print("V26_NO_ANIMAL_OR_HABITAT_PREDICTIONS_FITTED")

if __name__=="__main__":
    main()
