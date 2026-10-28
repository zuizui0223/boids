#!/usr/bin/env python3
"""v17-D: 2026 Morford 14-pair source quality and integrity ONLY, no GPS outcomes.

Pinned author GitHub commit + Git blob SHA1, independent SHA256; metadata pair
graph and original ZIP filenames/CSV *first header line* only. No animal
GPS rows, Course, coordinates, timestamps, heading or route-memory forecasts.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import tempfile
import urllib.request
import zipfile
from pathlib import Path

REPO="Morfordjoe/Collective-route-memories-in-homing-pigeons"
REV="8e4f7e48abfa57212c5207c28580003f0ef14210"
PAIR_PATH="CM info.csv"
PAIR_BLOB_SHA1="8c607d535e549fb72f0863b616e28cac24d031f7"
PAIR_BYTES=348
ZIP_PATH="CM_trimmed.zip"
ZIP_BLOB_SHA1="0b1bd66f08c1cac5f8ca582f289d49c43f553bfa"
ZIP_BYTES=21425810
ZIP_CAP=40_000_000
EXPANDED_CAP=900_000_000
SOURCE_DOI="10.1038/s41598-026-39898-2"
MIN_PAIR_COMPONENTS=8


def raw_url(name:str)->str:
    safe="".join("%20" if c==" " else c for c in name)
    return f"https://raw.githubusercontent.com/{REPO}/{REV}/{safe}"


def git_blob_digest(raw:bytes)->str:
    header=f"blob {len(raw)}\0".encode()
    return hashlib.sha1(header+raw).hexdigest()


def download_pinned(name:str,size:int,git_blob_sha1:str,cap:int,destination:Path)->dict:
    if not 1<=size<=cap:
        raise ValueError("Original source declared size outside cap")
    req=urllib.request.Request(raw_url(name),headers={
        "User-Agent":"boids-v17d-author-pinned-original-GPS/1.0"
    })
    sha=hashlib.sha256()
    git_hash=hashlib.sha1()
    git_hash.update(f"blob {size}\0".encode())
    total=0
    with urllib.request.urlopen(req,timeout=120) as stream:
        length=stream.headers.get("Content-Length")
        if length is not None and int(length)!=size:
            raise ValueError("Pinned source content length changed")
        with destination.open("wb") as f:
            while True:
                chunk=stream.read(1048576)
                if not chunk:break
                total+=len(chunk)
                if total>cap:
                    raise ValueError("Download beyond cap")
                f.write(chunk);sha.update(chunk);git_hash.update(chunk)
    if total!=size or git_hash.hexdigest()!=git_blob_sha1:
        raise ValueError("Pinned original Git blob or byte size mismatch")
    return {"name":name,"bytes":total,
            "git_sha1_verified":True,
            "sha256":sha.hexdigest(),
            "source_commit":REV}


def independent_pair_assignments(path:Path)->dict:
    seen={}
    component=[]
    ids=set()
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        rows=csv.DictReader(f)
        if tuple(rows.fieldnames or ())!=(
                "Bird","Partner","Pair_ID","Additional_training_site"):
            raise ValueError("Original pair metadata column schema changed")
        for row in rows:
            b=str(row["Bird"]).strip()
            partner=str(row["Partner"]).strip()
            pair=str(row["Pair_ID"]).strip()
            site=str(row["Additional_training_site"]).strip()
            if (not b or not partner or not pair or b==partner or
                b in ids or partner in ids or pair in seen or
                site not in ("LH","SH")):
                raise ValueError("Duplicate/missing original pair or unsupported site")
            ids.add(b);ids.add(partner)
            seen[pair]=(b,partner,site)
            component.append(sorted((b,partner)))
    if len(seen)!=14 or len(ids)!=28:
        raise ValueError("Original 14-pair/28-unique-bird source roster changed")
    components=sorted(component)
    sites=collections.Counter(x[2] for x in seen.values())
    return {
        "status":"VERIFIED_EXTERNAL_PAIR_ASSIGNMENT_GRAPH",
        "original_published_pair_ID_count":len(seen),
        "distinct_individual_IDs":len(ids),
        "connected_social_components_from_assigned_pairs":len(components),
        "source_pairs_have_no_shared_individuals":True,
        "source_site_counts":dict(sorted(sites.items())),
        "minimum_independent_pair_components_predeclared":MIN_PAIR_COMPONENTS,
        "passes_pair_component_source_gate":len(components)>=MIN_PAIR_COMPONENTS,
        "pair_component_IDs":components,
        "individual_GPS_rows_analyzed":0,
    }


def masked_header(row:bytes)->dict:
    txt=row.decode("utf-8-sig",errors="replace").strip("\r\n")
    words=[x.strip().strip('"') for x in txt.split(",")]
    valid=(2<=len(words)<=150 and all(
        re.fullmatch(r"[A-Za-z_][A-Za-z0-9_. ():/+\-%]*",v)
        for v in words))
    return {"status":"ORIGINAL_HEADER_ONLY" if valid else "MISSING_OR_NUMERIC_FIRST_RECORD",
            "columns":words if valid else None,
            "field_count":len(words)}


def archive_inventory(path:Path)->dict:
    with zipfile.ZipFile(path,"r") as arc:
        entries=arc.infolist()
        names=[e.filename for e in entries]
        if len(names)!=len(set(names)):
            raise ValueError("Duplicate original ZIP entries")
        for entry in entries:
            name=entry.filename.replace("\\","/")
            if name.startswith("/") or ".." in name.split("/") or entry.flag_bits&1:
                raise ValueError("Unsafe original ZIP entry")
        expanded=sum(e.file_size for e in entries)
        if expanded>EXPANDED_CAP:
            raise ValueError("Source archive would exceed expanded cap")
        files=sorted((e for e in entries if not e.is_dir()),
                     key=lambda e:e.filename)
        ext=collections.Counter(Path(e.filename).suffix.lower() or "none" for e in files)
        csvs=[e for e in files if e.filename.lower().endswith(".csv") and
              not Path(e.filename).name.startswith("._")]
        headers=[]
        for idx in sorted(set(round(i*(len(csvs)-1)/max(1,min(len(csvs),32)-1))
                           for i in range(min(len(csvs),32)))):
            e=csvs[idx]
            with arc.open(e) as f:
                first=f.readline(65537)
            if len(first)>65536:
                raise ValueError("Huge first CSV header")
            headers.append({"name":e.filename,
                            "header":masked_header(first)})
        cols={tuple(h["header"]["columns"] or [])
              for h in headers if h["header"]["status"]=="ORIGINAL_HEADER_ONLY"}
        return {
            "status":"ORIGINAL_ZIP_FILENAME_AND_HEADER_PROFILE_ONLY",
            "regular_files":len(files),
            "physical_csv_files":len(csvs),
            "source_zip_uncompressed_bytes":expanded,
            "file_extensions":dict(sorted(ext.items())),
            "first_30_source_filename_examples":[e.filename for e in files[:30]],
            "lexically_even_csv_header_samples":headers,
            "header_variants":len(cols),
            "GPS_DT_column_listed":any("DT" in c for c in cols),
            "GPS_lat_lon_course_columns_listed":any(
                any("LAT" in k.upper() or k.lower() in ("latitude","lat")
                    for k in c)
                and any("LON" in k.upper() or k.lower() in ("longitude","lon")
                        for k in c)
                for c in cols),
            "raw_positions_or_courses_read":False,
            "observed_route_memory_scores_computed":False
        }


def run()->dict:
    with tempfile.TemporaryDirectory() as tmp:
        a=Path(tmp)/"info.csv"
        b=Path(tmp)/"source.zip"
        src1=download_pinned(PAIR_PATH,PAIR_BYTES,PAIR_BLOB_SHA1,100000,a)
        src2=download_pinned(ZIP_PATH,ZIP_BYTES,ZIP_BLOB_SHA1,ZIP_CAP,b)
        pair=independent_pair_assignments(a)
        archive=archive_inventory(b)
    return {"study":"v17D-source-first-2026-14-independent-pairs",
            "status":"SOURCE_ONLY_NO_ANIMAL_MEMORY_PREDICTION",
            "author_repository":REPO,
            "paper_DOI":SOURCE_DOI,
            "original_author_commit":REV,
            "pair_ledger_integrity":src1,
            "GPS_ZIP_integrity":src2,
            "assigned_pair_graph":pair,
            "original_GPS_archive_format":archive,
            "source_raw_file_license_status":"not_verified_in_repository",
            "weather_with_original_timestamp_verified":False,
            "independent_GPS_timestamp_accuracy_verified":False,
            "no_older_v15_v16_v17_animal_outcomes_reopened":True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
        "validation_v17/results/2026_fourteen_pair_source_audit.json"))
    a=parser.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V17D_ORIGINAL_SOURCE",json.dumps({
        "pairs":d["pair_ledger_integrity"],
        "gps":d["GPS_ZIP_integrity"]},sort_keys=True))
    print("V17D_PUBLISHED_PAIR_GRAPH",json.dumps(d["assigned_pair_graph"],sort_keys=True))
    print("V17D_ZIP_SOURCE_STRUCTURE",json.dumps(d["original_GPS_archive_format"],sort_keys=True))
    print("V17D_NO_ANIMAL_PREDICTION_FITTED")


if __name__=="__main__":
    main()
