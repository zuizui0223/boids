"""Original public USGS telemetry CSV checksum, header, rowcount only.

Potential crosswalk to 2023 California iSSA, NOT independent field replication.
Do not read or export animals, movements, ecology outcomes, or GPS coordinates.
"""
import argparse,csv,hashlib,io,json,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlsplit

ITEM='62ffeecfd34ed6dc55925915'
NAME='Datarelease_data_FinalDate_and_Status_List_Full_Data_withfinalclass_MNDWI.csv'
PUBLISHED_MD5='3e5a91b2d5176cce43101ffcb6a60f25'
PUBLISHED_BYTES=30403945
MAX_BYTES=34000000

def request_bytes(url,size_limit):
    h=urlsplit(url).hostname
    if h not in ('www.sciencebase.gov','sciencebase.gov','api.sciencebase.gov') or urlsplit(url).scheme!='https':
        raise ValueError('SOURCE_STOP unapproved provider URL')
    req=urllib.request.Request(url,headers={'User-Agent':'ecostate-v8c-USGS-original-source-only/1.0'})
    with urllib.request.urlopen(req,timeout=85) as f:
        b=f.read(size_limit+1)
    if len(b)>size_limit:raise ValueError('SOURCE_STOP original file size exceeds cap')
    return b

def run(out):
    report={'schema':'ecostate.v8c.usgs2022_original_header_only',
      'source_doi':'10.5066/P9XBZKZ8','source_item':ITEM,'expected_file':NAME,
      'published_md5':PUBLISHED_MD5,'published_bytes':PUBLISHED_BYTES,
      'any_animal_identifiers_exported':False,'any_ecological_outcomes_read':False,
      'any_biological_effect_estimated':False,'status':'SOURCE_STOP'}
    try:
        meta=json.loads(request_bytes(f'https://www.sciencebase.gov/catalog/item/{ITEM}?format=json',1000000))
        found=[f for f in meta.get('files',[]) if f.get('name')==NAME]
        if len(found)!=1:raise ValueError('SOURCE_STOP original CSV not uniquely identified')
        f=found[0]
        assert f.get('size')==PUBLISHED_BYTES
        checksum=f.get('checksum') or {}
        assert checksum.get('value')==PUBLISHED_MD5 and checksum.get('type','').lower()=='md5'
        url=f.get('downloadUri')
        if not url:raise ValueError('SOURCE_STOP no original publisher download URI')
        raw=request_bytes(url,MAX_BYTES)
        if len(raw)!=PUBLISHED_BYTES or hashlib.md5(raw).hexdigest()!=PUBLISHED_MD5:
            raise ValueError('SOURCE_STOP original source byte/digest mismatch')
        reader=csv.reader(io.StringIO(raw.decode('utf-8-sig',errors='strict')))
        header=next(reader)
        if len(header)!=len(set(header)) or len(header)<3:
            raise ValueError('SOURCE_SCHEMA_STOP duplicate or sparse header')
        n=sum(1 for _ in reader) # Do not materialize biological row values.
        report.update({'status':'SOURCE_HEADER_ONLY_ADMITTED',
            'sha256_original_bytes':hashlib.sha256(raw).hexdigest(),
            'n_original_csv_rows':n,'n_columns':len(header),
            'original_column_names':header,'raw_CSV_bytes':len(raw)})
    except Exception as e:
        report.update({'status':'SOURCE_STOP','reason_type':type(e).__name__,
                       'reason':str(e)[:300]})
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n')
    print('USGS_V8C_ORIGINAL_HEADER_ONLY',report['status'],report.get('n_original_csv_rows'))
    return report

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
