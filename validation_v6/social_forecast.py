#!/usr/bin/env python3
"""Prospectively fixed held-out 3D turning forecast on 30 bat flight pairs.

NOT a causal separation/alignment/cohesion coefficient fit. Model compares the
information in one's *recorded* partner with a fixed, other-trial ghost partner,
under the same held-out pairs, to assess directional short-horizon forecasting.
No identity across flight-pair episodes is assumed and no ecological niche or
long-term strategy forecast is issued from ~1-second flight segments.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from paired_trajectory_gate import (DIRECT_URL, STRIDE, MIN_ADMITTED,
                                    decode_cells, admit, http_bytes, verify_bytes)

ALPHA = 10.0
GHOST_OFFSET = 7
BOOT_REPLICATES = 5000
BOOT_SEED = 20261026
DT = STRIDE/180.0 # published spline-resampled pseudo-time; NOT true independent sensor frequency


def _interpolate_path(path: np.ndarray, n: int) -> np.ndarray:
    p = np.asarray(path, dtype=float)
    u = np.linspace(0,1,len(p)); v=np.linspace(0,1,n)
    return np.column_stack([np.interp(v,u,p[:,d]) for d in range(3)])


def rows_for_bat(x: np.ndarray, partner: np.ndarray) -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    """Return own-only X, neighbor X, 3D next-turn delta; no future features."""
    if x.shape != partner.shape or x.ndim!=2 or x.shape[1]!=3 or len(x)<5:
        raise ValueError('Paired tracking arrays must be matched XYZ matrices with >=5 positions')
    d = np.diff(x, axis=0)
    w = np.diff(partner, axis=0)
    speed = np.linalg.norm(d,axis=1)
    other_speed = np.linalg.norm(w,axis=1)
    if (speed<=1e-10).any() or (other_speed<=1e-10).any():
        raise ValueError('Undefined heading from zero speed')
    h = d / speed[:,None]
    ho = w / other_speed[:,None]
    own=[]; social=[]; y=[]
    k = len(h)
    for t in range(1,k-1):
        axis = h[t]
        perp = lambda v: v - np.dot(v,axis)*axis
        r = partner[t+1]-x[t+1]
        norm=np.linalg.norm(r)
        if norm <= 1e-10:
            raise ValueError('Partner shares exactly same position as target')
        # Distance is NOT used as an inferred species-specific interaction radius.
        own.append(np.hstack([axis, axis-h[t-1], x[t+1], speed[t]/DT, (t+1)/k]))
        social.append(np.hstack([perp(ho[t]), perp(r/norm)]))
        y.append(h[t+1]-axis)
    return np.asarray(own), np.asarray(social), np.asarray(y)


def make_trial_features(pairs: list[dict], *, ghost: bool, excluded_index: int | None = None) -> list[dict]:
    all_rows=[]
    n=len(pairs)
    if n<2:raise ValueError('Need multiple independent flight pairs')
    for idx,p in enumerate(pairs):
        xa,ya=p['x'],p['y']
        if ghost:
            candidates=[(idx+GHOST_OFFSET+k)%n for k in range(n)
                        if (idx+GHOST_OFFSET+k)%n not in (idx,excluded_index)]
            if not candidates:
                raise ValueError('No independently available ghost donor')
            donor=pairs[candidates[0]]
            partners=[_interpolate_path(donor['y'],len(xa)),
                      _interpolate_path(donor['x'],len(ya))]
        else:
            partners=[ya,xa]
        one=[]
        for path,oth in zip([xa,ya],partners):
            try:
                own,social,y=rows_for_bat(path,oth)
            except ValueError as exc:
                raise ValueError(f"structural fail for accepted pair {p['index']}: {exc}") from exc
            one.append((own,social,y))
        all_rows.append({'index':p['index'],'roles':one,
                         'ghost_donor_index':donor['index'] if ghost else None})
    return all_rows


def _ridge_fit_predict(xtrain:np.ndarray,ytrain:np.ndarray,train_weight:np.ndarray,
                       xtarget:np.ndarray) -> np.ndarray:
    mean=np.average(xtrain,axis=0,weights=train_weight)
    sd=np.sqrt(np.average((xtrain-mean)**2,axis=0,weights=train_weight))
    sd=np.maximum(sd,1e-8)
    x=(xtrain-mean)/sd;xt=(xtarget-mean)/sd
    ym=np.average(ytrain,axis=0,weights=train_weight)
    w=np.sqrt(train_weight)
    a=x*w[:,None];b=(ytrain-ym)*w[:,None]
    beta=np.linalg.solve(a.T@a+ALPHA*np.eye(a.shape[1]),a.T@b)
    return ym+xt@beta


def _role_rows(trial:dict,mode:str) -> list[tuple[np.ndarray,np.ndarray]]:
    result=[]
    for own,extra,y in trial['roles']:
        features=own if mode=='own' else np.column_stack([own,extra])
        result.append((features,y))
    return result


def run_scores(pairs:list[dict]) -> dict:
    if len(pairs)<MIN_ADMITTED:raise ValueError('STOP_INSUFFICIENT_PAIRS_FOR_HELDOUT_FORECAST')
    paired=make_trial_features(pairs,ghost=False)
    records=[]
    for target in range(len(pairs)):
        # Reconstruct fixed ghost mapping within each CV fold: held-out target
        # must NEVER enter any training ghost feature, even indirectly.
        ghost=make_trial_features(pairs,ghost=True,excluded_index=target)
        if any(tr['ghost_donor_index']==pairs[target]['index'] for tr in ghost):
            raise ValueError('STOP_GHOST_TARGET_LEAKAGE')
        per_model={}
        for mode,data in [('own',paired),('actual',paired),('ghost',ghost)]:
            trows=[_role_rows(x, 'own' if mode=='own' else 'social') for x in data]
            for_role=[]
            for role in range(2):
                # Train on other flight episodes only; no target rows in train.
                xx=[];yy=[];ww=[]
                for j in range(len(trows)):
                    if j==target:continue
                    a,b=trows[j][role]
                    xx.append(a);yy.append(b);ww.append(np.full(len(a),1/len(a)))
                xtrain=np.vstack(xx);ytrain=np.vstack(yy)
                weight=np.hstack(ww);weight/=weight.mean()  # equal trial total weight
                xtarget,ytarget=trows[target][role]
                pred=_ridge_fit_predict(xtrain,ytrain,weight,xtarget)
                mse=float(np.mean(np.sum((ytarget-pred)**2,axis=1)))
                for_role.append(mse)
            per_model[mode]=float(np.mean(for_role))
        records.append({'pair_index':int(pairs[target]['index']),
            'n_target_step_pairs':sum(len(r[2]) for r in paired[target]['roles']),
            'own_mse':per_model['own'], 'actual_partner_mse':per_model['actual'],
            'ghost_partner_mse':per_model['ghost'],
            'gain_vs_own':per_model['own']-per_model['actual'],
            'ghost_gain_vs_own':per_model['own']-per_model['ghost'],
            'actual_vs_ghost':per_model['ghost']-per_model['actual']})
    names=['gain_vs_own','ghost_gain_vs_own','actual_vs_ghost']
    means={k:float(np.mean([r[k] for r in records])) for k in names}
    mat=np.array([[r[k] for k in names] for r in records])
    rng=np.random.default_rng(BOOT_SEED)
    draws=mat[rng.integers(0,len(mat),size=(BOOT_REPLICATES,len(mat)))].mean(axis=1)
    ci={k:[float(np.quantile(draws[:,j],.025)),float(np.quantile(draws[:,j],.975))]
        for j,k in enumerate(names)}
    return {'status':'EXPLORATORY_OBSERVED_3D_DIRECTIONAL_FORECAST_ONLY',
        'n_pair_trials':len(pairs),'n_bat_roles_per_trial':2,'held_out':'entire pair trial',
        'resample_note':'Numerical stride 6 from spline-resampled 180Hz archive; not 30Hz independent original camera measurements.',
        'ridge_alpha':ALPHA,'ghost_partner_rule':f'cyclic offset {GHOST_OFFSET} in accepted pair order, skipping target fold as donor; trajectory linearly mapped to same normalized trial phase',
        'error_metric':'mean squared 3D heading change prediction error (dimensionless); positive improvement is better',
        'equal_pair_weighted_mean':means,'pair_bootstrap_95pct_CI':ci,
        'actual_better_than_ghost_n_pairs':int(sum(x['actual_vs_ghost']>0 for x in records)),
        'per_pair':records,
        'causal_status':'No independent camera position-error model, environmental geometry measurement, true original frame timestamps or cross-night identity. Gains cannot identify causal social steering.',
        'long_term_ecological_status':'Flight segments too short for repeatable individual 3D niche or population-level species partition forecast.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path)
    ap.add_argument('--out',type=Path,default=Path('validation_v6/results/bat_pair_directional_forecast.json'))
    args=ap.parse_args()
    raw=args.source.read_bytes() if args.source else http_bytes(DIRECT_URL)
    try:
        verify_bytes(raw)
        pairs, audit, gate = admit(decode_cells(raw))
        if gate['gate'] != 'PASS':
            print('STOP_SOURCE_GATE '+json.dumps(gate));return 3
        result=run_scores(pairs)
    except Exception as exc:
        print('STOP_FIT: '+type(exc).__name__+': '+str(exc));return 2
    result['doi']='10.7294/W4639MWR'
    result['source_md5_verified']=True
    result['admission']=gate
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='per_pair'},indent=2,ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
