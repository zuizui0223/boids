"""Fetch exact USGS ScienceBase CSV; verify MD5, inspect only column header and row count.

No biological response/environmental numerical values opened or saved.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, urllib.request
from pathlib import Path

SOURCE='https://www.sciencebase.gov/catalog/file/get/67c8bbcdd34ea599a3b9ae77?f=__disk__a0%2Fde%2F1b%2Fa0de1b601d022ae5829885bd1a83c60c43720a75'
SOURCE_DOI='10.5066/P13UJQP5'
MD5='48965f5cefa6364a34b6e92894b76a9b'
BYTES=45034


def source_schema_from_bytes(b: bytes):
    if len(b)!=BYTES or hashlib.md5(b).hexdigest()!=MD5:
        return {'status':'SOURCE_STOP_SIZE_OR_MD5','bytes':len(b), 'actual_md5':hashlib.md5(b).hexdigest()}
    text=b.decode('utf-8-sig', errors='strict')
    reader=csv.reader(io.StringIO(text))
    header=next(reader, None)
    if not header or len(set(header)) != len(header) or any(not c.strip() for c in header):
        return {'status':'SOURCE_SCHEMA_STOP_HEADER_INVALID','columns':header}
    n=0; ragged=0
    for row in reader:
        if not row: continue
        n+=1
        if len(row)!=len(header):ragged+=1
    if n<100 or ragged:
        return {'status':'SOURCE_SCHEMA_STOP_ROWS_OR_WIDTH','row_count':n,'ragged_rows':ragged, 'columns':header}
    return {'status':'SOURCE_SCHEMA_ONLY_ADMITTED','row_count':n,'column_count':len(header), 'column_names':header,
            'original_sha256':hashlib.sha256(b).hexdigest(), 'original_md5':MD5,'original_bytes':BYTES,
            'no_numeric_environment_or_bird_values_opened':True}


def run(out):
    receipt={'schema':'ecostate.usgs_california_wetland_original_header_v6b', 'source_doi':SOURCE_DOI,
             'source_file':'BirdUseCWHP.csv', 'status':'SOURCE_STOP_NETWORK',
             'no_numeric_environment_or_bird_values_opened':True}
    try:
        req=urllib.request.Request(SOURCE, headers={'User-Agent':'ecostate-source-header/6.1', 'Accept':'text/csv'})
        with urllib.request.urlopen(req,timeout=45) as r:
            b=r.read(BYTES+1)
        receipt.update(source_schema_from_bytes(b))
    except Exception as e:
        receipt.update({'reason_type':type(e).__name__,'reason':str(e)[:350]})
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('USGS_WETLAND_SOURCE_SCHEMA_V6B',receipt['status'],receipt.get('row_count',0),receipt.get('column_count',0))
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='comparative_state/results/usgs_waterbird_schema_v6b.json')
    run(ap.parse_args().out)
