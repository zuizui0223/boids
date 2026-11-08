"""v73 original wild January 2010 GPS vs original NIOZ monthly model exposure.

Frozen source gate first. Real source field GPS original 2010 events are
independent from 2010 model exposure values, but biological foraging and
exposed-cell times are NOT observed. Source units of time_expo UNKNOWN:
numeric difference only, never hours, foraging or physical dry-time ratio.
Only anonymous aggregates ever exported.
"""
from __future__ import annotations
import csv,gzip,json,math,os,tempfile
from collections import Counter,defaultdict
from datetime import timezone
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from astral import Observer
from astral.sun import elevation

from source_preflight import download_and_pin,parse_stamp
from source_gate_2012 import REGIONS
from original_coeval_wadden_model_metadata import (
    original_metadata,authenticated_provider_file)
from native_monthly_exposure_source import (
    FIXED_SHA,original_native_month,native_readme_meaning)
from probe_native_coordinate_mismatch import geo_valid

MIN_HOURLY_FIXES=200
MIN_BIRDS=5
MIN_GEO_COVER=.8
MAX_NEAREST_M=300
BACKGROUND_RADIUS_M=1000
MIN_BACKGROUND_CELLS=20
BIRD_MIN_FIXES=20
BIRD_BOOT_DRAWS=10000
BIRD_SEED=20261108
MIN_DISTINCT_MODEL_EXPO_VALUES=10

def original_visible_january_2010_fixes(path):
    """One native earliest visible source fix per bird-hour, no outcome filters."""
    bounds=REGIONS["schiermonnikoog"]
    wanted={"event-id","timestamp","location-lat","location-long",
            "individual-local-identifier","visible"}
    chosen=defaultdict(dict)
    seen=set();drops=Counter();raw=0
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not wanted<=set(reader.fieldnames or []):
            raise ValueError("SOURCE_STOP_V73_ORIGINAL_GPS_SCHEMA_CHANGED")
        for record in reader:
            raw+=1
            eid=(record.get("event-id") or "").strip()
            if not eid or eid in seen:
                drops["duplicate_or_missing_original_event"]+=1;continue
            seen.add(eid)
            if record["visible"].strip().upper() in ("FALSE","0"):
                drops["original_invisible_event"]+=1;continue
            bird=(record.get("individual-local-identifier") or "").strip()
            if not bird:
                drops["original_missing_bird"]+=1;continue
            try:
                t=parse_stamp(record["timestamp"])
                lat=float(record["location-lat"]);lon=float(record["location-long"])
            except (TypeError,ValueError):
                drops["original_invalid_native_clock_or_coords"]+=1;continue
            if t.year!=2010 or t.month!=1:
                drops["other_original_2010_month"]+=1;continue
            if not (math.isfinite(lat) and math.isfinite(lon) and
                    bounds[0]<=lat<=bounds[1] and bounds[2]<=lon<=bounds[3]):
                drops["outside_original_Schier_geographic_bounds"]+=1;continue
            hour=t.replace(minute=0,second=0,microsecond=0)
            old=chosen[bird].get(hour)
            if old is None or t<old[0]:
                chosen[bird][hour]=(t,lat,lon)
    rows=[{"id":bird,"t":t,"lat":lat,"lon":lon}
          for bird,records in chosen.items()
          for t,lat,lon in records.values()]
    return rows,{"raw_original_annual_rows_seen":raw,
                 "original_valid_visible_January_distinct_bird_hour_fixes":len(rows),
                 "original_visible_January_bird_ID_count":len(chosen),
                 "original_QC_source_reasons":dict(drops),
                 "no_per_bird_original_ids_locations_timestamps_exported":True}

def _locxy(lat,lon):
    """Frozen local flat metric transform; 53N domain only, x/y in metres."""
    return np.column_stack((
        np.asarray(lon)*math.cos(math.radians(53.45))*111195.,
        np.asarray(lat)*111195.))

def grid_source(original):
    la,lo,exposure=original
    valid=geo_valid(la,lo)&np.isfinite(exposure)&(exposure>=0)&(exposure<=1)
    if int(valid.sum())!=486*820:
        raise ValueError("SOURCE_STOP_V73_ORIGINAL_2010_NIOZ_MODEL_GRID_NOT_FULLY_VALID")
    return {"xy":_locxy(la[valid],lo[valid]),
            "exposure":exposure[valid],
            "n_source_cells":int(valid.sum())}

def map_geo_source_only(fixes,model):
    tree=cKDTree(model["xy"])
    xy=_locxy([r["lat"] for r in fixes],[r["lon"] for r in fixes])
    distance,closest=tree.query(xy,k=1)
    geo=distance<=MAX_NEAREST_M
    bybird=defaultdict(Counter)
    for i,r in enumerate(fixes):
        bybird[r["id"]]["all"]+=1
        if geo[i]:bybird[r["id"]]["match"]+=1
    matches=int(np.sum(geo))
    audit={
        "source_input_hourly_fix_count":len(fixes),
        "source_bird_count":len(bybird),
        "native_geo_matching_within_300m":matches,
        "native_geo_matching_coverage_fraction":matches/len(fixes) if fixes else 0,
        "source_birds_with_at_least_20_mapped_original_fixes":sum(
            c["match"]>=BIRD_MIN_FIXES for c in bybird.values()),
        "source_2010_NIOZ_native_grid_cells":model["n_source_cells"]}
    if (len(fixes)<MIN_HOURLY_FIXES or len(bybird)<MIN_BIRDS or
        audit["native_geo_matching_coverage_fraction"]<MIN_GEO_COVER or
        audit["source_birds_with_at_least_20_mapped_original_fixes"]<MIN_BIRDS):
        audit["source_admission"]="NOT_ADMITTED_V73_INSUFFICIENT_NATIVE_JAN_GPS_OR_2010_GRID"
        return [],audit
    matched=[]
    failure=Counter()
    for i in np.flatnonzero(geo):
        neighbors=tree.query_ball_point(xy[i],r=BACKGROUND_RADIUS_M)
        if len(neighbors)<MIN_BACKGROUND_CELLS:
            failure["fewer_than_twenty_native_1km_background_cells"]+=1
            continue
        matched.append((fixes[int(i)],int(closest[i]),neighbors))
    audit["original_January_native_GPS_with_full_background_cells"]=len(matched)
    audit["source_neighborhood_drop_reasons"]=dict(failure)
    return matched,audit

def _cluster_bootstrap(values,seed):
    a=np.asarray(values,dtype=float)
    if not len(a) or not np.isfinite(a).all():
        raise ValueError("ESTIMAND_STOP_V73_NO_VALID_ORIGINAL_BIRD_BLOCK")
    rng=np.random.default_rng(seed)
    samples=rng.integers(0,len(a),size=(BIRD_BOOT_DRAWS,len(a)))
    return [float(x) for x in np.quantile(a[samples].mean(1),[.025,.975])]

def model_used_vs_local(fixes,source,*,known_truth_allow_small=False):
    matched,audit=map_geo_source_only(fixes,source)
    if known_truth_allow_small:
        # For known truth tests only; actual field gate may NEVER use this path.
        pass
    if audit.get("source_admission","").startswith("NOT_ADMITTED"):
        return {"source_gate":audit,
                "original_field_exposure_index_contrast":"NOT_ESTIMATED_SOURCE_GATE"}
    bybird=defaultdict(list)
    daylight=defaultdict(lambda:defaultdict(list))
    distinct=set()
    model_uses=[];model_background=[]
    for fix,cell,neighbors in matched:
        observed=float(source["exposure"][cell])
        baseline=float(np.mean(source["exposure"][neighbors]))
        distinct.add(round(observed,8))
        bybird[fix["id"]].append(observed-baseline)
        model_uses.append(observed)
        model_background.append(baseline)
        # Secondary astronomical status uses GPS native clock interpreted as UTC;
        # this may differ from sensor GPS time; NEVER primary.
        t=fix["t"].replace(tzinfo=timezone.utc)
        obs=Observer(latitude=fix["lat"],longitude=fix["lon"],elevation=0)
        sunlit=float(elevation(obs,t,with_refraction=True))>0
        daylight["DAY" if sunlit else "NIGHT"][fix["id"]].append(observed-baseline)
    if len(distinct)<MIN_DISTINCT_MODEL_EXPO_VALUES or len(matched)<MIN_HOURLY_FIXES:
        audit["source_admission"]="NOT_ADMITTED_V73_TOO_FEW_DISTINCT_SOURCE_MODEL_VALUES"
        return {"source_gate":audit,
                "original_field_exposure_index_contrast":"NOT_ESTIMATED_SOURCE_GATE"}
    bird_means=[float(np.mean(rows)) for rows in bybird.values()]
    mean=float(np.mean(bird_means))
    ci=_cluster_bootstrap(bird_means,BIRD_SEED)
    daynight={}
    for key,birds in daylight.items():
        count=sum(len(z) for z in birds.values())
        if count<50 or len(birds)<3:
            daynight[key]={"status":"INSUFFICIENT_FIXED_OBSERVED_CLASS",
                           "source_valid_fixes":count,"source_birds":len(birds)}
        else:
            q=[float(np.mean(arr)) for arr in birds.values()]
            daynight[key]={
                "status":"DESCRIPTIVE_PROVISIONALLY_UTC_GPS_SOURCE",
                "source_valid_fixes":count,
                "original_birds":len(birds),
                "bird_equal_mean_numeric_model_exposure_minus_1km_background":
                    float(np.mean(q)),
                "bird_bootstrap_95":_cluster_bootstrap(q,BIRD_SEED+1),
                "original_birds_positive":sum(z>0 for z in q)}
    audit["source_admission"]="ORIGINAL_WILD_JANUARY_POSITION_NIOZ_MODEL_1KM_LOCAL_COMPARISON"
    return {
        "analysis":"V73_ORIGINAL_JAN_2010_GPS_VS_NATIVE_MODELED_MONTHLY_EXPOSURE_SOURCE_INDEX",
        "source_gate":audit,
        "model_original_units":"UNKNOWN_NUMERIC_ORDINAL_ONLY_NOT_EXPOSURE_HOURS_OR_FRACTION",
        "original_field_primary":{
            "source_original_detected_2010_bird_count":len(bybird),
            "source_original_January_positions_with_1km_native_model_reference":len(matched),
            "source_bird_equal_model_numeric_index_used_minus_nearby":mean,
            "whole_bird_cluster_bootstrap_95":ci,
            "source_birds_positive_local_index_contrast":sum(z>0 for z in bird_means),
            "pooled_original_source_used_index_mean_DESCRIPTIVE":
                float(np.mean(model_uses)),
            "pooled_1km_model_background_index_mean_DESCRIPTIVE":
                float(np.mean(model_background)),
            "source_field_status":(
                "EXPLORATORY_POSITIVE_LOCAL_NATIVE_MODELED_EXPOSURE_INDEX_ASSOCIATION"
                if mean>0 and ci[0]>0
                else "LOCAL_MODELED_EXPOSURE_ASSOCIATION_NOT_ESTABLISHED")},
        "source_UTC_UNVERIFIED_astronomical_day_night_secondary":daynight,
        "not_actual_measured_exposed_intertidal_area_or_prey":True,
        "no_2011_GPS_training_or_hydrodynamic_match":True,
        "no_per_bird_original_GPS_location_time_or_model_pixel_output":True}
