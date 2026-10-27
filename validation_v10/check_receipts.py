#!/usr/bin/env python3
"""Fail-closed numerical replay of committed v10 synthetic JSON contracts.

A replay checks deterministic source simulation, not wild-animal verification.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

ABS_TOL = 1e-9


def compare(expected, actual, path='$'):
    if type(expected) is not type(actual):
        # JSON writers may encode the same numeric value as int or float.
        if not (isinstance(expected,(int,float)) and not isinstance(expected,bool)
                and isinstance(actual,(int,float)) and not isinstance(actual,bool)):
            raise ValueError(f'STOP_SCHEMA_TYPE_CHANGED:{path}')
    if isinstance(expected,dict):
        if set(expected)!=set(actual):
            raise ValueError(f'STOP_SCHEMA_KEYS_CHANGED:{path}')
        for k in expected:compare(expected[k],actual[k],f'{path}.{k}')
    elif isinstance(expected,list):
        if len(expected)!=len(actual):raise ValueError(f'STOP_SCHEMA_LENGTH_CHANGED:{path}')
        for i,(a,b) in enumerate(zip(expected,actual)):compare(a,b,f'{path}[{i}]')
    elif isinstance(expected,bool) or isinstance(expected,str) or expected is None:
        if expected!=actual:raise ValueError(f'STOP_METADATA_CHANGED:{path}')
    elif isinstance(expected,(int,float)):
        if not math.isfinite(float(expected)) or not math.isfinite(float(actual)):
            raise ValueError(f'STOP_NUMERIC_NOT_FINITE:{path}')
        if not math.isclose(expected,actual,abs_tol=ABS_TOL,rel_tol=0):
            raise ValueError(f'STOP_NUMERIC_REPLAY_MISMATCH:{path}:{expected}:{actual}')
    else:
        raise ValueError(f'STOP_UNSUPPORTED_RECEIPT_TYPE:{path}')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--replay',type=Path,required=True)
    args=p.parse_args()
    compare(json.loads(args.baseline.read_text()),json.loads(args.replay.read_text()))
    print('PASS_V10_NUMERICAL_REPLAY',args.baseline)

if __name__=='__main__':main()
