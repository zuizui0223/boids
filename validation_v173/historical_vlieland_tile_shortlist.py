"""v173 SOURCE-only geographic shortlist of authentic historical RWS/Deltares tiles.

Exactly 165 provider-aligned rows in 2026-03-03 official catalog.nc:
urlPath, projectionCoverage_x/y, geospatialCoverage_eastwest/northsouth,
timeCoverage (days since 1970-01-01). Native binary SHA256 fixed by v172.

Reject tile names as location/survey-date proof: use original geographic
bounds and time-coverage metadata. Presence of 2016 in *coverage range* is
only a candidate year, NEVER a valid actual 2016 z raster at tagged bird GPS.

Do not output raw original GPS points, map exact birds, or any elevation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from netCDF4 import Dataset,chartostring

from native_catalog_nc_geoindex import acquire,VLIE_RD_SEARCH

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/"validation_v172/results/original_deltares_vaklodingen_catalog_nc_v172.json"
OUT=ROOT/"validation_v173/results/genuine_vlieland_historical_tiles_shortlist_v173.json"
EXPECTED_SHA="b4364e1d18ea3098ccef8fcbd9a9f3506e98264748c0fe9ce80697a9cb9a2193"
EXPECTED_B=40976
NATIVE_TILES=165
ALL_POSSIBLE_YEARS=(2016,2018,2019)
GEO_BBOX_WIDE=tuple(VLIE_RD_SEARCH)
GEO_BBOX_HARBOR_LL=(5.098,53.298)

def extract_urls(value):
    a=np.asarray(chartostring(value))
    result=[v.decode("utf-8","replace").strip() if isinstance(v,bytes)
            else str(v).strip() for v in np.ravel(a)]
    if len(result)!=NATIVE_TILES or len(set(result))!=NATIVE_TILES:
        raise AssertionError("Actual provider has not exactly 165 distinct tile URL rows")
    if not all(x.startswith("http") and x.endswith(".nc") and
               "rijkswaterstaat/vaklodingen/" in x for x in result):
        raise AssertionError("Original 165 source NetCDF URL rows invalid")
    return result

def xy_intersect(coords,box):
    xmin,ymin,xmax,ymax=coords
    x0,y0,x1,y1=box
    dx=max(0.0,min(xmax,x1)-max(xmin,x0))
    dy=max(0.0,min(ymax,y1)-max(ymin,y0))
    return dx>0 and dy>0,dx*dy/1e6

def actual_shortlist(raw):
    with Dataset("true_deltares_catalog.nc",memory=raw) as nc:
        names=("urlPath","projectionCoverage_x","projectionCoverage_y",
               "geospatialCoverage_eastwest","geospatialCoverage_northsouth","timeCoverage")
        if not all(x in nc.variables for x in names):
            raise AssertionError("Catalog missing aligned source geographic/time fields")
        if str(nc.getncattr("time_coverage_units")).strip()!="days since 1970-01-01":
            raise AssertionError("Original time coverage units drifted")
        urls=extract_urls(nc.variables["urlPath"][:])
        bounds={k:np.asarray(nc.variables[k][:],dtype=np.float64) for k in names[1:]}
        if any(v.shape!=(NATIVE_TILES,2) or not np.isfinite(v).all()
               for v in bounds.values()):
            raise AssertionError("Source per-tile xy/time/latlon 165×2 alignment changed")
        origin=datetime(1970,1,1,tzinfo=timezone.utc)
        results=[]
        has_2016_count=0
        for i,url in enumerate(urls):
            bx=sorted(bounds["projectionCoverage_x"][i])
            by=sorted(bounds["projectionCoverage_y"][i])
            lon=sorted(bounds["geospatialCoverage_eastwest"][i])
            lat=sorted(bounds["geospatialCoverage_northsouth"][i])
            ti=sorted(bounds["timeCoverage"][i])
            if bx[1]-bx[0]<=0 or by[1]-by[0]<=0 or ti[1]<ti[0]:
                raise AssertionError("Invalid native provider per-tile source bounds")
            d0=origin+timedelta(days=float(ti[0]))
            d1=origin+timedelta(days=float(ti[1]))
            cover_possible={str(yr): d0.year<=yr<=d1.year for yr in ALL_POSSIBLE_YEARS}
            if cover_possible["2016"]:has_2016_count+=1
            coords=(float(bx[0]),float(by[0]),float(bx[1]),float(by[1]))
            hit,area=xy_intersect(coords,GEO_BBOX_WIDE)
            if not hit:continue
            results.append({
                "source_original_native_tile_url":url,
                "source_tile_basename":url.split("/")[-1],
                "original_projected_xy_RD_NAP_search_bbox_m":[round(x,3) for x in coords],
                "original_WGS84_source_lonlat_bbox":[
                    round(float(x),6) for x in (lon[0],lat[0],lon[1],lat[1])],
                "catalog_wide_coarse_vlieland_search_overlap_km2":round(area,5),
                "original_catalog_timeCoverage_start":d0.date().isoformat(),
                "original_catalog_timeCoverage_end":d1.date().isoformat(),
                "calendar_year_in_tile_timeCoverage_RANGE_only":cover_possible,
                "real_2016_survey_or_valid_source_z_at_bird_GPS":"NOT_VERIFIED",
                "native_source_datum_NAP":"NOT_VERIFIED",
            })
        results.sort(key=lambda v:(-v["catalog_wide_coarse_vlieland_search_overlap_km2"],
                                   v["source_tile_basename"]))
    return {
        "version":"v173_real_deltares_Vlieland_historical_tile_bbox_shortlist_1",
        "genuine_original_deltares_catalog_sha256":hashlib.sha256(raw).hexdigest(),
        "original_catalog_native_rows":NATIVE_TILES,
        "n_official_tiles_with_catalog_timerange_covering_2016":has_2016_count,
        "fixed_coarse_vlieland_RD_box_m":list(GEO_BBOX_WIDE),
        "coarse_box_is_NOT_real_bird_GPS_envelope":True,
        "n_original_tiles_whose_xy_bbox_intersects_coarse_Vlieland_box":len(results),
        "all_original_intersecting_native_tile_source_metadata":results,
        "time_range_not_equal_real_survey_cell_time":True,
        "no_model_or_original_bird_GPS_z_join":True,
        "no_causal_tide_x_solar_or_social_boids_estimation":True,
    }

def run():
    prev=json.loads(PRIOR.read_text())
    if (prev["original_publisher_index_source"]["original_binary_SHA256"]!=EXPECTED_SHA or
        prev["original_publisher_index_source"]["original_content_bytes"]!=EXPECTED_B or
        prev["original_netcdf_dims"].get("dimension_length_165")!=165):
        raise AssertionError("Original v172 provider native source frozen scope changed")
    raw,meta=acquire()
    if len(raw)!=EXPECTED_B or hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:
        raise AssertionError("Official Deltares catalog.nc native bytes/SHA256 changed")
    result=actual_shortlist(raw)
    if not result["n_original_tiles_whose_xy_bbox_intersects_coarse_Vlieland_box"]:
        raise AssertionError("Original coordinate index returned no Vlieland candidate; SOURCE_STOP")
    return result

def main():
    parser=argparse.ArgumentParser()
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--emit",action="store_true")
    modes.add_argument("--check",action="store_true")
    args=parser.parse_args()
    result=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        if not OUT.is_file():
            raise AssertionError("Original v173 geographic-source shortlist receipt missing")
        if json.loads(OUT.read_text())!=result:
            raise AssertionError("Genuine original 165-tile source/geo/time shortlist changed")
        print("V173_GENUINE_ORIGINAL_165_TILE_BBOX_SHORTLIST_REPLAY_PASS")
    else:
        OUT.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
        print("V173_ORIGINAL_SOURCE_SHORTLIST_START")
        print(json.dumps(result,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V173_ORIGINAL_SOURCE_SHORTLIST_END")
    print("V173_ORIGINAL_SOURCE_SCOPE="+json.dumps({
        "n_total":result["original_catalog_native_rows"],
        "n_box_candidates":result["n_original_tiles_whose_xy_bbox_intersects_coarse_Vlieland_box"],
        "candidates":[
            {"tile":z["source_tile_basename"],
             "intersection_km2":z["catalog_wide_coarse_vlieland_search_overlap_km2"],
             "has_2016_in_range":z["calendar_year_in_tile_timeCoverage_RANGE_only"]["2016"],
             "start":z["original_catalog_timeCoverage_start"],
             "end":z["original_catalog_timeCoverage_end"]}
            for z in result["all_original_intersecting_native_tile_source_metadata"]]
    },sort_keys=True))
if __name__=="__main__":
    main()
