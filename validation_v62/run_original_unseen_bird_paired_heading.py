"""v62 original Schier same 2011 observed pairs, 2010 identities strictly held out.

The scientifically new object is a fitted 2010 source model trained on **zero**
birds whose IDs occur in 2011 original test; frozen 211 wild observed pairs
and endpoint remain v59/v60/v61. All outputs are anonymous aggregate-only.
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

def run(output,cache_dir):
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    def actual_nap(station,year):
        if station!="schiermonnikoog.waddenzee" or year not in (2009,2010,2011):
            raise ValueError("SOURCE_STOP_V62_UNREGISTERED_NAP_GAUGE")
        tide,meta=observed_original_rws_year_cached(cache,station,year)
        if meta["gauge_rows"]!=52561:
            raise ValueError("SOURCE_STOP_V62_MEASURED_NAP_COUNT_DRIFT")
        print(f"V62_ORIGINAL_RWS_ADMITTED year={year} n={meta['gauge_rows']}",flush=True)
        return tide,meta
    try:
        with patch("source_fetch_resilience.observed_rws_year",new=actual_nap):
            annual,qa=load_site("schiermonnikoog")
        full_train,test=annual[2010],annual[2011]
        pins={}
        for yr in (2010,2011):
            source=qa["original_receipts"][str(yr)]
            if not source["original_GPS_MD5_and_SHA256_verified"] or not source["original_GPS_SHA256"]:
                raise ValueError("SOURCE_STOP_V62_GPS_PROVIDER_MD5_SHA256_CHANGED")
            pins[str(yr)]=source["original_GPS_SHA256"]
        # No true next heading is accessed during source matching, identity removal,
        # or qualified subset selection. Keep full 2011 target cohort.
        pairs,source_audit=reconstruct_private_pair_indices(test)
        verify_schier_source(test,pairs,source_audit)
        train,identity_audit=disjoint_2010_training(full_train,test)
        subset,subset_audit=source_qualified_pair_subset(test,pairs)
        print("V62_UNSEEN_ID_AND_V59_SOURCE_ADMITTED "+json.dumps({
            "original_2010_train":len(full_train),
            "unseen_2010_fit":len(train),
            "unseen_2010_birds":identity_audit["disjoint_training_birds"],
            "original_2011_birds":identity_audit["original_2011_test_birds"],
            "overlap":identity_audit["literal_train_test_identity_overlap"],
            "original_all_matched_pairs":len(pairs),
            "source_qualified_pairs":len(subset),
            "source_qualified_birds":subset_audit["source_qualified_birds"]},
            sort_keys=True),flush=True)
        # Known v61 full-fit 2010 exact replay is a source/model integrity check,
        # not a new success measure, scored after original v59 source admission.
        old=score_matched_observed_heading(full_train,test,pairs,forecast)
        old_t=old["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"]
        exact_prior_v61_replay(old_t)
        print("V62_OLD_V61_EXACT_REPLAY_OK "+json.dumps({"v61_T":old_t},sort_keys=True),flush=True)
        # Now, and only now, score the frozen identity-disjoint train model
        # against genuine future 2011 original B->C directional observations.
        all_results=score_matched_observed_heading(train,test,pairs,forecast)
        qualified_results=score_matched_observed_heading(train,test,subset,forecast)
        main=all_results["metrics"]["observed_paired_tide_direction_concordance"]
        q=qualified_results["metrics"]["observed_paired_tide_direction_concordance"]
        result={
            "analysis":"V62_SCHIER_REAL_OPPOSITE_TIDE_UNSEEN_TRAINING_BIRDS",
            "executed_code_commit":os.environ.get("GITHUB_SHA","local"),
            "frozen_protocol":"docs/V62_FROZEN_UNSEEN_BIRD_REAL_PAIRED_HEADING.md",
            "original_GPS_MD5_and_SHA256_verified":True,
            "original_GPS_2010_2011_sha256":pins,
            "RWS_2009_2010_2011_original_NAP_rows":[52561]*3,
            "v59_precommitted_unchanged_source_audit":source_audit,
            "v62_frozen_identity_disjoint_training_source":identity_audit,
            "v62_predefined_qualified_source_only_subset":subset_audit,
            "old_v61_T_replayed_to_tolerance_1e_minus_9":old_t,
            "v62_primary_all_original_matched_birds":all_results,
            "v62_secondary_source_qualified_at_least_ten_pairs":qualified_results,
            "source_transport_aggregate_only":cache.snapshot(),
            "limits":"Post-v61 exploratory. Same species and previously studied historical field cohort. Source IDs literally disjoint across 2010 fit and 2011 test, not independent ID recapture audit. No tide causation, 3D front movement, prey, social Boids force, or taxon-general niche response identified.",
            "no_raw_bird_ids_locations_times_source_matches_headings_or_NAP_published":True}
        path=Path(output)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("V62_ORIGINAL_UNSEEN_BIRD_REAL_PAIRED_RESULT "+json.dumps({
            "original_pairs":len(pairs),
            "source_qualified_pairs":len(subset),
            "primary_T":main["equal_bird_mean"],
            "primary_whole_bird_95":main["whole_bird_bootstrap_95"],
            "primary_positive_birds":main["positive_birds"],
            "primary_sign_flip_sensitivity_p":main["equal_bird_one_sided_sign_flip_sensitivity_p"],
            "primary_status":all_results["observational_concordance_status"],
            "qualified_T":q["equal_bird_mean"],
            "qualified_whole_bird_95":q["whole_bird_bootstrap_95"],
            "qualified_positive_birds":q["positive_birds"]},sort_keys=True),flush=True)
        print("V62_UNSEEN_SOURCE_OBSERVED_COMPLETED",flush=True)
        return result
    finally:
        print("V62_RWS_SOURCE_TRANSPORT_RECEIPT "+
              json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_rws_v62_cache"))
    a=p.parse_args()
    run(a.output,a.source_cache_dir)
