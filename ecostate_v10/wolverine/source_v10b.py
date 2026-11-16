"""One-shot original Zenodo Wolverine 2017 workbook header+checksum, no animal rows read."""
from __future__ import annotations
import hashlib,json,sys,tempfile,urllib.request,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
BASE='https://zenodo.org'
REC='5011732'
FILENAME='GPS_traffic_data_wolverine_revised.xlsx'
SOURCE_MD5='6d694faeadde68fbce1c0b45632aa21c'
MAXBYTES=90_000_000
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

def download(url,p):
    from urllib.parse import urlsplit
    h=urlsplit(url)
    if h.scheme!='https' or h.hostname not in ['zenodo.org','www.zenodo.org']:
        raise ValueError('UNTRUSTED_URL')
    req=urllib.request.Request(url,headers={'User-Agent':'ecostate-v10b-header-only/1'})
    md=hashlib.md5();sh=hashlib.sha256();n=0
    with urllib.request.urlopen(req,timeout=80) as r,open(p,'wb') as f:
        while 1:
            data=r.read(1024*1024)
            if not data:break
            n+=len(data)
            if n>MAXBYTES:raise ValueError('SIZE_LIMIT')
            f.write(data);md.update(data);sh.update(data)
    return n,md.hexdigest(),sh.hexdigest()

def first_row(z,member):
    with z.open(member) as f:
        for _,el in ET.iterparse(f,events=('end',)):
            if el.tag==NS+'row':
                cells=[]
                for c in el.findall(NS+'c'):
                    vv=c.find(NS+'v');inl=c.find(NS+'is')
                    value=vv.text if vv is not None else ''.join(inl.itertext()) if inl is not None else None
                    cells.append({'ref':c.attrib.get('r'),'type':c.attrib.get('t'),'value':value})
                return cells
            # The first row is at the head of sheet XML; keep child values until its end.
            # Clearing individual <v>/<c> nodes before row completion would erase headers.
    return []

def shared_lookup(z,indices):
    if 'xl/sharedStrings.xml' not in z.namelist():return {}
    out={}; ix=0
    with z.open('xl/sharedStrings.xml') as fh:
        for _,el in ET.iterparse(fh,events=('end',)):
            if el.tag==NS+'si':
                if ix in indices:out[ix]=''.join(el.itertext())
                ix+=1;el.clear()
                if len(out)==len(indices):break
            elif el.tag not in (NS+'t',NS+'r'):el.clear()
    return out

def run(outpath):
    out=Path(outpath);out.parent.mkdir(parents=True,exist_ok=True)
    r={'schema':'v10b.original_wolverine_zenodo_source','record_id':int(REC),
       'status':'SOURCE_STOP','original_animal_numeric_rows_opened':False,
       'biological_effect_estimated':False}
    try:
        url=f'{BASE}/api/records/{REC}'
        req=urllib.request.Request(url,headers={'User-Agent':'ecostate-v10b/1'})
        with urllib.request.urlopen(req,timeout=30) as inp:meta=json.load(inp)
        files=[x for x in meta['files'] if x.get('key')==FILENAME]
        if len(files)!=1:raise ValueError('FILE_MANIFEST_AMBIGUOUS')
        f=files[0]
        if str(f.get('checksum')).lower() != 'md5:'+SOURCE_MD5:raise ValueError('PROVIDER_CHECKSUM_MISMATCH')
        r['provider_size']=f.get('size');r['provider_md5']=SOURCE_MD5
        with tempfile.TemporaryDirectory() as t:
            name=Path(t)/'original.xlsx'
            url=f['links'].get('content') or f['links'].get('self')
            if not url:raise ValueError('NO_PROVIDER_DOWNLOAD_LINK')
            n,md,sh=download(url,name)
            if md!=SOURCE_MD5:raise ValueError('SOURCE_ORIGINAL_MD5_FAIL')
            r['actual_size']=n;r['actual_sha256']=sh
            with zipfile.ZipFile(name) as z:
                names=z.namelist()
                sheets=[x for x in names if x.startswith('xl/worksheets/sheet') and x.endswith('.xml')]
                if len(sheets)<1:raise ValueError('NO_WORKSHEET')
                cells=first_row(z,sheets[0]);ids={int(c['value']) for c in cells if c['type']=='s' and c['value'] is not None}
                look=shared_lookup(z,ids)
                header=[look.get(int(c['value']),c['value']) if c['type']=='s' and c['value'] is not None else c['value'] for c in cells]
                r['header_only']=header;r['worksheet_count']=len(sheets)
        r['status']='SOURCE_CHECKSUM_HEADER_ADMITTED'
    except Exception as e:
        r['status']='SOURCE_STOP_'+(f'HTTP_{e.code}' if hasattr(e,'code') else str(e))
    out.write_text(json.dumps(r,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    print('WOLVERINE_SOURCE_V10B',r['status'],'columns',len(r.get('header_only',[])))
    assert not r['biological_effect_estimated'] and not r['original_animal_numeric_rows_opened']
    return r
if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v10/results/wolverine_source_v10b.json')
