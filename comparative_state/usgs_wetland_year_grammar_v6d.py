"""Read only exact source year/date/region/property IDs; no animal or habitat outcomes."""
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import csv, io, json, hashlib, argparse
from comparative_state.usgs_2025_schema_gate_v6b import SOURCE,MD5,BYTES
import urllib.request

DATE_FORMATS=['%Y-%m-%d','%m/%d/%Y','%m/%d/%y','%Y/%m/%d','%d-%b-%Y','%m/%d/%Y %H:%M:%S']

def parse_date_grammar(value):
    for fmt in DATE_FORMATS:
        try:
            d=datetime.strptime(value.strip(),fmt)
            return d.year, fmt
        except ValueError:pass
    return None,None

def audit(b):
    if len(b)!=BYTES or hashlib.md5(b).hexdigest()!=MD5: return {'status':'SOURCE_STOP_MD5'}
    rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
    tokens=Counter();year_tokens=defaultdict(Counter);date_formats=Counter();unknown=[]
    for i,r in enumerate(rows):
        ytoken=r['Study year'].strip();year,fmt=parse_date_grammar(r['Date'])
        tokens[ytoken]+=1
        if fmt:date_formats[fmt]+=1;year_tokens[ytoken][str(year)]+=1
        else:unknown.append({'row_index_1based':i+1,'date_raw_format_sample':r['Date'][:45]})
    groups=len(set((r['Region'],r['County'],r['Property']) for r in rows))
    units=len(set((r['Region'],r['County'],r['Property'],r['Wetland unit']) for r in rows))
    status='SOURCE_YEAR_GRAMMAR_ADMITTED' if len(unknown)==0 else 'SOURCE_YEAR_GRAMMAR_STOP'
    return {'status':status,'row_count':len(rows),'year_tokens_counts':dict(tokens),
            'year_token_to_calendar_year_counts':{y:dict(c) for y,c in year_tokens.items()},
            'date_format_counts':dict(date_formats),'unparsed_date_count':len(unknown),
            'unparsed_date_examples':unknown[:3], 'unique_property_keys':groups,'unique_wetland_units':units,
            'original_bird_and_environment_values_opened':False,
            'original_sha256':hashlib.sha256(b).hexdigest()}

def run(out):
    r={'status':'SOURCE_STOP','original_bird_and_environment_values_opened':False}
    try:
        req=urllib.request.Request(SOURCE,headers={'User-Agent':'ecostate-study-year-source-audit/6.3'})
        with urllib.request.urlopen(req,timeout=50) as x:raw=x.read(BYTES+1)
        r=audit(raw)
    except Exception as e:r.update({'exception_type':type(e).__name__,'exception':str(e)[:300]})
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n')
    print('USGS_YEAR_GRAMMAR_V6D',r['status'])
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='comparative_state/results/usgs_wetland_year_grammar_v6d.json')
    run(p.parse_args().out)
