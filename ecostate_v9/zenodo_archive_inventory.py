#!/usr/bin/env python3
"""Source-only exact original Zenodo 6319709 zip and safe member inventory. NO animal values."""
import hashlib,json,sys,zipfile,io,urllib.request,urllib.parse
from pathlib import Path
RECORD=6319709
API=f'https://zenodo.org/api/records/{RECORD}'
NAME='ESF_Rcodes.zip'
MD5='20bcf2babfc97c088f9b5948db23b5f1'
MAXSIZE=25_000_000

def source(url,maxn):
    u=urllib.parse.urlsplit(url)
    if u.scheme!='https' or u.hostname not in {'zenodo.org','www.zenodo.org','zenodo.cern.ch'}:
        raise ValueError('untrusted source domain')
    request=urllib.request.Request(url,headers={'User-Agent':'ecostate-v9-original-source/1.0'})
    with urllib.request.urlopen(request,timeout=100) as r:
        if int(r.headers.get('Content-Length','0'))>maxn:raise ValueError('max size limit')
        b=r.read(maxn+1)
    if len(b)>maxn:raise ValueError('over limit')
    return b

def run(output):
    out={'schema':'ecostate.v9.source_zip_v1','source_doi':'10.5281/zenodo.6319709',
         'status':'SOURCE_STOP','field_outcomes_accessed':False,'number_real_animal_results':0}
    try:
        m=json.loads(source(API,800_000))
        files=[f for f in m.get('files',[]) if f.get('key')==NAME]
        if len(files)!=1:raise ValueError('original archive name not unique')
        f=files[0];out['announced_size']=f.get('size');out['announced_checksum']=f.get('checksum')
        if 'md5:'+MD5 not in str(f.get('checksum')):raise ValueError('published MD5 mismatch')
        u=f.get('links',{}).get('self') or f.get('links',{}).get('content')
        if not u:raise ValueError('no official download link')
        b=source(u,MAXSIZE)
        if hashlib.md5(b).hexdigest()!=MD5:raise ValueError('original MD5 mismatch')
        out['sha256']=hashlib.sha256(b).hexdigest()
        out['byte_size']=len(b)
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            members=z.infolist()
            if len(members)>3000:raise ValueError('unsafe zip member count')
            if any(x.filename.startswith('/') or '..' in x.filename.split('/') for x in members):raise ValueError('unsafe member path')
            out['n_members']=len(members)
            out['members']=[{'path':x.filename,'bytes':x.file_size} for x in members]
            # Read only a README if present, never numeric/source animal observation rows.
            readme=[x for x in members if 'readme' in x.filename.lower() and x.file_size<100_000]
            if readme:
                out['readme_excerpt']=z.read(readme[0]).decode('utf8','replace')[:7500]
        out['status']='SOURCE_ARCHIVE_ORIGINAL_VERIFIED'
    except Exception as e:
        out['reason']=str(e)[:450]
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print('V9_ZENODO_SOURCE',out['status'],'members',out.get('n_members'),out.get('reason',''))
    return out

if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else '/tmp/zenodo_source_manifest_v9.json')
