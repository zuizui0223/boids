#!/usr/bin/env python3
"""v47 USGS 2026 NABat original ScienceBase item metadata-only source gate."""
import argparse
from collections import Counter
import json
import urllib.error
import urllib.request
from pathlib import Path

ITEM_ID="6ace802b1ba49b69a5819e47"
DOI="10.5066/P1HDZNY9"
URLS=(
    f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json",
    f"https://sciencebase.usgs.gov/catalog/item/{ITEM_ID}?format=json",
)
CAP=1_000_000
OUT=Path("validation_v47/results/nabat_usgs_public_manifest_source_v47.json")
WORDS=("readme","manifest","metadata","survey","effort","recording","deployment",
       "activity","count","sample","acoustic","audio","wav","csv","parquet","xml")


def request(url):
    req=urllib.request.Request(url,headers={
        "Accept":"application/json",
        "User-Agent":"boids-v47-independent-nabat-source-only/1.0"})
    with urllib.request.urlopen(req,timeout=25) as r:
        return r.status,r.headers.get("Content-Type",""),r.read(CAP+1)


def provider_json(source):
    """Only published file metadata, not acoustic data or species observations."""
    original_files=source.get("files") or []
    if not isinstance(original_files,list):original_files=[]
    categories=Counter()
    extensions=Counter()
    size_bins=Counter()
    for file in original_files:
        if not isinstance(file,dict):continue
        filename=str(file.get("name") or file.get("fileName") or "")
        for term in WORDS:
            if term in filename.casefold():categories[term]+=1
        if "." in filename:
            ext="."+filename.rsplit(".",1)[-1].casefold()
            extensions[ext if len(ext)<14 else "(long-ext)"]+=1
        size=file.get("size") or file.get("sizeInBytes")
        try:size=int(size)
        except (ValueError,TypeError):continue
        if size<1_000_000:size_bins["under_1MB"]+=1
        elif size<100_000_000:size_bins["1MB_to_100MB"]+=1
        else:size_bins["100MB_or_more"]+=1
    return {
        "original_provider_item_id_matches":str(source.get("id",""))==ITEM_ID,
        "original_provider_file_metadata_entries_n":len(original_files),
        "source_file_name_keyword_categories":dict(categories),
        "source_file_extensions":dict(extensions),
        "original_file_size_bands":dict(size_bins),
        "source_item_has_files_array":isinstance(source.get("files"),list),
        "source_body_numeric_acoustic_values_parsed":False,
        "original_file_names_site_paths_and_urls_not_exported":True,
    }


def audit(getter=request):
    record={
        "programme":"v47_independent_2026_usgs_NABat_public_source_admission",
        "official_release_doi":DOI,
        "official_sciencebase_item_id":ITEM_ID,
        "original_usfws_2010_2018_overlap_not_yet_resolved":True,
        "complete_site_night_effort_verified":False,
        "raw_audio_or_animal_species_activity_values_opened":False,
        "classification_causality_claimed":False,
        "biological_prediction_fitted":False,
        "attempts":[],
    }
    for url in URLS:
        attempt={"official_source_host":url.split("/")[2]}
        try:
            status,mime,raw=getter(url)
            attempt.update({"http":status,"mime":str(mime)[:80],
                            "response_bytes_capped":len(raw)})
            if status!=200 or len(raw)>CAP or not raw.lstrip().startswith(b"{"):
                attempt["status"]="SOURCE_NON_JSON_HTTP_OR_SIZE_STOP"
            else:
                try:
                    obj=json.loads(raw)
                except (UnicodeDecodeError,json.JSONDecodeError):
                    attempt["status"]="SOURCE_JSON_DECODE_STOP"
                else:
                    if not isinstance(obj,dict) or str(obj.get("id",""))!=ITEM_ID:
                        attempt["status"]="SOURCE_WRONG_ITEM_OR_SCHEMA_STOP"
                    else:
                        attempt["status"]="ORIGINAL_ITEM_JSON_RETRIEVED"
                        record["source_file_manifest_metadata"]=provider_json(obj)
                        record["attempts"].append(attempt)
                        record["status"]="PUBLIC_ORIGINAL_ITEM_METADATA_ONLY"
                        return record
        except urllib.error.HTTPError as e:
            attempt.update({"http":e.code,"status":"HTTP_ACCESS_STOP"})
        except (urllib.error.URLError,TimeoutError,OSError) as e:
            attempt.update({"status":"TRANSPORT_ACCESS_STOP","error_class":type(e).__name__})
        record["attempts"].append(attempt)
    record["status"]="PUBLIC_SOURCE_API_ACCESS_STOP"
    return record


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=OUT)
    args=p.parse_args()
    result=audit()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V47_USGS_NABAT_PUBLIC_ITEM_SOURCE="+json.dumps(result,sort_keys=True))
    assert result["raw_audio_or_animal_species_activity_values_opened"] is False
    assert result["complete_site_night_effort_verified"] is False
    assert result["biological_prediction_fitted"] is False
