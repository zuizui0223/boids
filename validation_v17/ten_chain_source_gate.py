#!/usr/bin/env python3
"""v17-C independent Valentini 2021 source-first Figshare audit (no GPS outcomes).

Source: eLife 68653, Figshare 14043362. Program ONLY enumerates official
provider metadata, optionally downloads size/MD5-verified original small
archives, and summarizes file paths and named CSV headers. NEVER interprets
or exports GPS fixes, routes, turns, destinations or observed predictor gains.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import tempfile
import urllib.request
import zipfile
from pathlib import Path

SOURCE_ID=14043362
SOURCE_DOI="10.6084/m9.figshare.14043362"
API=f"https://api.figshare.com/v2/articles/{SOURCE_ID}"
MAX_JSON_BYTES=6_000_000
MAX_SINGLE_BYTES=160_000_000
MAX_TOTAL_BYTES=350_000_000
ZIP_TOTAL_LIMIT=2_000_000_000
MIN_DOWNLOAD_BYTES=100
ARCHIVE_EXTS=(".zip",".csv",".txt",".json")
MAX_HEADER_BYTES=65536

def get_json()->dict:
    req=urllib.request.Request(API,headers={"Accept":"application/json",
         "User-Agent":"boids-v17-independent-ten-chain-source-gate/1.0"})
    with urllib.request.urlopen(req,timeout=40) as response:
        b=response.read(MAX_JSON_BYTES+1)
    if len(b)>MAX_JSON_BYTES:
        raise ValueError("Figshare API JSON exceeds limit")
    obj=json.loads(b)
    if not isinstance(obj,dict) or str(obj.get("id"))!=str(SOURCE_ID):
        raise ValueError("Wrong Figshare article ID")
    return obj


def original_listing(record:dict)->dict:
    files=record.get("files") or []
    if not isinstance(files,list):
        raise ValueError("Figshare original file listing unexpected")
    items=[]
    seen=set()
    for raw in files:
        if not isinstance(raw,dict):continue
        filename=raw.get("name")
        size=raw.get("size")
        url=raw.get("download_url")
        md5=raw.get("computed_md5") or raw.get("supplied_md5")
        if (not isinstance(filename,str) or filename in seen or
            not isinstance(size,int) or size<0):
            raise ValueError("Source filename/size missing or duplicated")
        if (not isinstance(url,str) or
            not url.startswith(("https://ndownloader.figshare.com/",
                                "https://figshare.com/",
                                "https://api.figshare.com/","https://s3-eu-west-1.amazonaws.com/"))):
            raise ValueError("Unexpected original Figshare file URL")
        seen.add(filename)
        items.append({"name":filename,"bytes":size,"provider_md5":md5,
                      "download_url":url,"file_id":raw.get("id"),
                      "is_link_only":raw.get("is_link_only",False)})
    return {"status":"OFFICIAL_FIGSHARE_FILE_METADATA",
            "files":items,
            "total_listed_bytes":sum(i["bytes"] for i in items)}


def bounded_download(file:dict,destination:Path)->dict:
    if file["bytes"]>MAX_SINGLE_BYTES:
        raise ValueError("Original file exceeds independent bounded source cap")
    req=urllib.request.Request(file["download_url"],
            headers={"User-Agent":"boids-v17-independent-ten-chain-source-gate/1.0"})
    sha,md5,n=hashlib.sha256(),hashlib.md5(),0
    with urllib.request.urlopen(req,timeout=120) as s:
        claim=s.headers.get("Content-Length")
        if claim and int(claim)!=file["bytes"]:
            raise ValueError("Original source claimed size changed")
        with destination.open("wb") as w:
            for chunk in iter(lambda:s.read(1024*1024),b""):
                n+=len(chunk)
                if n>MAX_SINGLE_BYTES:
                    raise ValueError("Unbounded download")
                w.write(chunk);sha.update(chunk);md5.update(chunk)
    if n!=file["bytes"]:
        raise ValueError("Source byte length differs from provider")
    official=file["provider_md5"]
    if not isinstance(official,str) or not re.fullmatch(r"[a-fA-F0-9]{32}",official):
        raise ValueError("No reliable Figshare source MD5 to match")
    if md5.hexdigest()!=official.lower():
        raise ValueError("Original MD5 does not match")
    return {"source_name":file["name"],"size_verified":n,
            "original_md5_matched":True,"sha256":sha.hexdigest()}


def masked_header(first:bytes)->dict:
    line=first.decode("utf-8-sig",errors="replace").strip("\r\n")
    fields=[x.strip('" ').strip() for x in line.split(",")]
    valid=(2<=len(fields)<=120 and all(re.fullmatch(
           r"[A-Za-z_][A-Za-z0-9_ /().+\-]*",s) for s in fields))
    if valid:
        return {"status":"COLUMN_NAMES_ONLY","columns":fields}
    return {"status":"UNKNOWN_HEADER_OR_NUMERIC_DATA_FIRST_LINE",
            "field_count":len(fields)}


def inventory_zip(path:Path)->dict:
    with zipfile.ZipFile(path,"r") as arc:
        names=[x.filename for x in arc.infolist()]
        if len(names)!=len(set(names)):
            raise ValueError("Duplicate ZIP member paths")
        for z in arc.infolist():
            name=z.filename.replace("\\","/")
            if name.startswith("/") or ".." in name.split("/") or z.flag_bits&1:
                raise ValueError("Original ZIP has unsafe/encrypted member")
        if sum(z.file_size for z in arc.infolist())>ZIP_TOTAL_LIMIT:
            raise ValueError("Original archive expansion exceeds bounded limit")
        files=sorted(z for z in arc.infolist() if not z.is_dir())
        ext=collections.Counter(Path(f.filename).suffix.lower() or "none" for f in files)
        stage_names=collections.Counter()
        chain_candidate_names=set()
        inspected=[]
        for z in files:
            tokens=re.findall(r"(?:chain|transmission)[_\-\s]*(\d{1,2})",
                              z.filename.lower())
            chain_candidate_names.update(tokens)
            if (len(inspected)<30 and
                    Path(z.filename).suffix.lower() in (".csv",".txt")):
                with arc.open(z) as stream:
                    line=stream.readline(MAX_HEADER_BYTES+1)
                inspected.append({"path":z.filename,"header":masked_header(line),
                                  "file_size":z.file_size})
        return {"status":"SOURCE_FILENAME_AND_HEADER_ONLY",
                "files_in_zip":len(files),
                "extension_counts":dict(sorted(ext.items())),
                "filename_examples":[z.filename for z in files[:80]],
                "source_explicit_chain_label_count":len(chain_candidate_names),
                "candidate_chain_ids":sorted(chain_candidate_names),
                "first_30_text_headers":inspected,
                "source_original_UTC_verified":False,
                "source_navigational_outcomes_analyzed":False,
                "weather_with_verified_clock_available":False}


def run()->dict:
    meta=get_json()
    listing=original_listing(meta)
    licence=meta.get("license")
    out={"study":"v17c-independent-ten-chain-2021-figshare-source",
         "status":"SOURCE_PROVENANCE_NOT_BIOLOGICAL_EFFECT",
         "source_article_id":SOURCE_ID,
         "source_doi":meta.get("doi"),
         "source_title":meta.get("title"),
         "source_license":licence,
         "source_publication":meta.get("published_date"),
         "source_file_listing":listing,
         "no_movement_outcomes_read":True,
         "acquired_files":[]}
    aggregate=0
    with tempfile.TemporaryDirectory() as tmp:
        for idx,file in enumerate(listing["files"]):
            if (not file["name"].lower().endswith(ARCHIVE_EXTS) or
                not MIN_DOWNLOAD_BYTES<=file["bytes"]<=MAX_SINGLE_BYTES or
                aggregate+file["bytes"]>MAX_TOTAL_BYTES or
                file["is_link_only"]):
                continue
            path=Path(tmp)/f"public_{idx}"
            try:
                integrity=bounded_download(file,path)
                if file["name"].lower().endswith(".zip"):
                    integrity["structure"]=inventory_zip(path)
                elif file["name"].lower().endswith(".csv"):
                    with path.open("rb") as raw:
                        integrity["first_record"]=masked_header(raw.readline(MAX_HEADER_BYTES+1))
                else:
                    integrity["text_value_rows_parsed"]=0
                out["acquired_files"].append(integrity)
                aggregate+=file["bytes"]
            except Exception as exc:
                out["acquired_files"].append({
                    "source_name":file["name"],
                    "status":"STOP_SOURCE_DOWNLOAD_OR_STRUCTURE_ERROR",
                    "error":type(exc).__name__+": "+str(exc)[:160]})
    out["raw_original_records_exported"]=False
    out["independent_ten_chain_units_source_verified"]=False
    out["wind_gated_prediction_admitted"]=False
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,
              default=Path("validation_v17/results/ten_chain_original_metadata_v17.json"))
    args=ap.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,
                                   indent=2,allow_nan=False)+"\n")
    print("TEN_CHAIN_FIGSHARE_METADATA",json.dumps(result,ensure_ascii=False,sort_keys=True))
    print("NO_GPS_OR_WIND_PREDICTIONS_FITTED")


if __name__=="__main__":
    main()
