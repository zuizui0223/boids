"""v75 original 2010 wild GPS and coeval native monthly NIOZ use-rank source.

SOURCE-ONLY gates on all 5 months before reading or scoring used raster index
ranks. Original GPS, bird IDs, exact stamps and model pixels remain ephemeral.
"""
from __future__ import annotations
import argparse
import json
import os
import tempfile
from pathlib import Path

from source_preflight import download_and_pin
from original_coeval_wadden_model_metadata import (
    authenticated_provider_file)
from native_monthly_exposure_source import (
    FIXED_SHA as OLD_NIOZ_SHA,native_readme_meaning)
from real_2010_monthly_nioz_gps_source_gate import original_all_2010_manifest
from wild_2010_modelled_tidal_exposure_rank import (
    MONTHS,GPS_SHA,PINNED_MODEL_SHA,ORIGINAL_GPS_RAW,
    original_all_wild_months,original_2010_native_month,geometric_preflight,
    combined_field_score)

def run(output):
    manifest=original_all_2010_manifest()
    raw_readme,proof=authenticated_provider_file(manifest["README.txt"])
    if proof["original_computed_sha256"]!=OLD_NIOZ_SHA["README.txt"]:
        raise ValueError("SOURCE_STOP_V75_ORIGINAL_PUBLISHER_README_SHA_CHANGED")
    meaning=native_readme_meaning(raw_readme)
    if not (meaning["native_exposure_variable_literal_mentioned"]
            and meaning["native_exposure_word_documented"]):
        raise ValueError("SOURCE_STOP_V75_NIOZ_README_MODEL_EXPOSURE_MEANING_CHANGED")
    with tempfile.TemporaryDirectory(prefix="v75_original_2010_wild_") as folder:
        f=Path(folder)/"original_Zenodo_2010.csv.gz"
        gps_manifest=download_and_pin(2010,f)
        if (gps_manifest.get("provider_md5_match") is not True or
            gps_manifest["original_sha256"]!=GPS_SHA):
            raise ValueError("SOURCE_STOP_V75_2010_ZENODO_GPS_SOURCE_SHA_DRIFT")
        months,qa=original_all_wild_months(f)
    assert qa["original_full_2010_raw_gps_rows_seen"]==ORIGINAL_GPS_RAW
    # Model originals are independently authenticated MD5 by NIOZ CKAN and
    # v74 source-only existing whole-year SHA, no use values yet inspected.
    geom={}
    proofs={}
    for month in MONTHS:
        filename=f"eco_av.2010{month:02d}.nc"
        raw,receipt=authenticated_provider_file(manifest[filename])
        if receipt["original_computed_sha256"]!=PINNED_MODEL_SHA[month]:
            raise ValueError("SOURCE_STOP_V75_V74_FIXED_MONTH_MODEL_SHA_CHANGED")
        proofs[filename]={
            "original_MD5_verified":True,
            "original_source_SHA256":receipt["original_computed_sha256"],
            "original_bytes":receipt["original_bytes"]}
        model=original_2010_native_month(raw,month)
        audit=geometric_preflight(month,months[month],model)
        geom[month]=audit
        s=audit["source_receipt"]
        print("V75_ORIGINAL_GPS_NIOZ_MONTH_SOURCE_BEFORE_OUTCOME "+json.dumps({
            "month":month,
            "original_hourly_fixes":s["original_gps_source_hourly_positions"],
            "original_birds":s["original_gps_source_birds"],
            "native_model_cells":s["source_native_model_geolocated_cells"],
            "native_GPS_with_1km_background":s["source_gps_with_at_least_twenty_1km_original_grid_cells"],
            "original_eligible_birds_with_20_fixes":s["source_original_bird_IDs_with_twenty_1km_complete_GPS"],
            "source_status":s["fixed_source_admission"]},sort_keys=True),flush=True)
    receipt={str(m):geom[m]["source_receipt"] for m in MONTHS}
    if any(r["fixed_source_admission"]!=
       "SOURCE_ADMITTED_V75_ORIGINAL_GPS_2010_MONTH_NATIVE_MODEL_1KM"
       for r in receipt.values()):
        answer={"source_admission":"NOT_ADMITTED_V75_FIXED_ALL_MONTHS_SOURCE",
                "wild_observed_tidal_modelled_use_effect":"NOT_ESTIMATED_SOURCE_GATE"}
    else:
        print("V75_ALL_FIVE_ORIGINAL_GEOGRAPHIC_AND_BIRD_MONTH_SOURCE_PASSED",flush=True)
        answer=combined_field_score(geom)
    result={
        "analysis":"V75_REAL_WILD_2010_SCHIER_TIDAL_EXPOSURE_MODEL_LOCAL_ORDINAL_RANK",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "frozen_protocol":"docs/V75_FROZEN_ORIGINAL_2010_TIDAL_MODEL_USED_PIXEL_LOCAL_RANK.md",
        "original_GPS_year":2010,
        "original_source_2010_Zenodo_gps_MD5_and_SHA256":{
            "original_provider_MD5_match":True,
            "original_source_SHA256":gps_manifest["original_sha256"],
            "original_source_gzip_bytes":gps_manifest["original_bytes"]},
        "original_source_model_readme_unchanged":meaning,
        "original_source_NIOZ_native_2010_month_SHA":proofs,
        "source_original_2010_all_months_visible_GPS_positions_replayed":qa,
        "fixed_five_months_native_model_geographic_gate_BEFORE_OUTCOME":receipt,
        "original_wild_2010_bird_model_index_field_result":answer,
        "source_model_index_is_ordinal_units_not_originally_verified":True,
        "no_causal_daylength_tide_or_measured_foraging_inferred":True,
        "no_original_GPS_individual_tag_timestamp_latlon_or_model_cells_saved":True,
        "no_2011_NIOZ_geo_lat_imputed":True}
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    primary=answer.get("original_used_vs_local_ordinal_rank_bird_equal_primary")
    print("V75_AUTHENTIC_WILD_GPS_2010_MONTHLY_TIDE_MODEL_RANK_RESULT "+json.dumps({
        "source_admission":answer.get("source_admission"),
        "original_independent_birds":primary["source_original_birds"] if primary else None,
        "source_bird_months":primary["source_admitted_bird_months"] if primary else None,
        "mean_local_ordinal_midrank_minus0p5":
            primary["equal_month_within_bird_then_bird_equal_mean"] if primary else None,
        "bird_block_bootstrap_95":
            primary["whole_bird_cluster_bootstrap_percentile95"] if primary else None,
        "original_positive_birds":
            primary["source_original_birds_with_positive_contrast"] if primary else None,
        "primary_status":answer.get("frozen_primary_status",
                                   "NOT_ESTIMATED_SOURCE_GATE"),
        "model_is_numeric_ordinal_and_NOT_directly_measured":True},sort_keys=True),flush=True)
    print("V75_ORIGINAL_ZENODO_WILD_NIOZ_MONTHLY_HABITAT_SOURCE_AND_RESULT_COMPLETED",flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    run(p.parse_args().output)
