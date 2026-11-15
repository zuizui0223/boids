"""Outcome-blind original Zenodo xlsx retrieval for site-level community test.
Source: Secondi et al 2026, 10.5281/zenodo.18161913, CC BY 4.0.
"""
from __future__ import annotations
import hashlib, json, sys, urllib.request
from pathlib import Path
from urllib.parse import urlsplit

RECORD='18161913'
API=f'https://zenodo.org/api/records/{RECORD}'
EXPECTED_MD5='a08325ee4e24acfc159b1cd7c1fe425d'
EXPECTED_NAME='Dataset Secondi et al.Water bird diversity in a coastal wetland.xlsx'
LIMIT=5_000_000

def checked_url(url):
    p=urlsplit(url)
    if p.scheme!='https' or p.hostname not in {'zenodo.org','www.zenodo.org'}:
        raise ValueError('SOURCE_STOP: unrecognized original Zenodo host')
    return url

def get(url, limit):
    checked_url(url)
    request=urllib.request.Request(url,headers={'User-Agent':'ecostate-zenodo-preflight/3.0',
                                              'Accept':'application/json,application/octet-stream'})
    with urllib.request.urlopen(request,timeout=40) as resp:
        if int(resp.headers.get('Content-Length','0'))>limit:
            raise ValueError('SOURCE_STOP: source larger than byte bound')
        b=resp.read(limit+1)
    if len(b)>limit:raise ValueError('SOURCE_STOP: source exceeds byte bound')
    return b

def run(out_dir):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    result={'source_doi':'10.5281/zenodo.18161913','status':'SOURCE_STOP',
            'original_outcomes_opened':False,'original_expected_md5':EXPECTED_MD5}
    try:
        record=json.loads(get(API,1_500_000))
        items=record.get('files',[])
        selected=[x for x in items if x.get('key')==EXPECTED_NAME or x.get('filename')==EXPECTED_NAME]
        if len(selected)!=1:raise ValueError('SOURCE_STOP: original named workbook not unique')
        f=selected[0]
        link=f.get('links',{}).get('self') or f.get('links',{}).get('content')
        if not link:raise ValueError('SOURCE_STOP: original source URL absent')
        if not str(f.get('checksum','')).lower().endswith(EXPECTED_MD5):
            raise ValueError('SOURCE_STOP: provider MD5 mismatch in API declaration')
        b=get(link,LIMIT)
        md5=hashlib.md5(b).hexdigest()
        if md5!=EXPECTED_MD5:raise ValueError('SOURCE_STOP: original bytes MD5 mismatch')
        if b[:2]!=b'PK':raise ValueError('SOURCE_STOP: not a valid xlsx ZIP')
        file=out/'original_marais_breton_zenodo_18161913.xlsx';file.write_bytes(b)
        result.update(status='SOURCE_ONLY_ADMITTED',file_name=EXPECTED_NAME,source_bytes=len(b),
              original_md5=md5,original_sha256=hashlib.sha256(b).hexdigest(),
              source_download_host=urlsplit(link).hostname,original_workbook_local=str(file))
    except Exception as e:
        result.update(status='SOURCE_STOP',reason=str(e))
    (out/'zenodo_marais_source_gate_v3.json').write_text(json.dumps(result,indent=2)+'\n')
    print('MARAIS_ZENODO_SOURCE_GATE',result['status'],result.get('reason',''))
    return result

if __name__=='__main__':
    run(sys.argv[1] if len(sys.argv)>1 else 'comparative_state/results/zenodo_marais_source_v3')
