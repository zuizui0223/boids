"""v125 Independent Belgian 2020 original gull GPS SOURCE-only source gate.
Three public first-party INBO Zenodo studies, not new habitat or tide effects.
No bird identifiers, trajectories, exact positions, UTC stamps, raw files exported.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone,timedelta
from hashlib import sha256,md5
from math import radians,sin,cos,atan2,sqrt,isfinite
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import argparse,csv,gzip,io,json,time

PANELS={
 'LBBG_JUVENILE':{'record':22083230,'gps':'LBBG_JUVENILE-gps-2020.csv.gz',
  'md5':'85b9ce9fa0bcee3bcd982260763c7c14','colony':(51.341,3.182),
  'study':'independent juvenile BOTH focal species source candidate'},
 'HG_OOSTENDE':{'record':10054230,'gps':'HG_OOSTENDE-gps-2020.csv.gz',
  'md5':'9c48e6e5b9fa9fe5324568cc9e122bd9','colony':(51.233,2.931),
  'study':'independent adult herring gull source'},
 'LBBG_ZEEBRUGGE':{'record':12336021,'gps':'LBBG_ZEEBRUGGE-gps-2020.csv.gz',
  'md5':'a59224e9b0a771c422ce757811fb5585','colony':(51.341,3.182),
  'study':'independent adult lesser black-backed gull source'}}
FOCAL=('Larus argentatus','Larus fuscus')
YEAR=2020
MONTHS=(7,8,9,10)
RADIUS_KM=40.
MIN_BIRD_HOURS=20
MIN_TAXON_BIRDS=5
MIN_TAXON_HOURS=1000
MIN_MONTH_BIRDS=3
MIN_MONTH_HOURS=150
MIN_MONTHS=2
MIN_STEP_DATES=8
MIN_STEPS=2000
MIN_STEP_HOURS=.75
MAX_STEP_HOURS=1.50
MAX_DISPLACEMENT_KMH=150.
MAX_META_BYTES=1_000_000
MAX_GPS_BYTES=65_000_000
SOURCE_RUN_YEAR='2026-11-12'
REQUEST_ATTEMPTS=3
TAXON_COLUMNS=('individual-taxon-canonical-name','taxon-canonical-name',
               'scientific-name','individual-taxon-name')
BIRD_KEYS=('individual-local-identifier','individual-id','animal-id')
EXPECTED_GPS_COLS={'timestamp','location-lat','location-long',
                   'individual-local-identifier'}

class OriginalSourceStop(Exception):pass

def get_publisher(url,limit=MAX_GPS_BYTES,fetch_fn=None,sleeper=time.sleep):
    if not url.startswith('https://zenodo.org/'):
        raise OriginalSourceStop('SOURCE_STOP_NOT_ZENODO_FIRST_PARTY')
    for attempt in range(REQUEST_ATTEMPTS):
        try:
            if fetch_fn is not None:
                data=fetch_fn(url)
            else:
                req=Request(url,headers={
                  'Accept':'application/json,application/gzip,text/csv,*/*',
                  'User-Agent':'boids-v125-independent-Belgian-gull-2020-source-only/1.0'})
                with urlopen(req,timeout=85) as resp:
                    if not resp.geturl().startswith('https://zenodo.org/'):
                        raise OriginalSourceStop('SOURCE_STOP_NON_PUBLISHER_REDIRECT')
                    data=resp.read(limit+1)
            if len(data)>limit:
                raise OriginalSourceStop('SOURCE_STOP_NATIVE_ORIGINAL_ZENODO_BYTES_TOO_LARGE')
            return data,attempt+1
        except HTTPError as e:
            if e.code not in (429,502,503,504) or attempt==REQUEST_ATTEMPTS-1:
                raise OriginalSourceStop('SOURCE_UNAVAILABLE_OFFICIAL_ZENODO_HTTP_'+str(e.code)) from e
        except (URLError,TimeoutError) as e:
            if attempt==REQUEST_ATTEMPTS-1:
                raise OriginalSourceStop('SOURCE_UNAVAILABLE_OFFICIAL_ZENODO_TRANSPORT') from e
        sleeper(2**attempt)
    raise OriginalSourceStop('SOURCE_STOP_PUBLISHER_RETRY_EXHAUSTED')

def native_catalog(panel,fetch_fn=None):
    item=PANELS[panel]
    url=f"https://zenodo.org/api/records/{item['record']}"
    raw,attempts=get_publisher(url,MAX_META_BYTES,fetch_fn=fetch_fn)
    try:obj=json.loads(raw)
    except (UnicodeDecodeError,ValueError) as e:
        raise OriginalSourceStop('SOURCE_STOP_NATIVE_ZENODO_CATALOG_NOT_JSON') from e
    if int(obj.get('id',-1))!=item['record']:
        raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_ZENODO_RECORD_IDENTITY')
    title=(obj.get('metadata') or {}).get('title') or ''
    if panel not in title and panel not in str((obj.get('metadata') or {}).get('description') or ''):
        raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_PUBLISHED_STUDY_TITLE_IDENTITY')
    required={item['gps'],panel+'-reference-data.csv','datapackage.json'}
    files={}
    for f in obj.get('files') or []:
        name=f.get('key')
        if name not in required:continue
        digest=f.get('checksum') or ''
        if digest.startswith('md5:'):digest=digest[4:]
        uri=(f.get('links') or {}).get('self') or (f.get('links') or {}).get('content')
        size=f.get('size')
        if (not isinstance(uri,str) or not uri.startswith('https://zenodo.org/') or
            not isinstance(size,int) or size<=0 or size>MAX_GPS_BYTES or
            len(digest)!=32 or name in files):
            raise OriginalSourceStop('SOURCE_STOP_PUBLISHER_NATIVE_FILE_ID_MD5_SIZE_OR_URL')
        files[name]={'url':uri,'md5':digest,'size':size,'name':name}
    if set(files)!=required:
        raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_PUBLISHER_GPS_REFERENCE_SCHEMA_INCOMPLETE')
    if files[item['gps']]['md5']!=item['md5']:
        raise OriginalSourceStop('SOURCE_STOP_2020_GPS_MD5_FROZEN_BEFORE_SOURCE_DRIFT')
    proof={'original_2020_source_study':panel,
        'original_published_record':item['record'],
        'publisher_title':title,
        'native_record_metadata_sha256':sha256(raw).hexdigest(),
        'catalogue_request_attempts':attempts,
        'original_files':[{'name':v['name'],'bytes':v['size'],'md5':v['md5']}
                          for v in files.values()],
        'source_tags_cumulative_are_NOT_2020_tagged_birds':True}
    return files,proof

def checked_original_file(file,fetch_fn=None):
    raw,attempts=get_publisher(file['url'],MAX_GPS_BYTES,fetch_fn=fetch_fn)
    if len(raw)!=file['size'] or md5(raw).hexdigest()!=file['md5']:
        raise OriginalSourceStop('SOURCE_STOP_REAL_PUBLISHER_GPS_OR_REFERENCE_MD5_BYTES_CHANGED')
    return raw,{'file':file['name'],'publisher_original_MD5_verified':True,
                'actual_source_file_bytes':len(raw),'local_source_SHA256':sha256(raw).hexdigest(),
                'source_transport_attempts':attempts}

def source_taxon(row):
    for key in TAXON_COLUMNS:
        value=(row.get(key) or '').strip()
        if value:return value
    return None

def source_reference_taxa(raw):
    try:
        reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
        cols=reader.fieldnames or []
        labels=defaultdict(set)
        for row in reader:
            bird=next(((row.get(k) or '').strip() for k in BIRD_KEYS
                       if (row.get(k) or '').strip()),None)
            label=source_taxon(row)
            if bird and label:labels[bird].add(label)
    except (UnicodeDecodeError,csv.Error) as e:
        raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_REFERENCE_TAXON_CSV_DECODE') from e
    resolved={bird:next(iter(names)) for bird,names in labels.items() if len(names)==1}
    return resolved,{'reference_original_source_columns':cols,
       'reference_ids_with_unique_taxon':len(resolved),
       'reference_ids_with_ambiguous_taxon':sum(len(names)>1 for names in labels.values())}

def great_circle(lat1,lon1,lat2,lon2):
    phi1,phi2=radians(lat1),radians(lat2)
    dphi=radians(lat2-lat1);dlam=radians(lon2-lon1)
    a=sin(dphi/2)**2+cos(phi1)*cos(phi2)*sin(dlam/2)**2
    return 12742*atan2(sqrt(max(0,a)),sqrt(max(0,1-a)))

def parse_native_gps(raw,reference,panel):
    spec=PANELS[panel];center=spec['colony']
    try:
        reader=csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(raw)),
                                               encoding='utf-8-sig'))
        heads=reader.fieldnames or []
    except (UnicodeDecodeError,OSError,csv.Error) as e:
        raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_2020_GPS_NOT_TRUE_CSV_GZIP') from e
    if not EXPECTED_GPS_COLS<=set(heads):
        raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_GPS_MOVEBANK_REQUIRED_COLUMNS_MISSING')
    points=defaultdict(dict)
    bybirdtaxon=defaultdict(set)
    bad=Counter();native_rows=0;native_juloct_rows=0
    try:
        for row in reader:
            native_rows+=1
            bird=(row.get('individual-local-identifier') or '').strip()
            if not bird:
                bad['native_missing_bird_id']+=1;continue
            if str(row.get('visible','')).strip().upper() in ('0','FALSE'):
                bad['native_invisible_fix']+=1;continue
            st=(row.get('timestamp') or '').strip()
            try:
                stamp=datetime.fromisoformat(st.replace('Z','+00:00'))
                if stamp.tzinfo is not None:stamp=stamp.astimezone(timezone.utc).replace(tzinfo=None)
                lat=float(row['location-lat']);lon=float(row['location-long'])
            except (TypeError,ValueError):
                bad['native_timestamp_or_coordinate_unreadable']+=1;continue
            if stamp.year!=YEAR or stamp.month not in MONTHS:continue
            native_juloct_rows+=1
            if not (isfinite(lat) and isfinite(lon) and -90<=lat<=90 and -180<=lon<=180):
                bad['native_invalid_WGS84_location']+=1;continue
            tax=source_taxon(row) or reference.get(bird)
            if tax:bybirdtaxon[bird].add(tax)
            hour=stamp.replace(minute=0,second=0,microsecond=0)
            old=points[bird].get(hour)
            if old is None or stamp<old[0]:
                points[bird][hour]=(stamp,lat,lon)
    except (UnicodeDecodeError,csv.Error,OSError) as e:
        raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_NATIVE_GPS_DATA_ROWS_INVALID') from e
    counts={}
    allnative=Counter()
    for bird,fixes in points.items():
        group=bybirdtaxon.get(bird) or set()
        tax=next(iter(group)) if len(group)==1 else 'UNKNOWN_OR_AMBIGUOUS_ORIGINAL_TAXON'
        if tax not in FOCAL:bad['original_bird_taxon_not_resolved_to_focal']+=1
        allnative[tax]+=len(fixes)
    for tax in (*FOCAL,'UNKNOWN_OR_AMBIGUOUS_ORIGINAL_TAXON'):
        coastal={}
        for bird,fixes in points.items():
            label=bybirdtaxon.get(bird) or set()
            name=next(iter(label)) if len(label)==1 else 'UNKNOWN_OR_AMBIGUOUS_ORIGINAL_TAXON'
            if name!=tax:continue
            coastal_fix={hour:p for hour,p in fixes.items() if
                         great_circle(p[1],p[2],*center)<=RADIUS_KM}
            if coastal_fix:coastal[bird]=coastal_fix
        eligible={bird:fixes for bird,fixes in coastal.items() if len(fixes)>=MIN_BIRD_HOURS}
        monthly=[]
        for month in MONTHS:
            qualified_by_bird=[sum(h.month==month for h in fix)
                               for fix in eligible.values()]
            n=sum(k>0 for k in qualified_by_bird)
            total=sum(qualified_by_bird)
            if n>=MIN_MONTH_BIRDS and total>=MIN_MONTH_HOURS:monthly.append(month)
        step_n=0;step_dates=set();source_flag=Counter()
        for bird,fixes in eligible.items():
            p=sorted(fixes.values(),key=lambda v:v[0])
            for first,last in zip(p,p[1:]):
                elapsed=(last[0]-first[0]).total_seconds()/3600
                if not MIN_STEP_HOURS<=elapsed<=MAX_STEP_HOURS:
                    source_flag['outside_predeclared_0p75_1p5_elapsed']+=1
                    continue
                distance=great_circle(first[1],first[2],last[1],last[2])
                if distance/elapsed>MAX_DISPLACEMENT_KMH:
                    source_flag['source_displacement_above150km_perhour']+=1
                    continue
                step_n+=1;step_dates.add(first[0].date())
        coastal_source_hours=sum(len(fixes) for fixes in eligible.values())
        passq=(len(eligible)>=MIN_TAXON_BIRDS and coastal_source_hours>=MIN_TAXON_HOURS
               and len(monthly)>=MIN_MONTHS)
        counts[tax]={
          'true_2020_original_birds_with_any_JulOct_coastal_hour':len(coastal),
          'true_2020_original_birds_with_ge20_coastal_hours':len(eligible),
          'native_original_2020_JulOct_coastal_bird_hours_in_eligible_tags':coastal_source_hours,
          'source_months_meeting_3_birds_150_hours':monthly,
          'source_original_consecutive_bird_hour_steps_0p75_to_1p5_h_in_40km':step_n,
          'source_distinct_original_calendar_dates_with_steps':len(step_dates),
          'source_steps_quality_flags':dict(source_flag),
          'fixed_bird_hour_source_admitted':passq,
          'fixed_step_source_gate_admitted':passq and step_n>=MIN_STEPS
                                        and len(step_dates)>=MIN_STEP_DATES,
          'NO_HABITAT_TIDE_SOLAR_RESPONSE_ESTIMATED':True}
    return {'original_native_all_2020_gzip_GPS_rows':native_rows,
       'original_native_2020_JulyOctober_rows':native_juloct_rows,
       'source_native_gps_columns':heads,
       'true_all_source_bird_hour_counts_by_taxon':dict(allnative),
       'coastal_source_fixed_40km_center_public':list(center),
       'source_months':list(MONTHS),
       'source_2020_by_actual_original_taxon':counts,
       'original_GPS_source_QA':dict(bad),
       'source_both_focal_species_admitted_IN_THIS_ONE_STUDY':all(
            counts[s]['fixed_bird_hour_source_admitted'] for s in FOCAL),
       'source_not_a_2020_animal_activity_or_tide_sun_result':True,
       'NO_2020_BIRD_ID_OR_COORDINATE_OR_TIMESTAMP_EXPORTED':True}

def run(panel,out):
    if panel not in PANELS:
        raise ValueError('SOURCE_STOP_NOT_FROZEN_2020_BELGIAN_STUDY')
    p=PANELS[panel]
    report={'analysis':'V125_ORIGINAL_2020_BELGIUM_THREE_PANELS_INDEPENDENT_GULL_GPS_SOURCE_ONLY',
        'panel':panel,'original_archive_record_id':p['record'],
        'source_year':YEAR,'original_months':list(MONTHS),
        'source_colony_center_public':list(p['colony']),
        'source_radius_km':RADIUS_KM,
        'source_2020_GPS_publisher_md5_frozen':p['md5'],
        'source_status':'PUBLISHER_SOURCE_UNAVAILABLE_OR_NOT_AUTHENTICATED',
        'NOT_A_NEW_GIC_OR_TIDE_OR_SOLAR_OR_FORAGING_RESULT':True}
    try:
        manifest,proof=native_catalog(panel)
        report['publisher_authentic_manifest']=proof
        refraw,refproof=checked_original_file(manifest[panel+'-reference-data.csv'])
        schema,schemaproof=checked_original_file(manifest['datapackage.json'])
        data=json.loads(schema)
        if not isinstance(data,dict) or not isinstance(data.get('resources'),list):
            raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_CORRECTED_MOVEBANK_DATAPACKAGE_INVALID')
        taxa,referenceproof=source_reference_taxa(refraw)
        report['original_reference_source_receipt']=refproof
        report['original_datapackage_source_receipt']=schemaproof
        report['original_reference_source_taxonomy_QA']=referenceproof
        gps,gpsproof=checked_original_file(manifest[p['gps']])
        report['original_2020_source_gps_receipt']=gpsproof
        report['native_source_2020_birds_hour_and_movement_QA']=parse_native_gps(gps,taxa,panel)
        report['source_status']='ORIGINAL_2020_BELGIAN_GULL_ANNUAL_BIRD_SOURCE_AUTHENTICATED'
    except (OriginalSourceStop,ValueError,UnicodeDecodeError,OSError) as e:
        report['source_status']='SOURCE_STOP_NOT_A_BIOLOGICAL_NULL'
        report['source_failure_type']=type(e).__name__
        report['source_failure']=str(e)[:220]
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    source=report.get('native_source_2020_birds_hour_and_movement_QA') or {}
    print('V125_TRUE_INDEPENDENT_BELGIUM_2020_GULL_SOURCE_ONLY '+json.dumps({
        'panel':panel,'status':report['source_status'],
        'native_JulOct_2020_rows':source.get('original_native_2020_JulyOctober_rows'),
        'true_species_source':source.get('source_2020_by_actual_original_taxon'),
        'both_species_in_same_study_source_admitted':
            source.get('source_both_focal_species_admitted_IN_THIS_ONE_STUDY'),
        'source_failure':report.get('source_failure'),
        'NO_NEW_ECOLOGICAL_EFFECT':True},sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--panel',required=True,choices=sorted(PANELS))
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.panel,a.output)
