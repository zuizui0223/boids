"""v126 ORIGINAL 2019 Vlieland GPS (publisher MD5) × ACC-derived forage/inactive
event time source link. No estimated tide×sun behaviour effect. Event labels
from v125 genuine 2019 source, not human visually observed feeding.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from bisect import bisect_left
from datetime import datetime
from hashlib import sha256,md5
from math import radians,sin,cos,sqrt,atan2,isfinite
from pathlib import Path
from io import TextIOWrapper,BytesIO
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import argparse,csv,gzip,json

from original_2019_Vlieland_behaviour_source import (
    API,PUBLISHER,RECORD,FREEZE,
    original_publisher_manifest,original_native_file,
    _reference_anonymous_identity,_native_datetime,
    exact_source_transport_retry,_publisher_get,SourceStop,TemporarySourceFailure)

ORIGINAL_YEAR=2019
GPS_FILE='O_VLIELAND-gps-2019.csv.gz'
BEHAVIOUR_FILE='O_VLIELAND-accessory-measurements-2019.csv.gz'
GPS_MD5='65426aedf6f48c36f81990268d267c7b'
MAX_GPS_COMPRESSED_BYTES=86_000_000
STATION_CODE='vlieland.haven'
SOURCE_STATION_LAT_LON=(53.30,5.09)
JOIN_MAX_ABSOLUTE_SECS=15*60
DISTANCE_PRIMARY_KM=25.
DISTANCE_SENSITIVITIES_KM=(15.,35.)
LABEL_FORAGE='forage'
LABEL_INACTIVE='inactive'
LABELS_FIXED={'forage':512605,'inactive':868331,'walk':102897,'fly':47275,'preen':285925}
ORIGINAL_BEHAVIOUR_ROWS=1817033
ORIGINAL_SOURCE_BIRDS=43
MIN_ORIGINAL_BIRDS=8
MIN_CLASS_EVENTS_PER_BIRD=100
MIN_MONTHS_WITH_BOTH=2

def _great_circle_km(lat,lon,lat0,lon0):
    a=radians(lat0-lat);b=radians(lon0-lon)
    x=sin(a/2)**2+cos(radians(lat))*cos(radians(lat0))*sin(b/2)**2
    return 12742*atan2(sqrt(max(0.,x)),sqrt(max(0.,1.-x)))

def authenticate_original_gps_2019():
    meta,provenance=exact_source_transport_retry(
        lambda:_publisher_get(API,2_000_000),
        'O_VLIELAND_YEAR2019_GPS_METADATA')
    obj=json.loads(meta)
    if str(obj.get('id'))!=str(RECORD):raise SourceStop('STOP_NOT_FROZEN_ORIGINAL_VLIELAND_ZENODO_RECORD')
    candidates=[r for r in (obj.get('files') or []) if r.get('key')==GPS_FILE]
    if len(candidates)!=1:raise SourceStop('STOP_ZENODO_2019_GPS_PUBLISHER_FILE_NOT_UNIQUE')
    record=candidates[0]
    expected_hash=str(record.get('checksum') or '').removeprefix('md5:')
    length=record.get('size')
    url=(record.get('links') or {}).get('self') or (record.get('links') or {}).get('content')
    if (expected_hash!=GPS_MD5 or not isinstance(length,int) or not 0<length<MAX_GPS_COMPRESSED_BYTES
        or not isinstance(url,str) or not url.startswith(PUBLISHER+'/')):
        raise SourceStop('STOP_2019_GPS_PUBLISHER_MD5_OR_SOURCE_VERSION_DRIFT')
    raw,source_attempts=exact_source_transport_retry(
       lambda:_publisher_get(url,MAX_GPS_COMPRESSED_BYTES),
       'O_VLIELAND_NATIVE_2019_GPS_FULL_PUBLISHER')
    if md5(raw).hexdigest()!=GPS_MD5 or len(raw)!=length:
        raise SourceStop('STOP_2019_ZENODO_FULL_GPS_SOURCE_HASH_OR_LENGTH_MISMATCH')
    return raw,{'native_source_2019_GPS':GPS_FILE,
        'source_publisher_MD5_replayed_exactly':GPS_MD5,
        'source_publisher_full_bytes':len(raw),
        'source_SHA256_local':sha256(raw).hexdigest(),
        'native_original_publication_record':RECORD,
        'source_transport_metadata':provenance,
        'source_transport_GPS':source_attempts,
        'no_native_original_tags_or_lat_lons_exported':True}

def _bird_id_from_native(row,ref):
    bird=(row.get('individual-local-identifier') or '').strip()
    if bird:return bird
    return ref.get((row.get('tag-local-identifier') or '').strip(),'')

def original_2019_gps_source_index(raw,reference):
    if raw[:2]!=b'\x1f\x8b':raise SourceStop('STOP_2019_NATIVE_GPS_NOT_GZIP')
    stream=TextIOWrapper(gzip.GzipFile(fileobj=BytesIO(raw)),encoding='utf-8-sig',newline='')
    reader=csv.DictReader(stream)
    header=reader.fieldnames or []
    if not {'timestamp','location-lat','location-long'}<=set(header) or (
        not {'individual-local-identifier','tag-local-identifier'}&set(header)):
        raise SourceStop('STOP_2019_VLIELAND_GPS_MOVEBANK_SCHEMA_DRIFT')
    original=0;quality=Counter();bird_month=defaultdict(set)
    bybird=defaultdict(list)
    for row in reader:
        original+=1
        bird=_bird_id_from_native(row,reference)
        if not bird:quality['source_original_GPS_no_resolved_bird']+=1;continue
        if (row.get('visible') or '').strip().upper() in ('0','FALSE'):
            quality['source_original_GPS_invisible']+=1;continue
        try:
            d=_native_datetime(row.get('timestamp'))
            lat=float(row['location-lat']);lon=float(row['location-long'])
        except (ValueError,TypeError):
            quality['source_original_GPS_bad_timestamp_or_WGS84']+=1;continue
        if d.year!=ORIGINAL_YEAR or not(isfinite(lat) and isfinite(lon) and -90<=lat<=90 and -180<=lon<=180):
            quality['source_original_GPS_year_or_geography_not_admitted']+=1;continue
        bybird[bird].append((d,lat,lon))
        bird_month[d.month].add(bird)
    indexed={}
    for bird,rows in bybird.items():
        rows.sort(key=lambda r:r[0])
        indexed[bird]=([v[0] for v in rows],rows)
    return indexed,{'native_original_2019_GPS_full_source_rows':original,
       'native_original_2019_genuine_GPS_birds':len(bybird),
       'native_original_2019_valid_WGS84_fix_n':sum(len(v[1]) for v in indexed.values()),
       'original_month_number_of_GPS_source_birds':
             {str(i):len(bird_month[i]) for i in range(1,13)},
       'native_source_GPS_schema':header,
       'source_GPS_rejected_or_unavailable_counts':dict(quality),
       'all_original_GPS_bird_ID_exact_time_and_WGS84_private':True}

def _nearest_real_original_gps(indexed,bird,time):
    data=indexed.get(bird)
    if data is None:return None
    stamps,rows=data
    loc=bisect_left(stamps,time)
    at=[i for i in (loc-1,loc) if 0<=i<len(rows)]
    if not at:return None
    choice=min(at,key=lambda i:(abs((stamps[i]-time).total_seconds()),stamps[i]))
    seconds=abs((stamps[choice]-time).total_seconds())
    if seconds>JOIN_MAX_ABSOLUTE_SECS:return None
    return rows[choice],seconds

def true_original_2019_behaviour_gps_join(raw,reference,indexed):
    if raw[:2]!=b'\x1f\x8b':raise SourceStop('STOP_2019_GENUINE_CLASSIFIED_BEHAVIOUR_NOT_GZIP')
    source=csv.DictReader(TextIOWrapper(gzip.GzipFile(fileobj=BytesIO(raw)),
                                        encoding='utf-8-sig',newline=''))
    native_columns=source.fieldnames or []
    if not {'timestamp','behavioural-classification'}<=set(native_columns):
        raise SourceStop('STOP_ORIGINAL_V125_VLIELAND_BEHAVIOUR_SOURCE_CHANGED')
    observed_labels=Counter()
    source_qa=Counter()
    geography_qa={r:Counter() for r in (DISTANCE_PRIMARY_KM,)+DISTANCE_SENSITIVITIES_KM}
    by_radius={r:defaultdict(lambda:defaultdict(Counter))
               for r in geography_qa}
    all_rows=0;raw_class_source_birds=set()
    for row in source:
        all_rows+=1
        label=str(row.get('behavioural-classification') or '').strip().casefold()
        observed_labels[label]+=1
        bird=_bird_id_from_native(row,reference)
        if not bird:source_qa['original_classification_bird_identity_unresolved']+=1;continue
        raw_class_source_birds.add(bird)
        if (row.get('visible') or '').strip().upper() in ('FALSE','0'):
            source_qa['original_classification_invisible']+=1;continue
        try:t=_native_datetime(row.get('timestamp'))
        except ValueError:
            source_qa['original_classification_UTC_timestamp_invalid']+=1;continue
        if t.year!=ORIGINAL_YEAR:
            source_qa['original_classification_outside_original_2019']+=1;continue
        # GPS is matched by same ORIGINAL bird, not a fixed colony coordinate.
        match=_nearest_real_original_gps(indexed,bird,t)
        if match is None:
            source_qa['original_behaviour_no_same_bird_GPS_within_15min']+=1;continue
        (native_time,lat,lon),lag=match
        source_qa['original_behaviour_true_same_bird_GPS_within_15min']+=1
        if label not in (LABEL_FORAGE,LABEL_INACTIVE):
            continue
        distance=_great_circle_km(lat,lon,*SOURCE_STATION_LAT_LON)
        for radius in geography_qa:
            if distance<=radius:
                by_radius[radius][bird][t.month][label]+=1
                geography_qa[radius]['source_original_GPS_linked_binary_class_events']+=1
            else:
                geography_qa[radius]['source_original_GPS_matched_events_farther_than_radius']+=1
    if all_rows!=ORIGINAL_BEHAVIOUR_ROWS or set(observed_labels)!=set(LABELS_FIXED) or any(
        observed_labels[label]!=expected for label,expected in LABELS_FIXED.items()) or (
        len(raw_class_source_birds)!=ORIGINAL_SOURCE_BIRDS):
        raise SourceStop('STOP_V126_PREVIOUS_V125_GENUINE_BEHAVIOUR_ROWS_LABELS_OR_BIRDS_NOT_REPRODUCED')
    reports={}
    for radius,bybird in by_radius.items():
        suitable=0
        native_monthly=defaultdict(lambda:{'birds':set(),'forage':0,'inactive':0})
        source_by_bird_n=Counter()
        for bird,months in bybird.items():
            totalforage=sum(v.get(LABEL_FORAGE,0) for v in months.values())
            totalinactive=sum(v.get(LABEL_INACTIVE,0) for v in months.values())
            months_with_both=sum(v.get(LABEL_FORAGE,0)>0 and v.get(LABEL_INACTIVE,0)>0 for v in months.values())
            if totalforage>=MIN_CLASS_EVENTS_PER_BIRD and totalinactive>=MIN_CLASS_EVENTS_PER_BIRD and months_with_both>=MIN_MONTHS_WITH_BOTH:
                suitable+=1
            for month,counts in months.items():
                if sum(counts.values()):
                    native_monthly[month]['birds'].add(bird)
                    native_monthly[month]['forage']+=counts.get(LABEL_FORAGE,0)
                    native_monthly[month]['inactive']+=counts.get(LABEL_INACTIVE,0)
            source_by_bird_n[bird]=totalforage+totalinactive
        reports[str(radius)]={'source_geo_radius_km':radius,
          'genuine_original_birds_with_2019_foraging_OR_inactive_GPS_matched_near_station':len(bybird),
          'genuine_original_birds_with_both_native_labels_ge100_each_in_ge2months':suitable,
          'native_original_month_source':{
              str(i):{'genuine_bird_count':len(native_monthly[i]['birds']),
                      'original_foraging_class_records':native_monthly[i]['forage'],
                      'original_inactive_class_records':native_monthly[i]['inactive']}
                      for i in range(1,13)},
          'future_genuine_bird_support_gate_8_birds_source_ONLY':suitable>=MIN_ORIGINAL_BIRDS,
          'min_max_true_original_binary_classifier_records_per_tracked_bird':[
              int(min(source_by_bird_n.values())),int(max(source_by_bird_n.values()))] if source_by_bird_n else None,
          'source_geography_coverage_QA':dict(geography_qa[radius]),
          'original_accessory_records_NOT_equal_true_bird_hours':True}
    return {'source_original_v125_2019_rows_exact_replayed':all_rows,
      'source_original_2019_classifier_label_counts_exact':dict(observed_labels),
      'source_original_2019_tagged_birds_source_exact_replayed':len(raw_class_source_birds),
      'original_source_matched_GPS_lag_seconds_MAX':JOIN_MAX_ABSOLUTE_SECS,
      'original_source_identity_and_time_QA':dict(source_qa),
      'original_2019_local_behavior_to_original_GPS_by_radii':reports,
      'source_primary_RWS_Vlieland_Haven_bird_GPS_radius_km':DISTANCE_PRIMARY_KM,
      'NO_2019_TIDE_SOLAR_BEHAVIOUR_Y_ESTIMATED':True,
      'original_individuals_native_coordinates_and_timestamps_not_exported':True}

def run(output):
    report={'analysis':'V126_ORIGINAL_2019_VLIELAND_NATIVE_FORAGE_INACTIVE_GPS_TIME_GEO_SOURCE_QA',
      'source_status':'SOURCE_PENDING',
      'original_publisher_record':RECORD,'frozen_original_GPS_MD5':GPS_MD5,
      'native_labeled_foraging_class_exact':'forage',
      'source_frozen_no_2019_RWS_tide_solar_behavior_interaction':True,
      'source_year':ORIGINAL_YEAR}
    try:
        files,meta=original_publisher_manifest()
        report['original_reference_and_classification_manifest_MD5_proof']=meta
        ref,refreceipt=original_native_file(files['O_VLIELAND-reference-data.csv'])
        birdmap,refqa=_reference_anonymous_identity(ref)
        report['original_public_reference_anonymized_source_QA']={**refreceipt,**refqa}
        raw,accreceipt=original_native_file(files[BEHAVIOUR_FILE])
        report['original_2019_classification_native_source_MD5_proof']=accreceipt
        gps,gps_proof=authenticate_original_gps_2019()
        report['original_2019_native_GPS_MD5_proof']=gps_proof
        indexed,gpsqa=original_2019_gps_source_index(gps,birdmap)
        report['original_year2019_GPS_native_source_count_and_monthly_QA']=gpsqa
        joined=true_original_2019_behaviour_gps_join(raw,birdmap,indexed)
        report['original_2019_native_samebird_ACC_classification_GPS_time_space_link']=joined
        report['source_status']='ADMITTED_PUBLISHER_2019_VLIELAND_FORAGE_GPS_15MIN_25KM_SOURCE_ONLY'
    except (TemporarySourceFailure,SourceStop,ValueError,UnicodeDecodeError,OSError,json.JSONDecodeError) as e:
        report['source_status']='SOURCE_STOP_2019_VLIELAND_GENUINE_GPS_ACC_LINK'
        report['original_source_blocker']=str(e)[:240]
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    a=report.get('original_2019_native_samebird_ACC_classification_GPS_time_space_link') or {}
    print('V126_REAL_2019_VLIELAND_FORAGE_INACTIVE_GPS_15MIN_SOURCE_FINAL '+json.dumps({
      'status':report['source_status'],
      'genuine_2019_GPS_source':report.get('original_year2019_GPS_native_source_count_and_monthly_QA'),
      '2019_original_25km_radius_source':a.get('original_2019_local_behavior_to_original_GPS_by_radii',{}).get('25.0'),
      'original_genuine_behavior_GPS_timestamp_source_QA':a.get('original_source_identity_and_time_QA'),
      'native_original_blocker':report.get('original_source_blocker'),
      'NO_GENUINE_2019_TIDE_SUN_OR_BEHAVIOR_UTILITY_ESTIMATED':True},sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
