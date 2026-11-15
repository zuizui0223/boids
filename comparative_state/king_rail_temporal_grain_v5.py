#!/usr/bin/env python3
"""King Rail, within-one-dataset decision-time vs lagged-environment prediction.

Exploratory post-original-outcome test. Source: original Zenodo 6604660
Brewer et al., Ecology and Evolution, 2023, DOI 10.1002/ece3.10043.
No row-heldout pseudo replication; only train-first, test-later bird series.
This is conditional prediction of used *depth* with retrospective measured
random-plot availability, NOT a movement forecast or portfolio-exhaustion test.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics as st
import urllib.request
from collections import defaultdict
from pathlib import Path
from random import Random

SOURCE_RECORD = '6604660'
SOURCE_FILE = 'CARTdataset_12.31.21_All_D.csv'
ZENODO_API = 'https://zenodo.org/api/records/' + SOURCE_RECORD
ID_RE = re.compile(r'^(\d+)\.(\d+)(H|R)(\d+)(?:_(\d+))?_(\d{2})$')
SEED = 20261115


def source_bytes():
    meta_req = urllib.request.Request(ZENODO_API, headers={'User-Agent': 'king-rail-temporal-grain-v5/1.0'})
    with urllib.request.urlopen(meta_req, timeout=90) as h:
        meta = json.loads(h.read(2_000_000))
    files = [f for f in meta.get('files', []) if f.get('key') == SOURCE_FILE]
    if len(files) != 1:
        raise ValueError('SOURCE_STOP: original Zenodo file not uniquely identified')
    f = files[0]
    url = f.get('links', {}).get('self') or f.get('links', {}).get('content')
    if not url or not url.startswith('https://zenodo.org/'):
        raise ValueError('SOURCE_STOP: not official original Zenodo download')
    expected = str(f.get('checksum', '')).lower()
    if not expected.startswith('md5:') or len(expected) != 36:
        raise ValueError('SOURCE_STOP: source MD5 not verified in official metadata')
    req = urllib.request.Request(url, headers={'User-Agent': 'king-rail-temporal-grain-v5/1.0'})
    with urllib.request.urlopen(req, timeout=120) as h:
        raw = h.read(10_000_001)
    if len(raw) > 10_000_000:
        raise ValueError('SOURCE_STOP: original file exceeds registered byte limit')
    observed_md5 = hashlib.md5(raw).hexdigest()
    if expected != 'md5:' + observed_md5:
        raise ValueError('SOURCE_STOP: original-file MD5 does not match Zenodo metadata')
    return raw, {'doi':'10.5281/zenodo.6604660','filename':SOURCE_FILE,
                 'original_file_md5':observed_md5,'original_file_sha256':hashlib.sha256(raw).hexdigest(),
                 'file_bytes':len(raw)}


def build_events(rows):
    events = {}
    qc = {'source_rows':len(rows),'missing_yes_excluded':0,'malformed_ID_excluded':0,
          'invalid_depth_or_date_excluded':0}
    for row in rows:
        if (row.get('Missing') or '').strip().lower() == 'yes':
            qc['missing_yes_excluded'] += 1
            continue
        match = ID_RE.fullmatch((row.get('ID') or '').strip())
        if not match:
            qc['malformed_ID_excluded'] += 1
            continue
        try:
            depth = float(row['WaterDepth'])
            year = int(float(row['Year']))
            julian = int(float(row['Julian']))
        except (ValueError, KeyError, TypeError):
            qc['invalid_depth_or_date_excluded'] += 1
            continue
        if not math.isfinite(depth) or not 1 <= julian <= 366:
            qc['invalid_depth_or_date_excluded'] += 1
            continue
        bird = f'{match.group(2)}_{match.group(6)}'
        eid = (bird, int(match.group(4)))
        x = events.setdefault(eid, {'id':eid,'bird':bird,'prefix':match.group(2),
                                    'used':[],'random':[], 'used_dates':[], 'random_dates':[]})
        kind = 'used' if match.group(3) == 'H' else 'random'
        x[kind].append(depth)
        x['used_dates' if kind == 'used' else 'random_dates'].append((year,julian))
    bybird = defaultdict(list)
    discarded = 0
    for e in events.values():
        if len(e['used']) != 1 or not e['random'] or len(set(e['used_dates'])) != 1:
            discarded += 1
            continue
        year, julian = e['used_dates'][0]
        bybird[e['bird']].append({'bird':e['bird'],'prefix':e['prefix'],
               'event':e['id'][1],'year':year,'julian':julian,
               'A':st.mean(e['random']),'U':e['used'][0],
               'random_count':len(e['random'])})
    for events_b in bybird.values():
        events_b.sort(key=lambda e:(e['year'],e['julian'],e['event']))
    qc.update({'matched_bird_years':len(bybird),
               'distinct_prefix_tokens':len({x.split('_')[0] for x in bybird}),
               'valid_matched_events':sum(map(len,bybird.values())),
               'unmatched_event_groups':discarded,
               'valid_events_with_two_random_plots':sum(e['random_count']==2 for ev in bybird.values() for e in ev)})
    return dict(bybird),qc


def chronological_split(events_b):
    days = sorted({(e['year'],e['julian']) for e in events_b})
    # Date-block split; prevents events on same date landing in both sets.
    k = math.floor(0.6 * len(days))
    if k < 4 or len(days)-k < 3:
        return None
    train_dates = set(days[:k])
    tr = [e for e in events_b if (e['year'],e['julian']) in train_dates]
    te = [e for e in events_b if (e['year'],e['julian']) not in train_dates]
    if len(tr)<5 or len(te)<3:
        return None
    return tr,te


def center_slope(train_by_bird):
    num=den=0.0
    for group in train_by_bird.values():
        ma=st.mean(x['A'] for x in group)
        mu=st.mean(x['U'] for x in group)
        for e in group:
            a=e['A']-ma; u=e['U']-mu
            num+=a*u
            den+=a*a
    if den<=1e-9:raise ValueError('SOURCE_STOP: insufficient independent training availability variance')
    return num/den


def score_single(focal_bird, split, other_train, *, coarsen=3):
    tr, te = split
    b = center_slope(other_train)
    ref_u = st.mean(e['U'] for e in tr)
    ref_a = st.mean(e['A'] for e in tr)
    pooled_u = st.mean(e['U'] for x in other_train.values() for e in x)
    pooled_a = st.mean(e['A'] for x in other_train.values() for e in x)
    # Training-date mean availability history (state of the environment, not used outcomes).
    daily_history=[]
    for day in sorted({(e['year'],e['julian']) for e in tr}):
        daily_history.append(st.mean(e['A'] for e in tr if (e['year'],e['julian'])==day))
    rows=[]
    tests = defaultdict(list)
    for e in te:
        tests[(e['year'],e['julian'])].append(e)
    for day in sorted(tests):
        lag_a = st.mean(daily_history[-coarsen:])
        for e in tests[day]:
            rows.append({'date':day,'observed_used':e['U'], 'current_a':e['A'],
                         'lag_a':lag_a,'history_only':ref_u,
                         'lag_3_dates':ref_u+b*(lag_a-ref_a),
                         'current_event':ref_u+b*(e['A']-ref_a),
                         'other_bird_current':pooled_u+b*(e['A']-pooled_a)})
        daily_history.append(st.mean(e['A'] for e in tests[day]))
    if not rows:raise ValueError('SOURCE_STOP: no heldout events')
    def mse(name):return st.mean((r['observed_used']-r[name])**2 for r in rows)
    def mae(name):return st.mean(abs(r['observed_used']-r[name]) for r in rows)
    return {'bird':focal_bird,'prefix':tr[0]['prefix'],'n_train':len(tr),'n_test':len(te),
            'unique_train_dates':len({(e['year'],e['julian']) for e in tr}),
            'unique_test_dates':len({(e['year'],e['julian']) for e in te}),
            'other_bird_training_slope':b,
            'mse_cm2':{m:mse(m) for m in ('history_only','lag_3_dates','current_event','other_bird_current')},
            'mae_cm':{m:mae(m) for m in ('history_only','lag_3_dates','current_event','other_bird_current')},
            'current_a':[r['current_a'] for r in rows],
            'test_u':[r['observed_used'] for r in rows],
            'train_u_mean':ref_u,'train_a_mean':ref_a,
            'gain_event_over_lag':mse('lag_3_dates')-mse('current_event'),
            'gain_event_over_self':mse('history_only')-mse('current_event'),
            'gain_self_over_other':mse('other_bird_current')-mse('current_event')}


def boot_equal_cluster(indiv, key, *, reps=10000, seed=SEED, collapse_prefix=False):
    rng=Random(seed)
    if collapse_prefix:
        d=defaultdict(list)
        for s in indiv:d[s['prefix']].append(s[key])
        groups=[st.mean(v) for v in d.values()]
    else:
        groups=[s[key] for s in indiv]
    obs=st.mean(groups)
    null=[]
    for _ in range(reps):
        sample=[rng.choice(groups) for j in groups]
        null.append(st.mean(sample))
    null.sort()
    return {'mean':obs,'ci95':[null[int(.025*len(null))],null[int(.975*len(null))]],
            'n_groups':len(groups),'positive_groups':sum(x>0 for x in groups)}


def test_circular_shift(indiv, *, reps=3999, seed=SEED):
    """Question whether event-matched A predicts U better than shifted A (same target)."""
    rng=Random(seed)
    observed=st.mean(s['mse_cm2']['current_event'] for s in indiv)
    null=[]
    for _ in range(reps):
        mses=[]
        for s in indiv:
            A=s['current_a']; n=len(A)
            shift=rng.randrange(1,n)
            b=s['other_bird_training_slope']
            u0=s['train_u_mean']; a0=s['train_a_mean']
            mses.append(st.mean((u-(u0+b*(A[(k+shift)%n]-a0)))**2 for k,u in enumerate(s['test_u'])))
        null.append(st.mean(mses))
    return {'observed_event_mse':observed,'shifted_null_median_mse':st.median(null),
            'add_one_p_event_better_than_shift':(1+sum(v<=observed for v in null))/(reps+1),
            'n_rotations':reps,'caution':'Within-series circular-shift control, limited by heldout series length; not independent field replication'}


def evaluate(bybird, *, reps=10000):
    split={}
    excluded={}
    for bird, ev in sorted(bybird.items()):
        a=chronological_split(ev)
        if a is None:excluded[bird]='fewer than 4 training or 3 testing distinct dates, or insufficient events'
        else:split[bird]=a
    if len(split)<7:
        return {'status':'SOURCE_SCHEMA_STOP_INSUFFICIENT_CHRONOLOGICAL_BIRDS','eligible':len(split),'exclusions':excluded}
    scores=[]
    for bird, pair in sorted(split.items()):
        others={k:v[0] for k,v in split.items() if k!=bird}
        scores.append(score_single(bird,pair,others))
    ret={'status':'FIELD_COMPUTED_EXPLORATORY','eligible_bird_years':len(scores),
         'distinct_ID_prefixes':len({s['prefix'] for s in scores}),
         'all_source_events':sum(map(len,bybird.values())),
         'tested_events':sum(s['n_test'] for s in scores),
         'excluded_series':excluded,
         'pooled_model':'nine other bird-year training series only, whole-series exclusion',
         'history_model':'first 60% of unique dates per bird; no heldout U leakage',
         'time_model':'M0 personal train mean; Mlag previous 3 date mean A; Mevent matched A at current date; same U outcome',
         'per_series':[{k:v for k,v in s.items() if k not in ('current_a','test_u')} for s in scores]}
    ret['primary_event_over_lag']=boot_equal_cluster(scores,'gain_event_over_lag',reps=reps)
    ret['secondary_event_over_history']=boot_equal_cluster(scores,'gain_event_over_self',reps=reps,seed=SEED+1)
    ret['secondary_self_over_other']=boot_equal_cluster(scores,'gain_self_over_other',reps=reps,seed=SEED+2)
    ret['conservative_ID_prefix_cluster_event_over_lag']=boot_equal_cluster(scores,'gain_event_over_lag',reps=reps,seed=SEED+3,collapse_prefix=True)
    ret['date_alignment_shift_null']=test_circular_shift(scores)
    p=ret['primary_event_over_lag']
    ret['fixed_primary_gate']='PASS' if p['ci95'][0]>0 and p['positive_groups'] >= math.ceil(.7*len(scores)) else 'FAIL'
    ret['claim_limits']=['Original site-matched depth records reused after original state-buffering result: EXPLORATORY, not external replication',
                         'Outcomes are heldout measured depth, not prospective animal geographic movement trajectories',
                         'Contemporaneous random depth values are retrospectively observed within 72 hours, not remotely forecast covariates',
                         'Measured random 75-m habitat plots are conditioned on used location and not a complete accessible state portfolio',
                         'Same bird ID prefix across 2020/2021 has ambiguous identity; original paper reports no birds recaptured/observed across years',
                         'No causal effect of water depth, movement, niche differentiation, fitness or habitat-portfolio exhaustion inferred']
    return ret


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',default='comparative_state/results/king_rail_temporal_grain_v5.json')
    ap.add_argument('--bootstrap-reps',type=int,default=10000)
    args=ap.parse_args()
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    try:
        source,provenance=source_bytes()
        rows=list(csv.DictReader(io.StringIO(source.decode('utf-8-sig'))))
        bybird,qc=build_events(rows)
        if not (qc['source_rows']==607 and qc['valid_matched_events']==190 and qc['matched_bird_years']==10):
            raise ValueError('SOURCE_STOP: original row/event/bird-year QC differs from frozen louis record')
        result=evaluate(bybird,reps=args.bootstrap_reps)
        result.update({'schema':'boids.ecostate.king_rail_time_grain_v5','source':provenance,'qc':qc,
                       'analysis_class':'posthoc original-data within-study time-grain holdout'})
    except Exception as e:
        result={'schema':'boids.ecostate.king_rail_time_grain_v5','status':'SOURCE_STOP',
                'reason':str(e),'new_field_effect_calculated':False}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('KING_RAIL_V5',result['status'],result.get('fixed_primary_gate',''),
          result.get('reason',''), 'artifact',out)

if __name__=='__main__':
    main()
