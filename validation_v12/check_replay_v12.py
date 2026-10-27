#!/usr/bin/env python3
"""Reproduce all synthetic v12 JSON receipts, fail closed on discrepancy.

This reruns numerical known-truth generators. Success is algorithmic
reproducibility, NOT an independent animal or ecological validation.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from emergent_preferences import experiment as ecological_experiment, CONDITIONS
from species_partition_null import run as relabel_experiment
from social_influence_scan import scan
from grain_audit_v12 import experiment as grain_experiment
from crossover_audit_v12 import audit as crossing_audit
from audit_v12 import paired_seed_contrasts

RESULTS=Path('validation_v12/results')
FILES={
 'main':'endogenous_policy_v12.json',
 'family':'force_family_sensitivity_v12.json',
 'guild_null':'guild_relabel_null_v12.json',
 'coupling':'social_influence_scan_v12.json',
 'grain':'grain_audit_v12.json',
 'crossover':'crossover_bootstrap_v12.json',
 'audit':'driver_audit_v12.json',
}


def compare(expected,actual,loc='$',tol=1e-9):
    if type(expected) != type(actual):
        if not(isinstance(expected,(int,float)) and isinstance(actual,(int,float))
               and not isinstance(expected,bool) and not isinstance(actual,bool)):
            raise ValueError(f'STOP_V12_TYPE_MISMATCH:{loc}')
    if isinstance(expected,dict):
        if expected.keys()!=actual.keys():
            raise ValueError(f'STOP_V12_KEYSET_MISMATCH:{loc}')
        for k in expected:compare(expected[k],actual[k],f'{loc}.{k}',tol)
    elif isinstance(expected,list):
        if len(expected)!=len(actual):raise ValueError(f'STOP_V12_SEQUENCE_LENGTH:{loc}')
        for k,(a,b) in enumerate(zip(expected,actual)):compare(a,b,f'{loc}[{k}]',tol)
    elif isinstance(expected,bool) or isinstance(expected,str) or expected is None:
        if expected!=actual:raise ValueError(f'STOP_V12_METADATA_CHANGED:{loc}')
    elif isinstance(expected,(int,float)):
        if not math.isfinite(float(expected)) or not math.isfinite(float(actual)):
            raise ValueError(f'STOP_V12_NONFINITE:{loc}')
        if not math.isclose(float(expected),float(actual),rel_tol=0.,abs_tol=tol):
            raise ValueError(f'STOP_V12_NUMERIC_REPLAY:{loc}:expected={expected}:actual={actual}')
    else:
        raise ValueError(f'STOP_V12_UNSUPPORTED_JSON:{loc}')


def replays():
    primary=ecological_experiment(seeds=30)
    targeted=tuple(c for c in CONDITIONS if c.name in ('private_learning_plus_boids','learning_plus_social','learning_social_depletion'))
    family=ecological_experiment(seeds=30,conditions=targeted,alphas=(0.,1.,2.))
    guild_null=relabel_experiment(seeds=30)
    coupling=scan(seeds=30)
    grain=grain_experiment(seeds=30)
    crossover=crossing_audit(coupling)
    audit=paired_seed_contrasts(primary,guild_null,family)
    return {'main':primary,'family':family,'guild_null':guild_null,'coupling':coupling,
            'grain':grain,'crossover':crossover,'audit':audit}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--replay',action='store_true',help='Rerun the full finite known-truth simulator benchmark')
    p.add_argument('--only',choices=list(FILES),help='Check a single frozen receipt by regenerating only its prerequisites')
    p.add_argument('--result-root',type=Path,default=RESULTS)
    args=p.parse_args()
    baseline={name:json.loads((args.result_root/path).read_text()) for name,path in FILES.items()}
    # All frozen output files must have valid known-truth status.
    if baseline['main']['status']!='EXPLORATORY_SIMULATOR_ONLY_NOT_WILD_EVIDENCE':
        raise ValueError('STOP_V12_CLAIM_STATUS')
    if len(baseline['main']['seeds'])!=30:
        raise ValueError('STOP_V12_SEED_COUNT')
    if args.replay:
        import time
        t=time.monotonic()
        if args.only:
            name=args.only
            print('V12_REPLAY_START',name,flush=True)
            if name=='main': actual=ecological_experiment(seeds=30)
            elif name=='family':
                subset=tuple(c for c in CONDITIONS if c.name in ('private_learning_plus_boids','learning_plus_social','learning_social_depletion'))
                actual=ecological_experiment(seeds=30,conditions=subset,alphas=(0.,1.,2.))
            elif name=='guild_null':actual=relabel_experiment(seeds=30)
            elif name=='coupling':actual=scan(seeds=30)
            elif name=='grain':actual=grain_experiment(seeds=30)
            elif name=='crossover':actual=crossing_audit(baseline['coupling'])
            elif name=='audit':actual=paired_seed_contrasts(baseline['main'],baseline['guild_null'],baseline['family'])
            compare(baseline[name],actual,'$.'+name)
            print('PASS_V12_FROZEN_RECEIPT',name,'elapsed_s',round(time.monotonic()-t,2))
        else:
            print('V12_REPLAY_ALL_START',flush=True)
            actual=replays()
            for name,baseline_receipt in baseline.items():
                compare(baseline_receipt,actual[name],f'$.{name}')
            print('PASS_V12_FROZEN_SIMULATOR_RECEIPTS_ALL_SEVEN elapsed_s',round(time.monotonic()-t,2))
    else:
        print('PASS_V12_SEVEN_RECEIPTS_PRESENT_NO_NUMERICAL_REPLAY')

if __name__=='__main__':main()
