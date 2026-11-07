"""v61 pre-frozen same endpoint on original Schiermonnikoog 2011 GPS pairs.

Never publish original bird IDs, matched GPS indices, B coordinates/dates,
observed next-direction vectors or original RWS gauge values.
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
import matched_tide_support as v59

EXPECTED={
    "source_rows":4948,"source_birds":13,
    "unique_disjoint_actual_opposite_tide_pairs":211,
    "birds_with_at_least_ten_pairs":7,
    "matched_distinct_ISO_weeks":45,
    "matched_distinct_calendar_months":12}
EXPECTED_STAGES=(1784,1294,1276,969,572,277,248)

def verify_schier_source(rows,pairs,source_audit):
    if source_audit["admission"]!="SOURCE_SUPPORT_ADMITTED_FOR_LATER_PREREGISTERED_OUTCOME":
        raise ValueError("NOT_ADMITTED_V61_ORIGINAL_SCHIER_SOURCE_SUPPORT")
    for field,expected in EXPECTED.items():
        if source_audit.get(field)!=expected:
            raise ValueError("SOURCE_STOP_V61_FROZEN_SCHIER_AGGREGATE_DRIFT_"+field)
    if tuple(source_audit["rising_rows_with_candidate_after_sequential_gates"][s] for s in v59.STAGES)!=EXPECTED_STAGES:
        raise ValueError("SOURCE_STOP_V61_SCHIER_STAGE_COUNTS_DRIFT")
    if len(pairs)!=211:
        raise ValueError("SOURCE_STOP_V61_ORIGINAL_PRIVATE_MATCH_COUNT_DRIFT")
    return True

def run(output,cache_dir):
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    def original_gauge(station,year):
        if station!="schiermonnikoog.waddenzee" or year not in (2009,2010,2011):
            raise ValueError("SOURCE_STOP_V61_UNFROZEN_STATION_OR_YEAR")
        tide,meta=observed_original_rws_year_cached(cache,station,year)
        if meta["gauge_rows"]!=52561:
            raise ValueError("SOURCE_STOP_V61_RWS_NAP_YEAR_COUNT_DRIFT")
        print(f"V61_AUTHENTIC_SCHIER_NAP year={year} count={meta['gauge_rows']}",flush=True)
        return tide,meta
    try:
        with patch("source_fetch_resilience.observed_rws_year",new=original_gauge):
            annual,qa=load_site("schiermonnikoog")
        train,test=annual[2010],annual[2011]
        if len(train)!=7911 or len(test)!=4948:
            raise ValueError("SOURCE_STOP_V61_AUTHENTIC_ORIGINAL_2010_2011_COHORT_DRIFT")
        pins={}
        for yr in (2010,2011):
            v=qa["original_receipts"][str(yr)]
            if (v["RWS_original_NAP_count"]!=52561
                    or not v["original_GPS_MD5_and_SHA256_verified"]
                    or not v["original_GPS_SHA256"]):
                raise ValueError("SOURCE_STOP_V61_ORIGINAL_GPS_AUTHENTICATION")
            pins[str(yr)]=v["original_GPS_SHA256"]
        pairs,audit=reconstruct_private_pair_indices(test)
        verify_schier_source(test,pairs,audit)
        print("V61_SOURCE_ONLY_SCHIER_PAIR_ADMITTED "+
              json.dumps({"source_test":len(test),"pairs":len(pairs),
                          "birds_with_ten_pairs":audit["birds_with_at_least_ten_pairs"],
                          "weeks":audit["matched_distinct_ISO_weeks"],
                          "months":audit["matched_distinct_calendar_months"]},sort_keys=True),flush=True)
        # First reading of original B->C targets is strictly after source replay.
        observed=score_matched_observed_heading(train,test,pairs,forecast)
        primary=observed["metrics"]["observed_paired_tide_direction_concordance"]
        report={
            "analysis":"V61_ORIGINAL_SCHIER_REAL_OPPOSITE_PHASE_PAIRED_DIRECTION",
            "executed_commit":os.environ.get("GITHUB_SHA","local"),
            "frozen_specification":"docs/V61_FROZEN_SCHIER_OBSERVED_PAIRED_HEADING.md",
            "exact_same_v60_primary_code_unchanged":True,
            "original_GPS_2010_2011_sha256":pins,
            "source_original_RWS_2009_2010_2011_NAP_counts":[52561]*3,
            "original_source_2010_train":len(train),
            "original_source_2011_test":len(test),
            "original_GPS_provider_MD5_and_SHA256_verified":True,
            "predeclared_v59_original_source_check":audit,
            "new_authentic_paired_next_heading_result":observed,
            "source_transport_aggregate_only":cache.snapshot(),
            "no_original_animal_ids_tracks_dates_pairs_or_gauge_time_series_published":True,
            "not_causal_or_independent_new_species_validation":True}
        path=Path(output)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print("V61_ORIGINAL_PAIRED_OBSERVED_RESULT "+json.dumps({
            "pairs":len(pairs),"concordance_equal_bird":primary["equal_bird_mean"],
            "whole_bird_95":primary["whole_bird_bootstrap_95"],
            "positive_birds":primary["positive_birds"],
            "sign_flip_p_sensitivity":primary["equal_bird_one_sided_sign_flip_sensitivity_p"],
            "result":observed["observational_concordance_status"]
        },sort_keys=True),flush=True)
        print("V61_ORIGINAL_SCHIER_OBSERVED_COMPLETED",flush=True)
        return report
    finally:
        print("V61_RWS_SOURCE_TRANSPORT_RECEIPT "+
              json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_rws_v61_cache"))
    a=p.parse_args()
    run(a.output,a.source_cache_dir)
