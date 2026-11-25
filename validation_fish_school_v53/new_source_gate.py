"""v53 source-only Dryad admission. No fish movement predictions."""
import argparse, hashlib, json, re, tempfile, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path, PurePosixPath
from collections import Counter

HOST='https://datadryad.org'
CONFIG={
 'ring':('10.5061/dryad.9m6d2',('metadata.txt','README.txt','8.zip')),
 'banded3d':('10.5061/dryad.j0226',('Data Dryad.zip',))
}
CAP=230_000_000
def api_url(href):
    u=urllib.parse.urljoin(HOST,href)
    p=urllib.parse.urlparse(u)
    if p.scheme!='https' or p.netloc!='datadryad.org' or not p.path.startswith('/api/v2/'):raise ValueError('UNEXPECTED_DRYAD_API_LINK')
    return u
def get_json(url):
    req=urllib.request.Request(api_url(url),headers={'Accept':'application/json','User-Agent':'boids-v53-source-audit/1.0'})
    with urllib.request.urlopen(req,timeout=60) as r:
        b=r.read(4_000_001)
    if len(b)>4_000_000:raise ValueError('API_JSON_CAP')
    return json.loads(b)
def href(d,key):return d['_links'][key]['href']
def inventory(doi):
    ds=get_json('/api/v2/datasets/'+urllib.parse.quote('doi:'+doi,safe=''))
    if str(ds.get('identifier','')).lower() not in ('doi:'+doi,doi):raise ValueError('DOI_DRIFT')
    vu=api_url(href(ds,'stash:version'))
    ver=get_json(vu)
    fu=api_url(ver.get('_links',{}).get('stash:files',{}).get('href',vu.rstrip('/')+'/files'))
    files=[];seen=set();declared=None
    for _ in range(10):
        if fu in seen:raise ValueError('PAGINATION_LOOP')
        seen.add(fu);d=get_json(fu);batch=d['_embedded']['stash:files']
        if declared is None:declared=d.get('total')
        files.extend(batch)
        nxt=d.get('_links',{}).get('next',{}).get('href')
        if not nxt:break
        fu=api_url(nxt)
    else:raise ValueError('FILE_PAGES_CAP')
    if declared is not None and len(files)!=int(declared):raise ValueError('INCOMPLETE_FILE_INVENTORY')
    return ds,vu,ver,files
def download(f,path):
    size=int(f['size'])
    if not 0<size<=CAP:raise ValueError('PUBLISHED_SIZE_STOP')
    u=api_url(href(f,'stash:download'))
    sha=hashlib.sha256();typ=str(f.get('digestType','')).lower().replace('-','')
    digest=str(f.get('digest','')).lower()
    if digest and typ not in ('sha256','sha1','md5','sha512'):raise ValueError('UNKNOWN_PROVIDER_HASH')
    other=hashlib.new(typ) if digest else None
    n=0
    req=urllib.request.Request(u,headers={'User-Agent':'boids-v53-source-audit/1.0','Accept':'application/octet-stream'})
    with urllib.request.urlopen(req,timeout=120) as r,path.open('wb') as out:
        if urllib.parse.urlparse(r.geturl()).scheme!='https':raise ValueError('NON_HTTPS_FILE')
        for b in iter(lambda:r.read(1024*1024),b''):
            n+=len(b)
            if n>size or n>CAP:raise ValueError('DOWNLOAD_CAP_OR_SIZE_DRIFT')
            sha.update(b)
            if other:other.update(b)
            out.write(b)
    if n!=size:raise ValueError('BYTE_SIZE_DRIFT')
    if other and other.hexdigest()!=digest:raise ValueError('PROVIDER_DIGEST_MISMATCH')
    return {'bytes':n,'sha256':sha.hexdigest(),'provider_digest_verified':bool(other)}
def structure(z):
    inf=z.infolist()
    if len(inf)>5000 or len({x.filename for x in inf})!=len(inf):raise ValueError('ZIP_ROSTER_STOP')
    if sum(x.file_size for x in inf)>1_800_000_000:raise ValueError('ZIP_EXPANDED_CAP')
    out=[]
    for f in inf:
        p=PurePosixPath(f.filename)
        if p.is_absolute() or '..' in p.parts or '\\' in f.filename:raise ValueError('UNSAFE_ZIP_PATH')
        if f.is_dir():continue
        row={'path':f.filename,'size':f.file_size,'crc32':format(f.CRC,'08x')}
        if p.suffix.lower() in ('.csv','.txt','.dat','.tsv'):
            # Only structural counts of at most first 64 lines; never export coordinate/time values.
            with z.open(f) as ff:
                lines=[ff.readline(65536) for _ in range(64)]
            nonempty=[s.decode('utf-8-sig',errors='replace').strip() for s in lines if s.strip()]
            widths=Counter(len(re.split(r'[\s,;]+',s)) for s in nonempty)
            row['sample_nonempty_line_count']=len(nonempty)
            row['sample_field_count_histogram']=dict(widths)
            if nonempty:
                h=nonempty[0].lstrip('#').strip()
                tok=re.split(r'[\s,;]+',h)
                if all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.()\[\]-]{0,79}',x) for x in tok) and len(tok)<=128:row['explicit_label_header']=tok
        out.append(row)
    return out
def run(which,out):
    doi,want=CONFIG[which]
    out.update(status='SOURCE_INVENTORY_STARTED',study=which,doi=doi,raw_coordinates_or_prediction_scores_exported=False)
    ds,vu,ver,files=inventory(doi)
    out.update(identifier=ds.get('identifier'),title=ds.get('title'),version_url=vu,version_number=ver.get('versionNumber',ds.get('versionNumber')),version_status=ver.get('versionStatus'),license=ds.get('license'),files=[])
    for f in files:
        out['files'].append({k:f.get(k) for k in ('path','size','digest','digestType','mimeType')}|{'download_endpoint':href(f,'stash:download')})
    chosen={}
    for w in want:
        m=[f for f in files if f['path']==w]
        if len(m)!=1:raise ValueError('SELECTED_SOURCE_NAME_NOT_UNIQUE:'+w)
        chosen[w]=m[0]
    out['downloaded']={}
    with tempfile.TemporaryDirectory() as td:
        for name,f in chosen.items():
            p=Path(td)/Path(name).name
            row=download(f,p);out['downloaded'][name]=row
            if name.lower().endswith('.zip'):
                with zipfile.ZipFile(p) as z:row['members']=structure(z)
            elif name=='README.txt':
                # Author data dictionary, bounded; do not copy observations from metadata.txt.
                raw=p.read_bytes()
                if len(raw)>32_000:raise ValueError('README_CAP')
                row['author_readme']=raw.decode('utf-8',errors='replace')
            elif name=='metadata.txt':
                raw=p.read_bytes()
                if len(raw)>100_000:raise ValueError('METADATA_CAP')
                lines=raw.decode('utf-8-sig',errors='replace').splitlines()
                clean=[l.strip() for l in lines if l.strip()]
                row['nonempty_lines']=len(clean)
                if clean:
                    tok=re.split(r'[\s,;]+',clean[0].lstrip('#').strip())
                    if all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.()\[\]-]{0,79}',x) for x in tok):row['explicit_label_header']=tok
            print('source authenticated',which,name,row['bytes'],row['sha256'],flush=True)
            p.unlink()
    out['status']='SOURCE_BYTES_AND_STRUCTURE_VERIFIED_ONLY'
def main():
    a=argparse.ArgumentParser();a.add_argument('study',choices=list(CONFIG));args=a.parse_args()
    p=Path('validation_fish_school_v53/results')/(args.study+'.json');p.parent.mkdir(parents=True,exist_ok=True)
    out={}
    try:run(args.study,out)
    except Exception as e:
        out['status']='SOURCE_STOP';out['error_type']=type(e).__name__
        out['reason']=str(e).split('?')[0][:500] # no signed storage query strings
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'study':args.study,'status':out.get('status'),'reason':out.get('reason'),'version':out.get('version_url'),'files':out.get('files'),'downloaded':{n:{k:v for k,v in d.items() if k not in ('members','author_readme')} for n,d in out.get('downloaded',{}).items()}},sort_keys=True),flush=True)
    if out['status']!='SOURCE_BYTES_AND_STRUCTURE_VERIFIED_ONLY':raise SystemExit(1)
if __name__=='__main__':main()
