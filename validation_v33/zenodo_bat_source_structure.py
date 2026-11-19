#!/usr/bin/env python3
"""v33 original Zenodo bat acoustic event SOURCE ONLY structure and co-use feasibility."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import io
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

URL="https://zenodo.org/records/10149959/files/data_bats_barre%20et%20al%202023.csv?download=1"
SOURCE_DOI="10.5281/zenodo.10149959"
FILE_MD5="60ce63b79fd8a5b9bc4771997de97839"
MAX_BYTES=8_000_000
OUTPUT=Path("validation_v33/results/zenodo_original_bat_event_structure_v33.json")
REQ=("id_site","typeSite","date","time","Trajectory_identifier",
    "Species_corrected","guild","x (m)","y (m)","z (m)",
    "Speed","Imprecision","buzz_proba","mean_buzz_proba")


def original_source(getter=None):
    if getter is None:
        def getter(url):
            r=urllib.request.Request(url,headers={
                "User-Agent":"Mozilla/5.0 (boids-source-audit/1.0)",
                "Accept":"text/csv,text/plain,application/octet-stream,*/*;q=0.1"})
            with urllib.request.urlopen(r,timeout=30) as res:
                return res.status,res.headers.get("content-type",""),res.read(MAX_BYTES+1)
    try:
        status,typ,data=getter(URL)
    except urllib.error.HTTPError as exc:
        return {"status":"HTTP_SOURCE_STOP","http":exc.code}
    except (urllib.error.URLError,OSError,TimeoutError) as exc:
        return {"status":"TRANSPORT_SOURCE_STOP","error_type":type(exc).__name__}
    if status!=200 or len(data)>MAX_BYTES:
        return {"status":"SOURCE_UNEXPECTED_HTTP_OR_SIZE","http":status,"bytes_received":len(data)}
    md5=hashlib.md5(data).hexdigest()
    sha=hashlib.sha256(data).hexdigest()
    if md5!=FILE_MD5:
        return {"status":"SOURCE_MD5_MISMATCH_STOP","bytes_received":len(data),
                "actual_md5":md5,"actual_sha256":sha,"expected_md5":FILE_MD5}
    try: text=data.decode("utf-8-sig")
    except UnicodeDecodeError: text=data.decode("latin-1")
    header=next(csv.reader(io.StringIO(text),delimiter=";"))
    if not all(k in header for k in REQ):
        return {"status":"SOURCE_SCHEMA_STOP","bytes_received":len(data),
                "actual_md5":md5,"actual_sha256":sha,"source_header":header[:50]}
    return {"status":"SOURCE_BYTES_PINNED","bytes_received":len(data),
            "original_md5":md5,"original_sha256":sha,
            "original_header":header,"text":text}


def parse_timestamp(date_s,time_s):
    dt=(date_s or "").strip().replace(":","-")
    tm=(time_s or "").strip()
    if not re.fullmatch(r"\d{4}-\d\d-\d\d",dt):
        return None
    try:
        return datetime.fromisoformat(dt+"T"+tm)
    except ValueError:
        return None


def analyze_structure(text):
    """Visits only structural columns; never evaluates XYZ, speed or buzz numbers."""
    reader=csv.DictReader(io.StringIO(text),delimiter=";")
    n=0
    episodes=defaultdict(list)
    sites=Counter();stem=Counter(); species=Counter();guilds=Counter()
    source_type=Counter();dates=Counter();times_missing=0
    per_session=defaultdict(set);precision=Counter()
    for row in reader:
        n+=1
        sid=(row["id_site"] or "").strip()
        date=(row["date"] or "").strip()
        ty=(row["typeSite"] or "").strip()
        sp=(row["Species_corrected"] or "").strip()
        gl=(row["guild"] or "").strip()
        eid=(row["Trajectory_identifier"] or "").strip()
        # Nominal locality only; not asserted to be actual unique physical place.
        locstem=re.sub(r"^\d{8}_","",sid)
        ts=parse_timestamp(date,row["time"])
        sites[sid]+=1;stem[locstem]+=1;species[sp]+=1
        guilds[gl]+=1;source_type[ty]+=1;dates[date]+=1
        precision["timestamp_string_fractional"]+=int("." in (row["time"] or "").split("+")[0])
        precision["timestamp_string_no_fraction"]+=int("." not in (row["time"] or "").split("+")[0])
        if ts is None:times_missing+=1
        else:
            key=(sid,date,ty,eid,sp)
            episodes[key].append(ts)
            per_session[(sid,date,ty)].add(key)

    durations={}
    repeated_time_n=0
    for key, ts in episodes.items():
        unique=set(ts)
        repeated_time_n+=len(ts)-len(unique)
        durations[key]=(min(ts),max(ts),len(ts),len(unique))

    overlaps=Counter()
    overlap_n=0;overlap_intersp=0;exact_shared_second=0;contexts_with_overlap=0
    for ses, ep_keys in per_session.items():
        valid=[(k,durations[k]) for k in ep_keys if k in durations]
        localpairs=0
        for a in range(len(valid)):
            k1,(b1,e1,n1,u1)=valid[a]
            for b in range(a+1,len(valid)):
                k2,(b2,e2,n2,u2)=valid[b]
                if max(b1,b2)>min(e1,e2):
                    continue
                overlap_n+=1;localpairs+=1
                if k1[-1]!=k2[-1]:overlap_intersp+=1
                if b1==b2 or e1==e2:exact_shared_second+=1
        if localpairs: contexts_with_overlap+=1
        if localpairs:overlaps[str(ses[2])]+=localpairs

    checks={
        "md5_matches_published_source":True,  # Verified before this function
        "at_least_1000_source_rows":n>=1000,
        "at_least_8_nominal_locality_stems":len(stem)>=8,
        "at_least_4_species":len(species)>=4,
        "at_least_10_distinct_trajectory_interval_overlap_pairs":overlap_n>=10,
        "overlap_pairs_across_at_least_3_recording_site_sessions":contexts_with_overlap>=3,
    }
    return {
        "source_structure_status":"FEASIBLE_PROXY_ONLY" if all(checks.values()) else "SOURCE_FEASIBILITY_STOP",
        "source_feasibility_fixed_conditions":checks,
        "source_raw_event_row_count":n,
        "source_trajectory_key_count":len(episodes),
        "source_recording_session_count":len(per_session),
        "source_id_site_n":len(sites),
        "date_stripped_nominal_locality_n":len(stem),
        "source_species_labels_n":len(species),"source_guild_labels_n":len(guilds),
        "source_date_labels_n":len(dates),
        "source_type_site_counts":dict(source_type),
        "source_species_label_counts":dict(species),
        "raw_rows_with_unparseable_time_strings_n":times_missing,
        "raw_event_rows_repeating_timestamp_within_trajectory_n":repeated_time_n,
        "raw_time_string_precision":dict(precision),
        "possible_different_trajectory_interval_overlap_pairs":overlap_n,
        "possible_inter_species_trajectory_interval_overlap_pairs":overlap_intersp,
        "possible_overlap_pairs_sharing_endpoint_second":exact_shared_second,
        "site_date_type_recordings_with_possible_overlap":contexts_with_overlap,
        "possible_interval_overlaps_by_source_type":dict(overlaps),
        "3d_coordinates_speed_buzz_numeric_values_read":False,
        "not_independent_2025_Delmotte_dataset":True,
        "cannot_identify_independent_bat_individuals":True,
        "not_an_original_synchronised_multi_animal_tracking_record":True,
        "social_interaction_or_continuous_time_overlap_established":False,
        "no_biological_effect_or_prediction_computed":True,
    }


def run(getter=None):
    source=original_source(getter)
    result={
        "programme":"v33_original_Zenodo_bat_acoustic_flight_source_structure",
        "source_doi":SOURCE_DOI,"source_url":URL,"expected_published_md5":FILE_MD5,
        "original_access_status":source["status"],
        "3d_coordinates_speed_buzz_numeric_values_read":False,
        "no_biological_effect_or_prediction_computed":True,
        "source_is_not_independent_of_Delmotte_2025":True,
    }
    if source["status"]!="SOURCE_BYTES_PINNED":
        result["status"]="SOURCE_ACCESS_OR_INTEGRITY_STOP"
        result["source_error_receipt"]={k:v for k,v in source.items() if k!="text"}
        return result
    result.update({
        "source_bytes":source["bytes_received"],"source_verified_md5":source["original_md5"],
        "source_derived_sha256":source["original_sha256"],
        "source_headers":source["original_header"]})
    result.update(analyze_structure(source["text"]))
    result["status"]=result["source_structure_status"]
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=OUTPUT)
    args=p.parse_args()
    data=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    keys=["status","original_access_status","source_bytes","source_verified_md5",
          "source_raw_event_row_count","source_trajectory_key_count","source_recording_session_count",
          "source_species_labels_n","date_stripped_nominal_locality_n",
          "possible_different_trajectory_interval_overlap_pairs","site_date_type_recordings_with_possible_overlap",
          "source_feasibility_fixed_conditions"]
    print("V33_ORIGINAL_ZENODO_SOURCE_ONLY="+json.dumps({k:data.get(k) for k in keys},sort_keys=True))
    assert data["3d_coordinates_speed_buzz_numeric_values_read"] is False
    assert data["no_biological_effect_or_prediction_computed"] is True


if __name__=="__main__":
    main()
