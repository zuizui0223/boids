#!/usr/bin/env python3
"""v8: pre-outcome dual-tracker alignment and position observability audit.

Only time coverage, 3D completeness and neighbor observability are measured.
No velocity response, force parameter, or predictive outcome is inspected.
Public data: Zenodo 5010830, exact original ZIP MD5 pinned by v7.
"""
from __future__ import annotations
import argparse, bisect, csv, hashlib, io, json, math, re, statistics, zipfile
from collections import defaultdict, Counter
from datetime import datetime, date, timedelta
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

SOURCE_URL='https://zenodo.org/api/records/5010830/files/GPS_tracks.zip/content'
EXPECTED_BYTES=35052731
EXPECTED_MD5='8c8e95641182363ea7ad6d0a9a50a3b1'
PHASE='2_demonstrator_observer_paired_releases'
PAIR_RE=re.compile(r'^([A-Za-z]\d{2})([A-Za-z]\d{2})_(\d+)\.csv$',re.I)
MAX_ZIP_FILES=10000
MAX_UNCOMPRESSED=1000000000
MAX_TIME_MISMATCH_S=0.11
MIN_MATCHED_SAMPLES=30
MIN_FLIGHT_DURATION_S=5
MIN_ELIGIBLE_FLIGHTS=8
MIN_DYADS=3

DATE_FORMATS=('%Y-%m-%d','%Y/%m/%d','%d/%m/%Y','%m/%d/%Y','%d.%m.%Y','%d-%m-%Y','%m-%d-%Y','%d/%m/%y','%m/%d/%y','%Y%m%d')
TIME_FORMATS=('%H:%M:%S.%f','%H:%M:%S','%H:%M:%S,%f','%H%M%S.%f','%H%M%S')

def time_value(date_s:str,time_s:str):
    date_s=date_s.strip();time_s=time_s.strip()
    if not date_s or not time_s:return None
    dd=None
    for fmt in DATE_FORMATS:
        try:dd=datetime.strptime(date_s,fmt).date();break
        except ValueError:pass
    if dd is None:
        try:dd=datetime.fromisoformat(date_s).date()
        except ValueError:return None
    tt=None
    for fmt in TIME_FORMATS:
        try:tt=datetime.strptime(time_s,fmt).time();break
        except ValueError:pass
    if tt is None:
        try:
            q=float(time_s)
            if not (math.isfinite(q) and 0<=q<1):return None
            return datetime.combine(dd,datetime.min.time()).timestamp()+q*86400
        except ValueError:return None
    return datetime.combine(dd,tt).timestamp()

def numeric(s):
    try:
        z=float(s)
        return z if math.isfinite(z) else None
    except (TypeError,ValueError):return None

def verify(data):
    if len(data)!=EXPECTED_BYTES:raise ValueError('STOP_SOURCE_LENGTH')
    md5=hashlib.md5(data).hexdigest()
    if md5!=EXPECTED_MD5:raise ValueError('STOP_SOURCE_MD5')
    return {'length':len(data),'md5':md5,'sha256':hashlib.sha256(data).hexdigest()}

def group_archive(archive):
    files=[x for x in archive.infolist() if not x.is_dir()]
    if len(files)>MAX_ZIP_FILES or sum(x.file_size for x in files)>MAX_UNCOMPRESSED:
        raise ValueError('STOP_ZIP_BOMB')
    group=defaultdict(dict)
    for e in files:
        p=PurePosixPath(e.filename)
        if p.is_absolute() or '..' in p.parts:raise ValueError('STOP_UNSAFE_PATH')
        if '__MACOSX' in p.parts or p.name.startswith('._') or PHASE not in p.parts:continue
        m=PAIR_RE.fullmatch(p.name)
        if not m:continue
        a,b=m.group(1).upper(),m.group(2).upper()
        if a==b:continue
        site=next((v for v in p.parts if v.startswith('Site')), 'unknown')
        key=(site,*sorted((a,b)),int(m.group(3)))
        group[key][a]=e
    return {k:v for k,v in group.items() if len(v)==2 and set(v)==set(k[1:3])}

def parse_csv(archive,info):
    buf=archive.read(info)
    rows=csv.DictReader(io.TextIOWrapper(io.BytesIO(buf),encoding='utf-8-sig',errors='replace',newline=None))
    needed={'Date','Time','Latitude','Longitude','Altitude'}
    header=set((rows.fieldnames or []))
    if not needed<=header:raise ValueError('STOP_REQUIRED_COLUMNS')
    points=[];count=0;malformed=0;parsedtime=0
    for row in rows:
        count+=1
        t=time_value(row.get('Date') or '',row.get('Time') or '')
        if t is None:
            malformed+=1;continue
        parsedtime+=1
        lat=numeric(row.get('Latitude'));lon=numeric(row.get('Longitude'));h=numeric(row.get('Altitude'))
        if lat is None or lon is None or h is None or not(-90<=lat<=90) or not(-180<=lon<=180):
            malformed+=1;continue
        points.append((t,lat,lon,h))
    points.sort(key=lambda x:x[0])
    # Timestamp duplicates reflect unresolved observation precision; we cannot silently interpolate them.
    unique=[]
    for p in points:
        if not unique or p[0]>unique[-1][0]:unique.append(p)
    dt=[b[0]-a[0] for a,b in zip(unique,unique[1:]) if b[0]>a[0]]
    return unique,{'total_rows':count,'valid_rows':len(unique),'time_parsed':parsedtime,
                   'invalid_rows':malformed,'duplicate_timestamps':len(points)-len(unique),
                   'median_dt_s':statistics.median(dt) if dt else None}

def meter_distance(x,y):
    # Horizontal local-tangent approximation; only a proximity feasibility metric.
    meanlat=math.radians((x[1]+y[1])/2)
    dx=(y[2]-x[2])*111320*math.cos(meanlat)
    dy=(y[1]-x[1])*111320
    return math.sqrt(dx*dx+dy*dy+(y[3]-x[3])**2)

def pair_match(a,b,tol=MAX_TIME_MISMATCH_S):
    ts=[q[0] for q in b]
    match=[];taken=set();last=-1
    for left in a:
        p=bisect.bisect_left(ts,left[0]);opts=(p-1,p,p+1)
        candidates=[j for j in opts if 0<=j<len(b) and j not in taken and j>last and abs(ts[j]-left[0])<=tol]
        if not candidates:continue
        j=min(candidates,key=lambda k:abs(ts[k]-left[0]));taken.add(j);last=j
        match.append((left,b[j]))
    return match

def evaluate(data,skip_checksum=False):
    checksum=verify(data) if not skip_checksum else {'source_sha256':None,'checksum_bypassed_for_synthetic_test':True}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        candidates=group_archive(z)
        bydyad=Counter();per=[];cadence=[];close=Counter(); parsefail=Counter();used_positions=0
        for key,paths in sorted(candidates.items()):
            a,b=key[1:3]
            x,mx=parse_csv(z,paths[a]);y,my=parse_csv(z,paths[b]);match=pair_match(x,y)
            if not match:parsefail['no_time_match']+=1;continue
            dtmed=[]
            for zed in (mx,my):
                if zed['median_dt_s'] is not None:dtmed.append(zed['median_dt_s'])
            if dtmed:cadence.append(statistics.median(dtmed))
            duration=match[-1][0][0]-match[0][0][0] if len(match)>1 else 0
            if len(match)<MIN_MATCHED_SAMPLES or duration<MIN_FLIGHT_DURATION_S:
                parsefail['insufficient_synchronous_support']+=1;continue
            d=[meter_distance(q,r) for q,r in match]
            if sum(t<=100 for t in d)>=10:close['10_x_100m']+=1
            if sum(t<=500 for t in d)>=10:close['10_x_500m']+=1
            if sum(t<=1000 for t in d)>=10:close['10_x_1000m']+=1
            bydyad[(key[0],key[1],key[2])]+=1
            used_positions+=len(match)
            per.append({'site':key[0],'dyad':f'{key[1]}-{key[2]}','release':key[3],
                        'matched_fix_count':len(match),'matched_duration_s':round(duration,3),
                        'median_pair_distance_m':round(statistics.median(d),1),
                        'samples_within_100m':sum(t<=100 for t in d),
                        'samples_within_500m':sum(t<=500 for t in d),
                        'invalid_rows_a':mx['invalid_rows'],'invalid_rows_b':my['invalid_rows'],
                        'dup_timestamps_a':mx['duplicate_timestamps'],'dup_timestamps_b':my['duplicate_timestamps']})
    n=len(per);n_dyads=len(bydyad)
    return {'study':'PIGEON_PAIRED_NUMERIC_ELIGIBILITY_V8','analysis_status':'STRUCTURAL_ONLY_NO_DIRECTIONAL_OUTCOMES',
        'source':checksum,'fixed_time_match_tolerance_s':MAX_TIME_MISMATCH_S,'min_matched_samples_per_flight':MIN_MATCHED_SAMPLES,
        'candidate_named_pairs':len(candidates),'eligible_synchronized_flights':n,'eligible_site_dyads':n_dyads,
        'total_matched_fix_pairs':used_positions,'median_track_cadence_seconds':statistics.median(cadence) if cadence else None,
        'n_flights_10_fixes_under_100m':close['10_x_100m'], 'n_flights_10_fixes_under_500m':close['10_x_500m'],
        'n_flights_10_fixes_under_1000m':close['10_x_1000m'],
        'dyad_replicate_counts':{f'{k[0]}:{k[1]}-{k[2]}':v for k,v in bydyad.items()},
        'structural_exclusion_reasons':dict(parsefail),'eligible_flights':per,
        'gate':'PASS' if n>=MIN_ELIGIBLE_FLIGHTS and n_dyads>=MIN_DYADS else 'STOP',
        'boundary':'No directional response, steering model or forecast score opened. Potential GPS altitude error and bird identity overlap not assessed.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--out',type=Path,default=Path('validation_v8/results/pigeon_timing_gate_v8.json'));a=p.parse_args()
    data=a.source.read_bytes() if a.source else urlopen(Request(SOURCE_URL,headers={'User-Agent':'boids-v8-structural-gate/1.0'}),timeout=180).read()
    result=evaluate(data)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='eligible_flights'},indent=2))
    return 0 if result['gate']=='PASS' else 3
if __name__=='__main__':raise SystemExit(main())
