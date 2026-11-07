"""v60: authentically observed matched opposite-tide next headings in Ameland 2011.

This runner never exports original GPS ID, paired episode indices, B positions,
times, next-heading vectors, or raw RWS values. Source gate is replayed FIRST.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
from unittest.mock import patch

from original_rws_cached_transport import OriginalRwsCache,observed_original_rws_year_cached
from run_cross_island_transfer import load_site
from original_heading_tide import forecast
from paired_real_phase_heading import (
    reconstruct_private_pair_indices,verify_frozen_primary_source,
    score_matched_observed_heading)

def run(output,cache_dir):
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    def source(station,year):
        if station!="ameland.nes" or year not in (2009,2010,2011):
            raise ValueError("SOURCE_STOP_V60_UNREGISTERED_GAUGE_STATION_OR_YEAR")
        tide,metadata=observed_original_rws_year_cached(cache,station,year)
        if metadata["gauge_rows"]!=52561:
            raise ValueError("SOURCE_STOP_V60_ORIGINAL_RWS_NAP_SOURCE_COUNT_CHANGED")
        print(f"V60_AUTHENTIC_AMELAND_NAP year={year} count={metadata['gauge_rows']}",flush=True)
        return tide,metadata
    try:
        with patch("source_fetch_resilience.observed_rws_year",new=source):
            annual,qa=load_site("ameland")
        train,test=annual[2010],annual[2011]
        if len(train)!=3753 or len(test)!=4678:
            raise ValueError("SOURCE_STOP_V60_2010_2011_ORIGINAL_AMELAND_COHORT_DRIFT")
        pins={}
        for year in (2010,2011):
            a=qa["original_receipts"][str(year)]
            if (a["RWS_original_NAP_count"]!=52561
                    or not a["original_GPS_MD5_and_SHA256_verified"]
                    or not a["original_GPS_SHA256"]):
                raise ValueError("SOURCE_STOP_V60_SOURCE_PROVIDER_PIN_CHANGED")
            pins[str(year)]=a["original_GPS_SHA256"]
        # Do NOT read next-heading target before these gates. The match routine
        # accesses only v59 frozen source-B state and own preceding movement.
        private_pairs,source_audit=reconstruct_private_pair_indices(test)
        verify_frozen_primary_source(test,private_pairs,source_audit)
        print("V60_FROZEN_SOURCE_PAIR_ADMITTED "+
              json.dumps({"n_original_triplets":len(test),
                          "pairs":len(private_pairs),
                          "qualified_birds":source_audit["birds_with_at_least_ten_pairs"],
                          "matched_weeks":source_audit["matched_distinct_ISO_weeks"],
                          "matched_months":source_audit["matched_distinct_calendar_months"],
                          "original_source_gate":source_audit["admission"]},sort_keys=True),flush=True)
        result=score_matched_observed_heading(train,test,private_pairs,forecast)
        if result["actual_real_disjoint_matched_pairs"]!=168:
            raise ValueError("SOURCE_STOP_V60_OBSERVED_HEADING_SAMPLE_DRIFT")
        out={
            "analysis":"V60_AUTHENTIC_ACTUAL_OPPOSITE_TIDE_PAIRED_DIRECTIONAL_CONCORDANCE",
            "executed_commit":os.environ.get("GITHUB_SHA","local"),
            "frozen_protocol":"docs/V60_FROZEN_ACTUAL_OPPOSITE_TIDE_PAIRED_HEADING.md",
            "source_year":2011,"model_training_year":2010,
            "source_site":"ameland",
            "source_gps_2010_2011_sha256":pins,
            "source_original_RWS_NAP_2009_2010_2011_counts":[52561]*3,
            "source_matched_v59_audit":source_audit,
            "source_gps_original_publisher_md5_and_sha256_verified":True,
            "previous_v43_v58_full_original_source_preexisting_replay_verified":True,
            "new_observed_paired_heading_result":result,
            "source_transport_aggregate_only":cache.snapshot(),
            "source_has_no_identity_disjoint_train_requirement":True,
            "scientific_scope":"Post-v59 exploratory real observed matched GPS directions, conditioned on an already studied 2010-fitted tide-phase model. No tidal manipulation, prey exposure, neighbor Boids force or universal taxa inference.",
            "original_ids_coordinates_times_pairs_per_bird_vectors_and_gauges_never_published":True}
        path=Path(output)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
        s=result["metrics"]["observed_paired_tide_direction_concordance"]
        print("V60_AUTHENTIC_PAIRED_OBSERVED_RESULT "+json.dumps({
            "pairs":result["actual_real_disjoint_matched_pairs"],
            "concordance_equal_bird":s["equal_bird_mean"],
            "concordance_bird_95":s["whole_bird_bootstrap_95"],
            "positive_birds":s["positive_birds"],
            "sign_flip_p_sensitivity":s["equal_bird_one_sided_sign_flip_sensitivity_p"],
            "actual_vs_flip_paired_equal_bird_cosine_gain":result["metrics"][
                "actual_vs_flipped_tide_cosine_loss_gain"]["equal_bird_mean"],
            "observed_heading_separation_degrees":result["metrics"][
                "observed_paired_absolute_heading_separation_degrees"]["equal_bird_mean"],
            "conclusion":result["observational_concordance_status"]
        },sort_keys=True),flush=True)
        print("V60_ORIGINAL_PAIRED_OBSERVED_COMPLETED",flush=True)
        return out
    finally:
        print("V60_SOURCE_TRANSPORT_RECEIPT "+json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_rws_v60_cache"))
    args=parser.parse_args()
    run(args.output,args.source_cache_dir)
