#!/usr/bin/env python3
"""Exploratory bat vertical-transition benchmark (NOT full social Boids).

Usage:
    python empirical_transition_benchmark.py --csv path/to/annotated.csv --out result.json
    python empirical_transition_benchmark.py --download --out result.json

Dataset: archived annotated Tadarida teniotis, Movebank DOI 10.5441/001/1.52nn82r9.
The annotated archive is publicly accessible. Verify licensing/citation before redistribution.

Models are nested *descriptive categorical transition policies*, not inferred steering forces:
 M0 next climb class marginal
 M1 previous climb class
 M2 previous climb class + contemporaneous environmental vertical wind estimate
 M3 individual-specific residual to M2, shrunk to pooled M2 (individuals with repeat nights only)

Primary: next-step climb class from native GPS height above MSL (no test-session centering),
 with two consecutive GPS intervals each 15..75 seconds. Threshold = 0.5 m/s.
 Exposures use only previous step (t-2,t-1) and wind at t-1; target is t-1->t.
 Leave one BatDay x animal session out. Pseudocount strengths fixed in model functions.
 All scores weighted session equally then biological individual equally, not per-fix pseudo-replicated.
 Environment term W.Component is an estimated component, not direct contemporaneous measurement.

Source preflight is exploratory, and the Tadarida archive has been repeatedly analysed elsewhere;
 no claims of prospective or fully independent confirmatory evaluation are made here.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
import csv
import hashlib
import json
import math
import numpy as np

SOURCE_URL = 'https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content'
SOURCE_EXPECTED_SIZE = 3630088
SOURCE_EXPECTED_MD5 = 'e0f6faedfd1f21bac222d9da430ea5d8'
SOURCE_EXPECTED_ROWS = 9873
PRIMARY_SPEED_THRESHOLD = .5
PRIMARY_WIND_THRESHOLD = .05
DT_MIN,DT_MAX = 15.,75.
MIN_TRIPLES = 30
N_CLASSES = 3


def numeric(s):
    try:
        x=float(s)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def bin3(x, threshold):
    return 0 if x < -threshold else 2 if x > threshold else 1


def data_to_sessions(csv_bytes, speed_threshold=.5, wind_threshold=.05):
    from io import StringIO
    rows=list(csv.DictReader(StringIO(csv_bytes.decode('utf-8-sig'))))
    by_session=defaultdict(list)
    for r in rows:
        iid=(r.get('animal-id') or '').strip()
        day=(r.get('BatDay') or '').strip()
        z=numeric(r.get('height-above-msl'))
        wind=numeric(r.get('W.Component'))
        if not iid or not day or z is None or wind is None:
            continue
        try:
            time=datetime.fromisoformat(r['timestamp'].strip()).timestamp()
        except (ValueError, TypeError, KeyError):
            continue
        by_session[(iid,day)].append((time,z,wind,r.get('location-long'),r.get('location-lat')))
    counts={}
    meta={}
    for (iid,day),pts in by_session.items():
        pts.sort(key=lambda o:o[0])
        counts3=np.zeros((3,3,3),dtype=np.int64)
        pairs=0
        for a,b,c in zip(pts[:-2],pts[1:-1],pts[2:]):
            dt0=b[0]-a[0];dt1=c[0]-b[0]
            if not (DT_MIN<=dt0<=DT_MAX and DT_MIN<=dt1<=DT_MAX):
                continue
            p=bin3((b[1]-a[1])/dt0,speed_threshold)
            w=bin3(b[2],wind_threshold)
            y=bin3((c[1]-b[1])/dt1,speed_threshold)
            counts3[p,w,y]+=1
            pairs+=1
        if pairs>=MIN_TRIPLES:
            key=f'{iid}::{day}'
            counts[key]=counts3
            meta[key]={'id':iid,'session':day,'n':pairs,'first_ts':pts[0][0],'last_ts':pts[-1][0]}
    return counts,meta,{'source_rows':len(rows),'candidate_sessions':len(by_session),'included_sessions':len(counts),'included_triplets':int(sum(x.sum() for x in counts.values()))}


def probs_from_counts(c):
    """Cooled conditional transition distributions with predeclared empirical-Bayes constants."""
    c=np.asarray(c,dtype=float)
    marg=c.sum(axis=(0,1))
    p0=(marg+.5)/(marg.sum()+1.5)
    prev=c.sum(axis=1)  # prev, target
    p1=(prev+12*p0[None,:])/(prev.sum(axis=1,keepdims=True)+12)
    p2=(c+20*p1[:,None,:])/(c.sum(axis=2,keepdims=True)+20)
    return p0,p1,p2


def score_session(target,p0,p1,p2,personal=None):
    tr=np.asarray(target,dtype=float)
    n=tr.sum()
    # counts shape (prev=3,wind=3,next=3)
    base=np.broadcast_to(p0[None,None,:],tr.shape)
    inertia=np.broadcast_to(p1[:,None,:],tr.shape)
    res={'M0':float((tr*np.log(base)).sum()/n), 'M1':float((tr*np.log(inertia)).sum()/n), 'M2':float((tr*np.log(p2)).sum()/n)}
    if personal is not None:
        cp=np.asarray(personal,dtype=float)
        p3=(cp+30*p2)/(cp.sum(axis=2,keepdims=True)+30)
        res['M3']=float((tr*np.log(p3)).sum()/n)
    return res


def summarize_session_scores(per_session,meta):
    inds=defaultdict(list)
    for key,sc in per_session.items():
        inds[meta[key]['id']].append(sc)
    per_ind={}
    for iid,rows in inds.items():
        per_ind[iid]={k:float(np.mean([r[k] for r in rows if k in r])) for k in ('M0','M1','M2','M3') if any(k in r for r in rows)}
        per_ind[iid]['sessions']=len(rows)
    summary={k:float(np.mean([x[k] for x in per_ind.values() if k in x])) for k in ('M0','M1','M2','M3') if any(k in x for x in per_ind.values())}
    return summary,per_ind


def loo(counts,meta,labels=None,exclude_individual=False):
    keys=sorted(counts)
    if labels is None:labels={k:meta[k]['id'] for k in keys}
    per_session={}
    for k in keys:
        lab=labels[k]
        keep=[j for j in keys if j!=k and (not exclude_individual or labels[j]!=lab)]
        if not keep: continue
        ctrain=sum((counts[j] for j in keep), np.zeros((3,3,3),int))
        p0,p1,p2=probs_from_counts(ctrain)
        self_keys=[j for j in keep if labels[j]==lab]
        cp=sum((counts[j] for j in self_keys), np.zeros((3,3,3),int)) if self_keys and not exclude_individual else None
        per_session[k]=score_session(counts[k],p0,p1,p2,cp)
    summary,per_ind=summarize_session_scores(per_session,meta)
    personal_ids=[v for v in per_ind.values() if 'M3' in v]
    # M3-vs-M2 must be compared on identical evaluable biological individuals.
    excess=float(np.mean([v['M3']-v['M2'] for v in personal_ids])) if personal_ids else None
    return {'summary':summary,'per_individual':per_ind,'repeat_individual_count':len(personal_ids),'personal_excess':excess,
            'n_sessions':len(per_session)}


def run_dataset(data,nperm=199,seed=20261026,threshold=.5,wind_threshold=.05):
    counts,meta,source=data_to_sessions(data,threshold,wind_threshold)
    ids=sorted(set(x['id'] for x in meta.values()))
    if len(ids)<2:raise RuntimeError('Need at least two individuals with eligible sessions')
    sessions_result=loo(counts,meta)
    unseen=loo(counts,meta,exclude_individual=True)
    keys=sorted(counts)
    rng=np.random.default_rng(seed)
    orig=[meta[k]['id'] for k in keys]
    null=[]
    for _ in range(nperm):
        labs=dict(zip(keys,rng.permutation(orig)))
        score=loo(counts,meta,labels=labs)['personal_excess']
        if score is not None:null.append(score)
    obs=sessions_result['personal_excess']
    p=float((1+sum(x>=obs for x in null))/(1+len(null))) if obs is not None and null else None
    return {'source_summary':source,'n_individuals':len(ids),'primary_speed_threshold_m_s':threshold,
            'wind_bin_threshold_m_s':wind_threshold,'time_gap_s':[DT_MIN,DT_MAX],
            'session_holdout':sessions_result,'new_individual_holdout':unseen,
            'permutation':{'n':len(null),'seed':seed,'unit':'whole BatDay sessions','null_mean':float(np.mean(null)) if null else None,'null_sd':float(np.std(null)) if null else None,'p_ge_obs':p},
            'caution':'Exploratory new predictive endpoint applied to source already analysed for other purposes. This is NOT a social-Boids coefficient fit.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--csv',type=Path)
    ap.add_argument('--download',action='store_true')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--permutations',type=int,default=199)
    ap.add_argument('--sensitivity',action='store_true')
    args=ap.parse_args()
    if args.csv:
        data=args.csv.read_bytes()
    elif args.download:
        data=urlopen(Request(SOURCE_URL,headers={'User-Agent':'boids3d-empirical-v4/1.0'}),timeout=90).read()
        if len(data)!=SOURCE_EXPECTED_SIZE or hashlib.md5(data).hexdigest()!=SOURCE_EXPECTED_MD5:
            raise RuntimeError('Archived data checksum/size changed; abort without analysis')
    else:
        ap.error('Pass --csv FILE or --download')
    result=run_dataset(data,args.permutations)
    result['source']={'doi':'10.5441/001/1.52nn82r9','byte_count':len(data),'md5':hashlib.md5(data).hexdigest(),
                      'expected_verified':len(data)==SOURCE_EXPECTED_SIZE and hashlib.md5(data).hexdigest()==SOURCE_EXPECTED_MD5}
    if args.sensitivity:
        result['sensitivity']={f'speed={sp},wind={wp}':run_dataset(data,0,threshold=sp,wind_threshold=wp) for sp,wp in [(1.,.05),(.5,.15)]}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('source_summary','n_individuals','permutation')},indent=2))
    print('session_holdout',result['session_holdout']['summary'])
    print('unseen_individual',result['new_individual_holdout']['summary'])

if __name__=='__main__':
    main()
