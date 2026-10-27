#!/usr/bin/env python3
"""Offline v9 integrity/interpretation audit of the frozen observed pigeon v8 receipt.

This module DOES NOT refit v8, select new lags, contact the remote source, or
infer animal-specific Boids coefficients. All endpoint arithmetic is reproduced
from the immutable v8 held-out summary and its declared cluster weighting.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

DEFAULT_SOURCE = Path('validation_v8/results/pigeon_social_forecast_v8.json')
DEFAULT_DEST = Path('validation_v9/results/v8_consistency_audit_v9.json')
CONTRASTS = ('actual_vs_own', 'stale_vs_own', 'actual_vs_stale')
MODELS = ('own', 'real', 'stale')
EXPECTED_ORIGINAL_SHA256 = '509bd4748056ff952fed15c4a0155ed7bb17a6f80e959f8cfdeec461e24124b6'
EXPECTED_SOURCE_SHA256 = '959d6a9d277363e763aeabfb995f4d6b8d0a76675744126495d433b1b9b14ca0'
PRIMARY_B = 10000
PRIMARY_SEED = 20261026
TOL = 1e-11


def close(a, b, label, tolerance=TOL):
    if not np.isclose(float(a),float(b),rtol=0.,atol=tolerance):
        raise ValueError(f'STOP_V8_AGGREGATION_MISMATCH:{label}:{a}:{b}')


def validate_and_summarize(data: bytes, check_pinned_source: bool = True) -> dict:
    digest = hashlib.sha256(data).hexdigest()
    if check_pinned_source and digest != EXPECTED_ORIGINAL_SHA256:
        raise ValueError('STOP_V8_RECEIPT_CHANGED')
    r=json.loads(data)
    if r.get('status') != 'EXPLORATORY_PIGEON_PAIRED_FORECAST_V8':
        raise ValueError('STOP_V8_STATUS')
    if r.get('source_sha256') != EXPECTED_SOURCE_SHA256:
        raise ValueError('STOP_V8_PUBLIC_SOURCE_CHANGED')
    groups=r['per_component'];flights=r['per_flight']
    if not groups or len(groups)!=r['n_bird_components']:
        raise ValueError('STOP_V8_COMPONENTS_INCONSISTENT')
    if len(flights)!=r['n_paired_flights']:
        raise ValueError('STOP_V8_FLIGHT_COUNT_INCONSISTENT')
    groupnames=[x['component'] for x in groups]
    if len(set(groupnames))!=len(groupnames):
        raise ValueError('STOP_V8_DUPLICATED_COMPONENT')
    seen=set()
    for flight in flights:
        if flight['component'] not in groupnames:
            raise ValueError('STOP_V8_ORPHAN_FLIGHT')
        key=(flight['site'],flight['dyad'],flight['flight_release'])
        if key in seen:raise ValueError('STOP_V8_DUPLICATED_FLIGHT')
        seen.add(key)
        if flight['n_rows']<=0 or not all(math.isfinite(float(flight['mse'][m])) for m in MODELS):
            raise ValueError('STOP_V8_INVALID_FLIGHT_MSE')
    for g in groups:
        subset=[f['mse'] for f in flights if f['component']==g['component']]
        if len(subset)!=g['n_flights']:
            raise ValueError('STOP_V8_GROUP_FLIGHT_COUNT')
        for m in MODELS:
            close(np.mean([f[m] for f in subset]),g['mse'][m],f"{g['component']}-{m}")
        close(g['mse']['own']-g['mse']['real'],g['actual_vs_own'],'component_vs_own')
        close(g['mse']['own']-g['mse']['stale'],g['stale_vs_own'],'component_stale_vs_own')
        close(g['mse']['stale']-g['mse']['real'],g['actual_vs_stale'],'component_primary')
        if g['two_lateral_neighbor_kernels_training_condition'] is None or not math.isfinite(float(g['two_lateral_neighbor_kernels_training_condition'])):
            raise ValueError('STOP_V8_KERNEL_DIAGNOSTIC_MISSING')
    equal={m:float(np.mean([g['mse'][m] for g in groups])) for m in MODELS}
    for m in MODELS:close(equal[m],r['equal_independent_bird_component_mse'][m],f'pooled_{m}')
    matrix=np.array([[g[key] for key in CONTRASTS] for g in groups],float)
    gain={c:float(matrix[:,i].mean()) for i,c in enumerate(CONTRASTS)}
    for c in CONTRASTS:close(gain[c],r['equal_component_gain'][c],f'pooled_{c}')
    rng=np.random.default_rng(PRIMARY_SEED)
    picks=rng.integers(0,len(groups),size=(PRIMARY_B,len(groups)))
    boot=matrix[picks].mean(axis=1)
    intervals={c:[float(np.quantile(boot[:,i],.025)),float(np.quantile(boot[:,i],.975))] for i,c in enumerate(CONTRASTS)}
    for c in CONTRASTS:
        for a,b in zip(intervals[c],r['cluster_bootstrap95'][c]):close(a,b,f'boot_{c}')
    positives=int(np.sum(matrix[:,2]>0))
    if positives!=r['actual_better_than_stale_groups']:
        raise ValueError('STOP_V8_SIGN_MISMATCH')
    pvalue=sum(math.comb(len(groups),k) for k in range(positives,len(groups)+1))/2**len(groups)
    close(pvalue,r['exact_one_sided_sign_p'],'sign_test',1e-15)
    cond=np.array([g['two_lateral_neighbor_kernels_training_condition'] for g in groups])
    # Source receipt already fits the numerical diagnostic; these ranges are
    # descriptive only, not an independent test for causal Boids identifiability.
    return {
        'audit':'boids-v9-immutable-v8-receipt-arithmetic-and-boundary',
        'status':'PASS_FROZEN_RECEIPT_REPLAY_ONLY',
        'receipt_sha256':digest,
        'source_archive_sha256':r['source_sha256'],
        'n_bird_connected_components':len(groups),
        'n_paired_flights':len(flights),
        'equal_connected_component_mse':equal,
        'contrasts':gain,
        'cluster_bootstrap95':intervals,
        'positive_connected_groups':{c:int(np.sum(matrix[:,i]>0)) for i,c in enumerate(CONTRASTS)},
        'primary_exact_one_sided_sign_p':pvalue,
        'reported_primary_supported':bool(intervals['actual_vs_stale'][0]>0 and intervals['actual_vs_own'][0]>0),
        'two_lateral_kernel_condition_min':float(cond.min()),
        'two_lateral_kernel_condition_median':float(np.median(cond)),
        'two_lateral_kernel_condition_max':float(cond.max()),
        'two_lateral_kernel_condition_scope':'Only the two standardized lateral social columns in *training* design for each v8 held-out fold; not a full 14-column model condition and not evidence of physical-force recovery.',
        'relative_reduction_in_mse_actual_vs_own':(equal['own']-equal['real'])/equal['own'],
        'relative_reduction_in_mse_actual_vs_stale':(equal['stale']-equal['real'])/equal['stale'],
        'claim_boundary':[ 'Entire bird-connected group remains the biological inference unit; 197 flights and GPS records are not 197 independent replicates.', 'This is an arithmetic/provenance replication of a previous observed result, not an additional independent biological validation or new alternative model.', 'The predeclared current-vs-stale primary contrast remains unsupported; do not retune lags, smoothing or cohort selection to rescue it.', 'Condition number for two chosen regressors does not show that social forces or long-term 3D niches are identifiable.' ]
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,default=DEFAULT_SOURCE)
    p.add_argument('--out',type=Path,default=DEFAULT_DEST)
    args=p.parse_args()
    result=validate_and_summarize(args.input.read_bytes())
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
