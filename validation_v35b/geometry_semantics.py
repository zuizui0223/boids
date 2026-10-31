#!/usr/bin/env python3
"""v35-B2: source-only spatial morphology units and optional elevation archive.

No original animal data or RWS tide heights read. The source map is original
extended Baptist 2019 units, not a corrected-v2 intertidal class map or DEM.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
import urllib.request
import zipfile

import shapefile
from pyproj import CRS,Transformer
from shapely.geometry import Point,shape
from shapely.validation import make_valid

import source_only as first

PIN_SHA="2cc448f22730ebcc751d51eba68c61d13be435479abbfd7ab483bc3f77d95856"
PIN_BYTES=194382
ZIP_ELEV="QuantileRegressionbased_ElevationChangesInTheWaddenSea.zip"
PIN_ELEV_MD5="3842bc5d2e9c68c8c9c13f2d60e781ee"
STATION_BUFFER_M=25000

def source_geometry(g,station,buffer_m=STATION_BUFFER_M):
    if not g.is_valid:
        return {"valid":False,"repair_needed":True,
                "distance_km":None,"intersects_fixed_buffer":False,
                "covers_original_station":False}
    return {"valid":True,"repair_needed":False,
            "distance_km":float(g.distance(station))/1000,
            "intersects_fixed_buffer":bool(g.intersects(station.buffer(buffer_m,quad_segs=16))),
            "covers_original_station":bool(g.covers(station))}

def inspect_original_morphology(archive):
    with zipfile.ZipFile(archive) as z:
        members=first.safe_members(z)
        stems=[p[:-4] for p in members if p.casefold().endswith(".shp")]
        if len(stems)!=1:raise ValueError("Original shapefile not unambiguously single")
        prefix=stems[0]
        blob={e:z.read(prefix+e) for e in (".shp",".shx",".dbf",".prj")}
    wkt=blob[".prj"].decode("utf-8-sig",errors="replace")
    crs=CRS.from_wkt(wkt)
    if crs.name!="ETRS89 / UTM zone 32N":
        raise ValueError("Original projected CRS name changed")
    xs,ys=Transformer.from_crs("EPSG:4326",crs,always_xy=True).transform(*first.STATION)
    point=Point(xs,ys)
    reader=shapefile.Reader(shp=io.BytesIO(blob[".shp"]),
                            shx=io.BytesIO(blob[".shx"]),
                            dbf=io.BytesIO(blob[".dbf"]),
                            encodingErrors="ignore")
    source_labels=[]
    invalid=0
    station_inside=[]
    buffer_overlaps=[]
    for i,rec in enumerate(reader.shapeRecords()):
        geom=shape(rec.shape.__geo_interface__)
        info=source_geometry(geom,point)
        attrs=rec.record.as_dict()
        name=str(attrs.get("Name",""))
        source=str(attrs.get("Source",""))
        item=str(attrs.get("Item",""))
        if not info["valid"]:invalid+=1
        if info["covers_original_station"]:station_inside.append(name)
        if info["intersects_fixed_buffer"]:buffer_overlaps.append(name)
        source_labels.append({"source_feature_serial":i+1,
           "published_Name":name[:120],"published_Source":source[:120],
           "published_Item":item[:80],
           "source_polygon_valid":info["valid"],
           "distance_from_public_gauge_km":info["distance_km"],
           "within_fixed_public_25km_gauge_region":info["intersects_fixed_buffer"],
           "public_gauge_point_in_original_polygon":info["covers_original_station"],
           "area_km2_in_projected_source":float(geom.area/1_000_000)})
    if len(source_labels)!=38:raise ValueError("Original source polygon count changed")
    return {"original_public_morphological_units":len(source_labels),
      "original_geometry_invalid_unrepaired_count":invalid,
      "one_original_public_gauge_in_polygon_Name":station_inside,
      "units_intersecting_25km_public_gauge_buffer":buffer_overlaps,
      "source_Label_Counts":dict(collections.Counter(
          r["published_Source"] for r in source_labels)),
      "original_all_units_public_source_metadata":source_labels,
      "source_has_no_local_seabed_elevation_or_dated_tidal_exposure_field":True,
      "source_attribute_fields_only_Name_Source_Item":True,
      "NO_bird_GPS_or_tide_values_opened":True}

def verify_second_archive(metadata,output):
    files=metadata.get("files") or []
    if isinstance(files,dict):files=list((files.get("entries") or {}).values())
    found=[f for f in files if (f.get("key") or f.get("filename"))==ZIP_ELEV]
    if len(found)!=1:raise ValueError("Optional original elevation summary archive absent")
    f=found[0]
    if f.get("checksum")!="md5:"+PIN_ELEV_MD5:raise ValueError("Published elevation ZIP MD5 mismatch")
    sz=f.get("size")
    if not isinstance(sz,int) or not 100<=sz<=10_000_000:raise ValueError("Original ZIP size cap")
    u=(f.get("links") or {}).get("content") or (f.get("links") or {}).get("self")
    if not isinstance(u,str) or not u.startswith("https://zenodo.org/"):
        raise ValueError("Original elevation summary URL not Zenodo")
    x=hashlib.md5();y=hashlib.sha256();total=0
    req=urllib.request.Request(u,headers={"User-Agent":first.AGENT})
    with urllib.request.urlopen(req,timeout=60) as response,output.open("wb") as h:
        for chunk in iter(lambda:response.read(1024*1024),b""):
            total+=len(chunk)
            if total>10_000_000:raise ValueError("Original elevation ZIP exceeded 10 MB cap")
            h.write(chunk);x.update(chunk);y.update(chunk)
    if total!=sz or x.hexdigest()!=PIN_ELEV_MD5:raise ValueError("Published original elevation ZIP digest mismatch")
    with zipfile.ZipFile(output) as z:
        members=first.safe_members(z)
        items=[]
        for name,meta in members.items():
            if len(items)>=60:raise ValueError("Original elevation archive too many subfiles")
            suf=Path(name).suffix.casefold()
            headers=None
            if suf in (".csv",".txt",".tsv") and meta.file_size<=10_000_000:
                with z.open(name) as f:
                    firstrow=f.readline(4096).decode("utf-8-sig",errors="replace").rstrip("\r\n")
                # Header (not the quantitative source numeric rows) only.
                headers=[x.strip()[:120] for x in firstrow.split("\t" if suf==".tsv" else ",")[:100]]
            items.append({"name":name,"original_uncompressed_bytes":meta.file_size,
                          "header_only":headers})
    return {"original_bytes":total,"original_md5":x.hexdigest(),
         "original_sha256":y.hexdigest(),"published_original_archive_members":items,
         "NO_regional_elevation_values_or_GPS_responses_scored":True}

def run():
    original=first.original_metadata()
    spec=first.select_original(original)
    with tempfile.TemporaryDirectory() as tmp:
        primary=Path(tmp)/first.DATAFILE
        original_receipt=first.original_download(spec,primary)
        if original_receipt["independently_computed_original_sha256"]!=PIN_SHA or original_receipt["original_bytes"]!=PIN_BYTES:
            raise ValueError("Frozen exact original source ZIP SHA/byte gate drift")
        geometry=inspect_original_morphology(primary)
        second=verify_second_archive(original,Path(tmp)/ZIP_ELEV)
    status="PUBLIC_MORPHOLOGICAL_UNITS_NOT_POINTWISE_TIDAL_EXPOSURE"
    if not geometry["units_intersecting_25km_public_gauge_buffer"] or geometry["original_geometry_invalid_unrepaired_count"]:
        status="V35B_ORIGINAL_MAP_GEOMETRY_STATION_OVERLAP_NOT_ADMITTED"
    return {"status":status,
       "original_zenodo_record":first.RECORD,
       "original_published_MD5_SHA_source":original_receipt,
       "original_public_morphological_unit_source":geometry,
       "optional_annual_quantile_summary_source":second,
       "this_is_NOT_corrected_Mendeley_ecotope_v2":True,
       "no_currently_exposed_intertidal_habitat_or_foraging_GPS_detected":True,
       "NO_animal_GPS_or_original_RWS_tide_time_series_read":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v35b/results/zenodo_morphology_units_and_quantile_source.json"))
    args=p.parse_args()
    try:data=run()
    except Exception as e:
        data={"status":"V35B_ORIGINAL_MORPHOLOGY_UNIT_SOURCE_STOP",
              "reason":type(e).__name__,
              "message":str(e)[:350],
              "NO_animal_GPS_or_original_RWS_tide_time_series_read":True}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V35B_SOURCE_UNIT_STATUS",data["status"])
    print("V35B_ALL_ORIGINAL_PUBLIC_SOURCE_METADATA",json.dumps(data,sort_keys=True,separators=(",",":")))
    print("V35B_NOT_ANIMAL_HABITAT_EFFECT")
if __name__=="__main__":main()
