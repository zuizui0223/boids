"""Metadata-only, fail-closed original GIN behavioral source preflight.

No fish positions, stimulus outcomes, or raw files are fetched by this script.
An HTTP success is not original-data admission or replication.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SOURCE_URL = "https://gin.g-node.org/api/v1/repos/danionella/veith_et_al_2024/contents/behavior?ref=master"
MAX_METADATA_BYTES = 1024 * 1024


def inspect(opener=urlopen) -> dict:
    receipt = {
        "status": "SOURCE_ACCESS_STOP",
        "purpose": "VEITH_2024_METADATA_ONLY_NO_TRAJECTORY_VALUES",
        "source_url": SOURCE_URL,
        "raw_fish_data_downloaded": False,
        "field_scores_computed": False,
    }
    try:
        req = Request(SOURCE_URL, headers={"User-Agent": "boids-v21-source-preflight/1.0", "Accept": "application/json"})
        with opener(req, timeout=25) as response:
            blob = response.read(MAX_METADATA_BYTES + 1)
    except HTTPError as exc:
        receipt.update({"stop_reason": "HTTP_STATUS", "http_status": exc.code})
        return receipt
    except (URLError, TimeoutError, OSError) as exc:
        receipt.update({"stop_reason": "NETWORK_OR_TIMEOUT", "error_type": type(exc).__name__})
        return receipt
    if len(blob) > MAX_METADATA_BYTES:
        receipt["stop_reason"] = "METADATA_TOO_LARGE"
        return receipt
    try:
        listing = json.loads(blob)
    except (ValueError, UnicodeDecodeError):
        receipt["stop_reason"] = "NOT_JSON"
        return receipt
    if not isinstance(listing, list):
        receipt["stop_reason"] = "NOT_DIRECTORY_LISTING"
        return receipt
    if not listing or len(listing) > 1000:
        receipt["stop_reason"] = "EMPTY_OR_UNBOUNDED_LISTING"
        return receipt
    entries = []
    for item in listing:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) for k in ("name", "path", "type")):
            receipt["stop_reason"] = "INVALID_ENTRY_SCHEMA"
            return receipt
        size = item.get("size")
        if size is not None and (not isinstance(size, int) or isinstance(size, bool) or size < 0):
            receipt["stop_reason"] = "INVALID_ENTRY_SIZE"
            return receipt
        if not item["path"].startswith("behavior/") or "/../" in item["path"]:
            receipt["stop_reason"] = "UNEXPECTED_PATH"
            return receipt
        entries.append({"name": item["name"], "path": item["path"], "type": item["type"],
                        "size": size, "provider_sha": item.get("sha")})
    receipt.update({
        "status": "METADATA_LISTED_NOT_DATA_ADMITTED",
        "listing_sha256": hashlib.sha256(blob).hexdigest(),
        "entry_count": len(entries),
        "entries": entries,
        "next_gate": "Verify official version/license, individual file checksums and raw bytes before inspection of trial fields or outcomes",
    })
    return receipt


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    payload = json.dumps(inspect(), sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
