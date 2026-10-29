#!/usr/bin/env python3
"""v24-A2 original USGS CSV/FGDC integrity, headers, identifier grain ONLY.

Source pin was established from official ScienceBase A1 manifest before
opening any chosen/available label or original animal/habitat target value.
Full MD5 from provider required before reading headers. Source file bytes
and exact brood IDs/coordinates will never be stored in boids repository.
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
import xml.etree.ElementTree as ET
from pathlib import Path

import sciencebase_source_gate as usgs

EXPECTED = {
    "Duckling_Habitat_Selection_Dataset.csv": {
        "bytes": 7699152,
        "md5": "f4bf54ea42490b535f77400fe3308c06",
    },
    "Duckling_Movement_Dataset.csv": {
        "bytes": 109492,
        "md5": "cbcc3c8f6602f5e5df256b6c315f6f5f",
    },
    "duckling_habitat_use_movements.xml": {
        "bytes": 47300,
        "md5": "9787a34e43410a5544cb9b12fedc3cbc",
    },
}
MAX_SINGLE_BYTES = 15_000_000
MAX_ROWS = 750_000
ID_REGEX = re.compile(
    r"(?:^|_|\b)(brood|bird|duckling|nest|hen|indiv|animal|wetland|pond|site)[^ ]*(?:id|number)|"
    r"(?:brood|duckling|nest|wetland|bird|hen)[._ ]?id|^id$", re.I)
DATETIME_REGEX = re.compile(r"(date|time|year|age|week|day)", re.I)
LABEL_REGEX = re.compile(r"(?<![a-z])(use|used|avail|selected|choice|choice_set|sample)[^a-z]|"
                         r"(used|avail|selected|choice|case|sample)", re.I)
SAFE_LABELS = {
    "0", "1", "used", "available", "true", "false", "yes", "no",
    "u", "a", "observed", "random", "used_point", "available_point",
}


def declared_md5(original: dict) -> str | None:
    chk = original.get("published_checksum")
    if not isinstance(chk, dict):
        return None
    if str(chk.get("type") or "").lower() != "md5":
        return None
    return str(chk.get("value") or "").lower()


def select_original_files(source_item: dict) -> dict:
    if source_item["source_item_id"] != usgs.SOURCE_ITEM:
        raise ValueError("Incorrect ScienceBase source item")
    byname = collections.defaultdict(list)
    for f in source_item["attachments"]:
        byname[f["original_name"]].append(f)
    out = {}
    for name, pin in EXPECTED.items():
        candidates = byname[name]
        if len(candidates) != 1:
            raise ValueError("Missing or duplicated original fixed USGS filename")
        rec = candidates[0]
        if rec["reported_bytes"] != pin["bytes"]:
            raise ValueError("Original file length differs from source-only A1")
        if declared_md5(rec) != pin["md5"]:
            raise ValueError("Original USGS MD5 differs from source-only A1")
        original_url = rec.get("source_download_uri") or rec.get("source_url")
        if (not isinstance(original_url, str)
                or not original_url.startswith("https://www.sciencebase.gov/catalog/file/get/")):
            raise ValueError("Original binary download URL not from ScienceBase")
        out[name] = {"name": name, "url": original_url, **pin}
    return out


def download_exact(item: dict, path: Path) -> dict:
    req = urllib.request.Request(item["url"], headers={
        "User-Agent": usgs.USER_AGENT})
    sh, md = hashlib.sha256(), hashlib.md5()
    total = 0
    with urllib.request.urlopen(req, timeout=110) as source:
        # Endpoint can redirect to an official signed USGS storage backend;
        # only follow HTTPS, reject insecure file fetches.
        if not source.geturl().startswith("https://"):
            raise ValueError("Insecure raw binary redirect")
        reported = source.headers.get("Content-Length")
        if reported is not None and int(reported) != item["bytes"]:
            raise ValueError("USGS file Content-Length changed")
        with path.open("wb") as out:
            for block in iter(lambda: source.read(512 * 1024), b""):
                total += len(block)
                if total > MAX_SINGLE_BYTES:
                    raise ValueError("Original source exceeded absolute cap")
                sh.update(block)
                md.update(block)
                out.write(block)
    if total != item["bytes"] or md.hexdigest() != item["md5"]:
        raise ValueError("Original USGS binary bytes or published MD5 changed")
    return {
        "name": item["name"], "status": "ORIGINAL_BYTES_AND_PROVIDER_MD5_VERIFIED",
        "exact_bytes": total, "provider_md5_verified": True,
        "provider_md5": md.hexdigest(), "independent_sha256": sh.hexdigest(),
        "source_download_url": item["url"],
    }


def name_type(label: str) -> str:
    if ID_REGEX.search(label):
        return "source_identifier_candidate"
    if DATETIME_REGEX.search(label):
        return "date_or_time_candidate"
    if LABEL_REGEX.search(label) and not ("vegetation" in label.lower()):
        return "use_availability_or_choice_label_candidate"
    return "habitat_or_other_covariate"


def source_csv_schema(path: Path) -> dict:
    headers: tuple[str, ...] = ()
    eligible = {}
    category_counts = {}
    unique = {}
    missing = {}
    rows = 0
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as raw:
        reader = csv.reader(raw)
        try:
            headers = tuple(next(reader))
        except StopIteration:
            raise ValueError("Empty original USGS CSV")
        if not headers or len(headers) != len(set(headers)):
            raise ValueError("Empty/duplicate USGS table column headers")
        if len(headers) > 180:
            raise ValueError("Unexpected source >180 fields")
        for i, col in enumerate(headers):
            typ = name_type(col)
            if typ != "habitat_or_other_covariate":
                eligible[i] = typ
                unique[i] = set()
                missing[i] = 0
                if typ == "use_availability_or_choice_label_candidate":
                    category_counts[i] = collections.Counter()
        for row in reader:
            rows += 1
            if rows > MAX_ROWS:
                raise ValueError("Original USGS CSV too many data lines")
            if len(row) != len(headers):
                raise ValueError("Original USGS CSV row width changed")
            # Selected categorical source metadata ONLY.
            # Never convert coordinates, salinity, habitat characteristics,
            # used/available outcome or modeled predictor numerical values.
            for i, typ in eligible.items():
                v = row[i].strip()
                if not v or v.lower() in ("na", "nan", "null", "missing"):
                    missing[i] += 1
                    continue
                unique[i].add(v)
                if i in category_counts:
                    category_counts[i][
                        v.lower() if v.lower() in SAFE_LABELS else "other_masked"
                    ] += 1
    return {
        "status": "SOURCE_SCHEMA_ID_TIME_ONLY_NO_HABITAT_OUTCOMES",
        "original_column_names": list(headers),
        "columns_classified_by_name_only": {
            col: name_type(col) for col in headers
        },
        "physical_csv_data_rows": rows,
        "identifier_time_and_choice_label_fields": {
            headers[i]: {
                "role_candidate": typ,
                "n_distinct_observed_tokens": len(unique[i]),
                "null_or_missing_token_count": missing[i],
                "recognizable_generic_label_counts": (
                    dict(sorted(category_counts[i].items()))
                    if i in category_counts else None),
            } for i, typ in eligible.items()
        },
        "GPS_coordinates_or_habitat_numerics_analyzed": False,
        "actual_chosen_wetland_and_brood_outcomes_scored": False,
        "independent_matched_choice_sets_verified": False,
    }


def fgdc_xml_attributes(path: Path) -> dict:
    root = ET.parse(path).getroot()
    data = []
    for att in root.findall(".//attr"):
        label = att.findtext("attrlabl")
        definition = att.findtext("attrdef")
        if label:
            data.append({
                "name": label.strip()[:160],
                "definition": (definition or "").strip()[:400],
            })
    return {
        "status": "ORIGINAL_FGDC_ATTRIBUTE_DEFINITIONS_ONLY",
        "original_FGDC_attribute_count": len(data),
        "original_attribute_definitions": data[:180],
        "original_animal_records_examined": False,
    }


def run() -> dict:
    item = None
    failures = []
    for url in usgs.SCIENCEBASE_ITEM_URLS:
        try:
            item = usgs.extract_item_metadata(usgs.bounded_json(url))
            break
        except Exception as exc:
            failures.append({"source": url, "status": usgs.safe_failure(exc)})
    result = {
        "study": "v24-original-2026-USGS-Suisun-brood-available-choice-source-A2",
        "USGS_DOI": usgs.SOURCE_DOI,
        "USGS_item": usgs.SOURCE_ITEM,
        "status": "NOT_ADMITTED_ORIGINAL_SOURCE_UNAVAILABLE",
        "original_source_integrity": {},
        "source_columns_and_categorical_grain": {},
        "metadata_access_errors": failures,
        "original_animal_coordinates_or_habitat_outcome_values_exported": False,
        "source_prediction_or_model_fit_computed": False,
    }
    if item is None:
        return result
    files = select_original_files(item)
    with tempfile.TemporaryDirectory() as temp:
        for name, config in files.items():
            path = Path(temp) / name
            try:
                integrity = download_exact(config, path)
                result["original_source_integrity"][name] = integrity
                # This is a schema/IDs-only gate. Do not examine habitat
                # numeric values or which option chosen at an event.
                if name.endswith(".csv"):
                    result["source_columns_and_categorical_grain"][name] = source_csv_schema(path)
                elif name.endswith(".xml"):
                    result["source_columns_and_categorical_grain"][name] = fgdc_xml_attributes(path)
            except Exception as exc:
                result["original_source_integrity"][name] = {
                    "status": "NOT_ADMITTED_BINARY_OR_SCHEMA",
                    "error": type(exc).__name__ + ": " + str(exc)[:160],
                }
    complete = (len(result["original_source_integrity"]) == len(EXPECTED)
                and all(v.get("provider_md5_verified") is True
                        for v in result["original_source_integrity"].values())
                and len(result["source_columns_and_categorical_grain"]) == len(EXPECTED))
    result["status"] = ("ORIGINAL_SOURCE_BYTES_SCHEMA_PASS_CHOICES_NOT_YET_VERIFIED"
                        if complete else
                        "NOT_ADMITTED_ORIGINAL_BYTES_OR_TABLE_SCHEMA")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path,
                   default=Path("validation_v24/results/duckling_source_a2.json"))
    a = p.parse_args()
    data = run()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(data, sort_keys=True,
                                 indent=2, allow_nan=False) + "\n")
    print("V24_A2_FILE_INTEGRITY", json.dumps(data["original_source_integrity"], sort_keys=True))
    print("V24_A2_TABLE_SOURCE_SCHEMA",
          json.dumps(data["source_columns_and_categorical_grain"], sort_keys=True))
    print("V24_A2_STATUS", data["status"])
    print("V24_A2_NO_ECOLOGICAL_HABITAT_CHOICE_PREDICTION")


if __name__ == "__main__":
    main()
