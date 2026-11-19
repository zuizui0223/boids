#!/usr/bin/env python3
"""Source-only structural audit for pinned Tunnel_2026 Carollia MATLAB files.

Never reads original numerical animal/sonar outcomes: h5py object keys, shape,
dtype and metadata only. Does NOT establish causal sensing or motor forecasts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import h5py

SOURCE_COMMIT = "59928a71887d521fec143080b0b187736c046a0e"
MANIFEST = Path("docs/BAT_ACTIVE_SENSING_TUNNEL_SOURCE_INVENTORY_V1.json")
DEFAULT_OUT = Path("validation_v29/results/tunnel_source_schema_audit_v29.json")
REQUIRED_FIELDS = (
    "RESULTS/calls/tSec",
    "RESULTS/track/tSec",
    "RESULTS/track/pos_sm",
    "RESULTS/beam/rel_deg",
    "RESULTS/beam/fitR",
)
OPTIONAL_FIELDS = (
    "RESULTS/calls/XYZ_sm",
    "RESULTS/calls/trkIdx",
    "RESULTS/turns/peakTime_s",
    "RESULTS/turns/angleDeg",
    "RESULTS/intensity/SL10cm_best_dB",
)


def git_blob_sha1(path: Path) -> str:
    """Git content SHA-1 with correct 'blob SIZE\0' prefix."""
    digest = hashlib.sha1()
    digest.update(b"blob " + str(path.stat().st_size).encode("ascii") + b"\0")
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 18), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 18), b""):
            digest.update(block)
    return digest.hexdigest()


def _ds_shape(node):
    """Dimensions only: never evaluates a source dataset."""
    if isinstance(node, h5py.Dataset):
        return {"shape": list(node.shape), "dtype": str(node.dtype)}
    if isinstance(node, h5py.Group):
        return {"group_keys": sorted(str(key) for key in node.keys())}
    return {"type": type(node).__name__}


def inspect_mat(path: Path) -> dict:
    """Use HDF5 metadata exclusively, avoiding all original-value reads."""
    if not h5py.is_hdf5(path):
        return {"hdf5_supported": False, "structure_status": "NOT_HDF5"}
    with h5py.File(path, "r") as h5:
        top_keys = sorted(k for k in h5.keys() if k != "#refs#")
        required = {p: p in h5 for p in REQUIRED_FIELDS}
        optional = {p: p in h5 for p in OPTIONAL_FIELDS}
        field_info = {
            p: _ds_shape(h5[p])
            for p in REQUIRED_FIELDS + OPTIONAL_FIELDS
            if p in h5
        }
        n_calls = None
        calls_path = "RESULTS/calls/tSec"
        if calls_path in h5 and isinstance(h5[calls_path], h5py.Dataset):
            n_calls = math.prod(h5[calls_path].shape)
        beam_shape = field_info.get("RESULTS/beam/rel_deg", {}).get("shape")
        beam_n = math.prod(beam_shape) if beam_shape is not None else None
        track_shape = field_info.get("RESULTS/track/tSec", {}).get("shape")
        track_n = math.prod(track_shape) if track_shape is not None else None
        pos_shape = field_info.get("RESULTS/track/pos_sm", {}).get("shape")
        xyz_shape = field_info.get("RESULTS/calls/XYZ_sm", {}).get("shape")

        return {
            "hdf5_supported": True,
            "top_level_keys_excluding_refs": top_keys,
            "required_fields_present": required,
            "optional_fields_present": optional,
            "metadata_only_field_structure": field_info,
            "call_timestamp_array_length_from_shape": n_calls,
            "beam_array_length_from_shape": beam_n,
            "call_beam_shape_matched": (
                n_calls == beam_n if n_calls is not None and beam_n is not None else None
            ),
            "track_time_array_length_from_shape": track_n,
            "track_pos_sm_shape": pos_shape,
            "track_pos_sm_time_and_xyz_structurally_matched": (
                len(pos_shape) == 2 and 3 in pos_shape and track_n in pos_shape
                if pos_shape is not None and track_n is not None else None
            ),
            "calls_XYZ_sm_shape": xyz_shape,
            "all_required_fields_present": all(required.values()),
            "numeric_animal_or_sonar_dataset_values_accessed": False,
        }


def audit(source_root: Path, manifest: dict) -> dict:
    assert manifest["github_ref"] == SOURCE_COMMIT, "Source commit unexpectedly changed"
    assert manifest["trial_mat_n"] == len(manifest["git_blobs"]) == 30
    results = []
    source_root = source_root.resolve()
    for source in manifest["git_blobs"]:
        rel = source["path"]
        if rel.startswith("/") or ".." in Path(rel).parts:
            raise ValueError("Unexpected source path in manifest")
        path = source_root / rel
        row = {"path": rel, "expected_git_blob_sha1": source["git_blob_sha1"]}
        if not path.is_file():
            row["status"] = "SOURCE_MISSING"
            results.append(row)
            continue
        row["source_file_bytes"] = path.stat().st_size
        row["git_blob_sha1"] = git_blob_sha1(path)
        row["sha256"] = sha256(path)
        row["bytes_and_git_sha_verified"] = (
            row["source_file_bytes"] == source["size_bytes"]
            and row["git_blob_sha1"] == source["git_blob_sha1"]
        )
        if not row["bytes_and_git_sha_verified"]:
            row["status"] = "SOURCE_MISMATCH_STOP"
            results.append(row)
            continue
        try:
            row.update(inspect_mat(path))
            row["status"] = (
                "STRUCTURE_PRESENT_SOURCE_ONLY"
                if row.get("all_required_fields_present")
                else "STRUCTURE_INCOMPLETE_SOURCE_ONLY"
            )
        except (OSError, ValueError, TypeError, KeyError) as exc:
            row["status"] = "HDF5_METADATA_ACCESS_STOP"
            row["source_metadata_error_type"] = type(exc).__name__
        results.append(row)

    verified = sum(bool(r.get("bytes_and_git_sha_verified")) for r in results)
    present = sum(r["status"] == "STRUCTURE_PRESENT_SOURCE_ONLY" for r in results)
    complete = verified == len(results) == 30
    all_structural = present == len(results)
    call_beam = sum(r.get("call_beam_shape_matched") is True for r in results)
    label_counts = manifest["trial_counts_by_label"]
    assert sum(label_counts.values()) == len(results)
    return {
        "programme": "bat_active_sensing_tunnel_source_schema_v29",
        "source_owner_repo": manifest["github_repository"],
        "original_commit": SOURCE_COMMIT,
        "source_reported_species": manifest["reported_paper_species"],
        "source_trials_listed": len(results),
        "source_trial_labels_listed": sorted(label_counts),
        "source_trials_by_label": label_counts,
        "original_files_git_blob_verified_n": verified,
        "all_original_files_hash_and_size_verified": complete,
        "hdf5_matlab_fields_structurally_complete_n": present,
        "call_beam_lengths_matched_n": call_beam,
        "source_original_numeric_animal_or_sonar_values_read": False,
        "source_code_reconstruction_warning": (
            "MATLAB carollia_build_track_from_calls.m reconstructs continuous "
            "trajectories from per-call localized positions by interpolation; "
            "track/sonar independence must not be assumed."
        ),
        "independent_obstacle_clearance_geometry_confirmed": False,
        "calibrated_usable_echo_probability_confirmed": False,
        "roussettus_raw_paired_data_in_checked_repository": False,
        "primary_q_law_admitted": False,
        "primary_q_law_stop_reason": (
            "Independent d_free and p_usable not yet verified; "
            "other species raw Rousettus source missing. "
            "No behavior value, effect, or future-turn prediction opened."
        ),
        "carollia_call_track_beam_schema_gate": (
            "SOURCE_METADATA_READY_NEEDS_INDEPENDENCE_AUDIT"
            if all_structural else
            "SOURCE_STRUCTURE_INCOMPLETE_OR_UNVERIFIED"
        ),
        "source_row_details": results,
        "source_level_biological_conclusion": "NONE",
        "prior_frozen_batter_and_boids_results_unchanged": True,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, default=MANIFEST)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()
    with args.manifest.open("r", encoding="utf-8") as fd:
        manifest = json.load(fd)
    result = audit(args.source_root, manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    headline_keys = [
        "source_trials_listed",
        "original_files_git_blob_verified_n",
        "hdf5_matlab_fields_structurally_complete_n",
        "call_beam_lengths_matched_n",
        "carollia_call_track_beam_schema_gate",
        "primary_q_law_admitted",
        "source_level_biological_conclusion",
    ]
    print("AUDIT_SUMMARY=" + json.dumps({k: result[k] for k in headline_keys}, sort_keys=True))
    assert result["all_original_files_hash_and_size_verified"], "Pinned source bytes unavailable"
    assert result["source_original_numeric_animal_or_sonar_values_read"] is False


if __name__ == "__main__":
    main()
