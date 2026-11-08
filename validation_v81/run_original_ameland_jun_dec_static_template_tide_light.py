"""v81 original Ameland 2010 real RWS tide×light model-habitat 4-way transport.

June/July original NIOZ latitude is entirely MISSING; only use explicitly
inferred Jan2010 static numerical model grid after original publisher SHA and
2009 independent model-month exact-mesh proof. Native Aug-Dec unchanged.
Original wild GPS and source tide/solar groups checked BEFORE model-use ranks.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from datetime import timedelta
from pathlib import Path

from ameland_external_site import original_gps
from original_nioz_static_2010_grid import original_manifest
from authenticated_nioz_static_template_model import (
    MONTHS_V81,ORIGINAL_INFERRED_MONTHS,
    authenticated_template_and_model_months)
from original_ameland_native_gps_source import (
    AMELAND_RAW_2010,AMELAND_SHA_2010,AMELAND_STATUS,
    original_ameland_2010_hourly,original_ameland_month_native_source_gate)
from matched_tide_state_day_night_native_ranks import tide_light_source_groups
from tide_solar_four_way_source_and_effect import (
    fourway_source_only,score_fourway_difference_in_differences,ADMIT)
from original_rws_cached_transport import (
    OriginalRwsCache,observed_original_rws_year_cached)

GAUGE="ameland.nes"
ORIGINAL_RWS_2010_COUNT=52561
ORIGINAL_PREVIOUS_V78_NATIVE_ONLY_FOURWAY_SOURCE_STRATA=267
ORIGINAL_PREVIOUS_V78_NATIVE_ONLY_FOURWAY_SOURCE_BIRDS=7
SOURCE_MONTH_COUNTS_V79={
    6:(6450,15),7:(5321,8),8:(5106,7),9:(4581,7),
    10:(3629,7),11:(3220,6),12:(3076,6)}
ORIGINAL_SCHIER_V77_D=.03803110272968872
ORIGINAL_SCHIER_V77_BIRD95=[.019161565501295177,.059818006892836444]

def _source_no_eco(source):
    return {
        "source_status":source["admission"],
        "true_original_four_condition_groups":
            source["original_four_way_exact_same_bird_month_RWS_height_groups"],
        "actual_original_birds":
            source["original_birds_in_all_four_tide_and_light_conditions"],
        "original_GPS_source_positions":
            source["original_four_way_source_fix_count"],
        "source_year_months":
            source["original_2010_months_with_complete_four_way_conditions"]}

def run(output,cache_dir):
    provider=original_manifest()
    source_models,model_provenance=authenticated_template_and_model_months(
        provider)
    print("V81_NIOZ_EXPLICIT_STATIC_COMPUTATIONAL_MESH_PROVENANCE "+
          json.dumps({
            "2009_real_source_mesh_controls_exact":model_provenance[
                "original_2010_Jan_and_2009_Jan_Aug_exact_grid_provenance_verified"],
            "original_JuneJuly_lat_genuinely_missing":True,
            "month_geographic_modes":{
                str(m):a["model_spatial_reference_mode"] for m,a in
                model_provenance["original_month_specific_spatial_source"].items()},
            "native_original_model_index_units":"UNKNOWN"
          },sort_keys=True),flush=True)
    with tempfile.TemporaryDirectory(prefix="v81_orig_Ameland_2010_") as td:
        gpsfile=Path(td)/"original_Ameland_2010.csv.gz"
        gps_source=original_gps(2010,gpsfile)
        if gps_source["original_sha256"]!=AMELAND_SHA_2010 or not gps_source[
            "provider_original_md5_matched"]:
            raise ValueError("SOURCE_STOP_V81_AUTHENTIC_ORIGINAL_AMELAND_GPS_DRIFT")
        monthly,gpsqa=original_ameland_2010_hourly(
            gpsfile,allowed_months=MONTHS_V81)
    georefs={}
    for m in MONTHS_V81:
        s=gpsqa["source_fixed_2010_Aug_to_Dec_hourly_bird_fixes"][str(m)]
        if (s["original_Ameland_native_hourly_locations"],
            s["original_distinct_birds"])!=SOURCE_MONTH_COUNTS_V79[m]:
            raise ValueError("SOURCE_STOP_V81_FROZEN_V79_2010_SOURCE_MONTH_BIRDS_DRIFT")
        pre=original_ameland_month_native_source_gate(
            m,monthly[m],source_models[m],allowed_months=MONTHS_V81)
        georefs[m]=pre
        original=pre["source_receipt"]
        print("V81_REAL_AMELAND_MONTH_GPS_ORIGINAL_VS_MODEL_TEMPLATE_SOURCE "+
              json.dumps({
                "month":m,
                "original_gps_hourly_fixes":original["source_original_native_hourly_fixes"],
                "actual_bird_ID_count":original["source_original_distinct_birds"],
                "gps_native_model_near_300m_count":
                    original["original_GPS_nearest_NIOZ_grid_within_300m"],
                "gps_birds_at_least20":
                    original["original_birds_with_20plus_source_locations_and_1km_background"],
                "native_model_spatial_mode":model_provenance[
                    "original_month_specific_spatial_source"][m][
                    "model_spatial_reference_mode"],
                "original_native_lat_was_masked":m in ORIGINAL_INFERRED_MONTHS,
                "source_gate":original["fixed_source_admission"]
              },sort_keys=True),flush=True)
    model_month_receipts={str(m):georefs[m]["source_receipt"]
                          for m in MONTHS_V81}
    all_source=all(x["fixed_source_admission"]==AMELAND_STATUS
                   for x in model_month_receipts.values())
    tide_proof=None
    prior_native_source=None
    source_meta=None
    main=None
    controls={}
    if all_source:
        cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
        try:
            tide,gauge=observed_original_rws_year_cached(cache,GAUGE,2010)
            if (gauge["gauge_rows"]!=ORIGINAL_RWS_2010_COUNT or
                tide.provenance!="observed" or
                len(tide.times)!=ORIGINAL_RWS_2010_COUNT or
                tide.times[1]-tide.times[0]!=timedelta(minutes=10)):
                raise ValueError("SOURCE_STOP_V81_AUTHENTIC_RWS_AMELAND_NAP_2010")
            tide_proof={
                "station":GAUGE,
                "2010_original_measured_10min_NAP_samples":ORIGINAL_RWS_2010_COUNT,
                "original_year_RWS_transport":cache.snapshot(),
                "no_synthetic_gauge_source":True}
            native_months=(8,9,10,11,12)
            old_pairs,old_source=tide_light_source_groups(
                {m:georefs[m] for m in native_months},tide,
                required_geo_status=AMELAND_STATUS,
                required_months=native_months)
            old4,old_gate=fourway_source_only(
                old_pairs,old_source,verify_original_replay=False)
            if (len(old4)!=ORIGINAL_PREVIOUS_V78_NATIVE_ONLY_FOURWAY_SOURCE_STRATA or
                old_gate["original_birds_in_all_four_tide_and_light_conditions"]!=
                ORIGINAL_PREVIOUS_V78_NATIVE_ONLY_FOURWAY_SOURCE_BIRDS or
                old_gate["admission"]==ADMIT):
                raise ValueError("SOURCE_STOP_V81_FROZEN_V78_NATIVE_MONTH_SOURCE_GATE_DRIFT")
            prior_native_source={
                "original_native_2010_AugDec_fourway_groups_NO_EFFECT_SCORE":
                    len(old4),
                "actual_original_AugDec_Ameland_birds":
                    old_gate["original_birds_in_all_four_tide_and_light_conditions"],
                "old_v78_source_admission":old_gate["admission"],
                "no_previous_failed_source_biological_score_opened":True}
            print("V81_PRIOR_V78_ORIGINAL_NATIVELY_GEOREFERENCED_GPS_GATE_UNCHANGED "+
                  json.dumps(prior_native_source,sort_keys=True),flush=True)
            paired,source=tide_light_source_groups(
                georefs,tide,height_bin=.2,shift_seconds=0,
                required_geo_status=AMELAND_STATUS,
                required_months=MONTHS_V81)
            four,foursource=fourway_source_only(
                paired,source,verify_original_replay=False)
            inferred_source_groups=sum(g[1] in ORIGINAL_INFERRED_MONTHS
                                       for g in four)
            native_source_groups=len(four)-inferred_source_groups
            inferred_source_fixes=sum(
                len(v[phase][label])
                for key,v in four.items()
                if key[1] in ORIGINAL_INFERRED_MONTHS
                for phase in (-1,1) for label in ("DAY","NIGHT"))
            source_meta={
                "original_tide_phase_daynight_source_qa":source,
                "original_full_four_cell_source_qa":foursource,
                "original_4way_groups_with_INFERRED_JuneJuly_monthly_lat":
                    inferred_source_groups,
                "original_4way_groups_with_original_native_AugDec_lat":
                    native_source_groups,
                "original_GPS_fixes_inferred_template_month_fourcell_source":
                    inferred_source_fixes,
                "explicit_imputation_not_original_native_geographic_observation":True}
            print("V81_ORIGINAL_AMELAND_JUN_DEC_SAME_BIRD_MONTH_TIDE_FOURWAY_SOURCE "+
                  json.dumps({
                    **_source_no_eco(foursource),
                    "native_original_4way_groups":native_source_groups,
                    "inferred_static_model_mesh_4way_groups":inferred_source_groups,
                    "inferred_model_mesh_GPS_source_fixes":inferred_source_fixes,
                    "original_2010_JuneJuly_lat_NOT_observed":True
                  },sort_keys=True),flush=True)
            main=score_fourway_difference_in_differences(
                four,foursource,georefs)
            if foursource["admission"]==ADMIT:
                for label,binwidth,seconds in (
                   ("RWS_height_band_0p10m",.1,0),
                   ("RWS_height_band_0p40m",.4,0),
                   ("original_GPS_native_clock_minus15seconds",.2,-15)):
                    paired_s,source_s=tide_light_source_groups(
                        georefs,tide,height_bin=binwidth,
                        shift_seconds=seconds,
                        required_geo_status=AMELAND_STATUS,
                        required_months=MONTHS_V81)
                    four_s,qa_s=fourway_source_only(
                        paired_s,source_s,verify_original_replay=False)
                    controls[label]=score_fourway_difference_in_differences(
                        four_s,qa_s,georefs,seed=20261108+
                        (1 if binwidth==.1 else 2 if binwidth==.4 else 3))
        finally:
            print("V81_REAL_AMELAND_RWS_ORIGINAL_TRANSPORT_RECEIPT "+
                  json.dumps(cache.snapshot(),sort_keys=True),flush=True)
    else:
        main={
            "source_admission":"NOT_ADMITTED_V81_ALL_SEVEN_MONTH_NATIVE_MODEL_AND_GPS_SOURCE",
            "flood_minus_ebb_of_NIGHT_minus_DAY":"NOT_ESTIMATED_SOURCE_GATE"}
    result={
       "analysis":"V81_ORIGINAL_AMELAND_EXTERNAL_SITE_JUN_DEC_TIDE_BY_SOLAR_FOUR_WAY_EXPLICIT_NIOZ_STATIC_GRID_TEMPLATE",
       "executed_commit":os.environ.get("GITHUB_SHA","local"),
       "frozen_protocol":"docs/V81_FROZEN_EXPLICIT_STATIC_TEMPLATE_AMELAND_2010_JUN_DEC_TIDE_LIGHT.md",
       "original_NIOZ_publisher_MD5_SHA_and_JunJul_template_source":model_provenance,
       "original_Zenodo_2010_Ameland_GPS_MD5_SHA_verified":True,
       "original_Zenodo_2010_Ameland_GPS_SHA256":gps_source["original_sha256"],
       "original_Ameland_2010_JunDec_GPS_native_hour_source":gpsqa,
       "original_Ameland_true_monthly_GPS_to_model_geometry_source":model_month_receipts,
       "all_seven_original_2010_months_spatial_source_admitted":all_source,
       "independent_original_2010_Ameland_Nes_measured_gauge_source":tide_proof,
       "v78_old_AugDec_native_original_late_months_7bird_failed_gate_replayed":prior_native_source,
       "new_JunDec_RWS_tide_solar_FOUR_condition_source":source_meta,
       "new_Ameland_original_wild_GPS_model_4way_interaction_IF_admitted":main,
       "frozen_height_bin_and_original_GPS_clock_controls":controls,
       "original_Schier_v77_comparison_for_context_NOT_POOLS":{
           "original_Schier_flood_minus_ebb_of_NIGHT_minus_DAY":ORIGINAL_SCHIER_V77_D,
           "source_Schier_16wholebird_bootstrap95":ORIGINAL_SCHIER_V77_BIRD95},
       "JuneJuly_NATIVE_LAT_WAS_MISSING_AND_STILL_IS":True,
       "source_model_time_expo_monthly_units_NOT_originally_verified":True,
       "different_site_same_species_same_Wadden_sea_region":True,
       "post_v78_v79_exploratory_not_independent_species_confirmation":True,
       "no_individual_GPS_bird_ID_exact_time_location_RWS_series_or_model_rasters_exported":True}
    out=Path(output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    observed=main.get("original_2010_Schier_RWS_tide_phase_by_astro_light_interaction") if main else None
    primary=observed.get(
       "frozen_primary_genuine_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY") if observed else None
    f=source_meta["original_full_four_cell_source_qa"] if source_meta else None
    print("V81_ORIGINAL_AMELAND_INFERRED_TEMPLATE_TIDE_LIGHT_OUT_OF_SITE_RESULT "+
          json.dumps({
            "original_NIOZ_static_mesh_src_verified":True,
            "all_seven_month_model_and_bird_source_passed":all_source,
            "original_fourway_Ameland_source_status":
                f["admission"] if f else "NO_SEVEN_MONTH_SOURCE",
            "source_4cell_same_bird_month_height_groups":
                f["original_four_way_exact_same_bird_month_RWS_height_groups"] if f else None,
            "genuine_original_birds_in_four_conditions":
                f["original_birds_in_all_four_tide_and_light_conditions"] if f else None,
            "original_model_index_D_flood_vs_ebb_NIGHT_minus_DAY":
                primary["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"] if primary else None,
            "whole_Ameland_original_bird_bootstrap95":
                primary["whole_original_bird_10000_bootstrap95"] if primary else None,
            "birds_positive":
                primary["original_birds_with_night_higher"] if primary else None,
            "ecological_source_temporal_geography_LIMIT":
                "JuneJuly_NIOZ_lat_INFERRED_STATIC_MODEL_GRID_NOT_ORIGINAL_OBSERVED",
            "result_status":
                observed["frozen_exploratory_primary_status"] if observed
                else "NOT_ESTIMATED_SOURCE_GATE",
            "prior_Schier_v77_source_D":ORIGINAL_SCHIER_V77_D
          },sort_keys=True),flush=True)
    print("V81_ORIGINAL_AMELAND_JUN_DEC_SOURCE_AND_INTERACTION_COMPLETED",flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_RWS_v81"))
    args=p.parse_args()
    run(args.output,args.source_cache_dir)
