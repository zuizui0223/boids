"""v84C original WMR WS3 GeoServer ALL SOURCE polygons (no CQL), local mid/high.

Original WMR GetFeature CQL unsupported (original HTTP500). Full original
public geojson count=800 unfiltered returns 345 Schier and 280 Ameland
reported features. Require exact source numberMatched and every returned
source feature; then use only mid/high littoral codes3/4 IN MEMORY.

The public WS3 map version IS NOT certified corrected Mendeley 2021 v2.
Original bird GPS, waterlevel RWS and NIOZ wildlife used-index unexamined.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json

import numpy as np
import shapely
from shapely.geometry import shape

from wmr_geoserver_ecotope_source_probe import (
    BASE,MAIN,SourceUnavailable,bounded_request as wfs)
from wmr_original_midhigh_native_nioz_grid_source import (
    SourceStop,FIXED_SITE_BBOX,MAX_GEOJSON_BYTES,
    MAX_INVALID_POLYGON_PERCENT,FIXED_CODES,
    METRIC_X,METRIC_Y,_native_original_Jan2010_grid,_overlay_model_centers,
    SOURCE_MIN_GRID_CELLS_PER_SITE)

PUBLISHER_FULL_WFS_UNFILTERED_MATCHED={
    "Schiermonnikoog":345,
    "Ameland_Nes":280}
MAX_NATIVE_SOURCE_ALL_FEATURES=800
ALL_ORIGINAL_CODES=tuple(range(7))
TRUE_MIDHIGH=(3,4)
ADMIT="SOURCE_ADMITTED_V84C_FULL_ORIGINAL_WMR_WS3_MIDHIGH_LITTORAL_SOURCE_ONLY_VERSION_UNVERIFIED"

def _original_full_site(site,bbox,fetch=wfs):
    if site not in PUBLISHER_FULL_WFS_UNFILTERED_MATCHED:
        raise SourceStop("SOURCE_STOP_V84C_UNFROZEN_WMR_SITE")
    if tuple(bbox)!=tuple(FIXED_SITE_BBOX[site]):
        raise SourceStop("SOURCE_STOP_V84C_SITE_SOURCE_BBOX_CHANGED")
    args={
        "request":"GetFeature",
        "typeNames":MAIN,
        "count":str(MAX_NATIVE_SOURCE_ALL_FEATURES),
        "outputFormat":"application/json",
        "srsName":"CRS:84",
        "bbox":",".join(f"{z:.5f}" for z in bbox)+",CRS:84"}
    raw=fetch(args,limit=MAX_GEOJSON_BYTES)
    try:q=json.loads(raw)
    except (ValueError,TypeError) as e:
        raise SourceStop("SOURCE_STOP_V84C_UNFILTERED_NOT_GEOJSON") from e
    if not isinstance(q,dict) or not isinstance(q.get("features"),list):
        raise SourceStop("SOURCE_STOP_V84C_WFS_NO_POLYGON_FEATURE_COLLECTION")
    group=q["features"]
    try:matched=int(q.get("numberMatched"))
    except (TypeError,ValueError) as e:
        raise SourceStop("SOURCE_STOP_V84C_WFS_MISSING_TRUE_SOURCE_MATCHED_COUNT") from e
    if (matched!=PUBLISHER_FULL_WFS_UNFILTERED_MATCHED[site]
        or len(group)!=matched
        or len(group)>=MAX_NATIVE_SOURCE_ALL_FEATURES
        or q.get("next")):
        raise SourceStop("SOURCE_STOP_V84C_ORIGINAL_ALL_SOURCE_POLYGONS_NOT_COMPLETE")
    rawcounts=Counter()
    selected=[]
    invalid=0
    for feature in group:
        data=feature.get("properties") or {}
        try:code=int(data.get("litoralcode"))
        except (TypeError,ValueError) as e:
            raise SourceStop("SOURCE_STOP_V84C_WMR_MISSING_ORIGINAL_CODE") from e
        if code not in ALL_ORIGINAL_CODES:
            raise SourceStop("SOURCE_STOP_V84C_WMR_NATIVE_CLASS_OUTSIDE_0_6")
        rawcounts[code]+=1
        if code not in TRUE_MIDHIGH:
            continue
        obj=feature.get("geometry")
        if not isinstance(obj,dict):
            raise SourceStop("SOURCE_STOP_V84C_WMR_NO_NATIVE_POLYGON_GEOMETRY")
        geom=shape(obj)
        if geom.is_empty or geom.geom_type not in ("Polygon","MultiPolygon"):
            raise SourceStop("SOURCE_STOP_V84C_WMR_NOT_VALID_POLYGON_SOURCE")
        a,b,c,d=geom.bounds
        if not (4<=a<=c<=10 and 52<=b<=d<=56):
            raise SourceStop("SOURCE_STOP_V84C_WMR_GEOJSON_COORDS_NOT_WADDEN_DEGREES")
        if not geom.is_valid:
            invalid+=1
            geom=shapely.make_valid(geom)
            if geom.geom_type=="GeometryCollection":
                parts=[g for g in geom.geoms
                       if g.geom_type in ("Polygon","MultiPolygon")]
                if not parts:
                    raise SourceStop("SOURCE_STOP_V84C_CANNOT_FIX_NATIVE_POLYGON")
                geom=shapely.union_all(parts)
        if geom.geom_type not in ("Polygon","MultiPolygon") or geom.is_empty:
            raise SourceStop("SOURCE_STOP_V84C_POLYGON_SOURCE_REPAIR_FAILED")
        projected=shapely.transform(
            geom,lambda coords:coords*np.array([METRIC_X,METRIC_Y]))
        selected.append((projected,code))
    if not selected or (100*invalid/len(selected)>MAX_INVALID_POLYGON_PERCENT):
        raise SourceStop("SOURCE_STOP_V84C_MID_HIGH_ORIGINAL_SOURCE_BAD_GEOMETRY")
    return selected,{
        "site":site,
        "original_WMR_GeoServer_source_layer":MAIN,
        "original_full_WFS_GetFeature_NO_CQL_source_count":matched,
        "original_true_received_source_polygon_features":len(group),
        "native_all_litoralcode_0_6_polygon_counts":{
            str(z):rawcounts[z] for z in ALL_ORIGINAL_CODES},
        "source_mid3_selected_native_polygon_count":rawcounts[3],
        "source_high4_selected_native_polygon_count":rawcounts[4],
        "original_mid_high_repaired_invalid_polygon_count":invalid,
        "original_full_provider_WFS_response_SHA256_COMPUTED_NOT_PUBLISHER":
            sha256(raw).hexdigest(),
        "original_2019_v1_vs_2021_v2_status":"UNVERIFIED, only unchanged codes3,4",
        "no_low_littoral2_geometry_or_biology_included":True,
        "geometry_source_not_exported":True}

def run(output):
    result={
        "analysis":"V84C_WMR_TRUE_FULL_UNFILTERED_2008_2012_MIDHIGH_CODE3_4_POLYGON_AND_2010_NIOZ_GEOGRAPHIC_SOURCE",
        "original_WMR_publisher":BASE,
        "original_WMR_native_layer":MAIN,
        "native_WMR_2021_corrected_v2_version_UNVERIFIED":True,
        "previous_v84_filtered_WFS_HTTP500":True,
        "previous_v84B_unfiltered_source_matched_counts":
            PUBLISHER_FULL_WFS_UNFILTERED_MATCHED,
        "native_low_littoral_code2_IGNORED_due_corrigendum":True,
        "source_original_animal_GPS_and_RWS_NAP_tide_not_read":True}
    try:
        lat,lon,proof=_native_original_Jan2010_grid()
        result["original_NIOZ_2010_Jan_native_coordinate_SHA_source"]=proof
        original={};cells={}
        for site,bbox in FIXED_SITE_BBOX.items():
            polygons,receipt=_original_full_site(site,bbox)
            original[site]=receipt
            cells[site]=_overlay_model_centers(lat,lon,polygons,site)
            print("V84C_AUTHENTIC_WMR_COMPLETE_PUBLISHED_POLYGON_SET_AND_SOURCE_NIOZ_GRID "+
                  json.dumps({
                    "site":site,"all_native_WMR_polygons":receipt[
                       "original_full_WFS_GetFeature_NO_CQL_source_count"],
                    "original_mid_littoral_polygon_count":receipt[
                       "source_mid3_selected_native_polygon_count"],
                    "original_high_littoral_polygon_count":receipt[
                       "source_high4_selected_native_polygon_count"],
                    "source_NIOZ_2010_true_mid_littoral_cells":cells[site][
                       "WMR_original_code3_mid_littoral_NATIVE_2010_model_center_count"],
                    "source_NIOZ_2010_true_high_littoral_cells":cells[site][
                       "WMR_original_code4_high_littoral_NATIVE_2010_model_center_count"],
                    "source_5km_station_mid_high_cells":cells[site][
                       "native_original_model_mid_high_littoral_centers_near_gauge_5km"]},
                   sort_keys=True),flush=True)
        result["original_WMR_complete_polygon_class_source"]=original
        result["source_original_2010_NIOZ_model_geographic_mid_high_class_3_4_footprints"]=cells
        admitted=all(
           z["mid_high_littoral_NATIVE_2010_model_centers_source_only"]>=
           SOURCE_MIN_GRID_CELLS_PER_SITE for z in cells.values())
        result["frozen_source_admission"]=(ADMIT if admitted else
            "NOT_ADMITTED_V84C_SOURCE_TOO_FEW_MID_HIGH_NIOZ_CELLS")
    except (SourceStop,SourceUnavailable,ValueError,TypeError,ImportError,OSError) as e:
        result["frozen_source_admission"]="NOT_ADMITTED_V84C_ORIGINAL_WMR_WFS_OR_MODEL"
        result["source_error"]=str(e)[:350]
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("V84C_ORIGINAL_COMPLETE_WMR_MIDHIGH_ECOTOPE_SOURCE_GATE "+
          json.dumps({
             "result":result["frozen_source_admission"],
             "source_issue":result.get("source_error"),
             "native_model_NIOZ_2010_geography_site_count":len(result.get(
                  "source_original_2010_NIOZ_model_geographic_mid_high_class_3_4_footprints",{})),
             "ecotope_version_is_exact_corrected2021_V2":False,
             "no_original_bird_used_index_scored":True},
            sort_keys=True),flush=True)
    print("V84C_ORIGINAL_SOURCE_COMPLETE_UNFILTERED_GEOSERVER_QA_FINISHED",flush=True)
    return result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    run(p.parse_args().output)
