"""Dryad independent P. kuhlii archival source gate: official metadata only.

No biological acoustic outcomes or original XLSX worksheet records are read.
Only official provider dataset/version/file metadata and 4KB Range if allowed.
If HTTP401/403, source admission STOP; do not bypass publisher access controls.
"""
from __future__ import annotations
import hashlib,json,urllib.request,urllib.error
from pathlib import Path
import time

OUT=Path(__file__).resolve().parent/"PIPISTRELLUS_2015_SOURCE_GATE_V1.json"
DOI="10.5061/dryad.8f0v4"
DATASET_URL="https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.8f0v4"
HEADERS={"User-Agent":"bat-original-data-access-admission/1.0","Accept":"application/json,*/*"}

def fetch(url,mode="GET",limit=250000,range_header=None):
    headers=HEADERS.copy()
    if range_header:
        headers["Range"]=range_header
    req=urllib.request.Request(url,headers=headers,method=mode)
    with urllib.request.urlopen(req,timeout=40) as r:
        outcome={"status":r.status,
                 "content_type":r.headers.get("Content-Type"),
                 "content_length":r.headers.get("Content-Length"),
                 "accept_ranges":r.headers.get("Accept-Ranges"),
                 "content_range":r.headers.get("Content-Range")}
        if mode=="HEAD":return outcome
        data=r.read(limit+1)
        if len(data)>limit:
            raise ValueError("BOUNDED_READ_LIMIT_REACHED; STOP_NO_FULL_FILE_DOWNLOAD")
        outcome["data"]=data
        return outcome

def uri_link(base,relative):
    if not relative:raise ValueError("SOURCE_LINK_MISSING")
    if relative.startswith("/"):return "https://datadryad.org"+relative
    if relative.startswith("https://"):return relative
    raise ValueError("SOURCE_UNTRUSTED_RELATIVE_LINK")

def json_resource(url):
    r=fetch(url,limit=300000)
    return json.loads(r["data"].decode("utf-8"))

def main():
    result={"schema":1,"status":"NOT_CHECKED","date":"2026-11-05",
            "source":"Dryad DOI "+DOI,
            "external_species":"Pipistrellus kuhlii",
            "new_animal_measurements":False,
            "source_xlsx_rows_or_bat_IDs_opened":False,
            "original_source_bytes_committed":False,
            "source_get_authorization_not_bypassed":True,
            "publisher_dataset":{},
            "publisher_file":{}}
    try:
        dataset=json_resource(DATASET_URL)
        links=dataset.get("_links") or {}
        version=uri_link(DATASET_URL,(links.get("stash:version") or {}).get("href"))
        original={
            "dataset_API_url":DATASET_URL,"source_identifier":dataset.get("identifier"),
            "source_title":dataset.get("title"),"license":dataset.get("license"),
            "source_publication_date":dataset.get("publicationDate"),
            "source_original_provider_id":dataset.get("id"),
            "dataset_version_API_url":version,
        }
        result["publisher_dataset"]=original
        ver=json_resource(version)
        u=uri_link(version,(ver.get("_links") or {}).get("stash:files",{}).get("href"))
        files=json_resource(u)
        arr=(files.get("_embedded") or {}).get("stash:files") or []
        if not isinstance(arr,list):raise ValueError("FILES_NOT_ARRAY")
        candidates=[x for x in arr if str(x.get("path","")).endswith("Dryad.xlsx")]
        result["original_file_catalog_n"]=len(arr)
        result["original_dataset_file_names"]=[
            {"basename":v.get("path"),"source_size_bytes":v.get("size"),"provider_md5":v.get("digest")}
            for v in arr[:30]
        ]
        if len(candidates)!=1:
            result["status"]="STOP_NO_UNIQUE_ORIGINAL_DATA_XLSX"
            raise ValueError("Expected exactly one publisher original Dryad.xlsx")
        file=candidates[0]
        direct_url=uri_link(u,(file.get("_links") or {}).get("stash:download",{}).get("href"))
        result["publisher_file"]={
            "file_basename":file.get("path"),"source_size_bytes":file.get("size"),
            "provider_digest":file.get("digest"),"download_original_API_url":direct_url,
            "rights_verified_license":dataset.get("license")}
        try:
            h=fetch(direct_url,mode="HEAD")
            result["publisher_file"]["HEAD"]={k:v for k,v in h.items()}
            result["publisher_file"]["HEAD_status"]="PASS"
        except Exception as e:
            result["publisher_file"]["HEAD_status"]="STOP_PROVIDER_HEAD"
            result["publisher_file"]["HEAD_error"]=type(e).__name__+":"+str(e)[:180]
        try:
            h=fetch(direct_url,mode="GET",range_header="bytes=0-4095",limit=4096)
            result["publisher_file"]["range_response"]={k:v for k,v in h.items() if k!="data"}
            result["publisher_file"]["range_magic_hex"]=h["data"][:4].hex()
            result["publisher_file"]["range_nbytes"]=len(h["data"])
            result["publisher_file"]["range_head_sha256"]=hashlib.sha256(h["data"]).hexdigest()
            result["status"]=("PASS_PUBLISHER_AUTHORIZED_RANGE_ONLY" if h["status"]==206
                              else "STOP_PROVIDER_NOT_HONORING_RANGE")
        except Exception as e:
            result["publisher_file"]["range_error"]=type(e).__name__+":"+str(e)[:180]
            result["status"]="STOP_PROVIDER_RANGE_ACCESS"
    except Exception as e:
        if result["status"]=="NOT_CHECKED":
            result["status"]="STOP_DATASET_CATALOG_ACCESS"
        result["source_gate_error"]=type(e).__name__+":"+str(e)[:200]
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("DRYAD_SOURCE_STATUS",result["status"])
    print("DRYAD_DATASET",result["publisher_dataset"])
    print("DRYAD_FILE",result["publisher_file"])
    print("DRYAD_FILE_COUNT",result.get("original_file_catalog_n"))
    print("ORIGINAL_BAT_SOURCE_RECORDS_OPENED",result["source_xlsx_rows_or_bat_IDs_opened"])
    return 0
if __name__=="__main__":
    raise SystemExit(main())
