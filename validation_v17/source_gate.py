#!/usr/bin/env python3
"""v17-A external-source-only Taylor et al. 2019 GPS + weather preflight.

No animal locations, GPS tracks, meteorological values, turns, or outcomes
are read, scored, exported, or included in repository. All raw downloads live
only inside a temporary GitHub Actions runner directory.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import posixpath
import re
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

RECORD_ID = 5026107
RECORD_API = f"https://zenodo.org/api/records/{RECORD_ID}"
SOURCE_EXPECTED = {
    "Experiment 1 - GPS data.zip": {
        "md5": "499943131e1f6596187cf2a756e3c8dd",
        "limit": 400_000_000,
    },
    "Experiment 1 - Weather Data.csv": {
        "md5": "1a8c56601ed982a7f2968f1348831317",
        "limit": 30_000_000,
    },
}
MAX_METADATA_BYTES = 5_000_000
MAX_UNCOMPRESSED_BYTES = 8_000_000_000
MAX_ZIP_ENTRY_BYTES = 1_000_000_000
HEADER_BYTES = 16_384
SAMPLED_HEADERS = 32
ZIP_FILENAME_EXAMPLES = 40
USER_AGENT = "boids-v17-independent-weather-source-gate/1.0"


def get_record(url: str = RECORD_API) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": "application/json"
    })
    with urllib.request.urlopen(req, timeout=40) as response:
        b = response.read(MAX_METADATA_BYTES + 1)
    if len(b) > MAX_METADATA_BYTES:
        raise ValueError("Refuse oversized provider metadata")
    record = json.loads(b)
    if not isinstance(record, dict) or str(record.get("id")) != str(RECORD_ID):
        raise ValueError("Wrong or malformed Zenodo record")
    return record


def select_manifest(record: dict) -> dict:
    if str(record.get("id")) != str(RECORD_ID):
        raise ValueError("Other record is not this source")
    files = record.get("files") or []
    if isinstance(files, dict):
        raw = files.get("entries") or {}
        files = list(raw.values()) if isinstance(raw, dict) else []
    if not isinstance(files, list):
        raise ValueError("Unrecognized Zenodo file schema")
    selected: dict[str, dict] = {}
    for name, expected in SOURCE_EXPECTED.items():
        matches = [f for f in files if isinstance(f, dict)
                   and (f.get("key") or f.get("filename")) == name]
        if len(matches) != 1:
            raise ValueError(f"Missing/duplicate required public source: {name}")
        f = matches[0]
        file_size = f.get("size")
        if not isinstance(file_size, int) or file_size <= 0 or file_size > expected["limit"]:
            raise ValueError(f"Missing/out-of-bounds original file size: {name}")
        checksum = str(f.get("checksum") or "").lower()
        if checksum != f"md5:{expected['md5']}":
            raise ValueError(f"Original provider MD5 changed: {name}")
        url = (f.get("links") or {}).get("content") or (f.get("links") or {}).get("self")
        if not isinstance(url, str) or not url.startswith(
            ("https://zenodo.org/", "https://www.zenodo.org/")
        ):
            raise ValueError(f"Unexpected file download origin: {name}")
        selected[name] = {
            "name": name,
            "url": url,
            "reported_size_bytes": file_size,
            "reported_md5": expected["md5"],
            "max_bytes": expected["limit"],
        }
    return selected


def original_download(info: dict, destination: Path) -> dict:
    sha, md5 = hashlib.sha256(), hashlib.md5()
    n = 0
    req = urllib.request.Request(info["url"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=150) as response:
        claimed = response.headers.get("Content-Length")
        if claimed is not None and int(claimed) != info["reported_size_bytes"]:
            raise ValueError("Source byte-count changed before transfer")
        with destination.open("wb") as f:
            for block in iter(lambda: response.read(1024 * 1024), b""):
                n += len(block)
                if n > info["max_bytes"]:
                    raise ValueError("Source exceeded capped byte size")
                f.write(block)
                sha.update(block)
                md5.update(block)
    verified = (n == info["reported_size_bytes"] and
                md5.hexdigest() == info["reported_md5"])
    if not verified:
        raise ValueError("Original metadata size/MD5 mismatch")
    return {
        "bytes": n,
        "sha256": sha.hexdigest(),
        "md5": md5.hexdigest(),
        "matches_reported_size_and_md5": True,
    }


def safe_header_line(first_line: bytes) -> dict:
    """Never expose a numeric GPS row pretending to be a CSV header."""
    line = first_line.decode("utf-8-sig", errors="replace").strip("\r\n")
    if len(line) > HEADER_BYTES or not line.strip():
        return {"status": "no_recognizable_header"}
    if line.startswith(("$GP", "$GN", "$GL")):
        return {"status": "raw_nmea_sentence_not_column_header"}
    try:
        columns = [x.strip().strip('"') for x in next(csv.reader([line]))]
    except (ValueError, csv.Error, StopIteration):
        return {"status": "csv_header_unparseable"}
    if len(columns) < 2 or len(columns) > 150:
        return {"status": "header_columns_not_resolved", "field_count": len(columns)}
    # Only names with alphabetic characters and no GPS-like numeric values.
    valid = all(
        len(x) <= 64 and re.fullmatch(r"[A-Za-z_#][A-Za-z0-9_\s./()+:\-°%]*", x)
        and any(ch.isalpha() for ch in x)
        for x in columns
    )
    if not valid:
        return {
            "status": "unverified_or_numeric_first_line",
            "field_count": len(columns),
        }
    return {"status": "verified_named_header", "columns": columns}


def sample_member_indices(n: int, max_count: int = SAMPLED_HEADERS) -> list[int]:
    """Evenly spaced *alphabetic* filenames, not source-data-adapted."""
    if n <= 0:
        return []
    if n <= max_count:
        return list(range(n))
    return sorted({int(round(i * (n - 1) / (max_count - 1)))
                   for i in range(max_count)})


def zip_structure(path: Path) -> dict:
    with zipfile.ZipFile(path, "r") as arc:
        members = arc.infolist()
        names = [m.filename for m in members]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entry filename")
        for m in members:
            name = m.filename.replace("\\", "/")
            if (name.startswith("/") or
                re.match(r"^[A-Za-z]:", name) or
                ".." in name.split("/") or
                m.flag_bits & 0x1 or
                m.file_size > MAX_ZIP_ENTRY_BYTES):
                raise ValueError("Unsafe/encrypted/too-large archive member")
        total = sum(m.file_size for m in members)
        if total > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("Expanded GPS archive exceeds 8 GB cap")
        files = sorted(
            [m for m in members if not m.is_dir() and
             not posixpath.basename(m.filename).startswith("._")],
            key=lambda m: m.filename
        )
        apple = sum(not m.is_dir() and
                    posixpath.basename(m.filename).startswith("._") for m in members)
        exts = collections.Counter(
            posixpath.splitext(m.filename)[1].lower() or "no_extension" for m in files
        )
        candidates = [
            m for m in files
            if posixpath.splitext(m.filename)[1].lower() in
            (".csv", ".txt", ".log", ".nmea")
        ]
        heads = []
        for ix in sample_member_indices(len(candidates)):
            m = candidates[ix]
            with arc.open(m) as f:
                first = f.readline(HEADER_BYTES + 1)
            heads.append({
                "path": m.filename,
                "bytes_original_decompressed": m.file_size,
                "header": safe_header_line(first),
            })
        return {
            "status": "STRUCTURAL_ONLY_NO_MOVEMENT_ANALYSIS",
            "total_entries": len(members),
            "normal_files": len(files),
            "appledouble_metadata_excluded": apple,
            "uncompressed_size_bytes_reported": total,
            "file_extension_counts": dict(sorted(exts.items())),
            "csv_or_raw_text_candidates": len(candidates),
            "file_name_examples": [m.filename for m in files[:ZIP_FILENAME_EXAMPLES]],
            "file_names_example_limit": ZIP_FILENAME_EXAMPLES,
            "sampled_header_files": len(heads),
            "header_samples": heads,
            "source_observations_scored": 0,
            "source_routes_exported": False,
            "gps_original_utc_precision_verified": False,
            "repeated_individual_sessions_verified": False,
            "independent_partner_network_components_verified": False,
            "wind_utc_alignment_verified": False,
        }


def weather_structure(path: Path) -> dict:
    """Physical row count and *first line only* for weather timestamps/columns."""
    count = 0
    with path.open("rb") as f:
        first = f.readline(HEADER_BYTES + 1)
        if len(first) > HEADER_BYTES:
            raise ValueError("Weather header too large")
        header = safe_header_line(first)
        for _ in f:
            count += 1
            if count > 2_000_000:
                raise ValueError("Weather rows beyond source-only bounded cap")
    cols = [c.lower() for c in header.get("columns", [])]
    return {
        "status": "WEATHER_HEADER_AND_ROW_COUNT_ONLY",
        "header": header,
        "physical_rows_after_first": count,
        "candidate_timestamp_columns": [s for s in cols
            if any(w in s for w in ("date", "time", "utc", "hour", "minute"))],
        "candidate_wind_columns": [s for s in cols
            if any(w in s for w in ("wind", "bearing", "direction"))],
        "wind_units_verified": False,
        "wind_from_to_convention_verified": False,
        "weather_timezone_verified": False,
        "weather_values_read_or_analyzed": False,
        "any_matched_GPS_weather_predictions": False,
    }


def run() -> dict:
    record = get_record()
    manifest = select_manifest(record)
    meta = record.get("metadata") or {}
    output = {
        "study": "v17-source-first-independent-Taylor2019-GPS-weather",
        "status": "SOURCE_ONLY_NO_FORECAST",
        "zenodo_record_id": RECORD_ID,
        "zenodo_record_url": RECORD_API,
        "record_doi": record.get("doi"),
        "record_title": meta.get("title"),
        "record_license": meta.get("license"),
        "record_published": record.get("created"),
        "source_manifest": {
            name: {
                "name": info["name"],
                "reported_size_bytes": info["reported_size_bytes"],
                "reported_md5": info["reported_md5"],
            } for name, info in manifest.items()
        },
        "no_reuse_of_v15_v16_observed_scores": True,
    }
    with tempfile.TemporaryDirectory() as temp:
        gps = Path(temp)/"original_gps.zip"
        weather = Path(temp)/"original_weather.csv"
        output["GPS_integrity"] = original_download(
            manifest["Experiment 1 - GPS data.zip"], gps
        )
        output["weather_integrity"] = original_download(
            manifest["Experiment 1 - Weather Data.csv"], weather
        )
        output["GPS_archive_structure"] = zip_structure(gps)
        output["weather_structure"] = weather_structure(weather)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(
        "validation_v17/results/source_first_taylor2019_v17.json"
    ))
    args = parser.parse_args()
    out = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, sort_keys=True, indent=2, allow_nan=False)
                        + "\n", encoding="utf-8")
    print("V17_SOURCE_PROVENANCE", json.dumps({
        "id": out["zenodo_record_id"],
        "source": out["GPS_integrity"],
        "weather": out["weather_integrity"],
        "license": out["record_license"],
        "doi": out["record_doi"],
    }, sort_keys=True))
    print("V17_GPS_STRUCTURE", json.dumps(out["GPS_archive_structure"], sort_keys=True))
    print("V17_WEATHER_STRUCTURE", json.dumps(out["weather_structure"], sort_keys=True))
    print("V17_NO_ECOLOGICAL_FORECAST_EXECUTED")


if __name__ == "__main__":
    main()
