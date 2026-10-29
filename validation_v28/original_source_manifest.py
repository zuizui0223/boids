#!/usr/bin/env python3
"""v28-A1: 2023 noctule bat Zenodo ORIGINAL source manifest ONLY, no GPS.

No source animal records are downloaded, parsed, or redistributed.
Official record ID, file names, original exact sizes, provider MD5,
version, license and source URLs are established independently of effects.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

RECORD_ID=7535030
API=f"https://zenodo.org/api/records/{RECORD_ID}"
META_CAP=4_000_000
SINGLE_FILE_CAP=100_000_000
ALL_FILE_CAP=200_000_000
AGENT="boids-v28-independent-original-wild-noctule-bat-source-only/1.0"
STRUCTURED_EXTENSIONS=(".csv",".tsv",".zip",".rds",".rdata",".xlsx",".parquet",".txt")


def fetch_original():
    req=urllib.request.Request(API,headers={
        "User-Agent":AGENT,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=45) as resp:
        final=urllib.parse.urlparse(resp.geturl())
        if final.hostname!="zenodo.org" or final.scheme!="https":
            raise ValueError("Official source metadata redirect outside Zenodo")
        content=resp.read(META_CAP+1)
    if len(content)>META_CAP:
        raise ValueError("Official source record over fixed metadata cap")
    x=json.loads(content)
    if not isinstance(x,dict) or str(x.get("id"))!=str(RECORD_ID):
        raise ValueError("Official Zenodo original record mismatched")
    return x


def source_list(original:dict):
    files=original.get("files") or []
    if isinstance(files,dict):
        files=list((files.get("entries") or {}).values())
    if not isinstance(files,list):
        raise ValueError("Unknown Zenodo source file manifest schema")
    known=set();data=[]
    for f in files:
        if not isinstance(f,dict):
            continue
        name=f.get("key") or f.get("filename")
        if not isinstance(name,str) or not name:
            raise ValueError("Zenodo original file has no name")
        if name in known:
            raise ValueError("Duplicated original provider filename")
        known.add(name)
        size=f.get("size")
        check=str(f.get("checksum") or "")
        links=f.get("links") or {}
        url=links.get("content") or links.get("self")
        if url is not None:
            parsed=urllib.parse.urlparse(url)
            if parsed.hostname!="zenodo.org" or parsed.scheme!="https":
                raise ValueError("Official source file URL outside Zenodo")
        lower=name.lower()
        candidate=lower.endswith(STRUCTURED_EXTENSIONS) and (
            not lower.endswith(("_readme.txt","_dictionary.txt")))
        data.append({
            "filename":name,
            "source_exact_bytes":size,
            "provider_original_checksum":check,
            "original_file_id":f.get("id"),
            "file_download_url":url,
            "structured_file_candidate":candidate,
            "single_source_cap_admissible":
                candidate and isinstance(size,int) and 0<size<=SINGLE_FILE_CAP,
            "provider_file_manifest_field_names":sorted(f.keys()),
        })
    return data


def run()->dict:
    original=fetch_original()
    files=source_list(original)
    md=original.get("metadata") or {}
    candidate=[f for f in files if f["single_source_cap_admissible"]]
    total=sum(f["source_exact_bytes"] for f in candidate)
    digest_ok=all(re.fullmatch(r"md5:[0-9a-fA-F]{32}",str(f["provider_original_checksum"]))
                  for f in candidate)
    return {
        "study":"v28-A1-original-noctule-bat-GPS-turbine-habitat-SSA-source-manifest",
        "status":"ORIGINAL_ZENODO_METADATA_ONLY_NO_BAT_BEHAVIOR",
        "source_record_id":RECORD_ID,
        "source_doi":original.get("doi"),
        "source_title":md.get("title"),
        "source_publication_date":original.get("created"),
        "source_version":md.get("version"),
        "source_license":md.get("license"),
        "parent_doi":md.get("prereserve_doi") or md.get("related_identifiers"),
        "source_files":files,
        "source_aggregate_file_count":len(files),
        "individual_structured_source_within_predeclared_size_cap":[f["filename"] for f in candidate],
        "structured_candidate_aggregate_source_bytes":total,
        "metadata_source_download_eligibility":
           "REQUIRES_SOURCE_SCOPED_FROZEN_FILE_CHOICE"
           if candidate and total<=ALL_FILE_CAP and digest_ok else
           "NOT_ADMITTED_SOURCE_SIZE_OR_MD5_OR_FILE_TYPE",
        "case_TRUE_random_FALSE_respondent_grain_not_verified":True,
        "independent_original_bat_IDs_or_flights_not_opened":True,
        "original_GPS_locations_or_habitat_outcome_numbers_not_read":True,
        "new_bat_prediction_or_social_force_fitted":False,
        "prior_v13_to_v27_frozen_endpoints_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v28/results/zenodo_original_bat_source_manifest_v28.json"))
    args=p.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V28_ORIGINAL_SOURCE_MANIFEST",json.dumps(out,sort_keys=True))
    print("V28_NO_BAT_OR_GPS_RSF_MODEL_FITTED")
if __name__=="__main__":
    main()
