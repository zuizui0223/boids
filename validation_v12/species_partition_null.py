#!/usr/bin/env python3
"""v12 exact pair-preserving guild-label permutation contrast (synthetic only).

All 20 divisions of six within-dyad social pairs into groups of 3 + 3 are
enumerated. Complement swaps yield identical mutual information and are both
included; minimal exact one-sided p is 2/20 = 0.1. The robust target is the
mean paired observed-minus-relabelled contrast ACROSS independent RNG seeds.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
from emergent_preferences import (CONDITIONS,N,N_PER_SPECIES,N_DAYS,TRAIN_DAYS,
        PRIMARY_GRAIN,SEED_START,categorical_xyz,simulate)

CONTRAST_CONDITIONS=('neutral','private_learning_only','learning_plus_social_no_boids',
 'learning_plus_social','learning_social_depletion','learning_social_history_shuffle',
 'learning_mixed_species_social')
ALL_SPLITS=tuple(itertools.combinations(range(N//2),N_PER_SPECIES//2))
ACTUAL_SPLIT=(0,1,2)
assert ACTUAL_SPLIT in ALL_SPLITS and len(ALL_SPLITS)==20


def mi(p:np.ndarray)->float:
    avg=p.mean(axis=0)
    q=np.divide(p,avg[None,...],out=np.ones_like(p),where=p>0)
    return float(np.sum(np.where(p>0,p*np.log(q),0.))/len(p))


def exact_label_audit(xyz: np.ndarray, grain:dict=PRIMARY_GRAIN)->dict:
    """Pair-preserving post hoc label null on HELDOUT days only."""
    hist=categorical_xyz(xyz[TRAIN_DAYS:],grain)
    nx,ny,nz=(len(grain[k])+1 for k in ('x','y','z'))
    counts=np.stack([np.bincount(hist[:,:,i].ravel(),minlength=nx*ny*nz).reshape(nx,ny,nz) for i in range(N)])
    counts=counts.astype(float)
    counts/=counts.sum(axis=(1,2,3),keepdims=True)
    results={}
    for split in ALL_SPLITS:
        idx=np.array([i for pair in split for i in (2*pair,2*pair+1)],int)
        rest=np.setdiff1d(np.arange(N),idx)
        a=counts[idx].mean(axis=0);b=counts[rest].mean(axis=0)
        xyz_sp=np.stack((a,b))
        xy_sp=xyz_sp.sum(axis=-1)
        ix=mi(xy_sp)
        iz=max(mi(xyz_sp)-ix,0.)
        results[str(split)]=(ix,iz)
    values=np.asarray(list(results.values()),float)
    observed=np.asarray(results[str(ACTUAL_SPLIT)])
    null_mean=values.mean(axis=0)
    # Observed assignment is among all 20, so exact tail p cannot be <0.1.
    p=(values>=observed[None,:]-1e-12).sum(axis=0)/len(values)
    return {'actual_horizontal_information':float(observed[0]),
            'actual_vertical_given_xy_information':float(observed[1]),
            'pair_partition_null_horizontal_mean':float(null_mean[0]),
            'pair_partition_null_vertical_mean':float(null_mean[1]),
            'horizontal_excess_over_pair_null':float(observed[0]-null_mean[0]),
            'vertical_excess_over_pair_null':float(observed[1]-null_mean[1]),
            'exact_horizontal_tail_p':float(p[0]),
            'exact_vertical_tail_p':float(p[1]),
            'n_pair_preserving_assignments':len(ALL_SPLITS)}


def run(seeds:int=30)->dict:
    if seeds<3:raise ValueError('Need 3 independent stochastic worlds')
    cond={c.name:c for c in CONDITIONS}
    per=[]
    for name in CONTRAST_CONDITIONS:
        for seed in range(SEED_START,SEED_START+seeds):
            sim=simulate(cond[name],seed,alpha=1.)
            per.append({'condition':name,'seed':seed,**exact_label_audit(sim['xyz'])})
    results={}
    keys=('actual_horizontal_information','pair_partition_null_horizontal_mean',
          'horizontal_excess_over_pair_null','vertical_excess_over_pair_null')
    for name in CONTRAST_CONDITIONS:
        selected=[row for row in per if row['condition']==name]
        results[name]={k:{'mean':float(np.mean([x[k] for x in selected])),
                          'min':float(min(x[k] for x in selected)),
                          'max':float(max(x[k] for x in selected)),
                          'positive_seeds':int(sum(x[k]>0 for x in selected))}
                       for k in keys}
        results[name]['exact_horizontal_tail_p_le_0.1_seeds']=int(sum(x['exact_horizontal_tail_p']<=.1000001 for x in selected))
    return {'study':'v12-pair-network-preserving-guild-label-null',
            'status':'SYNTHETIC_RELABELLING_CONTROL_NOT_FIELD_SPECIES_INFERENCE',
            'protocol':{'seeds':seeds,'pair_partition_assignments':len(ALL_SPLITS),
                        'minimum_possible_per_seed_exact_p':.1,
                        'permutation_unit':'whole 2-agent Boids dyad; 3 dyads per pseudoguild',
                        'statistics':'I(pseudoguild; XY) and I(pseudoguild;Z|XY) on heldout simulated days'},
            'results':results,'per_seed':per}


def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=30)
    p.add_argument('--out',type=Path,default=Path('validation_v12/results/guild_relabel_null_v12.json'))
    a=p.parse_args();result=run(a.seeds)
    a.out.parent.mkdir(exist_ok=True,parents=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    for name,v in result['results'].items():
        print(name,'Ixy',round(v['actual_horizontal_information']['mean'],3),
        'null mean',round(v['pair_partition_null_horizontal_mean']['mean'],3),
        'excess',round(v['horizontal_excess_over_pair_null']['mean'],3),
        'min_p_count',v['exact_horizontal_tail_p_le_0.1_seeds'])

if __name__=='__main__':main()
