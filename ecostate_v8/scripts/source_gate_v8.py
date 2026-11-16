"""Source-only inspection of independent ecological-state tracking candidates.

Never open response data or animal identities here. Fail closed on unavailable
source and save auditable provider/source metadata. Standard library only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BULBUL_DOI = '10.5061/dryad.wwpzgmsxg'
BULBUL_ARCHIVE = 'Field_Margins_Bulbul.zip'
USGS_ITEM = '62ffeecfd34ed6dc55925915'


def safe_get_json(url: str, limit: int = 5_000_000) -> tuple[dict | None, dict]:
    meta = {'host': urllib.parse.urlsplit(url).hostname, 'status': None,
            'response_sha256': None, 'error_type': None, 'error_code': None}
    try:
        request = urllib.request.Request(url, headers={
            'User-Agent': 'ecostate-source-only/8 (research, public metadata)',
            'Accept': 'application/json'})
        with urllib.request.urlopen(request, timeout=35) as response:
            data = response.read(limit + 1)
            meta['status'] = response.status
        if len(data) > limit:
            meta['error_type'] = 'SIZE_LIMIT'; return None, meta
        meta['response_sha256'] = hashlib.sha256(data).hexdigest()
        obj = json.loads(data.decode('utf-8'))
        if not isinstance(obj, dict):
            meta['error_type'] = 'NON_OBJECT'; return None, meta
        return obj, meta
    except urllib.error.HTTPError as e:
        meta.update({'status': e.code, 'error_type': 'HTTP_ERROR', 'error_code': e.code})
    except urllib.error.URLError:
        meta.update({'error_type': 'TRANSPORT_ERROR'})
    except (ValueError, UnicodeError, json.JSONDecodeError):
        meta.update({'error_type': 'NOT_VALID_JSON'})
    return None, meta


def file_summaries(items):
    out = []
    for x in items:
        if not isinstance(x, dict): continue
        name = x.get('filename') or x.get('name') or x.get('key') or ''
        out.append({'name': str(name), 'size': x.get('size') or x.get('sizeBytes'),
                    'checksum': x.get('digest') or x.get('checksum'),
                    'file_id': x.get('id'),
                    'has_download_link': isinstance(x.get('_links') or x.get('links'), dict)})
    return out


def dryad_gate() -> dict:
    enc = urllib.parse.quote('doi:' + BULBUL_DOI, safe='')
    base = f'https://datadryad.org/api/v2/datasets/{enc}'
    doc = {'source': 'Dryad', 'doi': BULBUL_DOI,
           'source_page': f'https://datadryad.org/dataset/doi:{BULBUL_DOI}',
           'reference_n_tracked_from_readme': 68,
           'reference_n_translocated_from_readme': 64,
           'expected_archive': BULBUL_ARCHIVE,
           'raw_animal_observations_read': False,
           'any_biological_effect_estimated': False,
           'status': 'SOURCE_STOP'}
    obj, m = safe_get_json(base)
    doc['dataset_attempt'] = m
    if obj is None:
        doc['reason'] = 'OFFICIAL_DRYAD_API_METADATA_UNAVAILABLE'
        return doc
    doc['dataset_metadata_fields'] = sorted(obj.keys())
    doc['dataset_metadata_sha256'] = m['response_sha256']
    for k in ('id','identifier','doi','publicationDate','versionNumber'):
        if k in obj and isinstance(obj[k],(str,int,float)):
            doc[k] = obj[k]
    # The official API exposes current version URLs; no numeric files are read.
    links = obj.get('_links') or obj.get('links') or {}
    versions = []
    if isinstance(links, dict):
        for key, val in links.items():
            if 'version' in str(key).lower():
                vv = val if isinstance(val,list) else [val]
                for item in vv:
                    if isinstance(item,dict) and item.get('href'):
                        versions.append(item['href'])
    versions.append(base + '/versions')
    seen = set()
    for u in versions:
        if u in seen: continue
        seen.add(u)
        if urllib.parse.urlsplit(u).hostname != 'datadryad.org': continue
        vo, vm = safe_get_json(u)
        doc.setdefault('version_attempts', []).append(vm)
        if vo is None: continue
        doc['version_metadata_fields'] = sorted(vo.keys())
        if isinstance(vo.get('files'), list):
            doc['files'] = file_summaries(vo['files'])
        for x in ((vo.get('_embedded') or {}).values() if isinstance(vo.get('_embedded'),dict) else []):
            if isinstance(x,list):
                for row in x:
                    if not isinstance(row,dict): continue
                    ver_id=row.get('id')
                    if not isinstance(ver_id,int):continue
                    fo, fm = safe_get_json(f'https://datadryad.org/api/v2/versions/{ver_id}/files')
                    doc.setdefault('file_list_attempts', []).append(fm)
                    if fo is None:continue
                    embedded=fo.get('_embedded') or {}
                    cand=[]
                    for k,v in embedded.items():
                        if isinstance(v,list) and 'file' in k.lower(): cand+=v
                    if isinstance(fo.get('files'),list):cand+=fo['files']
                    if cand: doc['files']=file_summaries(cand)
            
        if doc.get('files'):break
    if doc.get('files'):
        match = [x for x in doc['files'] if x['name'] == BULBUL_ARCHIVE]
        doc['status'] = ('SOURCE_FILE_METADATA_ONLY' if len(match)==1 else 'SOURCE_STOP')
        if len(match)!=1:doc['reason']='ARCHIVE_NOT_UNIQUELY_IDENTIFIED'
    else:
        doc['status'] = 'SOURCE_METADATA_ONLY_NO_FILE_LIST'
        doc['reason'] = 'NO_AUTHORITATIVE_ORIGINAL_FILE_ID'
    return doc


def usgs_gate() -> dict:
    url=f'https://www.sciencebase.gov/catalog/item/{USGS_ITEM}?format=json'
    doc={'source':'USGS','item':USGS_ITEM,'doi':'10.5066/P9XBZKZ8',
         'source_page':'https://doi.org/10.5066/P9XBZKZ8',
         'note':'Overlaps possible with existing California studies; NOT an independent replication until ID cohort crosswalk',
         'raw_animal_observations_read':False,'any_biological_effect_estimated':False,
         'status':'SOURCE_STOP'}
    obj,m=safe_get_json(url)
    doc['source_attempt']=m
    if obj is None:
        doc['reason']='ORIGINAL_SCIENCEBASE_METADATA_UNAVAILABLE';return doc
    doc['source_metadata_sha256']=m['response_sha256']
    doc['file_count']=len(obj.get('files',[])) if isinstance(obj.get('files'),list) else None
    doc['files']=file_summaries(obj.get('files',[]))
    doc['status']='SOURCE_METADATA_ONLY'
    return doc


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    a=p.parse_args()
    output={'schema':'ecostate.v8.no_outcome_source_gate',
            'design':'both candidates only, NO animal observations or effect sizes',
            'bulbul':dryad_gate(),'usgs_waterfowl':usgs_gate()}
    assert not any(output[k]['any_biological_effect_estimated'] or output[k]['raw_animal_observations_read'] for k in ('bulbul','usgs_waterfowl'))
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('ECOSTATE_V8_SOURCE_ONLY',output['bulbul']['status'],output['usgs_waterfowl']['status'])
    print('SOURCE_RECEIPT',path)

if __name__=='__main__':main()
