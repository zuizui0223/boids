"""v88 authentic independently collected four-shorebird China Dryad source audit.

SOURCE ONLY, not a tide×sunlight or habitat preference result.
Dryad 2026 Jun 4 published data, doi:10.5061/dryad.51c59zwm3.
DO NOT fabricate Leizhou local measured tide or treat field survey
Tide rise/fall observation labels as the GPS physical tide at UTC time.
Only official public Dryad API; 401/403 explicitly unavailable, no
credential bypass or invented download URL/record SHA.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import os
import re
import stat
import zipfile
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
from urllib.error import HTTPError,URLError
from urllib.parse import quote,urlparse
from urllib.request import Request,urlopen

DOI="10.5061/dryad.51c59zwm3"
DRYAD_DOI="doi:"+DOI
ENCODED=quote(DRYAD_DOI,safe="")
API="https://datadryad.org/api/v2"
PUBLIC_VERSION_DATE="2026-06-04"
EXPECTED_ARCHIVE="Raw_data.zip"
EXPECTED_README="README.md"
MAX_JSON=8_000_000
MAX_PACKAGED_DOWNLOAD=12_000_000
MAX_ZIP_MEMBER=100_000_000
MAX_NESTED_BYTES=12_000_000
ORIGINAL_EXPECTED_TAXA={
    "Tringa totanus":9,
    "Pluvialis squatarola":3,
    "Charadrius leschenaultii":2,
    "Calidris canutus":2}
REQUIRED_GPS_COLS={
    "S/N","Collecting time","Longitude","Latitude"}
README_REQUIRED=("Tracking", "habitat")
SENSITIVE_ORIGINAL_GPS_COLS={
    "S/N","UUID","Collecting time","Transmitting time",
    "Latitude","Longitude","Altitude","Geoid height"}

class SourceStop(Exception):pass

def _get_official(uri,limit,*,client=None):
    if not uri.startswith("https://"):
        raise SourceStop("SOURCE_STOP_V88_NO_NON_HTTPS_ORIGINAL_URLS")
    # Only the published Dryad API host, or the literal public host
    # returned as a true Dryad download redirect. No guessing.
    url=urlparse(uri)
    if url.hostname!="datadryad.org":
        raise SourceStop("SOURCE_STOP_V88_NOT_OFFICIAL_DRYAD_API")
    if client is not None:
        return client(uri,limit)
    try:
        with urlopen(Request(uri,headers={
            "User-Agent":"boids-v88-original-leizhou-Dryad-source-20261109/1.0",
            "Accept":"application/json,application/zip,*/*"}),
            timeout=90) as r:
            content=r.read(limit+1)
            if len(content)>limit:
                raise SourceStop("SOURCE_STOP_V88_DRYAD_SOURCE_MORE_THAN_CAP")
            if urlparse(r.geturl()).scheme!="https":
                raise SourceStop("SOURCE_STOP_V88_DRYAD_INSECURE_REDIRECT")
            return content,{"http_status":int(r.status),
                            "content_type":r.headers.get("content-type",""),
                            "final_download_https":True}
    except HTTPError as e:
        raise SourceStop(
           "SOURCE_UNAVAILABLE_V88_ORIGINAL_DRYAD_PUBLIC_HTTP_"+str(e.code)) from e
    except (URLError,TimeoutError) as e:
        raise SourceStop(
           "SOURCE_UNAVAILABLE_V88_ORIGINAL_DRYAD_TRANSPORT_"+str(e)[:110]) from e

def _json(uri,client=None):
    payload,_=_get_official(uri,MAX_JSON,client=client)
    try:
        return json.loads(payload)
    except (ValueError,TypeError) as e:
        raise SourceStop("SOURCE_STOP_V88_ORIGINAL_DRYAD_API_NOT_JSON") from e

def _records(x,names):
    if isinstance(x,list):return x
    if isinstance(x,dict):
        for name in names:
            if isinstance(x.get(name),list):return x[name]
        embedded=x.get("_embedded")
        if isinstance(embedded,dict):
            for value in embedded.values():
                if isinstance(value,list):return value
        if isinstance(x.get("data"),list):return x["data"]
    return []

def _field_id(x):
    """Accept only publisher actual numeric ID or official version/file link.

    HAL published Dryad versions may expose ID only in _links.self.href,
    not top-level fields. Never confuse versionNumber (ordinal) with ID.
    """
    for field in ("id","versionId","fileId"):
        a=x.get(field)
        if a is not None and str(a).isdigit():
            return str(a)
        if isinstance(a,str):
            found=re.search(r"/(?:versions|files)/(\d+)(?:/|$|\?)",a)
            if found:return found.group(1)
    for k in ("_links","links"):
        value=x.get(k)
        if not isinstance(value,dict):continue
        for link in value.values():
            strings=[]
            if isinstance(link,str):strings=[link]
            if isinstance(link,dict):
                strings=[str(v) for n,v in link.items() if n in ("href","url")]
            for url in strings:
                found=re.search(r"/(?:versions|files)/(\d+)(?:/|$|\?)",url)
                if found:return found.group(1)
    return None

def _literal_publisher_original_file_links(file):
    """Only exact original links literally present in Dryad file metadata."""
    out={}
    for key in ("downloadUrl","download_url","url"):
        uri=file.get(key)
        if isinstance(uri,str) and uri.startswith(("https://datadryad.org/","/api/")):
            out[key]=uri
    raw=file.get("_links") or file.get("links") or {}
    if isinstance(raw,dict):
        for key,value in raw.items():
            if not re.search("download|file_stream",str(key),re.I):
                continue
            val=value.get("href") if isinstance(value,dict) else value
            if isinstance(val,str) and val.startswith(("https://datadryad.org/","/api/")):
                out[str(key)[:60]]=val
    return out

def metadata_source(*,client=None):
    """Only actual published DOI/versions/file IDs, never fabricated."""
    root=_json(f"{API}/datasets/{ENCODED}",client)
    if not isinstance(root,dict):
        raise SourceStop("SOURCE_STOP_V88_DRYAD_PUBLISHED_DATASET_NOT_OBJECT")
    canonical=str(root.get("identifier") or root.get("doi") or "")
    if DOI.lower() not in canonical.lower():
        raise SourceStop("SOURCE_STOP_V88_PUBLIC_DOI_NOT_THE_REGISTERED_SOURCE")
    version=_json(f"{API}/datasets/{ENCODED}/versions",client)
    versions=_records(version,("versions","items"))
    if not versions:
        raise SourceStop("SOURCE_STOP_V88_NO_PUBLIC_DATASET_VERSION_METADATA")
    # Use ORIGINAL 2026-06-04 version, not a potentially changed later
    # file set. If server has only one visible version, preserve its
    # observed publication date verbatim and source-stop if ambiguous.
    exact=[]
    for z in versions:
        if not isinstance(z,dict):continue
        dates=[str(z.get(k) or "")[:10] for k in (
            "versionPublicationDate","publicationDate",
            "publication_date","createdAt","updatedAt")]
        if PUBLIC_VERSION_DATE in dates:exact.append(z)
    if len(exact)==1:chosen=exact[0]
    elif len(versions)==1:chosen=versions[0]
    else:
        raise SourceStop("SOURCE_STOP_V88_PUBLIC_ORIGINAL_VERSION_AMBIGUOUS")
    ver_id=_field_id(chosen)
    if not isinstance(ver_id,(int,str)) or not str(ver_id).isdigit():
        raise SourceStop("SOURCE_STOP_V88_DRYAD_ORIGINAL_VERSION_ID_UNKNOWN")
    files_response=_json(f"{API}/versions/{ver_id}/files",client)
    files=_records(files_response,("files","items"))
    names=Counter()
    public=[]
    for f in files:
        if not isinstance(f,dict):continue
        name=f.get("path") or f.get("filename") or f.get("name")
        if not isinstance(name,str):continue
        base=PurePosixPath(name).name
        if base not in (EXPECTED_ARCHIVE,EXPECTED_README):continue
        fid=_field_id(f)
        size=f.get("size")
        if fid is None or not str(fid).isdigit():
            raise SourceStop("SOURCE_STOP_V88_ORIGINAL_DRYAD_FILE_IDENTIFIER")
        if not isinstance(size,(int,float)) or size<=0 or size>MAX_PACKAGED_DOWNLOAD:
            raise SourceStop("SOURCE_STOP_V88_ORIGINAL_FILE_SIZE_MISSING_OR_ABSURD")
        names[base]+=1
        public.append({
            "true_original_filename":base,
            "actual_Dryad_file_id":str(fid),
            "source_reported_bytes":int(size),
            "source_checksum_if_metadata_gives_it":str(
               f.get("digest") or f.get("sha256") or
               f.get("checksum") or "")[:128] or None,
            "original_file_metadata_available_top_level_fields":
                sorted(str(k) for k in f.keys())[:30],
            "actual_original_publisher_advertised_public_file_download_links":
                _literal_publisher_original_file_links(f)})
    if names[EXPECTED_ARCHIVE]!=1 or names[EXPECTED_README]!=1:
        raise SourceStop("SOURCE_STOP_V88_ORIGINAL_DRYAD_TWO_FILES_NOT_IN_MANIFEST")
    return {
        "source":root,
        "original_chosen_version":chosen,
        "original_version_ID":str(ver_id),
        "files":public,
        "sanitized_receipt":{
            "original_publisher":"Dryad",
            "original_DOI":DOI,
            "original_stated_publication_date":PUBLIC_VERSION_DATE,
            "chosen_Dryad_version_ID":str(ver_id),
            "metadata_original_title":str(root.get("title") or "")[:160],
            "original_source_files":public,
            "source_metadata_only_no_actual_raw_animal_time_or_habitat_Y":True}}

def zip_members(blob,*,max_member=MAX_ZIP_MEMBER):
    try:source=zipfile.ZipFile(io.BytesIO(blob))
    except (zipfile.BadZipFile,OSError) as e:
        raise SourceStop("SOURCE_STOP_V88_ORIGINAL_DRYAD_NOT_ZIP") from e
    allmembers={}
    for info in source.infolist():
        path=PurePosixPath(info.filename.replace("\\","/"))
        if (info.filename.startswith(("/","\\")) or
            ".." in path.parts or
            ((info.external_attr>>16)&0o170000)==stat.S_IFLNK or
            info.file_size>max_member or info.file_size<0):
            raise SourceStop("SOURCE_STOP_V88_ORIGINAL_PUBLIC_ZIP_UNSAFE")
        if not info.is_dir():
            allmembers[info.filename]=info
    return source,allmembers

def _gps_time(raw):
    if not raw or not raw.endswith("Z"):
        raise ValueError("Original GPS collecting-time is not UTC ISO-8601 Z")
    x=datetime.fromisoformat(raw[:-1]+"+00:00")
    if x.tzinfo is None or x.utcoffset().total_seconds()!=0:
        raise ValueError("Original GPS collected-time UTC parse fails")
    return x

def raw_zip_source_summary(blob):
    """Anonymous source-only shape, never animal-specific habitat outcomes."""
    ziproot,names=zip_members(blob)
    gps_candidates=[
        k for k in names if
        "tracking data/" in k.lower().replace("\\","/") and
        k.lower().endswith(".csv")]
    if len(gps_candidates)!=1:
        raise SourceStop("SOURCE_STOP_V88_NO_EXACT_ONE_ORIGINAL_GPS_CSV")
    mapping=[
        k for k in names if PurePosixPath(k).name.lower()=="sn to id.txt"]
    legend=[
        k for k in names if PurePosixPath(k).name.lower()=="habitat mapping scheme.txt"]
    maps=[k for k in names if PurePosixPath(k).name.lower()=="habitat map.tif"]
    if not (len(mapping)==len(legend)==len(maps)==1):
        raise SourceStop("SOURCE_STOP_V88_ORIGINAL_GPS_TAG_MAPPING_HABITAT_OR_LEGEND")
    source_headers={}
    for kind,name in (("tag_mapping",mapping[0]),
                      ("habitat_class_legend",legend[0])):
        data=ziproot.read(name)
        if len(data)>30000:
            raise SourceStop("SOURCE_STOP_V88_TAG_OR_LEGEND_TEXT_TOO_LARGE")
        source_headers[kind]={
            "original_source_member_bytes":len(data),
            "original_source_member_SHA256_local":hashlib.sha256(data).hexdigest(),
            "nonempty_lines":sum(bool(l.strip()) for l in
                data.decode("utf-8-sig",errors="replace").splitlines())}
    native=ziproot.read(gps_candidates[0])
    if len(native)>MAX_ZIP_MEMBER:
        raise SourceStop("SOURCE_STOP_V88_ORIGINAL_GPS_TOO_LARGE")
    csv_reader=csv.DictReader(io.StringIO(
         native.decode("utf-8-sig",errors="strict")))
    fields=csv_reader.fieldnames or []
    if not REQUIRED_GPS_COLS.issubset(fields):
        raise SourceStop("SOURCE_STOP_V88_GPS_COLLECTING_TIME_AND_GEO_SCHEMA_CHANGED")
    # Only SOURCE temporal coverage, GPS source serial count, accuracy;
    # original serials/UUID/time/locations never serialized.
    seen=set();monthly=Counter();yearly=Counter()
    valid=0;bad=Counter();n=0;sn=Counter()
    horacc=[];bounds=[math.inf,math.inf,-math.inf,-math.inf]
    for row in csv_reader:
        n+=1
        try:
            snv=(row["S/N"] or "").strip()
            if not snv:raise ValueError("GPS serial missing")
            t=_gps_time((row["Collecting time"] or "").strip())
            lat=float(row["Latitude"]);lon=float(row["Longitude"])
            if not(math.isfinite(lat) and math.isfinite(lon) and
                   -90<=lat<=90 and -180<=lon<=180):
                raise ValueError("GPS coords invalid")
            if t.year not in (2019,2020,2021):
                raise ValueError("GPS study source year outside published")
            if "HorAccuracy" in row and row["HorAccuracy"]:
                a=float(row["HorAccuracy"])
                if math.isfinite(a) and a>=0:horacc.append(a)
        except (ValueError,TypeError,OverflowError) as e:
            bad[str(e)[:60]]+=1
            continue
        valid+=1
        sn[snv]+=1
        yearly[t.year]+=1
        monthly[f"{t.year}-{t.month:02d}"]+=1
        bounds[0]=min(bounds[0],lat)
        bounds[1]=min(bounds[1],lon)
        bounds[2]=max(bounds[2],lat)
        bounds[3]=max(bounds[3],lon)
    if valid<10 or len(sn)<2:
        raise SourceStop("SOURCE_STOP_V88_NOT_ENOUGH_PUBLIC_ORIGINAL_GPS_SOURCE")
    # Original species mapping source requires native SN to id.txt parse,
    # cannot safely infer species IDs from just serial numbers.
    prefix_code=ziproot.read(mapping[0]).decode(
        "utf-8-sig",errors="replace")
    species_matches={
        label:bool(re.search(
            re.escape(label),prefix_code,re.I)) for label in ORIGINAL_EXPECTED_TAXA}
    source_map_name=maps[0]
    return {
        "original_raw_zip_members_files_count":len(names),
        "original_tracking_GPS_CSV_basename":PurePosixPath(gps_candidates[0]).name,
        "original_GPS_native_header_names":fields[:50],
        "original_GPS_source_raw_rows":n,
        "original_GPS_source_valid_UTC_WGS84_rows":valid,
        "original_GPS_source_bad_rows_by_reason":dict(bad),
        "original_GPS_source_device_serial_count_NOT_equivalent_to_independent_birds":
            len(sn),
        "original_2019_2020_2021_calendar_months_source_counts":
            dict(sorted(monthly.items())),
        "original_years":dict(sorted(yearly.items())),
        "GPS_horizontal_accuracy_available_count":len(horacc),
        "source_hor_accuracy_m_quantiles_if_present":(
           [float(v) for v in __import__("numpy").quantile(horacc,[0.5,0.95])]
           if horacc else None),
        "GPS_source_latlon_bbox_rounded_0p25_degrees":[
            math.floor(bounds[0]*4)/4,math.floor(bounds[1]*4)/4,
            math.ceil(bounds[2]*4)/4,math.ceil(bounds[3]*4)/4],
        "source_tag_and_raster_legend_headers_only":source_headers,
        "original_source_map_GeoTIFF_filename":PurePosixPath(source_map_name).name,
        "original_native_tag_mapping_mentions_latin_name_source":species_matches,
        "individual_species_key_source_NOT_INFERRED_without_README_and_mapping":True,
        "original_global_IDs_exact_coordinates_and_observation_clock_NOT_RELEASED":True,
        "no_tide_solar_habitat_outcome_was_scored":True}

def run(output):
    out={
        "analysis":"V88_ORIGINAL_LEIZHOU_CHINA_FOUR_SHOREBIRD_DRYAD_PUBLIC_GPS_HABITAT_SOURCE_ONLY",
        "frozen_pre_source_protocol":"docs/V88_FROZEN_LEIZHOU_4_SHOREBIRD_DRYAD_GPS_HABITAT_SOURCE_ONLY.md",
        "expected_original_DOI":DOI,
        "expected_original_source_research_taxa":ORIGINAL_EXPECTED_TAXA,
        "public_Dryad_source_API_status":"NOT_TESTED",
        "no_original_measured_2019_2021_Leizhou_real_tide_gauge_available":True,
        "no_external_tide_by_solar_GPS_behavior_outcome_estimated":True,
        "not_2010_Wadden_same_species_same_coast":True}
    try:
        md=metadata_source()
        out["original_publisher_metadata"]=md["sanitized_receipt"]
        out["public_Dryad_source_API_status"]="PUBLISHED_METADATA_AUTHENTICATED"
        # EXACT official public dataset package download, no guessed files.
        path=f"{API}/datasets/{ENCODED}/download"
        binary,transport=_get_official(path,MAX_PACKAGED_DOWNLOAD)
        datasetzip,allfiles=zip_members(binary)
        bybase=defaultdict(list)
        for entry in allfiles:
            bybase[PurePosixPath(entry).name].append(entry)
        if len(bybase[EXPECTED_ARCHIVE])!=1 or len(bybase[EXPECTED_README])!=1:
            raise SourceStop("SOURCE_STOP_V88_PUBLIC_DATASET_PACKAGE_NOT_ORIGINAL_TWO_FILES")
        archive=datasetzip.read(bybase[EXPECTED_ARCHIVE][0])
        readme=datasetzip.read(bybase[EXPECTED_README][0])
        if len(archive)>MAX_NESTED_BYTES or len(readme)>100_000:
            raise SourceStop("SOURCE_STOP_V88_ORIGINAL_BUNDLED_FILES_WRONG_SIZE")
        out["source_downloaded_original_public_dataset_package"]={
            "actual_public_Dryad_dataset_archive_bytes":len(binary),
            "original_dataset_package_sha256_LOCAL_not_publisher":
                hashlib.sha256(binary).hexdigest(),
            "original_nested_Raw_data_zip_bytes":len(archive),
            "original_nested_Raw_data_zip_sha256_LOCAL_not_publisher":
                hashlib.sha256(archive).hexdigest(),
            "source_original_README_size":len(readme),
            "source_original_README_SHA256_LOCAL_not_publisher":
                hashlib.sha256(readme).hexdigest(),
            "all_original_source_member_count":len(allfiles),
            "anonymized_original_source_member_basenames":
                sorted([PurePosixPath(x).name for x in allfiles]),
            "not_publisher_certified_Sha_if_no_true_provider_digest":True}
        out["original_GPS_and_habitat_source_preflight"]=raw_zip_source_summary(archive)
        out["public_Dryad_source_API_status"]="ORIGINAL_PUBLIC_DRYAD_ZIP_GPS_SOURCE_OBTAINED_SOURCE_QA_ONLY"
    except SourceStop as e:
        out["source_QA_blocker"]=str(e)[:300]
        if out["public_Dryad_source_API_status"]=="NOT_TESTED":
            out["public_Dryad_source_API_status"]="ORIGINAL_DRYAD_METADATA_NOT_PUBLICLY_ACCESSIBLE"
        else:
            out["public_Dryad_source_API_status"]="ORIGINAL_DRYAD_PUBLIC_PACKAGE_OR_STRUCTURED_SOURCE_STOP"
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("V88_ORIGINAL_LEIZHOU_DRYAD_FOUR_SHOREBIRD_PUBLIC_SOURCE_RESULT "+
          json.dumps({
            "public_source_status":out["public_Dryad_source_API_status"],
            "file_or_source_blocker":out.get("source_QA_blocker"),
            "actual_metadata_file_names":(
                [f["true_original_filename"] for f in out.get(
                    "original_publisher_metadata",{}).get(
                    "original_source_files",[])]),
            "native_source_only_GPS_rows":out.get(
                "original_GPS_and_habitat_source_preflight",{}).get(
                "original_GPS_source_valid_UTC_WGS84_rows"),
            "no_fabricated_local_tide_or_bird_effect":True},
                sort_keys=True),flush=True)
    print("V88_GENUINE_CHINA_OUT_OF_WADDEN_FOUR_SPECIES_SOURCE_AUDIT_COMPLETED",
          flush=True)
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    run(p.parse_args().output)
