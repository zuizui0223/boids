#!/usr/bin/env python3
"""v16 source-first eight-flock experiment admission. NO ecological outcomes.

Data from Watts et al. (2016), Zenodo record 4943714. This source is different
from the frozen v8 (Zenodo 5010830) and v15 (Zenodo 21092705) sources.
Only inspect metadata, archive member names and CSV headers/physical row counts.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import posixpath
import re
import tempfile
import urllib.request
import zipfile
from pathlib import Path

RECORD_ID = 4943714
RECORD_API = f"https://zenodo.org/api/records/{RECORD_ID}"
DATA_FILE = "Data.zip"
REQUIRED_MD5 = "ab0950ffebd924950632f727cd487c27"
MAX_DOWNLOAD_BYTES = 400_000_000
MAX_UNCOMPRESSED_BYTES = 3_000_000_000
MAX_SINGLE_MEMBER_BYTES = 300_000_000
MAX_CSV_PHYSICAL_LINES = 2_000_000
EXPECTED_SOURCE_FLOCKS = 8
MIN_RELEASES_PER_FLOCK = 5
MIN_BIRDS_PER_FLOCK = 3
VERSION = "v16-source-structural-only"

# Article repository: examples "01_08_S01_12" denote second token flock,
# SXX the bird, final numeric token release. Unknown names are rejected.
NAME_PATTERN = re.compile(
    r"^(?:\d{2}_)?(?P<flock>\d{2})_(?P<bird>S\d{1,3})_(?P<release>\d{1,3})$",
    re.IGNORECASE,
)


def member_identity(path: str) -> tuple[str,str,int] | None:
    name=posixpath.basename(path.replace("\\","/"))
    if not name.lower().endswith(".csv"):
        return None
    stem=name[:-4]
    match=NAME_PATTERN.fullmatch(stem)
    if not match:
        return None
    return (match.group("flock"),match.group("bird").upper(),
            int(match.group("release")))


def select_file(api_json: dict) -> dict:
    if str(api_json.get("id")) != str(RECORD_ID):
        raise ValueError("Wrong Zenodo record")
    files = api_json.get("files") or []
    if isinstance(files,dict):
        entries=files.get("entries") or {}
        files=list(entries.values()) if isinstance(entries,dict) else []
    if not isinstance(files,list):
        raise ValueError("Unrecognized Zenodo file listing")
    options=[f for f in files if isinstance(f,dict)
             and (f.get("key") or f.get("filename"))==DATA_FILE]
    if len(options)!=1:
        raise ValueError("Absent or duplicated original Data.zip")
    f=options[0]
    md5=str(f.get("checksum") or "")
    size=f.get("size")
    if md5.lower()!="md5:"+REQUIRED_MD5:
        raise ValueError("Published ZIP MD5 mismatched")
    if not isinstance(size,int) or not 10_000_000<=size<=MAX_DOWNLOAD_BYTES:
        raise ValueError("Missing/out-of-range exact source bytes")
    link=(f.get("links") or {}).get("content") or (f.get("links") or {}).get("self")
    if not isinstance(link,str) or not link.startswith("https://zenodo.org/"):
        raise ValueError("Unexpected non-Zenodo data URL")
    return {"url":link,"size":size,"reported_md5":REQUIRED_MD5,
            "name":DATA_FILE}


def get_api(url: str) -> dict:
    req=urllib.request.Request(url,headers={
        "User-Agent":"boids-v16-original-eight-flock-source/1.0",
        "Accept":"application/json"
    })
    with urllib.request.urlopen(req,timeout=35) as response:
        raw=response.read(2_000_001)
    if len(raw)>2_000_000:
        raise ValueError("Unbounded metadata response")
    return json.loads(raw)


def bounded_download(record_file:dict,to:Path) -> dict:
    req=urllib.request.Request(record_file["url"],headers={
        "User-Agent":"boids-v16-original-eight-flock-source/1.0"
    })
    sha,md5,n=hashlib.sha256(),hashlib.md5(),0
    with urllib.request.urlopen(req,timeout=120) as incoming:
        length=incoming.headers.get("Content-Length")
        if length is not None and int(length)!=record_file["size"]:
            raise ValueError("Source declared length changed before transfer")
        with to.open("wb") as output:
            for block in iter(lambda:incoming.read(1_048_576),b""):
                n+=len(block)
                if n>MAX_DOWNLOAD_BYTES:
                    raise ValueError("Download exceeded fixed 400 MB limit")
                output.write(block)
                sha.update(block)
                md5.update(block)
    if n!=record_file["size"] or md5.hexdigest()!=record_file["reported_md5"]:
        raise ValueError("STOP published source size or MD5 mismatch")
    return {"bytes":n,"sha256":sha.hexdigest(),"md5":md5.hexdigest(),
            "matches_published_size_and_md5":True}


def archive_name_gate(members:list[zipfile.ZipInfo]) -> dict:
    names=[m.filename for m in members]
    if len(names)!=len(set(names)):
        raise ValueError("Duplicate ZIP member names")
    for m in members:
        path=m.filename.replace("\\","/")
        if (path.startswith("/") or re.match(r"^[a-zA-Z]:",path) or
                ".." in path.split("/") or (m.flag_bits & 0x1)):
            raise ValueError("Unsafe or encrypted source ZIP")
        if m.file_size>MAX_SINGLE_MEMBER_BYTES:
            raise ValueError("Unbounded individual ZIP member")
    size=sum(m.file_size for m in members)
    if size>MAX_UNCOMPRESSED_BYTES:
        raise ValueError("Uncompressed archive too large")
    return {"members":len(members),"uncompressed_bytes":size,
            "regular_files":sum(not m.is_dir() for m in members)}


def csv_head_and_lines(arc:zipfile.ZipFile,member:zipfile.ZipInfo) -> tuple[tuple[str,...],int]:
    """CSV *header* and physical data line count; never reads numerical fields."""
    with arc.open(member) as inp:
        head=inp.readline(100_001)
        if len(head)>100_000:
            raise ValueError("Oversized/unrecognized CSV header")
        try:
            column_names=next(csv.reader([head.decode("utf-8-sig").strip()]))
        except (UnicodeDecodeError,csv.Error,StopIteration) as exc:
            raise ValueError("Unparseable CSV column header") from exc
        header=tuple(str(c).strip() for c in column_names)
        if not header or len(header)!=len(set(header)):
            raise ValueError("Invalid or duplicate CSV columns")
        lines=0
        for _ in inp:
            lines+=1
            if lines>MAX_CSV_PHYSICAL_LINES:
                raise ValueError("Too many physical rows within single ZIP member")
        return header,lines


def inspect_zip(path:Path) -> dict:
    with zipfile.ZipFile(path) as arc:
        members=arc.infolist()
        summary=archive_name_gate(members)
        csv_files=[m for m in members if not m.is_dir() and
                   m.filename.lower().endswith(".csv")]
        records={}
        unknown=[]
        header_occ=collections.Counter()
        line_counts=[]
        nonempty=0
        for m in csv_files:
            ident=member_identity(m.filename)
            if ident is None:
                unknown.append(m.filename)
                continue
            if ident in records:
                raise ValueError("Duplicate flock-bird-release member")
            header,nlines=csv_head_and_lines(arc,m)
            records[ident]=(header,nlines)
            header_occ[header]+=1
            line_counts.append(nlines)
            nonempty+=int(nlines>=10)
        release_by_flock=collections.defaultdict(set)
        bird_by_flock=collections.defaultdict(set)
        bird_releases=collections.defaultdict(set)
        for (flock,bird,rel),(header,nlines) in records.items():
            if nlines<10:
                continue
            release_by_flock[flock].add(rel)
            bird_by_flock[flock].add(bird)
            bird_releases[(flock,bird)].add(rel)
        group_overview={}
        for flock in sorted(release_by_flock):
            group_overview[flock]={
                "distinct_releases":len(release_by_flock[flock]),
                "min_release_id":min(release_by_flock[flock]),
                "max_release_id":max(release_by_flock[flock]),
                "distinct_bird_ids":len(bird_by_flock[flock]),
                "bird_IDs_seen_in_at_least_5_releases":
                    sum(len(bird_releases[(flock,b)])>=MIN_RELEASES_PER_FLOCK
                        for b in bird_by_flock[flock]),
                "csv_tracks":sum(k[0]==flock for k in records),
            }
        # This gate does not treat a filename release as a sensor clock.
        valid_flocks=[
            f for f,q in group_overview.items()
            if q["distinct_releases"]>=MIN_RELEASES_PER_FLOCK and
               q["bird_IDs_seen_in_at_least_5_releases"]>=MIN_BIRDS_PER_FLOCK
        ]
        names_union=set(x.lower() for columns in header_occ for x in columns)
        time_candidates=[s for s in names_union if any(z in s for z in
                         ("time","date","utc","second","ms","millis"))]
        lat_lon_candidates=[s for s in names_union if any(z in s for z in
                            ("lat","lon","lng","gps","north","east","x","y"))]
        summary.update({
            "status":"STRUCTURAL_PROFILE_ONLY_NO_MOVEMENT_OUTCOMES",
            "csv_files":len(csv_files),
            "filenames_parsed":len(records),
            "unrecognized_csv_filename_count":len(unknown),
            "unrecognized_csv_examples":[posixpath.basename(s) for s in unknown[:10]],
            "headers":[{"columns":list(cols),"files":n}
                       for cols,n in header_occ.most_common(10)],
            "header_variants":len(header_occ),
            "total_csv_physical_data_lines":sum(line_counts),
            "nonempty_csv_tracks":nonempty,
            "minimum_csv_physical_data_lines":min(line_counts) if line_counts else None,
            "maximum_csv_physical_data_lines":max(line_counts) if line_counts else None,
            "flock_release_structure":group_overview,
            "flocks_meeting_repeated_design_gate":len(valid_flocks),
            "observed_time_header_candidates":sorted(time_candidates),
            "observed_position_header_candidates":sorted(lat_lon_candidates),
            "all_8_flocks_admitted_for_future_schema_contract":
                len(valid_flocks)>=EXPECTED_SOURCE_FLOCKS and
                len(unknown)==0 and bool(time_candidates),
            "measured_3D_altitude_admitted":False,
            "fast_social_time_sync_admitted":False,
            "observed_treatment_schedule_verified":False,
            "target_route_scores_computed":False,
            "raw_coordinates_distributed":False,
            "note":"The design gate checks only repeated filenames/headers; original GPS sample-rate and cross-bird clock synchrony are NOT established by these facts.",
        })
        return summary


def run()->dict:
    record=get_api(RECORD_API)
    file=select_file(record)
    met=record.get("metadata") or {}
    out={"study":VERSION,
         "source_record_id":RECORD_ID,
         "source_doi":record.get("doi"),
         "publication_title":met.get("title"),
         "source_license_metadata":met.get("license"),
         "source_url":RECORD_API,
         "record_version":met.get("version"),
         "download_record":{"name":file["name"],
                             "expected_bytes":file["size"],
                             "expected_md5":file["reported_md5"]},
         "status":"SOURCE_ONLY_NO_FORECAST"}
    with tempfile.TemporaryDirectory() as d:
        local=Path(d)/"Data.zip"
        out["archive_integrity"]=bounded_download(file,local)
        out["archive_structure"]=inspect_zip(local)
    return out


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v16/results/independent_eight_flock_preflight_v16.json"))
    a=p.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n",
                     encoding="utf-8")
    print("V16_SOURCE_PROVENANCE",json.dumps({
        "record":d["source_record_id"],"doi":d["source_doi"],
        "license":d["source_license_metadata"],"archive":d["archive_integrity"]},
        sort_keys=True))
    print("V16_STRUCTURAL_GATE",json.dumps(d["archive_structure"],sort_keys=True))
    print("V16_NO_MOVEMENT_FORECAST_EXECUTED")


if __name__=="__main__":
    main()
