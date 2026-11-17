#!/usr/bin/env python3
"""Admit/STOP the original independent buffalo GPS/landscape source (no ecological response fit).

Forrest et al. (Ecography 2025), Zenodo 13749246. No raw GPS or sensitive
coordinates exported. Exact provider-MD5 checked buffalo.csv is downloaded,
only its header, row count, source animal-ID cardinality, timestamp grammar,
and spatial-file list are emitted. Header and source metadata first; never
assume IDs or coordinate references without inspection.
"""
from __future__ import annotations
import csv, hashlib, json, os, tempfile, urllib.request, sys
from pathlib import Path
from urllib.parse import urlsplit
RECORD=13749246
API=f'https://zenodo.org/api/records/{RECORD}'
MAX_BYTES=30_000_000
FILENAME='buffalo.csv'

def get_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'ecostate-v11-source/1.0', 'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=45) as r:
        b=r.read(2_500_000)
    return json.loads(b)

def fetch_exact(url,out):
    u=urlsplit(url)
    if u.scheme!='https' or u.netloc not in ('zenodo.org','www.zenodo.org'):
        raise ValueError('SOURCE_STOP_BAD_SOURCE_URL')
    req=urllib.request.Request(url,headers={'User-Agent':'ecostate-v11-source/1.0'})
    size=0; m=hashlib.md5(); s=hashlib.sha256()
    with urllib.request.urlopen(req,timeout=75) as r, open(out,'wb') as f:
        while True:
            b=r.read(1<<20)
            if not b:break
            size+=len(b)
            if size>MAX_BYTES:raise ValueError('SOURCE_STOP_FILE_TOO_LARGE')
            m.update(b);s.update(b);f.write(b)
    return size,m.hexdigest(),s.hexdigest()

def run(out):
    v={'schema':'ecostate.v11.independent_buffalo_source_admission',
       'publication_doi':'10.1111/ecog.07421','source_record_id':RECORD,
       'status':'SOURCE_STOP','animal_habitat_effects_computed':False,
       'original_coordinates_exported':False}
    try:
        j=get_json(API)
        files=j.get('files',[])
        v['source_file_inventory']=[{'name':x.get('key'), 'size':x.get('size'),
             'checksum':x.get('checksum')} for x in files if any(w in str(x.get('key','')).lower() for w in ['buffalo','ndvi','canopy','slope','veg_herb'])]
        matches=[x for x in files if x.get('key')==FILENAME]
        if len(matches)!=1:raise ValueError('SOURCE_STOP_BUFFALO_CSV_NOT_UNIQUE')
        x=matches[0]
        checksum=str(x.get('checksum','')).lower()
        if not checksum.startswith('md5:'):raise ValueError('SOURCE_STOP_NO_PROVIDER_MD5')
        url=x.get('links',{}).get('content') or x.get('links',{}).get('self')
        if not url:raise ValueError('SOURCE_STOP_NO_PROVIDER_CONTENT')
        if int(x.get('size',0))>MAX_BYTES:raise ValueError('SOURCE_STOP_BUFFALO_CSV_SIZE')
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'buffalo.csv'
            n,md,sha=fetch_exact(url,path)
            if n!=x['size'] or md!=checksum[4:]:raise ValueError('SOURCE_STOP_CHECKSUM_MISMATCH')
            with path.open('r',newline='',encoding='utf-8-sig') as f:
                rd=csv.reader(f)
                header=next(rd,None)
                if not header:raise ValueError('SOURCE_STOP_NO_HEADER')
                # No location, ID or behavioural row values are printed or exported.
                rowcount=sum(1 for _ in rd)
            v.update({'status':'SOURCE_CHECKSUM_AND_HEADER_ADMITTED','file_name':FILENAME,
              'original_file_bytes':n,'original_md5':md,'original_sha256':sha,
              'source_rows':rowcount,'header':header})
    except Exception as e:
        v['reason']=str(e)[:1200]
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
    print('V11_BUFFALO_SOURCE',v['status'], 'rows', v.get('source_rows'),
          'columns', v.get('header'), 'reason',v.get('reason'))
    assert not v['animal_habitat_effects_computed'] and not v['original_coordinates_exported']
    return v
if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v11/results/buffalo_source.json')
