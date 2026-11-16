#!/usr/bin/env python3
"""Original verified 2022 polar-bear SSF zip; structure-only CSV schema, no outcomes."""
import csv,hashlib,io,json,sys,zipfile,urllib.request,urllib.parse
from pathlib import Path
API='https://zenodo.org/api/records/6319709'; FILE='ESF_Rcodes.zip'
MD5='20bcf2babfc97c088f9b5948db23b5f1'; MAX=25_000_000
CSV=['data/SSF_data.csv','data/ESF_data.csv','data/model_comparison_data.csv']

def fetch(url):
 u=urllib.parse.urlparse(url)
 if u.scheme!='https' or u.hostname not in {'zenodo.org','www.zenodo.org'}:
  raise ValueError('untrusted download domain')
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'v9-source-only/1.0'}),timeout=100) as r:
  b=r.read(MAX+1)
 if len(b)>MAX:raise ValueError('oversized')
 return b

def run(out):
 result={'status':'SOURCE_STOP','source_doi':'10.5281/zenodo.6319709','numeric_ecological_outcomes_opened':False,'estimated_effects':0,'role':'original_csv_header_and_rowcount_only'}
 try:
  record=json.loads(fetch(API));f=[x for x in record['files'] if x['key']==FILE]
  if len(f)!=1:raise ValueError('duplicate archive')
  url=f[0]['links'].get('self') or f[0]['links'].get('content');b=fetch(url)
  if hashlib.md5(b).hexdigest()!=MD5:raise ValueError('MD5 error')
  result['original_zip_sha256']=hashlib.sha256(b).hexdigest()
  result['files']={}
  with zipfile.ZipFile(io.BytesIO(b)) as z:
   for path in CSV:
    with z.open(path) as stream:
     data=io.TextIOWrapper(stream,encoding='utf-8-sig',newline='')
     reader=csv.reader(data)
     columns=next(reader)
     n=sum(1 for _ in reader)
     result['files'][path]={'row_count':n,'columns':columns,'n_columns':len(columns),'original_member_bytes':z.getinfo(path).file_size}
  result['status']='SOURCE_SCHEMA_ADMITTED'
 except Exception as e:result['reason']=str(e)[:500]
 p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
 print('V9_ORIGINAL_CSV_SOURCE_SCHEMA',result['status'],json.dumps({k:{'rows':v['row_count'],'columns':v['columns']} for k,v in result.get('files',{}).items()}))
 return result
if __name__=='__main__':run(sys.argv[1])
