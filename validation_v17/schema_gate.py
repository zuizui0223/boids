#!/usr/bin/env python3
"""v17-A2 pure source-format admission: file identity & weather syntax, no outcomes.

The script downloads exactly the previously pinned independent source files,
not older v15/v16 data. Original animal positions/courses and weather magnitudes
are NEVER reported or used in a regression.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import io
import json
import math
import re
import tempfile
import zipfile
from pathlib import Path

from source_gate import get_record, select_manifest, original_download, safe_header_line

NAME_RE = re.compile(
    r"^(?P<bird>[A-Za-z]\d{2})_(?P<phase>[1-4])_(?P<release>[1-6])_GPS\.csv$",
    re.I,
)
GPS_SAMPLE_FILES = 32
GPS_SAMPLE_ROWS = 100
WEATHER_SAMPLE_ROWS = 4096
EXPECTED_GPS_SCHEMA = (
    "INDEX", "TRACK ID", "VALID", "UTC DATE", "UTC TIME",
    "LOCAL DATE", "LOCAL TIME", "MS", "LATITUDE", "N/S",
    "LONGITUDE", "E/W", "ALTITUDE", "SPEED", "HEADING",
    "G-X", "G-Y", "G-Z"
)

WEATHER_DATE_FORMATS = (
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y %H:%M",
    "%m-%d-%Y %H:%M:%S",
    "%m-%d-%Y %H:%M",
)

def mask_format(s: str) -> str:
    """Describe source string shape, not its actual date/wind values."""
    return "".join("D" if x.isdigit() else "A" if x.isalpha() else x
                   for x in str(s).strip()[:80])


def file_identity(path: str):
    name = path.split("/")[-1]
    m = NAME_RE.fullmatch(name)
    if not m:
        return None
    return m.group("bird").upper(), int(m.group("phase")), int(m.group("release"))


def original_gps_inventory(path: Path) -> dict:
    with zipfile.ZipFile(path) as arc:
        members = sorted([m for m in arc.infolist()
                          if not m.is_dir() and m.filename.lower().endswith(".csv")
                          and not m.filename.split("/")[-1].startswith("._")],
                         key=lambda m:m.filename)
        seen = set()
        unexpected = []
        bird_releases = collections.defaultdict(set)
        phases = collections.Counter()
        rows_per_phase = collections.Counter()
        for member in members:
            identity = file_identity(member.filename)
            if identity is None:
                unexpected.append(member.filename)
                continue
            if identity in seen:
                raise ValueError("Original GPS bird/phase/release duplicates")
            seen.add(identity)
            bird, phase, release = identity
            phases[phase] += 1
            rows_per_phase[phase] += member.file_size
            bird_releases[bird].add((phase, release))
        # Source-only schema sample: first, middle, last files and evenly spaced
        # 32-entry selection. Results never include exact date/time values.
        ix = [round(i*(len(members)-1)/(GPS_SAMPLE_FILES-1))
              for i in range(min(len(members),GPS_SAMPLE_FILES))]
        chosen = [members[i] for i in sorted(set(ix))]
        head_counts = collections.Counter()
        valid_counts = collections.Counter()
        shapes = collections.defaultdict(collections.Counter)
        impossible_ms = 0
        sampled_rows = 0
        for member in chosen:
            with arc.open(member) as raw:
                f = io.TextIOWrapper(raw,encoding="utf-8-sig",errors="replace",newline="")
                reader = csv.DictReader(f)
                head = tuple(reader.fieldnames or [])
                head_counts[head] += 1
                for index,row in enumerate(reader):
                    if index>=GPS_SAMPLE_ROWS:
                        break
                    sampled_rows += 1
                    valid_counts[str(row.get("VALID","")).strip()] += 1
                    for c in ("UTC DATE","UTC TIME","MS"):
                        shapes[c][mask_format(row.get(c,""))] += 1
                    v=str(row.get("MS") or "").strip()
                    try:
                        n=int(v)
                        if not 0 <= n <= 999:
                            impossible_ms += 1
                    except (ValueError,TypeError):
                        impossible_ms += 1
        return {
            "status": "GPS_FILENAME_CLOCK_TOKEN_STRUCTURE_ONLY",
            "raw_gps_csv_files": len(members),
            "filenames_parsed": len(seen),
            "unrecognized_csv_filenames": len(unexpected),
            "unexpected_filename_examples": unexpected[:8],
            "unique_bird_ids": len(bird_releases),
            "phase_track_count": dict(sorted(phases.items())),
            "individual_file_counts_distribution": dict(
                sorted(collections.Counter(len(s) for s in bird_releases.values()).items())
            ),
            "individuals_in_all_four_phases": sum(
                set(phase for phase,_ in a) == {1,2,3,4}
                for a in bird_releases.values()),
            "all_header_samples_match_original_18_columns":
                all(h == EXPECTED_GPS_SCHEMA for h in head_counts),
            "header_samples": len(chosen),
            "first_100_row_sampled_GPS_records": sampled_rows,
            "gps_fix_validity_categories": dict(sorted(valid_counts.items())),
            "gps_UTC_date_time_ms_token_shapes": {
                k: dict(sorted(v.items())) for k,v in shapes.items()},
            "out_of_range_or_noninteger_ms_tokens": impossible_ms,
            "GPS_timestamp_cross_receiver_accuracy_verified": False,
            "partner_pair_ledger_verified": False,
            "GPS_movement_response_read": False,
            "GPS_positions_exported": False,
            "GPS_course_target_read": False,
        }


def parse_datetime_candidates(s: str) -> tuple[str,...]:
    matched = []
    for pattern in WEATHER_DATE_FORMATS:
        try:
            dt.datetime.strptime(s.strip(),pattern)
            matched.append(pattern)
        except ValueError:
            continue
    return tuple(matched)


def original_weather_format(path: Path) -> dict:
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as f:
        first = f.readline()
    head = safe_header_line(first.encode())
    has_header = head.get("status") == "verified_named_header"
    with path.open("r",encoding="utf-8-sig",errors="replace",newline="") as f:
        reader = csv.reader(f)
        total = 0
        widths = collections.Counter()
        shapes = [collections.Counter() for _ in range(3)]
        numeric = collections.Counter()
        datetime_formats = collections.Counter()
        bad_weather_direction = 0
        sample_stride = 37  # deterministic, not weather-outcome adapted
        sampled = 0
        for i,row in enumerate(reader):
            if has_header and i==0:
                continue
            if not any(str(c).strip() for c in row):
                continue
            total += 1
            widths[len(row)] += 1
            if i%sample_stride != 0 or sampled>=WEATHER_SAMPLE_ROWS:
                continue
            sampled += 1
            for idx in range(min(3,len(row))):
                shapes[idx][mask_format(row[idx])] += 1
            if len(row) != 3:
                continue
            poss = parse_datetime_candidates(row[0])
            if poss:
                for p in poss:
                    datetime_formats[p] += 1
            else:
                datetime_formats["NONE_OF_FIXED_DATETIME_FORMATS"] += 1
            for c in (1,2):
                try:
                    n=float(row[c])
                    if not math.isfinite(n):
                        raise ValueError("not finite")
                    numeric[f"col{c+1}_finite"] += 1
                    if c==2 and not 0<=n<=360:
                        bad_weather_direction+=1
                except (ValueError,TypeError):
                    numeric[f"col{c+1}_not_finite_numeric"] += 1
        return {
            "status":"WEATHER_DATA_SCHEMA_ONLY_NO_MOVEMENT_OUTCOME",
            "first_line_is_named_header":has_header,
            "weather_physical_nonempty_data_rows":total,
            "sample_stride":sample_stride,
            "sample_rows_with_token_shapes":sampled,
            "field_count_histogram":dict(sorted(widths.items())),
            "three_column_masked_token_shapes":[dict(sorted(x.items())) for x in shapes],
            "fixed_candidate_datetime_parsability":dict(sorted(datetime_formats.items())),
            "numeric_finite_counts":dict(sorted(numeric.items())),
            "out_of_range_direction_candidates":bad_weather_direction,
            "source_wind_speed_units_verified":False,
            "source_wind_bearing_from_to_verified":False,
            "source_weather_UTC_offset_verified":False,
            "weather_GPS_join_attempted":False,
            "movement_targets_scored":False,
        }


def run() -> dict:
    record=get_record()
    manifest=select_manifest(record)
    out={"study":"v17-A2-independent-2019-weather-individual-source-structure",
         "status":"SOURCE_FORMAT_ONLY_NO_ECOLOGICAL_RESULT",
         "zenodo_record_id":5026107,
         "source_contract":"docs/V17_ORIGINAL_SCHEMA_OBSERVABILITY_ADDENDUM.md",
         "provider_doi":record.get("doi")}
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/"original_gps.zip"
        wx=Path(d)/"original_weather.csv"
        out["GPS_provenance"]=original_download(manifest["Experiment 1 - GPS data.zip"],path)
        out["weather_provenance"]=original_download(manifest["Experiment 1 - Weather Data.csv"],wx)
        out["GPS_filename_time_structure"]=original_gps_inventory(path)
        out["weather_timestamp_format"]=original_weather_format(wx)
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("validation_v17/results/original_schema_wind_v17.json"))
    args=ap.parse_args()
    d=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V17_A2_GPS",json.dumps(d["GPS_filename_time_structure"],sort_keys=True))
    print("V17_A2_WEATHER",json.dumps(d["weather_timestamp_format"],sort_keys=True))
    print("V17_A2_SOURCE_ONLY_NO_MOTION_TARGET")


if __name__=="__main__":
    main()
