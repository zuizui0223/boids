#!/usr/bin/env python3
"""v17-A3: weather MATLAB serial date and external GPS UTC clock structural overlap.

Never reads GPS positions or courses; never outputs any wind values or GPS times.
No observed turning, resource use or ecological response is calculated.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import csv
import datetime as dt
import io
import json
import math
import tempfile
import zipfile
from pathlib import Path

from schema_gate import file_identity
from source_gate import get_record, select_manifest, original_download

GPS_SHA256 = "030e70082b107a353dd4f0afb0cd54868438273a416efac135120a6bdf9c2b29"
WEATHER_SHA256 = "45885ce19954fd99397b92847421d3e11a6ea2c8d22d1a1d6220ea4940fa2917"
OFFSET_HOURS = (-1, 0, 1)
RAW_GPS_PREVIEW_ROWS = 3
NEAREST_WEATHER_SEC = 90
YEAR_MIN = 2015
YEAR_MAX = 2015


def matlab_datenum_candidate(value: str) -> dt.datetime:
    try:
        n = float(value)
    except (ValueError,TypeError) as exc:
        raise ValueError("Not a numeric MATLAB serial day") from exc
    if not (math.isfinite(n) and 730000 < n < 760000):
        raise ValueError("MATLAB candidate outside plausible decades")
    integer=math.floor(n)
    fraction=n-integer
    d=dt.datetime.fromordinal(integer) + dt.timedelta(days=fraction) - dt.timedelta(days=366)
    return d


def original_utc_candidate(row: dict) -> dt.datetime:
    raw_date=str(row.get("UTC DATE","")).strip()
    raw_clock=str(row.get("UTC TIME","")).strip()
    raw_ms=str(row.get("MS","")).strip()
    x=raw_date.split("/")
    y=raw_clock.split(":")
    if len(x)!=3 or len(y)!=3:
        raise ValueError("Unexpected source GPS date/time tokens")
    if len(x[0])==4:
        yr,month,day=map(int,x)
    elif len(x[2])==4:
        # UK Qstarz rows with dd/mm/yyyy (day first), not inferred from outcome.
        day,month,yr=map(int,x)
    else:
        raise ValueError("Original GPS ambiguous year position")
    h,m,s=map(int,y)
    ms=int(raw_ms)
    if not(0<=ms<=999):
        raise ValueError("Out-of-range GPS milliseconds")
    return dt.datetime(yr,month,day,h,m,s,ms*1000)


def summarize_weather(path: Path) -> tuple[list[dt.datetime],dict]:
    times=[]
    failed=0
    counts=collections.Counter()
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as f:
        for row in csv.reader(f):
            if not row or not any(str(x).strip() for x in row):
                continue
            if len(row)!=3:
                failed+=1
                continue
            try:
                d=matlab_datenum_candidate(row[0])
            except (ValueError,TypeError,OverflowError):
                failed+=1
                continue
            times.append(d)
            counts[d.year]+=1
    if not times:
        raise ValueError("No valid candidate MATLAB dates")
    times.sort()
    positive=[(b-a).total_seconds() for a,b in zip(times,times[1:]) if b>a]
    median_delta=positive[len(positive)//2] if positive else None
    return times,{"weather_rows_parsed_serial_days":len(times),
                  "weather_rows_unparsable_as_serial_days":failed,
                  "weather_calendar_year_histogram":dict(sorted(counts.items())),
                  "candidate_year_2015_fraction":counts[YEAR_MIN]/len(times),
                  "median_positive_weather_interval_seconds":median_delta,
                  "weather_unique_calendar_days":len({v.date() for v in times}),
                  "candidate_no_assumed_UTC_timezone":True}


def count_samples_from_gps(path:Path)->tuple[list[dt.datetime],dict]:
    samples=[]
    counts=collections.Counter()
    phase=collections.Counter()
    invalid=0
    with zipfile.ZipFile(path) as arc:
        files=sorted(n for n in arc.namelist()
                     if n.lower().endswith("_gps.csv") and
                     not n.split("/")[-1].startswith("._"))
        for name in files:
            ident=file_identity(name)
            if ident is None:
                invalid+=1
                continue
            _,p,_=ident
            phase[p]+=1
            first=[]
            last=collections.deque(maxlen=RAW_GPS_PREVIEW_ROWS)
            with arc.open(name) as f:
                reader=csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig",
                                                       errors="replace",newline=""))
                for row in reader:
                    if len(first)<RAW_GPS_PREVIEW_ROWS:
                        first.append(row)
                    last.append(row)
            samples_from_file=0
            # Never parse movement values: only existing recorded UTC date/time/MS.
            for row in first+list(last):
                if str(row.get("VALID","")).strip().upper()!="FIXED":
                    continue
                try:
                    timestamp=original_utc_candidate(row)
                except (ValueError,TypeError,OverflowError):
                    invalid+=1
                    continue
                if timestamp.year!=YEAR_MIN:
                    invalid+=1
                    continue
                samples.append(timestamp)
                samples_from_file+=1
            counts[samples_from_file]+=1
    return samples,{"source_filenames":len(files),
                    "GPS_preview_timestamp_count":len(samples),
                    "GPS_original_date_clock_decode_failures":invalid,
                    "GPS_preview_datetime_sample_count_by_file":dict(sorted(counts.items())),
                    "GPS_phase_track_counts":dict(sorted(phase.items())),
                    "original_GPS_coordinate_or_course_columns_read":False}


def nearest_structure(gps_times:list[dt.datetime],weather_times:list[dt.datetime])->dict:
    """Compare source timing only, no meteorological values/flight predictors."""
    # A1 source candidate weather dates, shifted +/-1 hour; no chosen timezone.
    out={}
    for h in OFFSET_HOURS:
        # Use sampling time of observed GPS, offset mapped weather timestamps.
        shifted=[x+dt.timedelta(hours=h) for x in weather_times]
        matches=0
        for observed in gps_times:
            index=bisect.bisect_left(shifted,observed)
            candidates=[shifted[k] for k in (index-1,index)
                        if 0<=k<len(shifted)]
            if candidates and min(abs((observed-x).total_seconds()) for x in candidates)<=NEAREST_WEATHER_SEC:
                matches+=1
        out[str(h)]={"source_timing_matches_within_90s":matches,
                     "GPS_source_timestamps_tested":len(gps_times),
                     "coverage_fraction":matches/len(gps_times) if gps_times else 0.}
    # NO automatic argmax to "choose offset"; absolute weather clock absent.
    return out


def run()->dict:
    rec=get_record()
    manifest=select_manifest(rec)
    with tempfile.TemporaryDirectory() as d:
        gps=Path(d)/"gps.zip"
        wx=Path(d)/"weather.csv"
        gp=original_download(manifest["Experiment 1 - GPS data.zip"],gps)
        wp=original_download(manifest["Experiment 1 - Weather Data.csv"],wx)
        if gp["sha256"]!=GPS_SHA256 or wp["sha256"]!=WEATHER_SHA256:
            raise ValueError("Pinned v17 original source hash changed")
        weather_t,weather_qc=summarize_weather(wx)
        gps_t,gps_qc=count_samples_from_gps(gps)
        cov=nearest_structure(gps_t,weather_t)
    return {"status":"V17_A3_TIME_SOURCE_ONLY_NO_RESPONSE",
            "study":"v17 weather candidate matlab serial days vs original GPS UTC date structure",
            "source_id":5026107,
            "gps_integrity":gp,
            "weather_integrity":wp,
            "weather_date_decode":weather_qc,
            "original_GPS_timestamp_preview":gps_qc,
            "weather_minus_UTC_offset_hour_candidates":cov,
            "timezone_selected":None,
            "timezone_verified_by_publisher":False,
            "source_pair_ledger_verified":False,
            "animal_movement_outcomes_computed":False,
            "weather_movement_associations_computed":False,
            "notes":["Numeric serial day identified by a fixed candidate conversion, NOT a verified weather timezone.",
                     "All three offset coverage fractions may be high if weather is nearly continuous.",
                     "No weather speed or direction magnitudes read or exported.",
                     "No raw animal GPS timestamps, positions, headings or routes exported."]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v17/results/original_weather_clock_v17.json"))
    a=p.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V17_WEATHER_DATE_SOURCE",json.dumps(d["weather_date_decode"],sort_keys=True))
    print("V17_RAW_GPS_TIME_SOURCE",json.dumps(d["original_GPS_timestamp_preview"],sort_keys=True))
    print("V17_WEATHER_GPS_OFFSET_COVERAGE",json.dumps(d["weather_minus_UTC_offset_hour_candidates"],sort_keys=True))
    print("V17_A3_NO_ANIMAL_RESPONSE_ANALYZED")


if __name__=="__main__":
    main()
