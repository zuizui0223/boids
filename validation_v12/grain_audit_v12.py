#!/usr/bin/env python3
"""Observation-grain sensitivity of simulator-derived 3D niches (known truth)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from emergent_preferences import (CONDITIONS,SEED_START,PRIMARY_GRAIN,FINE_GRAIN,
                                guild_vertical_gain_given_xy,vertical_gain,
                                species_niche_information,simulate)

CASES=('neutral','private_learning_only','learning_plus_social',
       'learning_social_depletion','learning_mixed_species_social')


def experiment(seeds:int=30):
    if seeds<3:raise ValueError('Need repeated simulation seeds')
    mapping={c.name:c for c in CONDITIONS};rows=[]
    for name in CASES:
        for seed in range(SEED_START,SEED_START+seeds):
            t=simulate(mapping[name],seed,alpha=1.)['xyz']
            r={'seed':seed,'condition':name}
            for gr,grain in [('coarse',PRIMARY_GRAIN),('fine',FINE_GRAIN)]:
                personal,support=vertical_gain(t,grain)
                guild=guild_vertical_gain_given_xy(t,grain)
                info=species_niche_information(t,grain)
                r[gr]={'person_z_heldout':personal,'guild_z_heldout':guild,
                       'fraction_heldout_supported_in_person_training':support,
                       'species_horizontal_information':info['horizontal_information_nats'],
                       'species_vertical_given_xy_information':info['vertical_information_given_xy_nats']}
            rows.append(r)
    summary={}
    for name in CASES:
        subset=[r for r in rows if r['condition']==name]
        summary[name]={}
        for grain in ('coarse','fine'):
            summary[name][grain]={k:float(np.mean([r[grain][k] for r in subset]))
                       for k in subset[0][grain]}
    return {'study':'v12-grain-sensitivity-comparable-heldout-states',
     'status':'SYNTHETIC_GRAIN_AUDIT_NOT_WILD_ANIMAL_INFERENCE',
     'seeds':[SEED_START+i for i in range(seeds)],
     'scoring':'All heldout states scored with per-contributor Dirichlet prior weights; support diagnostic separately.',
     'grain_bins':{'coarse':PRIMARY_GRAIN,'fine':FINE_GRAIN},
     'results':summary,'per_seed':rows}


def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=30)
    p.add_argument('--out',type=Path,default=Path('validation_v12/results/grain_audit_v12.json'))
    a=p.parse_args();r=experiment(a.seeds)
    a.out.parent.mkdir(exist_ok=True,parents=True)
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    for c,gr in r['results'].items():
        print(c,'coarse',round(gr['coarse']['guild_z_heldout'],3),'fine',round(gr['fine']['guild_z_heldout'],3),
          'XY coarse/fine',round(gr['coarse']['species_horizontal_information'],3),round(gr['fine']['species_horizontal_information'],3))

if __name__=='__main__':main()
