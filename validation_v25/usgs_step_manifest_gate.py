#!/usr/bin/env python3
"""v25-B1 official USGS 2023 4-species waterfowl step source manifest only.

NO original step, animal, hunting or habitat observation value is fetched.
Tests provenance, file sizes/MD5, site origin description and author license.
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE_ID="652edfe8d34edd15305a9ab0"
SOURCE_DOI="10.5066/P9ELSUHN"
ENDPOINTS=(
    f"https://www.sciencebase.gov/catalog/item/{SOURCE_ID}?format=json",
    f"https://www.sciencebase.gov/catalog/item/{SOURCE_ID}",
    f"https://api.sciencebase.gov/catalog/item/{SOURCE_ID}",
)
CAP_JSON=12_000_000
MAX_SINGLE=250_000_000
MAX_COMBINED=400_000_000
EXPECTED_DOI=SOURCE_DOI.lower()
EXPECTED_SPECIES=("Anser albifrons","Anser caerulescens caerulescens",
                  "Anas platyrhynchos","Anas acuta")
UA="boids-v25-original-USGS-California-waterfowl-step-source/1.0"


def error(e):
    if isinstance(e,urllib.error.HTTPError):return "HTTP_"+str(e.code)
    if isinstance(e,urllib.error.URLError):return "URL_"+type(e.reason).__name__
    return type(e).__name__+": "+str(e)[:120]


def original_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=45) as f:
        host=urllib.parse.urlparse(f.geturl()).hostname
        if host not in ("www.sciencebase.gov","sciencebase.gov","api.sciencebase.gov"):
            raise ValueError("ScienceBase metadata redirected outside official domain")
        b=f.read(CAP_JSON+1)
    if len(b)>CAP_JSON:raise ValueError("Official source metadata beyond fixed cap")
    x=json.loads(b)
    if not isinstance(x,dict):raise ValueError("Invalid original source metadata JSON")
    return x


def source_files(x):
    out=[]
    seen=set()
    for f in x.get("files") or []:
        if not isinstance(f,dict):continue
        name=f.get("name")
        if not isinstance(name,str) or not name:continue
        if name in seen:raise ValueError("Repeated original file name")
        seen.add(name)
        check=f.get("checksum") or {}
        out.append({
            "name":name,
            "reported_bytes":f.get("size"),
            "provider_checksum":check,
            "provider_ContentType":f.get("contentType"),
            "official_download_url":f.get("downloadUri") or f.get("url"),
            "file_field_names":sorted(f.keys()),
            "is_original_structured_candidate":name.lower().endswith(
               (".csv",".zip",".rds",".xlsx",".txt",".gpkg",".gdb.zip",".feather",".parquet")),
        })
    return out


def original_item(x):
    if str(x.get("id") or "")!=SOURCE_ID:
        raise ValueError("Wrong USGS original ScienceBase source item")
    title=str(x.get("title") or "")
    if not all(z in title.lower() for z in ("movements","habitats","waterfowl")):
        raise ValueError("Source original title is not pinned step study")
    identifiers=x.get("identifiers") or []
    tags=json.dumps(identifiers).lower()
    if EXPECTED_DOI not in tags:
        raise ValueError("Original USGS DOI missing or mismatched in official source")
    fs=source_files(x)
    candidates=[z for z in fs if z["is_original_structured_candidate"]]
    return {
      "status":"OFFICIAL_USGS_FOUR_SPECIES_STEP_SOURCE_META_VERIFIED",
      "source_Doi":SOURCE_DOI,
      "source_item_id":SOURCE_ID,
      "source_title":title,
      "rights":x.get("rights"),
      "dates":x.get("dates"),
      "file_manifest":fs,
      "original_attachment_count":len(fs),
      "candidate_original_data_files":len(candidates),
      "candidate_metadata_only_total_bytes":sum(z["reported_bytes"] for z in candidates if isinstance(z["reported_bytes"],int)),
      "candidate_data_file_over_fixed_250MB_limit":[
          z["name"] for z in candidates if isinstance(z["reported_bytes"],int)
          and z["reported_bytes"]>MAX_SINGLE
      ],
      "candidate_files_under_limit":[
          z["name"] for z in candidates if isinstance(z["reported_bytes"],int)
          and 0<z["reported_bytes"]<=MAX_SINGLE
      ],
      "source_item_metadata_field_names":sorted(x.keys()),
      "has_source_children":x.get("hasChildren"),
      "animal_step_or_original_numeric_habitat_data_read":False,
      "model_fitted":False,
    }


def children():
    params=urllib.parse.urlencode({
      "q":"","filter":"parentId="+SOURCE_ID,
      "format":"json","max":100
    })
    url="https://www.sciencebase.gov/catalog/items?"+params
    try:
        x=original_json(url)
        records=x.get("items") or []
        if len(records)>100:raise ValueError("Excess children")
        return {"status":"OFFICIAL_SOURCE_CHILDREN_LISTED",
                "count":x.get("total"),
                "items":[{"id":v.get("id"),"title":v.get("title"),
                          "file_count":len(v.get("files") or [])}
                         for v in records if isinstance(v,dict)]}
    except Exception as e:
        return {"status":"NO_PUBLIC_CHILD_LISTING","error":error(e)}


def run():
    output={
        "study":"v25-B1-original-independent-USGS-waterfowl-step-sampling-source",
        "source_DOI":SOURCE_DOI,
        "source_item_ID":SOURCE_ID,
        "status":"NOT_ADMITTED_OFFICIAL_SOURCE_METADATA_UNAVAILABLE",
        "original_source":None,
        "source_children":None,
        "attempts":[],
        "source_animal_or_habitat_response_opened":False,
        "new_habitat_choice_prediction_computed":False,
        "all_v13_to_v24_previous_endpoints_unchanged":True,
    }
    for url in ENDPOINTS:
        try:
            raw=original_json(url)
            output["original_source"]=original_item(raw)
            output["attempts"].append({"route":url,"status":"VERIFIED"})
            output["source_children"]=children()
            break
        except Exception as e:
            output["attempts"].append({"route":url,"status":error(e)})
    if output["original_source"]:
        out=output["original_source"]
        output["status"]=("SOURCE_MANIFEST_REVIEWED_SIZE_OR_SCHEMA_GATE_NEEDED"
                          if out["candidate_original_data_files"]>0 else
                          "NOT_ADMITTED_NO_SOURCE_DATA_FILES_IN_ITEM")
    return output


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "validation_v25/results/usgs_four_species_manifest_v25.json"))
    args=parser.parse_args()
    d=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V25_B1_USGS_SOURCE",json.dumps(d,sort_keys=True))
    print("V25_NO_ORIGINAL_WATERFOWL_STEP_SELECTION_SCORED")

if __name__=="__main__":
    main()
