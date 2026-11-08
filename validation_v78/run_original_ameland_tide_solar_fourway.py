"""v78 original Ameland independent island 2010 source -> four-way endpoint.

All original Ameland GPS/month/model source gates precede any observed
NIOZ used-location score. Separate area / GPS bird population from Schier,
same Wadden NIOZ model provider and species, not independent ocean basin.
"""
from __future__ import annotations
import argparse
import json
import os
import tempfile
import time
from pathlib import Path
from datetime import timedelta

from ameland_external_site import original_gps,STATION
from original_coeval_wadden_model_metadata import (
    authenticated_provider_file)
from native_monthly_exposure_source import FIXED_SHA,native_readme_meaning
from real_2010_monthly_nioz_gps_source_gate import original_all_2010_manifest
from wild_2010_modelled_tidal_exposure_rank import (
    MONTHS,PINNED_MODEL_SHA,original_2010_native_month)
from original_ameland_native_gps_source import (
    AMELAND_RAW_2010,AMELAND_SHA_2010,AMELAND_STATUS,
    original_ameland_2010_hourly,original_ameland_month_native_source_gate)
from matched_tide_state_day_night_native_ranks import tide_light_source_groups
from tide_solar_four_way_source_and_effect import (
    fourway_source_only,score_fourway_difference_in_differences,ADMIT)
from original_rws_cached_transport import (
    OriginalRwsCache,observed_original_rws_year_cached)

EXPECTED_OFFICIAL_RWS=52561
FIXED_ORIGINAL_YEAR=2010
FIXED_ORIGINAL_STATION="ameland.nes"
SHIER_ORIGINAL_V77_MAIN=.03803110272968872
SHIER_ORIGINAL_V77_BIRD95=[.019161565501295177,.059818006892836444]

def run(output,cache_dir):
    provider=original_all_2010_manifest()
    readme,receipt=authenticated_provider_file(provider["README.txt"])
    if receipt["original_computed_sha256"]!=FIXED_SHA["README.txt"]:
        raise ValueError("SOURCE_STOP_V78_ORIGINAL_NIOZ_README_MD5_SHA")
    meaning=native_readme_meaning(readme)
    if not (meaning["native_exposure_variable_literal_mentioned"]
            and meaning["native_exposure_word_documented"]):
        raise ValueError("SOURCE_STOP_V78_ORIGINAL_TIDAL_INDEX_SOURCE_SEMANTICS")
    with tempfile.TemporaryDirectory(prefix="v78_original_Ameland_") as tmp:
        gp=Path(tmp)/"Ameland_2010_original.csv.gz"
        original=original_gps(2010,gp)
        if (original.get("provider_original_md5_matched") is not True or
            original["original_sha256"]!=AMELAND_SHA_2010):
            raise ValueError("SOURCE_STOP_V78_ORIGINAL_AMELAND_PROVIDER_IDENTITY_DRIFT")
        months,original_qa=original_ameland_2010_hourly(gp)
    original_geo={}
    shas={}
    for month in MONTHS:
        filename=f"eco_av.2010{month:02d}.nc"
        raw,receipt=authenticated_provider_file(provider[filename])
        if receipt["original_computed_sha256"]!=PINNED_MODEL_SHA[month]:
            raise ValueError("SOURCE_STOP_V78_ORIGINAL_NIOZ_2010_MODEL_SHA_DRIFT")
        shas[filename]=receipt["original_computed_sha256"]
        model=original_2010_native_month(raw,month)
        qa=original_ameland_month_native_source_gate(
            month,months[month],model)
        original_geo[month]=qa
        s=qa["source_receipt"]
        print("V78_ORIGINAL_AMELAND_2010_NATIVE_GPS_MODEL_SOURCE_BEFORE_OUTCOME "+
              json.dumps({"original_month":month,
                "real_native_hourly_fixes":s["source_original_native_hourly_fixes"],
                "real_original_birds":s["source_original_distinct_birds"],
                "source_model_valid_cells":s["genuine_original_NIOZ_native_model_cells"],
                "original_GPS_within_native_grid_300m":
                    s["original_GPS_nearest_NIOZ_grid_within_300m"],
                "bird_IDs_with_20plus_model_background":
                    s["original_birds_with_20plus_source_locations_and_1km_background"],
                "fixed_source_admission":s["fixed_source_admission"]},
                sort_keys=True),flush=True)
    months_qa={str(m):original_geo[m]["source_receipt"] for m in MONTHS}
    pass_months=all(x["fixed_source_admission"]==AMELAND_STATUS
                    for x in months_qa.values())
    gauge_data=None
    matched_source=None
    primary=None
    controls={}
    old_comparison={
        "original_Schier_2010_flood_minus_ebb_of_night_minus_day":
            SHIER_ORIGINAL_V77_MAIN,
        "original_Schier_2010_16bird_whole_bird_bootstrap95":
            SHIER_ORIGINAL_V77_BIRD95,
        "independent_original_Ameland_site_was_unscored_for_this_endpoint":True}
    if pass_months:
        cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
        try:
            tide,report=observed_original_rws_year_cached(
                cache,FIXED_ORIGINAL_STATION,FIXED_ORIGINAL_YEAR)
            if (report["gauge_rows"]!=EXPECTED_OFFICIAL_RWS or
                tide.provenance!="observed" or
                len(tide.times)!=EXPECTED_OFFICIAL_RWS or
                tide.times[1]-tide.times[0]!=timedelta(minutes=10)):
                raise ValueError("SOURCE_STOP_V78_AMELAND_NES_ORIGINAL_MEASURED_RWS")
            gauge_data={"station":FIXED_ORIGINAL_STATION,
                "original_verified_2010_tenminute_RWS_WATHTE_NAP_records":
                    EXPECTED_OFFICIAL_RWS,
                "source_transport":cache.snapshot()}
            matched,source=tide_light_source_groups(
                original_geo,tide,height_bin=.2,shift_seconds=0,
                required_geo_status=AMELAND_STATUS)
            four,matchqa=fourway_source_only(
                matched,source,verify_original_replay=False)
            matched_source={
                "source_M0_prior_same_phase_daynight":source,
                "complete_original_four_cell_matched_tide_solar_gate":matchqa}
            print("V78_ORIGINAL_EXTERNAL_AMELAND_2010_RWS_TIDE_FOURWAY_SOURCE "+
                  json.dumps(matchqa,sort_keys=True),flush=True)
            primary=score_fourway_difference_in_differences(
                four,matchqa,original_geo)
            if matchqa["admission"]==ADMIT:
                for label,band,seconds in (
                    ("original_Ameland_RWS_height_band_0p1m",.1,0),
                    ("original_Ameland_RWS_height_band_0p4m",.4,0),
                    ("Ameland_original_GPS_clock_minus15s",.2,-15)):
                    low_groups,low_source=tide_light_source_groups(
                        original_geo,tide,height_bin=band,
                        shift_seconds=seconds,required_geo_status=AMELAND_STATUS)
                    low_four,low_gate=fourway_source_only(
                        low_groups,low_source,verify_original_replay=False)
                    controls[label]=score_fourway_difference_in_differences(
                        low_four,low_gate,original_geo,
                        seed=20261108+
                             (1 if band==.1 else 2 if band==.4 else 3))
        finally:
            print("V78_ORIGINAL_AMELAND_RWS_TRANSPORT_RECEIPT "+
                  json.dumps(cache.snapshot(),sort_keys=True),flush=True)
    else:
        print("V78_ORIGINAL_AMELAND_ALL_FIVE_MONTH_SOURCE_NOT_ADMITTED_NO_EFFECT "+
              json.dumps({m:x["fixed_source_admission"]
                  for m,x in months_qa.items()},sort_keys=True),flush=True)
        primary={"source_admission":"NOT_ADMITTED_V78_ORIGINAL_AMELAND_GPS_MONTH_SOURCE",
                 "flood_minus_ebb_of_NIGHT_minus_DAY":"NOT_ESTIMATED_SOURCE_GATE"}
    answer={
        "analysis":"V78_ORIGINAL_2010_AMELAND_OUT_OF_SCHIER_SITE_FOURWAY_RWS_TIDE_BY_SOLAR_MONTHLY_HABITAT_MODEL_INDEX",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "frozen_protocol":"docs/V78_FROZEN_EXTERNAL_AMELAND_TIDE_SOLAR_FOUR_WAY.md",
        "original_Ameland_gps_2010_publisher_md5_and_sha_verified":True,
        "original_Ameland_gps_2010_sha256":original["original_sha256"],
        "original_original_Ameland_gps_2010_annual_fix_count":
            AMELAND_RAW_2010,
        "original_Ameland_native_monthly_GPS_source":original_qa,
        "original_original_NIOZ_month_SHA_provider_md5_verified":shas,
        "original_NIOZ_README_model_time_expo_units_unknown":meaning,
        "original_Ameland_all_five_month_model_geo_source_only":months_qa,
        "source_Ameland_five_original_model_months_all_admitted":pass_months,
        "original_Ameland_Nes_independent_measured_RWS_2010":gauge_data,
        "external_original_Ameland_tidal_solar_four_condition_source":matched_source,
        "source_frozen_true_four_way_out_of_site_animal_use_rank":primary,
        "original_frozen_Schier_reference_not_fitted_on_Ameland":old_comparison,
        "all_precommitted_Ameland_height_clock_sensitivities":controls,
        "NIOZ_index_units_unknown_not_actual_2010_dry_hours":True,
        "previously_investigated_Ameland_GPS_other_tide_endpoints_not_new_field_animals":True,
        "two_sites_same_species_same_Wadden_region_not_cross_taxon_macro_generalization":True,
        "no_individual_bird_ID_original_time_geo_or_model_pixels_emitted":True}
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(answer,indent=2,sort_keys=True)+"\n")
    field=primary.get("original_2010_Schier_RWS_tide_phase_by_astro_light_interaction")
    q=field.get("frozen_primary_genuine_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY") if field else None
    source4=matched_source.get("complete_original_four_cell_matched_tide_solar_gate") if matched_source else None
    print("V78_ORIGINAL_AMELAND_EXTERNAL_TIDE_BY_SOLAR_SITE_RESULT "+
          json.dumps({
            "source_five_original_months_passed":pass_months,
            "original_fourway_source_status":source4["admission"] if source4 else "NO_FIVE_MONTH_SOURCE",
            "original_fourway_Ameland_groups":source4["original_four_way_exact_same_bird_month_RWS_height_groups"] if source4 else None,
            "original_distinct_Ameland_birds":q["original_independent_birds"] if q else None,
            "original_external_site_flood_vs_ebb_NIGHT_DAY":
                q["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"] if q else None,
            "Ameland_external_bird_bootstrap95":q["whole_original_bird_10000_bootstrap95"] if q else None,
            "original_Ameland_birds_positive":q["original_birds_with_night_higher"] if q else None,
            "external_site_frozen_status":
                field["frozen_exploratory_primary_status"] if field else
                "NOT_ESTIMATED_SOURCE_GATE",
            "previous_Schier_original_interaction":SHIER_ORIGINAL_V77_MAIN},
            sort_keys=True),flush=True)
    print("V78_EXTERNAL_ORIGINAL_AMELAND_SITE_SOURCE_AND_FIELD_COMPLETED",flush=True)
    return answer

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",
                   default=os.environ.get("BOIDS_ORIGINAL_RWS_CACHE_DIR",
                        "/tmp/boids_original_RWS_v78_Ameland"))
    a=p.parse_args()
    run(a.output,a.source_cache_dir)
