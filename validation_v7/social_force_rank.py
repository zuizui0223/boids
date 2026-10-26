#!/usr/bin/env python3
"""Known-truth structural identifiability of Boids separation vs cohesion.

This is NOT a simulation of real bats or birds. It checks a local steering-design
matrix for two explicit candidate vector kernels, not the entire motion law.
No observational animal data are used, and no GPS source is required.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

DEFAULT_SEEDS = 60
N_TRAIN = 100
N_TEST = 60
TRUE_BETA = (0.70, -0.25)
NOISE_SD = .10


def build_force_matrix(*, rng: np.random.Generator, n_states: int, n_neighbors: int,
                       distance_regime: str) -> np.ndarray:
    if n_neighbors not in (1,3):
        raise ValueError('Known-truth benchmark admits only one or three observed neighbors')
    directions = rng.normal(size=(n_states,n_neighbors,3))
    directions /= np.linalg.norm(directions,axis=-1,keepdims=True)
    if distance_regime == 'fixed':
        distances = np.full((n_states,n_neighbors,1), 10.,dtype=float)
    elif distance_regime == 'variable':
        distances = rng.uniform(6.,18.,size=(n_states,n_neighbors,1))
    else:
        raise ValueError('Unexpected distance regime')
    displacement = directions * distances
    dist = np.linalg.norm(displacement,axis=-1,keepdims=True)
    separation = (-displacement / (dist**3)).mean(axis=1)
    cohesion = displacement.mean(axis=1)
    return np.stack([separation, cohesion],axis=-1).reshape(n_states*3,2)


def standardized_design(Xtrain, Xtest):
    scale = np.sqrt((Xtrain**2).mean(axis=0))
    if np.any(scale<1e-12):
        raise ValueError('Degenerate observed force kernel')
    return Xtrain/scale, Xtest/scale, scale


def trial(seed:int,n_neighbors:int,regime:str) -> dict:
    rng = np.random.default_rng(seed)
    X0 = build_force_matrix(rng=rng,n_states=N_TRAIN,n_neighbors=n_neighbors,distance_regime=regime)
    Y0 = build_force_matrix(rng=rng,n_states=N_TEST,n_neighbors=n_neighbors,distance_regime=regime)
    X,Y,_ = standardized_design(X0,Y0)
    singular = np.linalg.svd(X,compute_uv=False)
    rank=int(np.linalg.matrix_rank(X,tol=1e-8))
    corr=float(np.corrcoef(X.T)[0,1])
    beta=np.array(TRUE_BETA,dtype=float)
    observed=X@beta + rng.normal(0,NOISE_SD,size=X.shape[0])
    holdout=Y@beta + rng.normal(0,NOISE_SD,size=Y.shape[0])
    fit=np.linalg.lstsq(X,observed,rcond=1e-10)[0]
    return {'rank':rank,'standardized_condition':float(singular[0]/singular[-1]) if singular[-1]>1e-12 else None,
            'force_column_correlation':corr,
            'beta_absolute_error':float(np.linalg.norm(fit-beta)),
            'heldout_mse':float(np.mean((Y@fit-holdout)**2)),
            'noise_oracle_mse':float(np.mean((Y@beta-holdout)**2))}


def experiment(seeds=DEFAULT_SEEDS):
    if seeds<2: raise ValueError('At least two independent seeds required')
    scenarios={
      'two_birds_fixed_distance':(1,'fixed'),
      'two_birds_variable_distance':(1,'variable'),
      'four_birds_heterogeneous_distances':(3,'variable'),
      'four_birds_equal_neighbor_distances':(3,'fixed')
    }
    out={}
    for label,(n,regime) in scenarios.items():
        rows=[trial(20261027+i,n,regime) for i in range(seeds)]
        out[label]={'n_runs':seeds,'n_neighbors':n,'distance_regime':regime,
         'rank_two_fraction':float(np.mean([r['rank']==2 for r in rows])),
         'mean_force_column_correlation':float(np.mean([r['force_column_correlation'] for r in rows])),
         'mean_estimated_beta_absolute_error':float(np.mean([r['beta_absolute_error'] for r in rows])),
         'mean_heldout_mse':float(np.mean([r['heldout_mse'] for r in rows])),
         'mean_noise_oracle_mse':float(np.mean([r['noise_oracle_mse'] for r in rows])),
         'median_standardized_condition':float(np.median([r['standardized_condition'] for r in rows if r['standardized_condition'] is not None])) if all(r['standardized_condition'] is not None for r in rows) else None}
    return {'study':'known-truth-Boids-two-force-rank-v7',
     'source':'synthetic 3D local-neighbor configurations; NOT ecological or measured flight data',
     'model':'steering acceleration = beta_sep*(-mean r/d^3) + beta_coh*(mean r) + iid Gaussian noise; features standardized using training-only RMS',
     'true_beta_standardized':list(TRUE_BETA),'observation_noise_sd':NOISE_SD,
     'n_train_states':N_TRAIN,'n_holdout_states':N_TEST,'seeds':seeds,
     'scenarios':out,'claim_boundary':[
      'When all neighbor distances are the same and kernels are proportional, the two local-force columns have rank one even with many neighbors.',
      'Variable distances can make the two *specified* kernels distinguishable in known-truth settings.',
      'Low held-out error does not imply separate recovery of physically distinct social-force parameters.',
      'Identifiable algebraic coefficients do not by themselves prove a natural animal uses these force kernels.']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seeds',type=int,default=DEFAULT_SEEDS)
    p.add_argument('--out',type=Path,default=Path('validation_v7/results/social_force_rank_known_truth_v7.json'))
    a=p.parse_args()
    result=experiment(a.seeds)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
