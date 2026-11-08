"""v77 authentic original 2010 wild GPS four-condition interaction: true measured RWS flood/ebb × astronomical day/night.

All five NIOZ original 2010 monthly model source MD5/SHA validated.
True measured 2010 Schier waterlevel/phase and real GPS sunrise/altitude are
matched *before* any observed use-rank delta is computed.
"""
from __future__ import annotations
import argparse,json,os,tempfile,time
from pathlib import Path

from source_preflight import download_and_pin
from original_coeval_wadden_model_metadata import authenticated_provider_file
from real_2010_monthly_nioz_gps_source_gate import original_all_2010_manifest
from native_monthly_exposure_source import FIXED_SHA,native_readme_meaning
from wild_2010_modelled_tidal_exposure_rank import (
    MONTHS,GPS_SHA,PINNED_MODEL_SHA,
    original_all_wild_months,original_2010_native_month,geometric_preflight)
from matched_tide_state_day_night_native_ranks import (
    tide_light_source_groups,score_matched_tide_day_night)
from tide_solar_four_way_source_and_effect import (
    fourway_source_only,score_fourway_difference_in_differences)
from original_rws_cached_transport import (
    OriginalRwsCache,observed_original_rws_year_cached)

GAUGE="schiermonnikoog.waddenzee"
YEAR=2010
EXACT_2010_GAUGE=52561

def run(output,cache_dir):
    records=original_all_2010_manifest()
    readme,proof=authenticated_provider_file(records["README.txt"])
    if proof["original_computed_sha256"]!=FIXED_SHA["README.txt"]:
        raise ValueError("SOURCE_STOP_V76_ORIGINAL_NIOZ_MODEL_README_CHANGED")
    meaning=native_readme_meaning(readme)
    if not (meaning["native_exposure_variable_literal_mentioned"] and
            meaning["native_exposure_word_documented"]):
        raise ValueError("SOURCE_STOP_V76_MONTHLY_TIDAL_EXPOSURE_SOURCE_README")
    with tempfile.TemporaryDirectory(prefix="v76_original_2010_wild_") as tmp:
        gp=Path(tmp)/"original_schier_2010.csv.gz"
        manifest=download_and_pin(2010,gp)
        if (manifest.get("provider_md5_match") is not True or
            manifest.get("original_sha256")!=GPS_SHA):
            raise ValueError("SOURCE_STOP_V76_ORIGINAL_ZENODO_2010_GPS_MD5_SHA")
        months,source_qa=original_all_wild_months(gp)
    original_geo={}
    hashproof={}
    for month in MONTHS:
        filename=f"eco_av.2010{month:02d}.nc"
        raw,receipt=authenticated_provider_file(records[filename])
        if receipt["original_computed_sha256"]!=PINNED_MODEL_SHA[month]:
            raise ValueError("SOURCE_STOP_V76_PREVIOUSLY_PINNED_NIOZ_MONTH_SHA")
        hashproof[filename]=receipt["original_computed_sha256"]
        model=original_2010_native_month(raw,month)
        original_geo[month]=geometric_preflight(month,months[month],model)
        s=original_geo[month]["source_receipt"]
        if s["fixed_source_admission"]!=(
           "SOURCE_ADMITTED_V75_ORIGINAL_GPS_2010_MONTH_NATIVE_MODEL_1KM"):
            raise ValueError("SOURCE_STOP_V76_ORIGINAL_V75_SPATIAL_MODEL_SOURCE_CHANGED")
    print("V76_ORIGINAL_GPS_NATIVE_MODEL_REPLAY_ALL_FIVE_SOURCE_OK "+
          json.dumps({str(m):{
              "original_source_fix_count":
                  original_geo[m]["source_receipt"]["original_gps_source_hourly_positions"],
              "source_bird_IDs":
                  original_geo[m]["source_receipt"]["original_gps_source_birds"]}
              for m in MONTHS},sort_keys=True),flush=True)
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    try:
        tide,receipt=observed_original_rws_year_cached(
            cache,GAUGE,YEAR)
        if receipt["gauge_rows"]!=EXACT_2010_GAUGE:
            raise ValueError("SOURCE_STOP_V76_ORIGINAL_MEASURED_RWS_YEAR_SAMPLE_COUNT")
        if (tide.provenance!="observed" or len(tide.times)!=EXACT_2010_GAUGE
            or tide.times[1]-tide.times[0] != __import__("datetime").timedelta(minutes=10)):
            raise ValueError("SOURCE_STOP_V76_WRONG_ORIGINAL_RWS_TIDAL_SERIES")
        print("V76_RIJKSWATERSTAAT_MEASURED_2010_GAUGE_AUTHENTICATED "+
              json.dumps({"station":GAUGE,"year":YEAR,
                  "source_measured_gauge_10min_count":receipt["gauge_rows"]},
                  sort_keys=True),flush=True)
        # v76 SOURCE ONLY: genuine RWS phase+height and real sun altitude,
        # identity/month matched, no model used-value read here.
        paired,source=tide_light_source_groups(original_geo,tide,
            height_bin=.2,shift_seconds=0)
        print("V77_OLD_V76_REAL_RWS_PHASE_AND_SOLAR_SOURCE_REPLAY "+
              json.dumps(source,sort_keys=True),flush=True)
        # The new v77 four-cell source gate is applied BEFORE scoring
        # new or old used-location ordinal animal outcomes.
        complete,source4=fourway_source_only(
            paired,source,verify_original_replay=True)
        print("V77_ORIGINAL_FOUR_WAY_SAME_BIRD_MONTH_TIDE_HEIGHT_SOURCE_FIRST "+
              json.dumps(source4,sort_keys=True),flush=True)
        old_primary=None
        if source4["admission"]==(
            "SOURCE_ADMITTED_V77_FULL_SAME_BIRD_MONTH_HEIGHT_FOUR_WAY_TIDE_LIGHT"):
            old_primary=score_matched_tide_day_night(paired,source,original_geo)
            old=old_primary["primary_original_wild_same_bird_month_rws_tide_matched_ordinal_rank"]
            if abs(old["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"]-
                   .04097869307703187)>1e-9:
                raise ValueError("SOURCE_STOP_V77_UNCHANGED_V76_BIRD_LEVEL_RESULT_DRIFT")
            print("V77_PRIOR_V76_AUTHENTIC_2010_WILD_NIGHT_DAY_REPLAY "+
                  json.dumps({
                     "unchanged_v76_night_day_ordinal_rank":
                       old["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"],
                     "unchanged_v76_95":
                       old["whole_original_bird_10000_bootstrap95"]},
                    sort_keys=True),flush=True)
        main=score_fourway_difference_in_differences(complete,source4,original_geo)
        control={}
        if source4["admission"]==(
            "SOURCE_ADMITTED_V77_FULL_SAME_BIRD_MONTH_HEIGHT_FOUR_WAY_TIDE_LIGHT"):
            for label,binwidth,clockoffset in (
                ("original_RWS_height_band_0p1m",.1,0),
                ("original_RWS_height_band_0p4m",.4,0),
                ("original_GPS_clock_minus15s",.2,-15)):
                other,other_source=tide_light_source_groups(
                    original_geo,tide,height_bin=binwidth,
                    shift_seconds=clockoffset)
                subset,qa=fourway_source_only(
                    other,other_source,verify_original_replay=False)
                control[label]=score_fourway_difference_in_differences(
                    subset,qa,original_geo,
                    seed=20261108+(1 if binwidth==.1 else 2 if binwidth==.4 else 3))
        out={
            "analysis":"V77_ORIGINAL_WILD_2010_SCHIER_SAME_TIDE_HEIGHT_FOUR_WAY_TIDAL_PHASE_BY_SOLAR_SPATIAL_MODEL_INDEX",
            "executed_commit":os.environ.get("GITHUB_SHA","local"),
            "frozen_protocol":"docs/V77_FROZEN_ORIGINAL_FOUR_WAY_TIDE_PHASE_BY_DAYLIGHT.md",
            "original_gps_Zenodo_2010_provider_MD5_SHA256_verified":True,
            "original_gps_Zenodo2010_SHA256":manifest["original_sha256"],
            "original_NIOZ_2010_all_five_month_MD5_and_fixed_SHA_verified":True,
            "original_month_sha_pins":hashproof,
            "original_RWS_2010_station":GAUGE,
            "original_RWS_measured_2010_10minute_NAP_count":EXACT_2010_GAUGE,
            "original_source_GPS_month_counts_replayed":source_qa[
                "original_fixed_five_month_hourly_positions"],
            "old_v75_all_five_original_native_model_geographic_source_replays":{
                str(m):original_geo[m]["source_receipt"] for m in MONTHS},
            "NIOZ_README_original_model_exposure_units_unknown":meaning,
            "prior_original_v76_physical_tide_and_solar_source":source,
            "prior_v76_true_wild_night_minus_day_replayed_if_source_passed":
                old_primary,
            "new_v77_source_gate_and_four_condition_main":main,
            "predeclared_height_bin_and_GPS_clock_source_sensitivity":control,
            "original_native_GPS_clock_calibration_UTC_or_GPS_unknown":True,
            "post_v76_tide_phase_difference_hypothesis_EXPLORATORY_not_external_confirmation":True,
            "no_animal_tag_exact_GPS_time_coords_RWS_rows_NIOZ_pixel_arrays_saved":True,
            "no_observed_foraging_food_or_true_intertidal_exposure_hrs_inferred":True}
        target=Path(output)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
        effect=main.get("original_2010_Schier_RWS_tide_phase_by_astro_light_interaction")
        estimate=effect.get("frozen_primary_genuine_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY") if effect else None
        print("V77_ORIGINAL_TRUE_TIDE_BY_LIGHT_FOUR_WAY_WILD_EFFECT "+
              json.dumps({
                  "original_4way_source_status":source4["admission"],
                  "original_full_four_cell_groups":
                     source4["original_four_way_exact_same_bird_month_RWS_height_groups"],
                  "original_birds":
                     source4["original_birds_in_all_four_tide_and_light_conditions"],
                  "original_4way_source_locations":
                     source4["original_four_way_source_fix_count"],
                  "frozen_flood_vs_ebb_NIGHT_minus_DAY":
                     estimate["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"] if estimate else None,
                  "genuine_bird_cluster_95":
                     estimate["whole_original_bird_10000_bootstrap95"] if estimate else None,
                  "original_birds_positive":
                     estimate["original_birds_with_night_higher"] if estimate else None,
                  "primary_status":
                     effect["frozen_exploratory_primary_status"] if effect else
                     "NOT_ESTIMATED_SOURCE_GATE"},
                  sort_keys=True),flush=True)
        print("V77_ORIGINAL_WILD_FOUR_WAY_TIDE_SOLAR_INTERACTION_COMPLETE",flush=True)
        return out
    finally:
        print("V76_AUTHENTIC_RWS_TRANSPORT_RECEIPT "+
              json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",
      default=os.environ.get("BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_RWS_v77"))
    a=p.parse_args()
    run(a.output,a.source_cache_dir)
