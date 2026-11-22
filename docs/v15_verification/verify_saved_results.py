"""Independently verify complete v15 outputs without importing or running a simulation.

From any directory, pass the folder of completed outputs and the repository
whose computational sources generated them. For example:

    python verify_saved_results.py /path/to/results --repo-root /path/to/boids
"""
import argparse
import csv
from hashlib import sha256
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[2] / 'boids'
SEEDS = np.arange(2000, 2096)
ARMS = [f'{panel}__{mask:03b}' for panel, masks in [('intact', range(8)), ('motor_cut', (0, 3, 4, 7))] for mask in masks]
SOURCES = ['source__none', 'source__pulse']
FIELDS = ['call_fraction', 'hull_area', 'cue', 'snapshot_pos', 'snapshot_velocity', 'snapshot_calling']
TERMS = {'X': 4, 'V': 2, 'C': 1, 'XV': 6, 'XC': 5, 'VC': 3, 'XVC': 7}
WINDOWS = {'immediate': (1040, 1240), 'primary': (1040, 4040), 'late': (5000, 6000)}
SOURCE_PATHS = ['docs/V15_STATE_TRANSPLANT_PROTOCOL.md', 'validation_fish_boids_v14/simulation.py',
                *['validation_fish_boids_v15/' + p for p in ('analysis.py', 'simulation.py', 'run_audit.py')]]


def check(test, reason):
    if not test:
        raise ValueError(reason)


def digest(path):
    with path.open('rb') as f:
        h = sha256()
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
        return h.hexdigest()


def compare(saved, expected, name='result'):
    if isinstance(expected, dict):
        check(isinstance(saved, dict) and set(saved) == set(expected), f'{name} keys')
        for k, v in expected.items():
            compare(saved[k], v, f'{name}/{k}')
    elif isinstance(expected, list):
        check(isinstance(saved, list) and len(saved) == len(expected), f'{name} length')
        for i, v in enumerate(expected):
            compare(saved[i], v, f'{name}/{i}')
    elif isinstance(expected, (float, np.floating)):
        check(type(saved) in (float, int) and np.isfinite(saved)
              and np.isclose(saved, expected, rtol=5e-13, atol=0),
              f'{name}: expected {expected!r}, found {saved!r}')
    elif isinstance(expected, (np.integer, int)) and not isinstance(expected, bool):
        check(type(saved) is int and saved == expected, f'{name}: expected integer {expected}, found {saved}')
    else:
        check(type(saved) is type(expected) and saved == expected, f'{name}: {saved!r} != {expected!r}')


def raw_manifest(a):
    manifest = {'seeds', 'source_snapshot_steps', 'continuation_snapshot_steps', 'continuation_offset',
                'split_rng_state_json', 'end_rng_state_json'}
    check(set(a) == manifest | {f'{label}__{f}' for label in SOURCES + ARMS for f in FIELDS}, 'raw keys')
    for key, v in [('seeds', SEEDS), ('source_snapshot_steps', [1000, 1040]),
                   ('continuation_snapshot_steps', [1040, 1240, 4040, 6000]), ('continuation_offset', 1040)]:
        check(a[key].dtype.kind in 'iu' and np.array_equal(a[key], v), key)
    for key in ('split_rng_state_json', 'end_rng_state_json'):
        check(a[key].shape == (96,) and a[key].dtype.kind == 'U', key)
    for label in SOURCES + ARMS:
        pre = label in SOURCES
        length = 1040 if pre else 4960
        snap = a['source_snapshot_steps' if pre else 'continuation_snapshot_steps']
        v = {f: a[f'{label}__{f}'] for f in FIELDS}
        for f in FIELDS:
            shape = ((96, length) if f in FIELDS[:3] else
                     (96, len(snap), 32) if f == 'snapshot_calling' else (96, len(snap), 32, 2))
            check(v[f].shape == shape and v[f].dtype == np.float64 and np.isfinite(v[f]).all(), f'{label}/{f}')
        counts = v['call_fraction'] * 32
        check(((counts >= 0) & (counts <= 32) & (counts == counts.astype(int))).all(), label + ' count grid')
        check((v['hull_area'] > 0).all() and np.isin(v['snapshot_calling'], [0, 1]).all(), label + ' physical bounds')
        cue = np.zeros(length)
        if label == 'source__pulse':
            cue[1000:] = .8
        check((v['cue'] == cue).all(), label + ' cue schedule')
        for j, step in enumerate(snap):
            index = step - (0 if pre else 1040) - 1
            if index >= 0:
                check(np.array_equal(v['snapshot_calling'][:, j].sum(axis=1), counts[:, index]), label + ' snapshot calls')
                actual = [ConvexHull(pos).volume for pos in v['snapshot_pos'][:, j]]
                check(np.array_equal(actual, v['hull_area'][:, index]), label + ' hull')
        if not pre:
            mask = int(label.split('__')[1], 2)
            for field, bit in [('snapshot_pos', 4), ('snapshot_velocity', 2), ('snapshot_calling', 1)]:
                src = SOURCES[int(bool(mask & bit))]
                check(np.array_equal(v[field][:, 0], a[src + '__' + field][:, -1]), label + '/' + field + ' donor')
    for field in FIELDS:
        left, right = [a[s + '__' + field] for s in SOURCES]
        end = 1000 if field in FIELDS[:3] else 1
        check(np.array_equal(left[:, :end], right[:, :end]), 'pre-pulse pairing ' + field)
    for mask in (0, 1, 4, 5):
        check(np.array_equal(a[f'intact__{mask:03b}__call_fraction'][:, 0],
                             a[f'intact__{mask + 2:03b}__call_fraction'][:, 0]), 'first-call velocity invariance')
    for i, seed in enumerate(SEEDS):
        rng = np.random.Generator(np.random.PCG64(int(seed)))
        rng.normal(size=(32, 2))
        rng.uniform(-np.pi, np.pi, size=32)
        rng.binomial(1, .08, size=32)
        for key, steps in [('split_rng_state_json', 1040), ('end_rng_state_json', 4960)]:
            rng.random((steps, 32))
            check(json.loads(str(a[key][i])) == rng.bit_generator.state, f'{seed}/{key}')


def factorial(c):
    # Direct Möbius inclusion-exclusion and six permutations of marginal allocations.
    mob = {name: sum((-1) ** (mask.bit_count() - sub.bit_count()) * c[:, sub]
                     for sub in range(8) if sub & mask == sub) for name, mask in TERMS.items()}
    sixth = {}
    for k in 'XVC':
        bit = TERMS[k]
        num = np.zeros(len(c), dtype=np.int64)
        for order in itertools.permutations((4, 2, 1)):
            before = sum(order[:order.index(bit)])
            num += c[:, before | bit] - c[:, before]
        sixth[k] = num
    check(np.array_equal(sum(mob.values()), c[:, 7] - c[:, 0]), 'Möbius integer closure')
    check(np.array_equal(sum(sixth.values()), 6 * (c[:, 7] - c[:, 0])), 'Shapley integer closure')
    return {'mobius': {k: v/96000 for k, v in mob.items()}, 'shapley': {k: v/576000 for k, v in sixth.items()},
            'shapley_X_minus_C': (sixth['X'] - sixth['C'])/576000}


def contrasts(x, scale):
    out = {}
    for name, plus, minus in [('natural_history', 7, 0), ('X_insertion', 4, 0), ('X_deletion', 7, 3)]:
        d = {p: x[f'{p}__{plus:03b}'] - x[f'{p}__{minus:03b}'] for p in ('intact', 'motor_cut')}
        out[name if name == 'natural_history' else name+'_intact'] = d['intact']/scale
        out[name+'_motor_cut'] = d['motor_cut']/scale
        did = 'total' if name == 'natural_history' else name
        out['motor_DID_'+did] = (d['motor_cut'] - d['intact'])/scale
    return out


def summary(v, ix, draws, arm=False):
    x = np.asarray(v)[ix]
    count = len(x)
    ci = None
    if count >= 2:
        sample = np.sort(x[draws].mean(axis=1))
        # Independent linear interpolation between the known percentile ranks.
        ci = [float(np.interp(p*(len(sample)-1), np.arange(len(sample)), sample)) for p in (.025, .975)]
    s = {'n': count, 'mean': float(x.mean()) if count else None,
         'median': float(np.median(x)) if count else None, 'ci95': ci}
    if arm:
        return s
    pos = sorted([i for i in range(count) if x[i] > 0], key=lambda i: (-x[i], i))
    denominator = np.sum(x[x>0], dtype=float)
    top = pos[:2]
    s.update(positive=len(pos), zero=int(np.sum(x==0)), negative=int(np.sum(x<0)), positive_concentration={
        'top_two_indices': top, 'top_two_seeds': [int(SEEDS[ix[i]]) for i in top],
        'positive_total': float(denominator), 'top_two_share': float(sum(x[i] for i in top)/denominator) if pos else None,
        'largest_share': float(x[top[0]]/denominator) if pos else None})
    return s


def arrival(hits):
    if hits.size:
        latency = int(hits[0]) + 200
        return (1040+latency, True, False, latency)
    return (None, False, True, 4960)


def csv_check(path, expected_rows, identifiers):
    pending = {tuple(r[k] for k in identifiers):r for r in expected_rows}
    check(len(pending) == len(expected_rows), 'oracle duplicate CSV keys')
    with path.open(newline='') as f:
        rows = csv.DictReader(f)
        check(set(rows.fieldnames) == set(expected_rows[0]), path.name + ' columns')
        for row in rows:
            key = tuple(int(row[k]) if k == 'seed' else float(row[k]) if k == 'threshold' else row[k] for k in identifiers)
            check(key in pending, f'{path.name}: unknown/duplicate {key}')
            for col, value in pending.pop(key).items():
                if isinstance(value, (float, np.floating)):
                    check(float(row[col]) == value, f'{path.name} {key} {col}: {row[col]} != {value}')
                else:
                    check(row[col] == ('' if value is None else str(value)), f'{path.name} {key} {col}')
    check(not pending, path.name + ' missing rows')


def computed(a):
    baseline_counts=(a['source__none__call_fraction'][:,800:1000]*32).astype(int).sum(axis=1)
    low=100*baseline_counts < 90*32*200
    ix={'all': np.arange(96), 'baseline_low': np.flatnonzero(low)}
    boot={k: np.random.Generator(np.random.PCG64(2026112205)).integers(len(v), size=(10000,len(v)))
          if len(v) else np.empty((10000,0),dtype=int) for k,v in ix.items()}
    out={'cohorts':{k:{'indices':v.tolist(),'seeds':SEEDS[v].tolist(),'n':len(v)} for k,v in ix.items()},
         'windows':{}, 'arrivals':{}}
    def identity(i):
        return {'seed':int(SEEDS[i]), 'baseline_low': bool(low[i])}
    win_rows, fx_rows, arr_rows = [], [], []
    for window,(start,end) in WINDOWS.items():
        outcomes={k:{} for k in ix}
        out['windows'][window]={'steps':[start,end], 'cohorts':outcomes}
        for metric in ('call_fraction','hull_area'):
            traces={arm:a[arm+'__'+metric][:,start-1040:end-1040] for arm in ARMS}
            if metric=='call_fraction':
                scale=(end-start)*32
                raw={arm:(v*32).astype(np.int64).sum(axis=1) for arm,v in traces.items()}
            else:
                scale=1
                raw={arm:v.mean(axis=1) for arm,v in traces.items()}
            arms={arm:v/scale for arm,v in raw.items()}
            terms=contrasts(raw,scale)
            for arm,x in arms.items():
                win_rows.extend({**identity(i), 'window':window, 'start':start, 'end':end, 'arm':arm,
                                 'metric':metric, 'value':float(v)} for i,v in enumerate(x))
            primary=window=='primary' and metric=='call_fraction'
            if primary:
                allotted=factorial(np.column_stack([raw[arm] for arm in ARMS[:8]]))
                effects={**terms, **{kind+'_'+k:v for kind in ('mobius','shapley') for k,v in allotted[kind].items()},
                         'shapley_X_minus_C':allotted['shapley_X_minus_C']}
                for name,x in effects.items():
                    fx_rows.extend({**identity(i),'effect':name,'value':float(v)} for i,v in enumerate(x))
            for k,v in ix.items():
                section={'arms':{arm:summary(x,v,boot[k],True) for arm,x in arms.items()},
                         'contrasts':{t:summary(x,v,boot[k]) for t,x in terms.items()}}
                if primary:
                    d={kind:{t:summary(x,v,boot[k]) for t,x in allotted[kind].items()} for kind in ('mobius','shapley')}
                    for kind in ('mobius','shapley'):
                        err=sum(allotted[kind].values())-terms['natural_history']
                        d['max_'+kind+'_closure_error']=float(np.max(np.abs(err[v]))) if len(v) else None
                    d['shapley_X_minus_C']=summary(allotted['shapley_X_minus_C'],v,boot[k])
                    section['decomposition']=d
                outcomes[k][metric]=section
    for percent in (80,90,95):
        events,latency={},{}
        for arm in ARMS:
            traces=(a[arm+'__call_fraction']*32).astype(np.int64)
            # Integer convolution is independent of the production prefix-sum method.
            recs=[arrival(np.flatnonzero(np.convolve(row,np.ones(200,dtype=np.int64),'valid')>=64*percent)) for row in traces]
            events[arm]=np.array([r[1] for r in recs]); latency[arm]=np.array([r[3] for r in recs])
            for i,(time,event,censored,restricted) in enumerate(recs):
                arr_rows.append({**identity(i),'arm':arm,'threshold':percent/100,'confirmation_step':time,
                                 'event_observed':event,'censored':censored,'restricted_latency':restricted})
        out['arrivals'][str(percent/100)]={'cohorts':{
            k:{'arms':{arm:{'n':len(v),'events':int(events[arm][v].sum()),'censored':int((~events[arm][v]).sum()),
                          'mean_restricted_latency':float(latency[arm][v].mean()) if len(v) else None}
                       for arm in ARMS},
               'natural_latency_contrast':summary(latency['intact__111']-latency['intact__000'],v,boot[k])}
            for k,v in ix.items()}}
    return out, (win_rows, fx_rows, arr_rows)


def verify(directory, repo_root=ROOT):
    load=lambda name: json.loads((directory/name).read_text())
    saved=load('summary.json')
    check(saved==load('audit_result.json'),'aggregate files disagree')
    receipt=load('trace_receipt.json')
    trace=directory/'full_traces.npz'
    compare(receipt,{'file':trace.name,'sha256':digest(trace),'bytes':trace.stat().st_size},'archive receipt')
    sources={path:digest(repo_root/path) for path in SOURCE_PATHS}
    check(sources['docs/V15_STATE_TRANSPLANT_PROTOCOL.md']=='9d430a88cf2f99d5be8113344343a243f482726ef31471f6286a5e0fbfa572f2','frozen protocol')
    check(sources['validation_fish_boids_v14/simulation.py']=='9ef61c7a92e4ae5ea98472e00e25b48751103fb7e056100c514af8c576acfb46','frozen v14 reference')
    check(sources['validation_fish_boids_v15/run_audit.py']=='edf36d73cba0b55a96844dc841cb9bdff3c9e6c6f30b4aa6f4683683a41689d4','frozen runner')
    check(sources['validation_fish_boids_v15/analysis.py']=='c371928539d2e826c05d35b094df1ef969e9fa8ce09b9680a650b5e1359c626c','frozen analysis')
    check(sources['validation_fish_boids_v15/simulation.py']=='a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb','frozen simulator')
    with np.load(trace, allow_pickle=False) as data:
        check(len(data.files)==len(set(data.files)),'duplicate NPZ keys')
        arrays={k:data[k] for k in data.files}
    raw_manifest(arrays)
    stats,csvs=computed(arrays)
    wanted={'version':'v15_state_transplant','status':'SYNTHETIC_ONLY_NOT_FIELD_RESULT',
            'protocol_commit':'3fcbdfc157ca362cad4560bf3b2400ec4ee7e7e0','predecessor_commit':'7295d885b587d808cb74fbae11163819ed8cf22d',
            'seeds':SEEDS.tolist(),'n':32,'split_step':1040,'steps':6000,'source_histories':192,'trajectories':1152,
            'primary_window':[1040,4040],'bootstrap':{'replicates':10000,'seed':2026112205,'unit':'paired simulator seed',
            'interval':'percentile95%, descriptive and unadjusted'},'runtime':saved['runtime'],
            'source_sha256':sources, 'source_hashes_captured_before_execution_and_verified_after':True,
            'validations':{**{k:True for k in ('exact_schema','integer_call_counts','snapshot_consistency','component_provenance',
            'pre_pulse_pairing','first_call_V_invariance','common_rng_at_split_and_end')},'exact_v14_natural_seed_pairs':96},
            'trace_receipt':receipt, **stats}
    check(set(saved['runtime'])=={'numpy','scipy','python'} and saved['runtime']['python'].startswith('3.12.')
          and saved['runtime']['numpy']=='2.3.5' and saved['runtime']['scipy']=='1.17.0','pinned runtime')
    compare(saved,wanted)
    for entries,name,keys in zip(csvs,['per_seed_windows','per_seed_effects','arrival_records'],
                                 [('seed','metric','window','arm'),('seed','effect'),('seed','arm','threshold')]):
        csv_check(directory/(name+'.csv'),entries,keys)
    return {'verdict':'verified','receipt':receipt,'csv_rows':list(map(len,csvs)),
            'baseline_low':stats['cohorts']['baseline_low'],'primary':stats['windows']['primary']['cohorts']['all']['call_fraction']['contrasts']['natural_history']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('completed_directory', type=Path, help='directory containing the complete JSON, NPZ and CSV outputs')
    parser.add_argument('--repo-root', type=Path, default=ROOT,
                        help='Boids repository root containing the frozen protocol and computational sources')
    args=parser.parse_args()
    print(json.dumps(verify(args.completed_directory, args.repo_root),indent=2))
