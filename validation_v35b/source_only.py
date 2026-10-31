#!/usr/bin/env python3
"""v35-B: original Zenodo morphological tidal-flat polygon SOURCE ONLY.

This performs byte/checksum, ZIP archive, original Shapefile CRS/fields/extent
verification. Never reads original oystercatcher GPS or RWS water-level data.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import tempfile
import urllib.error
import urllib.request
import zipfile

import shapefile
from pyproj import CRS,Transformer

RECORD=14535985
DATAFILE="TidalFlats_UTM32_Baptistetal2019_extended.zip"
PUBLISHED_MD5="eaa559c9b8401ed4db70b0ef70fe2d7c"
MAX_ZIP_BYTES=10_000_000
MAX_DECOMPRESSED_BYTES=30_000_000
MAX_ARCHIVE_MEMBERS=100
MAX_FEATURES=100000
STATION=(6.202908,53.468937) # Schiermonnikoog Waddenzee, official RWS geographic locator.
API=f"https://zenodo.org/api/records/{RECORD}"
AGENT="boids-v35b-original-source-geometry-only/1.0"

def original_metadata():
    req=urllib.request.Request(API,headers={"Accept":"application/json","User-Agent":AGENT})
    with urllib.request.urlopen(req,timeout=45) as response:
        raw=response.read(2_000_001)
    if len(raw)>2_000_000:raise ValueError("Original provider metadata over limit")
    m=json.loads(raw)
    if m.get("id")!=RECORD:raise ValueError("Wrong original published dataset record")
    return m

def select_original(m):
    files=m.get("files") or []
    if isinstance(files,dict):files=list((files.get("entries") or {}).values())
    matches=[x for x in files if (x.get("key") or x.get("filename"))==DATAFILE]
    if len(matches)!=1:raise ValueError("Original named tidal-flat ZIP file not unique")
    f=matches[0]
    size=f.get("size")
    checksum=f.get("checksum")
    url=(f.get("links") or {}).get("content") or (f.get("links") or {}).get("self")
    if not isinstance(size,int) or not 100<=size<=MAX_ZIP_BYTES:
        raise ValueError("Original ZIP provider size invalid or too large")
    if checksum!=f"md5:{PUBLISHED_MD5}":
        raise ValueError("Source provider MD5 differs from publicly registered original")
    if not isinstance(url,str) or not url.startswith("https://zenodo.org/"):
        raise ValueError("Original ZIP must come from official Zenodo HTTPS")
    return {"size":size,"url":url,"name":DATAFILE}

def original_download(spec, dest):
    req=urllib.request.Request(spec["url"],headers={"User-Agent":AGENT})
    sha=hashlib.sha256()
    md5=hashlib.md5()
    count=0
    with urllib.request.urlopen(req,timeout=100) as response,dest.open("wb") as f:
        for chunk in iter(lambda:response.read(1024*1024),b""):
            count+=len(chunk)
            if count>MAX_ZIP_BYTES:raise ValueError("Original file exceeded cap")
            f.write(chunk);sha.update(chunk);md5.update(chunk)
    if count!=spec["size"] or md5.hexdigest()!=PUBLISHED_MD5:
        raise ValueError("Original published MD5/size mismatch")
    return {"original_zip_name":DATAFILE,"original_bytes":count,
            "original_published_md5":PUBLISHED_MD5,
            "independently_computed_original_sha256":sha.hexdigest(),
            "original_source_byte_gate":"PASS"}

def safe_members(z):
    entries=z.infolist()
    if len(entries)>MAX_ARCHIVE_MEMBERS:raise ValueError("Too many ZIP members")
    if sum(x.file_size for x in entries)>MAX_DECOMPRESSED_BYTES:
        raise ValueError("Potential ZIP expansion exceeded source gate")
    allowed={}
    for v in entries:
        p=Path(v.filename)
        if v.filename.startswith("/") or ".." in p.parts or "\\" in v.filename:
            raise ValueError("Invalid original ZIP path")
        if v.is_dir():continue
        allowed[v.filename]=v
    return allowed

def inspect_shapefile(z):
    members=safe_members(z)
    roots=[x[:-4] for x in members if x.casefold().endswith(".shp")]
    if len(roots)!=1:raise ValueError("Expected single unambiguous original source shapefile")
    stem=roots[0]
    # Same original common stem, with one shapefile/DBF/SHX/PRJ.
    needed={k:stem+k for k in (".shp",".shx",".dbf",".prj")}
    if any(x not in members for x in needed.values()):
        raise ValueError("Missing original shapefile components or original CRS")
    payload={k:z.read(v) for k,v in needed.items()}
    prj=payload[".prj"].decode("utf-8-sig",errors="replace")
    try:crs=CRS.from_wkt(prj)
    except Exception as e:raise ValueError("Original shapefile CRS/WKT invalid") from e
    if not crs.is_projected:raise ValueError("Source map CRS is not projected")
    original=shapefile.Reader(shp=io.BytesIO(payload[".shp"]),
                             shx=io.BytesIO(payload[".shx"]),
                             dbf=io.BytesIO(payload[".dbf"]),
                             encodingErrors="ignore")
    records=len(original)
    if not 1<=records<=MAX_FEATURES:raise ValueError("Original polygon count unsupported")
    if original.shapeType not in (shapefile.POLYGON,shapefile.POLYGONZ,shapefile.POLYGONM):
        raise ValueError("Original source layer is not polygons")
    bbox=list(map(float,original.bbox))
    if not (bbox[0]<bbox[2] and bbox[1]<bbox[3]):
        raise ValueError("Invalid original source bounding box")
    coords=Transformer.from_crs("EPSG:4326",crs,always_xy=True).transform(*STATION)
    if not all(map(math.isfinite,coords)):
        raise ValueError("Original station transform nonfinite")
    within=(bbox[0]<=coords[0]<=bbox[2] and bbox[1]<=coords[1]<=bbox[3])
    fields=[{"name":f[0],"type":f[1],"length":f[2],"decimals":f[3]}
            for f in original.fields[1:]]
    src=original.shapeTypeName
    return {"original_named_shapefile_root":stem,
            "original_geometry_type":src,
            "original_projected_CRS_wkt_sha256":hashlib.sha256(prj.encode()).hexdigest(),
            "original_projected_CRS_name":crs.name,
            "original_projected_CRS_EPSG":crs.to_epsg(),
            "original_layer_feature_count":records,
            "original_polygon_envelope_in_original_CRS":bbox,
            "official_station_public_coords_in_source_CRS":list(map(float,coords)),
            "official_station_within_polygon_layer_global_bbox":within,
            "original_DBf_public_field_names_types":fields,
            "source_archive_members":[{"name":x.filename,"bytes":x.file_size}
                                      for x in members.values()],
            "no_per_polygon_geometries_or_animal_GPS_read":True}

def run():
    m=original_metadata()
    spec=select_original(m)
    with tempfile.TemporaryDirectory() as folder:
        loc=Path(folder)/DATAFILE
        receipt=original_download(spec,loc)
        with zipfile.ZipFile(loc) as z:
            morph=inspect_shapefile(z)
    l=(m.get("metadata") or {}).get("license")
    if isinstance(l,dict):l=l.get("id") or l.get("title")
    status=("ORIGINAL_ZENODO_TIDAL_FLAT_POLYGON_SOURCE_SCHEMA_ADMITTED"
             if morph["official_station_within_polygon_layer_global_bbox"]
             else "ORIGINAL_SOURCE_STUDY_STATION_OUTSIDE_TIDAL_FLAT_GEOMETRY_BBOX")
    return {"status":status,
            "source_doi":m.get("doi"),
            "original_record_id":RECORD,
            "original_provider_version":(m.get("metadata") or {}).get("version"),
            "license_original_provider":l,
            "derived_from":"Baptist et al. 2019 morphological units (source archive publication 2024/2025)",
            "NOT_corrected_2021_ecotope_v2":True,
            "NOT_a_dynamic_bed_DEM_or_time_specific_dry_mudflat":True,
            "original_provider_integrity":receipt,
            "original_shapefile_geometry_and_schema":morph,
            "no_animal_GPS_or_tide_values_or_GIS_join_scored":True,
            "previous_v35A_source_STOP_preserved":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v35b/results/zenodo_static_tidal_flats_source.json"))
    args=p.parse_args()
    try: data=run()
    except Exception as e:
        data={"status":"V35B_ORIGINAL_ZENODO_SOURCE_STOP",
              "error_type":type(e).__name__,"error_message":str(e)[:400],
              "no_animal_GPS_or_tide_values_or_GIS_join_scored":True}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V35B_SOURCE_STATUS",data["status"])
    print("V35B_SOURCE_ONLY_JSON",json.dumps(data,sort_keys=True,separators=(",",":")))
    print("V35B_NO_ANIMAL_HABITAT_SPATIAL_JOIN")
if __name__=="__main__":
    main()
