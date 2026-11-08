"""v73 original source-only geographic admission, then January 2010 wild model index.

This workflow intentionally uses exactly one original animal GPS year (2010)
and exactly one coeval original monthly hydro model (2010-01). No 2011 native
latitude recovery, extrapolation, unmeasured foraging or tide/daylight test.
"""
from __future__ import annotations
import argparse,json,os,tempfile
from pathlib import Path

from source_preflight import download_and_pin
from original_coeval_wadden_model_metadata import original_metadata,authenticated_provider_file
from native_monthly_exposure_source import FIXED_SHA,native_readme_meaning,original_native_month
from wild_gps_native_month_exposure import (
    original_visible_january_2010_fixes,grid_source,map_geo_source_only,
    model_used_vs_local)

def run(out):
    src=original_metadata()
    original_receipts={}
    original={}
    for name in ("README.txt","eco_av.201001.nc"):
        raw,receipt=authenticated_provider_file(src["source_original_resources"][name])
        if receipt["original_computed_sha256"]!=FIXED_SHA[name]:
            raise ValueError("SOURCE_STOP_V73_IMMUTABLE_ORIGINAL_NIOZ_SHA_CHANGED")
        original[name]=raw
        original_receipts[name]=receipt
    meaning=native_readme_meaning(original["README.txt"])
    # Evidence confirms a monthly modeled tidal flat time exposure *index*
    # but lacks units: do not turn its numeric [0,1] into measured hours.
    if not meaning["native_exposure_variable_literal_mentioned"] or not meaning["native_exposure_word_documented"]:
        raise ValueError("SOURCE_STOP_V73_NIOZ_MODEL_EXPOSURE_SEMANTIC_NOT_SUPPORTED")
    hydro=grid_source(original_native_month(
        original["eco_av.201001.nc"],"eco_av.201001.nc"))
    with tempfile.TemporaryDirectory(prefix="v73_original_Jan2010_GPS_") as td:
        original_path=Path(td)/"2010-original.csv.gz"
        gps_manifest=download_and_pin(2010,original_path)
        if gps_manifest.get("provider_md5_match") is not True:
            raise ValueError("SOURCE_STOP_V73_GPS_PUBLISHER_MD5_FAILED")
        observations,gps_qa=original_visible_january_2010_fixes(original_path)
    matches,source_only_audit=map_geo_source_only(observations,hydro)
    print("V73_ORIGINAL_WILD_2010_GEO_SOURCE_ONLY "+json.dumps({
        "original_gps_total_2010_annual_rows":gps_qa["raw_original_annual_rows_seen"],
        "original_january_hourly_bird_fixes":gps_qa["original_valid_visible_January_distinct_bird_hour_fixes"],
        "original_january_birds":gps_qa["original_visible_January_bird_ID_count"],
        "native_grid_cells":source_only_audit["source_2010_NIOZ_native_grid_cells"],
        "original_geo_300m_count":source_only_audit["native_geo_matching_within_300m"],
        "original_geo_fraction":source_only_audit["native_geo_matching_coverage_fraction"],
        "original_birds_at_least_20_geo":source_only_audit["source_birds_with_at_least_20_mapped_original_fixes"],
        "original_full_1km_background_count":len(matches),
        "status":source_only_audit.get("source_admission","STAGE_2_PENDING_SOURCE_REPLAY")},sort_keys=True),flush=True)
    # map_geo_source_only is a *source geometry* admission. A failed gate
    # prevents model use-local contrast and its outcome bootstrap.
    if source_only_audit.get("source_admission","").startswith("NOT_ADMITTED"):
        result={"source_gate":source_only_audit,
                "original_field_exposure_index_contrast":"NOT_ESTIMATED_SOURCE_GATE"}
    else:
        # Deliberately repeat the identical fixed source gate, checking
        # source -> native 1km opportunity without data-dependent tuning.
        result=model_used_vs_local(observations,hydro)
    report={
        "analysis":"V73_GENUINE_JAN_2010_WADDEN_BIRD_HOURLY_LOCATION_NATIVE_MODEL_INDEX",
        "original_source_DOIs":{
            "GPS":"https://doi.org/10.5281/zenodo.22296922",
            "NIOZ_model":"https://doi.org/10.25850/nioz/7b.b.n"},
        "original_Zenodo_2010_publisher_MD5_verified":True,
        "original_Zenodo_2010_GPS_SHA256":gps_manifest["original_sha256"],
        "original_Zenodo_2010_gzip_bytes":gps_manifest["original_bytes"],
        "original_NIOZ_provider_MD5_SHA256_verified":original_receipts,
        "original_model_exposure_README_semantics":meaning,
        "source_2010_original_visible_january_GPS_QA":gps_qa,
        "original_source_vs_2010_native_model_local_index":result,
        "frozen_protocol":"docs/V73_FROZEN_WILD_2010_GPS_LOCAL_MODEL_EXPOSURE_INDEX.md",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "2011_NIOZ_original_lat_MISSING_NO_2011_JOIN":True,
        "2010_model_exposure_numeric_units_UNKNOWN":True,
        "not_measured_foraging_or_real_intertidal_exposure":True,
        "no_tidal_daylength_causal_or_new_prediction_result":True,
        "no_original_individual_tag_exact_GPS_UTM_or_model_pixel_exported":True}
    target=Path(out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    main=result.get("original_field_primary")
    print("V73_JANUARY_REAL_BIRD_MODELED_EXPOSURE_FIELD_OR_SOURCE_STOP "+
          json.dumps({"source_status":result["source_gate"].get("source_admission"),
                      "real_fixes":main["source_original_January_positions_with_1km_native_model_reference"] if main else None,
                      "individuals":main["source_original_detected_2010_bird_count"] if main else None,
                      "real_bird_equal_model_numeric_index_contrast":
                          main["source_bird_equal_model_numeric_index_used_minus_nearby"] if main else None,
                      "whole_bird_cluster_bootstrap95":
                          main["whole_bird_cluster_bootstrap_95"] if main else None,
                      "birds_positive":main["source_birds_positive_local_index_contrast"] if main else None,
                      "field_status":main["source_field_status"] if main else "NOT_ESTIMATED_SOURCE_GATE",
                      "missing_2011_grid_not_joined":True},sort_keys=True),flush=True)
    print("V73_ORIGINAL_NATIVE_2010_GPS_SOURCE_ANALYSIS_COMPLETED",flush=True)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    run(p.parse_args().output)
