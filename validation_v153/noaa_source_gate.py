"""v153 source-only admission for NOAA verified hourly water-level proxies (2018-23).

Purpose: test that independent *observed NOAA coastal reference-gauge* hourly
tide data exist for the exact frozen California fish-chorus recorder-hours,
BEFORE modeling any cochorus, tide interaction, or forecasting endpoints.

Original 60 XLS(X) and 9-site deployment/masks are verified by immutable v142
per-workbook SHA through v144.original(). Hour selection copied from v145.
NO FISH OUTCOMES READ OR SCORED after source parser admission: no social effect.

Gauge geography is v142 exact source Table 1 + NOAA station locations.
Nearest geo station is NOT calibrated tide/current at offshore hydrophones.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen,Request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v145"))
sys.path.insert(0,str(ROOT/"validation_v144"))
from v145_blockshift import original,eligible_complete_days,contiguous_runs
from full9_temporal import EPOCH,local_time

V145=ROOT/"validation_v145/results/source_blockshift_cochorus_null.json"
GEO=ROOT/"validation_v142/results/nine_sites_reference_gauge_geography.json"
OUT=ROOT/"validation_v153/results/noaa_verified_tide_source_admission_v153.json"

BASE="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
PARAMS={"product":"hourly_height","application":"Boids_Tidal_Acoustic_Source_Audit",
        "datum":"MLLW","time_zone":"gmt","units":"metric","format":"json"}
MIN_GAUGE_COVERAGE_FOR_NEXT_ANALYSIS=0.80
MIN_LOCAL_YEAR_GAUGE_MATCHED_HOURS=720
MIN_REPEATED_LOCAL_YEARS_FOR_NEXT_ANALYSIS=2
SOURCE_REQUEST_MAX_BYTES=3500000

def hourly_index(dt):
    if dt.tzinfo is None or dt.utcoffset()!=timedelta(0):
        raise ValueError("NOAA timestamps must be UTC")
    return int((dt-EPOCH).total_seconds()//3600)

def parse_noaa(raw,station_id,year):
    obj=json.loads(raw)
    if obj.get("error"):
        raise ValueError("NOAA API returned error "+str(obj["error"])[:250])
    metadata=obj.get("metadata",{})
    if str(metadata.get("id"))!=str(station_id):
        raise ValueError("NOAA station identity not authenticated")
    if not isinstance(obj.get("data"),list) or not obj["data"]:
        raise ValueError("NOAA returned no verified source rows")
    beginning=datetime(year,1,1,tzinfo=timezone.utc)
    ending=datetime(year+1,1,1,tzinfo=timezone.utc)
    gauge={}
    flags=defaultdict(int)
    for record in obj["data"]:
        try:
            timestamp=datetime.strptime(record["t"],"%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except (TypeError,ValueError,KeyError):
            flags["bad_original_timestamp"]+=1;continue
        if not (beginning<=timestamp<ending):
            raise ValueError("NOAA full-year original observed timestamp outside source year")
        if timestamp.minute!=0:
            raise ValueError("NOAA hourly source unexpectedly non-hourly timestamp")
        try:
            height=float(record["v"])
        except (TypeError,ValueError,KeyError):
            flags["missing_or_nonnumeric_height"]+=1;continue
        if not math.isfinite(height):
            flags["missing_or_nonfinite_height"]+=1;continue
        k=hourly_index(timestamp)
        if k in gauge:raise AssertionError("NOAA duplicate original verified UTC hour")
        gauge[k]=height
    if len(gauge)<24:
        raise ValueError("NOAA source lacks at least one verified daily tide cycle")
    possible=int((ending-beginning).total_seconds()//3600)
    return gauge,{
       "station_id":str(station_id),"year":year,"source_station_name":metadata.get("name"),
       "original_record_rows":len(obj["data"]),
       "verified_numeric_hours":len(gauge),
       "expected_calendar_UTC_hours":possible,
       "source_coverage_fraction":round(len(gauge)/possible,6),
       "source_min_height_m_MLLW":round(min(gauge.values()),4),
       "source_max_height_m_MLLW":round(max(gauge.values()),4),
       "source_missing_OR_bad_rows":dict(flags),
       "actual_provider_content_sha256":hashlib.sha256(raw).hexdigest(),
       "raw_NOAA_not_redistributed":True,
    }

def fetch_year(station,year):
    p=dict(PARAMS)
    p.update({"station":str(station),"begin_date":f"{year}0101","end_date":f"{year}1231"})
    url=BASE+"?"+urlencode(p)
    try:
        with urlopen(Request(url,headers={"User-Agent":"Boids-Research-SourceQuality/1.0"}),
                     timeout=75) as response:
            raw=response.read(SOURCE_REQUEST_MAX_BYTES+1)
        if len(raw)>SOURCE_REQUEST_MAX_BYTES:
            raise ValueError("Full-year verified-hourly NOAA response exceeds source cap")
        samples,quality=parse_noaa(raw,station,year)
        quality["request_URL"]=url
        quality["status"]="SOURCE_NOAA_VERIFIED"
        return (station,year),samples,quality
    except Exception as exc:
        return (station,year),{},{
            "station_id":str(station),"year":year,"status":"STOP_NOAA_ORIGINAL_SOURCE_UNAVAILABLE",
            "source_failure_type":type(exc).__name__,
            "source_failure_note":str(exc)[:200],
            "request_URL":url,
        }

def plan_frozen_source_hours():
    old=json.loads(V145.read_text())
    geometry=json.loads(GEO.read_text())
    if old["sites"]!=9 or old["original_deployments"]!=60 or not old["source_original_workbook_SHA_verified_all_60"]:
        raise AssertionError("Original source provenance changed")
    if geometry["n_source_acoustic_sites"]!=9 or geometry["n_gauge_reference_sites"]!=4:
        raise AssertionError("Previously authenticated source geography changed")
    nearest={z["acoustic_site"]:z for z in geometry["site_rows"]}
    site_source=original()
    if set(site_source)!=set(nearest):raise AssertionError("Site names not same as prior published original")
    sites={}
    required_station_years=set()
    for name,record in sorted(site_source.items()):
        effort=record["nominal"]-record["off"]-record["noise"]
        day=eligible_complete_days(effort)
        runs=contiguous_runs(day)
        hours={h for run in runs for d in run for h in day[d]}
        oldsite=next(s for s in old["source_site_block_qc"] if s["site"]==name)
        if len(hours)!=oldsite["selected_source_eligible_hours"] or len(runs)!=oldsite["continuous_local_yearmonth_run_blocks_7days_plus"]:
            raise AssertionError("v145 original complete-day source opportunity changed "+name)
        station=str(nearest[name]["nearest_NOAA_station_id"])
        years=sorted({(EPOCH+timedelta(hours=h)).year for h in hours})
        for y in years:required_station_years.add((station,y))
        sites[name]={
            "site":name,
            "published_sanctuary":nearest[name]["sanctuary"],
            "reference_gauge_name":nearest[name]["nearest_NOAA_physical_gauge"],
            "reference_station_id":station,
            "geodesic_station_distance_km":nearest[name]["nearest_direct_geodesic_km"],
            "offshore_hydrophone_true_tide_or_current":"NOT_OBSERVED_OR_CALIBRATED",
            "source_recording_hours":len(hours),
            "source_yearmonth_7dplus_runs":len(runs),
            "site_source_hours":hours,
            "gauge_reference_required_UTC_years":years,
        }
    if sum(z["source_recording_hours"] for z in sites.values())!=136032:
        raise AssertionError("Source retained hour count is no longer v145 original 136032")
    return sites, sorted(required_station_years)

def build():
    sites,request_keys=plan_frozen_source_hours()
    gauge={};quality={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for (station,year),records,qc in pool.map(lambda x:fetch_year(*x),request_keys):
            gauge[(station,year)]=records
            quality[(station,year)]=qc
    site_result=[]
    for site,item in sites.items():
        by_local_year=defaultdict(lambda:{"source_hours":0,"matched_gauge_hour":0,
                                         "matched_gauge_with_both_neighbors":0})
        station=item["reference_station_id"]
        matched=0;both=0
        for hour in item["site_source_hours"]:
            y=(EPOCH+timedelta(hours=hour)).year
            annual=gauge.get((station,y),{})
            cur=hour in annual
            adjacent=cur and ((hour-1 in annual) or
                               (hour-1 in gauge.get((station,y-1),{}))) and (
                                   (hour+1 in annual) or
                                   (hour+1 in gauge.get((station,y+1),{})))
            local_year=local_time(hour).year
            v=by_local_year[local_year]
            v["source_hours"]+=1
            if cur:
                matched+=1;v["matched_gauge_hour"]+=1
            if adjacent:
                both+=1;v["matched_gauge_with_both_neighbors"]+=1
        yearly=[{"local_year":year,**z,
                 "gauge_match_fraction":round(z["matched_gauge_hour"]/z["source_hours"],6)}
                for year,z in sorted(by_local_year.items())]
        full_match=round(matched/item["source_recording_hours"],6)
        admitted_years=sum(z["matched_gauge_hour"]>=MIN_LOCAL_YEAR_GAUGE_MATCHED_HOURS for z in yearly)
        site_result.append({
            "site":site,"published_sanctuary":item["published_sanctuary"],
            "geodesic_reference_station_km":item["geodesic_station_distance_km"],
            "reference_station":station,"reference_name":item["reference_gauge_name"],
            "required_gauge_UTC_years":item["gauge_reference_required_UTC_years"],
            "source_recording_hours":item["source_recording_hours"],
            "source_matched_real_NOAA_gauge_hours":matched,
            "source_matched_with_both_real_adjacent_gauge_hours":both,
            "matched_fraction":full_match,
            "matched_local_years_above_min_n":admitted_years,
            "source_year_quality":yearly,
            "source_only_qualified_for_further_exploratory_model":full_match>=MIN_GAUGE_COVERAGE_FOR_NEXT_ANALYSIS
                and admitted_years>=MIN_REPEATED_LOCAL_YEARS_FOR_NEXT_ANALYSIS,
            "surrogate_water_height_not_in_situ_hydrophone_level":True,
            "true_local_tidal_current":"NOT_OBSERVED",
            "fish_detection_residual_or_tidal_biological_effect":"NOT_EVALUATED",
        })
    source_qual=[quality[k] for k in sorted(quality)]
    return {
        "version":"v153_original_noaa_verified_coastal_hourly_height_source_admission_1",
        "source_acoustic_DOI":"10.5061/dryad.q2bvq83sw",
        "original_all_60_acoustic_XLS_SHA256_matched":True,
        "NOAA_product":"verified hourly_height, datum MLLW, GMT, metric",
        "NOAA_reference_source_years_requested":source_qual,
        "source_earliest_year_min":min(k[1] for k in request_keys),
        "source_latest_year_max":max(k[1] for k in request_keys),
        "source_gauge_year_requests":len(request_keys),
        "source_gauge_years_verified":sum(x["status"]=="SOURCE_NOAA_VERIFIED" for x in source_qual),
        "source_sites":site_result,
        "source_n_hydrophone_sites":len(site_result),
        "source_original_hydrophone_recording_hours":sum(x["source_recording_hours"] for x in site_result),
        "source_gauge_hour_matched_recorder_hours":sum(x["source_matched_real_NOAA_gauge_hours"] for x in site_result),
        "source_gauge_hour_matched_with_neighbors":sum(x["source_matched_with_both_real_adjacent_gauge_hours"] for x in site_result),
        "site_source_qualified_count":sum(x["source_only_qualified_for_further_exploratory_model"] for x in site_result),
        "source_qualification_rule":{"min_total_hour_fraction":MIN_GAUGE_COVERAGE_FOR_NEXT_ANALYSIS,
                                    "min_local_year_h":MIN_LOCAL_YEAR_GAUGE_MATCHED_HOURS,
                                    "min_local_years":MIN_REPEATED_LOCAL_YEARS_FOR_NEXT_ANALYSIS},
        "within-site_hourly_fish_presence_versus_environment":"NOT_FITTED",
        "physical_offshore_tide_source":"UNAVAILABLE",
        "direct_fish_social_boids_effect":"NOT_IDENTIFIED",
        "global_tide_x_solar_meta_effect":"NOT_ESTIMATED",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    x=p.parse_args()
    result=build()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if x.check:
        if not OUT.is_file():raise AssertionError("Frozen v153 source receipt not yet present")
        saved=json.loads(OUT.read_text())
        if saved!=result:raise AssertionError("NOAA verified source content/coverage changed")
        print("V153_ORIGINAL_COASTAL_GAUGE_SOURCE_REPLAY_PASS")
    else:OUT.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V153_SOURCE_RESULT_START")
    print(json.dumps(result,sort_keys=True,ensure_ascii=True,separators=(",",":")))
    print("V153_SOURCE_RESULT_END")

if __name__=="__main__":main()
