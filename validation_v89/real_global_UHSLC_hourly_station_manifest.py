"""v89 global UHSLC hourly tide-gauge original STATION source manifest.

SOURCE ONLY: no original waterlevel series, no animal data, no ecological
effect. Global RQDS hourly station/record index via official UHSLC ERDDAP.
Original station metadata is public; do not conflate datum segments
record_id with independent station uhslc_id. A public ERDDAP mirror may
be used only when the originally fixed primary endpoint is unavailable,
not to choose an environmentally favorable result.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
import csv,io,json,math,re
from urllib.parse import quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

PROVIDERS=(
    ("primary_UHSLC","https://uhslc.soest.hawaii.edu/erddap/tabledap/global_hourly_rqds"),
    ("fixed_public_PacIOOS_mirror","https://pae-paha.pacioos.hawaii.edu/erddap/tabledap/uhslc_global_hourly_rqds"))
FIXED_FIELDS=("uhslc_id","record_id","station_name","station_country",
              "latitude","longitude")
SOURCE_YEAR_FOR_FUTURE_PILOT=2019
SOURCE_2019_LAT_BANDS_DEGREES=15
MIN_SOURCE_STATIONS_WITH_VALID_COORDS=30
MAX_SOURCE_CSV_BYTES=12_000_000
EQUATORIAL_LAT_BAND_KEY="0"
PUBLIC_ORIGINAL_SOURCE_END="2024-12-31T23:00:00Z"
REFERENCE_UNITS="millimeters"
ORIGINAL_QC_QUALITY=4

class SourceUnavailable(Exception):pass

def source_URL(base):
    if not any(base==registered for _,registered in PROVIDERS):
        raise SourceUnavailable("SOURCE_STOP_V89_NON_FROZEN_PUBLIC_UHSLC_ENDPOINT")
    return (base+".csv?"+",".join(FIXED_FIELDS)+"&distinct()")

def _download(url,*,fetcher=None):
    if fetcher is not None:return fetcher(url)
    try:
        with urlopen(Request(url,headers={
            "User-Agent":"boids-v89-global-original-UHSLC-RQDS-station-source/1.0",
            "Accept":"text/csv"}),timeout=75) as response:
            raw=response.read(MAX_SOURCE_CSV_BYTES+1)
            if len(raw)>MAX_SOURCE_CSV_BYTES:
                raise SourceUnavailable("SOURCE_STOP_V89_ORIGINAL_UHSLC_SOURCE_TOO_LARGE")
            if response.status!=200:
                raise SourceUnavailable("SOURCE_STOP_V89_ORIGINAL_UHSLC_HTTP_NOT_200")
            return raw
    except (HTTPError,URLError,TimeoutError) as e:
        raise SourceUnavailable("SOURCE_UNAVAILABLE_V89_ORIGINAL_UHSLC_ERDDAP_"+
                                str(e)[:160]) from e

def _normalize_original_lon(lon):
    """Original UHSLC 0..360 degrees East to meaningful signed longitude."""
    return ((lon+180.)%360.)-180.

def parse_original_station_manifest(raw):
    reader=csv.DictReader(io.StringIO(
        raw.decode("utf-8-sig",errors="strict")))
    headers=reader.fieldnames or []
    if not set(FIXED_FIELDS).issubset(headers):
        raise SourceUnavailable("SOURCE_STOP_V89_UHSLC_ORIGINAL_STATION_FIELDS_MISSING")
    records=[]
    skipped=Counter()
    seen=set()
    for row in reader:
        try:
            i=int(row["uhslc_id"])
            record=int(row["record_id"])
            lat=float(row["latitude"])
            lon=float(row["longitude"])
            name=(row["station_name"] or "").strip()
            country=(row["station_country"] or "").strip()
        except (ValueError,TypeError):
            skipped["CSV_headers_units_or_missing_ID"]+=1
            continue
        if (i<=0 or record<=0 or not name or
            not(math.isfinite(lat) and math.isfinite(lon)) or
            not(-90<=lat<=90 and 0<=lon<=360)):
            skipped["invalid_native_original_station_coordinate_or_name"]+=1
            continue
        key=(i,record)
        if key in seen:
            skipped["duplicated_original_station_record_segment"]+=1
            continue
        seen.add(key)
        records.append({
            "uhslc_id":i,"record_id":record,
            "original_station_name":name,
            "original_station_country":country,
            "latitude":lat,
            "original_longitude_0_360":lon,
            "longitude_signed":_normalize_original_lon(lon)})
    if not records:
        raise SourceUnavailable("SOURCE_STOP_V89_NO_GENUINE_UHSLC_STATION_METADATA")
    records.sort(key=lambda z:(z["uhslc_id"],z["record_id"]))
    return records,dict(skipped)

def _latitude_band(lat):
    """Independent SOURCE band, no tide/daylight outcome inspection."""
    hemisphere=("N" if lat>=0 else "S")
    lo=int(math.floor(abs(lat)/SOURCE_2019_LAT_BANDS_DEGREES)*
           SOURCE_2019_LAT_BANDS_DEGREES)
    return f"{hemisphere}_{lo:02d}_{lo+SOURCE_2019_LAT_BANDS_DEGREES:02d}"

def aggregate_station_source(records):
    groups=defaultdict(list)
    country=Counter()
    bands=defaultdict(set)
    hemi=Counter()
    for record in records:
        groups[record["uhslc_id"]].append(record)
        country[record["original_station_country"] or "UNKNOWN"]+=1
        bands[_latitude_band(record["latitude"])].add(record["uhslc_id"])
    station_bands={
        b:{"original_unique_station_ID_count":len(ids),
           "original_station_IDs_ascending":sorted(ids)}
        for b,ids in sorted(bands.items())}
    original_unique=len(groups)
    pilot=[{
        "original_latitude_band":band,
        "candidate_smallest_uhslc_id_source_only":
            min(info["original_station_IDs_ascending"]),
        "coverage_in_2019_not_yet_confirmed":True}
        for band,info in station_bands.items()]
    return {
        "original_unique_physical_UHSLC_stations_by_station_ID":original_unique,
        "original_total_versioned_station_datum_records":len(records),
        "original_station_IDs_with_more_than_one_datum_version":
            sum(len(group)>1 for group in groups.values()),
        "original_original_station_count_BY_country_field":{
            c:n for c,n in sorted(country.items())},
        "original_latitude_15deg_source_bands":station_bands,
        "original_global_latitude_bounds":
            [min(x["latitude"] for x in records),
             max(x["latitude"] for x in records)],
        "original_pilot_no_waterheight_selection_one_station_per_lat_band":
            pilot,
        "source_not_yet_original_2019_hourly_coverage_verified":True,
        "original_hourly_RQDS_sea_level_mm_source_NOT_FETCHED":True}

def run(output,manifest_output=None):
    result={
        "analysis":"V89_GLOBAL_ORIGINAL_UHSLC_RESEARCH_QUALITY_HOURLY_TIDE_GAUGE_STATION_SOURCE_FIRST",
        "frozen_protocol":"docs/V89_FROZEN_GLOBAL_TIDE_SOLAR_MACROECOLOGY_MAIN_REFRAME.md",
        "fixed_main_original_RQDS_hourly_observation_quality":ORIGINAL_QC_QUALITY,
        "fixed_second_scale_original_global_intertidal_map":
            "Global Intertidal Change v1.2 (1999-2019) 30m true flat presence, separate source",
        "underlying_source_requested":"original_UHSLC_station_manifest_only",
        "fixed_global_source_providers":[{"id":n,"url":url}
                                         for n,url in PROVIDERS],
        "none_original_wild_GPS_RWS_2island_or_global_hourly_waterheights_scored":True}
    errors={}
    candidates=None
    for name,url in PROVIDERS:
        try:
            raw=_download(source_URL(url))
            station,skipped=parse_original_station_manifest(raw)
            if len({x["uhslc_id"] for x in station})<
                MIN_SOURCE_STATIONS_WITH_VALID_COORDS:
                raise SourceUnavailable("SOURCE_STOP_V89_TOO_FEW_GENUINE_GLOBAL_SOURCE_STATIONS")
            result["original_source_used"]=name
            result["original_source_provider_download_SHA256_local_not_uploader_certified"]=sha256(raw).hexdigest()
            result["original_source_download_bytes"]=len(raw)
            result["original_malformed_or_duplicate_station_source_rows"]=skipped
            candidates=station
            break
        except SourceUnavailable as e:
            errors[name]=str(e)[:350]
    result["source_attempts_failure_if_any"]=errors
    if candidates is not None:
        result["original_global_station_source"]=aggregate_station_source(candidates)
        result["source_status"]="SOURCE_ADMITTED_V89_ORIGINAL_GLOBAL_UHSLC_HOURLY_STATION_MANIFEST"
        # Original gauge metadata is PUBLIC science, not personal tracking.
        # Full exact station_ID and datum version list lives in artifact,
        # helping inspect reproducibility and reconstruct pilot choice.
        if manifest_output is not None:
            p=Path(manifest_output);p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps({
                "source_original_provider":result["original_source_used"],
                "source_original_manifest_raw_SHA":result[
                    "original_source_provider_download_SHA256_local_not_uploader_certified"],
                "original_public_UHSLC_stations_and_datum_segments":candidates,
                "no_measured_sea_levels_or_wild_animal_positions_present":True},
                sort_keys=True,indent=2)+"\n")
    else:
        result["source_status"]="SOURCE_UNAVAILABLE_V89_GENUINE_UHSLC_GLOBAL_STATION_MANIFEST"
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    src=result.get("original_global_station_source") or {}
    print("V89_REAL_GLOBAL_UHSLC_TIDE_STATION_MACRO_SOURCE_FIRST "+
          json.dumps({
           "status":result["source_status"],
           "original_global_UHSLC_stations":
               src.get("original_unique_physical_UHSLC_stations_by_station_ID"),
           "original_reference_datum_segmented_records":
               src.get("original_total_versioned_station_datum_records"),
           "source_original_latitude_band_count":
               len(src.get("original_latitude_15deg_source_bands") or {}),
           "original_station_source_latitude_range":
               src.get("original_global_latitude_bounds"),
           "source_failures":errors,
           "NO_observed_hourly_coincidence_or_animal_effect_estimated":True},
           sort_keys=True),flush=True)
    print("V89_MACRO_GLOBAL_ORIGINAL_GAUGE_STATION_SOURCE_COMPLETED",flush=True)
    return result

if __name__=="__main__":
    import argparse
    args=argparse.ArgumentParser()
    args.add_argument("--output",required=True)
    args.add_argument("--station-manifest-output")
    a=args.parse_args()
    run(a.output,a.station_manifest_output)
