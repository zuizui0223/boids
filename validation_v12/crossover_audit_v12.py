#!/usr/bin/env python3
"""Bootstrap seeded social-influence gain crossover (descriptive known truth)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

SEED = 20261029
DRAWS = 5000


def crossing(strengths, values):
    a=np.asarray(strengths,float)
    b=np.asarray(values,float)
    for i in range(len(a)-1):
        if b[i]==0:return float(a[i])
        if b[i]<0<=b[i+1]:
            return float(a[i]+(a[i+1]-a[i])*(-b[i])/(b[i+1]-b[i]))
    return None


def audit(doc:dict,draws:int=DRAWS)->dict:
    if doc['status']!='EXPLORATORY_SYNTHETIC_FINITE_STRENGTH_SCAN_NOT_PHASE_TRANSITION':
        raise ValueError('Not a synthetic strength receipt')
    seeds=doc['seeds'];xs=doc['strengths']
    if len(seeds)<3 or len(xs)<3:raise ValueError('Not enough worlds')
    # paired stochastic seeds across social strengths (common random numbers)
    per=np.array([[v['patch_guild']-v['patch_personal'] for v in row['per_seed']] for row in doc['worlds']])
    if per.shape!=(len(xs),len(seeds)):
        raise ValueError('Paired strength×seed matrix changed')
    obs=crossing(xs,per.mean(axis=1))
    rng=np.random.default_rng(SEED)
    idx=rng.integers(0,len(seeds),(draws,len(seeds)))
    reps=per[:,idx].mean(axis=2)  # strengths × bootstrap replicate
    samples=[crossing(xs,reps[:,i]) for i in range(draws)]
    good=np.array([v for v in samples if v is not None],float)
    out={'status':'EXPLORATORY_SYNTHETIC_CROSSOVER_AUDIT',
      'n_independent_simulator_seeds':len(seeds),
      'same_rng_world_paired_strength_grid':True,
      'n_bootstrap_seed_resamples':draws,
      'estimated_gain_crossover':obs,
      'bootstrap_fraction_with_a_crossing':float(len(good)/draws),
      'bootstrap_interpolated_95pct_range':[float(np.quantile(good,.025)),float(np.quantile(good,.975))] if len(good) else None,
      'interpretation':'This is a model- and parameter-dependent forecast-gain crossover, not a biological threshold, critical point, or bifurcation.'}
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=Path('validation_v12/results/social_influence_scan_v12.json'))
    p.add_argument('--out',type=Path,default=Path('validation_v12/results/crossover_bootstrap_v12.json'))
    args=p.parse_args();res=audit(json.loads(args.input.read_text()))
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(res,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    print(json.dumps(res,indent=2))

if __name__=='__main__':main()
