#!/usr/bin/env python3
"""No-response-value source-only original checksum and CSV headers: USGS P922KDU6.

Downloads 3 original open files solely for exact size/MD5 and first header line.
Never exports original telemetry rows, original GPS coordinates, animal IDs or data
values. A shared field name does not establish actual identity/time/event join.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,urllib.parse,urllib.request
from pathlib import Path
SRC={
 'distance':('6014a85dd34edf5c66ea0f16','telem_day_night_distance.csv',5258934,'b901d2e2ebbdaf36b1e30a86ba2fd959'),
 'wet_habitat':('6014a9efd34edf5c66ea0f1b','telemetry_3maps_intersection.csv',3195785,'4219b56c671c3440665850278c3e2299'),
 'dynamic_area':('6014a739d34edf5c66ea0f10','proportion_area_flooded_3_maps.csv',5014,'f7c6e98fbdc205e8657fb1f6ef626314'),
}

def allowed_uri(url):
 p=urllib.parse.urlparse(url)
 return p.scheme=='https' and p.hostname in ('www.sciencebase.gov','sciencebase.gov') and (p.path.startswith('/catalog/file/get/') or p.path.startswith('/catalog/item/'))

def file_url(itemid,filename):
 return 'https://www.sciencebase.gov/catalog/file/get/'+itemid+'?f='+urllib.parse.quote(filename,safe='')

def header_only(b):
 if b[:4]==b'PK\x03\x04': raise ValueError('not plain CSV')
 start=b.split(b'\n',1)[0].rstrip(b'\r')
 if len(start)>4000:raise ValueError('CSV header too large')
 line=start.decode('utf-8-sig')
 cols=next(csv.reader([line]))
 if len(cols)<2:raise ValueError('no tabular header')
 return cols

def source_get(url,limit):
 if not allowed_uri(url):raise ValueError('blocked outside original source')
 req=urllib.request.Request(url,headers={'User-Agent':'ecostate-usgs-2021-original-header-only-v7d/1.0'})
 with urllib.request.urlopen(req,timeout=60) as resp: b=resp.read(limit+1)
 if len(b)>limit:raise ValueError('size gate')
 return b

def main(out):
 data={'schema':'ecostate.usgs_roost_csv_header_v7d','source_doi':'10.5066/P922KDU6',
   'status':'SOURCE_STOP','original_bird_outcomes_opened':False,'original_rows_exported':False,
   'individual_origin_to_destination_verified':False,'independent_cohort_verified':False,'entries':{}}
 try:
  for key,(itemid,name,size,md5) in SRC.items():
   # Fetch exactly the published original file bytes; do not parse original rows.
   b=source_get(file_url(itemid,name),size+1024)
   if len(b)!=size:raise ValueError(f'{key}: provider original size mismatch {len(b)} vs {size}')
   realmd5=hashlib.md5(b).hexdigest()
   if realmd5!=md5:raise ValueError(f'{key}: provider original MD5 mismatch')
   data['entries'][key]={'file':name,'size':len(b),'md5':realmd5,
      'sha256':hashlib.sha256(b).hexdigest(),'source_columns':header_only(b),
      'original_body_not_parsed':True}
  data['status']='SOURCE_HEADERS_ONLY_ADMITTED'
 except Exception as exc:
  data['status']='SOURCE_STOP'
  data['reason']=type(exc).__name__+': '+str(exc)[:180]
 dst=Path(out);dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
 print('USGS_ROOST_ORIGINAL_CSV_V7D',data['status'],'files',len(data['entries']))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',default='comparative_state/results/usgs_roost_csv_schema_v7d.json')
 main(p.parse_args().out)
