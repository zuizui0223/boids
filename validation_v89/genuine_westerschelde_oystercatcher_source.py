"""v89 independent Westerschelde 2018-20 GPS original-source census ONLY.

Published INBO/Zenodo DOI 10.5281/zenodo.10053702; file MD5
source-verified, native Movebank reference data, original genuine bird
ID/hour GPS and broad externally fixed Western Scheldt/East Flanders
coastal region. NO actual tide, astronomy, habitat classification,
model-index rank or novel behavioral positive/negative outcome scored.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import md5,sha256
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import argparse,csv,gzip,io,json,math,os,re

ZENODO_REC="10053702"
ZENODO_META=f"https://zenodo.org/api/records/{ZENODO_REC}"
SOURCE_DOI="10.5281/zenodo.10053702"
SITE="O_WESTERSCHELDE"
YEARS=(2018,2019,2020)
ORIGINAL_GPS_FILES={
  2018:("O_WESTERSCHELDE-gps-2018.csv.gz",
        "2d37d87d42fe23925f1ab5869f9b49f2"),
  2019:("O_WESTERSCHELDE-gps-2019.csv.gz",
        "ba0bf9f1fd1bcc415a0505485d3f4f27"),
  2020:("O_WESTERSCHELDE-gps-2020.csv.gz",
        "255beb9052fd84f93c3aeb4d621f5d36")}
AUX_PUBLIC={
  "datapackage.json":"1911faf4b4cceb7896beea23a3455d83",
  "O_WESTERSCHELDE-reference-data.csv":"97666bc1be0e9c85cad0fc81ab0b58a7"}
ALLOWED_FILES={f:checksum for f,checksum in AUX_PUBLIC.items()}
ALLOWED_FILES.update({f:hash for f,hash in ORIGINAL_GPS_FILES.values()})
SOURCE_BBOX=(50.90,51.65,3.00,4.70)
MAX_METADATA_BYTES=2_000_000
MAX_FILE_BYTES=12_000_000
FROZEN_YEARS_FOR_FUTURE_TIDE=(2018,2019)
MIN_BIRDS_YEAR=8
MIN_BIRD_HOURS_PER_YEAR=20
MIN_SOURCE_GOOD_MONTHS=3
MIN_MONTH_BIRDS=5
MIN_HOURS_PER_BIRD_MONTH=20
MIN_HOURS_PER_MONTH=200
MIN_TOTAL_YEAR_HOURS=2000
EXPECTED_TAGGED_IN_PUBLICATION=13

class SourceStop(Exception):pass

def official_get(url,limit=MAX_FILE_BYTES,*,fetch=None):
    if not isinstance(url,str) or not url.startswith("https://zenodo.org/"):
        raise SourceStop("SOURCE_STOP_V89_NOT_OFFICIAL_ZENODO_FILE_URL")
    if fetch is not None:return fetch(url,limit)
    try:
        with urlopen(Request(url,headers={
            "User-Agent":"boids-v89-authentic-INBO-Westerschelde-GPS/1.0",
            "Accept":"application/json,text/csv,application/gzip,*/*"}),timeout=100) as res:
            blob=res.read(limit+1)
            if len(blob)>limit:
                raise SourceStop("SOURCE_STOP_V89_SOURCE_FILE_TOO_LARGE")
            if urlparse(res.geturl()).scheme!="https":
                raise SourceStop("SOURCE_STOP_V89_INSECURE_DOWNLOAD_REDIRECT")
            return blob
    except (HTTPError,URLError,TimeoutError) as error:
        raise SourceStop("SOURCE_UNAVAILABLE_V89_ZENODO_PUBLIC_FILE "+str(error)[:170]) from error

def original_manifest(*,fetch=None):
    payload=official_get(ZENODO_META,limit=MAX_METADATA_BYTES,fetch=fetch)
    try:record=json.loads(payload)
    except (ValueError,TypeError) as error:
        raise SourceStop("SOURCE_STOP_V89_ZENODO_ORIGINAL_RECORD_INVALID_JSON") from error
    if not isinstance(record,dict) or str(record.get("id"))!=ZENODO_REC:
        raise SourceStop("SOURCE_STOP_V89_WRONG_ORIGINAL_ZENODO_RECORD")
    manifest={}
    for item in record.get("files") or []:
        if not isinstance(item,dict):continue
        key=item.get("key")
        if key not in ALLOWED_FILES:continue
        if key in manifest:
            raise SourceStop("SOURCE_STOP_V89_ORIGINAL_ZENODO_FILE_DUPLICATE")
        provider_md5=str(item.get("checksum") or "").lower()
        if provider_md5.startswith("md5:"):provider_md5=provider_md5[4:]
        if provider_md5!=ALLOWED_FILES[key]:
            raise SourceStop("SOURCE_STOP_V89_ORIGINAL_PUBLISHER_MD5_DRIFT")
        links=item.get("links") or {}
        href=links.get("self") or links.get("content")
        if not isinstance(href,str) or not href.startswith("https://zenodo.org/"):
            raise SourceStop("SOURCE_STOP_V89_ORIGINAL_PUBLISHER_LINK_INVALID")
        length=item.get("size")
        if not isinstance(length,int) or not(0<length<MAX_FILE_BYTES):
            raise SourceStop("SOURCE_STOP_V89_ORIGINAL_PUBLISHER_FILE_SIZE")
        manifest[key]={"actual_original_publisher_file_key":key,
                       "actual_original_provider_md5":provider_md5,
                       "source_original_bytes":length,"source_literal_download_url":href}
    if set(manifest)!=set(ALLOWED_FILES):
        raise SourceStop("SOURCE_STOP_V89_INCOMPLETE_ORIGINAL_PUBLISHED_GPS_MANIFEST")
    return manifest,{
        "original_Zenodo_source_record":ZENODO_REC,
        "original_source_DOI":SOURCE_DOI,
        "published_true_tagged_birds_descriptive":EXPECTED_TAGGED_IN_PUBLICATION,
        "original_source_manifest_files_and_md5":[
           {"name":k,"md5":d["actual_original_provider_md5"],
            "published_compressed_bytes":d["source_original_bytes"]}
            for k,d in sorted(manifest.items())],
        "original_acceleration_files_EXCLUDED":True,
        "no_original_bird_data_read_at_manifest_stage":True}

def original_file_bytes(entry,*,fetch=None):
    data=official_get(entry["source_literal_download_url"],fetch=fetch)
    if len(data)!=entry["source_original_bytes"]:
        raise SourceStop("SOURCE_STOP_V89_ORIGINAL_ZENODO_SIZE_NOT_PUBLISHER")
    if md5(data).hexdigest()!=entry["actual_original_provider_md5"]:
        raise SourceStop("SOURCE_STOP_V89_ORIGINAL_GPS_OR_METADATA_MD5_CHANGED")
    return data,{
        "real_source_published_file":entry["actual_original_publisher_file_key"],
        "published_original_md5_matched":True,
        "original_source_computed_sha256":sha256(data).hexdigest(),
        "original_source_bytes":len(data)}

def original_native_hourly_GPS(gz,year,*,expected_cols=None):
    if year not in YEARS:
        raise SourceStop("SOURCE_STOP_V89_UNREGISTERED_ORIGINAL_YEAR")
    try:raw=gzip.decompress(gz)
    except (ValueError,OSError) as e:
        raise SourceStop("SOURCE_STOP_V89_ORIGINAL_GPS_SOURCE_GZIP_BROKEN") from e
    if len(raw)>120_000_000:
        raise SourceStop("SOURCE_STOP_V89_ORIGINAL_UNCOMPRESSED_GPS_TOO_LARGE")
    stream=io.StringIO(raw.decode("utf-8-sig"))
    reader=csv.DictReader(stream)
    expected={"event-id","timestamp","location-lat","location-long",
              "individual-local-identifier","visible"}
    if not expected.issubset(reader.fieldnames or []):
        raise SourceStop("SOURCE_STOP_V89_ORIGINAL_MOVEBANK_NATIVE_GPS_COLUMNS")
    seen=set();earliest=defaultdict(dict);bad=Counter()
    n=0
    for row in reader:
        n+=1
        ev=(row.get("event-id") or "").strip()
        if not ev or ev in seen:
            bad["duplicate_or_missing_original_event_id"]+=1
            continue
        seen.add(ev)
        if (row.get("visible") or "").strip().upper() in ("FALSE","0"):
            bad["not_visible_source_event"]+=1
            continue
        bird=(row.get("individual-local-identifier") or "").strip()
        if not bird:
            bad["source_missing_true_bird_ID"]+=1
            continue
        try:
            tt=(row.get("timestamp") or "").strip()
            if tt.endswith("Z"):
                dt=datetime.fromisoformat(tt[:-1]+"+00:00").replace(tzinfo=None)
            else:dt=datetime.fromisoformat(tt)
            la=float(row["location-lat"])
            lo=float(row["location-long"])
        except (TypeError,ValueError):
            bad["source_original_bad_GPS_time_or_geography"]+=1
            continue
        if (dt.year!=year or not(math.isfinite(la) and math.isfinite(lo)) or
            not (-90<=la<=90 and -180<=lo<=180)):
            bad["source_outside_original_annual_and_WGS84"]+=1
            continue
        hour=dt.replace(minute=0,second=0,microsecond=0)
        prev=earliest[bird].get(hour)
        if prev is None or dt<prev[0]:
            earliest[bird][hour]=(dt,la,lo)
    per_month=defaultdict(lambda:defaultdict(list))
    for bird,hours in earliest.items():
        for dt,lat,lon in hours.values():
            per_month[dt.month][bird].append((lat,lon))
    receipt={}
    for month in range(1,13):
        b=per_month[month]
        flat=[pos for fixes in b.values() for pos in fixes]
        inside=sum(SOURCE_BBOX[0]<=lat<=SOURCE_BBOX[1] and
                   SOURCE_BBOX[2]<=lon<=SOURCE_BBOX[3] for lat,lon in flat)
        eligible_birds=sum(
            sum(SOURCE_BBOX[0]<=lat<=SOURCE_BBOX[1] and
                SOURCE_BBOX[2]<=lon<=SOURCE_BBOX[3] for lat,lon in x)>=
                MIN_HOURS_PER_BIRD_MONTH
            for x in b.values())
        receipt[f"{month:02d}"]={
            "original_annual_GPS_one_native_fix_per_bird_hour":len(flat),
            "original_distinct_source_bird_IDs":len(b),
            "original_GPS_hours_in_frozen_WesterScheldt_EastFlanders_source_box":inside,
            "original_birds_with_ge20_hours_in_frozen_source_box_this_month":
                eligible_birds}
    period=Counter()
    monthly_good=[]
    for month in range(1,13):
        for bird,positions in per_month[month].items():
            n_in=sum(SOURCE_BBOX[0]<=lat<=SOURCE_BBOX[1] and
                     SOURCE_BBOX[2]<=lon<=SOURCE_BBOX[3] for lat,lon in positions)
            period[bird]+=n_in
    eligible={bird for bird,n in period.items() if n>=MIN_BIRD_HOURS_PER_YEAR}
    for m in range(1,13):
        b=per_month[m]
        qualifying=[
            sum(SOURCE_BBOX[0]<=lat<=SOURCE_BBOX[1] and
                SOURCE_BBOX[2]<=lon<=SOURCE_BBOX[3] for lat,lon in b[bird])
            for bird in eligible]
        n_supported=sum(k>=MIN_HOURS_PER_BIRD_MONTH for k in qualifying)
        total_supported=sum(k for k in qualifying if k>=MIN_HOURS_PER_BIRD_MONTH)
        if n_supported>=MIN_MONTH_BIRDS and total_supported>=MIN_HOURS_PER_MONTH:
            monthly_good.append(m)
    total_period=sum(period[bird] for bird in eligible)
    candidate=(len(eligible)>=MIN_BIRDS_YEAR
        and len(monthly_good)>=MIN_SOURCE_GOOD_MONTHS
        and total_period>=MIN_TOTAL_YEAR_HOURS)
    return {
        "source_original_nominal_year":year,
        "source_original_raw_GPS_event_rows":n,
        "source_original_valid_native_bird_IDs_in_year":len(earliest),
        "source_original_hourly_GPS_fixes_in_any_WGS84_area":
            sum(len(v) for v in earliest.values()),
        "source_original_native_GPS_or_event_exclusions":dict(bad),
        "original_calendar_months_anonymized_source":receipt,
        "original_2018_2020_anytime_original_birds_ge20_GPS_in_frozen_estuary_region":
            len(eligible),
        "original_2018_2020_genuine_source_months_5birds_200hours":
            monthly_good,
        "original_fixed_WesterScheldt_EastFlanders_source_region_GPS_hours":
            total_period,
        "original_source_status_candidate_for_separate_RWS_tide_and_ecotope_test":
            "CANDIDATE_YEAR_WITH_GPS_BIRD_SOURCE_ONLY" if
            candidate and year in FROZEN_YEARS_FOR_FUTURE_TIDE else
            "NOT_ADMITTED_V89_YEAR_ORIGINAL_BIRD_SOURCE_OR_NOT_PRIMARY_YEAR",
        "source_native_clock_not_verified_GPS_UTC_hardware":True,
        "source_WesterScheldt_region_bbox_pre_frozen":[
           50.9,51.65,3.0,4.7],
        "original_animal_tag_IDs_exact_geography_and_times_not_saved":True,
        "NO_actual_original_tide_or_sunlight_or_foraging_habitat_response":True}

def run(output):
    report={
        "analysis":"V89_ORIGINAL_WESTERSCHELDE_2018_2020_INDEPENDENT_ESTUARY_OYSTERCATCHER_GPS_SOURCE_ONLY",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "frozen_protocol":"docs/V89_FROZEN_ORIGINAL_WESTERSCHELDE_2018_2020_GPS_ECOTOPE_TIDE_SOURCE_ONLY.md",
        "original_zenodo_DOI":SOURCE_DOI,
        "source_candidate_independent_coast_not_taxon":"WESTERSCHELDE_NEAR_BELGIUM_NETHERLANDS",
        "original_genuine_2018_2020_Westerschelde_GPS_year_receipts":{},
        "original_RWS_vlissingen_2018_2019_measured_gauge_NOT_TESTED":True,
        "original_RWS_Westerschelde_2018_native_ecotope_map_NOT_OPENED":True,
        "no_animal_tide_sun_habitat_outcome_scored":True}
    try:
        source,identity=original_manifest()
        report["original_Zenodo_publisher_file_manifest"]=identity
        files={}
        for name in AUX_PUBLIC:
            binary,receipt=original_file_bytes(source[name])
            files[name]=binary
            report["original_genuine_2018_2020_Westerschelde_GPS_year_receipts"][
                name]=receipt
        schema=json.loads(files["datapackage.json"])
        if not isinstance(schema,dict) or not schema.get("resources"):
            raise SourceStop("SOURCE_STOP_V89_ORIGINAL_MOVEBANK_DATAPACKAGE_BROKEN")
        data={}
        for year in YEARS:
            fname,expected_md5=ORIGINAL_GPS_FILES[year]
            binary,identity=original_file_bytes(source[fname])
            q=original_native_hourly_GPS(binary,year)
            data[year]=q
            report["original_genuine_2018_2020_Westerschelde_GPS_year_receipts"][
                fname]={"original_file_source_proof":identity,"anonymized_native_GPS_source":q}
            print("V89_GENUINE_INBO_WESTERSCHELDE_GPS_NATIVE_SOURCE "+
                json.dumps({"year":year,
                    "source_original_birds":q["source_original_valid_native_bird_IDs_in_year"],
                    "source_original_bird_hours":
                        q["source_original_hourly_GPS_fixes_in_any_WGS84_area"],
                    "source_estuary_region_original_source_hours":q[
                        "original_fixed_WesterScheldt_EastFlanders_source_region_GPS_hours"],
                    "source_birds_ge20_estuary":q[
                        "original_2018_2020_anytime_original_birds_ge20_GPS_in_frozen_estuary_region"],
                    "source_status":q[
                        "original_source_status_candidate_for_separate_RWS_tide_and_ecotope_test"]},
                    sort_keys=True),flush=True)
        report["original_Zenodo_MD5_and_native_source_access"]="ADMITTED_ORIGINAL_WESTERSCHELDE_2018_2020_WILD_GPS_SOURCE"
        report["original_preselected_2018_2019_genuine_GPS_bird_year_capacity"]={
            str(year):data[year][
                "original_source_status_candidate_for_separate_RWS_tide_and_ecotope_test"]
            for year in FROZEN_YEARS_FOR_FUTURE_TIDE}
        report["original_source_reference_rows_count"]=max(0,
            len(files["O_WESTERSCHELDE-reference-data.csv"].decode(
                "utf-8-sig").splitlines())-1)
        report["original_native_frictionless_data_package_resource_names"]=[
             str(z.get("name") or "") for z in schema["resources"]][:30]
    except SourceStop as err:
        report["original_Zenodo_MD5_and_native_source_access"]="SOURCE_NOT_ADMITTED_V89_ORIGINAL_ZENODO"
        report["source_blocker"]=str(err)[:300]
    target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("V89_WESTERSCHELDE_NEW_ESTUARY_TRUE_GPS_SOURCE_RESULT "+
        json.dumps({
            "source_status":report["original_Zenodo_MD5_and_native_source_access"],
            "source_blocker_if_any":report.get("source_blocker"),
            "source_year_2018_19_candidate_status":
                report.get("original_preselected_2018_2019_genuine_GPS_bird_year_capacity"),
            "local_true_RWS_tidal_effect_NOT_TESTED":True,
            "no_source_animal_ID_location_time_or_predicted_tide_saved":True},
            sort_keys=True),flush=True)
    print("V89_REAL_NEW_COAST_ORIGINAL_GPS_SOURCE_AUDIT_COMPLETED",flush=True)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    run(p.parse_args().output)
