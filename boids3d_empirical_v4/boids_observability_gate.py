#!/usr/bin/env python3
"""Screen track data for short-range, approximately synchronous neighbor observations.

This is a structural *opportunity* gate, NOT evidence of social interactions.
Predeclared illustrative scale: <=5 sec and <=100 m in x-y-z for fast social Boids.
These thresholds are not taxon-universal and must be redesigned using actual sensory
range and movement response times for each future species. Does not fit Boids forces.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from datetime import datetime
from statistics import median
from collections import defaultdict


def fnum(s):
    try:
        x=float(s)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError):
        return None


def parse_ts(s):
    try:
        return datetime.fromisoformat(s.strip().replace('Z','+00:00')).timestamp()
    except (TypeError,ValueError,AttributeError):
        return None


def assess(csv_file, *, id_col='animal-id', time_col='timestamp', lon_col='location-long', lat_col='location-lat', z_col='height-above-msl'):
    by=defaultdict(list)
    events=[]
    with Path(csv_file).open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            iid=(r.get(id_col) or '').strip()
            t=parse_ts(r.get(time_col) or '')
            lon=fnum(r.get(lon_col));lat=fnum(r.get(lat_col));z=fnum(r.get(z_col))
            if not iid or t is None or lon is None or lat is None or z is None:continue
            e=(t,iid,lon,lat,z)
            events.append(e)
            by[iid].append(t)
    events.sort()
    gaps=[]
    for times in by.values():
        times.sort()
        gaps.extend([v-u for u,v in zip(times[:-1],times[1:]) if v>u and v-u<3600])
    pair_count={5:0,15:0}
    near_count={100:0,500:0}
    near_sets={100:set(),500:set()}
    for i,a in enumerate(events):
        j=i+1
        while j<len(events) and events[j][0]-a[0]<=15:
            b=events[j]
            j+=1
            dt=b[0]-a[0]
            if a[1]==b[1]:continue
            pair_count[15]+=1
            if dt<=5:pair_count[5]+=1
            # Approximation only valid for regional-scale tracking (typical locations within a few 100km).
            dx=(b[2]-a[2])*111320*math.cos(math.radians((a[3]+b[3])/2))
            dy=(b[3]-a[3])*111320
            dist=math.hypot(math.hypot(dx,dy),b[4]-a[4])
            if dt<=5 and dist<=100:
                near_count[100]+=1
                near_sets[100].add(tuple(sorted((a[1],b[1]))))
            if dist<=500:
                near_count[500]+=1
                near_sets[500].add(tuple(sorted((a[1],b[1]))))
    return {
        'events':len(events),'individuals':len(by),'median_within_individual_gap_s':median(gaps) if gaps else None,
        'cross_individual_pairs_temporal_5sec':pair_count[5],
        'cross_individual_pairs_temporal_15sec':pair_count[15],
        'near_5sec_100m':near_count[100], 'near_15sec_500m':near_count[500],
        'unique_100m_individual_pairs':len(near_sets[100]),
        'unique_500m_individual_pairs':len(near_sets[500]),
        'illustrative_fast_social_boids_gate_pass':near_count[100]>=50 and len(near_sets[100])>=3 and median(gaps)<=10 if gaps else False,
        'not_a_biological_rule':'Spatial/time filters are sample observability heuristics, not universal taxon constants.'
    }

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--csv',type=Path,required=True)
    ap.add_argument('--out',type=Path)
    for name in ('id-col','time-col','lon-col','lat-col','z-col'):ap.add_argument('--'+name)
    args=ap.parse_args()
    kw={x:getattr(args,x,None) for x in ('id_col','time_col','lon_col','lat_col','z_col') if getattr(args,x,None)}
    d=assess(args.csv,**kw)
    if args.out:args.out.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
    print(json.dumps(d,indent=2))
