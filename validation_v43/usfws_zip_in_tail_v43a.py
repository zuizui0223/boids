#!/usr/bin/env python3
"""v43a: parse a pinned USFWS ZIP central directory already within a bounded tail.

One single official 206 Range request; no ZIP member data requested or read.
Historical v42/v43 stops are retained and not relabelled.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from usfws_zip_range_directory import (
    ORIGINAL_TOTAL, TAIL_BYTES, central_location, http_range, scan_directory,
)

PINNED_TAIL_SHA256="69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59"
OUT=Path("validation_v43/results/usfws_official_zip_intail_v43a.json")


def run(fetcher=None, expected_tail_sha256=PINNED_TAIL_SHA256):
    out={
        "programme":"v43a_official_usfws_original_zip_in_tail_source_metadata",
        "original_USFWS_reference":112151,
        "original_USFWS_download_id":165800,
        "official_full_archive_bytes_recorded":ORIGINAL_TOTAL,
        "original_v42_whole_zip_size_cap_stop_unchanged":True,
        "original_v43_second_range_transport_stop_unchanged":True,
        "single_exact_206_tail_range_only":True,
        "source_full_archive_sha256_verified":False,
        "bat_activity_or_species_numeric_outcomes_read":False,
        "original_member_payloads_requested_or_read":False,
        "complete_detector_effort_or_zeros_verified":False,
        "source_coordinates_member_names_or_site_locations_exported":False,
        "ecological_model_fitted":False,
    }
    start=ORIGINAL_TOTAL-TAIL_BYTES
    receipt,tail=http_range(start,ORIGINAL_TOTAL-1,fetcher=fetcher)
    out["tail_range_receipt"]=receipt
    if tail is None:
        out["status"]="TAIL_RANGE_SOURCE_STOP";return out
    checksum=hashlib.sha256(tail).hexdigest()
    out["same_original_tail_sha256"]=checksum
    out["pinned_original_tail_digest_matches"]=checksum==expected_tail_sha256
    if checksum!=expected_tail_sha256:
        out["status"]="PINNED_TAIL_CHECKSUM_MISMATCH_STOP";return out
    cd=central_location(tail)
    out["central_directory_locator"]=cd
    if cd["status"]!="STANDARD_ZIP_CENTRAL_DIRECTORY_LOCATED":
        out["status"]="ZIP_END_RECORD_SOURCE_STOP";return out
    off=cd["central_directory_offset"]
    size=cd["central_directory_size"]
    relative=off-start
    if relative<0 or relative+size>len(tail)-22:
        out["status"]="CENTRAL_DIRECTORY_NOT_FULLY_IN_VERIFIED_TAIL_STOP";return out
    # Full directory in previously verified 65,536 bytes. No second request.
    parsed=scan_directory(tail[relative:relative+size],cd["declared_entry_count"])
    out["central_directory_metadata"]=parsed
    out["status"]=parsed["status"]
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=OUT)
    args=p.parse_args()
    r=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V43A_USFWS_SINGLE_RANGE_DIRECTORY="+json.dumps(r,sort_keys=True))
    assert r["bat_activity_or_species_numeric_outcomes_read"] is False
    assert r["original_member_payloads_requested_or_read"] is False
    assert r["ecological_model_fitted"] is False
    assert r["original_v43_second_range_transport_stop_unchanged"] is True


if __name__=="__main__":
    main()
