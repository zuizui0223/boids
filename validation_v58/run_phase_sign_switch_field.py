"""Run frozen v58 phase-sign switch on authenticated original 2010->2011 GPS.

Physical original WATHTE measured NAP transport from v57 is unchanged.
Full original old v57 cross-site model scores replay BEFORE new phase swap.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
from unittest.mock import patch

from original_rws_cached_transport import OriginalRwsCache,observed_original_rws_year_cached
from run_cross_island_transfer import load_site,transfer_pairs
from cross_island_transfer import (
    evaluate_transfer,prepare_transfer,bird_equal_center,translate_rows)
from original_heading_tide import forecast
from phase_sign_switch import analyse_switch

EXPECTED_V57_TRANSLATED={
    "schiermonnikoog_to_ameland":{
        "source_train":7911,"target_test":4678,"target_birds":5,
        "angles":{"M0":72.93178509824226,
                  "M365":71.35487793871758,
                  "Mactual":65.7262909831397}},
    "ameland_to_schiermonnikoog":{
        "source_train":3753,"target_test":4948,"target_birds":13,
        "angles":{"M0":72.50932117199987,
                  "M365":70.19593767636698,
                  "Mactual":66.03068642794109}}}

def check_prior_cross_site_replay(name,prior):
    if name not in EXPECTED_V57_TRANSLATED:
        raise ValueError("Unfrozen transfer route")
    if prior.get("status")!="OBSERVED_CROSS_ISLAND_YEAR_TRANSFER":
        raise ValueError("SOURCE_STOP_PREVIOUS_TRANSFER_NO_LONGER_ADMITTED")
    ref=EXPECTED_V57_TRANSLATED[name]
    if (prior["source_gate"]["training_rows"]!=ref["source_train"] or
        prior["source_gate"]["test_rows"]!=ref["target_test"] or
        prior["source_gate"]["test_birds"]!=ref["target_birds"]):
        raise ValueError("SOURCE_STOP_V57_CROSS_SITE_SOURCE_COUNTS_DRIFT")
    original=prior["conditions"]["translated"]
    if original.get("status")!="OBSERVED_CROSS_ISLAND_ANGULAR_TRANSFER":
        raise ValueError("SOURCE_STOP_V57_TRANSLATED_MODEL_NOT_ADMITTED")
    vals=original["metrics"]["equal_bird"]["model_mean_losses"]
    for model,target in ref["angles"].items():
        if abs(float(vals[model]["absolute_angle_degrees"])-target)>1e-9:
            raise ValueError("SOURCE_STOP_V57_PREVIOUS_TRANSFER_ANGLE_CHANGED")
    return {"source_train_rows":ref["source_train"],
            "original_test_rows":ref["target_test"],
            "test_birds":ref["target_birds"],
            "prior_v57_translated_angles_exactly_replayed":True,
            "prior_v57_translated_angles_degrees":ref["angles"]}

def run(output,cache_dir):
    cache=OriginalRwsCache(cache_dir,sleeper=time.sleep)
    def same_original_source(station,year):
        tide,meta=observed_original_rws_year_cached(cache,station,year)
        if meta["gauge_rows"]!=52561:
            raise ValueError("SOURCE_STOP_ORIGINAL_RWS_NAP_YEAR_COUNT_CHANGED")
        print(f"V58_ORIGINAL_SOURCE_ADMITTED station={station} year={year} n={meta['gauge_rows']}",flush=True)
        return tide,meta
    result=None
    try:
        # Existing v56 site source loader, model and original QA are untouched.
        with patch("source_fetch_resilience.observed_rws_year",new=same_original_source):
            dataset={};source_audits={}
            for site in ("schiermonnikoog","ameland"):
                dataset[site],source_audits[site]=load_site(site)
                print("V58_OLD_LOCAL_SOURCE_MODEL_REPLAY_OK "+site,flush=True)
        results={}
        for source,target in transfer_pairs():
            name=source+"_to_"+target
            old=evaluate_transfer(dataset[source][2010],
                                  dataset[target][2010],
                                  dataset[target][2011],forecast)
            prior=check_prior_cross_site_replay(name,old)
            train,gate=prepare_transfer(dataset[source][2010],
                                        dataset[target][2010],
                                        dataset[target][2011])
            if not gate["admitted"]:
                raise ValueError("SOURCE_STOP_PREDECLARED_CROSS_SITE_GATE")
            src_center=bird_equal_center(train)
            target_center=bird_equal_center(dataset[target][2010])
            # Unchanged geographic calibration from v56/v57.
            heldout=translate_rows(dataset[target][2011],src_center,target_center)
            new=analyse_switch(train,heldout,forecast)
            if new.get("admission")!="MODEL_FIXED_PHASE_SWAP_ON_ORIGINAL_HELDOUT_GPS":
                raise ValueError("SOURCE_STOP_NEW_PHASE_SWITCH_SAMPLE_NOT_ADMITTED")
            if new["test_original_rows"]!=prior["original_test_rows"]:
                raise ValueError("SOURCE_STOP_PHASE_SWAP_MUTATED_GPS_COHORT")
            results[name]={"source":source,"test_site":target,
                           "training_year":2010,"test_year":2011,
                           "original_v57_replay":prior,
                           "source_train_test_gate":gate,
                           "phase_switch":new}
            main=new["main"]["metrics"]
            summary={
                "route":name,
                "test_original_rows":new["test_original_rows"],
                "test_birds":new["test_birds"],
                "actual_minus_flip_cosine":main["actual_minus_flipped_cosine_loss_gain"],
                "actual_minus_flip_angle_deg":main["actual_minus_flipped_angle_error_gain_degrees"],
                "model_only_abs_rotation_deg":main["model_phase_switch_absolute_angle_degrees"],
                "model_only_signed_rotation":main["model_implied_signed_switch"],
                "phase_groups":new["original_phase_subgroups"],
                "water_height_quartiles":new["source_height_quartile_subgroups"]}
            print("V58_ORIGINAL_PHASE_SWITCH_RESULT "+json.dumps(summary,sort_keys=True),flush=True)
        result={
            "analysis":"V58_SAME_STATE_RISING_VS_FALLING_MODEL_HEADING_GEOMETRY",
            "source_run_commit":os.environ.get("GITHUB_SHA","local"),
            "parent_observed_v57":"42319830514",
            "source_sites_original_provider_replay":{
                site:{"2010_gps_sha256":v["original_receipts"]["2010"]["original_GPS_SHA256"],
                      "2011_gps_sha256":v["original_receipts"]["2011"]["original_GPS_SHA256"],
                      "2009_2010_2011_original_measured_rws_nap_counts":[
                         v["original_receipts"][str(y)]["RWS_original_NAP_count"]
                         for y in (2009,2010,2011)],
                      "prior_original_local_model_replay":True}
                for site,v in source_audits.items()},
            "source_cache":cache.snapshot(),
            "primary":"schiermonnikoog_to_ameland",
            "all_phase_switch_source_results":results,
            "scientific_limit":"Model-implied conditional rotation, not observed biological phase intervention or actual prey-front/social Boids force. Historic data previously studied; post-v57 exploratory."}
        Path(output).parent.mkdir(parents=True,exist_ok=True)
        Path(output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("V58_ORIGINAL_SOURCE_AND_PHASE_SWITCH_COMPLETED",flush=True)
        return result
    finally:
        print("V58_SOURCE_CACHE_RECEIPT "+json.dumps(cache.snapshot(),sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--source-cache-dir",default=os.environ.get("BOIDS_ORIGINAL_RWS_CACHE_DIR",
                      "/tmp/boids_original_rws_v58_cache"))
    args=p.parse_args()
    run(args.output,args.source_cache_dir)
