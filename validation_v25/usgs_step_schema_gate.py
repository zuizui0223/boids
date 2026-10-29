#!/usr/bin/env python3
"""v25-B2: original USGS four-waterfowl-step full MD5+SHA256 and columns.

Read ONLY original CSV column names and physical line count, and FGDC
attribute names/definitions. Never extract observed habitat/animal choice
numeric values, used/available labels, individual GPS locations or steps.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import usgs_step_manifest_gate as original

PINNED={
  "Data Release P9ELSUHN.csv":(27997528,"78eb6064eca992225d6907d6e46f5bef"),
  "Data Release P9ELSUHN.xml":(26316,"170cf76948ef8604ae41f268bc3bf4f0"),
}
MAX_SINGLE=80_000_000
MAX_LINE=200_000
USER_AGENT="boids-v25-USGS-source-original-step-schema-only/1.0"


def select_files(official:dict)->dict:
    if official["source_item_id"]!=original.SOURCE_ID:
        raise ValueError("Official source item changed")
    fs={x["name"]:x for x in official["file_manifest"]}
    if not set(PINNED).issubset(fs):
        raise ValueError("Missing original source CSV or XML")
    result={}
    for name,(n,md5) in PINNED.items():
        f=fs[name]
        if f["reported_bytes"]!=n:
            raise ValueError("Official file length no longer matches metadata pin")
        check=f.get("provider_checksum") or {}
        if str(check.get("type") or "").lower()!="md5" or str(check.get("value") or "").lower()!=md5:
            raise ValueError("Official original file MD5 mismatch")
        uri=f.get("official_download_url")
        if not isinstance(uri,str) or not uri.startswith(
            "https://www.sciencebase.gov/catalog/file/get/"+original.SOURCE_ID):
            raise ValueError("Unexpected official USGS download origin")
        result[name]={"size":n,"md5":md5,"download_url":uri}
    return result


def fetch_verified(name:str,source:dict,to:Path)->dict:
    req=urllib.request.Request(source["download_url"],
                               headers={"User-Agent":USER_AGENT})
    sh=hashlib.sha256();md=hashlib.md5();total=0
    with urllib.request.urlopen(req,timeout=110) as stream:
        if not stream.geturl().startswith("https://"):
            raise ValueError("Original source redirected insecurely")
        header=stream.headers.get("Content-Length")
        if header and int(header)!=source["size"]:
            raise ValueError("Unexpected original source byte count in HTTP")
        with to.open("wb") as file:
            while True:
                block=stream.read(512*1024)
                if not block:break
                total+=len(block)
                if total>MAX_SINGLE:raise ValueError("Original file too large")
                sh.update(block);md.update(block);file.write(block)
    if total!=source["size"] or md.hexdigest()!=source["md5"]:
        raise ValueError("Original source checksum or file size changed")
    return {"file":name,"bytes":total,
            "status":"ORIGINAL_PROVIDER_MD5_AND_BYTES_VERIFIED",
            "provider_md5":md.hexdigest(),
            "original_independent_sha256":sh.hexdigest(),
            "source_file_url":source["download_url"],
            "original_GPS_or_choice_outcomes_read":False}


def csv_schema_only(path:Path)->dict:
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as raw:
        line=raw.readline(MAX_LINE+1)
        if len(line)>MAX_LINE:raise ValueError("Original header too large")
        fields=next(csv.reader([line]))
        if not fields or len(fields)!=len(set(fields)):
            raise ValueError("Empty or repeated original column headings")
        # count physical lines without decoding/inspecting ANY values.
        physical_lines=sum(1 for _ in raw)
    return {
      "status":"ORIGINAL_CSV_HEADER_AND_FILE_LINE_COUNT_ONLY",
      "original_column_names":fields,
      "n_original_column_names":len(fields),
      "original_physical_lines_after_header":physical_lines,
      "categorical_values_or_step_IDs_opened":False,
      "GPS_start_end_coordinates_or_choice_numeric_values_read":False,
      "source_choice_stratum_units_still_unverified":True,
    }


def fgdc_schema_only(path:Path)->dict:
    root=ET.parse(path).getroot()
    raw=[]
    for elem in root.findall(".//attr"):
        label=elem.findtext("attrlabl")
        definition=elem.findtext("attrdef")
        if label:
            raw.append({"field":label.strip()[:160],
                        "definition":(definition or "").strip()[:460]})
    return {
      "status":"OFFICIAL_FGDC_SOURCE_FIELD_DICTIONARY_ONLY",
      "number_of_documented_source_fields":len(raw),
      "source_field_definitions":raw[:180],
      "original_movement_or_landcover_values_opened":False,
    }


def run()->dict:
    original_item=None;failed=[]
    for url in original.ENDPOINTS:
        try:
            original_item=original.original_item(original.original_json(url))
            break
        except Exception as e:
            failed.append({"url":url,"failure":original.error(e)})
    out={
      "study":"v25-B2-independent-2023-original-USGS-waterfowl-step-source-schema",
      "source_DOI":original.SOURCE_DOI,
      "source_item_ID":original.SOURCE_ID,
      "status":"NOT_ADMITTED_OFFICIAL_ORIGINAL_FILES_UNAVAILABLE",
      "full_file_hashes":{},
      "source_structures":{},
      "manifest_errors":failed,
      "original_step_choice_effect_scores_computed":False,
      "previous_v13_to_v24_endpoints_untouched":True,
    }
    if original_item is None:return out
    try: files=select_files(original_item)
    except Exception as e:
        out["status"]="NOT_ADMITTED_ORIGINAL_PROVIDER_FILE_METADATA_CHANGED"
        out["manifest_errors"].append({"stage":"source_files","failure":str(e)[:160]})
        return out
    with tempfile.TemporaryDirectory() as temp:
        for name,c in files.items():
            path=Path(temp)/name
            try:
                h=fetch_verified(name,c,path)
                out["full_file_hashes"][name]=h
                if name.endswith(".csv"):
                    out["source_structures"][name]=csv_schema_only(path)
                else:
                    out["source_structures"][name]=fgdc_schema_only(path)
            except Exception as e:
                out["full_file_hashes"][name]={
                  "status":"NOT_ADMITTED_SOURCE_BINARY_OR_SCHEMA",
                  "reason":type(e).__name__+": "+str(e)[:160]}
    if (len(out["source_structures"])==len(PINNED)
        and all(x.get("status")=="ORIGINAL_PROVIDER_MD5_AND_BYTES_VERIFIED"
                for x in out["full_file_hashes"].values())):
        out["status"]="ORIGINAL_SOURCE_FULL_HASH_AND_SCHEMA_VERIFIED_NO_CHOICE_SCORES"
    else:
        out["status"]="NOT_ADMITTED_SOURCE_BINARY_OR_HEADER_UNVERIFIED"
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
         "validation_v25/results/usgs_four_species_schema_v25.json"))
    args=p.parse_args()
    d=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V25_B2_ORIGINAL_FILE_HASHES",json.dumps(d["full_file_hashes"],sort_keys=True))
    print("V25_B2_CSV_AND_FGDC_SCHEMA",json.dumps(d["source_structures"],sort_keys=True))
    print("V25_B2_STATUS",d["status"])
    print("V25_B2_NO_WATERFOWL_ECOLOGICAL_CHOICE_EFFECT_COMPUTED")
if __name__=="__main__":
    main()
