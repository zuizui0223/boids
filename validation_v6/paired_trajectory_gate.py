#!/usr/bin/env python3
"""Outcome-blind admission of 3D bat-pair trajectories; fixed analysis grain.

Source: CC BY 3.0 US, Roy & Abaid, DOI 10.7294/W4639MWR.
Strict fail-closed gates: 30 MATLAB cells per bat; both array coordinates
pairwise frame-aligned; no numeric outcome/adaptive threshold choices.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from source_preflight import (DIRECT_URL, API_URL, http_bytes, verify_bytes,
                              verify_remote_metadata)

EXPECTED_PAIRS = 30
STRIDE = 6             # predeclared 180->30 Hz numerical analysis spacing
MIN_DOWNSAMPLED = 12  # min 12 positions => 9 heading-transition targets/bat
MIN_ADMITTED = 12
EPS = 1e-10


def decode_cells(raw: bytes, *, verify: bool = True) -> list[tuple[np.ndarray, np.ndarray]]:
    if verify:
        verify_bytes(raw)
    mat = loadmat(BytesIO(raw), squeeze_me=False, struct_as_record=False)
    exact = ('XYZ_b1', 'XYZ_b2', 'Curvature_b1', 'Curvature_b2')
    if not all(k in mat for k in exact):
        raise ValueError('STOP_SOURCE_SCHEMA_MISMATCH: expected paired coordinates and curvatures')
    for k in exact:
        if mat[k].shape != (EXPECTED_PAIRS, 1) or mat[k].dtype != object:
            raise ValueError(f'STOP_CELL_ARCHITECTURE_{k}: {mat[k].shape} {mat[k].dtype}')
    pairs = []
    for i in range(EXPECTED_PAIRS):
        a = np.asarray(mat['XYZ_b1'][i, 0], dtype=float)
        b = np.asarray(mat['XYZ_b2'][i, 0], dtype=float)
        pairs.append((a, b))
    return pairs


def admit(pairs: list[tuple[np.ndarray,np.ndarray]]) -> tuple[list[dict], list[dict], dict]:
    if len(pairs) != EXPECTED_PAIRS:
        raise ValueError(f'STOP_INCOMPLETE_ARCHIVE: {len(pairs)} != {EXPECTED_PAIRS}')
    retained: list[dict] = []
    audit: list[dict] = []
    for idx, (x, y) in enumerate(pairs, 1):
        rec: dict = {'pair_index': idx}
        if x.ndim != 2 or y.ndim != 2 or x.shape[1:] != (3,) or y.shape[1:] != (3,):
            rec['decision'] = 'FAIL_NON_3D'; audit.append(rec); continue
        rec['raw_n_b1'] = int(len(x));rec['raw_n_b2'] = int(len(y))
        if len(x) != len(y):
            rec['decision'] = 'FAIL_UNALIGNED_LENGTH';audit.append(rec);continue
        if len(x[::STRIDE]) < MIN_DOWNSAMPLED:
            rec['decision'] = 'FAIL_TOO_SHORT';audit.append(rec);continue
        if not (np.isfinite(x).all() and np.isfinite(y).all()):
            rec['decision'] = 'FAIL_NONFINITE';audit.append(rec);continue
        xa, ya = x[::STRIDE], y[::STRIDE]
        diffa, diffb = np.diff(xa,axis=0), np.diff(ya,axis=0)
        if (np.linalg.norm(diffa, axis=1) <= EPS).any() or (np.linalg.norm(diffb,axis=1) <= EPS).any():
            rec['decision'] = 'FAIL_ZERO_DISPLACEMENT';audit.append(rec);continue
        rec['downsampled_n'] = int(len(xa))
        rec['decision'] = 'ELIGIBLE_SCHEMA_AND_QC'
        audit.append(rec)
        retained.append({'index':idx, 'x':xa, 'y':ya})
    n = len(retained)
    return retained, audit, {'pair_count': len(pairs), 'eligible_pairs':n,
        'primary_stride':STRIDE, 'minimum_downsampled_positions':MIN_DOWNSAMPLED,
        'minimum_pairs_for_prediction':MIN_ADMITTED,
        'gate':'PASS' if n >= MIN_ADMITTED else 'STOP_INSUFFICIENT_ALIGNED_PAIR_SUPPORT',
        'warning':'Index-alignment of b1/b2 relies on published pair interpretation; original acquisition timestamps are not provided.',
        'no_outcomes_examined':'No steering coefficients or held-out log scores estimated during this gate.'}


def run(raw: bytes) -> dict:
    verify_bytes(raw)
    pairs = decode_cells(raw)
    _, audit, summary = admit(pairs)
    return {'study':'independent_bat_pair_30_source_eligibility_v6',
        'doi':'10.7294/W4639MWR','source_md5_verified':True,
        'assumed_numeric_sampling':'180Hz spline resampled per published source; numerical decimation stride=6 to approx 30Hz, not new independent observations',
        'summary':summary, 'pair_audit':audit,
        'source_data_redistributed':False}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path)
    ap.add_argument('--out',type=Path,default=Path('validation_v6/results/paired_eligibility.json'))
    args=ap.parse_args()
    raw=args.source.read_bytes() if args.source else http_bytes(DIRECT_URL)
    try:
        out=run(raw)
    except Exception as e:
        print(f'STOP_SOURCE_GATE: {type(e).__name__}: {e}')
        return 2
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'source_md5_verified':True,'summary':out['summary'], 'pair_audit':out['pair_audit']},indent=2))
    return 0 if out['summary']['gate']=='PASS' else 3

if __name__=='__main__':raise SystemExit(main())
