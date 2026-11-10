"""v109 original INBO DELTATRACK gull GPS 2020 independent species SOURCE-ONLY gate.

ONE exact corrected publisher Zenodo record (22102508); no later study-wide
99 cumulative birds can be counted as annual birds; no tidal/solar effect yet.
Do not export bird tag IDs, actual GPS points or precise native times.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,os
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

PUBLISHER_RECORD=22102508
SOURCE_API=f'https://zenodo.org/api/records/{PUBLISHER_RECORD}'
GPS_FILE='DELTATRACK-gps-2020.csv.gz'
GPS_EXPECTED_MD5='730549beb8079213ac893d3bf126c2bf'
REFERENCE_FILE='DELTATRACK-reference-data.csv'
SCHEMA_FILE='datapackage.json'
FOCAL={'Larus argentatus','Larus fuscus'}
YEAR=2020
ZONE=(50.90,52.20,2.50,4.80)
EXPECTED_TAGGED_CUMULATIVE=99
MIN_YEAR_BIRDS_TAXON=8
MIN_YEAR_BIRD_HOURS=2000
MIN_MONTH_BIRDS=5
MIN_MONTH_HOURS=200
MIN_MONTHS=3
MIN_BIRD_REGION_HOURS=20
MAX_FILE_BYTES=95_000_000
MAX_META=1_000_000

class SourceNotAdmitted(Exception):pass

def get_zenodo(url,limit=MAX_FILE_BYTES):
    if not isinstance(url,str) or not url.startswith('https://zenodo.org/'):
        raise SourceNotAdmitted('STOP_NOT_AUTHENTIC_ZENODO_PUBLISHER_SOURCE')
    request=Request(url,headers={
        'User-Agent':'boids-v109-genuine-DELTATRACK-2020-gull-two-species-source-first/1.0',
        'Accept':'application/json,application/gzip,text/csv,*/*'})
    try:
        with urlopen(request,timeout=95) as resp:
            raw=resp.read(limit+1)
            if len(raw)>limit:raise SourceNotAdmitted('STOP_SOURCE_BYTES_TOO_LARGE')
            if urlparse(resp.geturl()).scheme!='https':
                raise SourceNotAdmitted('STOP_INSECURE_PUBLISHER_REDIRECT')
            return raw
    except (HTTPError,URLError,TimeoutError) as e:
        raise SourceNotAdmitted('SOURCE_UNAVAILABLE_ZENODO_PUBLISHER_'+str(e)[:170]) from e

def original_manifest():
    raw=get_zenodo(SOURCE_API,MAX_META)
    try:obj=json.loads(raw)
    except ValueError as e:raise SourceNotAdmitted('STOP_ORIGINAL_ZENODO_INVALID_JSON') from e
    if str(obj.get('id'))!=str(PUBLISHER_RECORD):
        raise SourceNotAdmitted('STOP_WRONG_ORIGINAL_PUBLISHER_VERSION')
    files={}
    for f in obj.get('files') or []:
        key=f.get('key')
        if key not in {GPS_FILE,REFERENCE_FILE,SCHEMA_FILE}:continue
        checksum=f.get('checksum','')
        if checksum.startswith('md5:'):checksum=checksum[4:]
        url=(f.get('links') or {}).get('self') or (f.get('links') or {}).get('content')
        size=f.get('size')
        if not isinstance(url,str) or not url.startswith('https://zenodo.org/') or (
           not isinstance(size,int) or size<=0 or size>MAX_FILE_BYTES):
            raise SourceNotAdmitted('STOP_PUBLISHER_FILE_ID_LINK_OR_SIZE_BAD')
        if not (isinstance(checksum,str) and len(checksum)==32):
            raise SourceNotAdmitted('STOP_PUBLISHER_ORIGINAL_MD5_NOT_PRESENT')
        if key in files:raise SourceNotAdmitted('STOP_DUPLICATE_ORIGINAL_ZENODO_FILE')
        files[key]={'name':key,'url':url,'publisher_md5':checksum,'publisher_size_bytes':size}
    if set(files)!={GPS_FILE,REFERENCE_FILE,SCHEMA_FILE}:
        raise SourceNotAdmitted('STOP_CORRECTED_ORIGINAL_VERSION_FILE_MANIFEST_INCOMPLETE')
    if files[GPS_FILE]['publisher_md5']!=GPS_EXPECTED_MD5:
        raise SourceNotAdmitted('STOP_CORRECTED_2020_NATIVE_GPS_FILE_MD5_DRIFT')
    return files,{'original_Zenodo_api_record_id':PUBLISHER_RECORD,
       'original_Zenodo_metadata_SHA256':hashlib.sha256(raw).hexdigest(),
       'original_published_title':obj.get('metadata',{}).get('title'),
       'publication_date':obj.get('metadata',{}).get('publication_date'),
       'native_original_three_files':[
          {'name':k,'bytes':v['publisher_size_bytes'],'MD5':v['publisher_md5']}
          for k,v in sorted(files.items())],
       'known_older_wrong_datapackage_record_22102036_EXCLUDED':True}

def genuine_file(meta):
    raw=get_zenodo(meta['url'])
    if len(raw)!=meta['publisher_size_bytes'] or hashlib.md5(raw).hexdigest()!=meta['publisher_md5']:
        raise SourceNotAdmitted('STOP_PUBLISHER_MD5_SIZE_DOES_NOT_MATCH_ORIGINAL')
    return raw,{'pub_file_name':meta['name'],
       'provider_MD5_verified':True,'raw_bytes':len(raw),
       'local_SHA256':hashlib.sha256(raw).hexdigest()}

def _get_native_taxon(row):
    for col in ('individual-taxon-canonical-name','taxon-canonical-name','scientific-name',
                'individual-taxon-name'):
        p=str(row.get(col) or '').strip()
        if p:return p
    return None

def native_reference_taxa(raw):
    stream=io.StringIO(raw.decode('utf-8-sig'))
    reader=csv.DictReader(stream)
    heads=reader.fieldnames or []
    ref=defaultdict(set)
    ids=('individual-local-identifier','individual-id','animal-id')
    for row in reader:
        bird=next((str(row.get(k) or '').strip() for k in ids if str(row.get(k) or '').strip()),'')
        taxa=_get_native_taxon(row)
        if bird and taxa:ref[bird].add(taxa)
    return {k:next(iter(v)) for k,v in ref.items() if len(v)==1},heads

def native_2020_original_annual_gps_source(raw,reference):
    try:stream=io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(raw)),encoding='utf-8-sig')
    except (ValueError,OSError) as e:raise SourceNotAdmitted('STOP_NATIVE_2020_GPS_NOT_GZIP') from e
    reader=csv.DictReader(stream)
    heads=reader.fieldnames or []
    required={'timestamp','location-lat','location-long','individual-local-identifier'}
    if not required<=set(heads):
        raise SourceNotAdmitted('STOP_NATIVE_2020_MOVEBANK_STANDARD_COLUMNS_MISSING')
    native_raw_n=0
    per_bird=defaultdict(dict)
    native_taxon=defaultdict(set)
    bad=Counter()
    for row in reader:
        native_raw_n+=1
        bird=str(row.get('individual-local-identifier') or '').strip()
        if not bird:
            bad['original_missing_bird_identifier']+=1;continue
        if str(row.get('visible','')).strip().upper() in ('FALSE','0'):
            bad['original_invisible_GPS']+=1;continue
        t=str(row.get('timestamp') or '').strip()
        try:
            # Movebank native timestamp usually UTC without offset.
            dt=datetime.fromisoformat(t.replace('Z','+00:00'))
            if dt.tzinfo is not None:
                dt=dt.astimezone(timezone.utc).replace(tzinfo=None)
            la,lo=float(row['location-lat']),float(row['location-long'])
        except (ValueError,TypeError):
            bad['original_timestamp_or_WGS84_parse_failed']+=1;continue
        if dt.year!=YEAR or not (math.isfinite(la) and math.isfinite(lo) and -90<=la<=90 and -180<=lo<=180):
            bad['original_year_or_valid_coordinates_failed']+=1;continue
        taxon=_get_native_taxon(row) or reference.get(bird)
        if taxon:native_taxon[bird].add(taxon)
        hour=dt.replace(minute=0,second=0,microsecond=0)
        old=per_bird[bird].get(hour)
        if old is None or dt<old[0]:
            per_bird[bird][hour]=(dt,la,lo)
    results={}
    for bird,hours in per_bird.items():
        taxa=native_taxon.get(bird) or set()
        if len(taxa)!=1:taxon='UNKNOWN_OR_AMBIGUOUS_ORIGINAL_TAXON'
        else:taxon=next(iter(taxa))
        for _,lat,lon in hours.values():
            if ZONE[0]<=lat<=ZONE[1] and ZONE[2]<=lon<=ZONE[3]:
                info=results.setdefault(taxon,{}).setdefault(bird,
                        {'hours':0,'monthly':Counter()})
                info['hours']+=1;info['monthly'][_.month]+=1
    summary={}
    for taxon,birds in sorted(results.items()):
        source_eligible={key:z for key,z in birds.items() if z['hours']>=MIN_BIRD_REGION_HOURS}
        months=[]
        for m in range(1,13):
            by_month=[z['monthly'].get(m,0) for z in source_eligible.values()]
            nbirds=sum(n>=20 for n in by_month)
            hours=sum(n for n in by_month if n>=20)
            if nbirds>=MIN_MONTH_BIRDS and hours>=MIN_MONTH_HOURS:months.append(m)
        count=sum(z['hours'] for z in source_eligible.values())
        status='CANDIDATE_NATIVE_GPS_YEAR_SOURCE_FOR_INDEPENDENT_TWO_SPECIES_TIDE_SOLAR' if (
            taxon in FOCAL and len(source_eligible)>=MIN_YEAR_BIRDS_TAXON
            and len(months)>=MIN_MONTHS and count>=MIN_YEAR_BIRD_HOURS) else 'NOT_ADMITTED_OR_NOT_FOCAL'
        summary[taxon]={
            'original_2020_source_individuals_with_any_2020_coastal_hours':len(birds),
            'native_tagged_birds_with_20plus_hourly_fix_in_coastal_box':len(source_eligible),
            'native_bird_hourly_fixes_coastal_box_after_source_eligibility':count,
            'source_months_with_5plus_birds_200plus_hours':months,
            'native_2020_source_adequacy':status}
    return {'original_2020_native_raw_GPS_rows':native_raw_n,
       'original_2020_distinct_birds_with_any_valid_yearly_gps':len(per_bird),
       'original_2020_native_valid_unique_bird_hour_GPS_fixes_anywhere':
             sum(len(h) for h in per_bird.values()),
       'native_source_headers':heads,
       'native_excluded_counts':dict(bad),
       'native_source_2020_source_region':list(ZONE),
       'distinct_native_bird_taxa_in_source_region':summary,
       'both_focal_taxa_pass_independent_original_source_gates':
            all(summary.get(s,{}).get('native_2020_source_adequacy','').startswith('CANDIDATE_') for s in FOCAL),
       'UNKNOWN_GPS_UTC_clock_hardware_0_second_offset_not_certified':True,
       'source_only_NO_2020_RWS_tide_solar_activity_or_foraging_scored':True,
       'no_native_bird_ids_or_precise_GPS_or_events_exported':True}

def run(output):
    report={'analysis':'V109_ORIGINAL_CORRECTED_2020_DELTATRACK_GULLS_TWO_SPECIES_ZENODO_SOURCE_ONLY',
        'corrected_original_Zenodo_record':PUBLISHER_RECORD,
        '2020_preselected_original_GPS_MD5':GPS_EXPECTED_MD5,
        '2020_annual_source_site_scope':list(ZONE),
        'not_animal_tide_or_solar_effect':True}
    try:
        files,origin=original_manifest()
        report['publisher_source_manifest']=origin
        reference_raw,reference_receipt=genuine_file(files[REFERENCE_FILE])
        schema_raw,schema_receipt=genuine_file(files[SCHEMA_FILE])
        schema=json.loads(schema_raw)
        if not isinstance(schema,dict) or not schema.get('resources'):
            raise SourceNotAdmitted('STOP_ORIGINAL_CORRECTED_FRICITIONLESS_SCHEMA_INVALID')
        names=[str(z.get('name') or '') for z in schema['resources']]
        report['original_reference_species_file_receipt']=reference_receipt
        report['original_corrected_datapackage_file_receipt']=schema_receipt
        report['original_datapackage_resources']=names[:35]
        reference,refheads=native_reference_taxa(reference_raw)
        report['original_reference_table_source_columns']=refheads
        report['original_reference_individuals_with_resolved_taxon_count']=len(reference)
        gps,receipt=genuine_file(files[GPS_FILE])
        report['original_2020_gps_file_source_proof']=receipt
        native=native_2020_original_annual_gps_source(gps,reference)
        report['2020_original_annual_native_gps_source_census']=native
        report['source_status']='ADMITTED_2020_TRUE_GULL_ORIGINAL_GPS_SOURCE_ONLY'
    except (SourceNotAdmitted,UnicodeDecodeError,json.JSONDecodeError,OSError) as e:
        report['source_status']='SOURCE_STOP_ZENODO_NATIVE_GULL_2020'
        report['source_blocker']=str(e)[:280]
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    native=report.get('2020_original_annual_native_gps_source_census') or {}
    print('V109_GENUINE_2020_TWO_GULL_TAXA_GPS_SOURCE '+json.dumps({
        'status':report['source_status'],'blocker':report.get('source_blocker'),
        'original_2020_raw_GPS_rows':native.get('original_2020_native_raw_GPS_rows'),
        'original_genuine_2020_GPS_birds':native.get('original_2020_distinct_birds_with_any_valid_yearly_gps'),
        '2020_original_gull_species_source_counts':native.get('distinct_native_bird_taxa_in_source_region'),
        'two_species_SOURCE_GATE_not_an_ecology_result':native.get('both_focal_taxa_pass_independent_original_source_gates'),
        'no_biological_tide_solar_effect_estimated':True},sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
