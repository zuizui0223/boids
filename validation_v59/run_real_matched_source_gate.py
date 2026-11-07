"""v59 authentic original GPS/RWS SOURCE-ONLY eligibility; no new heading score."""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
from unittest.mock import patch

from matched_tide_support import audit_source_only
from original_rws_cached_transport import OriginalRwsCache,observed_original_rws_year_cached
from run_cross_island_transfer import load_site

EXPECTED={"ameland":(4678,5),"schiermonnikoog":(4948,13)}

def run(output,cache_dir,sites=("ameland","schiermonnikoog")):
    if not sites or any(site not in EXPECTED for site in sites):
        raise ValueError("SOURCE_STOP_V59_INVALID_SITE_SELECTION")
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    def actual_gauge(station,year):
        series,metadata=observed_original_rws_year_cached(cache,station,year)
        if year not in (2009,2010,2011) or metadata["gauge_rows"]!=52561:
            raise ValueError("SOURCE_STOP_ORIGINAL_RWS_NAP_COUNT_CHANGED")
        print(f"V59_ORIGINAL_RWS_ADMITTED station={station} year={year} n={metadata['gauge_rows']}",flush=True)
        return series,metadata
    output_sites={}
    try:
        with patch("source_fetch_resilience.observed_rws_year",new=actual_gauge):
            for site in sites:
                annual,source_qa=load_site(site)
                original=annual[2011]
                expected_n,expected_birds=EXPECTED[site]
                if len(original)!=expected_n or len({r["id"] for r in original})!=expected_birds:
                    raise ValueError("SOURCE_STOP_V59_V58_ORIGINAL_HELDOUT_COHORT_DRIFT")
                for yr in (2009,2010,2011):
                    if source_qa["original_receipts"][str(yr)]["RWS_original_NAP_count"]!=52561:
                        raise ValueError("SOURCE_STOP_V59_AUTHENTIC_GAUGE_COUNT_DRIFT")
                pins={}
                for yr in (2010,2011):
                    r=source_qa["original_receipts"][str(yr)]
                    if not r["original_GPS_MD5_and_SHA256_verified"] or not r["original_GPS_SHA256"]:
                        raise ValueError("SOURCE_STOP_V59_ORIGINAL_GPS_PIN_INVALID")
                    pins[str(yr)]=r["original_GPS_SHA256"]
                audit=audit_source_only(original)
                if audit["source_rows"]!=expected_n:
                    raise ValueError("SOURCE_STOP_V59_MATCHING_DROPPED_ORIGINAL_ROWS")
                output_sites[site]={
                    "original_GPS_provider_MD5_and_SHA256_verified":True,
                    "original_GPS_sha256_2010_2011":pins,
                    "original_RWS_2009_2010_2011_NAP_counts":[52561]*3,
                    "prior_known_v41_full_source_heading_replay_performed":True,
                    "new_source_only_pair_eligibility":audit}
                print("V59_ORIGINAL_SOURCE_ONLY "+json.dumps({
                    "site":site,
                    "original_2011_rows":audit["source_rows"],
                    "pairs":audit["unique_disjoint_actual_opposite_tide_pairs"],
                    "birds_with_ten_pairs":audit["birds_with_at_least_ten_pairs"],
                    "weeks":audit["matched_distinct_ISO_weeks"],
                    "months":audit["matched_distinct_calendar_months"],
                    "admission":audit["admission"],
                    "candidate_stage_counts":audit["rising_rows_with_candidate_after_sequential_gates"]},
                    sort_keys=True),flush=True)
        result={
            "analysis":"V59_ACTUAL_OPPOSITE_TIDE_SAME_BIRD_SAME_B_FEASIBILITY",
            "source_code_commit":os.environ.get("GITHUB_SHA","local"),
            "preexisting_v58_successful_original_source_run":"42322154225",
            "predeclared_primary":"ameland",
            "completed_source_site_selection":list(sites),
            "companion":"schiermonnikoog",
            "already_inspected_original_cohorts_not_independent_new_field_sampling":True,
            "sites":output_sites,
            "source_transport_aggregate":cache.snapshot(),
            "new_observed_next_heading_effect":"NOT_ESTIMATED",
            "no_original_ids_coords_times_pairs_next_headings_or_raw_gauge_series_published":True,
            "not_a_causal_or_social_Boids_estimator":True}
        path=Path(output)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("V59_ORIGINAL_SOURCE_ONLY_COMPLETED",flush=True)
        return result
    finally:
        print("V59_SOURCE_TRANSPORT_RECEIPT "+
              json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--source-cache-dir",default=os.environ.get(
        "BOIDS_ORIGINAL_RWS_CACHE_DIR","/tmp/boids_original_rws_v59_cache"))
    parser.add_argument("--site",choices=("ameland","schiermonnikoog","both"),default="both")
    args=parser.parse_args()
    selected=("ameland","schiermonnikoog") if args.site=="both" else (args.site,)
    run(args.output,args.source_cache_dir,selected)
