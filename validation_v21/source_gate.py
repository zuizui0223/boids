#!/usr/bin/env python3
"""v21 A independent American-redstart original Dryad source/no-outcome gate.

No movement values, vegetation indices or bird tracks are exported or modeled.
Official Dryad metadata and, only when anonymously accessible, RDS field grain.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DOI="10.5061/dryad.gb5mkkwx1"
BASE="https://datadryad.org"
API=BASE+"/api/v2/datasets/doi%3A10.5061%2Fdryad.gb5mkkwx1"
TARGET_FILES=("forays.rds","ndvi.rds")
MAX_BYTES=10_000_000
MAX_JSON=3_000_000
UA="boids-v21-independent-redstart-ndvi-source-gate/1.0"

def errcode(e):
    if isinstance(e,urllib.error.HTTPError):return "HTTP_"+str(e.code)
    if isinstance(e,urllib.error.URLError):return "URL_"+type(e.reason).__name__
    return type(e).__name__+": "+str(e)[:130]

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=35) as response:
        raw=response.read(MAX_JSON+1)
    if len(raw)>MAX_JSON:raise ValueError("Source JSON size exceeded cap")
    obj=json.loads(raw)
    if not isinstance(obj,dict):raise ValueError("Unknown Dryad API schema")
    return obj

def link(obj,name):
    value=(obj.get("_links") or {}).get(name)
    if isinstance(value,list):value=value[0] if value else None
    if isinstance(value,dict):value=value.get("href")
    if not isinstance(value,str):return None
    url=urllib.parse.urljoin(BASE,value)
    if not url.startswith(BASE+"/"):raise ValueError("Non-Dryad link")
    return url

def official_list(doc):
    allfiles=[]
    for v in (doc.get("_embedded") or {}).values():
        if isinstance(v,list):
            allfiles.extend(x for x in v if isinstance(x,dict) and "path" in x)
    if not allfiles and isinstance(doc.get("files"),list):
        allfiles=doc["files"]
    return allfiles

def get_metadata():
    result={"status":"NOT_ACQUIRED","doi":DOI,"dataset_api":API,"files":[],
            "errors":[]}
    try:ds=get_json(API)
    except Exception as exc:
        result["errors"].append({"step":"dataset","reason":errcode(exc)})
        return result
    if str(ds.get("identifier") or "").lower()!="doi:"+DOI.lower():
        result["errors"].append({"step":"DOI","reason":"mismatch"})
        return result
    result.update({"status":"DATASET_META_VERIFIED",
                   "source_title":ds.get("title"),
                   "license":ds.get("license"),
                   "source_version":ds.get("versionNumber"),
                   "dataset_field_names":sorted(ds.keys())})
    versionlink=link(ds,"stash:version")
    if versionlink is None:
        # Explicit fallback to versions listing, never invent a version ID.
        try:
            versions=get_json(API+"/versions")
            items=(versions.get("_embedded") or {}).get("stash:versions",[])
            result["published_versions"]=[
                {"id":x.get("id"),"versionNumber":x.get("versionNumber")}
                for x in items if isinstance(x,dict)]
            if items: versionlink=link(items[-1],"self") or (
                BASE+"/api/v2/versions/"+str(items[-1].get("id")))
        except Exception as exc:result["errors"].append({
            "step":"versions","reason":errcode(exc)})
    if not versionlink:
        result["status"]="NO_PUBLIC_VERSION_METADATA"
        return result
    try:version=get_json(versionlink)
    except Exception as exc:
        result["status"]="SOURCE_VERSION_INACCESSIBLE"
        result["errors"].append({"step":"version","reason":errcode(exc)})
        return result
    result["version_id"]=version.get("id")
    result["version_number"]=version.get("versionNumber")
    fl=link(version,"stash:files")
    if not fl and isinstance(version.get("id"),int):
        fl=BASE+"/api/v2/versions/"+str(version["id"])+"/files"
    if not fl:
        result["status"]="NO_OFFICIAL_FILE_LISTING_LINK"
        result["version_field_names"]=sorted(version.keys())
        return result
    try:listing=get_json(fl)
    except Exception as exc:
        result["status"]="SOURCE_FILES_INACCESSIBLE"
        result["errors"].append({"step":"files","reason":errcode(exc)})
        return result
    entries=official_list(listing)
    result["file_list_response_fields"]=sorted(listing.keys())
    for f in entries:
        name=str(f.get("path") or f.get("name") or "")
        if not name:continue
        official_link=link(f,"self") or link(f,"stash:download")
        match=(__import__("re").search(r"/files/([0-9]+)(?:/download)?(?:$|[?])",
                                     official_link) if official_link else None)
        inferred_id=int(match.group(1)) if match else None
        result["files"].append({
          "name":Path(name).name,"original_path":name,
          "id":f.get("id") if isinstance(f.get("id"),int) else inferred_id,
          "official_file_reference_url":official_link,
          "source_link_keys":sorted((f.get("_links") or {}).keys()),
          "source_file_field_keys":sorted(f.keys()),
          "size":f.get("size"),
          "digest":f.get("digest"),"digestType":f.get("digestType")})
    result["status"]="ORIGINAL_MANIFEST_ACQUIRED" if result["files"] else "NO_FILES_IN_MANIFEST"
    return result

def fetch_file(item,to):
    size=item.get("size");ident=item.get("id")
    if not isinstance(size,int) or not 0<size<=MAX_BYTES or not isinstance(ident,int):
        return {"status":"SOURCE_OUTSIDE_BOUNDED_FILE_REQUIREMENT"}
    attempts=[]
    for u in (BASE+"/api/v2/files/"+str(ident)+"/download",
              BASE+"/stash/downloads/file_stream/"+str(ident)):
        try:
            md5=hashlib.md5();sha=hashlib.sha256();n=0
            req=urllib.request.Request(u,headers={"User-Agent":UA})
            with urllib.request.urlopen(req,timeout=75) as resp,to.open("wb") as out:
                for chunk in iter(lambda:resp.read(262144),b""):
                    n+=len(chunk)
                    if n>MAX_BYTES:raise ValueError("source exceeds fixed cap")
                    out.write(chunk);md5.update(chunk);sha.update(chunk)
            if n!=size:raise ValueError("provider byte count mismatch")
            published=item.get("digest");alg=str(item.get("digestType") or "").lower()
            if published and alg in ("md5","sha256","sha-256"):
                actual=md5.hexdigest() if alg=="md5" else sha.hexdigest()
                if str(published).lower()!=actual.lower():raise ValueError("published digest mismatch")
            return {"status":"ORIGINAL_BYTES_VERIFIED","bytes":n,
                    "sha256":sha.hexdigest(),"md5":md5.hexdigest(),
                    "source":u,"provider_digest_matched":
                        bool(published and alg in ("md5","sha256","sha-256"))}
        except Exception as exc:
            attempts.append({"route":u,"reason":errcode(exc)})
    return {"status":"ORIGINAL_BYTES_NOT_ACCESSIBLE","attempts":attempts}

def profile_rds(path,name):
    import pyreadr
    frames=[x for x in pyreadr.read_r(str(path)).values()
            if hasattr(x,"columns")]
    if len(frames)!=1:raise ValueError("Expected one original tabular RDS object")
    df=frames[0]
    p={"rows":len(df),"columns":list(map(str,df.columns)),
       "types":{str(k):str(df[k].dtype) for k in df.columns},
       "missing":{str(k):int(df[k].isna().sum()) for k in df.columns},
       "raw_movement_and_NDVI_values_exported":False}
    if name=="forays.rds" and {"motusID","year","week"}.issubset(df.columns):
        d=df.dropna(subset=["motusID","year","week"])
        n=d.groupby("motusID").size()
        keys=d[["motusID","year","week"]].astype(str)
        p.update({"distinct_individual_ids":len(n),
                  "individuals_with_at_least_3_records":int((n>=3).sum()),
                  "potential_future_week_targets_from_IDs_only":int(sum(max(0,x-2) for x in n)),
                  "distinct_years":d["year"].nunique(),
                  "distinct_weeks":d["week"].nunique(),
                  "duplicate_individual_year_week_keys":int(keys.duplicated(keep=False).sum())})
    if name=="ndvi.rds" and {"year","week"}.issubset(df.columns):
        d=df.dropna(subset=["year","week"])
        p.update({"unique_year_weeks":len(d[["year","week"]].drop_duplicates()),
                  "ndvi_raw_present":int(d["ndvi"].notna().sum()) if "ndvi" in d else 0,
                  "duplicate_year_week_keys":int(d[["year","week"]].duplicated(keep=False).sum())})
    return p

def run():
    meta=get_metadata()
    result={"study":"v21-original-redstart-NDVI-bird-week-source-audit",
            "source_metadata":meta,"source_bytes":{},"source_shape":{},
            "status":"NOT_ADMITTED_ORIGINAL_DATA_ACCESS_OR_STRUCTURE",
            "no_forecast_or_original_numeric_values_exported":True,
            "v13_v20_previous_results_unchanged":True}
    if meta["status"]!="ORIGINAL_MANIFEST_ACQUIRED":return result
    with tempfile.TemporaryDirectory() as d:
        for name in TARGET_FILES:
            matches=[x for x in meta["files"] if x["name"]==name]
            if len(matches)!=1:
                result["source_bytes"][name]={"status":"MISSING_OR_DUPLICATED_OFFICIAL_FILE"}
                continue
            f=Path(d)/name
            rec=fetch_file(matches[0],f)
            result["source_bytes"][name]=rec
            if rec["status"]!="ORIGINAL_BYTES_VERIFIED":continue
            try:result["source_shape"][name]=profile_rds(f,name)
            except Exception as exc:result["source_shape"][name]={
                "status":"SOURCE_RDS_GRANULARITY_UNREADABLE","reason":errcode(exc)}
    a=result["source_shape"].get("forays.rds",{})
    b=result["source_shape"].get("ndvi.rds",{})
    if (a.get("individuals_with_at_least_3_records",0)>=8 and
        a.get("potential_future_week_targets_from_IDs_only",0)>=30 and
        a.get("duplicate_individual_year_week_keys",999)==0 and
        a.get("distinct_years",0)>=2 and
        b.get("ndvi_raw_present",0)>0 and
        b.get("duplicate_year_week_keys",999)==0):
        result["status"]="SOURCE_STRUCTURE_ELIGIBLE_FOR_NEW_OUTCOME_BLIND_PREDICTION_CONTRACT"
    else:
        result["status"]="NOT_ADMITTED_INSUFFICIENT_INDIVIDUAL_WEEK_OR_RAW_NDVI"
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,
                   default=Path("validation_v21/results/source_gate_v21.json"))
    a=p.parse_args()
    d=run();a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V21_DRYAD_META",json.dumps(d["source_metadata"],sort_keys=True))
    print("V21_DRYAD_FILES",json.dumps(d["source_bytes"],sort_keys=True))
    print("V21_DRYAD_STRUCTURE",json.dumps(d["source_shape"],sort_keys=True))
    print("V21_STATUS",d["status"])
    print("V21_NO_MOVEMENT_OR_ENVIRONMENT_PREDICTION_FITTED")

if __name__=="__main__":
    main()
