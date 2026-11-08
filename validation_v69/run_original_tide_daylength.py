"""Original 2010/2011 Schier two-clock/tidal-daylight forecast runner.

Original source identity and v59-v63 previous results replayed first; new
solar/source support gate before touching new daylight-dependent outcome scores.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
from unittest.mock import patch

from original_rws_cached_transport import OriginalRwsCache,observed_original_rws_year_cached
from run_cross_island_transfer import load_site
from original_heading_tide import forecast
from paired_real_phase_heading import (
    reconstruct_private_pair_indices,score_matched_observed_heading)
from run_original_schier_paired_heading import verify_schier_source
from unseen_identity_support import (
    disjoint_2010_training,source_qualified_pair_subset,exact_prior_v61_replay)
from tide_daylight_interaction import augment,source_gate,score_two_clocks

OLD_ALL=.17641912034715593
OLD_QUALIFIED=.03815442590078731

def run(output,cache_dir):
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    def original_nap(station,year):
        if station!="schiermonnikoog.waddenzee" or year not in (2009,2010,2011):
            raise ValueError("SOURCE_STOP_V69_UNFROZEN_WADDEN_GAUGE")
        tide,meta=observed_original_rws_year_cached(cache,station,year)
        if meta["gauge_rows"]!=52561:
            raise ValueError("SOURCE_STOP_V69_ANNUAL_RWS_SOURCE_COUNT_DRIFT")
        print("V69_OFFICIAL_RWS_YEAR_AUTHENTICATED "+str(year),flush=True)
        return tide,meta
    try:
        with patch("source_fetch_resilience.observed_rws_year",new=original_nap):
            annual,qa=load_site("schiermonnikoog")
        full_train,original_test=annual[2010],annual[2011]
        if len(full_train)!=7911 or len(original_test)!=4948:
            raise ValueError("SOURCE_STOP_V69_ZENODO_ORIGINAL_GPS_COUNT_DRIFT")
        sha={}
        for yr in (2010,2011):
            rec=qa["original_receipts"][str(yr)]
            if (rec["RWS_original_NAP_count"]!=52561 or
                    not rec["original_GPS_MD5_and_SHA256_verified"] or
                    not rec["original_GPS_SHA256"]):
                raise ValueError("SOURCE_STOP_V69_ORIGINAL_FIELD_IDENTITY")
            sha[str(yr)]=rec["original_GPS_SHA256"]
        pairs,sourcepairqa=reconstruct_private_pair_indices(original_test)
        verify_schier_source(original_test,pairs,sourcepairqa)
        disjoint,disjoint_qa=disjoint_2010_training(full_train,original_test)
        supported,supported_qa=source_qualified_pair_subset(original_test,pairs)
        if len(supported)!=204:
            raise ValueError("SOURCE_STOP_V69_OLD_204_PAIR_SOURCE_DRIFT")
        print("V69_UNCHANGED_V59_SOURCE_PAIRED_AND_ID_DISJOINT "+json.dumps({
            "source_2010_all":len(full_train),
            "source_2010_disjoint":len(disjoint),
            "source_2011":len(original_test),"original_paired_2011":len(pairs),
            "original_source_qualified":len(supported)},sort_keys=True),flush=True)
        previous=score_matched_observed_heading(full_train,original_test,pairs,forecast)
        old=previous["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
        exact_prior_v61_replay(old)
        full=score_matched_observed_heading(disjoint,original_test,pairs,forecast)
        qualified=score_matched_observed_heading(disjoint,original_test,supported,forecast)
        old_all=full["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
        old_q=qualified["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
        if abs(old_all-OLD_ALL)>1e-9 or abs(old_q-OLD_QUALIFIED)>1e-9:
            raise ValueError("SOURCE_STOP_V69_OLD_V62_WILD_HEADING_T_REPLAY_DRIFT")
        print("V69_FROZEN_OLD_FIELD_POSITIVE_REPLAY "+json.dumps({
            "full_train_2010_matched_T":old,
            "disjoint_train_matched_T_211":old_all,
            "disjoint_train_source_qualified_T_204":old_q},sort_keys=True),flush=True)
        # Astronomy depends solely on public location and exact B UTC time;
        # source coverage is checked BEFORE running a single new model.
        train=augment(disjoint)
        test=augment(original_test)
        original_solar_source=source_gate(train,test)
        print("V69_SOLAR_SOURCE_GATE_ADMITTED "+json.dumps(original_solar_source,sort_keys=True),flush=True)
        comparison=score_two_clocks(train,test)
        result={
            "analysis":"V69_WILD_WADDEN_TIDAL_PHASE_BY_DAYLIGHT_PHOTOPERIOD_NEXT_HEADING",
            "executed_commit":os.environ.get("GITHUB_SHA","local"),
            "frozen_protocol":"docs/V69_FROZEN_TIDAL_SOLAR_DAYLENGTH_INTERACTION_FIELD.md",
            "original_ZENODO_GPS_provider_MD5_SHA256_verified":True,
            "source_ZENODO_original_2010_2011_SHA256":sha,
            "original_OFFICIAL_RWS_WATHTE_NAP_2009_2011_count_each":52561,
            "original_GPS_years":[2010,2011],
            "source_bird_training_disjoint_receipt":disjoint_qa,
            "unchanged_v59_source_pair_gate":sourcepairqa,
            "unchanged_v62_qualified_support_receipt":supported_qa,
            "previous_known_field_effects_replayed":{
                "old_full_2010_train_T":old,
                "old_disjoint_2010_train_2011_test_all_211_T":old_all,
                "old_disjoint_2010_train_2011_test_support_204_T":old_q
            },
            "new_original_astronomical_light_tidal_forecast":comparison,
            "source_RWS_transport_aggregate_only":cache.snapshot(),
            "no_raw_bird_ID_coords_dates_solar_episode_next_headings_or_gauge_rows_exported":True,
            "scientific_ceiling":"Historical one-species one-region exploratory interaction after v63 tide findings. Solar illumination model is astronomical, not measured exposure. No independent taxon replication, tide causality, prey front or social Boids mechanics."}
        dest=Path(output)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        src=comparison["frozen_source_only_solar_illumination_qa"]
        m=comparison["original_2011_equal_bird_heldout_next_heading_2D_half_MSE"]
        print("V69_ORIGINAL_TIDAL_SOLAR_INTERACTION_RESULT "+json.dumps({
            "new_source_train":len(train),"new_source_test":len(test),
            "2010_source_day":src["train"]["sun_above_horizon_source_triplets"],
            "2010_source_night":src["train"]["sun_below_horizon_source_triplets"],
            "2011_source_day":src["test"]["sun_above_horizon_source_triplets"],
            "2011_source_night":src["test"]["sun_below_horizon_source_triplets"],
            "2011_source_months":src["test"]["original_calendar_months_with_source"],
            "primary_gain":m["primary_M2_vs_M0_phase_by_solar_elevation_and_daylength"]["bird_equal_gain_half_MSE"],
            "primary_gain95":m["primary_M2_vs_M0_phase_by_solar_elevation_and_daylength"]["whole_bird_cluster_bootstrap_95"],
            "primary_gain_pct":m["primary_M2_vs_M0_phase_by_solar_elevation_and_daylength"]["percent_half_MSE_reduction_vs_baseline"],
            "primary_birds_positive":m["primary_M2_vs_M0_phase_by_solar_elevation_and_daylength"]["original_birds_positive"],
            "solar_interaction_gain":m["secondary_M1_vs_M0_phase_by_solar_elevation"]["bird_equal_gain_half_MSE"],
            "photoperiod_increment":m["secondary_M2_vs_M1_extra_phase_by_daylength"]["bird_equal_gain_half_MSE"],
            "ghost_gain":m["misaligned_sun_6hour_ghost_M2_vs_Mghost"]["bird_equal_gain_half_MSE"],
            "status":comparison["primary_status"]
        },sort_keys=True),flush=True)
        print("V69_ORIGINAL_TIDAL_DAYLENGTH_FIELD_COMPLETED",flush=True)
        return result
    finally:
        print("V69_RWS_TRANSPORT_RECEIPT "+json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_RWS_v69"))
    a=p.parse_args()
    run(a.output,a.source_cache_dir)
