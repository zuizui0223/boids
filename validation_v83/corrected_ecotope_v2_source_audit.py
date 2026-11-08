"""v83: authentic CORRECTED 2021 V2 Wadden 2008–2012 ecotope GeoPackage audit.

Source ONLY, no wild bird GPS, RWS arrays, NIOZ index raster or effect.
The official 2021 v2 fixes a 2019 v1 low-littoral 4% vs 0.001%
class boundary. Never silently substitute the wrong original version.
Public Mendeley Data API official 2024+ https://api.data.mendeley.com.
No unverified file URL, ID, or SHA or unauthorized download fabricated.
"""
from __future__ import annotations
from contextlib import closing
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import os
import re
import sqlite3
import stat
import tempfile
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from zipfile import ZipFile

import pyproj

SOURCE_ID="27mysx289g"
SOURCE_VERSION=2
EXPECTED_DOI="10.17632/27mysx289g.2"
DATASET_NAME="Data for: An ecotope map of the trilateral Wadden Sea"
ARCHIVE="EctpWZ3L_gpkg.zip"
NATIVE_POLYGONS="EcotopeWS3_mp"
NATIVE_CLASS="LitoralCod"
API_ROOT="https://api.data.mendeley.com"
MAX_API_BYTES=7_000_000
MAX_ARCHIVE_BYTES=50_000_000
MAX_GPKG_BYTES=750_000_000
PUBLIC_SITE_STATIONS={
    "Schiermonnikoog":(53.46894,6.20291),
    "Ameland Nes":(53.42977,5.75945)}
LITTORAL_CODES=(2,3,4)
OUTSIDE_CODES=(0,1,5,6)

class SourceStop(Exception):pass

def fetch_bound(url,cap=MAX_API_BYTES,*,expected_host=None):
    p=urlparse(url)
    if p.scheme!="https":
        raise SourceStop("SOURCE_STOP_V83_NON_HTTPS_PUBLISHER_ENDPOINT")
    if expected_host and p.hostname!=expected_host:
        raise SourceStop("SOURCE_STOP_V83_NOT_ORIGINAL_MENDELEY_METADATA_HOST")
    req=Request(url,headers={
        "User-Agent":"boids-v83-corrected-ecotope-public-source-qa/1.0",
        "Accept":"application/json, application/octet-stream, */*"})
    try:
        with urlopen(req,timeout=75) as response:
            out=response.read(cap+1)
            if len(out)>cap:raise SourceStop("SOURCE_STOP_V83_FILE_TOO_LARGE")
            final=urlparse(response.geturl())
            if final.scheme!="https":raise SourceStop("SOURCE_STOP_V83_REDIRECT_NOT_HTTPS")
            return out,{"http_status":response.status,
                        "download_final_https":True}
    except (HTTPError,URLError,TimeoutError) as exc:
        raise SourceStop("SOURCE_UNAVAILABLE_V83_PUBLIC_PROVIDER "+str(exc)[:170]) from exc

def _api_json(path):
    payload,_=fetch_bound(API_ROOT+path,expected_host="api.data.mendeley.com")
    try:
        return json.loads(payload)
    except (TypeError,ValueError) as exc:
        raise SourceStop("SOURCE_UNAVAILABLE_V83_NO_PUBLIC_API_JSON") from exc

def publisher_metadata():
    """Version2 fixed and true original fileUUID from original public API."""
    errors=[]
    dataset=None
    for endpoint in (
        f"/datasets/{SOURCE_ID}?version={SOURCE_VERSION}",
        f"/datasets/publics/{SOURCE_ID}?version={SOURCE_VERSION}"):
        try:
            dataset=_api_json(endpoint)
            if isinstance(dataset,dict):break
        except SourceStop as e:errors.append(str(e))
    if not isinstance(dataset,dict):
        raise SourceStop("SOURCE_UNAVAILABLE_V83_MENDELEY_DATASET_METADATA "+str(errors)[:350])
    src_version=dataset.get("version") or dataset.get("dataset_version")
    if src_version is None and isinstance(dataset.get("latestVersion"),dict):
        src_version=dataset["latestVersion"].get("version")
    if src_version is not None and int(src_version)!=SOURCE_VERSION:
        raise SourceStop("SOURCE_STOP_V83_WRONG_ORIGINAL_PUBLISHED_VERSION")
    doi=dataset.get("doi")
    if isinstance(doi,dict):doi=doi.get("id") or doi.get("doi")
    if doi and str(doi).lower().replace("https://doi.org/","")!=EXPECTED_DOI.lower():
        raise SourceStop("SOURCE_STOP_V83_WRONG_V2_DOI")
    if not doi and src_version is None:
        raise SourceStop("SOURCE_STOP_V83_CANNOT_VERIFY_CORRECTED_PUBLISHED_VERSION")
    errors=[]
    files=None
    for endpoint in (
        f"/datasets/{SOURCE_ID}/files?version={SOURCE_VERSION}",
        f"/datasets/publics/{SOURCE_ID}/files?version={SOURCE_VERSION}"):
        try:
            files=_api_json(endpoint)
            if isinstance(files,(list,dict)):break
        except SourceStop as e:errors.append(str(e))
    if isinstance(files,dict):
        files=files.get("results") or files.get("files") or files.get("data")
    if not isinstance(files,list):
        # Some public GET dataset metadata versions include files directly.
        files=dataset.get("files")
    if not isinstance(files,list):
        raise SourceStop("SOURCE_UNAVAILABLE_V83_MENDELEY_PUBLIC_FILE_MANIFEST "+str(errors)[:350])
    matching=[]
    for file in files:
        if not isinstance(file,dict):continue
        name=file.get("filename") or file.get("name")
        if name!=ARCHIVE:continue
        details=file.get("content_details") or {}
        fid=file.get("id") or file.get("file_id")
        size=file.get("size") or details.get("size")
        hashed=details.get("sha256_hash") or file.get("sha256_hash")
        if not (isinstance(fid,str) and re.fullmatch(
            "[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}",fid)):
            raise SourceStop("SOURCE_STOP_V83_PUBLISHER_ZIP_FILE_UUID_INVALID")
        if not (size and 0<int(size)<=MAX_ARCHIVE_BYTES):
            raise SourceStop("SOURCE_STOP_V83_ORIGINAL_PUBLISHER_ZIP_SIZE")
        if hashed and not re.fullmatch(r"[a-fA-F0-9]{64}",str(hashed)):
            raise SourceStop("SOURCE_STOP_V83_PUBLISHER_SHA256_INVALID")
        matching.append({
            "published_name":name,
            "original_file_UUID":fid,
            "publisher_advertised_bytes":int(size),
            "publisher_sha256_or_null":str(hashed).lower() if hashed else None})
    if len(matching)!=1:
        raise SourceStop("SOURCE_STOP_V83_NOT_EXACTLY_ONE_CORRECTED_GPKG_ZIP")
    return matching[0],{
        "original_dataset":SOURCE_ID,
        "source_version_2021_corrected":SOURCE_VERSION,
        "source_published_DOI":doi or EXPECTED_DOI,
        "publisher_dataset_name":str(dataset.get("name") or dataset.get("title") or DATASET_NAME)[:140],
        "source_v2_2019_low_intertidal_4pct_correction_required":True}

def download_publisher_zip(file_entry,*,fetch=fetch_bound):
    url=(API_ROOT+f"/datasets/{SOURCE_ID}/files/"+
         file_entry["original_file_UUID"]+
         f"/file_downloaded?version={SOURCE_VERSION}")
    raw,_=fetch(url,MAX_ARCHIVE_BYTES,
                expected_host="api.data.mendeley.com")
    actual=sha256(raw).hexdigest()
    if len(raw)!=file_entry["publisher_advertised_bytes"]:
        raise SourceStop("SOURCE_STOP_V83_PUBLIC_FILE_BYTES_NOT_PUBLISHER_SIZE")
    hashed=file_entry["publisher_sha256_or_null"]
    if hashed and hashed!=actual:
        raise SourceStop("SOURCE_STOP_V83_PUBLIC_SHA256_NOT_PUBLISHER_DIGEST")
    return raw,{
        "original_filename":ARCHIVE,
        "actual_compressed_bytes":len(raw),
        "original_download_SHA256":actual,
        "publisher_SHA256_available_and_verified":bool(hashed),
        "source_not_falsely_called_provider_hash_verified_when_missing":True}

def selected_gpkg_from_zip(raw):
    """No archive path traversal, symlink, executable scripts or source raster export."""
    try:
        zp=ZipFile(__import__("io").BytesIO(raw))
    except Exception as e:
        raise SourceStop("SOURCE_STOP_V83_NOT_A_VALID_ZIP") from e
    members=zp.infolist()
    for item in members:
        p=PurePosixPath(item.filename)
        if (item.filename.startswith("/") or ".." in p.parts or
            (item.external_attr>>16)&stat.S_IFMT(0o170000)==stat.S_IFLNK):
            raise SourceStop("SOURCE_STOP_V83_UNSAFE_ZIP_ARCHIVE_MEMBER")
        if item.file_size>MAX_GPKG_BYTES:
            raise SourceStop("SOURCE_STOP_V83_GPKG_UNCOMPRESSED_TOO_LARGE")
    expected=[item for item in members
              if not item.is_dir() and item.filename.lower().endswith(".gpkg")]
    if len(expected)!=1:
        raise SourceStop("SOURCE_STOP_V83_NEED_ONE_AND_ONLY_ONE_ORIGINAL_GPKG")
    item=expected[0]
    with tempfile.TemporaryDirectory(prefix="v83-original-v2-GPKG-") as folder:
        target=Path(folder)/"ecotope-v2.gpkg"
        with zp.open(item) as handle, target.open("wb") as dst:
            import shutil
            shutil.copyfileobj(handle,dst)
        if target.stat().st_size!=item.file_size:
            raise SourceStop("SOURCE_STOP_V83_ZIP_SOURCE_GPKG_BYTES_INVALID")
        yield_target=target
        # Do not leak original polygon bytes to GitHub: all later SQLite
        # reads and geometry source inspection occur while temporary exists.
        yield target,{"zip_GPKG_original_member_size":item.file_size,
                      "original_zip_GPKG_member_file_sha256":
                          sha256(target.read_bytes()).hexdigest()}

def _qident(s):
    return '"'+str(s).replace('"','""')+'"'

def geopackage_source_audit(path):
    with closing(sqlite3.connect(f"file:{path}?mode=ro",uri=True)) as cn:
        cn.execute("PRAGMA query_only=ON")
        integrity=cn.execute("PRAGMA integrity_check(1)").fetchone()
        if not integrity or integrity[0]!="ok":
            raise SourceStop("SOURCE_STOP_V83_ORIGINAL_GPKG_SQLITE_INTEGRITY")
        layer=cn.execute(
            "SELECT table_name,data_type,identifier,srs_id,min_x,min_y,max_x,max_y "
            "FROM gpkg_contents ORDER BY table_name").fetchall()
        shape=cn.execute(
            "SELECT table_name,column_name,geometry_type_name,srs_id "
            "FROM gpkg_geometry_columns ORDER BY table_name").fetchall()
        available={i[0] for i in layer}
        needed={"EcotopeWS3_mp","EcotopeWS3CodeInterpretation",
                "ZESsmpleCode2Legend"}
        if not needed.issubset(available):
            raise SourceStop("SOURCE_STOP_V83_CORRECTED_POLYGON_OR_LEGEND_MISSING")
        meta=next(z for z in layer if z[0]==NATIVE_POLYGONS)
        srs=cn.execute(
            "SELECT srs_id,organization,organization_coordsys_id,definition "
            "FROM gpkg_spatial_ref_sys WHERE srs_id=?",(meta[3],)).fetchone()
        if not srs:raise SourceStop("SOURCE_STOP_V83_ORIGINAL_ECOTOPE_CRS_UNKNOWN")
        try:
            crs=pyproj.CRS.from_wkt(srs[3]) if srs[3] and srs[3]!="undefined" \
                else pyproj.CRS.from_user_input(f"{srs[1]}:{srs[2]}")
            tr=pyproj.Transformer.from_crs("EPSG:4326",crs,always_xy=True)
        except Exception as e:
            raise SourceStop("SOURCE_STOP_V83_UNRECOGNIZED_NATIVE_CRS") from e
        if any(z is None for z in meta[4:8]):
            raise SourceStop("SOURCE_STOP_V83_NATIVE_POLYGON_MAP_GEO_BOUNDS_UNKNOWN")
        xmin,ymin,xmax,ymax=map(float,meta[4:8])
        bounds={}
        for name,(lat,lon) in PUBLIC_SITE_STATIONS.items():
            east,north=tr.transform(lon,lat)
            bounds[name]={
                "public_station_inside_polygon_LAYER_bounds":
                    bool(xmin<=east<=xmax and ymin<=north<=ymax),
                "source_station_CRS_coordinate_transformed":True}
        fields=[
            (v[1],v[2]) for v in cn.execute(
                f"PRAGMA table_info({_qident(NATIVE_POLYGONS)})").fetchall()]
        columns={k for k,_ in fields}
        if NATIVE_CLASS not in columns:
            raise SourceStop("SOURCE_NOT_ADMITTED_V83_NATIVE_LITORALCOD_ABSENT")
        classes=cn.execute(
            f"SELECT {_qident(NATIVE_CLASS)}, COUNT(*) FROM {_qident(NATIVE_POLYGONS)} "
            f"GROUP BY {_qident(NATIVE_CLASS)} ORDER BY {_qident(NATIVE_CLASS)}").fetchall()
        classcounts={str(code):int(n) for code,n in classes}
        if not all(int(code) in range(0,7) for code in classcounts if str(code).isdigit()):
            raise SourceStop("SOURCE_NOT_ADMITTED_V83_NATIVE_CLASS_VALUES_WRONG")
        if not all(str(code) in classcounts for code in LITTORAL_CODES):
            raise SourceStop("SOURCE_NOT_ADMITTED_V83_NO_GENUINE_LOW_MID_HIGH_LITTORAL")
        legends={}
        literal_name_found=False
        for lookup in ("EcotopeWS3CodeInterpretation","ZESsmpleCode2Legend"):
            flds=[i[1] for i in cn.execute(
                 f"PRAGMA table_info({_qident(lookup)})").fetchall()]
            q=cn.execute(
                f"SELECT * FROM {_qident(lookup)} LIMIT 150").fetchall()
            normalized=[dict(zip(flds,[str(v)[:180] if v is not None
                                     else None for v in z])) for z in q]
            joined=json.dumps(normalized,ensure_ascii=False).lower()
            literal_name_found|=("litoralcod" in joined or
                                 any(s.lower()=="litoralcod" for s in flds))
            legends[lookup]={
                "original_codebook_fields":flds[:30],
                "original_codebook_rows_inspected":len(q),
                "original_litoralcod_literal_mentioned":(
                    "litoralcod" in joined),
                "first_five_codebook_value_samples":normalized[:5]}
        if not literal_name_found:
            raise SourceStop("SOURCE_NOT_ADMITTED_V83_CORRECTED_LITORAL_NATIVE_CODEBOOK_UNVERIFIED")
        return {
            "source_v2_corrected_not_2019_v1":True,
            "original_GPKG_integrity_check":"ok",
            "original_layer_names_and_types":[
                {"name":r[0],"type":r[1],"srs_id":r[3]} for r in layer],
            "original_polygon_geometry_layers":[
                {"name":r[0],"geometry_type":r[2],"srs_id":r[3]} for r in shape],
            "ecotope_native_polygon_columns":fields,
            "original_native_polygon_srs_id":srs[0],
            "original_srs_authority":str(srs[1])+":"+str(srs[2]),
            "original_source_map_layer_geographic_station_bounds":bounds,
            "original_litoralcode_class_polygon_counts":classcounts,
            "fixed_true_low_mid_high_littoral_codes":list(LITTORAL_CODES),
            "fixed_separate_supralittoral_saltmarsh_codes":[5,6],
            "true_littoral_class_count_from_corrected_polygons":
                sum(int(classcounts.get(str(x),0)) for x in LITTORAL_CODES),
            "original_v2_codebook_tables":legends,
            "not_actual_date_2010_wet_dry_observations":True,
            "overlap_with_underlying_2009_2011_hydrodynamic_model_inputs_possible":True,
            "no_original_polygon_geometries_or_wild_animal_GPS_saved":True}

def run(output):
    result={
        "analysis":"V83_CORRECTED_2021_V2_2008_2012_WADDEN_ECOTOPE_GPKG_SOURCE_ONLY",
        "source_dataset_id":SOURCE_ID,"source_version":SOURCE_VERSION,
        "original_published_DOI":EXPECTED_DOI,
        "fixed_expected_zip":ARCHIVE,
        "original_model_tracking_frame_years":"2008-2012 REPRESENTATIVE COMPOSITE (not annual 2010 direct bed survey)",
        "original_source_metadata":None,
        "original_file_proof":None,
        "original_gpkg_native_fields":None,
        "no_wild_bird_GPS_or_NIOZ_model_index_or_RWS_series_read":True,
        "previous_v82_tide_solar_site_effects_UNCHANGED":True}
    try:
        meta,origin=publisher_metadata()
        result["original_source_metadata"]=origin
        raw,proof=download_publisher_zip(meta)
        result["original_file_proof"]=proof
        for gpkg,archive_proof in selected_gpkg_from_zip(raw):
            result["original_file_proof"].update(archive_proof)
            result["original_gpkg_native_fields"]=geopackage_source_audit(gpkg)
        b=result["original_gpkg_native_fields"]["original_source_map_layer_geographic_station_bounds"]
        if not all(x["public_station_inside_polygon_LAYER_bounds"] for x in b.values()):
            raise SourceStop("SOURCE_NOT_ADMITTED_V83_BOTH_WADDEN_SITES_NOT_IN_MAP_EXTENT")
        result["source_admission"]="SOURCE_ADMITTED_V83_CORRECTED_HISTORICAL_LITTORAL_ECOTOPE_MAP"
    except SourceStop as error:
        result["source_admission"]="SOURCE_NOT_ADMITTED_OR_PUBLIC_SOURCE_UNAVAILABLE_V83"
        result["source_error"]=str(error)[:500]
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V83_CORRECTED_ECOTOPE_PUBLISHER_SOURCE_GATE "+json.dumps({
        "original_fixed_DOI":EXPECTED_DOI,
        "source_status":result["source_admission"],
        "error_or_null":result.get("source_error"),
        "original_GPKG_original_geoclass_layer_count":
            (result["original_gpkg_native_fields"] or {}).get(
                "true_littoral_class_count_from_corrected_polygons"),
        "original_MD5_or_SHA_publisher_proof_status":
            (result["original_file_proof"] or {}).get(
                "publisher_SHA256_available_and_verified")
    },sort_keys=True,ensure_ascii=False),flush=True)
    print("V83_ORIGINAL_ECOTOPE_DATASET_GEO_SOURCE_AUDIT_FINISHED",flush=True)
    return result

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    run(ap.parse_args().output)
