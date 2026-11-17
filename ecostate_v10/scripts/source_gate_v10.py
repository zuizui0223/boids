"""Original Dryad DOI v10 source-only admission. No RDS parsing/outcome access."""
from __future__ import annotations
import hashlib, json, os, sys, time, urllib.request, urllib.error, urllib.parse
from pathlib import Path

DOI='10.5061/dryad.b8gtht7tf'
ROOT='https://datadryad.org'
DSPATH='/api/v2/datasets/doi%3A10.5061%2Fdryad.b8gtht7tf'
TARGET='data_for_model.rds'
MAX_BYTES=100_000_000

def trusted(url: str) -> str:
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.hostname not in ('datadryad.org','www.datadryad.org'):
        raise ValueError('SOURCE_STOP_UNTRUSTED_HOST')
    return url

def fetch_json(url):
    req=urllib.request.Request(trusted(url),headers={'User-Agent':'ecostate-v10-scientific-source-preflight/1.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=35) as r:
        return json.loads(r.read(5_000_000).decode())

def hrefs(o):
    # HAL linked sources; no guessed numeric versions or file ids.
    out=[]
    for x in o.get('_links',{}).values():
        if isinstance(x,dict) and x.get('href'):out.append(x['href'])
        elif isinstance(x,list):out +=[t['href'] for t in x if isinstance(t,dict) and t.get('href')]
    return out

def walk_embedded(o,depth=0):
    if depth>4:return []
    if isinstance(o,list):return sum((walk_embedded(x,depth+1) for x in o),[])
    if not isinstance(o,dict):return []
    found=[]
    if o.get('filename')==TARGET or o.get('path')==TARGET:found.append(o)
    for k,v in o.items():
        if isinstance(v,(list,dict)):found +=walk_embedded(v,depth+1)
    return found

def status_error(e):
    if isinstance(e,urllib.error.HTTPError):return f'HTTP_{e.code}'
    return type(e).__name__

def run(out_dir):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    receipt={'schema':'ecostate.v10.original_red_deer_source_only','source_doi':DOI,
             'original_data_opened':False,'numeric_animal_effect_computed':False,
             'status':'SOURCE_STOP','target':TARGET,
             'provider':'Dryad','source_version_known':False}
    try:
        ds=fetch_json(ROOT+DSPATH)
        receipt['dataset_title']=ds.get('title')
        receipt['dataset_id']=ds.get('id')
        receipt['source_version_known']=True
        # Resolve provider-supplied version link and file-list, without scraping HTML or guessing IDs.
        links=hrefs(ds)
        version_urls=[ROOT+u if u.startswith('/') else u for u in links if '/versions/' in u and not u.endswith('/files')]
        if not version_urls:
            for h in links:
                if h.endswith('/versions'):
                    v=fetch_json(ROOT+h if h.startswith('/') else h)
                    version_urls += [ROOT+k if k.startswith('/') else k for k in hrefs(v) if '/versions/' in k]
        receipt['provider_version_links']=len(version_urls)
        files=[]
        checked=set()
        for v in version_urls[:5]:
            if v in checked:continue
            checked.add(v)
            try:
                vv=fetch_json(v)
                files += walk_embedded(vv)
                for h in hrefs(vv):
                    if '/files' in h:
                        ff=fetch_json(ROOT+h if h.startswith('/') else h)
                        files += walk_embedded(ff)
                # Official simple variant, only for a verified version resource
                if not files and '/versions/' in v:
                    ff=fetch_json(v.rstrip('/')+'/files')
                    files +=walk_embedded(ff)
            except Exception as e:receipt.setdefault('nonfatal_source_errors',[]).append(status_error(e))
        if not files:
            receipt['status']='SOURCE_METADATA_ONLY_NO_FILE_LIST'
        else:
            canonical={json.dumps(x,sort_keys=True):x for x in files}
            fileobj=list(canonical.values())
            receipt['matched_named_files']=len(fileobj)
            receipt['declared_files']=[{'filename':f.get('filename'),'size':f.get('size'),'digest':str(f.get('digest') or f.get('checksum') or '')} for f in fileobj]
            if len(fileobj)!=1:
                receipt['status']='SOURCE_STOP_AMBIGUOUS_FILE'
            else:
                f=fileobj[0]
                # Source API offers downloadHref, or linked file resource that must resolve to official file_stream.
                links=hrefs(f)
                candidates=[x for x in links if ('file_stream' in x or '/download' in x)]
                if not candidates and f.get('id'):
                    candidates=[f'/downloads/file_stream/{f["id"]}']
                if not candidates:
                    receipt['status']='SOURCE_FILE_ID_NO_PUBLIC_ROUTE'
                else:
                    # HEAD only for source access preflight; later full GET must be separately frozen.
                    url=ROOT+candidates[0] if candidates[0].startswith('/') else candidates[0]
                    try:
                        req=urllib.request.Request(trusted(url),method='HEAD',headers={'User-Agent':'ecostate-v10-source-preflight/1.0'})
                        with urllib.request.urlopen(req,timeout=40) as resp:
                            receipt['status']='SOURCE_FILE_HEAD_ADMITTED'
                            receipt['public_download_route']=url
                            receipt['head_content_length']=resp.headers.get('Content-Length')
                    except Exception as e:
                        receipt['head_status']=status_error(e)
                        # A HEAD response can differ from ordinary public GET for a published file.
                        # One standard authenticated-free GET range check; no scraping or bypass.
                        # Inspect only HTTP status and first 16 magic bytes, NEVER RDS rows.
                        try:
                            request=urllib.request.Request(trusted(url),headers={
                                'User-Agent':'ecostate-v10-source-preflight/1.0',
                                'Range':'bytes=0-31','Accept':'application/octet-stream'})
                            with urllib.request.urlopen(request,timeout=40) as resp:
                                head=resp.read(32)
                                receipt['public_get_status']=resp.status
                                receipt['public_get_content_type']=resp.headers.get('Content-Type')
                                receipt['public_get_magic_sample_only']=len(head)
                                receipt['status']='SOURCE_PUBLIC_GET_HEADER_ADMITTED'
                                receipt['public_download_route']=url
                        except Exception as e2:
                            receipt['status']='SOURCE_PUBLIC_GET_'+status_error(e2)
        receipt['api_source_metadata_read']=True
    except Exception as e:
        receipt['status']='SOURCE_METADATA_'+status_error(e)
    (out/'red_deer_source_v10.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print('V10_SOURCE_GATE',receipt['status'], 'versionLinks',receipt.get('provider_version_links'), 'matched',receipt.get('matched_named_files'))
    assert receipt['original_data_opened'] is False and receipt['numeric_animal_effect_computed'] is False
    return receipt

if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v10/results')
