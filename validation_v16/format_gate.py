#!/usr/bin/env python3
"""v16 original GPS CSV *format* check, never route/turning outcome evaluation.

Samples predefined first/middle/last release files from each flock, keeps
column patterns and validity/missingness only, no position, speeds, headings,
dates, identities, paths or animal-target rows in the receipt.
"""
from __future__ import annotations
import collections
import csv
import io
import itertools
import math
import re
import zipfile
from pathlib import Path

from source_gate import member_identity, EXPECTED_SOURCE_FLOCKS

ROWS_PER_FILE = 1000
SOURCE_COLUMNS = (
    "INDEX", "TRACK ID", "VALID", "UTC DATE", "UTC TIME",
    "LOCAL DATE", "LOCAL TIME", "MS", "LATITUDE", "N/S",
    "LONGITUDE", "E/W", "ALTITUDE", "SPEED", "HEADING", "G-X", "G-Y", "G-Z"
)
NUMERIC_COLUMNS = ("MS","LATITUDE","LONGITUDE","ALTITUDE","SPEED","HEADING")


def mask_format(s:str)->str:
    out=[]
    for c in str(s).strip()[:40]:
        if c.isdigit():
            c="D"
        elif c.isalpha():
            c="A"
        out.append(c)
    return "".join(out)


def inspect_schema(zip_path:Path)->dict:
    with zipfile.ZipFile(zip_path) as arc:
        byflock=collections.defaultdict(list)
        for member in arc.infolist():
            if member.is_dir() or Path(member.filename).name.startswith("._"):
                continue
            key=member_identity(member.filename)
            if key is not None:
                byflock[key[0]].append((key,member.filename))
        if len(byflock)!=EXPECTED_SOURCE_FLOCKS:
            return {"status":"INCOMPLETE_FLOCK_SCHEMA","sampled_rows":0}
        chosen=[]
        for flock, tracks in sorted(byflock.items()):
            tracks=sorted(tracks,key=lambda x:(x[0][2],x[0][1]))
            selected=[tracks[0],tracks[len(tracks)//2],tracks[-1]]
            chosen.extend(selected)
        patterns=collections.defaultdict(collections.Counter)
        numeric=collections.defaultdict(collections.Counter)
        missing=collections.Counter()
        valid_categories=collections.Counter()
        hemisphere=collections.defaultdict(collections.Counter)
        total=0
        duplicate_utc_tokens=0
        for (_, _), name in chosen:
            with arc.open(name) as raw:
                reader=csv.DictReader(io.TextIOWrapper(raw,encoding="utf-8-sig",errors="replace",newline=""))
                if tuple(reader.fieldnames or ())!=SOURCE_COLUMNS:
                    raise ValueError("Unexpected changed original Qstarz CSV schema")
                seen=set()
                for row in itertools.islice(reader,ROWS_PER_FILE):
                    total+=1
                    for col in ("UTC DATE","UTC TIME","LOCAL DATE","LOCAL TIME","MS"):
                        patterns[col][mask_format(row.get(col,""))]+=1
                    valid_categories[str(row.get("VALID","")).strip()]+=1
                    for col in ("N/S","E/W"):
                        hemisphere[col][str(row.get(col,"")).strip()]+=1
                    key=(row.get("UTC DATE"),row.get("UTC TIME"),row.get("MS"))
                    if key in seen:
                        duplicate_utc_tokens+=1
                    seen.add(key)
                    for col in NUMERIC_COLUMNS:
                        s=str(row.get(col) or "").strip()
                        if not s:
                            missing[col]+=1
                            continue
                        try:
                            v=float(s)
                        except (ValueError,TypeError):
                            numeric[col]["non_numeric"]+=1
                            continue
                        if not math.isfinite(v):
                            numeric[col]["nonfinite"]+=1
                        else:
                            numeric[col]["finite"]+=1
                            if col=="MS":
                                numeric[col]["ms_integer_0_999"]+=int(
                                    0<=v<=999 and v.is_integer())
                            if col=="LATITUDE":
                                numeric[col]["latitude_degree_range"]+=int(-90<=v<=90)
                            if col=="LONGITUDE":
                                numeric[col]["longitude_degree_range"]+=int(-180<=v<=180)
                            if col=="HEADING":
                                numeric[col]["heading_0_360"]+=int(0<=v<=360)
        return {
            "status":"SCHEMA_ONLY_NO_KINEMATICS",
            "sampled_files":len(chosen),
            "sampled_rows":total,
            "sampling_contract":"first, median and last lexical release filename per flock; first 1000 rows each",
            "date_time_token_shapes":{k:dict(sorted(v.items())) for k,v in patterns.items()},
            "valid_field_categories":dict(sorted(valid_categories.items())),
            "hemisphere_field_categories":{k:dict(sorted(v.items())) for k,v in hemisphere.items()},
            "numeric_parsability_counts":{k:dict(sorted(v.items())) for k,v in numeric.items()},
            "missing_numeric_counts":dict(sorted(missing.items())),
            "duplicate_raw_utc_tokens_in_sample":duplicate_utc_tokens,
            "GPS_flight_speed_units_verified":False,
            "independent_time_synchrony_verified":False,
            "GPS_altitude_error_calibrated":False,
            "movement_outcomes_read":False,
            "individual_coordinates_exported":False
        }
