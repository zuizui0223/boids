"""v81 original NIOZ Ameland 2010 June-Dec, source-templated coordinates.

CRITICAL: June/July NIOZ lat is wholly masked in the original publisher
files. ONLY reuse Jan2010 exact native mesh latitude as EXPLICIT MODEL GRID
TEMPLATE INFERENCE, after original lon has exactly identical array indices and
2009 original exact mesh independent model checks. Never pretend original
June/July model lat existed, or modelled monthly time_expo is measured hours.
"""
from __future__ import annotations

import hashlib
import tempfile
import numpy as np
from pathlib import Path
from netCDF4 import Dataset
from scipy.spatial import cKDTree

from original_nioz_static_2010_grid import read_native_geo
from original_coeval_wadden_model_metadata import authenticated_provider_file
from native_monthly_exposure_source import _haversine_m
from wild_2010_modelled_tidal_exposure_rank import _locxy

MONTHS_V81=(6,7,8,9,10,11,12)
ORIGINAL_INFERRED_MONTHS=(6,7)
EXACT_MODEL_SHAS={
 "README.txt":"4a273823ed9ea7925caccecf87b1d0220d8c4eeed25869cbb379c45de66e19ff",
 "eco_av.200901.nc":"15d50a824e699144b47071bbe6b87038c7a3fc8e20d747db16c347e0065a3bb4",
 "eco_av.200908.nc":"f34a07d6f9d80a3bd1e90a4b0a8a17231ccdf8fd3406720eb86942bd07977df8",
 "eco_av.201001.nc":"f8df67d7351754173978364cd89afbf3a2bba4f3a4f85ef270b1090c14e72bad",
 "eco_av.201006.nc":"9d32caeda98fb5be6096b60ada49fd4109b9cf076f406451ffbe5ff3899ef952",
 "eco_av.201007.nc":"cec6d7f6d636b1005068aa05fef2ecaa39ce768c577a37d35612ce7604d33210",
 "eco_av.201008.nc":"0eacaa4b2a246ea89ed0a032be588fc77f7af630e183b4c73236104392b46ece",
 "eco_av.201009.nc":"61d3703efab9e8ba137aa99bd310368431fd9dcf5a8faed2fd6a82f1b86e4053",
 "eco_av.201010.nc":"4e2d9f53bcd6fa14da03e46b3fe0f51754e78d59e0efdebf50cf9707edd6b321",
 "eco_av.201011.nc":"093368f931a666a1d74591e481386801026160c0a6dc8bcf09fcf74ccd9bedfb",
 "eco_av.201012.nc":"a05182cacaa5473de167386d6c71f3da94ede515845cc84775c14ca2c5a62161"}
NATIVE_SHAPE=(486,820)
TOTAL_NATIVE_CELLS=398520
SITES_PUBLIC={
 "Schiermonnikoog":(53.46894,6.20291),
 "Ameland Nes":(53.42977,5.75945)}

def _array(var):
    return np.ma.filled(np.ma.asarray(var[:],dtype=float),np.nan).astype(float)

def actual_nioz_model_native(raw,filename):
    if filename not in EXACT_MODEL_SHAS or not filename.endswith(".nc"):
        raise ValueError("SOURCE_STOP_V81_UNFROZEN_NIOZ_MONTH")
    with tempfile.NamedTemporaryFile(suffix=".nc",mode="wb") as f:
        f.write(raw);f.flush()
        with Dataset(f.name,"r") as nc:
            if not {"lat","lon","time_expo"}.issubset(nc.variables):
                raise ValueError("SOURCE_STOP_V81_NIOZ_ORIGINAL_FIELDS_MISSING")
            lat,lon,x=(_array(nc.variables[k]) for k in ("lat","lon","time_expo"))
            if any(v.shape!=NATIVE_SHAPE for v in (lat,lon,x)):
                raise ValueError("SOURCE_STOP_V81_NATIVE_NIOZ_GRID_SHAPE_CHANGED")
    return lat,lon,x

def _full_native_lat_lon(lat,lon):
    return bool(lat.shape==NATIVE_SHAPE and lon.shape==NATIVE_SHAPE and
        np.isfinite(lat).all() and np.isfinite(lon).all() and
        ((48<=lat)&(lat<=57)).all() and ((2<=lon)&(lon<=10)).all())

def _exact(a,b):
    return bool(np.array_equal(a,b,equal_nan=True))

def authenticated_template_and_model_months(publisher,*,loader=authenticated_provider_file):
    """All original bytes publisher-MD5+original SHA rechecked in same run."""
    files={}
    receipts={}
    for filename in EXACT_MODEL_SHAS:
        if filename not in publisher:
            raise ValueError("SOURCE_STOP_V81_PUBLISHER_ORIGINAL_MONTH_MISSING")
        raw,r=loader(publisher[filename])
        if r["original_computed_sha256"]!=EXACT_MODEL_SHAS[filename]:
            raise ValueError("SOURCE_STOP_V81_PREVIOUS_V80_ORIGINAL_SHA_DRIFT")
        files[filename]=raw
        receipts[filename]={
            "original_source_SHA256":r["original_computed_sha256"],
            "original_provider_MD5_and_byte_count_verified":True}
    lat_template,lon_template,readme_unused=actual_nioz_model_native(
        files["eco_av.201001.nc"],"eco_av.201001.nc")
    if not _full_native_lat_lon(lat_template,lon_template):
        raise ValueError("SOURCE_STOP_V81_JAN_2010_REAL_NATIVE_TEMPLATE_FAILED")
    for control in ("eco_av.200901.nc","eco_av.200908.nc"):
        l,o,_=actual_nioz_model_native(files[control],control)
        if not (_full_native_lat_lon(l,o) and _exact(l,lat_template)
                and _exact(o,lon_template)):
            raise ValueError("SOURCE_STOP_V81_INDEPENDENT_2009_GRID_NOT_EXACT")
    gauges={}
    for label,(lat,lon) in SITES_PUBLIC.items():
        distances=_haversine_m(lat_template,lon_template,lat,lon)
        d=float(distances.min())
        if d>200:
            raise ValueError("SOURCE_STOP_V81_REAL_NATIVE_TEMPLATE_WRONG_STATION")
        gauges[label]={"genuine_Jan_2010_native_model_nearest_center_m":d}
    spatial={}
    source={}
    for month in MONTHS_V81:
        filename=f"eco_av.2010{month:02d}.nc"
        lat,lon,expo=actual_nioz_model_native(files[filename],filename)
        if not (_exact(lon,lon_template) and np.isfinite(lon).all()):
            raise ValueError("SOURCE_STOP_V81_NATIVE_LON_INDEX_NOT_STATIC")
        if (not np.isfinite(expo).all() or not
            ((0<=expo)&(expo<=1)).all() or
            len(np.unique(np.round(expo,8)))<10):
            raise ValueError("SOURCE_STOP_V81_ORIGINAL_MODEL_INDEX_OUT_OF_RANGE_OR_CONSTANT")
        if month in ORIGINAL_INFERRED_MONTHS:
            if np.isfinite(lat).any():
                raise ValueError("SOURCE_STOP_V81_EXPECTED_ORIGINAL_JUNE_JULY_MASK_CHANGED")
            # This is the ONLY explicitly inferred original MODEL grid
            # coordinate, not a recovery of actual source metadata.
            source_lat=lat_template
            mode="EXPLICIT_INFERRED_MODEL_STATIC_MESH_LAT_FROM_REAL_JAN2010"
            genuine_native_latitude=False
        else:
            if not(_full_native_lat_lon(lat,lon) and _exact(lat,lat_template)):
                raise ValueError("SOURCE_STOP_V81_NATIVE_AUG_DEC_LAT_GRID_NOT_EXACT")
            source_lat=lat
            mode="GENUINE_ORIGINAL_NATIVE_2010_MODEL_LAT_LON"
            genuine_native_latitude=True
        xy=_locxy(source_lat.ravel(),lon.ravel())
        source[month]={
            "xy":xy,
            "index":expo.ravel(),
            "n_native":TOTAL_NATIVE_CELLS,
            "tree":cKDTree(xy)}
        spatial[month]={
            "source_month":month,
            "source_original_NIOZ_file":filename,
            "original_actual_lat_nonmissing_cells":int(np.isfinite(lat).sum()),
            "original_actual_lon_nonmissing_cells":int(np.isfinite(lon).sum()),
            "original_model_index_finite_cells":int(np.isfinite(expo).sum()),
            "source_model_index_distinct_numeric_values":int(
                len(np.unique(np.round(expo,8)))),
            "original_jun_jul_native_lat_was_not_observed":not genuine_native_latitude,
            "model_spatial_reference_mode":mode,
            "2010_static_model_template_lat_explictly_inferred_not_measured":
                not genuine_native_latitude}
    return source,{
        "analysis":"V81_ORIGINAL_NIOZ_STATIC_MODEL_NATIVE_SOURCING_WITH_EXPLICIT_JUN_JUL_TEMPLATE",
        "original_model_source_sha_and_provider_certificates":receipts,
        "original_2010_Jan_and_2009_Jan_Aug_exact_grid_provenance_verified":True,
        "original_public_station_reference_checks":gauges,
        "original_month_specific_spatial_source":spatial,
        "original_month_2010_JunJul_lat_remains_missing_and_is_only_INFERRED":True,
        "source_model_units_UNKNOWN_monthly_not_hours":True,
        "no_wild_original_bird_used_index_or_measured_tide_consulted":True}
