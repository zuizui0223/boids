"""v32: 2010 and 2011 same-site independent-year holdout with UNCHANGED v31 model.

Each original data year is source-pinned and evaluated separately. No raw GPS
or tagged-animal identifiers persist. No 2010/2011 result-based tuning allowed.
"""
from __future__ import annotations
import argparse, json, tempfile
from datetime import datetime
from pathlib import Path
from source_preflight import download_and_pin
from tidal_observed_2009 import (ONE_HOUR, get_gauge, read_gps, make_steps,
                                  split_rows, score)

def one_year(year):
    if year not in (2010,2011):
        raise ValueError("Only pre-frozen independent-year validation 2010/2011")
    with tempfile.TemporaryDirectory(prefix="v32_gps_") as temp:
        path=Path(temp)/("original_%s.csv.gz"%year)
        manifest=download_and_pin(year,path)
        fixes,gps_quality=read_gps(path)
        path.unlink(missing_ok=True)
    first=datetime(year-1,12,30,tzinfo=ONE_HOUR)
    last=datetime(year+1,1,2,tzinfo=ONE_HOUR)
    tide,gauge_quality=get_gauge(start=first,end=last)
    result={"year":year,"source":"ORIGINAL_ZENODO_AND_RWS_MEASURED",
            "original_manifest":manifest,
            "original_gps_summary":gps_quality,
            "original_gauge_summary":gauge_quality,
            "effect_status":"EXPLORATORY_RETROSPECTIVE_CLOCK_UNVERIFIED",
            "source_gps_clock_unverified":True,
            "local_gauge_lag_and_DEM_unverified":True,
            "social_motor_force_not_estimated":True,"models":{}}
    # The four time scenarios, feature sets, endpoint and held-out week
    # definition are imported from frozen v31 without any model adjustments.
    for key,shift in [("source_clock_as_UTC",0),
                      ("GPS_clock_minus_15seconds",-15),
                      ("GPS_clock_minus_1hour",-3600),
                      ("GPS_clock_plus_1hour",3600)]:
        steps,audit=make_steps(fixes,tide,clock_offset_seconds=shift)
        train,test,split=split_rows(steps)
        scored=score(train,test,split)
        result["models"][key]={"clock_offset_seconds":shift,
                               "step_audit":audit,"result":scored}
    return result

def run(output):
    out={"analysis":"v32_FROZEN_INDEPENDENT_YEAR_TEMPORAL_REPLICATION",
         "baseline_year":"2009_completed_before_2010_2011_test",
         "source":"original_zenodo_2010_2011_RWS_NAP",
         "reproduction":"same_species_same_site_not_population_replication",
         "years":[one_year(2010),one_year(2011)]}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=run(a.output)
    # Only aggregate sources/metrics, no source locations or animal identifiers.
    print(json.dumps(result,sort_keys=True))
