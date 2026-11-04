"""v43 post-v41 exploratory field backtest, identical v41 heading source/model.

Original 2010 fit → original 2011 directional holdout; same wild population
that was already used in previous v41 2012 forecast training, NOT a new
independent field cohort. No Boids social force or resource-front inference.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np

from source_preflight import download_and_pin
from ameland_external_site import original_gps
from source_fetch_resilience import observed_rws_year
from original_heading_tide import (
    CLOCKS, SITES, original_three_fix_heading_episodes,
    forecast, directional_half_mse)
from tide_phase_yearago_placebo import percentile_interval

TRAIN_YEAR=2010
TEST_YEAR=2011
SOURCE_QA_MIN=1000
TEST_MIN_BIRDS=3
TEST_MIN_WEEKS=4

def score(train,test,seed=20261105,bird_draws=10000,week_draws=4000):
    if any(r["t"].year!=TRAIN_YEAR for r in train):
        raise ValueError("Training GPS episode year does not match frozen source")
    if any(r["t"].year!=TEST_YEAR for r in test):
        raise ValueError("Test GPS episode year is not fully withheld 2011")
    bybird=defaultdict(list);byweek=defaultdict(list)
    for k,r in enumerate(test):
        bybird[r["id"]].append(k)
        byweek[r["t"].isocalendar()[:2]].append(k)
    if (len(train)<SOURCE_QA_MIN or len(test)<SOURCE_QA_MIN or
        len(bybird)<TEST_MIN_BIRDS or len(byweek)<TEST_MIN_WEEKS):
        return {"status":"NOT_ADMITTED_INSUFFICIENT_ORIGINAL_2011_DIRECTION_SOURCE",
                "n_train":len(train),"n_test":len(test),
                "birds":len(bybird),"weeks":len(byweek)}
    target=np.array([[r["target_e"],r["target_n"]] for r in test],dtype=float)
    err0=directional_half_mse(target,forecast(train,test,0))
    err1=directional_half_mse(target,forecast(train,test,1))
    d=err0-err1
    bdelta=[float(np.mean(d[v])) for v in bybird.values()]
    wdelta=[]
    for idx in byweek.values():
        local=defaultdict(list)
        for i in idx:local[test[i]["id"]].append(i)
        wdelta.append(float(np.mean([np.mean(d[v]) for v in local.values()])))
    m0=float(np.mean([np.mean(err0[idx]) for idx in bybird.values()]))
    m1=float(np.mean([np.mean(err1[idx]) for idx in bybird.values()]))
    return {"status":"2011_REAL_DIRECTIONAL_BACKTEST_POST_V41_EXPLORATORY",
            "n_train":len(train),"n_test":len(test),
            "n_heldout_source_birds":len(bybird),"n_heldout_ISO_weeks":len(byweek),
            "M0_equal_bird_half_MSE":m0,
            "M1_equal_bird_half_MSE":m1,
            "tidal_phase_gain_pooled_equal_bird_half_MSE":m0-m1,
            "phase_gain_pct_of_M0":100*(m0-m1)/m0 if m0>0 else None,
            "n_positive_birds":sum(x>0 for x in bdelta),
            "pooled_bird_bootstrap95":percentile_interval(bdelta,bird_draws,seed),
            "separate_equal_week_bird_gain":float(np.mean(wdelta)),
            "n_positive_weeks":sum(x>0 for x in wdelta),
            "separate_week_bootstrap95":percentile_interval(wdelta,week_draws,seed+100),
            "v41_frozen_heading_model_imported_unchanged":True,
            "no_social_front_or_prey_causation":True}

def run(site,outfile):
    if site not in SITES:raise ValueError("Site outside frozen original field sources")
    station={"schiermonnikoog":"schiermonnikoog.waddenzee",
             "ameland":"ameland.nes"}[site]
    source_receipts={}
    data={clock:{} for clock in CLOCKS}
    with tempfile.TemporaryDirectory(prefix="v43_original_gps_") as folder:
        for year in (TRAIN_YEAR,TEST_YEAR):
            path=Path(folder)/f"{site}_{year}_original.csv.gz"
            manifest=(download_and_pin(year,path) if site=="schiermonnikoog"
                      else original_gps(year,path))
            tide,gauge=observed_rws_year(station,year)
            if gauge["gauge_rows"]<50000:
                raise ValueError("Source STOP: original measured annual tide incomplete")
            source_receipts[str(year)]={"original_MD5_verified":manifest.get("provider_md5_match",manifest.get("provider_original_md5_matched")),
                                        "original_gps_SHA256":manifest["original_sha256"],
                                        "measured_original_RWS_NAP_count":gauge["gauge_rows"],
                                        "RWS_station":station}
            for clock in CLOCKS:
                rows,audit=original_three_fix_heading_episodes(path,tide,site,clock)
                data[clock][year]=rows
                source_receipts[str(year)][f"source_clock_{clock}s"]=audit
            path.unlink(missing_ok=True)
    results={}
    for clock in CLOCKS:
        results[f"native_clock_shift_{clock}s"]=score(data[clock][TRAIN_YEAR],
                                                       data[clock][TEST_YEAR])
    report={"analysis":"V43_POST_V41_2010_TRAIN_2011_HEADING_HOLDOUT",
            "site":site,"original_source_type":"GPS_MD5_VERIFIED_AND_RWS_WATHTE_METING_NAP",
            "frozen_train_year":TRAIN_YEAR,"frozen_test_year":TEST_YEAR,
            "source_receipts":source_receipts,"scenarios":results,
            "interpretation":"Retrospective same-source backtest after v41 2012 results, not an independent population or external confirmation",
            "source_clock_caveat":"Native GPS UTC vs GPS time unresolved"}
    Path(outfile).parent.mkdir(parents=True,exist_ok=True)
    Path(outfile).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=SITES,required=True)
    p.add_argument("--output",required=True)
    arg=p.parse_args()
    print(json.dumps(run(arg.site,arg.output),sort_keys=True))
