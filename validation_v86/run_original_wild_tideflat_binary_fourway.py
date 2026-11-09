"""v86 authentic wild 2010 Schier/Ameland tidal-flat POSITION-use binary.

Real original Zenodo bird GPS, two official RWS 10-minute tide stations,
actual WMR 2008–12 mid/high littoral source polygons, original NIOZ
2009/2010 native model geographic coordinates ONLY (JuneJuly model
lat explicitly inferred from verified static computational mesh).

Original true RWS tidal-height/ebb-flood × astronomical light fourway
source groups must exactly replay v82 for BOTH sites before Y(B) is read.
Y(B) is GPS nearest NIOZ model center WMR class3/4, not NIOZ exposure
value, observed feeding or true habitat availability. No bird tags,
exact GPS positions/timestamps, raw RWS heights or WMR polygons exported.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from original_nioz_static_2010_grid import original_manifest
from authenticated_nioz_static_template_model import (
    authenticated_template_and_model_months)
from original_rws_cached_transport import OriginalRwsCache
from run_original_two_site_tide_solar_common_months import (
    _fetch_original_two_site_GPS,_original_gauge,GAUGE_CODES)
from two_island_common_month_bird_contrast import (
    SOURCE_MONTHS,prepare_whole_site,true_fourcell_source)
from midhigh_intertidal_source_and_fourway import (
    classify_native_2010_model_sites)
from wild_tideflat_binary_fourway import (
    hard_before_outcome_both_sites,
    score_binary_original_two_sites_if_source_gated,
    FROZEN_SOURCE_REAL_2010)

ORIGINAL_TIME_RESOLUTION_YEAR=2010

def run(output,cache_dir):
    native_models,native_source=authenticated_template_and_model_months(
        original_manifest())
    if sorted(native_models)!=list(SOURCE_MONTHS):
        raise ValueError("SOURCE_STOP_V86_GEO_SOURCE_NOT_EXACT_SAME_2010_JUN_DEC")
    native_reference=native_models[8]["xy"]
    if native_reference.shape!=(398520,2):
        raise ValueError("SOURCE_STOP_V86_ORIGINAL_2010_NATIVE_GRID_NOT_398520")
    for month in SOURCE_MONTHS:
        if not (native_reference==native_models[month]["xy"]).all():
            raise ValueError("SOURCE_STOP_V86_NIOZ_MONTHLY_MODEL_NATIVE_GRID_CHANGED")
    print("V86_AUTHENTIC_ORIGINAL_NIOZ_2010_NATIVE_GEOMETRY_SOURCE "+
          json.dumps({
              "2010_months":list(SOURCE_MONTHS),
              "native_cells":len(native_reference),
              "original_2010_June_July_lat_still_missing_and_EXPLICIT_model_template":True,
              "NIOZ_time_expo_NOT_used_for_binary_Y":True},sort_keys=True),
          flush=True)

    # Publisher WMR source content hash and original 2010 native pixel
    # class-mask hashes pinned by *two independent* original WFS reads/site
    # before any original wild GPS habitat outcome in v85D.
    classes={}
    class_receipts={}
    for site in ("Schier","Ameland"):
        q=classify_native_2010_model_sites(native_reference,site)
        classes[site]=q
        class_receipts[site]=q["source_record"]
        print("V86_AUTHENTIC_PUBLISHED_WMR_NATIVE_0_6_GEOGRAPHY_SHA_SOURCE "+
              json.dumps({
                 "site":site,
                 "all_original_WMR_geopolygons":
                     q["source_record"]["original_WMR_publisher_polygon_count"],
                 "canonical_original_WMR_0_6_source_SHA":
                     q["source_record"][
                       "source_original_WMR_ALL_CODE0_TO6_canonical_geometry_SHA256"],
                 "original_2010_NIOZ_native_class3_4_index_SHA":
                     q["source_record"][
                       "source_true_native_2010_mid_high_class_grid_vector_SHA256"],
                 "native_middle_littoral_model_centers":
                     q["source_record"]["native_model_center_count_mid3"],
                 "native_high_littoral_model_centers":
                     q["source_record"]["native_model_center_count_high4"],
                 "no_original_wild_GPS_Y_has_been_read":True},
                 sort_keys=True),flush=True)

    (schier,ameland),gps_receipts=_fetch_original_two_site_GPS()
    original_source={}
    original_source_receipts={}
    for site,monthly in (("Schier",schier),("Ameland",ameland)):
        source,qa=prepare_whole_site(site,monthly,native_models)
        if not qa["all_seven_original_model_and_bird_sources_admitted"]:
            raise ValueError("SOURCE_STOP_V86_PREVIOUS_V82_SOURCE_MONTH_GPS_FAILED")
        original_source[site]=source
        original_source_receipts[site]=qa
        print("V86_ORIGINAL_TRUE_ZENODO_2010_GPS_MONTH_PREMATCH_SOURCE "+
              json.dumps({"site":site,
                   "true_original_GPS_model_2010_months":len(source),
                   "native_GPS_month_source_admitted":True,
                   "original_GPS_per_month":{
                     x:{"genuine_birds":d["original_real_bird_IDs_in_month"],
                        "native_hourly_GPS":d["original_hourly_GPS_source_positions"]}
                     for x,d in qa["original_month_source_receipts"].items()},
                   "NOT_YET_a_WMR_tideflat_use_effect":True},
                 sort_keys=True),flush=True)

    tide_source={}
    matched={}
    for site in ("Schier","Ameland"):
        cache=OriginalRwsCache(
            str(Path(cache_dir)/site.lower()),sleeper=time.sleep)
        tide,original_gauge=_original_gauge(GAUGE_CODES[site],cache)
        four,qa=true_fourcell_source(original_source[site],tide)
        tide_source[site]={
            "source_original_observed_2010_tenminute_WATHTE_NAP":original_gauge,
            "real_original_tide_and_solar_source_four_conditions":
                qa["all_four_conditions_same_real_bird_month_height_source"],
            "original_RWS_source_transport":cache.snapshot()}
        matched[site]=(four,qa)
        print("V86_REAL_2010_OBSERVED_RWS_TIDE_ASTRO_FOUR_CONDITION_SOURCE "+
              json.dumps({
                 "site":site,
                 "original_true_real_2010_tide4_gps_groups":len(four),
                 "original_true_wild_birds_in_source":
                    qa["all_four_conditions_same_real_bird_month_height_source"][
                       "original_birds_in_all_four_tide_and_light_conditions"],
                 "original_true_gps_four_conditions_positions":
                    qa["all_four_conditions_same_real_bird_month_height_source"][
                        "original_four_way_source_fix_count"],
                 "bird_RWS_solar_only_source_frozen_before_Y":True},
                 sort_keys=True),flush=True)

    # Exact old original 2010 source-count signature for BOTH islands
    # first, then and only then evaluate newly defined WMR GPS habitat Y.
    source_replay=hard_before_outcome_both_sites(matched)
    print("V86_ORIGINAL_V82_ALL_GPS_TIDE_SOLAR_EXACT_SOURCE_REPLAY "+
          json.dumps({
              "source":source_replay,
              "new_WMR_GPS_habitat_binary_Y_not_yet_scored":True},
              sort_keys=True),flush=True)

    outcome=score_binary_original_two_sites_if_source_gated(
        matched,original_source,classes)
    main=outcome["binary_mid_high_2010_true_wild_RWS_tidal_solar_by_site"]
    difference=outcome[
        "main_binary_mid_high_GPS_position_two_site_bird_cluster_CONTRAST"]
    report={
        "analysis":"V86_WILD_2010_SCHIER_AMELAND_BINARY_MIDHIGH_TIDE_FLAT_GPS_POSITION_RWS_FLOOD_EBB_BY_SUNLIGHT",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "original_frozen_protocol":"docs/V86_FROZEN_REAL_WILD_GPS_WMR_MIDHIGH_OCCURRENCE_TIDE_LIGHT_FOURWAY.md",
        "original_publisher_NIOZ_source_SHA_MD5_and_static_mesh_qa":native_source,
        "original_WMR_2008_2012_midhigh_class_publisher_full_canonical_source":
            class_receipts,
        "genuine_original_2010_Zenodo_wild_GPS_source":gps_receipts,
        "original_original_2010_both_site_GPS_geography_source":original_source_receipts,
        "original_two_observed_2010_RWS_tide_and_solar_fourway_source":tide_source,
        "source_prior_v82_true_all_gps_fourway_counts_exactly_replayed_before_Y":
            source_replay,
        "genuine_wild_binary_midhigh_intertidal_GPS_use_response_if_both_source_admitted":
            outcome,
        "original_v85_within_midhigh_only_fourway_habitat_rank_source_FAILED_AND_NOT_SCORED":
            True,
        "original_v82_old_numeric_model_index_D_Schier":.0499790599,
        "original_v82_old_numeric_model_index_D_Ameland":.0052737884,
        "original_v82_old_numeric_model_index_site_diff_boot95":
            [-.0132526956,.0965821568],
        "source_WMR_exact_2021_corrected_Mendeley_v2_version_UNVERIFIED":True,
        "original_NIOZ_2010_JunJul_native_lat_was_masked_only_model_template_INFERRED":True,
        "genuine_response_GPS_position_record_fraction_NOT_feeding_duration_or_true_dry_area":True,
        "original_2010_GPS_clock_UTC_vs_GPS_calibration_UNVERIFIED":True,
        "original_only_two_islands_one_species_one_sea_and_many_past_tests_NOT_universal":True,
        "no_real_bird_ID_or_animal_location_timestamp_full_RWS_tide_or_raw_map_polygon_or_source_NIOZ_index_array_exported":True}
    target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("V86_AUTHENTIC_WILD_GPS_BINARY_TIDAL_FLAT_POSITION_TRUE_TIDE_SOLAR_RESULT "+
          json.dumps({
              "source_prior_real_fourway_fully_replayed":True,
              "site_source_real_birds":{
                  s:source_replay[s]["original_identified_real_birds_in_source"]
                  for s in ("Schier","Ameland")},
              "site_results":{
                  s:{
                     "genuine_binary_Y_midhigh_GPS_fraction_fourway_D":
                         main[s]["primary_binary_GPS_position_in_intertidal_probability_D"][
                         "site_original_true_bird_equal_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY"],
                     "source_whole_bird_bootstrap95":
                         main[s]["primary_binary_GPS_position_in_intertidal_probability_D"][
                         "true_bird_10000_bootstrap95"],
                     "birds_with_positive_D":
                         main[s]["primary_binary_GPS_position_in_intertidal_probability_D"][
                         "original_birds_positive_D"],
                     "original_source_result_status":
                         main[s]["primary_binary_GPS_position_in_intertidal_probability_D"][
                         "fixed_exploratory_class_status"]}
                  for s in ("Schier","Ameland")},
              "site_Schier_minus_Ameland_binary_use_probability_D":
                  difference["Schier_bird_equal_minus_Ameland_bird_equal"],
              "original_bird_independent_site_diff_bootstrap95":
                  difference["original_site_independent_whole_bird_10000_bootstrap95"],
              "site_difference_status":
                  difference["point_positive_or_negative_status"],
              "original_modelled_NIOZ_time_expo_index_Y_UNUSED":True},
              sort_keys=True),flush=True)
    print("V86_ORIGINAL_REAL_BIRD_MIDHIGH_TIDAL_FLAT_GPS_BINARY_4WAY_COMPLETE",
          flush=True)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",
                   default=os.environ.get(
                    "BOIDS_ORIGINAL_RWS_CACHE_DIR",
                    "/tmp/boids_original_RWS_v86"))
    q=p.parse_args()
    run(q.output,q.source_cache_dir)
