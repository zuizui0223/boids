#!/usr/bin/env python3
"""v24-A1: USGS ScienceBase original data-release manifest and DOI only.

No duckling location, used/available target, habitat value, or source binary
is inspected. Official ScienceBase provenance and attachment metadata only.
An unresponsive official API is an explicit NOT_ADMITTED source result.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE_DOI = "10.5066/P13NYGAI"
SOURCE_ITEM = "68631b39d4be025653d31f22"
SCIENCEBASE_ITEM_URLS = (
    f"https://www.sciencebase.gov/catalog/item/{SOURCE_ITEM}?format=json",
    f"https://www.sciencebase.gov/catalog/item/{SOURCE_ITEM}",
    f"https://api.sciencebase.gov/catalog/item/{SOURCE_ITEM}",
)
MAX_JSON = 12_000_000
MAX_LIST_ITEMS = 100
USER_AGENT = "boids-v24-original-USGS-wetland-source-provenance/1.0"


def bounded_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=35) as stream:
        final_url = stream.geturl()
        # Follow redirects only to ScienceBase domains, not untrusted data.
        parsed = urllib.parse.urlparse(final_url)
        if parsed.hostname not in ("www.sciencebase.gov", "sciencebase.gov",
                                   "api.sciencebase.gov"):
            raise ValueError("Source metadata redirected outside official ScienceBase")
        raw = stream.read(MAX_JSON + 1)
    if len(raw) > MAX_JSON:
        raise ValueError("Refuse oversized official metadata")
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("USGS metadata API did not return an object")
    return obj


def safe_failure(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return "HTTP_" + str(exc.code)
    if isinstance(exc, urllib.error.URLError):
        return "NETWORK_" + type(exc.reason).__name__
    return type(exc).__name__ + ": " + str(exc)[:160]


def parse_file_inventory(obj: dict) -> list[dict]:
    out = []
    seen = set()
    for original in obj.get("files") or []:
        if not isinstance(original, dict):
            continue
        filename = original.get("name") or original.get("filename")
        if not isinstance(filename, str) or not filename:
            continue
        if filename in seen:
            raise ValueError("Duplicate official USGS original attachment name")
        seen.add(filename)
        out.append({
            "original_name": filename,
            "reported_bytes": original.get("size"),
            "reported_content_type": original.get("contentType"),
            "source_download_uri": original.get("downloadUri"),
            "source_url": original.get("url"),
            "published_sha256": original.get("sha256"),
            "published_md5": original.get("md5"),
            "published_checksum": original.get("checksum"),
            "attachment_field_keys": sorted(original.keys()),
            "is_original_tabular_candidate": any(filename.lower().endswith(ext)
                         for ext in (".csv", ".xlsx", ".xls", ".zip",
                                     ".txt", ".gpkg", ".gdb.zip")),
        })
    return out


def ensure_source_identity(obj: dict) -> None:
    ident = str(obj.get("id") or "").lower()
    if ident != SOURCE_ITEM:
        raise ValueError("Returned ScienceBase item is not pinned original")
    title = str(obj.get("title") or "").lower()
    if "duckling" not in title and "duck" not in title:
        raise ValueError("Returned item has no duck source title")
    # Original DOI may be in identifiers or metadata, but not every item
    # response has the DOI field. Require ID + title and report missing DOI.
    ids = obj.get("identifiers") or []
    source_string = json.dumps(ids).lower() + " " + str(obj.get("doi") or "").lower()
    if "10.5066/" in source_string and SOURCE_DOI.lower() not in source_string:
        raise ValueError("USGS metadata identifies a different DOI")


def extract_item_metadata(obj: dict) -> dict:
    ensure_source_identity(obj)
    files = parse_file_inventory(obj)
    return {
        "status": "ORIGINAL_SCIENCEBASE_ITEM_META_VERIFIED",
        "source_item_id": obj.get("id"),
        "source_title": obj.get("title"),
        "source_summary_type": obj.get("systemType"),
        "published_metadata_identifiers": obj.get("identifiers"),
        "reported_license": obj.get("rights") or obj.get("license"),
        "dates": obj.get("dates"),
        "attachment_count": len(files),
        "attachments": files,
        "metadata_field_names": sorted(obj.keys()),
        "child_items_embedded_count": len(obj.get("childItems") or []),
        "original_animal_tracking_or_habitat_values_read": False,
    }


def child_item_listing(url: str) -> dict:
    try:
        data = bounded_json(url)
        records = data.get("items") or []
        if len(records) > MAX_LIST_ITEMS:
            raise ValueError("Official child listing unexpectedly too big")
        return {
            "status": "OFFICIAL_CHILDREN_LIST_READ",
            "url": url,
            "total": data.get("total"),
            "child_items": [
                {"id": v.get("id"), "title": v.get("title"),
                 "files_reported": len(v.get("files") or [])}
                for v in records if isinstance(v, dict)
            ],
            "listing_field_names": sorted(data.keys()),
        }
    except Exception as exc:
        return {"status": "OFFICIAL_CHILDREN_UNAVAILABLE",
                "url": url, "error": safe_failure(exc)}


def run() -> dict:
    result = {
        "study": "v24-USGS-original-brood-wetland-used-available-source-A1",
        "date_registered": "2026-10-29",
        "pinned_original_doi": SOURCE_DOI,
        "pinned_original_sciencebase_item_id": SOURCE_ITEM,
        "status": "NOT_ADMITTED_OFFICIAL_USGS_SOURCE_META_INACCESSIBLE",
        "attempts": [],
        "source_item": None,
        "child_listing": None,
        "used_available_choicesset_grain_verified": False,
        "original_brood_ID_date_habitat_rows_read": False,
        "model_outcomes_computed": False,
        "previous_v13_to_v23_endpoints_unchanged": True,
    }
    data = None
    for url in SCIENCEBASE_ITEM_URLS:
        try:
            obj = bounded_json(url)
            data = extract_item_metadata(obj)
            result["attempts"].append({"official_url": url,
                                       "status": "SOURCE_METADATA_SUCCESS"})
            break
        except Exception as exc:
            result["attempts"].append({"official_url": url,
                                       "status": safe_failure(exc)})
    if data is None:
        return result
    result["source_item"] = data
    result["status"] = ("ORIGINAL_USGS_MANIFEST_ACQUIRED_UNTESTED_CHOICES"
                        if data["attachment_count"] > 0 else
                        "NO_ATTACHMENTS_IN_PARENT_REQUIRES_CHILD_DISCOVERY")
    # Documented official ScienceBase parentId filter. Still only metadata.
    query = urllib.parse.urlencode({
        "q": "", "filter": "parentId=" + SOURCE_ITEM,
        "format": "json", "max": str(MAX_LIST_ITEMS),
    })
    result["child_listing"] = child_item_listing(
        "https://www.sciencebase.gov/catalog/items?" + query)
    if data["attachment_count"] == 0 and result["child_listing"].get("child_items"):
        result["status"] = "ORIGINAL_USGS_CHILD_ITEMS_REQUIRE_SEPARATE_SOURCE_ADMISSION"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path,
                        default=Path("validation_v24/results/sciencebase_source_a1.json"))
    args = parser.parse_args()
    out = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, sort_keys=True, indent=2,
                                   allow_nan=False) + "\n", encoding="utf-8")
    print("V24_A1_USGS_SOURCE", json.dumps(out, sort_keys=True))
    print("V24_A1_NO_ANIMAL_HABITAT_OR_CHOICE_OUTCOMES_COMPUTED")


if __name__ == "__main__":
    main()
