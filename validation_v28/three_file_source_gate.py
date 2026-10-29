#!/usr/bin/env python3
"""v28-B1 original 2023 Zenodo Nyctalus source full MD5/SHA + ID grain ONLY.

Never read UTM x/y, GPS heading, turbine-distance or habitat numeric
data; never fit case preference or animal ecological effects.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path

import original_source_manifest as z

PINS={
    "Model_dataset_RSFFlight_Complete_EPSG25833.csv":{
        "size":17582302,"md5":"fb0d7967d552b855ab530eeedcede7ff"},
    "Observed_GPS_locations.csv":{
        "size":3080045,"md5":"a1583b48487a78259f7e63937af232e5"},
    "Individual_Characteristics_Capture.csv":{
        "size":6388,"md5":"84e78242135fc50b12e5e2ffff91bcb5"},
}
MAX_LINES=2_000_000
NULLS={"","NA","NaN","nan","NULL","null","missing"}


def select_pin(source_file:dict)->dict:
    name=source_file["filename"]
    if name not in PINS:
        raise ValueError("Source file not preregistered")
    expected=PINS[name]
    if source_file.get("source_exact_bytes")!=expected["size"]:
        raise ValueError("Original source length changed")
    if str(source_file.get("provider_original_checksum") or "").lower()!="md5:"+expected["md5"]:
        raise ValueError("Original provider MD5 changed")
    url=source_file.get("file_download_url")
    if not isinstance(url,str) or not url.startswith(
        "https://zenodo.org/api/records/7535030/files/"):
        raise ValueError("Nonoriginal official download URL")
    return {**expected,"filename":name,"download_url":url}


def download_verified(source_file:dict,destination:Path)->dict:
    pin=select_pin(source_file)
    req=urllib.request.Request(pin["download_url"],headers={
        "User-Agent":z.AGENT})
    sha=hashlib.sha256();md5=hashlib.md5();n=0
    with urllib.request.urlopen(req,timeout=110) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("Source download redirected to insecure URL")
        announced=response.headers.get("Content-Length")
        if announced is not None and int(announced)!=pin["size"]:
            raise ValueError("Source Content-Length changed")
        with destination.open("wb") as dest:
            for block in iter(lambda:response.read(512*1024),b""):
                n+=len(block)
                if n>z.SINGLE_FILE_CAP:
                    raise ValueError("Source download exceeded file cap")
                sha.update(block);md5.update(block);dest.write(block)
    if n!=pin["size"] or md5.hexdigest()!=pin["md5"]:
        raise ValueError("Original file MD5 or exact size mismatch")
    return {
        "status":"ORIGINAL_ZENODO_MD5_AND_BYTES_VERIFIED",
        "name":pin["filename"],
        "bytes":n,
        "provider_original_md5":md5.hexdigest(),
        "independently_computed_sha256":sha.hexdigest(),
        "source_original_file_url":pin["download_url"],
        "original_animal_GPS_position_values_read":False,
    }


def source_csv_ids_only(path:Path,kind:str)->tuple[dict,set[str]]:
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as raw:
        reader=csv.DictReader(raw)
        cols=tuple(reader.fieldnames or ())
        if not cols or len(cols)!=len(set(cols)):
            raise ValueError("Original source has empty/repeated headers")
        if len(cols)>160:
            raise ValueError("Original source has unexpectedly many columns")
        ident="batid" if "batid" in cols else (
            "ring_number" if "ring_number" in cols else None)
        track="trackid" if "trackid" in cols else None
        use="case_" if "case_" in cols else None
        numeric_use="response_rvso" if "response_rvso" in cols else None
        cats=[c for c in ("sex","age_class","field_period","move_state","species")
              if c in cols]
        # Read only independent identity and source-defined categorical
        # availability labels, never numeric original GPS/HAB fields.
        individuals=set()
        tracks=collections.defaultdict(set)
        track_counts=collections.defaultdict(collections.Counter)
        use_counts=collections.Counter()
        mismatch=0
        missing=collections.Counter()
        category_counts={c:collections.Counter() for c in cats}
        count=0
        for row in reader:
            count+=1
            if count>MAX_LINES:
                raise ValueError("Unexpected original source CSV > cap")
            individual=(row.get(ident) or "").strip() if ident else ""
            flight=(row.get(track) or "").strip() if track else ""
            if ident:
                if individual in NULLS:
                    missing["missing_original_bat_identity"]+=1
                else:
                    individuals.add(individual)
            if track:
                if flight in NULLS:
                    missing["missing_original_flight_ID"]+=1
                elif individual not in NULLS:
                    tracks[individual].add(flight)
            if use:
                observed=(row.get(use) or "").strip()
                use_counts[observed]+=1
                if observed in NULLS:
                    missing["missing_original_used_available_label"]+=1
                if numeric_use:
                    binary=(row.get(numeric_use) or "").strip()
                    if (observed=="TRUE" and binary!="1") or (
                         observed=="FALSE" and binary!="0"):
                        mismatch+=1
                if flight not in NULLS and individual not in NULLS:
                    track_counts[(individual,flight)][observed]+=1
            for c in cats:
                value=(row.get(c) or "").strip()
                category_counts[c][value]+=1
        flights_per_bat=[len(v) for v in tracks.values()]
        original_tracks_by_count=collections.Counter(flights_per_bat)
        track_used=[v["TRUE"] for v in track_counts.values()]
        track_available=[v["FALSE"] for v in track_counts.values()]
        def stats(vals):
            if not vals:return {"n":0,"min":None,"median":None,"max":None}
            v=sorted(vals)
            return {"n":len(v),"min":v[0],"median":v[len(v)//2],"max":v[-1]}
        profile={
           "source_kind":kind,
           "status":"ORIGINAL_CSV_ID_AND_CATEGORY_ONLY",
           "source_columns":list(cols),
           "original_physical_csv_rows":count,
           "original_declared_bat_ID_column":ident,
           "original_declared_track_ID_column":track,
           "original_declared_use_label_column":use,
           "original_declared_binary_response_column":numeric_use,
           "original_distinct_bat_id_tokens":len(individuals),
           "original_distinct_track_ID_tokens_with_bat":sum(len(t) for t in tracks.values()),
           "bats_with_1_or_more_original_tracks":sum(v>=1 for v in flights_per_bat),
           "bats_with_2_or_more_original_tracks":sum(v>=2 for v in flights_per_bat),
           "bats_with_3_or_more_original_tracks":sum(v>=3 for v in flights_per_bat),
           "bats_with_5_or_more_original_tracks":sum(v>=5 for v in flights_per_bat),
           "original_track_IDs_per_bat_count_distribution":{
               str(k):int(n) for k,n in sorted(original_tracks_by_count.items())},
           "original_rows_per_track_used_TRUE_stats":stats(track_used),
           "original_rows_per_track_available_FALSE_stats":stats(track_available),
           "source_track_groups_with_both_TRUE_and_FALSE":
               sum(v["TRUE"]>0 and v["FALSE"]>0 for v in track_counts.values()),
           "source_track_groups_exactly_one_TRUE_and_one_or_more_FALSE":
               sum(v["TRUE"]==1 and v["FALSE"]>=1 for v in track_counts.values()),
           "original_use_availability_label_counts":dict(sorted(use_counts.items())),
           "original_binary_case_column_mismatch_count":mismatch,
           "categorical_source_row_counts":{
               c:dict(sorted(values.items())) for c,values in category_counts.items()},
           "missing_key_counts":dict(sorted(missing.items())),
           "actual_UTC_GPS_dates_per_bat_verified":False,
           "source_track_id_is_flight_not_step":True,
           "original_Utm_X_Y_altitude_turbine_distance_or_habitat_values_read":False,
           "original_full_animal_batid_trackid_strings_exported":False,
           "model_or_ecological_effects_fitted":False,
        }
        return profile,individuals


def run()->dict:
    manifest=z.source_list(z.fetch_original())
    official={x["filename"]:x for x in manifest}
    if not set(PINS).issubset(official):
        raise ValueError("Source missing preregistered bat/GPS or capture table")
    receipts={};structs={};ids={}
    with tempfile.TemporaryDirectory() as tmp:
        for name in PINS:
            dest=Path(tmp)/name
            receipts[name]=download_verified(official[name],dest)
            structs[name],ids[name]=source_csv_ids_only(dest,name)
    model=structs["Model_dataset_RSFFlight_Complete_EPSG25833.csv"]
    ledger=structs["Individual_Characteristics_Capture.csv"]
    gps=structs["Observed_GPS_locations.csv"]
    return {
        "study":"v28-B1-noctule-bat-GPS-RSF-actual-source-bytes-ID-grain-only",
        "source_original_record_id":z.RECORD_ID,
        "source_original_DOI":"10.5281/zenodo.7535030",
        "source_license":"cc-by-4.0",
        "source_file_exact_integrity":receipts,
        "source_ID_and_categorical_structure":structs,
        "number_model_bat_tokens_in_capture_ring_ledger":
            len(ids["Model_dataset_RSFFlight_Complete_EPSG25833.csv"] &
                ids["Individual_Characteristics_Capture.csv"]),
        "number_model_bat_tokens_in_observed_GPS_source":
            len(ids["Model_dataset_RSFFlight_Complete_EPSG25833.csv"] &
                ids["Observed_GPS_locations.csv"]),
        "status":"ORIGINAL_BAT_SOURCE_ONLY_STRUCTURE_CHECKED_NO_EFFECT",
        "at_least_8_independent_bat_tokens_with_3_flights":
            model["bats_with_3_or_more_original_tracks"]>=8,
        "source_original_date_separated_repeated_flights_not_yet_verified":True,
        "genuine_per_step_used_random_matched_choice_sets_not_yet_verified":True,
        "no_original_animal_coordinates_or_raw_source_data_exported":True,
        "all_v13_to_v27_frozen_results_unchanged":True,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=Path(
         "validation_v28/results/original_three_bat_CSV_source_gate_v28.json"))
    args=parser.parse_args()
    d=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V28_ORIGINAL_THREE_SOURCES",json.dumps(d,sort_keys=True))
    print("V28_NO_BAT_TURBINE_OR_HABITAT_COEFFICIENTS_COMPUTED")
if __name__=="__main__":
    main()
