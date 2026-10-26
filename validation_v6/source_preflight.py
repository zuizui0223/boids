#!/usr/bin/env python3
"""Fail-closed, schema-only preflight for Roy & Abaid's bat-pair Figshare archive.

This never reports a biological outcome. Fetches a checksum-pinned public .mat file,
prints the structure and sample counts, and deliberately does not fit Boids forces.
No source trajectories are committed or included in GitHub Actions artifacts.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import md5, sha256
from io import BytesIO
import json
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
from scipy.io import loadmat

DOI = "10.7294/W4639MWR"
API_URL = "https://api.figshare.com/v2/articles/14097077"
EXPECTED_ID = 26581166
EXPECTED_NAME = "data.mat"
EXPECTED_SIZE = 577806
EXPECTED_MD5 = "df055ac743fb2cc593a99c70a7afa15f"
DIRECT_URL = f"https://ndownloader.figshare.com/files/{EXPECTED_ID}"
MAX_SOURCE_BYTES = 2000000
MAX_DEPTH = 5
MAX_CHILDREN = 30


def verify_bytes(raw: bytes) -> dict:
    if len(raw) != EXPECTED_SIZE:
        raise ValueError(f"ABORT: byte length mismatch: {len(raw)} != {EXPECTED_SIZE}")
    digest = md5(raw).hexdigest()
    if digest != EXPECTED_MD5:
        raise ValueError(f"ABORT: MD5 mismatch: {digest} != {EXPECTED_MD5}")
    return {"bytes": len(raw), "md5": digest, "sha256": sha256(raw).hexdigest()}


def verify_remote_metadata(obj: dict) -> dict:
    if obj.get("id") != 14097077 or obj.get("doi") != DOI or not obj.get("is_public"):
        raise ValueError("ABORT: mismatched unpublished Figshare article")
    options = [f for f in obj.get("files", []) if f.get("id") == EXPECTED_ID]
    if len(options) != 1:
        raise ValueError("ABORT: pinned Figshare file ID not unique")
    f = options[0]
    if (f.get("size") != EXPECTED_SIZE or f.get("name") != EXPECTED_NAME
            or f.get("computed_md5") != EXPECTED_MD5
            or f.get("download_url") != DIRECT_URL or f.get("is_link_only")):
        raise ValueError("ABORT: official file properties differ from frozen manifest")
    return {"doi": DOI, "article_id": obj["id"], "file_id": EXPECTED_ID,
            "name": EXPECTED_NAME, "bytes": EXPECTED_SIZE, "md5": EXPECTED_MD5,
            "license": obj.get("license", {}).get("name", "not_recorded")}


def _dtype_text(x) -> str:
    if isinstance(x, np.ndarray):
        return str(x.dtype)
    return type(x).__name__


def inspect_mat(raw: bytes) -> dict:
    """Inspect shape/fields only. No numerical values are exported."""
    verify_bytes(raw)
    obj = loadmat(BytesIO(raw), squeeze_me=False, struct_as_record=False,
                  variable_names=None)
    roots = {k: v for k, v in obj.items() if not k.startswith("__")}
    if not roots:
        raise ValueError("ABORT: no MATLAB data variables")

    def visit(value, depth: int, budget: list[int]) -> dict:
        budget[0] -= 1
        if budget[0] < 0:
            return {"type": "truncated", "cause": "global_node_budget"}
        desc = {"type": _dtype_text(value)}
        if isinstance(value, np.ndarray):
            desc["shape"] = list(value.shape)
            desc["size"] = int(value.size)
            if value.dtype.names:
                desc["fields"] = list(value.dtype.names)
            if depth < MAX_DEPTH and value.dtype == object and value.size:
                # inspect first cell structure, NOT its measured coordinates
                desc["first_cell_schema"] = visit(value.flat[0], depth + 1, budget)
            elif depth < MAX_DEPTH and value.size and value.dtype.names:
                desc["first_record_schema"] = visit(value.flat[0], depth + 1, budget)
        elif hasattr(value, "_fieldnames"):
            fields = sorted(value._fieldnames or [])
            desc["fields"] = fields[:MAX_CHILDREN]
            if depth < MAX_DEPTH:
                desc["children"] = {k: visit(getattr(value, k), depth + 1, budget)
                                    for k in fields[:MAX_CHILDREN]}
        elif isinstance(value, np.void):
            desc["fields"] = list(value.dtype.names or [])
            if depth < MAX_DEPTH:
                desc["children"] = {k: visit(value[k], depth + 1, budget)
                                    for k in (value.dtype.names or [])[:MAX_CHILDREN]}
        return desc

    budget = [240]
    return {"top_level_count": len(roots),
            "top_level": {k: visit(v, 0, budget) for k, v in sorted(roots.items())},
            "note": "Schema only; values, velocity, pair proximity, camera accuracy and biological outcomes not inspected."}


def http_bytes(url: str, cap: int = MAX_SOURCE_BYTES) -> bytes:
    req = Request(url, headers={"User-Agent": "boids-v6-structural-preflight/1.0",
                                "Accept": "application/octet-stream,application/json"})
    with urlopen(req, timeout=65) as res:
        content = res.read(cap + 1)
    if len(content) > cap:
        raise ValueError("ABORT: data response exceeds pinned safe size limit")
    return content


def run(source: Path | None) -> dict:
    metadata = None
    if source is None:
        metadata = verify_remote_metadata(json.loads(http_bytes(API_URL, cap=100000)))
        raw = http_bytes(DIRECT_URL)
    else:
        raw = source.read_bytes()
    digest = verify_bytes(raw)
    return {"status": "SCHEMA_ONLY_NOT_A_BIOLOGICAL_RESULT", "source": metadata,
            "integrity": digest, "schema": inspect_mat(raw),
            "claim_boundary": [
                "Structural availability does not establish synchronized usable pairs.",
                "180-Hz spline resampling is not independent 180-Hz instrument observation.",
                "No Boids coefficient, effect size or ecological niche prediction was fitted.",
                "Raw biological trajectories are not redistributed." ]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, help="Local publicly downloaded data.mat (offline mode)")
    ap.add_argument("--out", type=Path, default=Path("validation_v6/results/bat_pair_schema.json"))
    args = ap.parse_args()
    try:
        receipt = run(args.source)
    except Exception as exc:
        print(f"STRUCTURAL_PREFLIGHT_FAILED: {type(exc).__name__}: {exc}")
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "integrity": receipt["integrity"],
                      "schema": receipt["schema"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
