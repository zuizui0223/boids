#!/usr/bin/env python3
"""v31-A: original Zenodo source-only manifest and ID/time structure.
Never read numeric GPS coordinates, altitude, speed or movement responses.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import tempfile
import urllib.request

RECORDS={
    "O_SCHIERMONNIKOOG": {"record":10053970,"years":list(range(2008,2015))},
    "O_WESTERSCHELDE": {"record":10053702,"years":[2018,2019,2020]},
}
MAX_FILE_BYTES=80_000_000
MAX_TOTAL_BYTES=100_000_000
MAX_ROWS_PER_GZIP=2_000_000
MAX_TOTAL_ROWS=3_000_000
MAX_METADATA_BYTES=2_000_000
ID_CANDIDATES=("individual-local-identifier","individual-id","individual_id","individual-local-id","animal-id","animal_id")
TIME_CANDIDATES=("timestamp",)
AGENT="boids-v31-independent-oystercatcher-source-only/1.0"
def read_api(record):
    url=f"https://zenodo.org/api/records/{record}"
    req=urllib.request.Request(url, headers={"Accept":"application/json","User-Agent":AGENT})
    with urllib.request.urlopen(req,timeout=45) as response:
        raw=response.read(MAX_METADATA_BYTES+1)
    if len(raw)>MAX_METADATA_BYTES: raise ValueError("Metadata oversized")
    obj=json.loads(raw)
    if obj.get("id")!=record: raise ValueError("Wrong original published record")
    return obj

def select_gps_files(obj, label, years):
    files=obj.get("files") or []
    if isinstance(files,dict):
        files=list((files.get("entries") or {}).values())
    if not isinstance(files,list):raise ValueError("Unexpected original file manifest")
    selected={}
    for f in files:
        name=f.get("key") or f.get("filename") or ""
        match=re.fullmatch(re.escape(label)+r"-gps-(\d{4})\.csv\.gz",name)
        if not match: continue
        year=int(match.group(1))
        if year not in years or year in selected:
            raise ValueError("Unexpected source year or duplicate GPS gzip")
        size=f.get("size")
        md5=f.get("checksum","")
        url=(f.get("links") or {}).get("content") or (f.get("links") or {}).get("self")
        if not isinstance(size,int) or not 100<=size<=MAX_FILE_BYTES:
            raise ValueError("Original gzip size over registered cap or invalid")
        if not isinstance(md5,str) or not re.fullmatch(r"md5:[0-9a-fA-F]{32}",md5):
            raise ValueError("Missing original provider MD5")
        if not isinstance(url,str) or not url.startswith("https://zenodo.org/"):
            raise ValueError("Original file download must use Zenodo")
        selected[year]={"name":name,"year":year,"size":size,"md5":md5[4:].lower(),"url":url}
    if sorted(selected)!=sorted(years):raise ValueError("Not every frozen GPS year available")
    return [selected[y] for y in sorted(years)]

def timestamp(s):
    if not s or not s.strip(): raise ValueError("Blank UTC time")
    v=s.strip().replace("Z","+00:00")
    out=dt.datetime.fromisoformat(v.replace(" ","T"))
    if out.tzinfo is not None:
        if out.utcoffset()!=dt.timedelta(0):
            raise ValueError("Not UTC timestamp")
        out=out.replace(tzinfo=None)
    return out

def structure_only(gzip_path, label):
    with gzip.open(gzip_path,"rt",encoding="utf-8-sig",errors="strict",newline="") as f:
        reader=csv.DictReader(f)
        names=tuple(reader.fieldnames or ())
        id_field=next((v for v in ID_CANDIDATES if v in names),None)
        time_field=next((v for v in TIME_CANDIDATES if v in names),None)
        # Headers alone may be inspected. Nothing resembling lat/lon values is touched.
        if id_field is None or time_field is None:
            raise ValueError("No trusted original bird ID / UTC columns; source-only STOP: "+repr(names))
        ids=collections.defaultdict(set)
        duplicates=set()
        dup_count=0
        rows=bad_id=bad_time=0
        for row in reader:
            rows+=1
            if rows>MAX_ROWS_PER_GZIP:raise ValueError("Decompressed CSV row cap exceeded")
            bird=(row.get(id_field) or "").strip()
            if not bird:
                bad_id+=1
                continue
            try:
                stamp=timestamp(row.get(time_field) or "")
            except (TypeError,ValueError):
                bad_time+=1
                continue
            key=(bird,stamp)
            if key in duplicates:dup_count+=1
            else:duplicates.add(key)
            ids[bird].add(stamp.date())
    return {"header_columns":list(names),"id_column":id_field,"UTC_column":time_field,
            "original_physical_rows":rows,"nonempty_original_birds":len(ids),
            "birds_with_3plus_distinct_UTC_days":sum(len(ds)>=3 for ds in ids.values()),
            "birds_with_7plus_distinct_UTC_days":sum(len(ds)>=7 for ds in ids.values()),
            "birds_with_14plus_distinct_UTC_days":sum(len(ds)>=14 for ds in ids.values()),
            "bird_UTC_duplicate_rows":dup_count,"rows_with_blank_bird_ID":bad_id,
            "rows_with_bad_UTC_time":bad_time,"any_location_or_movement_value_read":False}

def fetch_original_file(spec,path):
    req=urllib.request.Request(spec["url"],headers={"User-Agent":AGENT})
    md5=hashlib.md5()
    sha=hashlib.sha256()
    size=0
    with urllib.request.urlopen(req,timeout=120) as response, path.open("wb") as out:
        for chunk in iter(lambda:response.read(1048576),b""):
            size+=len(chunk)
            if size>MAX_FILE_BYTES:raise ValueError("Original file cap exceeded")
            md5.update(chunk);sha.update(chunk);out.write(chunk)
    if size!=spec["size"] or md5.hexdigest()!=spec["md5"]:
        raise ValueError("Provider original gzip checksum/bytes mismatch")
    return {"original_gzip_name":spec["name"],"source_year":spec["year"],
            "bytes":size,"provider_md5":md5.hexdigest(),"original_sha256":sha.hexdigest(),
            "published_md5_bytes_verified":True}

def run():
    data={"status":"SOURCE_ONLY_NOT_ADMITTED","records":{},"no_animal_location_or_response_opened":True}
    total_bytes=total_rows=0
    for label,cfg in RECORDS.items():
        rec=read_api(cfg["record"])
        specs=select_gps_files(rec,label,cfg["years"])
        total_bytes+=sum(f["size"] for f in specs)
        if total_bytes>MAX_TOTAL_BYTES:raise ValueError("Total original compressed GPS cap exceeded")
        rows=[]
        with tempfile.TemporaryDirectory() as folder:
            for f in specs:
                path=Path(folder)/f["name"]
                receipt=fetch_original_file(f,path)
                structure=structure_only(path,label)
                total_rows+=structure["original_physical_rows"]
                if total_rows>MAX_TOTAL_ROWS:raise ValueError("Total source-only row cap exceeded")
                rows.append({"file":receipt,"ID_and_UTC_only":structure})
        meta=rec.get("metadata") or {}
        license_value=meta.get("license")
        data["records"][label]={"original_record_id":cfg["record"],
           "source_doi":rec.get("doi"),"original_zenodo_version":meta.get("version"),
           "license":license_value if isinstance(license_value,str) else str(license_value),
           "source_only_years":[f["year"] for f in specs],"source_only_files":rows}
    data["total_original_compressed_gps_bytes"]=total_bytes
    data["total_original_GPS_rows"]=total_rows
    data["status"]="SOURCE_ONLY_TWO_ORIGINAL_ZENODO_RECORDS_VERIFIED"
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v31/results/oystercatcher_source_only_v31.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V31_SOURCE_STATUS",result["status"])
    print("V31_SOURCE_ONLY_AGGREGATE",json.dumps(result,sort_keys=True,separators=(",",":")))
    print("V31_NO_GPS_OUTCOME_ANALYZED")

if __name__=="__main__": main()
