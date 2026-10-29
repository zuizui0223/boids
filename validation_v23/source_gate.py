#!/usr/bin/env python3
"""v23-A: exact Zenodo seven-taxon duck source integrity and ID/time structure.

Read only original source filename, row ID, study, species and UTC timestamp.
DO NOT inspect animal latitude, longitude, GPS speed, direction or any
meteorology; Stage A cannot establish ecological predictor effects.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path

RECORD_ID=16940654
API=f"https://zenodo.org/api/records/{RECORD_ID}"
SOURCE_NAME="250823_LNU_dabbling_ducks_hourly.csv"
ORIGINAL_PROVIDER_MD5="1972d0ef08b83c2b88a169ba07bb48b3"
CAP=120_000_000
METADATA_CAP=2_000_000
ROW_CAP=2_000_000
SOURCE_COLS=(
    "study.name","study.ID","individual.id",
    "individual.taxon.canonical.name","timestamp",
    "location.long","location.lat","gps.hdop","ground.speed")
SOURCE_ID=("study.ID","individual.id")
AGENT="boids-v23-independent-dabbling-duck-source-only/1.0"

def fetch_metadata()->dict:
    req=urllib.request.Request(API,headers={"User-Agent":AGENT,
                                             "Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=40) as res:
        raw=res.read(METADATA_CAP+1)
    if len(raw)>METADATA_CAP:raise ValueError("Provider Zenodo metadata too large")
    record=json.loads(raw)
    if str(record.get("id"))!=str(RECORD_ID):
        raise ValueError("Unexpected provider Zenodo source record")
    return record

def select_original(rec:dict)->dict:
    files=rec.get("files") or []
    if isinstance(files,dict):files=list((files.get("entries") or {}).values())
    if not isinstance(files,list):raise ValueError("Unknown Zenodo file manifest")
    matches=[x for x in files if (x.get("key") or x.get("filename"))==SOURCE_NAME]
    if len(matches)!=1:raise ValueError("Original CSV absent or duplicated")
    f=matches[0]
    size=f.get("size")
    md5=str(f.get("checksum") or "").lower()
    if not isinstance(size,int) or not 100_000<=size<=CAP:
        raise ValueError("Source bytes absent/outside source cap")
    if md5!="md5:"+ORIGINAL_PROVIDER_MD5:
        raise ValueError("Original provider MD5 changed")
    urls=f.get("links") or {}
    url=urls.get("content") or urls.get("self")
    if not isinstance(url,str) or not url.startswith("https://zenodo.org/"):
        raise ValueError("Original source download URL not Zenodo")
    return {"name":SOURCE_NAME,"size":size,"md5":ORIGINAL_PROVIDER_MD5,
            "url":url}

def get_original_file(spec:dict,path:Path)->dict:
    req=urllib.request.Request(spec["url"],headers={"User-Agent":AGENT})
    md5=hashlib.md5();sha=hashlib.sha256();count=0
    with urllib.request.urlopen(req,timeout=125) as response:
        length=response.headers.get("Content-Length")
        if length and int(length)!=spec["size"]:
            raise ValueError("Source claimed Content-Length changed")
        with path.open("wb") as output:
            for b in iter(lambda:response.read(1048576),b""):
                count+=len(b)
                if count>CAP:raise ValueError("Source download > cap")
                output.write(b);sha.update(b);md5.update(b)
    if count!=spec["size"] or md5.hexdigest()!=ORIGINAL_PROVIDER_MD5:
        raise ValueError("Original published provider size/checksum disagrees")
    return {"status":"ORIGINAL_BYTES_VERIFIED","bytes":count,
            "provider_md5":md5.hexdigest(),"original_sha256":sha.hexdigest(),
            "provider_md5_and_exact_bytes_match":True}

def parse_utc(s:str)->dt.datetime:
    return dt.datetime.strptime(str(s).strip(),"%Y-%m-%d %H:%M:%S")

def inspect_source_ID_date_only(path:Path)->dict:
    seen=set()
    bird_days=collections.defaultdict(set)
    bird_months=collections.defaultdict(set)
    bird_species={}
    bird_studies={}
    study_rows=collections.Counter()
    species_rows=collections.Counter()
    year_rows=collections.Counter()
    species_set=set()
    bad=blank=duplicate=0
    rows=0
    with path.open("r",encoding="utf-8-sig",errors="strict",newline="") as src:
        reader=csv.DictReader(src)
        fields=tuple(reader.fieldnames or [])
        if not set(SOURCE_COLS).issubset(fields):
            raise ValueError("Original source expected GPS/UTC/ID columns not present")
        for row in reader:
            rows+=1
            if rows>ROW_CAP:raise ValueError("Unknown original source > row cap")
            i=row.get("individual.id")
            study=row.get("study.ID")
            stamp=row.get("timestamp")
            taxon=row.get("individual.taxon.canonical.name")
            studyname=row.get("study.name")
            if not i or not study or not taxon or not stamp:
                blank+=1
                continue
            try:t=parse_utc(stamp)
            except (ValueError,TypeError):bad+=1;continue
            key=(str(study).strip(),str(i).strip())
            obs=(key,t)
            if obs in seen:
                duplicate+=1
                continue
            seen.add(obs)
            if key in bird_species and bird_species[key]!=taxon:
                raise ValueError("Source individual/study has changing species")
            bird_species[key]=taxon
            bird_studies[key]=str(studyname).strip()
            bird_days[key].add(t.date())
            bird_months[key].add((t.year,t.month))
            study_rows[bird_studies[key]]+=1
            species_rows[taxon]+=1
            year_rows[str(t.year)]+=1
            species_set.add(taxon)
    birds_by_study=collections.Counter()
    for key in bird_days:
        birds_by_study[bird_studies[key]]+=1
    return {
        "status":"ID_DATE_SPECIES_ONLY_NO_GPS_OUTCOME",
        "source_header":list(fields),
        "original_physical_data_rows":rows,
        "blank_required_ID_or_stamp_rows":blank,
        "unparseable_UTC_rows":bad,
        "duplicate_same_individual_UTC_measurements":duplicate,
        "unique_individuals_within_source_study_ID":len(bird_days),
        "distinct_original_study_IDs":len({k[0] for k in bird_days}),
        "distinct_taxa":len(species_set),
        "taxon_GPS_fix_counts":dict(sorted(species_rows.items())),
        "source_study_GPS_fix_counts":dict(sorted(study_rows.items())),
        "source_study_individual_counts":dict(sorted(birds_by_study.items())),
        "year_fix_counts":dict(sorted(year_rows.items())),
        "individuals_at_least_7_distinct_UTC_days":sum(len(v)>=7 for v in bird_days.values()),
        "individuals_at_least_14_distinct_UTC_days":sum(len(v)>=14 for v in bird_days.values()),
        "individuals_at_least_30_distinct_UTC_days":sum(len(v)>=30 for v in bird_days.values()),
        "individuals_in_at_least_2_different_months":sum(len(v)>=2 for v in bird_months.values()),
        "min_distinct_UTC_dates_per_individual":min(map(len,bird_days.values())) if bird_days else 0,
        "max_distinct_UTC_dates_per_individual":max(map(len,bird_days.values())) if bird_days else 0,
        "original_individuals_with_spatial_GPS_outcomes_scored":0,
        "actual_weather_or_resource_covariates_verified_in_this_source":False,
        "precommitted_minimum_individual_history_passes":
            sum(len(v)>=14 for v in bird_days.values())>=20,
        "actual_group_assigned_social_network_available":False,
        "source_GPS_latitude_longitude_or_speed_read":False,
        "no_species_or_flight_course_effects_computed":True
    }

def run():
    meta=fetch_metadata()
    spec=select_original(meta)
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/SOURCE_NAME
        integrity=get_original_file(spec,path)
        structure=inspect_source_ID_date_only(path)
    metadata=meta.get("metadata") or {}
    return {
        "study":"v23-seven-duck-taxa-independent-original-hourly-GPS-source-admission",
        "source_record_id":RECORD_ID,
        "source_doi":meta.get("doi"),
        "title":metadata.get("title"),
        "provider_license":metadata.get("license"),
        "provider_published_at":meta.get("created"),
        "provider_manifest":{"original_filename":SOURCE_NAME,
                             "reported_bytes":spec["size"],
                             "reported_md5":spec["md5"]},
        "original_source_integrity":integrity,
        "original_ID_and_UTC_structure":structure,
        "status":("SOURCE_GPS_ID_DAY_ADMITTED_NO_ENVIRONMENT"
                  if structure["precommitted_minimum_individual_history_passes"]
                  else "NOT_ADMITTED_INSUFFICIENT_INDEPENDENT_INDIVIDUAL_DAYS"),
        "target_movement_trajectory_observations_scored":0,
        "independent_meteorological_data_not_acquired":True,
        "no_v13_v22_frozen_outcomes_modified":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,
                   default=Path("validation_v23/results/independent_duck_gps_source_v23.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V23_GPS_SOURCE",json.dumps(result["original_source_integrity"],sort_keys=True))
    print("V23_GPS_ID_TIME_ONLY",json.dumps(result["original_ID_and_UTC_structure"],sort_keys=True))
    print("V23_SOURCE_STATUS",result["status"])
    print("V23_NO_GPS_FORECAST_OR_ENVIRONMENT_EFFECT_FITTED")
if __name__=="__main__":
    main()
