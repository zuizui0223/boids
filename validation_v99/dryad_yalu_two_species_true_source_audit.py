"""v99 original-source admission for *independent* 2025 Yalu Jiang Estuary two-taxon shorebird data.

This is a NEW field dataset outside the 2010 Wadden oyster-catcher cohort,
NOT a proof of tide×daylight animal effects. Do not calculate behavioral
effects unless genuine original published files, independent bird IDs, precise
local timestamps, tide/light cells and source sampling design are admitted.
Source URLs are official publisher Dryad REST, no TinyFish or secondary scrapes.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import argparse,csv,io,json
ROOT='https://datadryad.org'
DOI='10.5061/dryad.h70rxwdwf'
DATASET='/api/v2/datasets/doi%3A10.5061%2Fdryad.h70rxwdwf'
NAMES={'movement_data_bar-tailed_godwit.csv','movement_data_great_knot.csv'}
MAX_DOWNLOAD=5_000_000
FIELDS={'f_time','f_lon','f_lat','f_tide','r_time','r_lon','r_lat','r_tide',
        'highesttide','Dawn','Dusk','r_Light','dist','predist_f'}
def get(url,download_limit=3_000_000):
    if not url.startswith(ROOT+'/api/v2/'):
        raise ValueError('STOP_NOT_ORIGINAL_DRYAD_API_PATH')
    req=Request(url,headers={'Accept':'application/json, text/csv, application/octet-stream',
       'User-Agent':'boids-v99-independent-Yalu-two-shorebird-publisher-source/1.0'})
    with urlopen(req,timeout=35) as handle:
        buf=handle.read(download_limit+1)
        if len(buf)>download_limit:raise ValueError('STOP_SOURCE_TOO_LARGE')
        return buf
def source_link(root,entity,key):
    links=entity.get('_links') or {}
    href=(links.get(key) or {}).get('href')
    if not href:raise ValueError('STOP_DRYAD_OFFICIAL_LINK_NOT_AVAILABLE_'+key)
    out=urljoin(root,href)
    if not out.startswith(ROOT+'/api/v2/'):
        raise ValueError('STOP_DRYAD_OFFICIAL_LINK_NON_API')
    return out
def _get_version_from_dataset(doc):
    links=doc.get('_links') or {}
    href=((links.get('stash:version') or {}).get('href'))
    if href:return urljoin(ROOT,href)
    return ROOT+DATASET+'/versions'
def original_filename_items(data):
    emb=data.get('_embedded',{})
    files=None
    for k,val in emb.items():
        if isinstance(val,list) and any(isinstance(v,dict) and ('path' in v or 'filename' in v) for v in val):
            files=val;break
    if files is None and isinstance(data.get('files'),list):files=data['files']
    return files or []
def _contents_inventory(raw,name):
    sample=raw.decode('utf-8-sig',errors='strict')
    reader=csv.DictReader(io.StringIO(sample))
    headers=reader.fieldnames or []
    norm={h.strip().lower().replace(' ','_'):h for h in headers}
    must={f.lower() for f in FIELDS}
    if not must<=set(norm):
        return {'state':'SOURCE_SCHEMA_INCOMPLETE_NOT_ADMITTED','missing_published_columns':
                sorted(must-set(norm)),'row_count_UNSCORED':sum(1 for _ in reader),
                'source_headers_original':headers}
    counts=Counter()
    ids=Counter()
    possible=[x for x in norm if x in
        {'id','bird_id','birdid','tag_id','individual_id','animal_id','animalid','ptt','ring','track_id','trackid'}]
    rows=0
    for v in reader:
        rows+=1
        counts['roost_light_'+str(v[norm['r_light']]).strip().lower()]+=1
        counts['foraging_tidal_annotation_'+str(v[norm['f_tide']]).strip().lower()]+=1
        counts['roost_tidal_annotation_'+str(v[norm['r_tide']]).strip().lower()]+=1
        if possible:
            ids[str(v[norm[possible[0]]])]+=1
    return {'state':'PUBLISHED_COLUMNS_SCHEMA_PRESENT_NOT_YET_BIOLOGICAL_OUTCOME',
       'source_headers_original':headers,'row_count_events_NOT_INDEPENDENT_BIRDS':rows,
       'candidate_explicit_bird_id_columns':possible,
       'source_independent_id_count_if_present':len(ids) if possible else None,
       'original_source_categorical_support':dict(counts),
       'author_timezone_and_clock_calibration_NOT_VERIFIED':True,
       'sampling_effort_NOT_VERIFIED':True,
       'NO_BEHAVIORAL_EFFECT_ESTIMATED':True}
def run(outpath):
    result={'analysis':'V99_INDEPENDENT_ORIGINAL_YALU_JIANG_TWO_SHOREBIRD_DRYAD_SOURCE_GATE',
       'source_doi':DOI,'publisher':'Dryad','source_mode':'original_published_metadata_then_original_csv_only',
       'species':['Calidris tenuirostris','Limosa lapponica'],
       'external_to_original_Wadden_C_h_ostralegus':True,
       'source_state':'SOURCE_UNAVAILABLE_NO_BIOLOGICAL_EFFECT'}
    try:
        raw=get(ROOT+DATASET)
        data=json.loads(raw)
        if not (str(data.get('identifier','')).lower()=='doi:'+DOI or str(data.get('identifier','')).lower()==DOI):
            raise ValueError('STOP_DRYAD_WRONG_ORIGINAL_DOI')
        result['metadata_sha256']=sha256(raw).hexdigest()
        result['publisher_title']=data.get('title')
        result['publisher_status']=data.get('versionStatus')
        version_url=_get_version_from_dataset(data)
        if not version_url.startswith(ROOT+'/api/v2/'):raise ValueError('STOP_WRONG_VERSION_SOURCE')
        # Resolve either one version or version-list API, without choosing observed outcomes
        version_json=json.loads(get(version_url))
        if '/versions' in version_url and '/versions/' not in version_url:
            versions=(version_json.get('_embedded') or {}).get('stash:versions',[])
            if not versions:raise ValueError('STOP_NO_PUBLIC_DRYAD_DATASET_VERSION')
            versions.sort(key=lambda o:o.get('versionNumber',0))
            version_url=source_link(ROOT,versions[-1],'self')
            version_json=json.loads(get(version_url))
        file_url=source_link(ROOT,version_json,'stash:files')
        info=json.loads(get(file_url))
        files=original_filename_items(info)
        meta=[]
        for item in files:
            name=str(item.get('path') or item.get('filename') or '')
            meta.append({'original_name':name,'size_bytes':item.get('size'),
                         'publisher_file_id':item.get('id'),
                         'digest_original':item.get('digest')})
        result['original_file_metadata']=meta
        source={}
        matched=[f for f in files if str(f.get('path') or f.get('filename','')).lower() in NAMES]
        if len(matched)!=2:
            raise ValueError('STOP_ORIGINAL_TWO_SPECIES_FILES_NOT_IDENTIFIED')
        for item in matched:
            name=str(item.get('path') or item.get('filename'))
            fid=int(item['id'])
            raw=get(ROOT+f'/api/v2/files/{fid}/download',download_limit=MAX_DOWNLOAD)
            report=_contents_inventory(raw,name)
            source[name]={'original_file_sha256':sha256(raw).hexdigest(),
                          'source_bytes':len(raw),'schema_admission':report}
            print('V99_ORIGINAL_SPECIES_SOURCE '+json.dumps({'file':name,
                    'source_bytes':len(raw),'source_status':report['state'],
                    'rows':report.get('row_count_events_NOT_INDEPENDENT_BIRDS'),
                    'explicit_bird_ids':report.get('source_independent_id_count_if_present')},sort_keys=True),flush=True)
        result['original_csv_source']=source
        result['source_state']='SOURCE_CSV_ADMITTED_PENDING_INDEPENDENCE_AND_4CELL_GATE'
    except (HTTPError,URLError,ValueError,KeyError,TimeoutError,UnicodeDecodeError) as e:
        result['source_state']='SOURCE_STOP_AUTH_OR_SCHEMA_OR_TRANSPORT'
        result['failure_type']=type(e).__name__
        result['failure_message']=str(e)[:220]
    Path(outpath).parent.mkdir(parents=True,exist_ok=True)
    Path(outpath).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('V99_SOURCE_GATE_FINAL '+json.dumps({'source_state':result['source_state'],
           'reason':result.get('failure_message'),'files':list((result.get('original_csv_source') or {}).keys()),
           'NO_NEW_BIOLOGICAL_EFFECT_ESTIMATED':True},sort_keys=True),flush=True)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
