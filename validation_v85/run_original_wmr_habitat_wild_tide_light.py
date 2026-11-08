"""v85 real original 2010 Wadden two-island oystercatcher GPS source ecology.

Use exact frozen:
- 2009/2010 original NIOZ model geospatial source and explicitly inferred
  STATIC model grid latitude only Jun/Jul (original lat still missing).
- original WMR WS3 complete 345/280 classified 2008-2012 map; exact corrected
  2021 Mendeley v2 VERSION NOT verified. Use mid/high code3/4 ONLY.
- two separate official original RWS measured 2010 10minute tide stations,
  Schier and Ameland; same bird×month×height flood/ebb × day/night.
- ecotope used-position eligibility first, then 4-way true tide source gate
  at BOTH sites; ONLY THEN native model index used rank score.
No bird tags, precise coords/times, model pixels, RWS series exported.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from pathlib import Path

from original_nioz_static_2010_grid import original_manifest
from authenticated_nioz_static_template_model import (
    authenticated_template_and_model_months)
from original_rws_cached_transport import OriginalRwsCache
from two_island_common_month_bird_contrast import (
    SOURCE_MONTHS, SCHIER_SOURCE, AMELAND_SOURCE)
from run_original_two_site_tide_solar_common_months import (
    _fetch_original_two_site_GPS, _original_gauge, GAUGE_CODES)
from midhigh_intertidal_source_and_fourway import (
    classify_native_2010_model_sites,
    source_class_restricted_gps_month,
    inspect_source_and_match_tide,
    shared_source_gates,
    score_if_both_source_admitted,
    SOURCE_COMMON_MONTH_MIN,
    SOURCE_MONTH_SOURCE_BIRDS_MIN,
    SOURCE_MONTH_SOURCE_FIXES_MIN,
    RESULT_STOP)

def _has_common_source(sources):
    common=[]
    for m in SOURCE_MONTHS:
        ok=all(
            sources[s][m]["source_qa"][
                "original_birds_with_ge20_strict_intertidal_GPS_this_month"]
                >=SOURCE_MONTH_SOURCE_BIRDS_MIN
            and sources[s][m]["source_qa"][
                "original_gps_after_bird_month20_and_WMR_neighborhood20"]
                >=SOURCE_MONTH_SOURCE_FIXES_MIN
            for s in ("Schier","Ameland"))
        if ok:common.append(m)
    return common

def run(output,cache_dir):
    # Actual independent SOURCE model and WMR full map provenance first.
    original_models,model_qa=authenticated_template_and_model_months(
        original_manifest())
    if sorted(original_models)!=list(SOURCE_MONTHS):
        raise ValueError("SOURCE_STOP_V85_NIOZ_NATIVE_OR_INFERRED_MODEL_MONTHS_DRIFT")
    native_reference=original_models[8]["xy"] # genuinely observed 2010 Aug lat
    for month in SOURCE_MONTHS:
        if not (native_reference==original_models[month]["xy"]).all():
            raise ValueError("SOURCE_STOP_V85_STATIC_NIOZ_MODEL_MONTH_MESH_MISMATCH")
    print("V85_NIOZ_PUBLISHER_2009_2010_STATIC_SOURCE_ADMITTED "+
          json.dumps({
              "2010_months":list(SOURCE_MONTHS),
              "original_2010_JuneJuly_lat_MISSING_and_explicit_template":True,
              "model_original_time_expo_units":"UNKNOWN",
              "native_source_grid_centers":len(native_reference)},sort_keys=True),
          flush=True)
    class_sources={}
    class_qa={}
    for site in ("Schier","Ameland"):
        source=classify_native_2010_model_sites(native_reference,site)
        class_sources[site]=source
        class_qa[site]=source["source_record"]
        print("V85_ORIGINAL_WMR_FULL_GEOGRAPHIC_MID_HIGH_SITE_SOURCE "+
              json.dumps({"site":site,**source["source_record"]},
                         sort_keys=True),flush=True)

    (gps_s,gps_a),gps_qa=_fetch_original_two_site_GPS()
    habitat={}
    source_month_qa={}
    for site,months in (("Schier",gps_s),("Ameland",gps_a)):
        by_month={}
        by_receipt={}
        for month in SOURCE_MONTHS:
            q=source_class_restricted_gps_month(
                site,month,months[month],original_models[month],
                class_sources[site])
            by_month[month]=q
            by_receipt[str(month)]=q["source_qa"]
            print("V85_SOURCE_ONLY_ACTUAL_BIRD_WMR_MIDHIGH_NATIVE_GPS_MONTH "+
                  json.dumps({"site":site,"month":month,**q["source_qa"]},
                       sort_keys=True),flush=True)
        habitat[site]=by_month
        source_month_qa[site]=by_receipt
    prelim_common=_has_common_source(habitat)
    print("V85_BOTH_SITE_ONLY_NATIVE_GPS_CLASS3_4_SHARED_MONTHS_SOURCE_GATE "+
          json.dumps({
              "source_supported_original_shared_calendar_months":prelim_common,
              "strict_three_common_month_source_requirement":
                   SOURCE_COMMON_MONTH_MIN,
              "no_NIOZ_GPS_used_cell_index_was_scored":True
          },sort_keys=True),flush=True)

    matched={}
    source_phase={}
    rws_qa={}
    rws_source_status="NOT_FETCHED_IF_SPATIAL_SOURCE_MONTHS_LT3"
    whole_result={
        "score":RESULT_STOP,
        "no_bird_model_index_values_read":True}
    if len(prelim_common)>=SOURCE_COMMON_MONTH_MIN:
        # Measured station water levels/true ebb/flood and original GPS
        # astronomical classification; still NO model index used effects.
        for site in ("Schier","Ameland"):
            cache=OriginalRwsCache(
                str(Path(cache_dir)/site.lower()),sleeper=time.sleep)
            tide,receipt=_original_gauge(GAUGE_CODES[site],cache)
            rws_qa[site]=receipt
            rws_qa[site]["authenticated_original_quarter_transport"]=cache.snapshot()
            four,meta=inspect_source_and_match_tide(habitat[site],tide)
            matched[site]=(four,meta)
            source_phase[site]=meta
            s=meta["original_tide_astro_same_bird_month_height_strata"]
            print("V85_ORIGINAL_RWS_TIDAL_SOLAR_WMR_CLASS3_4_FOURCELL_SOURCE "+
                  json.dumps({"site":site,
                     "real_four_conditions_groups":s[
                        "original_four_way_exact_same_bird_month_RWS_height_groups"],
                     "distinct_original_wild_birds":s[
                        "original_birds_in_all_four_tide_and_light_conditions"],
                     "source_gps_fixes_in_true_4cell_conditions":s[
                        "original_four_way_source_fix_count"],
                     "source_months":s[
                        "original_2010_months_with_complete_four_way_conditions"],
                     "source_status":s["admission"]},sort_keys=True),flush=True)
        gate=shared_source_gates(habitat,matched)
        rws_source_status="ORIGINAL_BOTH_RWS_STATIONS_MEASURED_2010_REAUTHENTICATED"
        print("V85_FIXED_TWO_ISLAND_REAL_WMR_HABITAT_SOURCE_ADMISSION "+
              json.dumps(gate,sort_keys=True),flush=True)
        if gate["all_fixed_original_source_gates_admitted_BEFORE_model_use_rank"]:
            print("V85_ALL_BIRD_HABITAT_AND_RWS_TIDE_SOURCE_GATES_PASS_NOW_SCORE_REAL_INDEX",
                  flush=True)
        whole_result=score_if_both_source_admitted(
            habitat,matched,gate,original_models)
    else:
        gate={
            "source_gate_status":
                "NOT_ADMITTED_V85_COMMON_MONTH_CLASS3_4_GPS_ONLY",
            "source_supported_shared_months_from_original_littoral_GPS_only":
                prelim_common,
            "all_fixed_original_source_gates_admitted_BEFORE_model_use_rank":
                False}

    output_data={
        "analysis":"V85_ORIGINAL_WILD_2010_SCHIER_AMELAND_CONDITIONAL_WMR_CODE3_4_INTERTIDAL_NIOZ_RANK_TIDAL_SOLAR",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "source_frozen_protocol":"docs/V85_FROZEN_GPS_CONDITIONAL_MIDHIGH_WMR_VS_ALLCELL_NIOZ_RANK.md",
        "original_NIOZ_2009_2010_publisher_model_grid_sha_rechecked":model_qa,
        "original_WMR_true_full_polygon_publisher_source_sha_and_native_model_class_counts":
            class_qa,
        "original_true_Zenodo_site_native_GPS_provider_hash_and_source_counts":gps_qa,
        "original_animal_site_month_ecotope_native_GEOGRAPHIC_source_only":
            source_month_qa,
        "original_site_common_source_supported_three_months":prelim_common,
        "independently_measured_original_RWS_two_station_2010_source":
            rws_qa,
        "original_RWS_source_status":rws_source_status,
        "original_tide_light_fourway_source_before_exposure_outcomes":
            source_phase,
        "gates_habitat_restricted_2010_both_coasts":gate,
        "observed_wild_gps_habitat_conditional_fourway_if_admitted":
            whole_result,
        "original_Schier_v82_allgps_allpixel_JunDec_D":.0499790599,
        "original_Ameland_v82_allgps_allpixel_JunDec_D":.0052737884,
        "old_v82_site_difference95_not_established":[-.0132526956,.0965821568],
        "WMR_corrected_2021_v2_original_source_identity_UNVERIFIED":True,
        "source_original_NIOZ_JuneJuly_lat_only_MODEL_TEMPLATE_INFERRED":True,
        "original_NIOZ_monthly_time_expo_units_UNKNOWN":True,
        "mid_high_mapped_habitat_not_direct_observed_food_or_instantaneous_patch_dry_time":True,
        "preexisting_v69_v70_future_heading_added_sunlight_gain_not_established_UNALTERED":True,
        "no_original_bird_ID_exact_locations_GPS_times_RWS_rows_model_pixels_GIS_shapes_exported":True}
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output_data,sort_keys=True,indent=2)+"\n")
    site_contrast=whole_result.get(
        "original_bird_site_CONTRAST_restricted_Schier_minus_Ameland")
    print("V85_REAL_WILD_WMR_INTERTIDAL_CONDITIONAL_TIDE_SOLAR_RESULT "+
          json.dumps({
            "frozen_source_gate":gate["source_gate_status"],
            "true_shared_months_source_only":prelim_common,
            "number_original_mid_high_gps_source_by_site":{
                s:int(sum(q["original_gps_after_bird_month20_and_WMR_neighborhood20"]
                          for q in source_month_qa[s].values()))
                for s in ("Schier","Ameland")},
            "new_habitat_filtered_S_minus_A_rank_D":
                site_contrast["Schier_bird_equal_minus_Ameland_bird_equal"]
                if site_contrast else None,
            "new_site_independent_bird_CI":
                site_contrast["original_site_independent_whole_bird_10000_bootstrap95"]
                if site_contrast else None,
            "animal_effect_computed_if_all_sources_admitted":
                bool(site_contrast),
            "no_claim_corrected_v2_or_observed_food":True},sort_keys=True),
          flush=True)
    print("V85_ORIGINAL_WMR_NATIVE_TIDE_FLAT_CLASS_SOURCE_BIRD_ECOLOGY_FINISHED",
          flush=True)
    return output_data

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_RWS_v85"))
    a=p.parse_args();run(a.output,a.source_cache_dir)
