"""v70 actual RWS tide×light opportunity in two Wadden island 2010–11 gauges.

Schier field runner replays v59/v61/v62 (positive) and v69 (negative)
before scoring a NEW fixed 2011 original GPS target outcome. Ameland
companion is a physically measured GAUGE-ONLY analysis, no animal outcome.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
from unittest.mock import patch

from original_rws_cached_transport import OriginalRwsCache,observed_original_rws_year_cached
from run_cross_island_transfer import load_site
from original_heading_tide import forecast as original_v41_forecast
from paired_real_phase_heading import reconstruct_private_pair_indices,score_matched_observed_heading
from run_original_schier_paired_heading import verify_schier_source
from unseen_identity_support import (
    disjoint_2010_training,source_qualified_pair_subset,exact_prior_v61_replay)
from tide_daylight_interaction import (
    augment as v69_solar_augment,source_gate as v69_source_gate,
    score_two_clocks as v69_old_score)
from physical_low_tide_sun_overlap import (
    ObservedGaugeSolarOpportunity,measured_2010_low_cutoff,
    summarize_real_annual_opportunity,source_only_GPS_window_gate)
from real_low_tide_sun_direction import score_field_opportunity
from tidal_front import TideSeries
from run_phase_control_transfer import merge_gauges

STATIONS={"schiermonnikoog":"schiermonnikoog.waddenzee","ameland":"ameland.nes"}
V62_ALL=.17641912034715593
V62_Q=.03815442590078731
V69_NEGATIVE=-.03006928542491632

def run(site,output,cache_dir):
    if site not in STATIONS:
        raise ValueError("SOURCE_STOP_V70_UNREGISTERED_WADDEN_SITE")
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    orig={}
    def authenticated(station,year):
        if station!=STATIONS[site] or year not in (2009,2010,2011):
            raise ValueError("SOURCE_STOP_V70_ORIGINAL_GAUGE_SITE_YEAR_CHANGED")
        tide,meta=observed_original_rws_year_cached(cache,station,year)
        if meta["gauge_rows"]!=52561:
            raise ValueError("SOURCE_STOP_V70_YEAR_AUTHENTICATED_GAUGE_ROWS_CHANGED")
        orig[year]=tide
        print("V70_RWS_ORIGINAL_VERIFIED "+json.dumps({
            "site":site,"year":year,"original_gauge_count":meta["gauge_rows"]},
            sort_keys=True),flush=True)
        return tide,meta
    try:
        cohort=None;receipts=None
        if site=="schiermonnikoog":
            with patch("source_fetch_resilience.observed_rws_year",new=authenticated):
                cohort,receipts=load_site(site)
            full,test=cohort[2010],cohort[2011]
            if len(full)!=7911 or len(test)!=4948:
                raise ValueError("SOURCE_STOP_V70_ORIGINAL_GPS_EPISODE_COHORT_DRIFT")
            gps_shas={}
            for yr in (2010,2011):
                receipt=receipts["original_receipts"][str(yr)]
                if (receipt["RWS_original_NAP_count"]!=52561 or
                    not receipt["original_GPS_MD5_and_SHA256_verified"] or
                    not receipt["original_GPS_SHA256"]):
                    raise ValueError("SOURCE_STOP_V70_ORIGINAL_PUBLISHER_MD5_SHA_REPLAY_FAILED")
                gps_shas[str(yr)]=receipt["original_GPS_SHA256"]
            # Source-only strict v59 matching and support without target values.
            pairs,pair_audit=reconstruct_private_pair_indices(test)
            verify_schier_source(test,pairs,pair_audit)
            disjoint,id_audit=disjoint_2010_training(full,test)
            qualified,qualified_audit=source_qualified_pair_subset(test,pairs)
            if len(pairs)!=211 or len(qualified)!=204:
                raise ValueError("SOURCE_STOP_V70_OLD_WILD_REAL_PAIR_COUNT")
        else:
            # Ameland contributes only measured physical 2010–11 day×tide
            # source observation, not a new fabricated GPS cohort.
            for year in (2010,2011):
                authenticated(STATIONS[site],year)
            gps_shas=None;pair_audit=None;id_audit=None;qualified_audit=None
        q25=measured_2010_low_cutoff(orig[2010])
        merged,waterqa=merge_gauges(orig,TideSeries)
        physical=ObservedGaugeSolarOpportunity(merged,site=site,cutoff=q25)
        annual={str(yr):summarize_real_annual_opportunity(physical,yr)
                for yr in (2010,2011)}
        if any(v["original_physical_source_days"]!=365 for v in annual.values()):
            raise ValueError("SOURCE_STOP_V70_PHYSICAL_365_FULL_DAYS_INCOMPLETE")
        print("V70_ORIGINAL_TIDAL_DAYLIGHT_PHYSICAL_SOURCE "+json.dumps({
            "site":site,"2010_fixed_station_gauge_Q25_m_NAP":q25,
            "annual":{yr:{
                "days":r["original_physical_source_days"],
                "same_photoperiod_matched_pre_post_solstice_pairs":
                    r["predeclared_same_daylength_sun_branch_pairs"],
                "same_daylength_paired_sunlit_low_water_median_abs_hour_difference":
                    r["same_daylength_pair_absolute_sunlit_low_h_difference"]["median"]
                    if r["same_daylength_pair_absolute_sunlit_low_h_difference"] else None,
                "pairs_with_difference_ge1_hour":r["same_daylength_pairs_difference_ge1_hour"],
                "annual_median_low_tide_sunlit_h":
                    r["source_low_water_sunlit_h_per_day"]["median"]}
                      for yr,r in annual.items()}},sort_keys=True),flush=True)
        animal=None
        previous=None
        if site=="schiermonnikoog":
            # Before any new 2011 heading outcome: source-only physical
            # B covariates and 2010-train/2011-test source opportunity gate.
            train_solar=v69_solar_augment(disjoint)
            test_solar=v69_solar_augment(test)
            v69_source_gate(train_solar,test_solar)
            train=physical.augmented_original_GPS_rows(train_solar)
            test70=physical.augmented_original_GPS_rows(test_solar)
            source_gate=source_only_GPS_window_gate(train,test70)
            print("V70_FROZEN_SOURCE_OPPORTUNITY_ADMITTED "+json.dumps(
                source_gate,sort_keys=True),flush=True)
            # Old known actual 2011 GPS heading result must exactly replay
            # before computing any new endpoint.
            prior=score_matched_observed_heading(full,test,pairs,original_v41_forecast)
            old=prior["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
            exact_prior_v61_replay(old)
            pairedall=score_matched_observed_heading(disjoint,test,pairs,original_v41_forecast)
            pairedq=score_matched_observed_heading(disjoint,test,qualified,original_v41_forecast)
            oldall=pairedall["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
            oldq=pairedq["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
            if abs(oldall-V62_ALL)>1e-9 or abs(oldq-V62_Q)>1e-9:
                raise ValueError("SOURCE_STOP_V70_OLD_POSITIVE_TIDE_GPS_PAIRS_CHANGED")
            old_v69=v69_old_score(train_solar,test_solar)
            old_g=old_v69["original_2011_equal_bird_heldout_next_heading_2D_half_MSE"][
                "primary_M2_vs_M0_phase_by_solar_elevation_and_daylength"][
                "bird_equal_gain_half_MSE"]
            if abs(old_g-V69_NEGATIVE)>1e-9:
                raise ValueError("SOURCE_STOP_V70_OLD_NEGATIVE_SOLAR_INTERACTION_RESULT_CHANGED")
            previous={"v61_full2010_train_real_matched_T":old,
                      "v62_disjoint_train_211_real_pairs_T":oldall,
                      "v62_disjoint_train_204_real_pairs_T":oldq,
                      "v69_previous_simple_tide_by_daylength_gain_NEGATIVE":old_g}
            print("V70_ALL_OLD_REAL_TIDE_GPS_POSITIVE_AND_SOLAR_NEGATIVE_REPLAY "+
                  json.dumps(previous,sort_keys=True),flush=True)
            animal=score_field_opportunity(train,test70)
            q=animal["2010_disjoint_training_and_2011_original_bird_equal_heldout"]
            print("V70_ORIGINAL_WILD_TIDAL_DAYLIGHT_GPS_RESULT "+json.dumps({
                "status":animal["frozen_primary_source_and_bird_interval_decision"],
                "source_birds":source_gate["train2010"]["original_individuals"],
                "eval_birds":source_gate["test2011"]["original_individuals"],
                "new_primary_M1_minus_M0_halfMSE_gain":
                    q["primary_M1_minus_M0_12h_overlap_beyond_marginal_hours"][
                        "bird_equal_gain_half_MSE"],
                "new_primary_M1_minus_M0_95":
                    q["primary_M1_minus_M0_12h_overlap_beyond_marginal_hours"][
                        "whole_bird_cluster_bootstrap_95"],
                "new_primary_pct":
                    q["primary_M1_minus_M0_12h_overlap_beyond_marginal_hours"][
                        "percent_half_MSE_reduction_vs_baseline"],
                "new_primary_positive_original_birds":
                    q["primary_M1_minus_M0_12h_overlap_beyond_marginal_hours"][
                        "original_birds_positive"],
                "secondary_M2_minus_M0":
                    q["secondary_M2_minus_M0_phase_x_opportunity"]["bird_equal_gain_half_MSE"],
                "past_six_hour_offset_ghost_M1_minus_Mghost":
                    q["negative_control_M1_minus_Mghost_actual_vs_6h_earlier_window"][
                        "bird_equal_gain_half_MSE"]},sort_keys=True),flush=True)
        result={
            "analysis":"V70_TWO_REAL_WADDEN_TIDE_GAUGE_SUNLIGHT_WINDOWS_AND_SCHIER_WILD_GPS",
            "executed_commit":os.environ.get("GITHUB_SHA","local"),
            "site":site,
            "original_station":STATIONS[site],
            "frozen_protocol":"docs/V70_FROZEN_MEASURED_TIDE_LOW_WATER_SUNLIT_OVERLAP.md",
            "official_original_RWS_WATHTE_meting_cm_NAP_year_counts":{
                str(k):len(v.times) for k,v in orig.items()},
            "measured_station_year_Q25_from_only_2010_m_NAP":q25,
            "original_gauge_merge_aggregate_receipt":waterqa,
            "observed_physical_low_water_x_astronomical_daylight_source_years":annual,
            "source_GPS_MD5_and_fixed_SHA256_verified":gps_shas is not None,
            "original_GPS_year_sha256":gps_shas,
            "original_strict_2011_opposite_phase_source":pair_audit,
            "disjoint_training_literal_bird_ids_aggregate":id_audit,
            "old_204_source_qualified_pair_receipt":qualified_audit,
            "old_v61_v62_v69_field_results_replayed":previous,
            "new_original_wild_schier_heldout_next_heading_if_admitted":animal,
            "observed_station_water_level_Q25_not_exposed_intertidal_habitat":True,
            "no_future_original_RWS_measured_gauge_in_animal_predictor":True,
            "no_raw_GPS_original_bird_ID_location_or_time_or_RWS_series_exported":True,
            "limits":"Retrospective measured water height 2010-Q25 index, no 2010 ground elevation or foraging prey, one GPS wild species, two adjacent tidal gauges physical source not two independent populations; exploratory same original 2011 bird cohort; astronomical station sunrise, not in situ photometry; no tide causation or social Boids force."}
        dest=Path(output)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("V70_ORIGINAL_TIDAL_LIGHT_SOURCE_AND_GPS_COMPLETE "+site,flush=True)
        return result
    finally:
        print("V70_ORIGINAL_RWS_TRANSPORT_RECEIPT "+json.dumps(
            cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=tuple(STATIONS),required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_rws_v70_cache"))
    a=p.parse_args()
    run(a.site,a.output,a.source_cache_dir)
