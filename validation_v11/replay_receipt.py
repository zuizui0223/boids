#!/usr/bin/env python3
"""Fail-closed comparison of the frozen synthetic v11 receipt with a fresh replay."""
import argparse,json,math
from pathlib import Path


def compare(a,b,path='$',eps=1e-9):
    if isinstance(a,dict):
        if not isinstance(b,dict) or a.keys()!=b.keys():raise ValueError('STOP_SCHEMA_KEYS_CHANGED:'+path)
        for k in a:compare(a[k],b[k],path+'.'+k,eps)
    elif isinstance(a,list):
        if not isinstance(b,list) or len(a)!=len(b):raise ValueError('STOP_SCHEMA_LENGTH_CHANGED:'+path)
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,f'{path}[{i}]',eps)
    elif isinstance(a,bool) or a is None or isinstance(a,str):
        if a!=b:raise ValueError('STOP_METADATA_CHANGED:'+path)
    elif isinstance(a,(int,float)):
        if (not isinstance(b,(int,float)) or isinstance(b,bool)
            or not math.isfinite(a) or not math.isfinite(b)
            or not math.isclose(a,b,rel_tol=0.,abs_tol=eps)):
            raise ValueError('STOP_NUMERICAL_REPLAY_MISMATCH:'+path)
    else: raise ValueError('STOP_UNSUPPORTED_RECEIPT:'+path)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--replay',type=Path,required=True)
    args=ap.parse_args()
    compare(json.loads(args.baseline.read_text()),json.loads(args.replay.read_text()))
    print('PASS_V11_SYNTHETIC_NUMERICAL_REPLAY')

if __name__=='__main__':main()
