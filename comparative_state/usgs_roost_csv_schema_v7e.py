#!/usr/bin/env python3
"""Exact provider downloadUri resolver amendment to v7d's URL-404 source stop.

No model, original telemetry values, coordinates or ID data read. Scans source
metadata for the publisher's exact file downloadUri, then verifies original
MD5 and reads only the CSV header line. Prior 404 v7d is immutable.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.parse,urllib.request
from pathlib import Path
from comparative_state.usgs_roost_csv_schema_v7d import SRC,allowed_uri,header_only,source_get

def choose_download(item, filename):
  files=item.get('files',[])
  if not isinstance(files,list):raise ValueError('invalid item file roster')
  hits=[f for f in files if isinstance(f,dict) and f.get('name')==filename]
  if len(hits)!=1:raise ValueError('source file missing or duplicate')
  f=hits[0]
  for k in ['downloadUri','url','downloadURL','downloadUrl']:
    uri=f.get(k)
    if isinstance(uri,str) and allowed_uri(uri):return uri
  raise ValueError('publisher direct download URI not provided on source file')

def original_item(itemid):
  url='https://www.sciencebase.gov/catalog/item/'+itemid+'?format=json'
  req=urllib.request.Request(url,headers={'User-Agent':'ecostate-roost-provider-link-v7e/1.0','Accept':'application/json'})
  with urllib.request.urlopen(req,timeout=30) as resp:b=resp.read(1_000_001)
  if len(b)>1_000_000:raise ValueError('metadata too large')
  return json.loads(b)

def main(out):
 d={'schema':'ecostate.usgs_roost_csv_header_v7e_provider_uri','source_doi':'10.5066/P922KDU6',
    'status':'SOURCE_STOP','prior_v7d':'SOURCE_STOP_HTTP404_GUESSED_URI',
    'bird_outcomes_opened':False,'original_rows_exported':False,'true_origin_join_verified':False,
    'cohort_independence_verified':False,'entries':{}}
 try:
  for key,(itemid,name,size,expected_md5) in SRC.items():
    u=choose_download(original_item(itemid),name)
    b=source_get(u,size+1024)
    if len(b)!=size:raise ValueError(f'{key}: size discrepancy')
    md5=hashlib.md5(b).hexdigest()
    if md5!=expected_md5:raise ValueError(f'{key}: MD5 mismatch')
    d['entries'][key]={'file':name,'bytes':len(b),'md5':md5,'sha256':hashlib.sha256(b).hexdigest(),
      'columns':header_only(b),'body_not_parsed':True}
  d['status']='SOURCE_EXACT_HEADER_ONLY_ADMITTED'
 except Exception as e:
  d['status']='SOURCE_STOP'
  d['reason']=f'{type(e).__name__}: {str(e)[:240]}'
 p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
 print('ROOST_PROVIDER_URL_V7E',d['status'],'files',len(d['entries']))

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',default='comparative_state/results/usgs_roost_csv_schema_v7e.json')
 main(a.parse_args().out)
