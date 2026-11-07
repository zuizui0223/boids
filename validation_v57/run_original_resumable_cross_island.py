"""Run UNCHANGED v56 cross-island scientific code using resumable RWS delivery."""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
from unittest.mock import patch

from original_rws_cached_transport import OriginalRwsCache,observed_original_rws_year_cached

def run(output,cache_dir):
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    from run_cross_island_transfer import run as old_run
    def same_source(station,year):
        print(f"V57_ORIGINAL_RWS_SOURCE_REQUEST {station} {year}",flush=True)
        tide,meta=observed_original_rws_year_cached(cache,station,year)
        print(f"V57_ORIGINAL_RWS_SOURCE_ADMITTED {station} {year} "
              f"unique={meta['gauge_rows']} cache_entries={cache.snapshot()['cached_request_files']}",
              flush=True)
        return tide,meta
    try:
        with patch("source_fetch_resilience.observed_rws_year",new=same_source):
            result=old_run(output)
    finally:
        # This executes even on a source-transport failure. The workflow's
        # cache-save step runs if: always(), protecting earlier successful
        # authenticated source requests from being lost.
        print("V57_SOURCE_TRANSPORT_RECEIPT "+
              json.dumps(cache.snapshot(),sort_keys=True),flush=True)
    result["source_delivery_amendment"]={
        "analysis":"V57_SAME_SOURCE_RWS_TRANSPORT_RESUME",
        "source_cache":cache.snapshot(),
        "biological_estimator_unchanged":"validation_v56/run_cross_island_transfer.py",
        "original_RWS_provider":"ddapi20-waterwebservices.rijkswaterstaat.nl",
        "no_original_source_records_committed":True}
    Path(output).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("V57_ORIGINAL_CROSS_ISLAND_COMPLETED",flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get("BOIDS_ORIGINAL_RWS_CACHE_DIR",
                  "/tmp/boids_original_rws_v57_cache"))
    args=p.parse_args()
    run(args.output,args.source_cache_dir)
