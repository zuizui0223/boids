#!/usr/bin/env python3
"""Source-only child file inventory for original 2021 USGS P922KDU6.

Do not fetch source telemetry, read file data or infer source identification. This
stage only records child item metadata and source file names/size/hash.
"""
from __future__ import annotations
import argparse, json, urllib.request, urllib.parse
from pathlib import Path
CHILDREN = {
  'overlap':'6014ab7dd34edf5c66ea0f20',
  'flooded_area':'6014a739d34edf5c66ea0f10',
  'roost_night_distance':'6014a85dd34edf5c66ea0f16',
  'telemetry_wet_habitat':'6014a9efd34edf5c66ea0f1b',
}

def child_url(itemid):
  if itemid not in CHILDREN.values():raise ValueError("unverified USGS item")
  return f'https://www.sciencebase.gov/catalog/item/{itemid}?format=json'

def parse_item(key,itemid,v):
  if not isinstance(v,dict):raise ValueError('invalid item')
  fs=v.get('files',[])
  if not isinstance(fs,list):raise ValueError('invalid files')
  return {'category':key,'source_item_id':itemid,'title':v.get('title'),
    'files':[{'name':f.get('name'), 'size':f.get('size'),
       'checksum':f.get('checksum',f.get('md5'))} for f in fs if isinstance(f,dict)],
    'original_bird_values_opened':False,'true_roost_feeding_event_join_verified':False}

def fetch(url):
  p=urllib.parse.urlparse(url)
  if p.hostname!='www.sciencebase.gov' or p.scheme!='https' or p.path!='/catalog/item/'+p.path.split('/')[-1]:
    raise ValueError('source host not allowed')
  req=urllib.request.Request(url,headers={'User-Agent':'ecostate-usgs-child-file-v7c/1.0','Accept':'application/json'})
  with urllib.request.urlopen(req,timeout=35) as r: b=r.read(1_500_001)
  if len(b)>1_500_000:raise ValueError('oversize metadata')
  return json.loads(b)

def main(out):
  result={'schema':'ecostate.usgs_child_files_v7c','source_doi':'10.5066/P922KDU6',
    'status':'SOURCE_STOP','original_bird_rows_read':False,'new_field_effects':False,
    'entries':{}, 'biological_independence_from_california_2023':False}
  try:
    for key,item in CHILDREN.items():
      result['entries'][key]=parse_item(key,item,fetch(child_url(item)))
    result['status']='CHILD_METADATA_ADMITTED_NO_OUTCOMES'
    result['files_total']=sum(len(e['files']) for e in result['entries'].values())
  except Exception as exc:
    result['status']='SOURCE_STOP'
    result['reason']=type(exc).__name__+': '+str(exc)[:180]
  dst=Path(out);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  print('ROOST_CHILD_FILES_V7C',result['status'],'files',result.get('files_total'))

if __name__=='__main__':
  p=argparse.ArgumentParser();p.add_argument('--out',default='comparative_state/results/usgs_roost_child_files_v7c.json')
  main(p.parse_args().out)
