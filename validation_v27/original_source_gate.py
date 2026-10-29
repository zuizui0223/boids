#!/usr/bin/env python3
"""v27-A1 independent long-tailed tit pair GPS+tree Dryad official original files.

Provider DOI/version/manifest and exact original bytes when anonymously
available. NO GPS coordinates, original nest/pair IDs, resource cover values
or model outcomes accessed. Inaccessible provider downloads are real STOPs.
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

DOI="10.5061/dryad.kprr4xhm0"
BASE="https://datadryad.org"
API=BASE+"/api/v2/datasets/doi%3A10.5061%2Fdryad.kprr4xhm0"
EXPECTED_FILES=(
    "GPS_LOCATIONS.csv","NestLocations.csv","README.md",
    "Tree_Availability_Data.csv","TREE_SAMPLING_LOCATIONS.csv",
)
MAX_FILE=5_000_000
MAX_TOTAL=20_000_000
MAX_METADATA=4_000_000
UA="boids-v27-original-long-tailed-tit-tree-source/1.0"

def error(exc):
    if isinstance(exc,urllib.error.HTTPError):return "HTTP_"+str(exc.code)
    if isinstance(exc,urllib.error.URLError):return "NETWORK_"+type(exc.reason).__name__
    return type(exc).__name__+": "+str(exc)[:110]

def official_json(url):
    if urllib.parse.urlparse(url).hostname!="datadryad.org":
        raise ValueError("Non-Dryad source metadata host")
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=40) as stream:
        raw=stream.read(MAX_METADATA+1)
    if len(raw)>MAX_METADATA:
        raise ValueError("Provider metadata exceeds cap")
    obj=json.loads(raw)
    if not isinstance(obj,dict):
        raise ValueError("Provider metadata is not a JSON object")
    return obj

def official_href(obj,key):
    link=(obj.get("_links") or {}).get(key)
    if isinstance(link,list):link=link[0] if link else None
    if isinstance(link,dict):link=link.get("href")
    if not isinstance(link,str):return None
    url=urllib.parse.urljoin(BASE,link)
    if urllib.parse.urlparse(url).hostname!="datadryad.org":
        raise ValueError("Source URL outside original Dryad host")
    return url

def official_files(js):
    files=[]
    for value in (js.get("_embedded") or {}).values():
        if isinstance(value,list):
            files.extend(x for x in value if isinstance(x,dict)
                         and isinstance(x.get("path") or x.get("name"),str))
    if not files and isinstance(js.get("files"),list):
        files=js["files"]
    items=[]
    names=set()
    for x in files:
        name=Path(x.get("path") or x.get("name")).name
        if name in names:raise ValueError("Duplicate original provider filename")
        names.add(name)
        selfuri=official_href(x,"self")
        m=re.search(r"/files/([0-9]+)(?:/download)?(?:$|[?])",selfuri or "")
        ident=x.get("id") if isinstance(x.get("id"),int) else int(m.group(1)) if m else None
        items.append({
            "name":name,
            "size":x.get("size"),
            "provider_file_ID":ident,
            "provider_digest":x.get("digest"),
            "provider_digest_type":x.get("digestType"),
            "published_download_uri":official_href(x,"stash:download"),
            "original_file_self_URI":selfuri,
        })
    return items

def source_manifest():
    d={"doi":DOI,"status":"NOT_ADMITTED_OFFICIAL_DRYAD_METADATA_UNAVAILABLE",
       "source_title":None,"version":None,"license":None,
       "original_files":[],"source_errors":[]}
    try:dataset=official_json(API)
    except Exception as e:
        d["source_errors"].append({"stage":"dataset","error":error(e)})
        return d
    if str(dataset.get("identifier") or "").lower()!="doi:"+DOI.lower():
        d["source_errors"].append({"stage":"DOI","error":"ORIGINAL_DOI_MISMATCH"})
        return d
    d.update({"status":"ORIGINAL_DRYAD_DATASET_METADATA_VERIFIED",
              "source_title":dataset.get("title"),
              "version":dataset.get("versionNumber"),
              "license":dataset.get("license"),
              "source_dates":{"publicationDate":dataset.get("publicationDate"),
                              "modificationDate":dataset.get("lastModificationDate")}})
    link=official_href(dataset,"stash:version")
    if link is None:
        try:
            hist=official_json(API+"/versions")
            entries=(hist.get("_embedded") or {}).get("stash:versions") or []
            if entries:
                last=entries[-1]
                link=official_href(last,"self")
                if not link and isinstance(last.get("id"),int):
                    link=BASE+"/api/v2/versions/"+str(last["id"])
        except Exception as e:d["source_errors"].append({"stage":"versions","error":error(e)})
    if link is None:
        d["status"]="NOT_ADMITTED_NO_OFFICIAL_VERSION_LINK"
        return d
    try:version=official_json(link)
    except Exception as e:
        d["source_errors"].append({"stage":"version","error":error(e)})
        d["status"]="NOT_ADMITTED_OFFICIAL_DRYAD_VERSION_UNAVAILABLE"
        return d
    d["original_version_ID"]=version.get("id")
    fileuri=official_href(version,"stash:files")
    if fileuri is None and isinstance(version.get("id"),int):
        fileuri=BASE+"/api/v2/versions/"+str(version["id"])+"/files"
    if fileuri is None:
        d["status"]="NOT_ADMITTED_NO_OFFICIAL_FILE_LIST"
        return d
    try:files=official_json(fileuri)
    except Exception as e:
        d["source_errors"].append({"stage":"files","error":error(e)})
        d["status"]="NOT_ADMITTED_OFFICIAL_FILE_LIST_UNAVAILABLE"
        return d
    d["original_files"]=official_files(files)
    d["status"]="ORIGINAL_DRYAD_TIT_DATA_DICTIONARY_AND_FILES_MANIFEST_VERIFIED"
    return d

def public_file_download(item,to:Path):
    n=item.get("size");ident=item.get("provider_file_ID")
    if not isinstance(n,int) or not 0<n<=MAX_FILE or not isinstance(ident,int):
        return {"status":"NOT_ADMITTED_MISSING_ID_OR_SIZE_LIMIT","file":item["name"]}
    uris=list(dict.fromkeys(x for x in (
       item.get("published_download_uri"),
       BASE+"/api/v2/files/"+str(ident)+"/download",
       BASE+"/stash/downloads/file_stream/"+str(ident))
       if isinstance(x,str) and x.startswith(BASE+"/")))
    attempts=[]
    for url in uris:
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA})
            md5,sha=hashlib.md5(),hashlib.sha256()
            total=0
            with urllib.request.urlopen(req,timeout=75) as source:
                if urllib.parse.urlparse(source.geturl()).scheme!="https":
                    raise ValueError("Insecure original source redirect")
                with to.open("wb") as target:
                    for b in iter(lambda:source.read(512*1024),b""):
                        total+=len(b)
                        if total>MAX_FILE:raise ValueError("Unexpected source file over cap")
                        sha.update(b);md5.update(b);target.write(b)
            if total!=n:raise ValueError("Official source length mismatch")
            alg=str(item.get("provider_digest_type") or "").lower()
            published=str(item.get("provider_digest") or "").lower()
            if published and alg in ("sha-256","sha256","md5"):
                if (sha.hexdigest() if alg!="md5" else md5.hexdigest())!=published:
                    raise ValueError("Source publisher SHA/MD5 mismatch")
            return {"status":"ORIGINAL_DRYAD_FILE_BYTES_HASH_VERIFIED",
                    "file":item["name"],"source_exact_bytes":n,
                    "original_source_sha256":sha.hexdigest(),
                    "original_md5":md5.hexdigest(),
                    "publisher_digest_verified":bool(published and alg in ("sha-256","sha256","md5")),
                    "source_route":url,
                    "numeric_animal_or_habitat_values_read":False}
        except Exception as e:
            attempts.append({"source_route":url,"error":error(e)})
    return {"status":"NOT_ADMITTED_ORIGINAL_DRYAD_DOWNLOAD_DENIED_OR_MISMATCH",
            "file":item["name"],"source_attempts":attempts}

def run():
    meta=source_manifest()
    result={
        "study":"v27-2026-original-18-long-tailed-tit-breeding-pairs-GPS-tree-source",
        "source_DOI":DOI,
        "official_source_manifest":meta,
        "original_file_byte_receipts":{},
        "source_status":"NOT_ADMITTED_OFFICIAL_SOURCE_ORIGINAL_BYTES_UNAVAILABLE",
        "source_file_columns_or_original_pair_IDs_read":False,
        "animal_tree_use_or_future_movement_scores_computed":False,
        "v13_to_v26_prior_endpoints_untouched":True
    }
    if meta["status"]!="ORIGINAL_DRYAD_TIT_DATA_DICTIONARY_AND_FILES_MANIFEST_VERIFIED":
        return result
    files={x["name"]:x for x in meta["original_files"]}
    if set(EXPECTED_FILES)-set(files):
        result["source_status"]="NOT_ADMITTED_ORIGINAL_FILES_MISSING"
        return result
    total=sum(files[name]["size"] for name in EXPECTED_FILES if isinstance(files[name]["size"],int))
    if total>MAX_TOTAL:
        result["source_status"]="NOT_ADMITTED_ORIGINAL_AGGREGATE_FILE_CAP"
        return result
    with tempfile.TemporaryDirectory() as root:
        for name in EXPECTED_FILES:
            p=Path(root)/name
            result["original_file_byte_receipts"][name]=public_file_download(files[name],p)
    result["source_status"]=(
        "ALL_FIVE_TIT_ORIGINAL_SOURCE_BYTES_VERIFIED_NO_ANIMAL_ROWS_OPENED"
        if all(x["status"]=="ORIGINAL_DRYAD_FILE_BYTES_HASH_VERIFIED"
               for x in result["original_file_byte_receipts"].values())
        else "NOT_ADMITTED_SOME_OR_ALL_ORIGINAL_DRYAD_FILES_NOT_RETRIEVABLE")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
       "validation_v27/results/longtailed_tit_original_Dryad_source_v27.json"))
    a=p.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V27_SOURCE_METADATA",json.dumps(d["official_source_manifest"],sort_keys=True))
    print("V27_SOURCE_BYTES",json.dumps(d["original_file_byte_receipts"],sort_keys=True))
    print("V27_SOURCE_STATUS",d["source_status"])
    print("V27_NO_MOVEMENT_OR_HABITAT_CHOICE_FITTED")
if __name__=="__main__":
    main()
