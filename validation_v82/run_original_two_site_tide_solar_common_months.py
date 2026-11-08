"""v82 authentic original 2010 wild GPS two-island equal-calendar tide×solar test.

Post-v81 exploratory. Source real bird month and all seven 2010 coeval NIOZ
model grids, June/July explicit INFERRED model latitude, measured RWS tide
10-min × each station, true astronomy. Score within-original-bird island
D and between-island independent bird bootstrap ONLY AFTER both sites have
four-condition original source admissions. No raw bird IDs, tracks, times,
RWS heights or modeled pixel fields exported.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from datetime import timedelta
from pathlib import Path

from original_nioz_static_2010_grid import original_manifest
from authenticated_nioz_static_template_model import (
    authenticated_template_and_model_months)
from source_preflight import download_and_pin
from ameland_external_site import original_gps
from original_ameland_native_gps_source import (
    original_ameland_2010_hourly)
from wild_2010_modelled_tidal_exposure_rank import (
    original_all_wild_months,GPS_SHA,ORIGINAL_GPS_RAW)
from original_rws_cached_transport import (
    OriginalRwsCache,observed_original_rws_year_cached)
from tide_solar_four_way_source_and_effect import ADMIT
from two_island_common_month_bird_contrast import (
    SOURCE_MONTHS,LATE_MONTHS,SCHIER_SOURCE,AMELAND_SOURCE,
    prepare_whole_site,true_fourcell_source,new_two_site_difference,
    EXPECTED_V77_LATE_SCHIER,EXPECTED_V81_FULL_AMELAND,
    EXPECTED_V78_NATIVE_AMELAND)

ORIGINAL_SCHIER_GPS_RAW=282920
ORIGINAL_AMELAND_GPS_RAW=119507
ORIGINAL_AMELAND_SHA="c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c"
GAUGE_CODES={
    "Schier":"schiermonnikoog.waddenzee",
    "Ameland":"ameland.nes"}
ORIGINAL_GAUGE_ROWS=52561

def _fetch_original_two_site_GPS():
    with tempfile.TemporaryDirectory(prefix="v82_two_island_original_GPS_") as d:
        sfile=Path(d)/"original_Schier_2010.csv.gz"
        afile=Path(d)/"original_Ameland_2010.csv.gz"
        source_s=download_and_pin(2010,sfile)
        source_a=original_gps(2010,afile)
        if (not source_s["provider_md5_match"] or source_s["original_sha256"]!=GPS_SHA
            or not source_a["provider_original_md5_matched"]
            or source_a["original_sha256"]!=ORIGINAL_AMELAND_SHA):
            raise ValueError("SOURCE_STOP_V82_2ISLAND_ORIGINAL_GPS_PROVIDER_MD5_SHA")
        actual_s,qa_s=original_all_wild_months(
            sfile,allowed_months=SOURCE_MONTHS,
            expected_month_counts=SCHIER_SOURCE)
        actual_a,qa_a=original_ameland_2010_hourly(
            afile,allowed_months=SOURCE_MONTHS)
        for m in SOURCE_MONTHS:
            a=qa_a["source_fixed_2010_Aug_to_Dec_hourly_bird_fixes"][str(m)]
            if (a["original_Ameland_native_hourly_locations"],
                a["original_distinct_birds"])!=AMELAND_SOURCE[m]:
                raise ValueError("SOURCE_STOP_V82_PRIOR_ORIGINAL_V79_AMELAND_SOURCE_DRIFT")
        if (qa_s["original_full_2010_raw_gps_rows_seen"]!=ORIGINAL_SCHIER_GPS_RAW
            or qa_a["original_provider_RAW_GPS_fixes"]!=ORIGINAL_AMELAND_GPS_RAW):
            raise ValueError("SOURCE_STOP_V82_ORIGINAL_PUBLIC_GPS_ANNUAL_SIZE")
    return (actual_s,actual_a),{
        "original_Zenodo_Schier_2010_publisher_MD5_SHA_verified":True,
        "original_Zenodo_Schier_gps_sha256":source_s["original_sha256"],
        "original_Zenodo_Ameland_2010_publisher_MD5_SHA_verified":True,
        "original_Zenodo_Ameland_gps_sha256":source_a["original_sha256"],
        "original_original_hourly_GPS_source_Schier_2010":qa_s,
        "original_original_hourly_GPS_source_Ameland_2010":qa_a}

def _original_gauge(station,cache):
    tide,proof=observed_original_rws_year_cached(cache,station,2010)
    if (proof["gauge_rows"]!=ORIGINAL_GAUGE_ROWS or
        tide.provenance!="observed" or len(tide.times)!=ORIGINAL_GAUGE_ROWS
        or tide.times[1]-tide.times[0]!=timedelta(minutes=10)):
        raise ValueError("SOURCE_STOP_V82_ORIGINAL_RWS_AUTHENTIC_2010_TIDE")
    return tide,{"original_RWS_measured_tenminute_NAP":ORIGINAL_GAUGE_ROWS,
                 "source_station":station,
                 "year":2010,
                 "RWS_observed_only_no_synthetic_or_missing_time_interpolation":True}

def run(output,cache_dir):
    native_models,native_qa=authenticated_template_and_model_months(
        original_manifest())
    if sorted(native_models)!=list(SOURCE_MONTHS):
        raise ValueError("SOURCE_STOP_V82_ORIGINAL_NIOZ_JUN_DEC_INFERRED_MONTHS_CHANGED")
    print("V82_ORIGINAL_NIOZ_STATIC_MODEL_MESH_SOURCE_OK "+
          json.dumps({"original_model_months":list(SOURCE_MONTHS),
              "original_2010_JuneJuly_lat_were_MISSING":True,
              "2009_independent_source_grid_controls_passed":native_qa[
                  "original_2010_Jan_and_2009_Jan_Aug_exact_grid_provenance_verified"],
              "NIOZ_original_time_expo_units":"UNKNOWN",
              "JuneJuly_lat_mode":"EXPLICITLY_INFERRED_FROM_ORIGINAL_JAN2010_STATIC_MODEL_GRID"},
              sort_keys=True),flush=True)
    (gps_s,gps_a),gpsproof=_fetch_original_two_site_GPS()
    geos={}
    geoqa={}
    for site,gps in (("Schier",gps_s),("Ameland",gps_a)):
        matched,source=prepare_whole_site(site,gps,native_models)
        geos[site]=matched
        geoqa[site]=source
        print("V82_ORIGINAL_TWO_SITE_GPS_MODEL_GEO_SOURCE_BEFORE_OUTCOME "+
              json.dumps({
                  "site":site,
                  "real_true_GPS_2010_months":len(gps),
                  "all_original_month_geographic_sources_admitted":
                      source["all_seven_original_model_and_bird_sources_admitted"],
                  "original_months":{
                      k:{"original_real_birds":v["original_real_bird_IDs_in_month"],
                         "original_hourly_fixes":v["original_hourly_GPS_source_positions"],
                         "source_300m_native_model_GPS":
                            v["genuine_GPS_source_nearest_model_grid_within300m"],
                         "source_status":v["fixed_source_admission"],
                         "JuneJuly_spatial_grid":v[
                             "original_native_JunJul_lat_missing_requires_labelled_static_template"]}
                       for k,v in source["original_month_source_receipts"].items()}},
                   sort_keys=True),flush=True)
    source_ok=all(q["all_seven_original_model_and_bird_sources_admitted"]
                  for q in geoqa.values())
    receipts={}
    pairdata={}
    old_replay=None
    new_result={
        "site_comparison_source_gate":"NOT_ADMITTED_V82_BOTH_ISLAND_MONTHS",
        "common_calendar_bird_site_interaction_difference":
            "NOT_ESTIMATED_SOURCE_GATE"}
    if source_ok:
        # Two genuine independent original 2010 RWS station measurements,
        # both verified BEFORE computing the models' bird-used-cell ranks.
        for site in ("Schier","Ameland"):
            cache=OriginalRwsCache(
                str(Path(cache_dir)/site.lower()),sleeper=time.sleep)
            tide,receipt=_original_gauge(GAUGE_CODES[site],cache)
            four,qa=true_fourcell_source(geos[site],tide)
            pairdata[site]=four
            receipts[site]=qa
            receipts[site]["original_independent_observed_RWS_gauge_source"]=receipt
            receipts[site]["original_RWS_transport_summary"]=cache.snapshot()
            source=qa["all_four_conditions_same_real_bird_month_height_source"]
            print("V82_ORIGINAL_GPS_TRUE_TIDE_SOURCE_SAME_2010_MONTHS "+
                  json.dumps({"site":site,
                      "original_2010_complete_four_cell_groups":
                          source["original_four_way_exact_same_bird_month_RWS_height_groups"],
                      "original_genuine_GPS_fix_count":
                          source["original_four_way_source_fix_count"],
                      "original_real_distinct_birds":
                          source["original_birds_in_all_four_tide_and_light_conditions"],
                      "explicit_template_JunJuly_four_cell_groups":
                          qa["original_source_four_condition_groups_using_INFERRED_JunJul_mesh"],
                      "true_native_AugDec_four_cell_groups":
                          qa["original_source_four_condition_groups_using_GENUINE_native_AugDec_model_coords"],
                      "source_gate":source["admission"]},sort_keys=True),flush=True)
        # Separate old native-only island source failure must NOT be rescued.
        # Source-only data from Ameland Aug–Dec should still have 267/7 and
        # previously frozen biological effect remains NOT_ESTIMATED.
        for site in ("Schier","Ameland"):
            from matched_tide_state_day_night_native_ranks import tide_light_source_groups
            from tide_solar_four_way_source_and_effect import fourway_source_only
            cache=OriginalRwsCache(
                str(Path(cache_dir)/site.lower()),sleeper=time.sleep)
            tide,_=_original_gauge(GAUGE_CODES[site],cache)
            late={m:geos[site][m] for m in LATE_MONTHS}
            from two_island_common_month_bird_contrast import STATUS
            pp,source=tide_light_source_groups(
                late,tide,required_geo_status=STATUS,required_months=LATE_MONTHS)
            old4,oldsource=fourway_source_only(pp,source,verify_original_replay=False)
            receipt_expected=(EXPECTED_V77_LATE_SCHIER if site=="Schier"
                              else EXPECTED_V78_NATIVE_AMELAND)
            if (len(old4),oldsource["original_birds_in_all_four_tide_and_light_conditions"])!=(
                receipt_expected[0],receipt_expected[1]):
                raise ValueError("SOURCE_STOP_V82_PRIOR_NATIVE_ONLY_TIDE_LIGHT_SITE_DRIFT")
            if site=="Ameland" and oldsource["admission"]==ADMIT:
                raise ValueError("SOURCE_STOP_V82_V78_7BIRD_SOURCE_WAS_UNSCORED")
            if old_replay is None:old_replay={}
            old_replay[site]={
                "prior_native_2010_AugDec_original_4way_source_groups":len(old4),
                "prior_native_2010_AugDec_original_birds":
                    oldsource["original_birds_in_all_four_tide_and_light_conditions"],
                "old_source_gate":oldsource["admission"],
                "old_Ameland_7bird_ecology_NOT_RESCORED":site=="Ameland"}
        print("V82_PRIOR_TWO_ISLAND_NATIVE_ONLY_SOURCE_FIDELITY "+
              json.dumps(old_replay,sort_keys=True),flush=True)
        # All source gates checked BEFORE any NEW animal-used model rank read.
        new_result=new_two_site_difference(
            geos["Schier"],geos["Ameland"],
            pairdata["Schier"],pairdata["Ameland"],
            receipts["Schier"],receipts["Ameland"])
    report={
        "analysis":"V82_REAL_ORIGINAL_2010_COMMON_JUN_DEC_SCHIER_AMELAND_TRUE_TIDE_BY_SOLAR_TWO_SITE_WILD_BIRD_CONTRAST",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "frozen_protocol":"docs/V82_FROZEN_TWO_ISLAND_COMMON_MONTHS_TRUE_TIDE_SOLAR_SITE_CONTRAST.md",
        "original_NIOZ_model_month_2009_and_2010_static_mesh_authenticated":native_qa,
        "original_Zenodo_2010_site_separate_wild_GPS_publisher_source":gpsproof,
        "original_genuine_year_and_month_source_preflights":geoqa,
        "original_two_station_measured_RWS_four_cell_source":receipts,
        "prior_native_only_bird_source_gates_unchanged":old_replay,
        "new_common_year_month_Schier_minus_Ameland_bird_effect_and_bootstrap":
            new_result,
        "both_sites_frozen_original_7month_source_admitted":source_ok,
        "2010_JunJul_original_model_lat_is_MISSING_in_both_sites":True,
        "original_NIOZ_monthly_model_index_units_UNVERIFIED":True,
        "original_GPS_UTC_or_GPS_recorder_clock_not_calibrated":True,
        "only_two_sites_same_species_same_Wadden_coast_NOT_general_terrestrial_causal_or_cross_taxon":True,
        "no_original_ID_or_per_bird_values_exact_times_GPS_geography_model_pixels_RWS_rows_exported":True}
    file=Path(output)
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    q=new_result.get("primary_same_original_2010_JuneDec_site_CONTRAST_S_minus_A")
    print("V82_ORIGINAL_TWO_ISLAND_COMMON_SOURCE_BIRD_CLUSTER_CONTRAST "+
          json.dumps({
             "source_both_sites_admitted":source_ok,
             "source_interaction_status":
                new_result["site_comparison_source_gate"],
             "same_2010_JunDec_Schier_D":
                new_result.get("new_common_month_original_bird_site_effects",{}).get(
                    "Schier",{}).get("site_original_bird_equal_D_floodNightDay_minus_ebbNightDay"),
             "same_2010_JunDec_Ameland_D":
                new_result.get("new_common_month_original_bird_site_effects",{}).get(
                    "Ameland",{}).get("site_original_bird_equal_D_floodNightDay_minus_ebbNightDay"),
             "site_difference_Schier_minus_Ameland":
                q["Schier_bird_equal_minus_Ameland_bird_equal"] if q else None,
             "source_site_independent_bird_bootstrap95":
                q["original_site_independent_whole_bird_10000_bootstrap95"] if q else None,
             "Schier_original_birds":q["original_true_birds_in_Schier"] if q else None,
             "Ameland_original_birds":q["original_true_birds_in_Ameland"] if q else None,
             "strict_status":q["point_positive_or_negative_status"] if q else
                "NOT_ESTIMATED_SOURCE_GATE",
             "no_2011_GPS_or_NEW_species_used":True
          },sort_keys=True),flush=True)
    print("V82_ORIGINAL_COMMON_2010_TWO_ISLAND_SITE_CONTRAST_COMPLETED",flush=True)
    return report

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True)
    a.add_argument("--source-cache-dir",
       default=os.environ.get("BOIDS_ORIGINAL_RWS_CACHE_DIR",
                              "/tmp/boids_original_RWS_v82"))
    opts=a.parse_args()
    run(opts.output,opts.source_cache_dir)
