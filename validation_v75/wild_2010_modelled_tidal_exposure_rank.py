"""v75 real 2010 oystercatcher GPS use versus 2010 NIOZ monthly model index.

Five original v74-SOURCE-ADMITTED months Aug-Dec. Original model time_expo
has UNKNOWN numeric units; only within-1km ordinal midrank is primary.
Original GPS bird IDs, UTC/GPS clocks, geographic positions and model pixels
are held ephemeral and NEVER serialized. No direct measured foraging, tide
surface or biological two-clock causal effect.
"""
from __future__ import annotations

import csv
import gzip
import json
import math
import os
import tempfile
from collections import Counter,defaultdict
from datetime import timezone
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from scipy.spatial import cKDTree
from astral import Observer
from astral.sun import elevation

from source_preflight import download_and_pin,parse_stamp
from source_gate_2012 import REGIONS
from original_coeval_wadden_model_metadata import authenticated_provider_file
from native_monthly_exposure_source import FIXED_SHA as NIOZ_FIXED_SHA
from probe_native_coordinate_mismatch import geo_valid
from wild_gps_native_month_exposure import _locxy
from real_2010_monthly_nioz_gps_source_gate import original_all_2010_manifest

MONTHS=(8,9,10,11,12)
GPS_SHA="8d7d0ac9cef0935e7351bcf9a525c0f9eeb7605dc603d227f9b09744dadd532d"
ORIGINAL_GPS_RAW=282920
MONTH_GPS_AND_BIRDS={8:(11427,16),9:(9572,16),10:(9508,15),
                      11:(7975,14),12:(6656,14)}
PINNED_MODEL_SHA={
    8:"0eacaa4b2a246ea89ed0a032be588fc77f7af630e183b4c73236104392b46ece",
    9:"61d3703efab9e8ba137aa99bd310368431fd9dcf5a8faed2fd6a82f1b86e4053",
    10:"4e2d9f53bcd6fa14da03e46b3fe0f51754e78d59e0efdebf50cf9707edd6b321",
    11:"093368f931a666a1d74591e481386801026160c0a6dc8bcf09fcf74ccd9bedfb",
    12:"a05182cacaa5473de167386d6c71f3da94ede515845cc84775c14ca2c5a62161"
}
NATIVE_EXPECTED=486*820
PRIMARY_RADIUS_METRES=1000
PRIMARY_MIN_N_NEIGHBORHOOD=20
ALTERNATIVE_RADII=((500,8),(2000,50))
MIN_MONTH_SOURCE_ANIMAL_COUNT=5
MIN_BIRD_MONTH_POINTS=20
BOOT_SEED=20261108
BOOTS=10000
MIN_ORIGINAL_DAILY_SUNLIT_SOURCE_FIXES=100
MIN_ORIGINAL_DAILY_BIRD_COUNT=5

def original_all_wild_months(path,*,expected_raw=ORIGINAL_GPS_RAW):
    """Native GPS hours source-only; all five fixed months, earliest each hour."""
    fields={"event-id","timestamp","location-lat","location-long",
            "individual-local-identifier","visible"}
    seen=set();values=defaultdict(dict);drops=Counter();rows=0
    bounds=REGIONS["schiermonnikoog"]
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as src:
        reader=csv.DictReader(src)
        if not fields<=set(reader.fieldnames or []):
            raise ValueError("SOURCE_STOP_V75_ZENODO_NATIVE_GPS_FIELDS_CHANGED")
        for r in reader:
            rows+=1
            eid=(r.get("event-id") or "").strip()
            if not eid or eid in seen:
                drops["missing_or_duplicate_original_event"]+=1;continue
            seen.add(eid)
            if (r.get("visible") or "").strip().upper() in ("FALSE","0"):
                drops["original_invisible"]+=1;continue
            bird=(r.get("individual-local-identifier") or "").strip()
            if not bird:
                drops["no_native_source_bird_ID"]+=1;continue
            try:
                stamp=parse_stamp(r["timestamp"])
                lat=float(r["location-lat"]);lon=float(r["location-long"])
            except (TypeError,ValueError):
                drops["source_native_timestamp_or_coordinates"]+=1;continue
            if (stamp.year!=2010 or not math.isfinite(lat) or
                not math.isfinite(lon) or not
                (bounds[0]<=lat<=bounds[1] and bounds[2]<=lon<=bounds[3])):
                drops["outside_original_2010_schier_scope"]+=1;continue
            if stamp.month not in MONTHS:
                drops["outside_precommitted_month_set"]+=1;continue
            hour=stamp.replace(minute=0,second=0,microsecond=0)
            old=values[bird].get(hour)
            if old is None or stamp<old[0]:
                values[bird][hour]=(stamp,lat,lon)
    if rows!=expected_raw:
        raise ValueError("SOURCE_STOP_V75_ORIGINAL_2010_RAW_COUNT_DRIFT")
    monthly=defaultdict(list)
    for bird,binmap in values.items():
        for t,lat,lon in binmap.values():
            monthly[t.month].append((bird,t,lat,lon))
    receipt={"original_full_2010_raw_gps_rows_seen":rows,
             "original_fixed_five_month_hourly_positions":{},
             "source_exclusions_all_original_2010_rows":dict(drops),
             "original_no_individual_ID_timestamp_location_serialized":True}
    for m in MONTHS:
        current=monthly[m]
        birds=len({r[0] for r in current})
        receipt["original_fixed_five_month_hourly_positions"][str(m)]={
            "source_observed_original_hourly_positions":len(current),
            "source_original_birds":birds}
        if expected_raw==ORIGINAL_GPS_RAW and (len(current),birds)!=MONTH_GPS_AND_BIRDS[m]:
            raise ValueError("SOURCE_STOP_V75_FROZEN_V74_GPS_MONTH_OR_BIRD_DRIFT")
    return monthly,receipt

def original_2010_native_month(raw,month):
    """No 2011 lat and no time-of-day imputation to numeric monthly grid."""
    if month not in MONTHS:
        raise ValueError("SOURCE_STOP_V75_UNREGISTERED_SCIENTIFIC_MONTH")
    with tempfile.NamedTemporaryFile(suffix=".nc",mode="wb") as tmp:
        tmp.write(raw);tmp.flush()
        with Dataset(tmp.name,"r") as data:
            if not {"lat","lon","time_expo"}<=set(data.variables):
                raise ValueError("SOURCE_STOP_V75_NIOZ_REQUIRED_ORIGINAL_NATIVE_FIELDS")
            def finite_native(name):
                a=np.ma.asarray(data.variables[name][:],dtype=float)
                return np.ma.filled(a,np.nan).astype(float)
            lat=finite_native("lat");lon=finite_native("lon")
            expo=finite_native("time_expo")
    if any(a.shape!=(486,820) for a in (lat,lon,expo)):
        raise ValueError("SOURCE_STOP_V75_NIOZ_2010_NATIVE_MODEL_GRID_SHAPE")
    ok=geo_valid(lat,lon)&np.isfinite(expo)&(expo>=0)&(expo<=1)
    if np.sum(ok)!=NATIVE_EXPECTED or len(np.unique(np.round(expo[ok],8)))<10:
        raise ValueError("SOURCE_STOP_V75_PREVIOUSLY_SOURCE_ADMITTED_MONTH_MODEL_CHANGED")
    return {"xy":_locxy(lat[ok],lon[ok]),"index":expo[ok],
            "n_native":int(ok.sum()),"tree":cKDTree(_locxy(lat[ok],lon[ok]))}

def geometric_preflight(month,fixes,model):
    """Do not touch used-model index values until ALL five months source-pass."""
    if month not in MONTHS:
        raise ValueError("SOURCE_STOP_V75_GPS_OUTSIDE_PRIOR_MONTHS")
    xyz=_locxy([r[2] for r in fixes],[r[3] for r in fixes])
    near,cell=model["tree"].query(xyz,k=1)
    inside=near<=300
    # Source background availability geometry, not habitat-selection results.
    circles=model["tree"].query_ball_point(xyz,r=PRIMARY_RADIUS_METRES)
    valid=np.asarray([bool(inside[i]) and len(circles[i])>=PRIMARY_MIN_N_NEIGHBORHOOD
                      for i in range(len(fixes))],dtype=bool)
    bird_counts=Counter(fixes[i][0] for i in np.flatnonzero(valid))
    birds_admitted={b for b,c in bird_counts.items() if c>=MIN_BIRD_MONTH_POINTS}
    qa={
        "source_month":month,
        "source_native_model_geolocated_cells":model["n_native"],
        "original_gps_source_hourly_positions":len(fixes),
        "original_gps_source_birds":len({r[0] for r in fixes}),
        "source_nearest_native_cell_300m":int(inside.sum()),
        "source_native_model_300m_geolocation_fraction":
            float(inside.mean()) if len(fixes) else 0,
        "source_gps_with_at_least_twenty_1km_original_grid_cells":int(valid.sum()),
        "source_original_bird_IDs_with_twenty_1km_complete_GPS":len(birds_admitted),
        "source_bird_month_eligible_GPS_after_20_per_bird":
            sum(bird_counts[b] for b in birds_admitted),
        "source_individual_bird_months_eligible":len(birds_admitted)}
    good=(len(fixes)==MONTH_GPS_AND_BIRDS[month][0] and
          len({r[0] for r in fixes})==MONTH_GPS_AND_BIRDS[month][1] and
          model["n_native"]==NATIVE_EXPECTED and
          inside.mean()>=.8 and
          valid.sum()>=200 and len(birds_admitted)>=5)
    qa["fixed_source_admission"]=(
        "SOURCE_ADMITTED_V75_ORIGINAL_GPS_2010_MONTH_NATIVE_MODEL_1KM"
        if good else "NOT_ADMITTED_V75_FIXED_MONTH_GEO_OR_BIRD_SUPPORT")
    # Private fixed-source indices; no raw animal model values here.
    return {"source_receipt":qa,"fixes":fixes,"xy":xyz,
            "closest":cell,"valid":valid,
            "valid_birds":birds_admitted,"circles":circles,"tree":model["tree"],
            "model_expo":model["index"]}

def _rank(expo,cell,native_circular_cells):
    """Numeric source midrank, monotonically invariant, tie-safe."""
    near=expo[native_circular_cells]
    val=float(expo[cell])
    if not len(near):raise ValueError("ESTIMAND_STOP_V75_EMPTY_REFERENCE")
    return (float(np.sum(near<val))+
            .5*float(np.sum(near==val)))/len(near)

def _whole_bird_bootstrap(values,*,draws=BOOTS,seed=BOOT_SEED):
    v=np.asarray(values,float)
    if not len(v) or not np.isfinite(v).all():
        raise ValueError("ESTIMAND_STOP_V75_MISSING_BIRD_CLUSTER")
    rng=np.random.default_rng(seed)
    select=rng.integers(0,len(v),size=(draws,len(v)))
    return [float(x) for x in np.quantile(v[select].mean(axis=1),[.025,.975])]

def _summarize_bird_blocks(month_bird_values,*,seed=BOOT_SEED,draws=BOOTS):
    """Equal months within a bird, THEN equal biological bird clusters."""
    all_birds=defaultdict(list)
    for m,perbird in sorted(month_bird_values.items()):
        for bird,dat in perbird.items():
            all_birds[bird].append(float(np.mean(dat)))
    if not all_birds:
        return None
    obs=np.asarray([np.mean(z) for z in all_birds.values()])
    return {
        "source_original_birds":len(obs),
        "source_admitted_bird_months":sum(len(x) for x in all_birds.values()),
        "equal_month_within_bird_then_bird_equal_mean":float(np.mean(obs)),
        "source_original_birds_with_positive_contrast":int((obs>0).sum()),
        "whole_bird_cluster_bootstrap_percentile95":_whole_bird_bootstrap(
            obs,seed=seed,draws=draws),
        "no_per_bird_or_gps_fix_values_saved":True}

def _evaluate_source_month(preflight):
    """Called ONLY after five independent source gates pass."""
    month=preflight["source_receipt"]["source_month"]
    model=preflight["model_expo"];fixes=preflight["fixes"]
    approved=preflight["valid_birds"]
    tree=preflight["tree"];xyz=preflight["xy"]
    bybird=defaultdict(list);bybird_num=defaultdict(list)
    scale={r:defaultdict(list) for r,_ in ALTERNATIVE_RADII}
    by_light={x:defaultdict(list) for x in ("DAY","NIGHT")}
    included=0;dropped_alt=Counter()
    for i,fix in enumerate(fixes):
        bird,t,lat,lon=fix
        if not preflight["valid"][i] or bird not in approved:continue
        included+=1
        near=preflight["circles"][i]
        cell=int(preflight["closest"][i])
        r=_rank(model,cell,near)
        bybird[bird].append(r-.5)
        bybird_num[bird].append(float(model[cell]-np.mean(model[near])))
        for radius,min_neighbors in ALTERNATIVE_RADII:
            cells=tree.query_ball_point(xyz[i],r=radius)
            if len(cells)>=min_neighbors:
                scale[radius][bird].append(_rank(model,cell,cells)-.5)
            else:dropped_alt[str(radius)]+=1
        solar=elevation(Observer(latitude=lat,longitude=lon,elevation=0),
                        t.replace(tzinfo=timezone.utc),with_refraction=True)
        light="DAY" if float(solar)>0 else "NIGHT"
        by_light[light][bird].append(r-.5)
    if included!=preflight["source_receipt"]["source_bird_month_eligible_GPS_after_20_per_bird"]:
        raise ValueError("SOURCE_STOP_V75_REPLAYED_ORIGINAL_1KM_BIRD_MONTH_SOURCE_DRIFT")
    return {"ordinal_rank_bybird":bybird,
            "index_numeric_bybird":bybird_num,
            "spatial_scale_bybird":scale,
            "light_bybird":by_light,
            "included":included,
            "secondary_radius_source_failures":dict(dropped_alt)}

def combined_field_score(preflights):
    """All five model source month gates must PASS BEFORE any used values read."""
    if sorted(preflights)!=list(MONTHS):
        raise ValueError("SOURCE_STOP_V75_CANNOT_SELECT_FAVORABLE_MONTH_SUBSET")
    for month in MONTHS:
        if preflights[month]["source_receipt"]["fixed_source_admission"]!=(
            "SOURCE_ADMITTED_V75_ORIGINAL_GPS_2010_MONTH_NATIVE_MODEL_1KM"):
            return {
                "source_admission":"NOT_ADMITTED_V75_FIXED_ALL_MONTHS_SOURCE",
                "wild_observed_tidal_modelled_use_effect":"NOT_ESTIMATED_SOURCE_GATE"}
    rank={};numeric={}
    radios={k:{} for k,_ in ALTERNATIVE_RADII}
    photos={k:{} for k in ("DAY","NIGHT")}
    monthly={}
    for month in MONTHS:
        v=_evaluate_source_month(preflights[month])
        rank[month]=v["ordinal_rank_bybird"]
        numeric[month]=v["index_numeric_bybird"]
        for r in radios:radios[r][month]=v["spatial_scale_bybird"][r]
        for label in photos:photos[label][month]={
            bird:values for bird,values in v["light_bybird"][label].items()
            if len(values)>=MIN_BIRD_MONTH_POINTS}
        monthly[str(month)]={
            "original_source_month":month,
            "gps_source_hourly_positions_with_month_specific_model_index":v["included"],
            "distinct_source_birds_with_20_or_more_source_fixes":len(rank[month]),
            "bird_equal_1km_ordinal_percentile_above_geometric_midpoint":
                _summarize_bird_blocks({month:rank[month]},
                                        seed=BOOT_SEED+month,draws=5000),
            "secondary_500m_2km_source_pixel_shortage":v["secondary_radius_source_failures"]}
    primary=_summarize_bird_blocks(rank)
    if primary is None:
        raise ValueError("ESTIMAND_STOP_V75_NO_WILD_2010_MONTHLY_BIRD_USED_SOURCE")
    main=primary["equal_month_within_bird_then_bird_equal_mean"]
    ci=primary["whole_bird_cluster_bootstrap_percentile95"]
    status=("EXPLORATORY_POSITIVE_WILD_GPS_MONTHLY_MODELED_TIDAL_INDEX_LOCAL_ORDINAL_ASSOCIATION"
            if main>0 and ci[0]>0
            else "LOCAL_MODELED_INDEX_RANK_OVER_LOCAL_GEOMETRIC_REFERENCE_NOT_ESTABLISHED")
    scales={}
    for r in radios:
        models=radios[r]
        acceptable={m:{b:arr for b,arr in birds.items() if len(arr)>=MIN_BIRD_MONTH_POINTS}
                    for m,birds in models.items()}
        scales[str(r)+"_m"]= _summarize_bird_blocks(
            acceptable,seed=BOOT_SEED+r)
    light={}
    for label,groups in photos.items():
        n=sum(len(values) for v in groups.values() for values in v.values())
        birds=len({bird for v in groups.values() for bird in v})
        if n<MIN_ORIGINAL_DAILY_SUNLIT_SOURCE_FIXES or birds<MIN_ORIGINAL_DAILY_BIRD_COUNT:
            light[label]={"status":"INSUFFICIENT_NATIVE_GPS_LIGHT_SOURCE",
                          "original_bird_months":sum(len(v) for v in groups.values()),
                          "original_source_positions":n,"original_birds":birds}
        else:
            light[label]={
                "status":"DESCRIPTIVE_PROVISIONALLY_UTC_SUNLIGHT_NOT_DAYLENGTH_CAUSATION",
                "original_source_positions":n,
                **_summarize_bird_blocks(groups,seed=BOOT_SEED+(11 if label=="DAY" else 12))}
    month_values=[monthly[str(m)]["bird_equal_1km_ordinal_percentile_above_geometric_midpoint"][
        "equal_month_within_bird_then_bird_equal_mean"] for m in MONTHS]
    return {
        "source_admission":"SOURCE_ADMITTED_ALL_FIVE_ORIGINAL_2010_MONTHS",
        "scientific_endpoint":"midrank of native NIOZ model index at original observed GPS cell versus original native 1km model cells, minus 0.5",
        "original_model_exposure_index_unit":"UNKNOWN_ORDINAL_NOT_HOURS_OR_PERCENT_OF_EXPOSURE",
        "original_used_vs_local_ordinal_rank_bird_equal_primary":primary,
        "frozen_primary_status":status,
        "per_2010_month_observed_source_ordinal_result_ALL_FIVE":monthly,
        "secondary_numeric_unitless_model_index_difference_bird_equal":
            _summarize_bird_blocks(numeric,seed=BOOT_SEED+1),
        "secondary_precommitted_spatial_radii":scales,
        "secondary_UTC_UNVERIFIED_astro_day_night":light,
        "month_equal_source_five_months_descriptive":{
            "original_months":5,
            "month_equal_mean_rank_above_0p5":float(np.mean(month_values)),
            "five_month_bootstrap95_DESCRIPTIVE_ONLY":
                _whole_bird_bootstrap(month_values,draws=5000,seed=BOOT_SEED+25)},
        "no_native_NIOZ_monthly_numeric_units_or_actual_preference_calibrated":True,
        "no_individual_GPS_animal_tag_timestamp_raster_pixel_or_monthly_bird_mean_released":True,
        "no_real_food_resource_or_daylight_tide_causal_mechanism_estimated":True,
        "not_new_wild_species_or_independent_area":True}
