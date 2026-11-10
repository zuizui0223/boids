"""v111 original 2020 gull GPS and original Roompot RWS May–August exact source.

No movement behavior scores in this module. Source bird IDs/locations remain
ephemeral memory, never in reported artifact.
"""
from __future__ import annotations
import csv,gzip,io,json,math,time
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from hashlib import sha256

from original_delta_2020_gull_source import (
    original_manifest,genuine_file,native_reference_taxa,GPS_FILE,REFERENCE_FILE,
    FOCAL,YEAR,GPS_EXPECTED_MD5,SourceNotAdmitted)
from rws_roompot_2020_source import RWS_ROOT,DATA_ROUTE,NATIVE_META

SOURCE_MONTHS=(5,6,7,8)
NATIVE_PRIMARY='oosterschelde.roompotsluis.buiten'
NATIVE_SECONDARY='oosterschelde.roompotsluis.binnen'
GEO_PRIMARY=(51.619722,3.681944)
WATER_MIN_MONTH_COVERAGE=.80
SOURCE_REQ_TIMEOUT=70
SOURCE_MAX_BYTES=22_000_000
RWS_SLOPE_MIN_METRES_PER_H=.012
FULL_MONTH_SOURCE_2020=(31,30,31,31)
GEO_RADIUS_PRIMARY_KM=20.
PHYSICAL_SPEED_QA_MAX_KMH=150.

class OriginalSourceStop(Exception):pass

def _request_tide_raw(code,month):
    if code not in (NATIVE_PRIMARY,NATIVE_SECONDARY) or month not in SOURCE_MONTHS:
        raise OriginalSourceStop('SOURCE_STOP_NOT_PRE_FROZEN_RWS_2020_STATION_OR_MONTH')
    starts=datetime(2020,month,1)
    ends=datetime(2020,month+1,1)
    payload={'Locatie':{'Code':code},
       'AquoPlusWaarnemingMetadata':{'AquoMetadata':NATIVE_META},
       'Periode':{'Begindatumtijd':starts.strftime('%Y-%m-%dT%H:%M:%S.000+01:00'),
                  'Einddatumtijd':ends.strftime('%Y-%m-%dT%H:%M:%S.000+01:00')}}
    req=Request(RWS_ROOT+DATA_ROUTE,
        data=json.dumps(payload).encode(),method='POST',
        headers={'Content-Type':'application/json','Accept':'application/json',
          'User-Agent':'boids-v111-2020-actual-Roompotsluis-NAP-gull-source/1.0'})
    try:
        with urlopen(req,timeout=SOURCE_REQ_TIMEOUT) as response:
            raw=response.read(SOURCE_MAX_BYTES+1)
        if len(raw)>SOURCE_MAX_BYTES:raise OriginalSourceStop('SOURCE_STOP_NATIVE_RWS_MONTH_RESPONSE_TOO_LARGE')
        obj=json.loads(raw)
        return obj,sha256(raw).hexdigest()
    except (HTTPError,URLError,TimeoutError,json.JSONDecodeError) as e:
        raise OriginalSourceStop('SOURCE_UNAVAILABLE_RWS_2020_OFFICIAL_MONTH '+str(e)[:170]) from e

def parse_official_RWS_month(source,month):
    if source.get('Succesvol') is not True:
        raise OriginalSourceStop('SOURCE_STOP_OFFICIAL_RWS_NATIVE_FAILURE')
    result={}
    original_n=0
    for series in source.get('WaarnemingenLijst') or []:
        meta=series.get('AquoMetadata') or {}
        if (meta.get('Grootheid') or {}).get('Code')!='WATHTE' or (
            (meta.get('Eenheid') or {}).get('Code')!='cm') or (
            (meta.get('Hoedanigheid') or {}).get('Code')!='NAP'):
            continue
        for event in series.get('MetingenLijst') or []:
            stamp=datetime.fromisoformat(event['Tijdstip'].replace('Z','+00:00'))
            if stamp.utcoffset()!=timedelta(hours=1):
                raise OriginalSourceStop('SOURCE_STOP_REAL_RWS_2020_OFFSET_NOT_FIXED_PLUS1')
            utc=stamp.astimezone(timezone.utc)
            value=(event.get('Meetwaarde') or {}).get('Waarde_Numeriek')
            if value is None:continue
            try:cm=float(value)
            except (TypeError,ValueError):continue
            if not math.isfinite(cm) or abs(cm)>500:continue
            if utc in result and abs(result[utc]-cm/100)>1e-6:
                raise OriginalSourceStop('SOURCE_STOP_TRUE_RWS_CONTRADICTORY_DUPLICATE_HEIGHT')
            result[utc]=cm/100;original_n+=1
    expected=144*FULL_MONTH_SOURCE_2020[SOURCE_MONTHS.index(month)]
    if len(result)<WATER_MIN_MONTH_COVERAGE*expected:
        raise OriginalSourceStop('SOURCE_STOP_RWS_2020_MONTH_LT80PCT_ORIGINAL_10MIN_SOURCE')
    return result,{'2020_native_month':month,'true_10min_NAP_cm_unique_timestamps':len(result),
        'expected_10min_month_slots':expected,'coverage':len(result)/expected,
        'native_source_NAP_m_convert_only_to_metres':True}

def original_2020_gauge_may_aug(source_station,*,request_fn=_request_tide_raw,sleeper=time.sleep):
    if source_station not in (NATIVE_PRIMARY,NATIVE_SECONDARY):
        raise OriginalSourceStop('SOURCE_STOP_NON_FROZEN_ORIGINAL_RWS_STATION')
    joined={};month_metadata=[]
    for idx,month in enumerate(SOURCE_MONTHS):
        if idx:sleeper(1)
        response,sh=request_fn(source_station,month)
        vals,qa=parse_official_RWS_month(response,month)
        if any(t in joined and abs(joined[t]-v)>1e-6 for t,v in vals.items()):
            raise OriginalSourceStop('SOURCE_STOP_CONFLICTING_ORIGINAL_RWS_MONTH_BOUNDARY')
        joined.update(vals)
        month_metadata.append({**qa,'native_original_response_SHA256':sh})
        print('V111_ORIGINAL_2020_RWS_MEASURED_MONTH '+json.dumps({
            'station':source_station,'month':month,'n_original_10min':qa['true_10min_NAP_cm_unique_timestamps'],
            'source_coverage':qa['coverage']},sort_keys=True),flush=True)
    return joined,{'station':source_station,'months':month_metadata,
         'total_unique_actual_measured_NAP_10min_timestamps':len(joined),
         'NO_original_measurements_exported_in_anonymous_artifact':True}

def parse_2020_original_source_gps_native(raw,reference):
    reader=csv.DictReader(io.TextIOWrapper(
        gzip.GzipFile(fileobj=io.BytesIO(raw)),encoding='utf-8-sig'))
    headers=reader.fieldnames or []
    needed={'timestamp','location-lat','location-long','individual-local-identifier'}
    if not needed<=set(headers):raise OriginalSourceStop('STOP_MOVEBANK_2020_NATIVE_GULL_SOURCE_SCHEMA')
    bird_hours=defaultdict(dict)
    errors=Counter()
    row_count=0
    for r in reader:
        row_count+=1
        bird=(r.get('individual-local-identifier') or '').strip()
        if not bird:errors['missing_native_bird_id']+=1;continue
        if (r.get('visible') or '').strip().upper() in ('FALSE','0'):
            errors['native_invisible_source']+=1;continue
        taxon=(r.get('individual-taxon-canonical-name') or reference.get(bird) or '').strip()
        if taxon not in FOCAL:continue
        try:
            stamp=datetime.fromisoformat((r['timestamp'] or '').replace('Z','+00:00'))
            if stamp.tzinfo is not None:stamp=stamp.astimezone(timezone.utc).replace(tzinfo=None)
            lat=float(r['location-lat']);lon=float(r['location-long'])
        except (TypeError,ValueError):
            errors['bad_native_time_or_location']+=1;continue
        if stamp.year!=YEAR or stamp.month not in SOURCE_MONTHS or not(
            math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180):
            continue
        hour=stamp.replace(minute=0,second=0,microsecond=0)
        old=bird_hours[(taxon,bird)].get(hour)
        if old is None or stamp<old[0]:bird_hours[(taxon,bird)][hour]=(stamp,lat,lon)
    by_taxon=Counter()
    original_birds=Counter()
    for (taxon,bird),fixes in bird_hours.items():
        if fixes:
            by_taxon[taxon]+=len(fixes);original_birds[taxon]+=1
    return bird_hours,{'2020_source_raw_native_GPS_event_rows':row_count,
       'one_tag_hour_GPS_fixes_in_COMMON_MayAug_by_species':dict(by_taxon),
       'original_birds_present_MayAug_by_species':dict(original_birds),
       'source_parse_qa_counts':dict(errors),'native_year':YEAR,
       'fixes_and_animal_identifiers_NOT_exported':True}
def fetch_original_gulls():
    files,manifest=original_manifest()
    reference_bytes,ref_proof=genuine_file(files[REFERENCE_FILE])
    reference,refheads=native_reference_taxa(reference_bytes)
    original_gps,proof=genuine_file(files[GPS_FILE])
    birds,qa=parse_2020_original_source_gps_native(original_gps,reference)
    return birds,{'corrected_original_Zenodo_record':manifest['original_Zenodo_api_record_id'],
       '2020_original_publisher_GPS_MD5_verified':proof['provider_MD5_verified'],
       '2020_original_compressed_GPS_SHA256':proof['local_SHA256'],
       'source_MayAug_individual_and_hour_support':qa,
       'original_reference_taxon_mapping_columns':refheads,
       'original_tag_identifiers_and_GPS_not_exported':True}
