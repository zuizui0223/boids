"""v72: verified NIOZ monthly model \`time_expo\` native array and README source.

At v71 source level, authenticated Jan 2010/Jan 2011 NIOZ files contain only
820x486 monthly environmental grids, NO within-tide time series.
This script CANNOT infer instantaneous low-tide/daylight or GPS behavior.
This is an explicitly MODELLED exposure-source audit only.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import tempfile
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from original_coeval_wadden_model_metadata import (
    original_metadata,authenticated_provider_file,STUDY_SITE_POINTS)

FILENAMES=("README.txt","eco_av.201001.nc","eco_av.201101.nc")
FIXED_SHA={
    "README.txt":"4a273823ed9ea7925caccecf87b1d0220d8c4eeed25869cbb379c45de66e19ff",
    "eco_av.201001.nc":"f8df67d7351754173978364cd89afbf3a2bba4f3a4f85ef270b1090c14e72bad",
    "eco_av.201101.nc":"fb709111351182af3355730b100e41010a565dd92d12b26f6212356ccaa3e5da",
}
EXPECTED_SHAPE=(486,820)
GEO_NEAREST_METRES=2000
NEIGHBORHOOD_METRES=5000
METRICS=("count","minimum","p05","median","p95","maximum","zero_fraction")

def native_readme_meaning(raw):
    """Meaning must be in original README, not guessed from shape or range."""
    text=raw.decode("utf-8-sig")
    # Only the metadata needed to interpret the literal original variable;
    # cannot print full original source text in artifact or logs.
    lines=text.splitlines()
    candidates=[(i,line) for i,line in enumerate(lines)
                if "expo" in line.lower() or "latitude" in line.lower()]
    neighbors=[]
    for index,line in candidates:
        chunk=" ".join(lines[max(0,index-1):min(len(lines),index+2)])
        if "expo" in chunk.lower():
            neighbors.append((index,chunk))
    joined="\n".join(c for _,c in neighbors)
    s=joined.lower()
    has_literal="time_expo" in s
    has_exposure=("expos" in s)
    unit_hint={
        "proportion":bool(re.search(r"\bfraction\b|\bproportion\b|\bpercentage\b|\bpercent\b|%",s)),
        "hour":bool(re.search(r"\bhours?\b|\bhrs?\b",s)),
        "minute":bool(re.search(r"\bminutes?\b|\bmins?\b",s)),
        "second":bool(re.search(r"\bseconds?\b",s)),
    }
    unit_matches=[name for name,flag in unit_hint.items() if flag]
    if not has_literal or not has_exposure:
        status="NOT_ADMITTED_ORIGINAL_README_EXPOSURE_VARIABLE_UNDEFINED"
    elif len(unit_matches)!=1:
        status="NOT_ADMITTED_ORIGINAL_README_UNIT_UNKNOWN_OR_CONFLICTING"
    else:
        status="ORIGINAL_README_EXPLICIT_MODELED_EXPOSURE_"+unit_matches[0].upper()
    # Short line token fragments only (source document is separate).
    fragments=[{"original_readme_line_number":i+1,
                "source_terms_words_10":" ".join(line.split()[:10])}
               for i,line in candidates if "expo" in line.lower()][:6]
    return {
        "original_readme_lines":len(lines),
        "native_exposure_variable_literal_mentioned":has_literal,
        "native_exposure_word_documented":has_exposure,
        "unit_hints":unit_hint,
        "semantics_admission":status,
        "source_line_extracts_at_most_ten_words":fragments,
        "original_monthly_exposure_is_not_inst_tide_or_visible_light":True}

def _haversine_m(lat1,lon1,lat2,lon2):
    # vectorized many original model grid cell centers to public station coords
    earth=6371008.8
    dphi=np.deg2rad(lat2-lat1)
    dlambda=np.deg2rad(lon2-lon1)
    a=(np.sin(dphi/2)**2+
       np.cos(np.deg2rad(lat1))*np.cos(np.deg2rad(lat2))*
       np.sin(dlambda/2)**2)
    return 2*earth*np.arcsin(np.sqrt(np.clip(a,0,1)))

def _unmasked_numeric(variable):
    a=np.ma.asarray(variable[:],dtype=float)
    return np.ma.filled(a,np.nan).astype(float)

def original_native_month(raw,name):
    if name not in FILENAMES[1:]:
        raise ValueError("SOURCE_STOP_V72_UNFROZEN_ORIGINAL_NIOZ_MONTH")
    with tempfile.NamedTemporaryFile(mode="wb",suffix=".nc") as tmp:
        tmp.write(raw);tmp.flush()
        with Dataset(tmp.name,"r") as ds:
            if not {"lat","lon","time_expo"}.issubset(set(ds.variables)):
                raise ValueError("SOURCE_STOP_V72_ORIGINAL_NATIVE_EXPOSURE_FIELDS_ABSENT")
            lat=_unmasked_numeric(ds.variables["lat"])
            lon=_unmasked_numeric(ds.variables["lon"])
            expo=_unmasked_numeric(ds.variables["time_expo"])
            if (lat.shape!=EXPECTED_SHAPE or lon.shape!=EXPECTED_SHAPE
                or expo.shape!=EXPECTED_SHAPE):
                raise ValueError("SOURCE_STOP_V72_ORIGINAL_NIOZ_NATIVE_GRID_SHAPE_CHANGED")
    return lat,lon,expo

def _summarize_array(values):
    if not len(values):
        return {"count":0,"minimum":None,"p05":None,"median":None,
                "p95":None,"maximum":None,"zero_fraction":None}
    arr=np.asarray(values,float)
    if not np.isfinite(arr).all():
        raise ValueError("SOURCE_STOP_V72_NONFINITE_SAFE_AGGREGATE")
    p=np.quantile(arr,[0,.05,.5,.95,1])
    return dict(zip(METRICS,[int(len(arr)),float(p[0]),float(p[1]),
          float(p[2]),float(p[3]),float(p[4]),float(np.mean(arr==0))]))

def check_monthly_native_source(two_months,meaning):
    """Two fixed months, original numeric spatial match; no bird behavior."""
    first=two_months["eco_av.201001.nc"]
    second=two_months["eco_av.201101.nc"]
    a,b,z0=first
    c,d,z1=second
    valid_degrees=np.isfinite(a)&np.isfinite(b)&(a>=48)&(a<=57)&(b>=2)&(b<=10)
    n_geocoords=int(valid_degrees.sum())
    if n_geocoords<10000:
        raise ValueError("SOURCE_STOP_V72_NIOZ_LAT_LON_NOT_NATIVE_DEGREES")
    consistent=(np.array_equal(a,c,equal_nan=True)
                and np.array_equal(b,d,equal_nan=True))
    if not consistent:
        raise ValueError("SOURCE_STOP_V72_DIFFERENT_SOURCE_NATIVE_GRIDS")
    reported={}
    fixed_ok=(meaning["semantics_admission"].startswith(
        "ORIGINAL_README_EXPLICIT_MODELED_EXPOSURE_"))
    months={}
    for name,values in (("eco_av.201001.nc",z0),("eco_av.201101.nc",z1)):
        finite=np.isfinite(values)
        accepted=finite&valid_degrees
        negative=int((accepted&(values<0)).sum())
        beyond_744h=int((accepted&(values>744)).sum())
        nonnegative=accepted&(values>=0)
        months[name]={
            "original_all_grid_cells":int(values.size),
            "original_numeric_positive_valid_degree_georeference_cells":int(nonnegative.sum()),
            "original_nonfinite_nodata_source_cells":int((~finite).sum()),
            "original_invalid_lat_lon_or_nonfinite_cells":int((~accepted).sum()),
            "original_negative_numeric_values_not_silently_removed":negative,
            "original_above_744_number_NOT_assumed_hours":beyond_744h,
            "original_native_numeric_nonnegative_expo_distribution_UNITS_UNVERIFIED":
                _summarize_array(values[nonnegative])}
    for label,(lat,lon) in STUDY_SITE_POINTS.items():
        km=_haversine_m(a[valid_degrees],b[valid_degrees],lat,lon)
        nearest=float(km.min())
        ring=np.zeros(a.shape,bool)
        ring[valid_degrees]=km<=NEIGHBORHOOD_METRES
        common=ring&np.isfinite(z0)&np.isfinite(z1)&(z0>=0)&(z1>=0)
        delta=z1[common]-z0[common]
        reported[label]={
            "nearest_original_native_model_cell_center_m":nearest,
            "original_geographic_grid_cells_within_5km":int(ring.sum()),
            "original_both_years_monthly_model_numeric_nonnegative_cells_5km":int(common.sum()),
            "2010_original_model_exposure_numeric_UNITS_UNVERIFIED":
                _summarize_array(z0[common]),
            "2011_original_model_exposure_numeric_UNITS_UNVERIFIED":
                _summarize_array(z1[common]),
            "2011_minus_2010_model_pixel_value_UNITS_UNVERIFIED":
                _summarize_array(delta),
            "proportion_common_pixels_2011_greater_than_2010":
                float(np.mean(delta>0)) if len(delta) else None,
            "proportion_common_pixels_2011_less_than_2010":
                float(np.mean(delta<0)) if len(delta) else None}
    geographically_ok=all(
        r["nearest_original_native_model_cell_center_m"]<=GEO_NEAREST_METRES
        and r["original_both_years_monthly_model_numeric_nonnegative_cells_5km"]>=50
        for r in reported.values())
    if not fixed_ok:
        admission="NOT_ADMITTED_SOURCE_NATIVE_EXPOSURE_UNITS_OR_SEMANTICS_UNVERIFIED"
    elif not geographically_ok:
        admission="NOT_ADMITTED_SOURCE_NATIVE_SPATIAL_OR_MODEL_VALID_SUPPORT"
    else:
        admission="SOURCE_ONLY_MODELED_MONTHLY_EXPOSURE_MAP_FOR_FUTURE_GPS_JOIN"
    return {
        "native_NIOZ_months":["201001","201101"],
        "source_geographic_cells_with_latlon_in_degrees":n_geocoords,
        "original_2010_2011_lat_lon_arrays_identical_numeric":consistent,
        "source_site_neighborhoods":reported,
        "source_monthly_pixel_variable_numerical_quality":months,
        "native_README_metadata_semantics":meaning,
        "modelled_monthly_exposure_source_admission":admission,
        "no_actual_tidal_phase_or_daily_sunlit_exposure_in_monthly_grid":True,
        "no_original_bird_GPS_perfix_source_or_outcome_used":True}

def run(output):
    meta=original_metadata()
    raw={}
    digests={}
    for filename in FILENAMES:
        orig,receipt=authenticated_provider_file(
            meta["source_original_resources"][filename])
        if receipt["original_computed_sha256"]!=FIXED_SHA[filename]:
            raise ValueError("SOURCE_STOP_V72_IMMUTABLE_V71_PUBLISHED_ORIGINAL_CHANGED")
        raw[filename]=orig
        digests[filename]=receipt
    meaning=native_readme_meaning(raw["README.txt"])
    original_native={name:original_native_month(raw[name],name)
                     for name in FILENAMES[1:]}
    qa=check_monthly_native_source(original_native,meaning)
    report={
        "analysis":"V72_ORIGINAL_NIOZ_MODELED_MONTHLY_INTERTIDAL_EXPOSURE_NATIVE_GRID_SOURCE",
        "original_doi":"10.25850/nioz/7b.b.n",
        "original_provider_manifest":meta["method"],
        "original_provider_MD5_and_SHA_receipts":digests,
        "original_native_model_spatial_exposure":qa,
        "original_model_not_original_observed_field":True,
        "v71_per_tide_phase_time_resolution_not_admitted_and_unaltered":True,
        "no_original_wild_GPS_2010_2011_heading_or_foraging_effect_scored":True,
        "data_dependent_unit_rescue_or_new_month_selection_forbidden":True}
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("V72_NIOZ_NATIVE_EXPOSURE_AND_SOURCE_MEANING "+json.dumps({
        "readme_semantic_status":meaning["semantics_admission"],
        "source_grid_identical":qa["original_2010_2011_lat_lon_arrays_identical_numeric"],
        "true_original_degree_cells":qa["source_geographic_cells_with_latlon_in_degrees"],
        "site_min_distance_m":{
            s:round(x["nearest_original_native_model_cell_center_m"],1)
            for s,x in qa["source_site_neighborhoods"].items()},
        "site_same_native_grids_valid_2010_2011_cells":{
            s:x["original_both_years_monthly_model_numeric_nonnegative_cells_5km"]
            for s,x in qa["source_site_neighborhoods"].items()},
        "model_exposure_geospatial_source_admission":
            qa["modelled_monthly_exposure_source_admission"]},
        sort_keys=True),flush=True)
    print("V72_ORIGINAL_MODELED_MONTHLY_EXPOSURE_SOURCE_AUDIT_COMPLETE",flush=True)
    return report

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    x=p.parse_args()
    run(x.output)
