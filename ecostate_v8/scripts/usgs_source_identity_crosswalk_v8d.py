"""Response-blind strict source-ID/time overlap screen: USGS 2022 GPS vs 2023 iSSA.

No GPS coords, MNDWI, species or case_ values are read, exported, or modeled.
Only exact ID/time string membership; no fuzzy/heuristic repairs or offset guesses.
"""
import csv,hashlib,io,json,urllib.request,urllib.error,datetime,collections, argparse
from urllib.parse import urlsplit
from pathlib import Path

SOURCES=[
 {'item':'62ffeecfd34ed6dc55925915','name':'Datarelease_data_FinalDate_and_Status_List_Full_Data_withfinalclass_MNDWI.csv','size':30403945,'md5':'3e5a91b2d5176cce43101ffcb6a60f25'},
 {'item':'652edfe8d34edd15305a9ab0','name':'Data Release P9ELSUHN.csv','size':27997528,'md5':'78eb6064eca992225d6907d6e46f5bef'},
]

def get(url,lim=34000000):
    u=urlsplit(url)
    if u.scheme!='https' or u.hostname not in {'www.sciencebase.gov','sciencebase.gov','api.sciencebase.gov'}:
        raise ValueError('SOURCE_STOP unapproved provider host')
    req=urllib.request.Request(url,headers={'User-Agent':'ecostate-original-two-source-id-only/8d'})
    with urllib.request.urlopen(req,timeout=95) as res:
        raw=res.read(lim+1)
    if len(raw)>lim:raise ValueError('SOURCE_STOP excessive original file size')
    return raw

def fetch(s):
    meta=json.loads(get(f'https://www.sciencebase.gov/catalog/item/{s["item"]}?format=json',1000000))
    f=[x for x in meta.get('files',[]) if x.get('name')==s['name']]
    if len(f)!=1:raise ValueError('SOURCE_STOP file not uniquely named in provider manifest')
    entry=f[0]
    if entry.get('size')!=s['size'] or (entry.get('checksum') or {}).get('value')!=s['md5']:
        raise ValueError('SOURCE_STOP provider size/hash changed')
    uri=entry.get('downloadUri')
    if not uri:raise ValueError('SOURCE_STOP original downloadUri absent')
    data=get(uri)
    if len(data)!=s['size'] or hashlib.md5(data).hexdigest()!=s['md5']:
        raise ValueError('SOURCE_STOP downloaded original checksum mismatch')
    return data,hashlib.sha256(data).hexdigest()

PATTERNS=(('%Y-%m-%d %H:%M:%S','iso_seconds'),('%Y-%m-%d %H:%M','iso_minutes'),
 ('%m/%d/%Y %H:%M','us_minutes'),('%m/%d/%Y %H:%M:%S','us_seconds'),
 ('%Y-%m-%dT%H:%M:%S','T_seconds'),('%Y-%m-%dT%H:%M:%S%z','T_offset'))

def parsed_time(s):
    s=str(s).strip()
    for p,label in PATTERNS:
        try:
            d=datetime.datetime.strptime(s,p)
            if d.tzinfo is not None: return d.strftime('%Y-%m-%dT%H:%M'),label+'_provided_offset_no_zone_conversion'
            return d.strftime('%Y-%m-%dT%H:%M'),label
        except ValueError:pass
    try:
        n=float(s)
        if 1e9<n<2e9:return datetime.datetime.fromtimestamp(n,datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M'),'unix_seconds_UTC'
        if 1e12<n<2e12:return datetime.datetime.fromtimestamp(n/1000,datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M'),'unix_milliseconds_UTC'
    except ValueError:pass
    return None,'unparsed'

def audit(out):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    report={'schema':'ecostate.v8d.usgs2022_vs_2023_nooutcome_identity_audit',
      'source_dois':['10.5066/P9XBZKZ8','10.5066/P9ELSUHN'],
      'original_animal_ids_exported':False,'species_or_habitat_values_read':False,
      'gps_coordinates_read':False,'behavioral_outcomes_estimated':False,'status':'SOURCE_STOP'}
    try:
        (r1,sha1),(r2,sha2)=[fetch(s) for s in SOURCES]
        t1=csv.DictReader(io.StringIO(r1.decode('utf-8-sig')))
        t2=csv.DictReader(io.StringIO(r2.decode('utf-8-sig')))
        h1,h2=t1.fieldnames,t2.fieldnames
        a=('Xdeployment ID','Concat','Timestamp')
        b=('birdyear','timestamp')
        if any(x not in h1 for x in a) or any(x not in h2 for x in b):
            raise ValueError('SOURCE_SCHEMA_STOP exact documented identifiers absent')
        ids1={a[0]:set(),a[1]:set()};c1={a[0]:set(),a[1]:set()}
        grammar1=collections.Counter();grammar2=collections.Counter()
        rows1=rows2=0
        for row in t1:
            rows1+=1
            ts,g=parsed_time(row[a[2]]);grammar1[g]+=1
            for key in ids1:
                value=str(row[key]).strip()
                ids1[key].add(value)
                if ts is not None and value:c1[key].add((value,ts))
        ids2=set();c2=set()
        for row in t2:
            rows2+=1
            ts,g=parsed_time(row[b[1]]);grammar2[g]+=1
            value=str(row[b[0]]).strip()
            ids2.add(value)
            if ts is not None and value:c2.add((value,ts))
        n2max=max(1,len(c2))
        matches={key:{'exact_ID_string_overlap':len(vals & ids2),
                      'exact_ID_and_timestamp_overlap':len(c1[key] & c2),
                      'distinct_2022_ID_strings':len(vals)} for key,vals in ids1.items()}
        report.update({'status':'SOURCE_ONLY_CROSSWALK_AUDITED',
          'source_sha256':[sha1,sha2], 'original_rows':[rows1,rows2],
          'distinct_2023_birdyear_tokens':len(ids2),
          'distinct_2023_birdyear_time_keys':len(c2),
          'timestamp_grammars_2022':dict(grammar1),
          'timestamp_grammars_2023':dict(grammar2),
          'overlap_without_fuzzy_ID_or_timezone_repair':matches,
          'claim_limit':'String coincidence alone does not verify stable tag identity; a source-authenticated crosswalk and original step-origin/endpoint schema are still required.'})
    except Exception as e:
        report.update({'status':'SOURCE_STOP','error_class':type(e).__name__,'reason':str(e)[:320]})
    out.write_text(json.dumps(report,indent=2)+'\n')
    print('USGS_V8D_ID_ONLY',report['status'], report.get('overlap_without_fuzzy_ID_or_timezone_repair',{}))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    audit(p.parse_args().out)
