"""v84: public WMR mid/high-littoral polygons -> original Jan2010 NIOZ source GRID.

Corrected 2021 Mendeley v2 original GPKG could not be obtained via
public official API (401). WMR official WS3 WFS native \`litoralcode\`
is accessible, BUT version not certified equal to corrected v2. The
v1 problem affected only the shallow sublittoral / LOW-littoral (code2)
boundary, so preregistered MID/HIGH littoral codes3,4 ONLY, still
labelled version-uncertain published ecological map.
SOURCE ONLY: NO birds, real tide series, GPS origin or habitat-use ranks.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
import json,math,os

import numpy as np
from shapely.geometry import shape
import shapely
from shapely import STRtree
from scipy.spatial import cKDTree

from original_coeval_wadden_model_metadata import (
    original_metadata,authenticated_provider_file)
from authenticated_nioz_static_template_model import (
    actual_nioz_model_native,EXACT_MODEL_SHAS)
from wild_2010_modelled_tidal_exposure_rank import _locxy
from wmr_geoserver_ecotope_source_probe import (
    BASE,MAIN,SourceUnavailable,native_capabilities,native_schema,
    bounded_request as original_wfs)
from native_monthly_exposure_source import _haversine_m

FIXED_SITE_BBOX={
    "Schiermonnikoog":(5.70,53.20,6.60,53.70),
    "Ameland_Nes":(5.30,53.20,6.10,53.60)}
FIXED_PUBLIC_GAUGE={
    "Schiermonnikoog":(53.46894,6.20291),
    "Ameland_Nes":(53.42977,5.75945)}
FIXED_CODES=(3,4)
SOURCE_LOWER_LITTORAL_CODE_NEVER_USED=2
NIOZ_JAN_2010="eco_av.201001.nc"
NIOZ_ORIGINAL_SHA=EXACT_MODEL_SHAS[NIOZ_JAN_2010]
MAX_PER_SITE=5000
MAX_GEOJSON_BYTES=55_000_000
MAX_INVALID_POLYGON_PERCENT=1.
MAX_CONFLICT_PERCENT=1.
SOURCE_MIN_GRID_CELLS_PER_SITE=100
METRIC_X=math.cos(math.radians(53.45))*111195.
METRIC_Y=111195.
MIDHIGH_SOURCE_STATUS="SOURCE_ADMITTED_V84_ORIGINAL_WMR_WS3_PUBLISHER_MIDHIGH_LITTORAL_ONLY_VERSION_UNVERIFIED"

class SourceStop(Exception):pass

def _wfs_region(site,bbox,*,fetch=original_wfs):
    if site not in FIXED_SITE_BBOX or tuple(bbox)!=FIXED_SITE_BBOX[site]:
        raise SourceStop("SOURCE_STOP_V84_WFS_SOURCE_BBOX_CHANGED")
    request={
        "request":"GetFeature",
        "typeNames":MAIN,
        "count":str(MAX_PER_SITE),
        "outputFormat":"application/json",
        "srsName":"CRS:84",
        "bbox":",".join(f"{v:.5f}" for v in bbox)+",CRS:84",
        "CQL_FILTER":"litoralcode IN (3,4)"}
    try:
        raw=fetch(request,limit=MAX_GEOJSON_BYTES)
        collection=json.loads(raw)
    except (HTTPError,URLError,ValueError,TypeError) as e:
        raise SourceStop("SOURCE_UNAVAILABLE_V84_ORIGINAL_WMR_WFS_REGION "+str(e)[:180]) from e
    if not isinstance(collection,dict) or not isinstance(collection.get("features"),list):
        raise SourceStop("SOURCE_STOP_V84_ORIGINAL_WFS_NOT_A_GEOJSON_FEATURECOLLECTION")
    features=collection["features"]
    if len(features)>=MAX_PER_SITE:
        raise SourceStop("SOURCE_STOP_V84_WFS_MAY_BE_TRUNCATED_MAX5000")
    number_matched=collection.get("numberMatched")
    if isinstance(number_matched,(str,int)) and str(number_matched).isdigit():
        if int(number_matched)>len(features):
            raise SourceStop("SOURCE_STOP_V84_WFS_ORIGINAL_MORE_POLYGONS_THAN_RETURNED")
    out=[]
    count=Counter()
    invalid=0
    for feature in features:
        props=feature.get("properties") or {}
        value=props.get("litoralcode")
        if value is None:
            raise SourceStop("SOURCE_STOP_V84_WMR_NATIVE_LITORALCODE_NULL")
        try:code=int(value)
        except (ValueError,TypeError):
            raise SourceStop("SOURCE_STOP_V84_NATIVE_WFS_CLASS_NOT_INTEGER")
        if code not in FIXED_CODES:
            raise SourceStop("SOURCE_STOP_V84_WMR_SERVER_FILTER_RETURNED_OUTSIDE_MIDHIGH")
        source=feature.get("geometry")
        if not isinstance(source,dict):
            raise SourceStop("SOURCE_STOP_V84_NO_POLYGON_GEOMETRY")
        geom=shape(source)
        if geom.geom_type not in ("Polygon","MultiPolygon") or geom.is_empty:
            raise SourceStop("SOURCE_STOP_V84_POLYGON_SOURCE_GEOMETRY_INVALID")
        lonmin,latmin,lonmax,latmax=geom.bounds
        if not(4<=lonmin<=lonmax<=10 and 52<=latmin<=latmax<=56):
            raise SourceStop("SOURCE_STOP_V84_NATIVE_GEOJSON_NOT_IN_WADDEN_LAT_LON")
        if not geom.is_valid:
            invalid+=1
            geom=shapely.make_valid(geom)
            if geom.is_empty:
                raise SourceStop("SOURCE_STOP_V84_INVALID_UNREPAIRABLE_POLYGON")
        if geom.geom_type=="GeometryCollection":
            parts=[g for g in geom.geoms
                   if g.geom_type in ("Polygon","MultiPolygon")]
            if not parts:
                raise SourceStop("SOURCE_STOP_V84_GEO_POLYGON_REPAIR_FAILED")
            geom=shapely.union_all(parts)
        if geom.geom_type not in ("Polygon","MultiPolygon"):
            raise SourceStop("SOURCE_STOP_V84_GEO_POLYGON_SOURCE_NOT_AREA")
        transformed=shapely.transform(
            geom,lambda coords:coords*np.array([METRIC_X,METRIC_Y]))
        out.append((transformed,code))
        count[code]+=1
    invalid_pct=100*invalid/len(out) if out else 100
    if not out or invalid_pct>MAX_INVALID_POLYGON_PERCENT:
        raise SourceStop("SOURCE_STOP_V84_TOO_FEW_OR_TOO_MANY_INVALID_WMR_POLYGONS")
    receipt={
        "original_public_WMR_WFS_source_layer":MAIN,
        "site":site,
        "actual_received_full_geojson_polygons":len(out),
        "original_publisher_declared_geometries_matched":
            str(number_matched) if number_matched is not None else "not_reported",
        "published_original_mid_littoral3_polygon_count":count[3],
        "published_original_high_littoral4_polygon_count":count[4],
        "original_invalid_geometry_fixed_for_source_only":invalid,
        "original_source_region_geojson_SHA256_COMPUTED_NOT_PROVIDER_HASH":
            sha256(raw).hexdigest(),
        "original_WFS_polygon_version2021_CORRECTED_V2_NOT_VERIFIED":True,
        "native_WFS_code2_low_littoral_NEVER_USED":True}
    return out,receipt

def _native_original_Jan2010_grid():
    meta=original_metadata()
    if NIOZ_JAN_2010 not in meta["source_original_resources"]:
        raise SourceStop("SOURCE_STOP_V84_NIOZ_PUBLISHED_JAN2010_NOT_FOUND")
    raw,proof=authenticated_provider_file(
        meta["source_original_resources"][NIOZ_JAN_2010])
    if proof["original_computed_sha256"]!=NIOZ_ORIGINAL_SHA:
        raise SourceStop("SOURCE_STOP_V84_ORIGINAL_2010_NIOZ_SHA_CHANGED")
    la,lo,ex=actual_nioz_model_native(raw,NIOZ_JAN_2010)
    if la.shape!=(486,820) or not np.isfinite(la).all() or not np.isfinite(lo).all():
        raise SourceStop("SOURCE_STOP_V84_NIOZ_NATIVE_JAN_COORDINATES_MISSING")
    return la.ravel(),lo.ravel(),{
        "source_NIOZ_original_file":NIOZ_JAN_2010,
        "source_original_PROVIDER_MD5_verified":True,
        "source_original_Jan2010_SHA256":proof["original_computed_sha256"],
        "source_original_grid_center_count":len(la.ravel()),
        "source_original_model_real_lat_lon_not_inferred":True,
        "original_native_model_index_VALUES_NOT_READ_OR_SCORED":True}

def _overlay_model_centers(native_lat,native_lon,polygons,site):
    """Use original NIOZ source native 200m grid, no GPS and no model exposure values."""
    src_bbox=FIXED_SITE_BBOX[site]
    in_box=(native_lon>=src_bbox[0])&(native_lon<=src_bbox[2])&(
        native_lat>=src_bbox[1])&(native_lat<=src_bbox[3])
    indices=np.flatnonzero(in_box)
    if not len(indices):
        raise SourceStop("SOURCE_STOP_V84_NIOZ_NATIVE_GRID_OUTSIDE_SITE")
    xy=_locxy(native_lat[indices],native_lon[indices])
    points=shapely.points(xy)
    tree=STRtree([poly for poly,code in polygons])
    pairs=tree.query(points,predicate="intersects")
    classes=np.zeros(len(indices),dtype=np.uint8)
    conflicts=np.zeros(len(indices),dtype=bool)
    for pt,poly in zip(pairs[0],pairs[1]):
        code=polygons[int(poly)][1]
        prev=int(classes[pt])
        if prev and prev!=code:
            conflicts[pt]=True
        elif not prev:
            classes[pt]=code
    classes[conflicts]=0
    n_candidates=int(np.sum(classes>0))
    conflicting=int(np.sum(conflicts))
    if n_candidates and 100*conflicting/(n_candidates+conflicting)>MAX_CONFLICT_PERCENT:
        raise SourceStop("SOURCE_STOP_V84_MID_HIGH_ECOTOPE_CLASSES_SPATIAL_OVERLAP_CONFLICT")
    center=FIXED_PUBLIC_GAUGE[site]
    distances=_haversine_m(
        native_lat[indices],native_lon[indices],center[0],center[1])
    near=distances<=5000.
    receipt={
        "site":site,
        "original_NIOZ_native_grid_cells_within_FIXED_GPS_SITE_BOX":len(indices),
        "WMR_original_code3_mid_littoral_NATIVE_2010_model_center_count":
            int(np.sum(classes==3)),
        "WMR_original_code4_high_littoral_NATIVE_2010_model_center_count":
            int(np.sum(classes==4)),
        "mid_high_littoral_NATIVE_2010_model_centers_source_only":
            n_candidates,
        "native_Jan2010_model_centers_near_public_gauge_5km":
            int(np.sum(near)),
        "native_original_model_mid_high_littoral_centers_near_gauge_5km":
            int(np.sum(near&(classes>0))),
        "native_original_WMR_mid_vs_high_conflicting_model_centers":
            conflicting,
        "source_mapping_only_no_GPS_or_NIOZ_time_expo_values":True}
    return receipt

def run(output):
    report={
        "analysis":"V84_ORIGINAL_WMR_PUBLIC_MIDHIGH_LITTORAL_CLASS3_4_TO_NIOZ_2010_NATIVE_GRID_SOURCE",
        "published_WMR_OGC_source":BASE,
        "source_is_2008_2012_COMPOSITE_not_pixel_2010_observation":True,
        "original_Mendeley_corrected_2021_V2_source_still_401_UNAVAILABLE":True,
        "WMR_WS3_publisher_polygon_version2021_CORRECTED_V2_UNVERIFIED":True,
        "lower_littoral_code2_NOT_in_this_robustness_mask":True,
        "original_animal_GPS_or_RWS_tide_not_read":True}
    try:
        original_schema=native_schema(original_wfs(
            {"request":"DescribeFeatureType","typeNames":MAIN},limit=1_000_000))
        native_fields={f["source_field"] for f in
                       original_schema["source_original_schema_fields"]}
        if not {"litoralcode","dynamiccode"}.issubset(native_fields):
            raise SourceStop("SOURCE_STOP_V84_WMR_NATIVE_CLASS_FIELDS_MISSING")
        report["original_WMR_WFS_schema_fields_checked"]=[
            "litoralcode","dynamiccode"]
        native_lat,native_lon,nativeproof=_native_original_Jan2010_grid()
        report["original_NIOZ_Jan2010_provider_source"]=nativeproof
        source={}
        footprints={}
        for site,bbox in FIXED_SITE_BBOX.items():
            polygons,source[site]=_wfs_region(site,bbox)
            footprints[site]=_overlay_model_centers(
                native_lat,native_lon,polygons,site)
            print("V84_REAL_WMR_MIDHIGH_LITTORAL_SOURCE_NATIVE_NIOZ_GRID "+
                  json.dumps({"site":site,
                    "original_WFS_original_features":source[site][
                       "actual_received_full_geojson_polygons"],
                    "source_class3_model_cells":footprints[site][
                       "WMR_original_code3_mid_littoral_NATIVE_2010_model_center_count"],
                    "source_class4_model_cells":footprints[site][
                       "WMR_original_code4_high_littoral_NATIVE_2010_model_center_count"],
                    "source_mid_high_in5km":footprints[site][
                       "native_original_model_mid_high_littoral_centers_near_gauge_5km"]
                  },sort_keys=True),flush=True)
        report["WMR_original_publisher_geo_source_receipts"]=source
        report["NIOZ_authenticated_original_model_2010_native_littoral_class_mask_SOURCE_COUNTS"]=footprints
        both=all(p["mid_high_littoral_NATIVE_2010_model_centers_source_only"]>=
                 SOURCE_MIN_GRID_CELLS_PER_SITE for p in footprints.values())
        report["source_admission"]=(
            MIDHIGH_SOURCE_STATUS if both else
            "NOT_ADMITTED_V84_SOURCE_MIDHIGH_MODEL_PIXELS_TOO_FEW_IN_SITE")
    except (SourceStop,SourceUnavailable,ValueError,TypeError,ImportError,OSError) as e:
        report["source_admission"]="NOT_ADMITTED_V84_ORIGINAL_PUBLISHER_GEO_SOURCE_OR_NATIVE_MODEL"
        report["source_error"]=str(e)[:500]
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("V84_ORIGINAL_WMR_MIDHIGH_NIOZ_GRID_SOURCE_GATE "+
          json.dumps({"source_status":report["source_admission"],
             "error_or_null":report.get("source_error"),
             "source_sites":list(report.get(
                "NIOZ_authenticated_original_model_2010_native_littoral_class_mask_SOURCE_COUNTS",
                {}))},sort_keys=True),flush=True)
    print("V84_CORRECTED_BOUNDARY_IMMUNE_MIDHIGH_SOURCE_AUDIT_COMPLETE",flush=True)
    return report

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser();a.add_argument("--output",required=True)
    run(a.parse_args().output)
