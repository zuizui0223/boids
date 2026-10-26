#!/usr/bin/env python3
"""Header-only diagnostic after v8 STOP_REQUIRED_COLUMNS.
No numeric rows are opened and no original animal GPS data are exported.
"""
from collections import Counter
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from urllib.request import Request,urlopen
import argparse,csv,json
from pigeon_timing_gate import verify, group_archive, SOURCE_URL
REQUIRED={'Date','Time','Latitude','Longitude','Altitude'}

def probe(data,skip_verify=False):
 if not skip_verify:verify(data)
 variants=Counter();missing=Counter();samples={};invalid=[]
 with ZipFile(BytesIO(data)) as arc:
  groups=group_archive(arc)
  for key,paired in groups.items():
   for bird,info in paired.items():
    sample=arc.read(info)[:12001]
    ends=[sample.find(n) for n in (b'\n',b'\r') if sample.find(n)>=0]
    head=sample[:min(ends)] if ends else sample[:12000]
    cols=tuple(c.strip() for c in next(csv.reader([head.decode('utf-8-sig','replace')]),[]))
    variants[cols]+=1
    gap=tuple(sorted(REQUIRED-set(cols)))
    if gap:
     missing[gap]+=1
     if len(invalid)<20:invalid.append({'file':info.filename,'missing':list(gap),'header':list(cols)[:14]})
    if cols not in samples:samples[cols]=info.filename
 return {'status':'HEADER_ONLY_NO_MOVEMENT_VALUES','candidate_flights':len(groups),
         'matched_files_checked':2*len(groups),
         'header_variant_count':len(variants),
         'header_variants':[{'fields':list(k)[:16],'file_count':v,'example_file':samples[k]} for k,v in variants.most_common(15)],
         'required_column_missing_patterns':[{'missing':list(k),'file_count':v} for k,v in missing.most_common()],
         'nonconforming_examples':invalid,'numeric_rows_inspected':False}

def main():
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=Path('validation_v8/results/pigeon_header_diagnostic.json'));s=a.parse_args()
 data=urlopen(Request(SOURCE_URL,headers={'User-Agent':'boids-v8-header-diagnostic/1.0'}),timeout=180).read()
 r=probe(data)
 s.out.parent.mkdir(parents=True,exist_ok=True);s.out.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
