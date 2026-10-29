#!/usr/bin/env python3
"""v23-C independently source-verified individual duck GPS x prior-day ERA5.

Predictions are strictly prequential: previous individual movement and
other-bird source results only from days < target UTC date; predictor weather
only day t-1 at the fixed site nearest LAST t-1 GPS fix. Current target
locations/weather are NEVER predictors. 14-day max own history, w=n/(n+2).
No true habitat/resource niche, social force or causal meteorology inferred.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import math
import tempfile
import urllib.request
from pathlib import Path

import numpy as np
import source_gate as ducks
import weather_source_gate as weather

PINNED_GPS_SHA256="001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e"
PINNED_CANONICAL_ERA5={
    "baikka_beel":"b6c1fc7323cb6cb7275e9f5d31ea8ad1f9f4bea4b479eb93e9a13058057d9b54",
    "tanguar_haor":"c856bc0b884b5d13c1529003fc2a1d1d335c856559ae4d4ae7c097837eb54307",
}
BANGLADESH_STUDY="Dabbling duck migration Bangladesh 2019-2022"
MIN_DAY_FIXES=6
MIN_DAY_HOURS=8.
MAX_HDOP=15.
MAX_CLIMATE_SITE_DISTANCE_KM=120.
MIN_OWN_HIST_DAYS=3
MAX_OWN_HIST_DAYS=14
MIN_EXTERNAL_BIRDS=5
MIN_EXTERNAL_BIRD_DAYS=20
MIN_SOURCE_BIRDS=20
MIN_FUTURE_TARGET_DAYS=200
MIN_NONSURROGATE_WEATHER_FRACTION=.20
RAIN_PREV_DAY_MM=1.
WARM_PREV_DAY_C=25.
SHRINK_KAPPA=2.
BOOT_SEED=20261029
BOOT_REPS=10000
KM_PER_DEGREE=111.2
EARTH_KM=6371.0088

def great_circle(lat1:float,lon1:float,lat2:float,lon2:float)->float:
    a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return EARTH_KM*2*math.asin(min(1.,math.sqrt(a)))

def select_weather_point(prior_last_lat:float,prior_last_lon:float)->tuple[str,float]|None:
    ranked=sorted([
        (great_circle(prior_last_lat,prior_last_lon,*coords),name)
        for name,coords in weather.REGION_POINTS.items()
    ])
    if ranked[0][0]>MAX_CLIMATE_SITE_DISTANCE_KM:return None
    return ranked[0][1],ranked[0][0]

def parse_original_gps(path:Path)->tuple[dict,dict]:
    """Original GPS values only after v23-C pre-outcome registration."""
    # Exclude every duplicate timestamp within source study, not first/last.
    raw_fixes=collections.defaultdict(list)
    seen=collections.Counter()
    rows=bangladesh_rows=invalid=0
    species={}
    with path.open("r",newline="",encoding="utf-8-sig") as src:
        reader=csv.DictReader(src)
        if not set(ducks.SOURCE_COLS).issubset(reader.fieldnames or ()):
            raise ValueError("Previously inspected source header changed")
        for row in reader:
            rows+=1
            if row.get("study.name")!=BANGLADESH_STUDY:
                continue
            bangladesh_rows+=1
            study_id=row.get("study.id")
            individual_id=row.get("individual.id")
            taxon=row.get("individual.taxon.canonical.name")
            try:
                t=ducks.parse_utc(row["timestamp"])
                lat=float(row["location.lat"])
                lon=float(row["location.long"])
                hdop=float(row["gps.hdop"])
                if not (all(map(math.isfinite,(lat,lon,hdop))) and
                        -90<=lat<=90 and -180<=lon<=180 and
                        0<=hdop<=MAX_HDOP):
                    raise ValueError("Invalid WGS84 or GPS horizontal dilution")
                if not study_id or not individual_id or not taxon:
                    raise ValueError("Missing source individual ID or taxon")
            except (TypeError,ValueError,KeyError):
                invalid+=1
                continue
            bird=(str(study_id).strip(),str(individual_id).strip())
            if bird in species and species[bird]!=taxon:
                raise ValueError("Original source bird changes taxonomic identity")
            species[bird]=taxon
            stamp=(bird,t)
            seen[stamp]+=1
            raw_fixes[(bird,t.date())].append((t,lat,lon))
    unique_day_fixes=collections.defaultdict(list)
    duplicate_rows=0
    for (bird,day),fixes in raw_fixes.items():
        for record in fixes:
            if seen[(bird,record[0])]!=1:
                duplicate_rows+=1
                continue
            unique_day_fixes[(bird,day)].append(record)
    daily={}
    source_good_days=0
    for key,fixes in unique_day_fixes.items():
        ordered=sorted(fixes,key=lambda x:x[0])
        if len(ordered)<MIN_DAY_FIXES:continue
        span=(ordered[-1][0]-ordered[0][0]).total_seconds()/3600.
        if span<MIN_DAY_HOURS:continue
        lat_mean=float(np.mean([p[1] for p in ordered]))
        lon_mean=float(np.mean([p[2] for p in ordered]))
        kx=KM_PER_DEGREE*math.cos(math.radians(lat_mean))
        x=np.array([(q[2]-lon_mean)*kx for q in ordered])
        y=np.array([(q[1]-lat_mean)*KM_PER_DEGREE for q in ordered])
        radius=float(np.sqrt(np.mean(x*x+y*y)))
        if not math.isfinite(radius):
            continue
        bird,day=key
        daily[key]={
            "radius_log1p_km":math.log1p(radius),
            "last_prior_location":(ordered[-1][1],ordered[-1][2]),
            "source_taxon":species[bird],
            "GPS_fix_count":len(ordered),
            "GPS_coverage_hours":span}
        source_good_days+=1
    return daily,{
       "original_source_row_count":rows,
       "original_Bangladesh_study_GPS_rows":bangladesh_rows,
       "quality_invalid_Bangladesh_GPS_rows":invalid,
       "original_duplicate_GPS_rows_discarded_entirely":duplicate_rows,
       "original_Bangladesh_birds_with_any_valid_GPS":len(species),
       "original_Bangladesh_birds_with_at_least_one_qualifying_day":
           len({b for b,_ in daily}),
       "original_Bangladesh_qualifying_UTC_days":source_good_days,
       "source_GPS_interpolation_used":False}

def load_exact_era5()->tuple[dict,dict]:
    sources={}
    qc={}
    for name in weather.REGION_POINTS:
        lat,lon=weather.REGION_POINTS[name]
        url=weather.request_url(lat,lon)
        req=urllib.request.Request(url,headers={
            "User-Agent":"boids-v23-frozen-bangladesh-ERA5-daily/1.0",
            "Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=90) as response:
            raw=response.read(weather.MAX_RESPONSE_BYTES+1)
        if len(raw)>weather.MAX_RESPONSE_BYTES:
            raise ValueError("ERA5 weather source original exceeds cap")
        data=json.loads(raw)
        result=weather.validate_weather_json(data,raw,name,url)
        if result["canonical_original_source_data_sha256"]!=PINNED_CANONICAL_ERA5[name]:
            raise ValueError("Independent previously frozen ERA5 daily source values drifted")
        vals=data["daily"]
        sources[name]={dt.date.fromisoformat(date):(
              float(vals["temperature_2m_mean"][i]),
              float(vals["precipitation_sum"][i]),
              float(vals["wind_speed_10m_max"][i]))
              for i,date in enumerate(vals["time"])}
        qc[name]={"status":"INDEPENDENT_ERA5_CANONICAL_SOURCE_MATCH",
                  "data_sha256":result["canonical_original_source_data_sha256"],
                  "original_UTC_days":result["days"],
                  "missing":result["missingness_counts"],
                  "source_grid":result["provider_returned_grid_point"]}
    return sources,qc

def eligible_daily_events(days:dict,ERA:dict)->tuple[list[dict],dict]:
    candidates=[]
    missing_prior=too_far=outside_dates=0
    for (bird,day),today in sorted(days.items(),key=lambda item:(item[0][1],item[0][0])):
        prior=days.get((bird,day-dt.timedelta(days=1)))
        if prior is None:
            missing_prior+=1
            continue
        site=select_weather_point(*prior["last_prior_location"])
        if site is None:
            too_far+=1
            continue
        station,km=site
        prev_weather=ERA[station].get(day-dt.timedelta(days=1))
        if prev_weather is None:
            outside_dates+=1
            continue
        temp,rain,wind=prev_weather
        category=(int(rain>RAIN_PREV_DAY_MM),int(temp>=WARM_PREV_DAY_C))
        candidates.append({
            "bird":bird,"date":day,"site":station,
            "weather_class":category,
            "taxon":today["source_taxon"],
            "response":today["radius_log1p_km"],
            "weather_location_from_prior_GPS_only":True,
            "weather_previous_date_only":True,
        })
    qc={
      "qualifying_daily_source_records":len(days),
      "no_previous_day_complete_GPS":missing_prior,
      "previous_GPS_farther_than_120km_from_both_weather_grids":too_far,
      "prior_ERA5_weather_day_missing":outside_dates,
      "source_weather_and_GPS_possible_candidate_days":len(candidates),
      "source_weather_target_conditions_class_count":len(set(x["weather_class"] for x in candidates)),
      "potential_source_duck_IDs_in_fixed_wetland_radius":len({x["bird"] for x in candidates}),
      "source_weather_rain_temp_bins_not_tuned":True,
    }
    return candidates,qc

def source_mean_by_external_bird(history:dict,bird)->tuple[float|None,int,int]:
    vals=[(sum(q)/len(q),len(q)) for key,q in history.items()
          if key!=bird and q]
    if not vals:return None,0,0
    return float(np.mean([v for v,_ in vals])),len(vals),sum(n for _,n in vals)

def prequential_predictions(events:list[dict])->tuple[list[dict],dict]:
    # All target days on the same UTC date are scored BEFORE current day data
    # enter any other or own history, guaranteeing no same-day leakage.
    external=collections.defaultdict(lambda:collections.defaultdict(list))
    by_class=collections.defaultdict(lambda:collections.defaultdict(list))
    own=collections.defaultdict(lambda:collections.deque(maxlen=MAX_OWN_HIST_DAYS))
    output=[]
    sufficient_own=external_insufficient=0
    class_fallback=0
    for day,block_iter in __import__("itertools").groupby(
            sorted(events,key=lambda x:(x["date"],x["bird"])),
            key=lambda x:x["date"]):
        block=list(block_iter)
        for row in block:
            site=row["site"]
            bird=row["bird"]
            weather_class=row["weather_class"]
            own_prior=list(own[(site,bird)])
            if len(own_prior)<MIN_OWN_HIST_DAYS:
                continue
            sufficient_own+=1
            m0,birds,nrows=source_mean_by_external_bird(external[site],bird)
            if (m0 is None or birds<MIN_EXTERNAL_BIRDS or
                nrows<MIN_EXTERNAL_BIRD_DAYS):
                external_insufficient+=1
                continue
            matching,match_birds,match_rows=source_mean_by_external_bird(
                by_class[(site,weather_class)],bird)
            fallback=(matching is None or match_birds<MIN_EXTERNAL_BIRDS or
                      match_rows<MIN_EXTERNAL_BIRD_DAYS)
            if fallback:class_fallback+=1
            me=m0 if fallback else matching
            mi=float(np.mean(own_prior))
            w=len(own_prior)/(len(own_prior)+SHRINK_KAPPA)
            mei=(1.-w)*me+w*mi
            y=row["response"]
            output.append({
                "bird":bird,"date":day,"site":site,"taxon":row["taxon"],
                "n_previous_own_days":len(own_prior),
                "weather_class":weather_class,
                "matching_weather_fallback":fallback,
                "error_M0":(y-m0)**2,
                "error_ME":(y-me)**2,
                "error_MI":(y-mi)**2,
                "error_MEI":(y-mei)**2})
        # Update source history after all day-t forecasts have been computed.
        for row in block:
            site,bird=row["site"],row["bird"]
            external[site][bird].append(row["response"])
            by_class[(site,row["weather_class"])][bird].append(row["response"])
            own[(site,bird)].append(row["response"])
    qc={
      "source_candidate_days_with_3plus_prior_individual_days":sufficient_own,
      "source_target_days_without_five_birds_and_twenty_prior_examples":
          external_insufficient,
      "matched_future_individual_days":len(output),
      "actual_individuals_in_common_target_set":len({r["bird"] for r in output}),
      "weather_context_missing_support_fallbacks":class_fallback,
      "weather_context_nonfallback_fraction":
          ((len(output)-class_fallback)/len(output)) if output else 0.,
      "same_day_or_future_other_bird_outcomes_used_in_predictor":False,
      "target_day_weather_used_in_predictor":False,
    }
    return output,qc

def evaluate(records:list[dict])->dict:
    bybird=collections.defaultdict(list)
    for r in records:bybird[r["bird"]].append(r)
    if len(bybird)<MIN_SOURCE_BIRDS or len(records)<MIN_FUTURE_TARGET_DAYS:
        return {"status":"NOT_ADMITTED_ORIGINAL_INDEPENDENT_DUCK_DAYS",
                "target_individuals":len(bybird),
                "target_duck_days":len(records),"any_forecast_score_exported":False}
    nonfallback=sum(not r["matching_weather_fallback"] for r in records)
    if nonfallback/len(records)<MIN_NONSURROGATE_WEATHER_FRACTION:
        return {"status":"NOT_ADMITTED_MEASURED_ERA5_CLASS_HISTORY_SUPPORT",
                "target_individuals":len(bybird),
                "target_duck_days":len(records),
                "matched_climate_history_nonfallback_count":nonfallback,
                "any_forecast_score_exported":False}
    per={}
    for ix,bird in enumerate(sorted(bybird),1):
        rows=bybird[bird]
        errs=np.array([[r["error_M0"],r["error_ME"],r["error_MI"],r["error_MEI"]]
                       for r in rows])
        m=errs.mean(axis=0)
        per[f"duck_{ix:03d}"]={
           "future_days_scored":len(rows),
           "study":BANGLADESH_STUDY,
           "taxon":rows[0]["taxon"],
           "source_wetland_names":sorted({x["site"] for x in rows}),
           "weather_class_fallback_days":sum(x["matching_weather_fallback"] for x in rows),
           "mean_squared_log_spread_error_M0_ME_MI_MEI":list(map(float,m)),
           "primary_ME_minus_MEI":float(m[1]-m[3]),
           "weather_M0_minus_ME":float(m[0]-m[1]),
           "shrink_MI_minus_MEI":float(m[2]-m[3]),
           "total_M0_minus_MEI":float(m[0]-m[3])}
    mat=np.array([d["mean_squared_log_spread_error_M0_ME_MI_MEI"] for d in per.values()])
    rng=np.random.default_rng(BOOT_SEED)
    bootstrap=rng.integers(0,len(mat),size=(BOOT_REPS,len(mat)))
    effects={
      "primary_individual_over_ERA5_ME_minus_MEI":mat[:,1]-mat[:,3],
      "secondary_ERA5_class_M0_minus_ME":mat[:,0]-mat[:,1],
      "secondary_fixed_shrink_MI_minus_MEI":mat[:,2]-mat[:,3],
      "secondary_total_M0_minus_MEI":mat[:,0]-mat[:,3],
    }
    comparisons={}
    for key,v in effects.items():
        ci=np.quantile(v[bootstrap].mean(axis=1),[.025,.975])
        comparisons[key]={
            "equal_individual_mean_MSE_gain_log_km_squared":float(v.mean()),
            "individuals_with_positive_gain":int((v>0).sum()),
            "n_independent_original_ducks":len(v),
            "individual_bootstrap_95_percentile":list(map(float,ci))}
    return {
       "status":"EXPLORATORY_NEW_INDEPENDENT_WILD_DUCK_GPS_ERA5_FUTURE_DAY_PREDICTION",
       "original_independent_bird_count":len(per),
       "source_future_original_duck_day_targets":len(records),
       "source_weather_match_nonfallback_duck_days":nonfallback,
       "mean_MSE_M0_ME_MI_MEI":list(map(float,mat.mean(axis=0))),
       "frozen_contrasts":comparisons,
       "per_original_individual_anonymized":per,
       "source_animal_social_network_membership_observed":False,
       "predicted_GPS_statistic":"log1p observed within-day horizontal GPS radius of gyration kilometres",
       "interpretation_limits":[
         "Bangladesh sub-study only, original duck GPS, not seven independent countries",
         "Weather is coarse ERA5 reanalysis from two fixed wetland grid cells, not direct local sensors or measured prey/food",
         "Only prior-day ERA5 at nearest prior GPS fix, and previous observed individual/environment history are predictors",
         "Many ducks share study year/wetland environmental shocks; individual bootstrap not independent climate replication",
         "No direct social group network, interaction force, path coordination or ecological realized niche identified",
       ]}

def run()->dict:
    record=ducks.fetch_metadata()
    spec=ducks.select_original(record)
    with tempfile.TemporaryDirectory() as temp:
        src=Path(temp)/ducks.SOURCE_NAME
        original=ducks.get_original_file(spec,src)
        if original["original_sha256"]!=PINNED_GPS_SHA256:
            raise ValueError("Previously frozen GPS original source SHA256 drift")
        era,eraqc=load_exact_era5()
        measured,gpsqc=parse_original_gps(src)
        possible,sourceqc=eligible_daily_events(measured,era)
        forecast,forecastqc=prequential_predictions(possible)
        result=evaluate(forecast)
    return {
      "study":"v23-source-verified-multiple-duck-taxa-Bangladesh-original-daily-GPS-ERA5",
      "registered_outcome_before_source_GPS_positions":
          "docs/V23_FROZEN_DUCK_DAILY_GPS_ERA5_FORECAST.md",
      "source_GPS_integrity":original,
      "source_ERA5_integrity":eraqc,
      "original_GPS_quality":gpsqc,
      "wetland_prior_day_weather_source_support":sourceqc,
      "forecast_target_support":forecastqc,
      "status":result["status"],
      "observed_outcome":result,
      "historical_source_is_2019_2023_ERA5_reanalysis_not_station_direct_measurement":True,
      "no_raw_animal_GPS_coordinates_or_time_or_weather_values_exported":True,
      "previous_v13_through_v22_frozen_empirical_endpoints_unchanged":True}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,
       default=Path("validation_v23/results/independent_duck_daily_ERA5_forecast_v23.json"))
    args=parser.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V23_SOURCE_GPS",json.dumps(result["source_GPS_integrity"],sort_keys=True))
    print("V23_SOURCE_ERA5",json.dumps(result["source_ERA5_integrity"],sort_keys=True))
    print("V23_ORIGINAL_GPS_QUALITY",json.dumps(result["original_GPS_quality"],sort_keys=True))
    print("V23_PRIOR_DAY_CONTEXT_SUPPORT",json.dumps(result["wetland_prior_day_weather_source_support"],sort_keys=True))
    print("V23_FUTURE_TARGET_SUPPORT",json.dumps(result["forecast_target_support"],sort_keys=True))
    print("V23_OBSERVED_STATUS",result["status"])
    if result["status"].startswith("EXPLORATORY"):
        print("V23_ALL_REGISTERED_MODEL_EFFECTS",json.dumps(result["observed_outcome"]["frozen_contrasts"],sort_keys=True))
        print("V23_ALL_INDEPENDENT_BIRD_FOLDS",json.dumps(result["observed_outcome"]["per_original_individual_anonymized"],sort_keys=True))
    else:
        print("V23_EXPLICIT_SOURCE_STOP",json.dumps(result["observed_outcome"],sort_keys=True))
    print("V23_DOES_NOT_IDENTIFY_SOCIAL_FORCES_OR_TRUE_RESOURCE_NICHES")
if __name__=="__main__":
    main()
