"""v72D after frozen primary v72 original coordinate mismatch: SOURCE-ONLY audit.

No new time-of-day tidal model, no actual bird tracking, no spatial matching
to rescue primary source acceptance. Source pixels stay only on runner.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from original_coeval_wadden_model_metadata import (
    original_metadata,authenticated_provider_file,STUDY_SITE_POINTS)
from native_monthly_exposure_source import (
    FIXED_SHA,native_readme_meaning,original_native_month,_haversine_m)

DEGREE_VALID_LAT=(48.,57.)
DEGREE_VALID_LON=(2.,10.)
ORIGINAL_NAMES=("README.txt","eco_av.201001.nc","eco_av.201101.nc")
DIAGNOSTIC_DISTANCE_M=(1.,10.,100.)
def quantile(a):
    if not len(a):return {"n":0,"median":None,"p90":None,"p99":None,"max":None}
    b=np.quantile(np.asarray(a,float),[.5,.9,.99,1.])
    return {"n":int(len(a)),"median":float(b[0]),"p90":float(b[1]),
            "p99":float(b[2]),"max":float(b[3])}

def geo_valid(lat,lon):
    return (np.isfinite(lat)&np.isfinite(lon)&
            (DEGREE_VALID_LAT[0]<=lat)&(lat<=DEGREE_VALID_LAT[1])&
            (DEGREE_VALID_LON[0]<=lon)&(lon<=DEGREE_VALID_LON[1]))

def diagnostic(first,second,meaning):
    lat0,lon0,expo0=first;lat1,lon1,expo1=second
    if (lat0.shape!=lat1.shape or lon0.shape!=lon1.shape or
        lat0.shape!=lon0.shape or lat0.shape!=expo0.shape or
        lat1.shape!=expo1.shape):
        raise ValueError("SOURCE_STOP_V72D_ORIGINAL_SHAPE_DRIFT")
    v0=geo_valid(lat0,lon0)
    v1=geo_valid(lat1,lon1)
    both=v0&v1
    if not both.any():
        # Post-failure *diagnosis only*: native lat/lon could have radians,
        # projected units, fill values, or land masking. Do NOT transform
        # without a separately frozen source-CRS method/README evidence.
        def raw_ranges(values):
            good=values[np.isfinite(values)]
            if not len(good):return {"finite":0}
            return {"finite":int(len(good)),"min":float(good.min()),
                    "median":float(np.median(good)),
                    "max":float(good.max())}
        print("V72D_ORIGINAL_SOURCE_NATIVE_COORDINATE_RANGES_NOT_CRS_ADMISSION "+json.dumps({
            "2010_lat":raw_ranges(lat0),"2010_lon":raw_ranges(lon0),
            "2011_lat":raw_ranges(lat1),"2011_lon":raw_ranges(lon1),
            "2010_degree_valid_cells":int(v0.sum()),
            "2011_degree_valid_cells":int(v1.sum())},sort_keys=True),flush=True)
        raise ValueError("SOURCE_STOP_V72D_NO_COMMON_GEO")
    distance=_haversine_m(lat0[both],lon0[both],
                          lat1[both],lon1[both])
    # Exact condition from v72, never changed.
    strict=(np.array_equal(lat0,lat1,equal_nan=True)
            and np.array_equal(lon0,lon1,equal_nan=True))
    site={}
    for label,(lat,lon) in STUDY_SITE_POINTS.items():
        d0=_haversine_m(lat0[v0],lon0[v0],lat,lon)
        d1=_haversine_m(lat1[v1],lon1[v1],lat,lon)
        site[label]={"original_2010_nearest_cell_center_m":float(d0.min()),
                     "original_2011_nearest_cell_center_m":float(d1.min()),
                     "original_2010_cells_within_5km":int((d0<=5000).sum()),
                     "original_2011_cells_within_5km":int((d1<=5000).sum())}
    return {
        "analysis":"V72D_POST_V72_GRID_SOURCE_MISMATCH_DIAGNOSTIC_ONLY",
        "original_cells_total":int(lat0.size),
        "2010_original_degree_valid_latlon_cells":int(v0.sum()),
        "2011_original_degree_valid_latlon_cells":int(v1.sum()),
        "both_original_months_degree_valid_same_array_indices":int(both.sum()),
        "one_year_only_native_geo_cells":int((v0^v1).sum()),
        "original_both_months_same_index_displacement_m":quantile(distance),
        "source_pairs_with_displacement_m_at_most_fixed_diagnostic":{
            str(thr):int((distance<=thr).sum())
            for thr in DIAGNOSTIC_DISTANCE_M},
        "fraction_source_pairs_at_most_fixed_diagnostic":{
            str(thr):float(np.mean(distance<=thr))
            for thr in DIAGNOSTIC_DISTANCE_M},
        "exact_lat_lon_all_native_array_indices_equal_unmodified":bool(strict),
        "native_geographic_reference_station_neighbors":site,
        "original_publisher_README_model_exposure_semantics":meaning,
        "frozen_v72_strict_source_admission_status":(
            "STILL_NOT_ADMITTED_V72_STRICT_SAME_GRID_FAILURE"
            if not strict else "STRICT_SAME_GRID_PASS_REQUIRES_SEPARATE_V72_FULL_GATE"),
        "source_diagnostics_not_an_allowed_matching_tolerance":True,
        "never_fits_wild_bird_GPS_or_interpolates_source_rasters":True}

def run(output):
    meta=original_metadata()
    content={}
    receipts={}
    for name in ORIGINAL_NAMES:
        raw,proof=authenticated_provider_file(meta["source_original_resources"][name])
        if proof["original_computed_sha256"]!=FIXED_SHA[name]:
            raise ValueError("SOURCE_STOP_V72D_ORIGINAL_NIOZ_V71_SHA_CHANGED")
        content[name]=raw
        receipts[name]={"original_provider_md5_match":True,
                        "source_SHA256":proof["original_computed_sha256"]}
    meaning=native_readme_meaning(content["README.txt"])
    first=original_native_month(content["eco_av.201001.nc"],"eco_av.201001.nc")
    second=original_native_month(content["eco_av.201101.nc"],"eco_av.201101.nc")
    report=diagnostic(first,second,meaning)
    report["original_source_verified_provider_hashes"]=receipts
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("V72D_NIOZ_SOURCE_COORDINATE_MISMATCH "+json.dumps({
        "v72_status":report["frozen_v72_strict_source_admission_status"],
        "model_exposure_readme_status":meaning["semantics_admission"],
        "original_geo_grid_2010":report["2010_original_degree_valid_latlon_cells"],
        "original_geo_grid_2011":report["2011_original_degree_valid_latlon_cells"],
        "both_years_valid":report["both_original_months_degree_valid_same_array_indices"],
        "native_displacement_m":report["original_both_months_same_index_displacement_m"],
        "fixed_1_10_100m_counts":report["source_pairs_with_displacement_m_at_most_fixed_diagnostic"]
    },sort_keys=True),flush=True)
    print("V72D_ORIGINAL_NIOZ_GRID_DIAGNOSTIC_COMPLETED",flush=True)
    return report

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    a=p.parse_args();run(a.output)
