"""v80 original NIOZ static 2010 native geographic mesh SOURCE ONLY.

12 authentic 2010 NIOZ files + preselected 4 original 2009/2011 files.
Publisher MD5/bytes + SHA256; exact numeric array-index lat/lon comparison.
June/July original latitude is NEVER claimed observed or reconstructed here.
NO wild bird GPS, original RWS tide, used-location index or ecological effect.
"""
from __future__ import annotations
import hashlib
import json
import re
import tempfile
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from original_coeval_wadden_model_metadata import (
    CKAN,PACKAGE,_get,_url_from_publisher,authenticated_provider_file,
    STUDY_SITE_POINTS)
from native_monthly_exposure_source import _haversine_m

MONTHS_2010=tuple(f"eco_av.2010{m:02d}.nc" for m in range(1,13))
PRESELECTED_OTHERYEAR=("eco_av.200901.nc","eco_av.200908.nc",
                       "eco_av.201108.nc","eco_av.201112.nc")
README="README.txt"
PUBLISHER_FILES=(README,)+MONTHS_2010+PRESELECTED_OTHERYEAR
PRE_PINNED={
 "README.txt":"4a273823ed9ea7925caccecf87b1d0220d8c4eeed25869cbb379c45de66e19ff",
 "eco_av.201001.nc":"f8df67d7351754173978364cd89afbf3a2bba4f3a4f85ef270b1090c14e72bad",
}
NATIVE_SHAPE=(486,820)
EXPECTED_CELLS=398520
COORD_TOLERANCE_FOR_EXACT_COMPARISON=0
DEGREE_LAT=(48.,57.)
DEGREE_LON=(2.,10.)
MAX_GAUGE_NEAREST_M=200.
MIN_GAUGE_5KM_NATIVE_CELLS=100
MIN_OTHER_YEAR_COMPLETE_IDENTICAL=2
MISSING_2010_MONTHS=(6,7)

def original_manifest(fetch=_get):
    """Original CKAN resource IDs/MD5/size not guessed download URLs."""
    response=json.loads(fetch(CKAN,cap=5_000_000))
    if response.get("success") is not True:
        raise ValueError("SOURCE_STOP_V80_NIOZ_ORIGINAL_PROVIDER_FAILURE")
    result=response.get("result") or {}
    if result.get("id")!=PACKAGE:
        raise ValueError("SOURCE_STOP_V80_NIOZ_ORIGINAL_PACKAGE_ID")
    resources=result.get("resources") or []
    if sum(bool(re.fullmatch(
            r"eco_av\.(?:2009|2010|2011)(?:0[1-9]|1[0-2])\.nc",
            str(r.get("name") or r.get("filename") or "")))
           for r in resources)!=36:
        raise ValueError("SOURCE_STOP_V80_ORIGINAL_NIOZ_36_MONTH_SOURCE_CHANGED")
    names={}
    for resource in resources:
        name=resource.get("name") or resource.get("filename") or ""
        if name not in PUBLISHER_FILES:
            continue
        if name in names:
            raise ValueError("SOURCE_STOP_V80_DUPLICATE_PUBLISHER_MONTH")
        item={
            "name":name,"md5":str(resource.get("hash") or "").lower(),
            "size":int(resource.get("size") or 0),
            "url":_url_from_publisher(
                "https://doi.nioz.nl/",resource.get("url"))}
        if not re.fullmatch("[0-9a-f]{32}",item["md5"]):
            raise ValueError("SOURCE_STOP_V80_MISSING_ORIGINAL_PROVIDER_MD5")
        if not (0<item["size"]<=25_000_000):
            raise ValueError("SOURCE_STOP_V80_WRONG_NATIVE_FILE_BYTES")
        names[name]=item
    if set(names)!=set(PUBLISHER_FILES):
        raise ValueError("SOURCE_STOP_V80_FROZEN_ORIGINAL_MONTHS_MISSING")
    return names

def read_native_geo(raw,filename):
    """Only original model raw geographic variables and metadata; no biology."""
    if filename not in MONTHS_2010+PRESELECTED_OTHERYEAR:
        raise ValueError("SOURCE_STOP_V80_UNREGISTERED_MODEL_MONTH")
    with tempfile.NamedTemporaryFile(suffix=".nc",mode="wb") as temp:
        temp.write(raw);temp.flush()
        with Dataset(temp.name,"r") as nc:
            needed={"lat","lon","time_expo"}
            if not needed.issubset(nc.variables):
                raise ValueError("SOURCE_STOP_V80_NO_ORIGINAL_NATIVE_COORDS")
            head={}
            native=[]
            for name in ("lat","lon","time_expo"):
                var=nc.variables[name]
                head[name]={
                    "dims":list(var.dimensions),
                    "dtype":str(var.dtype),
                    "units_original":str(getattr(var,"units",""))[:70],
                    "fillvalue_defined":hasattr(var,"_FillValue"),
                    "missing_value_defined":hasattr(var,"missing_value")}
                if tuple(var.shape)!=NATIVE_SHAPE:
                    raise ValueError("SOURCE_STOP_V80_ORIGINAL_GRID_NATIVE_SHAPE")
                arr=np.ma.asarray(var[:],dtype=float)
                head[name]["original_masked_count"]=int(
                    np.ma.getmaskarray(arr).sum())
                a=np.ma.filled(arr,np.nan).astype(float)
                head[name]["source_finite_count"]=int(np.isfinite(a).sum())
                native.append(a)
    lat,lon,expo=native
    valid=(np.isfinite(lat)&np.isfinite(lon)&
           (DEGREE_LAT[0]<=lat)&(lat<=DEGREE_LAT[1])&
           (DEGREE_LON[0]<=lon)&(lon<=DEGREE_LON[1]))
    head["native_source_geographic_degree_valid_cells"]=int(valid.sum())
    head["native_index_source_finite_count"]=int(np.isfinite(expo).sum())
    head["native_time_expo_model_not_10min_or_measured"]=True
    return lat,lon,head

def summaries(v):
    a=np.asarray(v,dtype=float)
    if not a.size:return {"n":0,"median":None,"p95":None,"maximum":None}
    if not np.isfinite(a).all():
        raise ValueError("SOURCE_STOP_V80_COORDINATE_METRIC_NONFINITE")
    x=np.quantile(a,[.5,.95,1.])
    return {"n":int(len(a)),"median":float(x[0]),"p95":float(x[1]),
            "maximum":float(x[2])}

def valid_coords(lat,lon):
    return (np.isfinite(lat)&np.isfinite(lon)&
            (DEGREE_LAT[0]<=lat)&(lat<=DEGREE_LAT[1])&
            (DEGREE_LON[0]<=lon)&(lon<=DEGREE_LON[1]))

def _all_native_equal(a,b):
    return bool(np.array_equal(a,b,equal_nan=True))

def audit_month(ref_lat,ref_lon,lat,lon,header,filename):
    if any(a.shape!=NATIVE_SHAPE for a in (ref_lat,ref_lon,lat,lon)):
        raise ValueError("SOURCE_STOP_V80_DIMENSIONS_CHANGED")
    native_complete=(int(valid_coords(lat,lon).sum())==EXPECTED_CELLS)
    valid_pair=valid_coords(ref_lat,ref_lon)&valid_coords(lat,lon)
    distances=_haversine_m(
        ref_lat[valid_pair],ref_lon[valid_pair],
        lat[valid_pair],lon[valid_pair])
    return {
        "original_model_filename":filename,
        "source_variable_QA":header,
        "native_full_geographic_degree_valid":native_complete,
        "all_original_lat_at_same_native_array_indices_identical_to_2010_Jan":
            _all_native_equal(ref_lat,lat),
        "all_original_lon_at_same_native_array_indices_identical_to_2010_Jan":
            _all_native_equal(ref_lon,lon),
        "geographic_native_index_pairs_valid_in_both_months":int(valid_pair.sum()),
        "same_original_index_coordinate_displacement_metres":summaries(distances),
        "no_spatial_interpolation_or_imputation_performed":True}

def gauge_reference_qa(lat,lon):
    source=valid_coords(lat,lon)
    if int(source.sum())!=EXPECTED_CELLS:
        raise ValueError("SOURCE_STOP_V80_JAN_TEMPLATE_ORIGINAL_COORDINATES_BAD")
    gauges={}
    for name,(slat,slon) in STUDY_SITE_POINTS.items():
        distance=_haversine_m(lat[source],lon[source],slat,slon)
        gauges[name]={
            "genuine_original_Jan2010_nearest_native_cell_m":float(distance.min()),
            "genuine_original_Jan2010_cells_within_5km":int(np.sum(distance<=5000)),
            "public_station_source_geolocated":bool(
                distance.min()<=MAX_GAUGE_NEAREST_M and
                np.sum(distance<=5000)>=MIN_GAUGE_5KM_NATIVE_CELLS)}
    return gauges

def static_grid_decision(qa,gauges):
    complete=[f for f in MONTHS_2010
              if qa[f]["native_full_geographic_degree_valid"]]
    original_missing=[f for f in MONTHS_2010
                      if not qa[f]["native_full_geographic_degree_valid"]]
    coord_exact_complete=all(
        qa[f]["all_original_lat_at_same_native_array_indices_identical_to_2010_Jan"]
        and qa[f]["all_original_lon_at_same_native_array_indices_identical_to_2010_Jan"]
        for f in complete)
    missing_lat_and_lon_index_exact=all(
        qa[f]["source_variable_QA"]["lat"]["source_finite_count"]==0 and
        qa[f]["source_variable_QA"]["lon"]["source_finite_count"]==EXPECTED_CELLS and
        qa[f]["all_original_lon_at_same_native_array_indices_identical_to_2010_Jan"]
        for f in (f"eco_av.2010{m:02d}.nc" for m in MISSING_2010_MONTHS))
    expected_missing=set(f"eco_av.2010{m:02d}.nc" for m in MISSING_2010_MONTHS)
    identical_other=[
        f for f in PRESELECTED_OTHERYEAR if
        qa[f]["native_full_geographic_degree_valid"] and
        qa[f]["all_original_lat_at_same_native_array_indices_identical_to_2010_Jan"] and
        qa[f]["all_original_lon_at_same_native_array_indices_identical_to_2010_Jan"]]
    strong=(set(original_missing)==expected_missing and
            len(complete)==10 and coord_exact_complete and
            missing_lat_and_lon_index_exact and
            len(identical_other)>=MIN_OTHER_YEAR_COMPLETE_IDENTICAL and
            all(v["public_station_source_geolocated"] for v in gauges.values()))
    return {
        "original_2010_months_full_native_lat_lon":complete,
        "original_2010_months_without_full_native_lat_lon":original_missing,
        "all_ten_original_2010_complete_grid_coordinates_exact_same":coord_exact_complete,
        "original_2010_June_July_lat_all_missing_lon_each_index_exact_match":
            missing_lat_and_lon_index_exact,
        "all_frozen_preselected_external_year_months":list(PRESELECTED_OTHERYEAR),
        "original_external_year_complete_grid_months_matching_Jan2010":
            identical_other,
        "model_static_geo_template_SOURCE_ONLY_status":(
          "MODEL_STATIC_GRID_PROVENANCE_SUPPORTED_FOR_NEW_EXPLICIT_IMPUTATION_STUDY"
          if strong else
          "NOT_ADMITTED_STATIC_GRID_TEMPLATE_SOURCE"),
        "genuine_original_June_July_lat_values_were_observed":False,
        "imputed_JuneJuly_lat_values_created_or_released":False,
        "not_a_verified_independent_2010_terrain_or_wild_bird_effect":True}

def run(output):
    source=original_manifest()
    receipt={}
    native={}
    for filename in PUBLISHER_FILES:
        data,identity=authenticated_provider_file(source[filename])
        if filename in PRE_PINNED and identity["original_computed_sha256"]!=PRE_PINNED[filename]:
            raise ValueError("SOURCE_STOP_V80_PREVIOUS_PINNED_ORIGINAL_CHANGED")
        receipt[filename]={
            "original_publisher_MD5_and_bytes_verified":True,
            "original_publisher_sha256":identity["original_computed_sha256"],
            "original_file_bytes":identity["original_bytes"]}
        if filename!=README:
            lat,lon,header=read_native_geo(data,filename)
            native[filename]=(lat,lon,header)
            print("V80_NATIVE_ORIGINAL_MONTH_SOURCE "+
                  json.dumps({"name":filename,
                    "lat_finite":header["lat"]["source_finite_count"],
                    "lon_finite":header["lon"]["source_finite_count"],
                    "lat_masked":header["lat"]["original_masked_count"],
                    "lon_masked":header["lon"]["original_masked_count"]},
                    sort_keys=True),flush=True)
    reference_lat,reference_lon,_=native["eco_av.201001.nc"]
    month_qa={}
    for f in MONTHS_2010+PRESELECTED_OTHERYEAR:
        lat,lon,head=native[f]
        month_qa[f]=audit_month(reference_lat,reference_lon,
                                lat,lon,head,f)
    gauges=gauge_reference_qa(reference_lat,reference_lon)
    verdict=static_grid_decision(month_qa,gauges)
    result={
        "analysis":"V80_NIOZ_ORIGINAL_NATIVE_2010_STATIC_GRID_PRE_IMPUTATION_SOURCE_ONLY",
        "source_NIOZ_DOI":"10.25850/nioz/7b.b.n",
        "full_original_CKAN_36_month_manifest_verified":True,
        "publisher_original_MD5_SHA_and_source_bytes":receipt,
        "each_original_month_native_coordinate_QA_no_geo_pixels_exported":month_qa,
        "original_public_gauge_station_native_template_check":gauges,
        "frozen_static_template_provenance_decision":verdict,
        "no_GPS_RWS_timeseries_or_wild_animal_outcome_was_read":True,
        "historical_v78_Ameland_7_original_bird_gate_NOT_ADMITTED_unchanged":True,
        "future_2010_JuneJuly_native_geocoordinates_could_only_be_EXPLICIT_INFERRED_TEMPLATE":True}
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("V80_ORIGINAL_2010_MODEL_STATIC_NATIVE_MESH_DECISION "+
          json.dumps({
              "source_status":verdict["model_static_geo_template_SOURCE_ONLY_status"],
              "original_2010_full_geo_months":verdict["original_2010_months_full_native_lat_lon"],
              "original_source_months_without_genuine_lat":
                  verdict["original_2010_months_without_full_native_lat_lon"],
              "exact_coordinate_template_all_complete":
                  verdict["all_ten_original_2010_complete_grid_coordinates_exact_same"],
              "JuneJuly_original_lon_at_all_cell_indices_exact":
                  verdict["original_2010_June_July_lat_all_missing_lon_each_index_exact_match"],
              "independent_year_model_months_with_exact_template":
                  verdict["original_external_year_complete_grid_months_matching_Jan2010"],
              "stations_template_nearest_m":{
                   k:round(v["genuine_original_Jan2010_nearest_native_cell_m"],2)
                   for k,v in gauges.items()},
              "original_missing_lat_not_filled":True
          },sort_keys=True),flush=True)
    print("V80_AUTHENTIC_NIOZ_STATIC_GEO_MESH_SOURCE_AUDIT_COMPLETE",flush=True)
    return result

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--output",required=True)
    run(ap.parse_args().output)
