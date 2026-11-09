"""v89 genuine different-species 2018 WATLAS source-first audit.

Published Bijleveld et al. Animal Biotelemetry 2022 supplementary data:
Additional file 13 sanderling, file 14 red knot. True publisher links are
pre-frozen in docs/V89_FROZEN_ORIGINAL_WATLAS_KNOT_SANDERLING_TRUE_TIDE_COLUMNS_SOURCE.md.
Actual source TIME is Unix UTC seconds, X/Y UTM31N metres. Data-derived
tidaltime and waterlevel at West Terschelling are NOT automatically an
independently verified 2018 RWS local gauge or a causal tide response.
No wild movement / habitat / speed outcomes scored. No individual TAG,
exact location or timestamps emitted, only anonymous source coverage QA.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import tempfile
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse
from urllib.request import Request,urlopen

from pyproj import Transformer
from astral import Observer
from astral.sun import elevation

ORIGINAL_PAPER_DOI="10.1186/s40317-022-00307-w"
FIGSHARE_ORIGINAL={
    "Red_knot":{
      "original_species":"Calidris canutus",
      "article_id":26553446,
      "doi":"10.6084/m9.figshare.26553446.v1",
      "springer_publisher_csv":
        "https://media.springernature.com/original/springer-static/esm/"
        "art%3A10.1186%2Fs40317-022-00307-w/MediaObjects/"
        "40317_2022_307_MOESM14_ESM.csv",
      "additional_file":14},
    "Sanderling":{
      "original_species":"Calidris alba",
      "article_id":26553443,
      "doi":"10.6084/m9.figshare.26553443.v1",
      "springer_publisher_csv":
        "https://media.springernature.com/original/springer-static/esm/"
        "art%3A10.1186%2Fs40317-022-00307-w/MediaObjects/"
        "40317_2022_307_MOESM13_ESM.csv",
      "additional_file":13}}
ORIGINAL_REQUIRED=("tag","time","x","y","nbs",
                   "tideid","tidaltime","waterlevel")
ORIGINAL_OPTIONAL=("varx","vary","covxy","ts")
MAX_PUBLISHER_CSV_BYTES=120_000_000
MAX_PUBLISHER_FIGSHARE_METADATA=1_500_000
MAX_ORIGINAL_SOURCE_ROWS=3_000_000
MIN_BIRD_WATLAS_RECEIVERS=3
TRACKING_SOURCE_YEAR=2018
LOCAL_MIDNIGHT_SOURCE_SOLAR_CUTOFF_DEG=3
ORIGINAL_PLAUSIBLE_LONGITUDE=(4.0,7.0)
ORIGINAL_PLAUSIBLE_LATITUDE=(52.0,55.0)
WATERLEVEL_SOURCE_CM=(-500.,500.)
TIDETIME_SOURCE_MINUTES=(-600.,600.)

class SourceStop(Exception):pass

def _fetch_literal_public_source(url,limit,*,allowed_metadata_host=None):
    parsed=urlparse(url)
    if parsed.scheme!="https":
        raise SourceStop("SOURCE_STOP_V89_NON_HTTPS_ORIGINAL_PUBLISHER")
    if allowed_metadata_host and parsed.hostname!=allowed_metadata_host:
        raise SourceStop("SOURCE_STOP_V89_NON_ORIGINAL_METADATA_HOST")
    try:
        with urlopen(Request(url,headers={
          "User-Agent":"boids-v89-source-only-original-WATLAS-data/1.0",
          "Accept":"text/csv,application/json,application/octet-stream,*/*"}),
          timeout=100) as response:
            content=response.read(limit+1)
            if len(content)>limit:
                raise SourceStop("SOURCE_STOP_V89_PUBLISHED_CSV_EXCEEDS_120MB")
            if urlparse(response.geturl()).scheme!="https":
                raise SourceStop("SOURCE_STOP_V89_ORIGINAL_PUBLISHER_REDIRECT_INSECURE")
            return content,{"source_public_HTTP":int(response.status),
                            "source_final_download_https":True}
    except (HTTPError,URLError,TimeoutError) as ex:
        raise SourceStop(
            "SOURCE_UNAVAILABLE_V89_ORIGINAL_PUBLISHER "+
            type(ex).__name__+" "+str(ex)[:150]) from ex

def figshare_actual_provider_metadata(spec,*,fetch=_fetch_literal_public_source):
    article=int(spec["article_id"])
    url=f"https://api.figshare.com/v2/articles/{article}"
    raw,_=fetch(url,MAX_PUBLISHER_FIGSHARE_METADATA,
                allowed_metadata_host="api.figshare.com")
    try:j=json.loads(raw)
    except (ValueError,TypeError) as ex:
        raise SourceStop("SOURCE_STOP_V89_FIGSHARE_ORIGINAL_PUBLIC_API_NOT_JSON") from ex
    if not isinstance(j,dict) or int(j.get("id") or 0)!=article:
        raise SourceStop("SOURCE_STOP_V89_FIGSHARE_WRONG_ARTICLE")
    doi=str(j.get("doi") or "")
    if doi and doi.lower().replace("https://doi.org/","")!=spec["doi"]:
        raise SourceStop("SOURCE_STOP_V89_FIGSHARE_WRONG_VERSIONED_SOURCE_DOI")
    all_files=j.get("files") or []
    matches=[f for f in all_files
             if isinstance(f,dict) and
             (str(f.get("name") or "").lower().endswith(".csv"))]
    if len(matches)!=1:
        raise SourceStop("SOURCE_STOP_V89_PUBLISHED_FIGSHARE_EXACT_ONE_CSV_REQUIRED")
    f=matches[0]
    original_download=f.get("download_url")
    if not isinstance(original_download,str) or not original_download.startswith("https://"):
        raise SourceStop("SOURCE_STOP_V89_FIGSHARE_NO_AUTHENTIC_DOWNLOAD_URL")
    size=int(f.get("size") or 0)
    if not 0<size<=MAX_PUBLISHER_CSV_BYTES:
        raise SourceStop("SOURCE_STOP_V89_FIGSHARE_FILE_SIZE")
    digest=f.get("computed_md5") or f.get("supplied_md5")
    if digest and not re.fullmatch(r"[a-f0-9]{32}",str(digest).lower()):
        raise SourceStop("SOURCE_STOP_V89_FIGSHARE_ORIGINAL_MD5_NOT_VALID")
    return {
        "real_figshare_article_ID":article,
        "original_source_DOI":spec["doi"],
        "real_figshare_original_file_ID":f.get("id"),
        "real_figshare_original_file_name":str(f.get("name") or "")[:160],
        "publisher_file_bytes":size,
        "provider_md5_or_null":str(digest).lower() if digest else None,
        "literal_original_download_url":original_download,
        "publisher_source_host":"api.figshare.com"}

def original_csv(spec,*,fetch=_fetch_literal_public_source):
    failures=[]
    try:
        b,proof=fetch(spec["springer_publisher_csv"],MAX_PUBLISHER_CSV_BYTES)
        if not b or b[:4]==b"<htm":
            raise SourceStop("SOURCE_STOP_V89_SPRINGER_ORIGINAL_RESPONSE_NOT_CSV")
        return b,{
            "original_path":"SPRINGER_EXACT_PUBLISHED_ADDITIONAL_FILE",
            "source_original_publisher_HTML_DOI":ORIGINAL_PAPER_DOI,
            "source_HTTP_success":True,
            "source_MD5_provider_verified":False,
            "original_csv_SHA256_LOCAL_NOT_PROVIDER_CERTIFIED":
                hashlib.sha256(b).hexdigest(),
            "original_csv_MD5_LOCAL_NOT_PROVIDER_CERTIFIED":
                hashlib.md5(b).hexdigest(),
            "original_source_bytes":len(b),
            "Springer_exact_original_URL":spec["springer_publisher_csv"]}
    except SourceStop as e:failures.append(str(e))
    meta=figshare_actual_provider_metadata(spec,fetch=fetch)
    try:
        b,receipt=fetch(meta["literal_original_download_url"],
                        MAX_PUBLISHER_CSV_BYTES)
    except SourceStop as e:
        raise SourceStop(
            "SOURCE_UNAVAILABLE_V89_SPRINGER_AND_REAL_FIGSHARE_FILE "+
            ";".join(failures+[str(e)])[:280]) from e
    if len(b)!=meta["publisher_file_bytes"]:
        raise SourceStop("SOURCE_STOP_V89_FIGSHARE_ORIGINAL_BYTES_CHANGED")
    md5=hashlib.md5(b).hexdigest()
    digest=meta["provider_md5_or_null"]
    if digest and digest!=md5:
        raise SourceStop("SOURCE_STOP_V89_FIGSHARE_MD5_PROVIDER_MISMATCH")
    return b,{
        "original_path":"FIGSHARE_ACTUAL_PUBLISHER_ARTICLE_FILE",
        "real_original_article_DOI":meta["original_source_DOI"],
        "real_original_file_ID":meta["real_figshare_original_file_ID"],
        "source_MD5_provider_verified":bool(digest),
        "original_csv_SHA256_LOCAL_NOT_PROVIDER_CERTIFIED":
            hashlib.sha256(b).hexdigest(),
        "original_csv_MD5_LOCAL_not_provider_if_no_MD5":md5,
        "original_source_bytes":len(b),
        "source_springer_original_download_failure":failures,
        "file_name_original":meta["real_figshare_original_file_name"]}

def _normalized_fields(header):
    fields={}
    for f in header:
        if f is None:continue
        key=re.sub(r"[^a-z0-9]+","",f.strip().lower())
        if key in fields:
            raise SourceStop("SOURCE_STOP_V89_DUPLICATE_NORMALIZED_WATLAS_CSV_FIELD")
        fields[key]=f
    if not set(ORIGINAL_REQUIRED).issubset(fields):
        raise SourceStop(
            "SOURCE_STOP_V89_ORIGINAL_WATLAS_CSV_FIELD_MISSING "+
            repr(sorted(set(ORIGINAL_REQUIRED)-set(fields))))
    return fields

def _window_UTM31N(x,y,*,transform):
    lon,lat=transform.transform(x,y)
    if not (math.isfinite(lon) and math.isfinite(lat)
            and ORIGINAL_PLAUSIBLE_LONGITUDE[0]<=lon<=ORIGINAL_PLAUSIBLE_LONGITUDE[1]
            and ORIGINAL_PLAUSIBLE_LATITUDE[0]<=lat<=ORIGINAL_PLAUSIBLE_LATITUDE[1]):
        raise ValueError("original_UTM31N_WGS84_outside_Wadden")
    return lon,lat

def audit_watlas_CSV(raw,species,*,transformer=None,
                     check_solar=True,expected_source_year=TRACKING_SOURCE_YEAR):
    """Never output tags, locations, time stamps, source rows, or behavior."""
    transformer=transformer or Transformer.from_crs(
        "EPSG:32631","EPSG:4326",always_xy=True)
    try:s=raw.decode("utf-8-sig",errors="strict")
    except UnicodeDecodeError as ex:
        raise SourceStop("SOURCE_STOP_V89_ORIGINAL_WATLAS_CSV_NOT_UTF8") from ex
    reader=csv.DictReader(io.StringIO(s))
    if not reader.fieldnames:
        raise SourceStop("SOURCE_STOP_V89_NO_ORIGINAL_CSV_HEADER")
    names=_normalized_fields(reader.fieldnames)
    counts=Counter()
    true_tags=Counter()
    true_month=Counter()
    true_date=set()
    native_hour=set()
    source_tides=set()
    source_days_and_nights=defaultdict(set)
    source_tide_sign=Counter()
    source_year=Counter()
    source_timezone=Counter()
    source_water=[]
    source_tidetime=[]
    source_receiver=Counter()
    bboxes=[math.inf,math.inf,-math.inf,-math.inf]
    solar_eligible=0
    errors=Counter()
    actual_read=0
    source_first_clock_tag_quarter={}
    for record in reader:
        actual_read+=1
        if actual_read>MAX_ORIGINAL_SOURCE_ROWS:
            raise SourceStop("SOURCE_STOP_V89_ORIGINAL_SOURCE_TOO_MANY_RECORDS")
        try:
            tag=(record[names["tag"]] or "").strip()
            if not tag:raise ValueError("source_missing_TAG")
            unix=float(record[names["time"]])
            if not math.isfinite(unix):raise ValueError("source_invalid_UNIX_TIME")
            when=datetime.fromtimestamp(unix,tz=timezone.utc)
            x=float(record[names["x"]]);y=float(record[names["y"]])
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("source_invalid_UTM_m")
            lon,lat=_window_UTM31N(x,y,transform=transformer)
            nbs=int(float(record[names["nbs"]]))
            tideid=(record[names["tideid"]] or "").strip()
            tide=float(record[names["tidaltime"]])
            water=float(record[names["waterlevel"]])
            if not tideid:raise ValueError("source_missing_tideID")
            if not (
                math.isfinite(tide) and TIDETIME_SOURCE_MINUTES[0]<=tide<=TIDETIME_SOURCE_MINUTES[1]):
                raise ValueError("source_tide_time_out_of_range")
            if not (
                math.isfinite(water) and WATERLEVEL_SOURCE_CM[0]<=water<=WATERLEVEL_SOURCE_CM[1]):
                raise ValueError("source_waterlevel_cm_out_of_range")
            if when.year not in (2017,2018,2019,2020,2021):
                raise ValueError("source_unexpected_WATLAS_tracking_year")
            if nbs<MIN_BIRD_WATLAS_RECEIVERS:
                raise ValueError("source_fewer_than_three_valid_base_stations")
        except (ValueError,TypeError,OverflowError,OSError) as ex:
            errors[str(ex)[:100]]+=1
            continue
        counts["original_raw_valid_UTC_UTM31N_rws_source"]+=1
        true_tags[tag]+=1
        true_month[f"{when.year}-{when.month:02d}"]+=1
        source_year[str(when.year)]+=1
        true_date.add((tag,when.date()))
        native_hour.add((tag,when.year,when.month,when.day,when.hour))
        source_tides.add((tag,tideid))
        source_tide_sign["before_high" if tide<0 else
                         "after_high" if tide>0 else "exact_high"]+=1
        source_receiver[str(nbs)]+=1
        source_water.append(water)
        source_tidetime.append(tide)
        bboxes[0]=min(bboxes[0],lat)
        bboxes[1]=min(bboxes[1],lon)
        bboxes[2]=max(bboxes[2],lat)
        bboxes[3]=max(bboxes[3],lon)
        # Original 1 source GPS fix per TAG×15 min is descriptive
        # *opportunity* only, never an animal step or per-fix independent effect.
        bin15=(tag,int(unix)//900)
        if bin15 not in source_first_clock_tag_quarter:
            source_first_clock_tag_quarter[bin15]=(when,lat,lon,tideid)
    if not counts["original_raw_valid_UTC_UTM31N_rws_source"]:
        raise SourceStop("SOURCE_STOP_V89_NO_VALID_ORIGINAL_WATLAS_LOCALIZATION")
    if check_solar:
        for (tag,bin15),(when,lat,lon,tid) in source_first_clock_tag_quarter.items():
            angle=float(elevation(Observer(latitude=lat,longitude=lon,
                                          elevation=0),when,with_refraction=True))
            light="DAY" if angle>LOCAL_MIDNIGHT_SOURCE_SOLAR_CUTOFF_DEG else (
                "NIGHT" if angle<-LOCAL_MIDNIGHT_SOURCE_SOLAR_CUTOFF_DEG
                else "TWILIGHT")
            source_timezone[light]+=1
            if light in ("DAY","NIGHT"):
                source_days_and_nights[tag].add(light)
                solar_eligible+=1
    return {
        "source_original_species":species,
        "actual_original_CSV_bytes":len(raw),
        "original_source_CSV_SHA256_LOCAL":hashlib.sha256(raw).hexdigest(),
        "original_source_header_columns":list(reader.fieldnames or []),
        "original_source_total_CSV_rows_including_source_invalid":actual_read,
        "original_source_valid_genuine_WATLAS_localizations":
            counts["original_raw_valid_UTC_UTM31N_rws_source"],
        "original_SOURCE_TAG_count_not_necessarily_independent_recaptures":len(true_tags),
        "original_source_TAG_clock_quarter_15min_unique_support":
            len(source_first_clock_tag_quarter),
        "source_TAGs_with_original_positions_in_both_astroDAY_NIGHT":
            sum(len(x)==2 for x in source_days_and_nights.values()),
        "original_source_total_tag_calendar_days":len(true_date),
        "original_source_total_tag_by_hour_source_opportunities":
            len(native_hour),
        "original_source_tide_cycles_per_TAG_unique":len(source_tides),
        "source_time_relative_to_high_tide_sign_counts":
            dict(source_tide_sign),
        "source_provided_waterlevel_cm_percentiles_5_50_95":
            [float(v) for v in __import__("numpy").quantile(
                source_water,[.05,.5,.95])],
        "source_provided_minutes_from_high_tide_percentiles_5_50_95":
            [float(v) for v in __import__("numpy").quantile(
                source_tidetime,[.05,.5,.95])],
        "source_date_year_counts":dict(sorted(source_year.items())),
        "source_calendar_month_counts":dict(sorted(true_month.items())),
        "source_ASTRAL_daynight_15min_true_TAG_gps_sample_counts":
            dict(source_timezone),
        "source_true_UTM31N_to_WGS84_anonymous_0p25deg_BBOX":[
            math.floor(bboxes[0]*4)/4,math.floor(bboxes[1]*4)/4,
            math.ceil(bboxes[2]*4)/4,math.ceil(bboxes[3]*4)/4],
        "source_original_receiver_NBS_ge3_value_histogram":dict(
            sorted(source_receiver.items(),key=lambda z:int(z[0]))),
        "original_source_errors_by_reason":dict(errors),
        "actual_2018_tracking_data_present":bool(source_year.get("2018",0)),
        "source_West_Terschelling_waterlevel_is_PUBLISHED_FIELD_NOT_YET_INDEPENDENT_RWS_AUDITED":True,
        "source_time_is_UNIX_seconds_UTC_not_native_CET_label":True,
        "original_WATLAS_UHF_tracking_not_GPS_satellite":True,
        "all_real_individual_TAG_values_and_precise_times_GPS_locations_NOT_RELEASED":True,
        "no_tidal_solar_animal_movement_or_habitat_effect_scored":True}

def run(output):
    result={
        "analysis":"V89_AUTHENTIC_PUBLISHED_WATLAS_2018_RED_KNOT_AND_SANDERLING_SOURCE_ONLY",
        "frozen_protocol":"docs/V89_FROZEN_ORIGINAL_WATLAS_KNOT_SANDERLING_TRUE_TIDE_COLUMNS_SOURCE.md",
        "original_WATLAS_Animal_Biotelemetry_source":ORIGINAL_PAPER_DOI,
        "original_figshare_version1_DOIs":{
            label:spec["doi"] for label,spec in FIGSHARE_ORIGINAL.items()},
        "genuine_source_status_by_species":{},
        "genuine_source_quality_by_species":{},
        "no_bird_movement_or_habitat_outcome_calculated":True}
    for label,spec in FIGSHARE_ORIGINAL.items():
        try:
            source,identity=original_csv(spec)
            score=audit_watlas_CSV(source,label)
            result["genuine_source_status_by_species"][label]="ORIGINAL_SOURCE_AUTHENTICATED_QA_ONLY"
            result["genuine_source_quality_by_species"][label]=score
            result.setdefault("provider_download_identity",{})[label]=identity
            print("V89_REAL_WATLAS_RED_KNOT_SANDERLING_SOURCE "+
                  json.dumps({
                    "species":label,
                    "original_CSV_source_rows":score[
                      "original_source_valid_genuine_WATLAS_localizations"],
                    "original_unique_TAGs":score[
                      "original_SOURCE_TAG_count_not_necessarily_independent_recaptures"],
                    "original_TAGs_day_night_source":score[
                      "source_TAGs_with_original_positions_in_both_astroDAY_NIGHT"],
                    "source_has_2018_dates":score["actual_2018_tracking_data_present"],
                    "source_paper_waterlevel_semantics_NOT_RWS_verified":True},
                    sort_keys=True),flush=True)
        except SourceStop as ex:
            result["genuine_source_status_by_species"][label]="SOURCE_UNAVAILABLE_OR_UNSUPPORTED_ORIGINAL"
            result.setdefault("source_original_blockers",{})[label]=str(ex)[:450]
            print("V89_REAL_WATLAS_PUBLISHER_DATA_SOURCE_STOP "+
                  json.dumps({"species":label,"issue":str(ex)[:250]},sort_keys=True),flush=True)
    result["full_both_original_published_species_source_admitted"]=all(
        v=="ORIGINAL_SOURCE_AUTHENTICATED_QA_ONLY"
        for v in result["genuine_source_status_by_species"].values())
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("V89_SOURCE_ONLY_PUBLISHED_WATLAS_TWO_TAXON_DECISION "+
          json.dumps({
            "both_sources_public_and_valid":result["full_both_original_published_species_source_admitted"],
            "source_site":"West Wadden near Griend/Richel",
            "source_data_has_waterlevel_tideID_tidaltime_as_published":True,
            "new_biological_tide_solar_predictions_scored":False},
            sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    run(p.parse_args().output)
