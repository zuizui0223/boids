#!/usr/bin/env python3
"""v23 independent ERA5 daily weather source metadata only; no duck responses.

Weather historical reanalysis assimilates observations, not in-situ field
measurements or prey/resource availability. Two original source-independent
Bangladesh wetland reference cells fixed before duck GPS location inspection.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API="https://archive-api.open-meteo.com/v1/archive"
REGION_POINTS={
  "baikka_beel":(24.3503,91.6995),
  "tanguar_haor":(25.1500,91.0667),
}
START="2019-01-01"
END="2023-12-31"
MODEL="era5"
VARIABLES=("temperature_2m_mean","precipitation_sum","wind_speed_10m_max")
N_DAYS=(dt.date.fromisoformat(END)-dt.date.fromisoformat(START)).days+1
MAX_RESPONSE_BYTES=2_000_000
MAX_MISSING_PERCENT=5.0
SOURCE_LABEL="OPEN_METEO_HISTORICAL_ERA5_NOT_IN_SITU"

def request_url(lat:float,lon:float)->str:
    params=[
      ("latitude",str(lat)),("longitude",str(lon)),
      ("start_date",START),("end_date",END),
      ("daily",",".join(VARIABLES)),("timezone","UTC"),
      ("models",MODEL)
    ]
    return API+"?"+urllib.parse.urlencode(params)

def validate_weather_json(data:dict,raw:bytes,name:str,url:str)->dict:
    if name not in REGION_POINTS:raise ValueError("Unknown registered wetland source")
    if data.get("error"):raise ValueError("Weather provider source error")
    if data.get("utc_offset_seconds")!=0:
        raise ValueError("Weather source is not aligned to UTC")
    weather=data.get("daily") or {}
    units=data.get("daily_units") or {}
    days=weather.get("time")
    if not isinstance(days,list) or len(days)!=N_DAYS:
        raise ValueError("Original weather days do not cover fixed interval")
    if days[0]!=START or days[-1]!=END:
        raise ValueError("Source original daily boundary mismatch")
    if any(days[k]!=str(dt.date.fromisoformat(START)+dt.timedelta(days=k))
           for k in range(len(days))):
        raise ValueError("Missing or reordered UTC daily dates")
    missing={}
    for variable in VARIABLES:
        v=weather.get(variable)
        if not isinstance(v,list) or len(v)!=N_DAYS:
            raise ValueError("Incomplete original weather data variable "+variable)
        bad=0
        for value in v:
            if value is None or not isinstance(value,(int,float)) or not math.isfinite(value):
                bad+=1
        missing[variable]=bad
        if 100*bad/len(v)>MAX_MISSING_PERCENT:
            raise ValueError("Original climate source exceeds fixed missingness gate")
    if units.get("temperature_2m_mean")!="°C":
        raise ValueError("Unrecognized original temperature unit")
    if units.get("precipitation_sum")!="mm":
        raise ValueError("Unrecognized original daily rainfall unit")
    if units.get("wind_speed_10m_max") not in ("km/h","kmh"):
        raise ValueError("Unrecognized original wind speed unit")
    return {
      "status":"ERA5_ORIGINAL_SOURCE_ONLY_VERIFIED",
      "name":name,"source_url":url,
      "source_response_bytes":len(raw),
      "original_response_sha256":hashlib.sha256(raw).hexdigest(),
      "requested_location":list(REGION_POINTS[name]),
      "provider_returned_grid_point":[data.get("latitude"),data.get("longitude")],
      "provider_timezone":data.get("timezone"),
      "provider_utc_offset_seconds":data.get("utc_offset_seconds"),
      "provider_model_requested":MODEL,
      "days":len(days),
      "start_date":days[0],"end_date":days[-1],
      "original_units":{v:units[v] for v in VARIABLES},
      "missingness_counts":missing,
      "source_is_reanalysis_not_direct_resource_measurement":True,
      "numeric_daily_weather_values_exported":False,
      "animal_GPS_or_movement_outcomes_processed":False,
    }

def obtain(name:str)->dict:
    lat,lon=REGION_POINTS[name]
    url=request_url(lat,lon)
    req=urllib.request.Request(url,headers={
        "User-Agent":"boids-v23-wetland-ERA5-original-context/1.0",
        "Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=80) as resp:
        raw=resp.read(MAX_RESPONSE_BYTES+1)
    if len(raw)>MAX_RESPONSE_BYTES:
        raise ValueError("ERA5 JSON is beyond fixed cap")
    obj=json.loads(raw)
    if not isinstance(obj,dict):raise ValueError("ERA5 response not a JSON object")
    return validate_weather_json(obj,raw,name,url)

def run()->dict:
    ret={"study":"v23-independent-ERA5-original-2019-2023-Bangladesh-wetlands",
         "source":SOURCE_LABEL,
         "status":"ERA5_SOURCE_ONLY_GATE_NOT_ADMITTED",
         "weather_grids":{},
         "errors":[],
         "raw_daily_weather_values_distributed":False,
         "any_wild_duck_position_or_behavior_analyzed":False}
    for name in REGION_POINTS:
        try:ret["weather_grids"][name]=obtain(name)
        except Exception as exc:ret["errors"].append({
            "wetland":name,
            "exception":type(exc).__name__,
            "message":str(exc)[:180]})
    if len(ret["weather_grids"])==len(REGION_POINTS):
        ret["status"]="ERA5_TWO_WETLANDS_SOURCE_VALIDATED_NO_BEHAVIOR"
    return ret

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v23/results/original_era5_bangladesh_weather_v23.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V23_ERA5_ORIGINAL_SOURCE",json.dumps(result,sort_keys=True))
    print("V23_NO_DUCK_CLIMATE_GPS_ASSOCIATION_FITTED")

if __name__=="__main__":
    main()
