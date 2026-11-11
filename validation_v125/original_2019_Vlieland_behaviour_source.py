"""v125 ORIGINAL Vlieland 2019 and 2020 accelerometer-derived behavioural
classifications SOURCE ONLY. Native first-party Zenodo v3 publisher MD5,
reference identity, timestamp and raw class frequency census.
DO NOT report observed feeding, actual foraging minutes, bird GPS, live tide,
sun-specific behaviour, or a circatidal clock without separate join/gauge.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256,md5
from io import BytesIO,StringIO,TextIOWrapper
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse
import argparse,csv,gzip,json,time

RECORD=10053988
PUBLISHER="https://zenodo.org"
API=PUBLISHER+f"/api/records/{RECORD}"
STUDY='O_VLIELAND'
FIRST_YEAR=2019
SECOND_YEAR=2020
FREEZE={
    'datapackage.json':'63d182624aff30fda1db665e8ae49087',
    'O_VLIELAND-reference-data.csv':'26638a0cc481e32ab7d744263741db62',
    'O_VLIELAND-accessory-measurements-2019.csv.gz':'a902b08ff0163edf91a9bcf3822b1c97',
    'O_VLIELAND-accessory-measurements-2020.csv.gz':'e2588eb066ac904dd330fcb458f455a3',
}
GPS_FUTURE_PUBLISHER_MD5={
    2019:'65426aedf6f48c36f81990268d267c7b',
    2020:'af53b89e0a096322e702ca3f88d45d22',
}
MAX_BYTES=36_000_000
MAX_META=1_500_000
EXPECTED_BEHAVIOR_COLUMN='behavioural-classification'
SOURCE_YEAR_LABELS=(2019,2020)
CLASS_FROZEN_FOR_FUTURE='foraging'
CLASS_FROZEN_REFERENCE='inactive'
SOURCE_YEAR_BIRDS_MIN_FUTURE=8
SOURCE_YEAR_CLASS_EVENTS_EACH_MIN_FUTURE=100
SOURCE_YEAR_MONTHS_MIN_FUTURE=2

class SourceStop(Exception): pass
class TemporarySourceFailure(SourceStop):pass

def _publisher_get(url,max_bytes=MAX_BYTES):
    if not (isinstance(url,str) and url.startswith(PUBLISHER+"/")):
        raise SourceStop('STOP_UNTRUSTED_NOT_ORIGINAL_ZENODO_VLIELAND_PUBLISHER_URL')
    request=Request(url,headers={
       'Accept':'application/json,application/gzip,text/csv,application/octet-stream,*/*',
       'User-Agent':'boids-v125-original-Vlieland-2019-2020-native-accelerometer-derived-behaviour/1.0'})
    try:
        with urlopen(request,timeout=120) as r:
            if urlparse(r.geturl()).scheme!='https':
                raise SourceStop('STOP_SOURCE_REDIRECT_NOT_HTTPS')
            body=r.read(max_bytes+1)
            if len(body)>max_bytes:raise SourceStop('STOP_ORIGINAL_PUBLISHER_SOURCE_TOO_LARGE')
            return body
    except HTTPError as e:
        if e.code in (429,502,503,504):
            raise TemporarySourceFailure('TEMP_ORIGINAL_ZENODO_HTTP_'+str(e.code)) from e
        raise SourceStop('STOP_ORIGINAL_ZENODO_HTTP_'+str(e.code)) from e
    except (URLError,TimeoutError) as e:
        raise TemporarySourceFailure('TEMP_ORIGINAL_ZENODO_TIMEOUT_OR_NETWORK_'+str(e)[:140]) from e

def exact_source_transport_retry(action,scope,sleeper=time.sleep):
    errors=[]
    for i in range(3):
        try:
            return action(),{'same_exact_source_attempts':i+1,
              'previous_original_provider_TRANSPORT_errors':errors}
        except TemporarySourceFailure as e:
            errors.append({'source':scope,'attempt':i+1,'transport_only':str(e)[:120]})
            if i==2:raise
            sleeper((i+1)*3)
    raise AssertionError('unreachable')

def original_publisher_manifest():
    raw,attempts=exact_source_transport_retry(
       lambda:_publisher_get(API,MAX_META),'zenodo-vlieland-10053988-metadata')
    try:obj=json.loads(raw)
    except ValueError as e:raise SourceStop('STOP_ORIGINAL_ZENODO_MANIFEST_INVALID_JSON') from e
    if str(obj.get('id'))!=str(RECORD) or STUDY not in str(obj.get('metadata',{}).get('title','')):
        raise SourceStop('STOP_WRONG_ORIGINAL_VLIELAND_PUBLISHER_RECORD')
    observed={}
    for record in obj.get('files') or []:
        name=record.get('key')
        if name not in FREEZE:continue
        if name in observed:raise SourceStop('STOP_DUPLICATE_ORIGINAL_NATIVE_FILE_IN_RECORD')
        digest=str(record.get('checksum') or '').removeprefix('md5:').lower()
        if digest!=FREEZE[name]:
            raise SourceStop('STOP_FROZEN_SOURCE_VERSION_OR_PUBLISHER_MD5_DRIFT_'+name)
        sourceurl=(record.get('links') or {}).get('self') or (record.get('links') or {}).get('content')
        n=record.get('size')
        if (not isinstance(sourceurl,str) or not sourceurl.startswith(PUBLISHER+"/")
              or not isinstance(n,int) or n<=0 or n>MAX_BYTES):
            raise SourceStop('STOP_ORIGINAL_ZENODO_FILE_LINK_OR_SIZE_MALFORMED_'+name)
        observed[name]={'native_filename':name,'source_publisher_md5':digest,
                        'source_publisher_length_bytes':n,
                        'original_source_download_URL':sourceurl}
    if set(observed)!=set(FREEZE):
        raise SourceStop('STOP_VLIELAND_CORRECTED_ORIGINAL_FOUR_FILES_MISSING')
    return observed,{'publisher_record_ID':RECORD,
       'source_native_public_title':obj['metadata'].get('title'),
       'source_original_Zenodo_metadata_SHA256':sha256(raw).hexdigest(),
       'source_metadata_transport':attempts,
       'source_2019_primary_2020_secondary_frozen_before_behaviour':True,
       'original_file_names_sizes_and_MD5_only':[
           {k:v for k,v in item.items() if k!='original_source_download_URL'}
           for item in observed.values()]}

def original_native_file(item):
    source=item['native_filename']
    raw,attempt=exact_source_transport_retry(lambda:_publisher_get(
        item['original_source_download_URL']),'vlieland-original-'+source)
    if len(raw)!=item['source_publisher_length_bytes'] or md5(raw).hexdigest()!=item['source_publisher_md5']:
        raise SourceStop('STOP_ORIGINAL_ZENODO_SOURCE_BYTES_OR_MD5_MISMATCH_'+source)
    return raw,{'native_original_file_name':source,
        'source_publisher_MD5_exactly_verified':True,
        'original_downloaded_bytes':len(raw),
        'original_source_SHA256_local':sha256(raw).hexdigest(),
        'source_transport_only':attempt}

def _reference_anonymous_identity(original_reference):
    reader=csv.DictReader(StringIO(original_reference.decode('utf-8-sig')))
    cols=reader.fieldnames or []
    tagmap=defaultdict(set)
    n=0
    methods=Counter()
    for row in reader:
        n+=1
        t=(row.get('tag-local-identifier') or '').strip()
        bird=(row.get('individual-local-identifier') or '').strip()
        if t and bird:tagmap[t].add(bird)
        for k,v in row.items():
            if 'behavio' in str(k).lower() and v and str(v).strip():
                methods[str(k).strip()]+=1
    unique={t:next(iter(b)) for t,b in tagmap.items() if len(b)==1}
    return unique,{'original_reference_rows':n,
        'original_reference_column_names':cols,
        'source_native_tags_with_unambiguous_single_bird_across_deployments':len(unique),
        'source_native_tags_with_ambiguous_reassigned_bird_ID':sum(len(b)!=1 for b in tagmap.values()),
        'native_behavior_method_reference_columns_present':dict(methods),
        'original_bird_tags_OR_personally_identifying_ID_NOT_exposed':True}

def original_resource_schema(package,year):
    resources=package.get('resources') or []
    filename=f'{STUDY}-accessory-measurements-{year}.csv.gz'
    matches=[r for r in resources if filename in str(r.get('path') or r.get('name') or '')]
    if len(matches)!=1:
        raise SourceStop('STOP_ORIGINAL_FRICITIONLESS_BEHAVIOUR_RESOURCE_MISSING_'+str(year))
    resource=matches[0]
    fields=(resource.get('schema') or {}).get('fields') or []
    return {'source_resource_name':resource.get('name'),
      'source_resource_path':resource.get('path'),
      'native_field_names_and_type':[{
          'name':x.get('name'),'type':x.get('type'),
          'native_description':str(x.get('description') or '')[:210]}
          for x in fields if x.get('name') in (
             'timestamp','individual-local-identifier','tag-local-identifier',
             'behavioural-classification','visible','sensor-type','event-id')],
      'native_schema_declares_classification':any(x.get('name')==EXPECTED_BEHAVIOR_COLUMN for x in fields),
      'source_field_count':len(fields)}

def _native_datetime(value):
    try:
        dt=datetime.fromisoformat(str(value or '').strip().replace('Z','+00:00'))
    except (ValueError,TypeError) as e:
        raise ValueError('ORIGINAL_TIMESTAMP_MALFORMED') from e
    # Movebank native timestamp is declared UTC by its attribute dictionary;
    # this does NOT by itself certify GPS fix/ACC sensor sync or clock offset.
    if dt.tzinfo is not None:dt=dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def native_annual_classification_census(raw,year,reference_tag_to_bird):
    if year not in SOURCE_YEAR_LABELS:raise ValueError('STOP_UNFROZEN_NATIVE_YEAR')
    if raw[:2]!=b'\x1f\x8b':raise SourceStop('STOP_ORIGINAL_BEHAVIOUR_SOURCE_NOT_GZIP')
    try:
        text=TextIOWrapper(gzip.GzipFile(fileobj=BytesIO(raw)),encoding='utf-8-sig',newline='')
        reader=csv.DictReader(text)
        columns=reader.fieldnames or []
        if not {'timestamp',EXPECTED_BEHAVIOR_COLUMN}<=set(columns):
            raise SourceStop('STOP_ORIGINAL_MOVEBANK_NATIVE_BEHAVIOUR_SCHEMA_MISSING')
        if not ({'individual-local-identifier','tag-local-identifier'}&set(columns)):
            raise SourceStop('STOP_ORIGINAL_BEHAVIOUR_ANIMAL_TAG_IDENTITY_COLUMNS_MISSING')
        data=Counter()
        classes=Counter()
        months=defaultdict(Counter)
        by_bird=defaultdict(lambda:defaultdict(Counter))
        native_birds=set()
        visible_counter=Counter()
        n=0
        for row in reader:
            n+=1
            raw_label=str(row.get(EXPECTED_BEHAVIOR_COLUMN) or '').strip()
            if not raw_label:
                data['native_label_blank']+=1;continue
            observed=(row.get('visible') or '').strip().upper()
            if observed in ('FALSE','0'):
                visible_counter['explicitly_invisible']+=1
                continue
            visible_counter['visible_or_unset']+=1
            try:stamp=_native_datetime(row.get('timestamp'))
            except ValueError:
                data['native_timestamp_parse_failed']+=1;continue
            if stamp.year!=year:
                data['original_timestamp_year_outside_frozen_'+str(year)]+=1
                continue
            bird=(row.get('individual-local-identifier') or '').strip()
            if not bird:
                tag=(row.get('tag-local-identifier') or '').strip()
                bird=reference_tag_to_bird.get(tag,'')
            if not bird:
                data['unresolved_original_bird_identity']+=1
            else:native_birds.add(bird)
            key=raw_label.strip().lower()
            classes[raw_label]+=1
            months[stamp.month][key]+=1
            data['native_valid_date_and_nonblank_behaviour_label']+=1
            if bird:
                by_bird[bird][stamp.month][key]+=1
        qualified=[]
        for bird,period in by_bird.items():
            foraging=sum(sum(v for k,v in counts.items() if k==CLASS_FROZEN_FOR_FUTURE)
                         for counts in period.values())
            inactive=sum(sum(v for k,v in counts.items() if k==CLASS_FROZEN_REFERENCE)
                         for counts in period.values())
            months_both=sum(c.get(CLASS_FROZEN_FOR_FUTURE,0)>0 and
                c.get(CLASS_FROZEN_REFERENCE,0)>0 for c in period.values())
            if (foraging>=SOURCE_YEAR_CLASS_EVENTS_EACH_MIN_FUTURE and
                inactive>=SOURCE_YEAR_CLASS_EVENTS_EACH_MIN_FUTURE and
                months_both>=SOURCE_YEAR_MONTHS_MIN_FUTURE):
                qualified.append(bird)
        source_months={}
        for month in range(1,13):
            counts=months.get(month,Counter())
            birds={bird for bird,period in by_bird.items()
                   if period.get(month)}
            source_months[str(month)]={
               'native_behaviour_labeled_events':sum(counts.values()),
               'native_unique_original_birds_with_identifiable_events':len(birds),
               'native_exact_foraging_label_count':counts.get(CLASS_FROZEN_FOR_FUTURE,0),
               'native_exact_inactive_label_count':counts.get(CLASS_FROZEN_REFERENCE,0)}
        out={'original_year':year,'original_raw_classifier_csv_rows':n,
             'original_source_native_header_columns':columns,
             'native_valid_nonblank_class_rows_in_original_year':
                data['native_valid_date_and_nonblank_behaviour_label'],
             'original_distinct_birds_with_resolved_identity_ANY_behaviour_event':len(native_birds),
             'original_native_label_counts_case_preserving':dict(classes),
             'original_native_monthly_source_support':source_months,
             'native_missing_or_rejected_source_quality':dict(data),
             'native_visible_source_records':dict(visible_counter),
             'n_original_individuals_with_at_least100_foraging_and100_inactive_two_months':
                   len(qualified),
             'source_future_n8_birds_for_each_class_eligible_but_GPS_tide_NOT_JOINED':
                   len(qualified)>=SOURCE_YEAR_BIRDS_MIN_FUTURE,
             'time_recording_effort_unknown_DO_NOT_CALL_COUNT_ACTIVITY_HOURS':True,
             'native_original_behaviour_from_ACC_not_human_field_observed':True,
             'GPS_location_tide_sun_and_true_foraging_time_BIOLOGICAL_EFFECT':'NOT_ESTIMATED'}
        return out
    except (EOFError,OSError,UnicodeDecodeError,csv.Error) as e:
        raise SourceStop('STOP_NATIVE_ORIGINAL_BEHAVIOUR_GZIP_OR_CSV_DECODE_'+str(e)[:150]) from e

def run(path):
    report={'analysis':'V125_ORIGINAL_VLIELAND_2019_2020_ACCEL_DERIVED_BEHAVIOUR_CLASS_SOURCE_ONLY',
      'native_Zenodo_record_id':RECORD,
      'original_primary_year':FIRST_YEAR,'original_secondary_year':SECOND_YEAR,
      'frozen_original_source_MD5':FREEZE,
      'true_original_oystercatcher_ACC_classifications_NOT_field_seen_feeding':True,
      'not_2019_RWS_tide_or_sun_or_animal_time_niche':True,
      'source_status':'SOURCE_NOT_YET_ADMITTED','source_years':{}}
    try:
        files,manifest=original_publisher_manifest()
        report['source_manifest']=manifest
        source_schema,sp=original_native_file(files['datapackage.json'])
        source_reference,rp=original_native_file(files['O_VLIELAND-reference-data.csv'])
        package=json.loads(source_schema)
        if not isinstance(package,dict) or not package.get('resources'):
            raise SourceStop('STOP_VLIELAND_NATIVE_DATAPACKAGE_SCHEMA_NOT_VALID')
        mapping,ref_source=_reference_anonymous_identity(source_reference)
        report['original_source_Frictionless_datapackage_receipt']=sp
        report['original_source_reference_tag_mapping_anonymous_QA']={**rp,**ref_source}
        for year in SOURCE_YEAR_LABELS:
            fname=f'{STUDY}-accessory-measurements-{year}.csv.gz'
            row={'year':year,'source_status':'SOURCE_PENDING'}
            try:
                d,receipt=original_native_file(files[fname])
                schema=original_resource_schema(package,year)
                row['original_publisher_actual_behavior_bytes']=receipt
                row['original_Frictionless_native_behaviour_schema']=schema
                source=native_annual_classification_census(d,year,mapping)
                row['native_true_annual_source_counts']=source
                row['source_status']='ORIGINAL_YEAR_ACCEL_BEHAVIOUR_CLASSIFICATIONS_ADMITTED'
            except (TemporarySourceFailure,SourceStop,ValueError,UnicodeDecodeError) as e:
                row['source_status']='SOURCE_STOP_ORIGINAL_PUBLISHER_YEAR_'+str(year)
                row['source_blocker']=str(e)[:200]
            report['source_years'][str(year)]=row
            print('V125_NATIVE_VLIELAND_ACTUAL_BEHAVIOUR_SOURCE_YEAR '+json.dumps({
                'year':year,'status':row['source_status'],
                'actual_original_annual_census':row.get('native_true_annual_source_counts'),
                'original_publisher_blocker':row.get('source_blocker'),
                'no_tide_solar_or_GPS_behavioral_result':True},sort_keys=True),flush=True)
        if all(v['source_status']=='ORIGINAL_YEAR_ACCEL_BEHAVIOUR_CLASSIFICATIONS_ADMITTED'
             for v in report['source_years'].values()):
            report['source_status']='GENUINE_ORIGINAL_2019_2020_VLIELAND_BEHAVIOUR_SOURCE_BOTH_ADMITTED'
        else:report['source_status']='ORIGINAL_VLIELAND_BEHAVIOUR_SOURCE_PARTIAL_ONLY'
    except (TemporarySourceFailure,SourceStop,ValueError,OSError,json.JSONDecodeError) as e:
        report['source_status']='SOURCE_STOP_NATIVE_PUBLISHER_MANIFEST_OR_REFERENCE'
        report['source_blocker']=str(e)[:230]
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V125_TRUE_ORIGINAL_2019_2020_VLIELAND_FORAGING_BEHAVIOUR_SOURCE_FINAL '+json.dumps({
       'source_status':report['source_status'],
       'genuine_original_annual_source':{
           y:{'status':r['source_status'],
              'real_bird_n':(r.get('native_true_annual_source_counts') or {}).get(
                 'original_distinct_birds_with_resolved_identity_ANY_behaviour_event'),
              'original_rows':(r.get('native_true_annual_source_counts') or {}).get(
                 'original_raw_classifier_csv_rows'),
              'foraging_label':(r.get('native_true_annual_source_counts') or {}).get(
                 'original_native_label_counts_case_preserving'),
              'n_birds_foraging_inactive_source_gate':(r.get('native_true_annual_source_counts') or {}).get(
                 'n_original_individuals_with_at_least100_foraging_and100_inactive_two_months')}
           for y,r in report['source_years'].items()},
       'no_tide_or_sun_or_foraging_time_niche_effect_estimated':True},sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    run(p.parse_args().output)
