"""v76 authentic 2010 wild bird vs true observed RWS tide state night/day rank.

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
        paired,source=tide_light_source_groups(original_geo,tide,
            height_bin=.2,shift_seconds=0)
        print("V76_ORIGINAL_SOURCE_MATCHED_RWS_TIDE_AND_DAY_NIGHT_BEFORE_OUTCOME "+
              json.dumps(source,sort_keys=True),flush=True)
        primary=score_matched_tide_day_night(paired,source,original_geo)
        controls={}
        if source["admission"]==(
            "SOURCE_ADMITTED_V76_ORIGINAL_REAL_SAME_BIRD_MONTH_TIDE_STATE"):
            for label,binwidth,clockoffset in (
                ("height_bin_0p1m_source_sensitivity",.1,0),
                ("height_bin_0p4m_source_sensitivity",.4,0),
                ("native_clock_minus15seconds_source_sensitivity",.2,-15)):
                child,support=tide_light_source_groups(
                    original_geo,tide,height_bin=binwidth,
                    shift_seconds=clockoffset)
                controls[label]=score_matched_tide_day_night(
                    child,support,original_geo,seed=20261108+
                    (1 if binwidth==.1 else 2 if binwidth==.4 else 3))
        out={
            "analysis":"V76_ORIGINAL_2010_SCHIER_NATIVE_NIOZ_MODEL_RANK_AT_MATCHED_ACTUAL_RWS_TIDE_AND_DAY_NIGHT",
            "executed_commit":os.environ.get("GITHUB_SHA","local"),
            "frozen_protocol":"docs/V76_FROZEN_SAME_TIDE_STATE_DAY_NIGHT_WILD_HABITAT_USE.md",
            "original_gps_Zenodo2010_provider_MD5_SHA256_verified":True,
            "original_gps_Zenodo2010_SHA256":manifest["original_sha256"],
            "original_native_NIOZ_2010_five_months_provider_MD5_verified":True,
            "source_model_month_shas":hashproof,
            "original_RWS_measured_2010_10minute_NAP_count":EXACT_2010_GAUGE,
            "original_RWS_station":GAUGE,
            "original_source_cohort_five_month_bird_and_hour_receipt":source_qa[
                "original_fixed_five_month_hourly_positions"],
            "old_v75_original_month_1km_geometric_source_receipts":{
                str(m):original_geo[m]["source_receipt"] for m in MONTHS},
            "original_model_README_exposure_unit_unverified":meaning,
            "original_true_RWS_tide_day_night_matched_primary":primary,
            "separate_preregistered_sensitivity_outcomes_regardless_sign":controls,
            "no_2011_NIOZ_model_geographic_or_GPS_reconstructed":True,
            "post_v75_unmatched_day_night_result_known_EXPLORATORY":True,
            "no_animal_ID_exact_time_coordinates_RWS_series_or_NIOZ_pixels_exported":True}
        target=Path(output)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
        main=primary.get("primary_original_wild_same_bird_month_rws_tide_matched_ordinal_rank")
        print("V76_ACTUAL_WILD_GPS_TIDE_CONDITION_MATCHED_NIGHT_DAY_RESULT "+
              json.dumps({
                "source_status":source["admission"],
                "paired_original_true_tide_strata":
                    source["original_paired_condition_groups_ge5_day_and_night"],
                "matched_birds":source["original_distinct_birds_in_tide_matched_groups"],
                "matched_2010_GPS_day":source["original_genuine_day_GPS_positions_in_matched_tide_conditions"],
                "matched_2010_GPS_night":source["original_genuine_night_GPS_positions_in_matched_tide_conditions"],
                "original_bird_equal_night_minus_day":
                    main["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"] if main else None,
                "bird_bootstrap95":
                    main["whole_original_bird_10000_bootstrap95"] if main else None,
                "birds_positive":
                    main["original_birds_with_night_higher"] if main else None,
                "frozen_status":main["frozen_exploratory_main_status"]
                    if main else "NOT_ESTIMATED_SOURCE_GATE"},
                sort_keys=True),flush=True)
        print("V76_ORIGINAL_TIDAL_HABITAT_DAY_NIGHT_FIELD_COMPLETE",flush=True)
        return out
    finally:
        print("V76_AUTHENTIC_RWS_TRANSPORT_RECEIPT "+
              json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",
      default=os.environ.get("BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_RWS_v76"))
    a=p.parse_args()
    run(a.output,a.source_cache_dir)
