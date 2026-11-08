"""v74: authentic all-2010-month NIOZ modeled tide index × original GPS SOURCE GATE.

This is a full-2010 SOURCE-ONLY census, after January 2010 v73 failed >=5
bird gate. No year/calendar, month, pixel, spatial coordinate is imputed.
No bird use-vs-local model-index effects, no model fit or heading outcome.
"""
from __future__ import annotations
import csv
import gzip
import hashlib
import json
import math
import os
import re
import tempfile
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from scipy.spatial import cKDTree

from source_preflight import download_and_pin,parse_stamp
from source_gate_2012 import REGIONS
from original_coeval_wadden_model_metadata import (
    CKAN,PACKAGE,_get,_url_from_publisher,authenticated_provider_file)
from native_monthly_exposure_source import FIXED_SHA,_haversine_m
from probe_native_coordinate_mismatch import geo_valid
from wild_gps_native_month_exposure import _locxy

MONTH_NAMES=tuple(f"eco_av.2010{month:02d}.nc" for month in range(1,13))
EXPECTED_RAW_GPS=282920
TOTAL_NATIVE_CELLS=486*820
EXPECTED_PUBLISHER_MODEL_MONTHS=36
MONTH_MIN_BIRDS=5
MONTH_MIN_NATIVE_HOURLY_GPS=200
MIN_GEO_FRACTION=.8
NEAREST_NATIVE_CENTRE_MAX_METRES=300
MIN_BIRD_FIVE_GEO_SUPPORT=20
MIN_NATIVE_PIXEL_GEOGRAPHIC=10000
MIN_DISTINCT_NATIVE_INDEX=10

def original_all_2010_manifest(fetch=_get):
    original=json.loads(fetch(CKAN,cap=5_000_000))
    if not original.get("success") or (
        original.get("result") or {}).get("id")!=PACKAGE:
        raise ValueError("SOURCE_STOP_V74_ORIGINAL_NIOZ_PACKAGE_ID_OR_SUCCESS")
    resources=original["result"]["resources"]
    n=sum(re.fullmatch(r"eco_av\.20(?:09|10|11)(?:0[1-9]|1[0-2])\.nc",
                       str(r.get("name") or r.get("filename") or "")) is not None
          for r in resources)
    if n!=EXPECTED_PUBLISHER_MODEL_MONTHS:
        raise ValueError("SOURCE_STOP_V74_ORIGINAL_36_MONTHS_SOURCE_MANIFEST_CHANGED")
    names={}
    for source in resources:
        name=source.get("name") or source.get("filename") or ""
        if name in MONTH_NAMES or name=="README.txt":
            if name in names:
                raise ValueError("SOURCE_STOP_V74_ORIGINAL_PROVIDER_DUPLICATE_MONTH")
            value={"name":name,
                   "md5":str(source.get("hash") or "").lower(),
                   "size":int(source.get("size") or 0),
                   "url":_url_from_publisher(
                       "https://doi.nioz.nl/",source.get("url"))}
            if not re.fullmatch(r"[a-f0-9]{32}",value["md5"]):
                raise ValueError("SOURCE_STOP_V74_ORIGINAL_PROVIDER_MD5_MISSING")
            if not 0<value["size"]<=25_000_000:
                raise ValueError("SOURCE_STOP_V74_ORIGINAL_PROVIDER_BYTES_MISSING")
            names[name]=value
    if not set(MONTH_NAMES+("README.txt",))==set(names):
        raise ValueError("SOURCE_STOP_V74_ONE_OR_MORE_ORIGINAL_2010_MONTHS_MISSING")
    return names

def parse_whole_2010_original_hourly(path,*,expected_raw=EXPECTED_RAW_GPS):
    """Source alone, original earliest visible native GPS per bird × hour."""
    needed={"event-id","timestamp","location-long","location-lat",
            "individual-local-identifier","visible"}
    bounds=REGIONS["schiermonnikoog"]
    early=defaultdict(dict)
    seen=set()
    reasons=Counter()
    raw=0
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not needed<=set(reader.fieldnames or []):
            raise ValueError("SOURCE_STOP_V74_ORIGINAL_GPS_FIELDS_CHANGED")
        for r in reader:
            raw+=1
            eid=(r.get("event-id") or "").strip()
            if not eid or eid in seen:
                reasons["missing_or_duplicate_event_id"]+=1
                continue
            seen.add(eid)
            if (r.get("visible") or "").strip().upper() in ("FALSE","0"):
                reasons["invisible_original_source_event"]+=1
                continue
            bird=(r.get("individual-local-identifier") or "").strip()
            if not bird:
                reasons["missing_original_animal_ID"]+=1
                continue
            try:
                t=parse_stamp(r["timestamp"])
                lat=float(r["location-lat"]);lon=float(r["location-long"])
            except (ValueError,TypeError):
                reasons["invalid_original_native_time_or_position"]+=1
                continue
            if (t.year!=2010 or not math.isfinite(lat) or
                not math.isfinite(lon) or not
                (bounds[0]<=lat<=bounds[1] and bounds[2]<=lon<=bounds[3])):
                reasons["outside_original_frozen_Schier_2010_source"]+=1
                continue
            key=t.replace(minute=0,second=0,microsecond=0)
            old=early[bird].get(key)
            if old is None or t<old[0]:
                early[bird][key]=(t,lat,lon)
    if raw!=expected_raw:
        raise ValueError("SOURCE_STOP_V74_ORIGINAL_2010_282920_GPS_CHANGED")
    months=defaultdict(list)
    for bird,values in early.items():
        for t,lat,lon in values.values():
            months[t.month].append((bird,lat,lon))
    counts={str(month):{"native_hourly_source_fixes":len(months[month]),
                        "original_birds":len({x[0] for x in months[month]})}
            for month in range(1,13)}
    return months,{"original_GPS_raw_2010_year_rows":raw,
                   "original_hourly_visible_Schier_2010_positions":
                       sum(x["native_hourly_source_fixes"] for x in counts.values()),
                   "original_animal_IDs_in_2010_visible_geographic_gate":len(early),
                   "source_year_months":counts,
                   "annual_original_event_QC_reasons":dict(reasons),
                   "no_bird_tag_or_original_time_coordinates_persisted":True}

def original_month_native_source(raw,filename):
    if filename not in MONTH_NAMES:
        raise ValueError("SOURCE_STOP_V74_OUTSIDE_FROZEN_ORIGINAL_2010_MONTHS")
    with tempfile.NamedTemporaryFile(mode="wb",suffix=".nc") as temp:
        temp.write(raw);temp.flush()
        with Dataset(temp.name,"r") as ds:
            if not {"lat","lon","time_expo"}<=set(ds.variables):
                raise ValueError("SOURCE_STOP_V74_ORIGINAL_NATIVE_MONTH_MODEL_FIELDS_CHANGED")
            def x(name):
                return np.ma.filled(np.ma.asarray(ds.variables[name][:],dtype=float),
                                    np.nan).astype(float)
            lat=x("lat");lon=x("lon");index=x("time_expo")
            if any(z.shape!=(486,820) for z in (lat,lon,index)):
                raise ValueError("SOURCE_STOP_V74_ORIGINAL_MODEL_NATIVE_SHAPE_CHANGED")
    geo=geo_valid(lat,lon)
    good=geo&np.isfinite(index)&(index>=0)&(index<=1)
    native_geo=int(geo.sum())
    model_eligible=int(good.sum())
    if model_eligible:
        num_unique=len(np.unique(np.round(index[good],8)))
    else:
        num_unique=0
    qa={
        "original_month_filename":filename,
        "original_native_grid_cells":int(index.size),
        "original_native_lat_lon_valid_geographic_cells":native_geo,
        "original_native_numerical_model_index_0_to_1_geographic_cells":model_eligible,
        "native_source_model_index_distinct_values_rounded_1e_minus8":num_unique,
        "original_missing_geographic_cells":int(index.size-native_geo),
        "original_source_model_index_nonfinite_cells":int((~np.isfinite(index)).sum()),
        "original_source_model_index_numeric_out_of_0_1_cells":
            int((geo&np.isfinite(index)&((index<0)|(index>1))).sum()),
        "monthly_model_is_gridded_hindcast_NOT_directly_measured_tidal_or_10min":True}
    if model_eligible>=MIN_NATIVE_PIXEL_GEOGRAPHIC and num_unique>=MIN_DISTINCT_NATIVE_INDEX:
        xy=_locxy(lat[good],lon[good])
        return {"xy":xy,"n":model_eligible},qa
    return None,qa

def source_month_geo_fixes(hourly,grid,qa):
    birds={r[0] for r in hourly}
    n=len(hourly)
    record={"original_native_hourly_GPS_fixes":n,
            "original_distinct_birds":len(birds),**qa}
    if grid is None:
        record.update(original_nearby_300m_source_fixes=0,
            original_geo_fraction=None,
            original_individuals_geocoded_at_least_20=None,
            original_fixed_month_admission="NOT_ADMITTED_V74_NATIVE_MODEL_GEOGRAPHIC_OR_INDEX")
        return record
    tree=cKDTree(grid["xy"])
    pts=_locxy([x[1] for x in hourly],[x[2] for x in hourly])
    if len(pts):
        dist,_=tree.query(pts,k=1)
        mapped=dist<=NEAREST_NATIVE_CENTRE_MAX_METRES
    else:
        mapped=np.zeros((0,),dtype=bool)
    by=defaultdict(Counter)
    for i,r in enumerate(hourly):
        by[r[0]]["total"]+=1
        if mapped[i]:by[r[0]]["geo"]+=1
    good_birds=sum(v["geo"]>=MIN_BIRD_FIVE_GEO_SUPPORT for v in by.values())
    record.update(
        original_nearby_300m_source_fixes=int(mapped.sum()),
        original_geo_fraction=float(mapped.mean()) if len(mapped) else None,
        original_individuals_geocoded_at_least_20=good_birds)
    admitted=(n>=MONTH_MIN_NATIVE_HOURLY_GPS and len(birds)>=MONTH_MIN_BIRDS
              and len(mapped)>0 and mapped.mean()>=MIN_GEO_FRACTION
              and good_birds>=MONTH_MIN_BIRDS)
    record["original_fixed_month_admission"]=(
        "SOURCE_ADMITTED_V74_FIXED_GPS_AND_MODELED_INDEX_GEOMETRY_ONLY"
        if admitted else
        "NOT_ADMITTED_V74_JAN_THRESHOLD_APPLIED_TO_NATIVE_MONTH")
    return record

def run(output):
    original_manifest=original_all_2010_manifest()
    # Verify and report the original NIOZ model + original GPS but no animal
    # used-index contrast. JAN original 2010 SHA is immutable v71.
    readme,meta=authenticated_provider_file(original_manifest["README.txt"])
    if meta["original_computed_sha256"]!=FIXED_SHA["README.txt"]:
        raise ValueError("SOURCE_STOP_V74_ORIGINAL_README_SHA_CHANGED")
    from native_monthly_exposure_source import native_readme_meaning
    meaning=native_readme_meaning(readme)
    if not (meaning["native_exposure_variable_literal_mentioned"]
            and meaning["native_exposure_word_documented"]):
        raise ValueError("SOURCE_STOP_V74_MODEL_EXPOSURE_SOURCE_MEANING_MISSING")
    with tempfile.TemporaryDirectory(prefix="boids_original_v74_2010_") as td:
        gps_path=Path(td)/"original_Schier_2010.csv.gz"
        manifest=download_and_pin(2010,gps_path)
        if manifest.get("provider_md5_match") is not True:
            raise ValueError("SOURCE_STOP_V74_ZENODO_ORIGINAL_GPS_NOT_MD5_VERIFIED")
        months,original_qa=parse_whole_2010_original_hourly(gps_path)
    print("V74_ORIGINAL_2010_WILD_GPS_MONTH_SOURCE_ONLY "+
          json.dumps(original_qa["source_year_months"],sort_keys=True),flush=True)
    reports={}
    source_shas={}
    for month in range(1,13):
        name=MONTH_NAMES[month-1]
        raw,receipt=authenticated_provider_file(original_manifest[name])
        if month==1 and receipt["original_computed_sha256"]!=FIXED_SHA[name]:
            raise ValueError("SOURCE_STOP_V74_IMMUTABLE_PRIOR_JAN_MODEL_CHANGED")
        source_shas[name]={"original_provider_MD5_verified":True,
                           "original_computed_sha256":receipt["original_computed_sha256"],
                           "original_bytes":receipt["original_bytes"]}
        grid,qa=original_month_native_source(raw,name)
        report=source_month_geo_fixes(months[month],grid,qa)
        reports[f"{month:02d}"]=report
        print("V74_ORIGINAL_JAN_TO_DEC_NATIVE_MODEL_SOURCE_SUPPORT "+
              json.dumps({"month":f"{month:02d}",
                "native_geo_cells":qa["original_native_lat_lon_valid_geographic_cells"],
                "source_model_cells":qa["original_native_numerical_model_index_0_to_1_geographic_cells"],
                "unique_model_numeric_values":qa["native_source_model_index_distinct_values_rounded_1e_minus8"],
                "original_GPS_hourly_fixes":report["original_native_hourly_GPS_fixes"],
                "original_bird_IDs":report["original_distinct_birds"],
                "matched_nearest_within300m":report["original_nearby_300m_source_fixes"],
                "bird_IDs_geocoded_at_least20":report["original_individuals_geocoded_at_least_20"],
                "admission":report["original_fixed_month_admission"]},
                sort_keys=True),flush=True)
    source_pass=[m for m,q in reports.items() if q["original_fixed_month_admission"].startswith("SOURCE_ADMITTED")]
    report={
        "analysis":"V74_ALL_2010_WILD_SCHIER_GPS_VS_NIOZ_HINDSIGHT_NATIVE_MONTH_SOURCE_ONLY",
        "original_source_2010_GPS_provider_md5_verified":True,
        "original_2010_GPS_SHA256":manifest["original_sha256"],
        "original_ZENODO_GPS_2010_public_record":"https://zenodo.org/records/22296922",
        "original_NIOZ_public_DOI":"https://doi.org/10.25850/nioz/7b.b.n",
        "original_model_publisher_2010_twelve_month_hashes":source_shas,
        "original_originally_published_readme_semantic":meaning,
        "wild_2010_original_annual_GPS_source":original_qa,
        "each_precommitted_2010_month_source_support":reports,
        "number_original_months_source_admitted":len(source_pass),
        "source_admitted_calendar_months_list_not_a_biological_effect":source_pass,
        "original_year_months_2010_source_census_complete":len(reports)==12,
        "original_exposure_model_index_numeric_units_undocumented":True,
        "no_monthly_wild_bird_use_vs_availability_contrast_was_fit":True,
        "no_original_2011_native_geographic_latitude_imputed":True,
        "original_same_species_same_year_no_cross_species_generalization":True,
        "ecological_conclusion":"SOURCE_ONLY_NO_NEW_WILD_TIDAL_HABITAT_CHOICE_EFFECT"}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("V74_ORIGINAL_YEAR_2010_12MONTH_SOURCE_QA_FINAL "+
          json.dumps({"total_native_months_examined":12,
                       "source_admitted_months":source_pass,
                       "monthly_index_original_year":"2010",
                       "no_biological_effect_scored":True},sort_keys=True),flush=True)
    print("V74_WHOLE_2010_MONTH_NATIVE_MODEL_SOURCE_AUDIT_COMPLETED",flush=True)
    return report

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    run(p.parse_args().output)
