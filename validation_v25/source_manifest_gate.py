#!/usr/bin/env python3
"""v25-A1: official Dryad mallard source manifest and anonymously accessible files.

Source-only: no wildlife location, used-available response or hunter access
values read. Original file bytes (if public) are pinned to provider size and
digest. Only README metadata text may be inspected; RDS bytes remain temporary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DOI="10.5061/dryad.cjsxksnd5"
BASE="https://datadryad.org"
API=BASE+"/api/v2/datasets/doi%3A10.5061%2Fdryad.cjsxksnd5"
TARGET_DATA="EAP23-0437_data.rds"
TARGET_DOC="README.md"
MAX_FILE=50_000_000
MAX_META=3_000_000
UA="boids-v25-independent-Tennessee-mallard-source-original-no-outcomes/1.0"


def safe_error(e):
    if isinstance(e,urllib.error.HTTPError):
        return "HTTP_"+str(e.code)
    if isinstance(e,urllib.error.URLError):
        return "URL_"+type(e.reason).__name__
    return type(e).__name__+": "+str(e)[:120]


def get_json(url):
    if not url.startswith(BASE+"/"):
        raise ValueError("Outside official Dryad source domain")
    req=urllib.request.Request(url,headers={
        "Accept":"application/json","User-Agent":UA})
    with urllib.request.urlopen(req,timeout=38) as resp:
        b=resp.read(MAX_META+1)
    if len(b)>MAX_META:raise ValueError("Official source JSON too big")
    obj=json.loads(b)
    if not isinstance(obj,dict):raise ValueError("Unexpected Dryad JSON schema")
    return obj


def provider_link(obj,key):
    record=(obj.get("_links") or {}).get(key)
    if isinstance(record,list):record=record[0] if record else None
    if isinstance(record,dict):record=record.get("href")
    if not isinstance(record,str):return None
    url=urllib.parse.urljoin(BASE,record)
    if not url.startswith(BASE+"/"):raise ValueError("Unexpected external provider link")
    return url


def list_original_files(document):
    items=[]
    for value in (document.get("_embedded") or {}).values():
        if isinstance(value,list):
            items.extend(x for x in value if isinstance(x,dict)
                         and isinstance(x.get("path") or x.get("name"),str))
    if not items and isinstance(document.get("files"),list):
        items=document["files"]
    out=[]
    for f in items:
        path=f.get("path") or f.get("name")
        name=Path(path).name
        link=provider_link(f,"self")
        match=re.search(r"/files/([0-9]+)(?:/download)?(?:$|[?])",link or "")
        id=f.get("id") if isinstance(f.get("id"),int) else int(match.group(1)) if match else None
        out.append({
           "filename":name,
           "original_file_id":id,
           "original_size_bytes":f.get("size"),
           "original_provider_digest":f.get("digest"),
           "original_provider_digest_type":f.get("digestType"),
           "original_file_uri":link,
           "published_download_uri":provider_link(f,"stash:download"),
           "field_keys":sorted(f.keys()),
           "source_link_keys":sorted((f.get("_links") or {}).keys()),
        })
    if len(set(x["filename"] for x in out))!=len(out):
        raise ValueError("Original provider duplicate filename")
    return out


def official_manifest():
    result={"doi":DOI,"record":API,
            "source_metadata_status":"NOT_ACQUIRED","files":[],
            "attempts":[]}
    try: d=get_json(API)
    except Exception as e:
        result["attempts"].append({"stage":"dataset","result":safe_error(e)})
        return result
    ident=str(d.get("identifier") or "").lower()
    if ident!="doi:"+DOI.lower():
        result["attempts"].append({"stage":"identifier","result":"ORIGINAL_DOI_MISMATCH",
                                  "reported":ident})
        return result
    result.update({
      "source_metadata_status":"DATASET_METADATA_VERIFIED",
      "source_title":d.get("title"),
      "license":d.get("license"),
      "source_version":d.get("versionNumber"),
      "publication_date":d.get("publicationDate"),
      "source_storage_bytes":d.get("storageSize"),
      "dataset_keys":sorted(d.keys())})
    version=provider_link(d,"stash:version")
    if version is None:
        try:
            versions=get_json(API+"/versions")
            val=(versions.get("_embedded") or {}).get("stash:versions") or []
            result["listed_versions"]=[
                {"version":v.get("versionNumber"),"id":v.get("id"),
                 "publicationDate":v.get("publicationDate")}
                for v in val if isinstance(v,dict)]
            if val:
                last=val[-1]
                version=provider_link(last,"self")
                if version is None and isinstance(last.get("id"),int):
                    version=BASE+"/api/v2/versions/"+str(last["id"])
        except Exception as e:
            result["attempts"].append({"stage":"versions","result":safe_error(e)})
    if not version:
        result["source_metadata_status"]="NO_PUBLIC_SOURCE_VERSION"
        return result
    try: v=get_json(version)
    except Exception as e:
        result["attempts"].append({"stage":"version","result":safe_error(e)})
        result["source_metadata_status"]="SOURCE_VERSION_UNAVAILABLE"
        return result
    result.update({"current_version_id":v.get("id"),
                   "current_version_number":v.get("versionNumber"),
                   "source_version_keys":sorted(v.keys())})
    files_uri=provider_link(v,"stash:files")
    if files_uri is None and isinstance(v.get("id"),int):
        files_uri=BASE+"/api/v2/versions/"+str(v["id"])+"/files"
    if files_uri is None:
        result["source_metadata_status"]="NO_FILE_MANIFEST_LINK"
        return result
    try: f=get_json(files_uri)
    except Exception as e:
        result["attempts"].append({"stage":"file_manifest","result":safe_error(e)})
        result["source_metadata_status"]="ORIGINAL_FILE_MANIFEST_UNAVAILABLE"
        return result
    result["files"]=list_original_files(f)
    result["file_list_response_keys"]=sorted(f.keys())
    result["source_metadata_status"]="OFFICIAL_FILE_MANIFEST_ACQUIRED" if result["files"] else "EMPTY_FILE_MANIFEST"
    return result


def original_file_download(source_file,to):
    size=source_file.get("original_size_bytes")
    id=source_file.get("original_file_id")
    if (not isinstance(size,int) or size<=0 or size>MAX_FILE
        or not isinstance(id,int)):
        return {"status":"NOT_ADMITTED_SOURCE_ID_OR_SIZE"}
    routes=list(dict.fromkeys(x for x in (
        source_file.get("published_download_uri"),
        BASE+"/api/v2/files/"+str(id)+"/download",
        BASE+"/stash/downloads/file_stream/"+str(id)
    ) if isinstance(x,str) and x.startswith(BASE+"/")))
    attempts=[]
    for u in routes:
        try:
            req=urllib.request.Request(u,headers={"User-Agent":UA})
            sha=hashlib.sha256();md5=hashlib.md5();total=0
            with urllib.request.urlopen(req,timeout=85) as incoming:
                if urllib.parse.urlparse(incoming.geturl()).scheme!="https":
                    raise ValueError("Insecure source download redirect")
                claimed=incoming.headers.get("Content-Length")
                if claimed and int(claimed)!=size:
                    raise ValueError("Source Content-Length mismatch")
                with to.open("wb") as file:
                    while True:
                        b=incoming.read(512*1024)
                        if not b:break
                        total+=len(b)
                        if total>MAX_FILE:raise ValueError("Outside original file size limit")
                        file.write(b);sha.update(b);md5.update(b)
            if total!=size:
                raise ValueError("Source data length differs from official manifest")
            reported=str(source_file.get("original_provider_digest") or "").lower()
            alg=str(source_file.get("original_provider_digest_type") or "").lower()
            if reported and alg in ("sha256","sha-256","md5"):
                actual=md5.hexdigest() if alg=="md5" else sha.hexdigest()
                if actual.lower()!=reported:
                    raise ValueError("Official source checksum mismatch")
            return {"status":"ORIGINAL_PROVIDER_BYTES_VERIFIED",
                    "file":source_file["filename"],
                    "bytes":total,"sha256":sha.hexdigest(),"md5":md5.hexdigest(),
                    "original_provider_digest_matched":
                      bool(reported and alg in ("sha256","sha-256","md5")),
                    "source_route":u,
                    "previous_public_attempts":attempts}
        except Exception as e:
            attempts.append({"route":u,"status":safe_error(e)})
    return {"status":"NOT_ADMITTED_SOURCE_ACCESS_OR_INTEGRITY",
            "file":source_file["filename"],"public_route_attempts":attempts}


def run():
    listing=official_manifest()
    out={"study":"v25-A1-original-Dryad-Tennessee-mallard-2024",
         "original_doi":DOI,
         "dataset_manifest":listing,
         "downloaded_original_files":{},
         "source_status":"NOT_ADMITTED_SOURCE_METADATA_OR_FILES_UNAVAILABLE",
         "original_animal_movement_or_habitat_response_read":False,
         "any_new_prediction_model_fitted":False,
         "all_prior_v13_to_v24_endpoints_unchanged":True}
    if listing["source_metadata_status"]!="OFFICIAL_FILE_MANIFEST_ACQUIRED":
        return out
    relevant=[x for x in listing["files"] if x["filename"] in (TARGET_DATA,TARGET_DOC)]
    if len(relevant)!=2:
        out["source_status"]="NOT_ADMITTED_SOURCE_REQUIRED_FILE_MISSING"
        return out
    with tempfile.TemporaryDirectory() as tmp:
        for item in relevant:
            path=Path(tmp)/item["filename"]
            d=original_file_download(item,path)
            out["downloaded_original_files"][item["filename"]]=d
            if d["status"]=="ORIGINAL_PROVIDER_BYTES_VERIFIED" and item["filename"]==TARGET_DOC:
                text=path.read_text(encoding="utf-8-sig",errors="replace")
                out["original_README_character_count"]=len(text)
                out["original_README_top_level_headings"]=[
                    line.strip()[:180] for line in text.splitlines()
                    if line.startswith("#")][:24]
    out["source_status"]=(
       "SOURCE_BINARIES_ACQUIRED_NO_RDS_ROWS_OPENED"
       if all(v["status"]=="ORIGINAL_PROVIDER_BYTES_VERIFIED"
              for v in out["downloaded_original_files"].values()) else
       "NOT_ADMITTED_SOURCE_RDS_OR_README_BYTES_UNAVAILABLE")
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v25/results/dryad_original_source_manifest_v25.json"))
    args=p.parse_args()
    r=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V25_ORIGINAL_SOURCE_META",json.dumps(r["dataset_manifest"],sort_keys=True))
    print("V25_ORIGINAL_SOURCE_FILES",json.dumps(r["downloaded_original_files"],sort_keys=True))
    print("V25_SOURCE_STATUS",r["source_status"])
    print("V25_SOURCE_ONLY_NO_ANIMAL_OR_HUNTING_EFFECT")
if __name__=="__main__":
    main()
