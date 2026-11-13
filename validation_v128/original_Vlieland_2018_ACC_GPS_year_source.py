"""v128 honest 2018 independent-calendar-year original Vlieland oystercatcher
ACC-predicted forage/inactive + native GPS SOURCE feasibility only.
Published 2018 and 2019 GPS bird ID overlap checked privately, no identities
exported. Does NOT evaluate 2018 tide, sun or behavior response Y.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime
from bisect import bisect_left
from hashlib import md5,sha256
from io import BytesIO,TextIOWrapper
from pathlib import Path
from urllib.parse import urlparse
import argparse,csv,gzip,json,math
from original_2019_Vlieland_behaviour_source import (
    _publisher_get,exact_source_transport_retry,_reference_anonymous_identity,
    _native_datetime,API,PUBLISHER,RECORD,SourceStop)
from real_2019_Vlieland_foraging_GPS_source import (
    _great_circle_km,SOURCE_STATION_LAT_LON,JOIN_MAX_ABSOLUTE_SECS,
    _bird_id_from_native,_nearest_real_original_gps)

YEAR=2018
FROZEN_MONTHS=(6,7,8,9)
FROZEN_RADIUS=25.
SOURCE_ALT_RADII=(15.,35.)
ORIGINAL_2018_ACC='O_VLIELAND-accessory-measurements-2018.csv.gz'
ORIGINAL_2018_GPS='O_VLIELAND-gps-2018.csv.gz'
ORIGINAL_2019_GPS='O_VLIELAND-gps-2019.csv.gz'
ORIGINAL_REFERENCE='O_VLIELAND-reference-data.csv'
NATIVE_MD5={
 ORIGINAL_2018_ACC:'2b079f5504a692a02db57dc7116e5a67',
 ORIGINAL_2018_GPS:'113a796ab087234f4282b97af02e7559',
 ORIGINAL_2019_GPS:'65426aedf6f48c36f81990268d267c7b',
 ORIGINAL_REFERENCE:'26638a0cc481e32ab7d744263741db62'}
MAX_BY_FILE={ORIGINAL_2018_ACC:36_000_000,ORIGINAL_2018_GPS:125_000_000,
             ORIGINAL_2019_GPS:85_000_000,ORIGINAL_REFERENCE:500_000}
LABELS=('forage','inactive')
MIN_EVENTS_PER_LABEL=100
MIN_DIVERSE_MONTHS=2
MIN_BIRD_ELIGIBLE=8
MIN_QUARTERHOUR_BINS=1000
ACTUAL_2019_GPS_SOURCE_N=1193728
ACTUAL_2019_GPS_SOURCE_BIRDS=42

def immutable_original_manifest():
    raw,attempt=exact_source_transport_retry(
        lambda:_publisher_get(API,2_000_000),'2018_VLIELAND_ORIGINAL_METADATA')
    obj=json.loads(raw)
    if str(obj.get('id'))!=str(RECORD) or 'O_VLIELAND' not in str(obj.get('metadata',{}).get('title','')):
        raise SourceStop('STOP_2018_NATIVE_PUBLISHER_RECORD_WRONG')
    found={}
    for item in obj.get('files') or []:
        k=item.get('key')
        if k not in NATIVE_MD5:continue
        hash_=str(item.get('checksum') or '').removeprefix('md5:')
        url=(item.get('links') or {}).get('self') or (item.get('links') or {}).get('content')
        size=item.get('size')
        if (k in found or hash_!=NATIVE_MD5[k] or not isinstance(size,int) or
            not (0<size<MAX_BY_FILE[k]) or not isinstance(url,str) or
            not url.startswith(PUBLISHER+'/')):
            raise SourceStop('STOP_2018_GENUINE_ZENODO_ORIGINAL_MD5_SIZE_OR_LINK_'+str(k))
        found[k]={'original_file':k,'provider_MD5':hash_,'original_bytes':size,'private_source_url':url}
    if set(found)!=set(NATIVE_MD5):
        raise SourceStop('STOP_2018_GENUINE_ORIGINAL_GPS_ACC_REF_2019_OVERLAP_FILES_MISSING')
    return found,{'original_2018_primary_record':RECORD,
         'source_2018_and_2019_original_metadata_SHA256':sha256(raw).hexdigest(),
         'original_pub_source_file_catalog':[{'name':k,'bytes':v['original_bytes'],
                                              'publisher_MD5':v['provider_MD5']}
                                             for k,v in sorted(found.items())],
         'publisher_original_metadata_transport':attempt,
         'no_original_animal_IDs_or_CSV_rows_exported':True}

def original_bytes(item):
    raw,transport=exact_source_transport_retry(
      lambda:_publisher_get(item['private_source_url'],MAX_BY_FILE[item['original_file']]),
      'genuine_original_Vlieland_'+item['original_file'])
    if len(raw)!=item['original_bytes'] or md5(raw).hexdigest()!=item['provider_MD5']:
        raise SourceStop('STOP_V128_NATIVE_SOURCE_BYTES_MD5_DIFF_'+item['original_file'])
    return raw,{'source_original_filename':item['original_file'],
         'source_MD5_from_real_publisher_reverified':True,
         'source_raw_original_bytes':len(raw),
         'source_SHA256_for_original_content':sha256(raw).hexdigest(),
         'source_transport':transport}

def original_GPS_bird_year(raw,year,ref,build_bird_index):
    if raw[:2]!=b'\x1f\x8b':raise SourceStop('STOP_V128_TRUE_ORIGINAL_GPS_NOT_GZIP')
    reader=csv.DictReader(TextIOWrapper(gzip.GzipFile(fileobj=BytesIO(raw)),
                                        encoding='utf-8-sig',newline=''))
    hdr=reader.fieldnames or []
    if not ({'timestamp','location-lat','location-long'}<=set(hdr) and
        {'tag-local-identifier','individual-local-identifier'}&set(hdr)):
        raise SourceStop('STOP_V128_NATIVE_2018_2019_GPS_COLUMNS_MISSING')
    count=0;reason=Counter();bird_month=defaultdict(set);birdset=set()
    bybird=defaultdict(list)
    for row in reader:
        count+=1
        bird=_bird_id_from_native(row,ref)
        if not bird:reason['GPS_original_identity_unresolved']+=1;continue
        if str(row.get('visible') or '').strip().upper() in ('FALSE','0'):
            reason['GPS_original_invisible']+=1;continue
        try:
            dt=_native_datetime(row.get('timestamp'))
            lat=float(row['location-lat']);lon=float(row['location-long'])
        except (ValueError,TypeError):
            reason['GPS_original_coordinate_or_timestamp_bad']+=1;continue
        if dt.year!=year or not (math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180):
            reason['GPS_original_year_or_WGS84_invalid']+=1;continue
        birdset.add(bird);bird_month[dt.month].add(bird)
        if build_bird_index:
            bybird[bird].append((dt,lat,lon))
    if year==2019 and (count!=ACTUAL_2019_GPS_SOURCE_N or
                       len(birdset)!=ACTUAL_2019_GPS_SOURCE_BIRDS):
        raise SourceStop('STOP_V128_2019_ORIGINAL_GPS_SOURCE_NOT_EXACT_REPLAYED')
    indexed={}
    if build_bird_index:
        for bird,events in bybird.items():
            events.sort(key=lambda x:x[0])
            indexed[bird]=([v[0] for v in events],events)
    return indexed,birdset,{'original_source_year':year,
       'genuine_original_GPS_rows':count,
       'original_annual_independent_genuine_birds_with_GPS':len(birdset),
       'native_real_GPS_birds_per_month':{str(m):len(bird_month[m]) for m in range(1,13)},
       'original_source_rejected_GPS_QA':dict(reason),
       'original_source_index_only_ephemeral_or_not_built':build_bird_index,
       'original_tagged_bird_ID_and_real_GPS_positions_not_exported':True}

def original_2018_ACC_GPS_source_feasibility(raw,ref,indexed):
    if raw[:2]!=b'\x1f\x8b':
        raise SourceStop('STOP_V128_ACC_ORIGINAL_2018_NOT_GZIP')
    reader=csv.DictReader(TextIOWrapper(gzip.GzipFile(fileobj=BytesIO(raw)),
                                        encoding='utf-8-sig',newline=''))
    columns=reader.fieldnames or []
    if not {'timestamp','behavioural-classification'}<=set(columns):
        raise SourceStop('STOP_V128_2018_BEHAVIOUR_CLASSIFIER_NATIVE_SCHEMA_CHANGED')
    labels=Counter();years=Counter();qa=Counter()
    bird_all=set();true_months=defaultdict(lambda:defaultdict(Counter))
    birdmonth=defaultdict(lambda:defaultdict(Counter))
    class_25km_bird_bins=set()
    num=0
    for row in reader:
        num+=1
        rawlabel=str(row.get('behavioural-classification') or '').strip().casefold()
        labels[rawlabel]+=1
        bird=_bird_id_from_native(row,ref)
        if not bird:qa['ACC_original_bird_identity_not_resolved']+=1;continue
        bird_all.add(bird)
        if str(row.get('visible') or '').strip().upper() in ('FALSE','0'):
            qa['ACC_native_invisible']+=1;continue
        try:dt=_native_datetime(row.get('timestamp'))
        except ValueError:
            qa['ACC_timestamp_bad']+=1;continue
        if dt.year!=YEAR:
            qa['ACC_original_different_year']+=1
            continue
        if rawlabel not in LABELS or dt.month not in FROZEN_MONTHS:
            continue
        qa['source_original_ACC_binary_events_2018_JuneSep_before_GPS']+=1
        match=_nearest_real_original_gps(indexed,bird,dt)
        if match is None:
            qa['ACC_original_2018_no_samebird_GPS_within15min']+=1
            continue
        (_fix,lat,lon),lag=match
        qa['ACC_original_2018_samebird_GPS_match_within15min']+=1
        r=_great_circle_km(lat,lon,*SOURCE_STATION_LAT_LON)
        for radius in (FROZEN_RADIUS,)+SOURCE_ALT_RADII:
            if r<=radius:
                true_months[radius][dt.month][rawlabel]+=1
                # Confidential real bird ID keyed in-memory only.
                if radius==FROZEN_RADIUS:
                    birdmonth[bird][dt.month][rawlabel]+=1
            else: qa[f'ACC_original_2018_OUTSIDE_source_{radius}km']+=1
        if r<=FROZEN_RADIUS:
            timebin=dt.replace(minute=dt.minute//15*15,second=0,microsecond=0)
            class_25km_bird_bins.add((bird,timebin))
    if LABELS[0] not in labels or LABELS[1] not in labels:
        raise SourceStop('STOP_V128_NATIVE_2018_LITERAL_FORAGE_OR_INACTIVE_CATEGORY_ABSENT')
    qualified=[]
    for bird,monthly in birdmonth.items():
        nF=sum(m.get('forage',0) for m in monthly.values())
        nI=sum(m.get('inactive',0) for m in monthly.values())
        n_months=sum(m.get('forage',0)>0 and m.get('inactive',0)>0 for m in monthly.values())
        if nF>=MIN_EVENTS_PER_LABEL and nI>=MIN_EVENTS_PER_LABEL and n_months>=MIN_DIVERSE_MONTHS:
            qualified.append(bird)
    monthsummary={}
    for m in FROZEN_MONTHS:
        monthsummary[str(m)]={
          'source_original_foraging_ACC_events_at_25km':int(true_months[25.][m]['forage']),
          'source_original_inactive_ACC_events_at_25km':int(true_months[25.][m]['inactive']),
          'genuine_original_bird_count_with_at_least_one_binary_GPS_ACC_25km':int(
              sum(bool(x.get(m)) for x in birdmonth.values()))}
    return {
        'original_2018_ACC_full_year_raw_rows':num,
        'original_2018_classification_original_native_label_counts':dict(labels),
        'original_2018_original_annual_birds_with_identity_for_ACC':len(bird_all),
        'original_native_ACC_schema':columns,
        'source_2018_original_gps_acc_15min_classified_source_QA':dict(qa),
        'source_original_genuine_birds_with_any_binary_25km_source':len(birdmonth),
        'source_original_genuine_birds_ge100_EACH_class_two_2018_months':len(qualified),
        'source_original_2018_bird_quarterhour_binary_classes_25km_n':len(class_25km_bird_bins),
        'source_original_2018_25km_monthly_true_bird_binary_classes':monthsummary,
        'source_original_2018_alternate_radius_binary_class_event_n':{
           str(r):int(sum(sum(v.values()) for v in true_months[r].values()))
           for r in (FROZEN_RADIUS,)+SOURCE_ALT_RADII},
        'source_frozen_YEAR2018_bird_ge8_15minute_bins_ge1000_eligible':(
           len(qualified)>=MIN_BIRD_ELIGIBLE and len(class_25km_bird_bins)>=MIN_QUARTERHOUR_BINS),
        'future_genuine_2018_RWS_tide_sun_or_behavioral_effect':'NOT_ESTIMATED_SOURCE_ONLY',
        'original_bird_identity_source_labels_and_precise_location_PRIVATE':True
    },set(qualified)

def run(output):
    report={'analysis':'V128_ORIGINAL_VLIELAND_2018_INDEPENDENT_CALENDAR_YEAR_ACC_GPS_SOURCE_GATE',
        'source_status':'SOURCE_PENDING','original_2018_fixed_months':[6,7,8,9],
        'source_2018_native_GPS_and_ACC_original_expected_MD5':NATIVE_MD5,
        '2018_source_year_chosen_AFTER_original_2019_v127_solar_result':True,
        'original_2018_actual_RWS_tide_and_acc_FORAGE_share_NOT_ESTIMATED':True,
        'identities_source_stay_in_transient_CI_not_repository_artifacts':True}
    try:
        files,manifest=immutable_original_manifest()
        report['original_Zenodo_2018_2019_original_metadata']=manifest
        raw_ref,p_ref=original_bytes(files[ORIGINAL_REFERENCE])
        ref,refQA=_reference_anonymous_identity(raw_ref)
        report['original_reference_source_MD5_proof']={**p_ref,**refQA}
        raw18,p18=original_bytes(files[ORIGINAL_2018_GPS])
        indexed,b18,gps18=original_GPS_bird_year(raw18,2018,ref,True)
        report['source_original_2018_GPS_true_source_QA']=gps18
        report['source_original_2018_publisher_GPS_receipt']=p18
        del raw18
        raw19,p19=original_bytes(files[ORIGINAL_2019_GPS])
        _,b19,gps19=original_GPS_bird_year(raw19,2019,ref,False)
        report['source_original_2019_GPS_unchanged_source_replay_for_bird_overlap']=gps19
        report['source_original_2019_GPS_MD5_receipt']=p19
        report['source_anonymous_true_2018_vs_2019_GPS_individual_overlap']={
          'original_2018_genuine_GPS_birds':len(b18),
          'original_2019_genuine_GPS_birds':len(b19),
          'same_true_tagged_birds_recorded_in_BOTH_2018_and2019_GPS_years':len(b18&b19),
          'original_2018_only_tagged_birds':len(b18-b19),
          'original_2019_only_tagged_birds':len(b19-b18),
          'source_new_2018_year_not_independent_2019_bird_replicates':len(b18&b19)>0}
        del raw19
        rawacc,pacc=original_bytes(files[ORIGINAL_2018_ACC])
        source,qual=original_2018_ACC_GPS_source_feasibility(rawacc,ref,indexed)
        report['original_2018_ACC_publisher_full_MD5_receipt']=pacc
        report['original_2018_samebird_ACC_class_and_GPS_25km_source_QA']=source
        report['source_status']='TRUE_PUBLISHER_2018_VLIELAND_GPS_ACC_BIN_FEASIBILITY_ADMITTED'
    except (SourceStop,ValueError,TypeError,OSError,UnicodeDecodeError,json.JSONDecodeError) as e:
        report['source_status']='SOURCE_STOP_ORIGINAL_2018_VLIELAND_GPS_ACC'
        report['source_blocker']=str(e)[:280]
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    src=report.get('original_2018_samebird_ACC_class_and_GPS_25km_source_QA') or {}
    print('V128_TRUE_ORIGINAL_VLIELAND_2018_INDEPENDENT_YEAR_SOURCE '+json.dumps({
       'status':report['source_status'],
       'original_2018_gps':report.get('source_original_2018_GPS_true_source_QA'),
       'original_2018_true_2019_bird_overlap':report.get('source_anonymous_true_2018_vs_2019_GPS_individual_overlap'),
       'original_2018_ACC_GPS_source':src,
       'original_source_blocker':report.get('source_blocker'),
       'NO_2018_RWS_TIDE_SOLAR_OR_BIOLOGICAL_EFFECT_YET':True},sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
