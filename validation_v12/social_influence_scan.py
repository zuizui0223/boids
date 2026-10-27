#!/usr/bin/env python3
"""Exploratory strength-response scan: within-individual vs social-guild persistence.

The finite strength grid is illustrative, not an inferential biological tipping
point. Reuses known-truth synthetic rules, frozen after v12 primary controls.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from emergent_preferences import (CONDITIONS,SEED_START,inspect_single)

STRENGTH_GRID=(0.,.25,.5,.75,1.,1.25,1.5,1.75,2.,2.5)


def scan(seeds:int=30, strengths=STRENGTH_GRID) -> dict:
    if seeds<3:raise ValueError('Need three independent stochastic conditions')
    if list(strengths)!=sorted(set(strengths)) or any(x<0 for x in strengths):
        raise ValueError('Invalid strength grid')
    c=next(z for z in CONDITIONS if z.name=='learning_plus_social')
    out=[]
    for strength in strengths:
        rows=[]
        for seed in range(SEED_START,SEED_START+seeds):
            r=inspect_single(c,1.,seed,social_strength=strength)
            rows.append({'seed':seed, 'patch_personal':r['patch_identity_gain_nats'],
              'patch_guild':r['guild_patch_gain_nats'],
              'vertical_personal':r['vertical_identity_gain_given_xy_nats'],
              'vertical_guild':r['guild_vertical_gain_given_xy_nats'],
              'horizontal_guild_information':r['species_niche']['horizontal_information_nats']})
        summary={k:{'mean':float(np.mean([r[k] for r in rows])),
                    'sd_across_seed':float(np.std([r[k] for r in rows],ddof=1))}
                 for k in rows[0] if k!='seed'}
        out.append({'social_strength':strength,'scores':summary,'per_seed':rows})
    # Interpolated crossing is a descriptive artifact of this *chosen model*.
    crossing=[]
    for a,b in zip(out[:-1],out[1:]):
        left=a['scores']['patch_guild']['mean']-a['scores']['patch_personal']['mean']
        right=b['scores']['patch_guild']['mean']-b['scores']['patch_personal']['mean']
        if left*right<0:
            crossing.append(float(a['social_strength']+(b['social_strength']-a['social_strength'])*(-left)/(right-left)))
    return {'status':'EXPLORATORY_SYNTHETIC_FINITE_STRENGTH_SCAN_NOT_PHASE_TRANSITION',
        'study':'boids-v12-private-habit-to-guild-lock-in-crossover',
        'source':'same symmetric 2 guild × 6 agents 3D simulator, no wild data',
        'seeds':[SEED_START+i for i in range(seeds)],
        'strengths':list(strengths),
        'note':'Boids locomotor force fixed on; imitation strength alone varies. Rewards identical; no resource depletion for this scan.',
        'crossings_guild_patch_minus_personal_patch':crossing,
        'worlds':out,
        'claim_boundary':['Interpolated crossing is conditional on arbitrary choice temperature, memory, and observation grain.',
                          'Do not call it a biological threshold, a bifurcation, or a real species interaction.']}


def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=30)
    p.add_argument('--out',type=Path,default=Path('validation_v12/results/social_influence_scan_v12.json'))
    a=p.parse_args();r=scan(a.seeds)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    for x in r['worlds']:
        print(x['social_strength'],round(x['scores']['patch_personal']['mean'],3),round(x['scores']['patch_guild']['mean'],3),round(x['scores']['horizontal_guild_information']['mean'],3))
    print('interpolated crossings',r['crossings_guild_patch_minus_personal_patch'])

if __name__=='__main__':main()
