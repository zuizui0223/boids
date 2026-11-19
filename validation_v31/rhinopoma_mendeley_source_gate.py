#!/usr/bin/env python3
"""Frozen v31 Mendeley Rhinopoma 2025 source-metadata audit; no animal rows."""
from __future__ import annotations
import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

DOI = "10.17632/k7pt2j84f7.1"
ID = "k7pt2j84f7"
VERSION = 1
OUTPUT = Path("validation_v31/results/rhinopoma_mendeley_source_v31.json")
ENDPOINTS = {
    "dataset": f"https://api.data.mendeley.com/datasets/{ID}?version={VERSION}",
    "version_files": f"https://api.data.mendeley.com/datasets/{ID}/files?version={VERSION}",
    "public_version_files": f"https://api.data.mendeley.com/datasets/publics/{ID}/files?version={VERSION}",
}
MAX_METADATA_BYTES = 1_000_000


def get_metadata(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.mendeley-public-dataset.1+json, application/json",
            "User-Agent": "boids-independent-source-schema-audit/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=14) as response:
            data = response.read(MAX_METADATA_BYTES + 1)
            status = response.status
            typ = response.headers.get("Content-Type", "")
            out = {
                "http_status": status,
                "content_type": typ.split(";")[0],
                "response_is_within_metadata_cap": len(data) <= MAX_METADATA_BYTES,
                "response_is_json": False,
            }
            if len(data) > MAX_METADATA_BYTES:
                out["status"] = "SOURCE_METADATA_SIZE_STOP"
                return out
            try:
                out["parsed_json"] = json.loads(data)
                out["response_is_json"] = True
                out["status"] = "PUBLIC_JSON_METADATA"
            except (UnicodeDecodeError, json.JSONDecodeError):
                out["status"] = "NON_JSON_SOURCE_METADATA_STOP"
            return out
    except urllib.error.HTTPError as exc:
        return {"http_status": exc.code, "status": "HTTP_ACCESS_STOP", "response_is_json": False}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"http_status": None, "status": "TRANSPORT_ACCESS_STOP",
                "error_type": type(exc).__name__, "response_is_json": False}


def summarize_files(raw) -> dict:
    if isinstance(raw, list):
        files = raw
    elif isinstance(raw, dict):
        files = raw.get("files") or raw.get("results") or raw.get("items") or []
        if isinstance(files, dict):
            files = files.get("files") or files.get("results") or []
    else:
        files = []
    if not isinstance(files, list):
        files = []
    names = []
    for x in files[:100]:
        if not isinstance(x, dict):
            continue
        detail = x.get("content_details") or {}
        if not isinstance(detail, dict):
            detail = {}
        names.append({
            "filename": str(x.get("filename") or x.get("name") or "")[:200],
            "provider_file_id": str(x.get("id") or "")[:80],
            "size_bytes": x.get("size") or detail.get("size"),
            "published_sha256": str(detail.get("sha256_hash") or x.get("sha256_hash") or "")[:80],
            "content_type": str(detail.get("content_type") or "")[:100],
        })
    return {"reported_file_entries": len(files), "files_metadata_up_to_100": names}


def audit(lookup=get_metadata) -> dict:
    results = {key: lookup(url) for key, url in ENDPOINTS.items()}
    d = results["dataset"].get("parsed_json")
    dataset_summary = {}
    if isinstance(d, dict):
        doi = d.get("doi")
        license_ = d.get("data_licence") or d.get("licence")
        dataset_summary = {
            "name": str(d.get("name") or "")[:250],
            "published_version": d.get("version"),
            "published_dataset_doi": doi.get("id") if isinstance(doi, dict) else doi,
            "published_license": license_.get("short_name") if isinstance(license_, dict) else str(license_ or ""),
            "dataset_file_metadata": summarize_files(d.get("files") or []),
        }
    files_summary = {
        key: summarize_files(r.get("parsed_json"))
        for key, r in results.items()
        if key.endswith("files") and r.get("response_is_json")
    }
    for obj in results.values():
        obj.pop("parsed_json", None)
    return {
        "source": "Goldshtein et al 2025 PNAS wild Rhinopoma microphyllum",
        "original_paper_doi": "10.1073/pnas.2407810122",
        "original_repository_doi": DOI,
        "original_version": VERSION,
        "metadata_endpoints": results,
        "dataset_metadata": dataset_summary,
        "file_listing_metadata": files_summary,
        "source_only_data_byte_download_performed": False,
        "raw_gps_or_acoustic_values_opened": False,
        "time_aligned_same_bat_raw_audio_and_movement_verified": False,
        "independent_sensing_margin_inputs_verified": False,
        "source_admitted_for_behavior_fitting": False,
        "carollia_v30_negative_primary_unchanged": True,
        "record_status": "PUBLIC_SOURCE_METADATA_ONLY" if any(
            r.get("response_is_json") for r in results.values()) else "ORIGINAL_PUBLIC_API_NOT_ACCESSIBLE",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=OUTPUT)
    args=parser.parse_args()
    result=audit()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V31_SOURCE_ONLY_STATUS="+json.dumps({
        "status": result["record_status"],
        "http": {k: v["http_status"] for k,v in result["metadata_endpoints"].items()},
        "file_counts": {k:v["reported_file_entries"] for k,v in result["file_listing_metadata"].items()},
        "dataset_name": result["dataset_metadata"].get("name"),
    },sort_keys=True))
    assert result["raw_gps_or_acoustic_values_opened"] is False


if __name__=="__main__":
    main()
