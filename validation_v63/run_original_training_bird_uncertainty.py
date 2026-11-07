"""v63 authenticate original Schier GPS/RWS and propagate 8 source-bird fit uncertainty.

Previous v61/v62 exact prediction, actual matched GPS source gates and original
yearly data checks are required BEFORE any new source-resampling result.
Only anonymous summaries are written. No original GPS or gauge rows exported.
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
from train_bird_uncertainty import (
    analyze_training_bird_uncertainty,PRIOR_V62_ALL,PRIOR_V62_QUALIFIED,REPS)

def run(output,cache_dir):
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    def original_nap(station,year):
        if station!="schiermonnikoog.waddenzee" or year not in (2009,2010,2011):
            raise ValueError("SOURCE_STOP_V63_WRONG_ORIGINAL_GAUGE_SOURCE")
        tide,meta=observed_original_rws_year_cached(cache,station,year)
        if meta["gauge_rows"]!=52561:
            raise ValueError("SOURCE_STOP_V63_ORIGINAL_NAP_OBSERVATION_COUNT_DRIFT")
        print(f"V63_ORIGINAL_RWS_VERIFIED year={year} n={meta['gauge_rows']}",flush=True)
        return tide,meta
    try:
        with patch("source_fetch_resilience.observed_rws_year",new=original_nap):
            annual,qa=load_site("schiermonnikoog")
        source,test=annual[2010],annual[2011]
        if len(source)!=7911 or len(test)!=4948:
            raise ValueError("SOURCE_STOP_V63_ORIGINAL_GPS_YEAR_COHORT_DRIFT")
        pins={}
        for y in (2010,2011):
            r=qa["original_receipts"][str(y)]
            if (r["RWS_original_NAP_count"]!=52561 or
                    not r["original_GPS_MD5_and_SHA256_verified"] or
                    not r["original_GPS_SHA256"]):
                raise ValueError("SOURCE_STOP_V63_ORIGINAL_GPS_RWS_IDENTITY_NOT_AUTHENTIC")
            pins[str(y)]=r["original_GPS_SHA256"]
        # First: exact unaltered outcome-BLIND 2011 original source gates.
        pairs,source_pair_audit=reconstruct_private_pair_indices(test)
        verify_schier_source(test,pairs,source_pair_audit)
        disjoint_train,disjoint_audit=disjoint_2010_training(source,test)
        qualified_pairs,qualified_audit=source_qualified_pair_subset(test,pairs)
        if (len(pairs)!=211 or len(qualified_pairs)!=204
            or len({r["id"] for r in disjoint_train})!=8):
            raise ValueError("SOURCE_STOP_V63_V62_SOURCE_COUNTS_NOT_REPRODUCED")
        print("V63_PRIOR_SOURCE_ADMITTED "+json.dumps({
            "original_2010_training":len(source),
            "original_2011_test":len(test),
            "unseen_source_train_rows":len(disjoint_train),
            "unseen_source_train_birds":disjoint_audit["disjoint_training_birds"],
            "literal_train_test_identity_overlap":disjoint_audit["literal_train_test_identity_overlap"],
            "real_pairs":len(pairs),"matched_birds":source_pair_audit["matched_birds"],
            "qualified_real_pairs":len(qualified_pairs),
            "qualified_source_birds":qualified_audit["source_qualified_birds"]
        },sort_keys=True),flush=True)
        # Second: fixed old field scores must replay before opening new v63
        # source-side uncertainty result. No change in response or ridge code.
        old=score_matched_observed_heading(source,test,pairs,forecast)
        oldT=old["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
        exact_prior_v61_replay(oldT)
        known_all=score_matched_observed_heading(disjoint_train,test,pairs,forecast)
        known_q=score_matched_observed_heading(disjoint_train,test,qualified_pairs,forecast)
        replay_all=known_all["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
        replay_q=known_q["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
        if abs(replay_all-PRIOR_V62_ALL)>1e-9 or abs(replay_q-PRIOR_V62_QUALIFIED)>1e-9:
            raise ValueError("SOURCE_STOP_V63_V62_PAIRED_HEADING_CONTROL_NOT_EXACT")
        print("V63_V61_V62_ORIGINAL_REPLAY_OK "+json.dumps({
            "old_full_2010_fit_v61_T":oldT,
            "unseen_2010_v62_all_T":replay_all,
            "unseen_2010_v62_source_qualified_T":replay_q},sort_keys=True),flush=True)
        # The new v63 result is NOT another 2011 test sample, but the
        # same observed GPS pair T over 1024 *re-fitted* 2010 models.
        uncertainty=analyze_training_bird_uncertainty(
            disjoint_train,test,pairs,qualified_pairs,forecast,reps=REPS)
        if (abs(uncertainty["main_all_211_original_real_matched_pairs"][
                "original_fixed_source_T_replay"]-replay_all)>1e-9 or
            abs(uncertainty["secondary_source_qualified_204_real_pairs"][
                "original_fixed_source_T_replay"]-replay_q)>1e-9):
            raise ValueError("SOURCE_STOP_V63_COMPACT_SCORE_REPLAY_DIFFERENT")
        report={
            "analysis":"V63_TRAIN_SOURCE_AND_TEST_BIRD_UNCERTAINTY_OF_REAL_TIDE_PAIRED_HEADING",
            "executed_commit":os.environ.get("GITHUB_SHA","local"),
            "frozen_protocol":"docs/V63_FROZEN_TRAIN_AND_TEST_BIRD_BOOTSTRAP_TIDE.md",
            "known_original_v62_source":"42327445833",
            "original_publisher_MD5_and_pinned_SHA256_verified":True,
            "source_gps_2010_2011_sha256":pins,
            "original_RWS_2009_2010_2011_NAP_obs":[52561]*3,
            "old_v61_v62_original_model_replay":{
                "old_v61_full_2010_train_T":oldT,
                "old_v62_original_unseen_fit_211_T":replay_all,
                "old_v62_unseen_fit_204_T":replay_q},
            "source_pair_admission":source_pair_audit,
            "source_disjoint_2010_training":disjoint_audit,
            "source_only_qualified_pair_admission":qualified_audit,
            "new_training_bird_bootstrap_and_joint_uncertainty":uncertainty,
            "original_RWS_transport_only_aggregate":cache.snapshot(),
            "no_raw_original_bird_ID_exact_GPS_times_coords_pairs_bearings_or_gauge_series":True,
            "ecological_boundaries":"Same already studied Eurasian oystercatcher population; post-v62 exploratory. Train-bird and test-bird bootstrap intervals are conditional on historical records and fitted model family, not random tide intervention, measured prey-front, social Reynolds forces, or multi-species causal generality."}
        path=Path(output)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        all_result=uncertainty["main_all_211_original_real_matched_pairs"]
        q_result=uncertainty["secondary_source_qualified_204_real_pairs"]
        print("V63_ORIGINAL_TRAINING_BIRD_UNCERTAINTY_RESULT "+json.dumps({
            "original_real_pairs":len(pairs),
            "unique_training_birds":disjoint_audit["disjoint_training_birds"],
            "source_bootstrap_refits":REPS,
            "old_v62_primary_T":replay_all,
            "primary_train_only_95":all_result["train_bird_only_bootstrap"]["percentile_95"],
            "primary_joint_train_test_95":all_result["joint_train_and_test_bird_bootstrap"]["percentile_95"],
            "primary_joint_fraction_positive":all_result["joint_train_and_test_bird_bootstrap"]["fraction_positive"],
            "primary_loo_positive":all_result["leave_one_original_train_bird_out"]["positive_leave_one_out_models"],
            "old_v62_qualified_T":replay_q,
            "qualified_train_only_95":q_result["train_bird_only_bootstrap"]["percentile_95"],
            "qualified_joint_train_test_95":q_result["joint_train_and_test_bird_bootstrap"]["percentile_95"],
            "qualified_joint_fraction_positive":q_result["joint_train_and_test_bird_bootstrap"]["fraction_positive"],
            "qualified_loo_positive":q_result["leave_one_original_train_bird_out"]["positive_leave_one_out_models"],
            "primary_status":uncertainty["v63_primary_status"],
            "secondary_status":uncertainty["qualified_secondary_status"]
        },sort_keys=True),flush=True)
        print("V63_ORIGINAL_SOURCE_AND_UNCERTAINTY_COMPLETE",flush=True)
        return report
    finally:
        print("V63_RWS_SOURCE_TRANSPORT_RECEIPT "+json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_rws_v63_cache"))
    args=p.parse_args()
    run(args.output,args.source_cache_dir)
