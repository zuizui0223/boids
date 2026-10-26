"""Prospective synthetic sensitivity scan connecting batter, ODSP and louis.

All scenario axes and endpoint contrasts are declared in source BEFORE outcomes.
This does not fit telemetry or prove ecological causation. Only generated data.

Niche partitioning endpoints are distinct: (1) coarse spatial overlap;
(2) species information in XY and Z conditional on XY; (3) held-out
independent-individual prediction. Environment-state buffering is independent.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace, asdict
from itertools import product
from pathlib import Path
import json
import numpy as np
from eco_dynamics import EcologicalRules,run,state_information

SEEDS=(17,23,47,71,101)
PREFS=(0., .12, .30)
DEPLETION=(0., .08, .30)
TRACKING=(0., .80)
BASE=EcologicalRules(steps=300,burn=100,thin=4,nights=3)
ARMS=list(product(PREFS,DEPLETION,TRACKING,SEEDS))
PRIMARY=['segregation_excess','within_species_overlap','between_species_overlap',
         'species_horizontal_partition_information_nats',
         'species_vertical_partition_information_nats',
         'species_heldout_individual_gain_mean',
         'state_buffering_advantage','effective_vertical_states',
         'mean_uptake']

def worker(spec):
    pref,depletion,tracking,seed=spec
    r=replace(BASE,resource_contrast=pref,consumption=depletion,
              state_tracking=tracking,seed=seed)
    m,tr,st,available,groups=run(r,return_trajectories=True)
    info=state_information(tr,groups)
    return dict(preference=pref,depletion=depletion,tracking=tracking,seed=seed,
        segregation_excess=m['segregation_excess'],
        within_species_overlap=m['within_species_overlap'],
        between_species_overlap=m['between_species_overlap'],
        species_horizontal_partition_information_nats=info['species_horizontal_partition_information_nats'],
        species_vertical_partition_information_nats=info['species_vertical_partition_information_nats'],
        species_heldout_individual_gain_mean=float(np.mean(info['species_heldout_individual_gain'])),
        species_heldout_individual_gain_positive=int(sum(np.array(info['species_heldout_individual_gain'])>0)),
        state_buffering_advantage=m['state_buffering_advantage'],
        effective_vertical_states=info['effective_vertical_states'],
        mean_uptake=m['mean_uptake'])

def analysis(rows):
    lookup={(r['preference'],r['depletion'],r['tracking'],r['seed']):r for r in rows}
    percell=[]
    for pref,dep,tracking in product(PREFS,DEPLETION,TRACKING):
        subset=[lookup[(pref,dep,tracking,seed)] for seed in SEEDS]
        o=dict(preference=pref,depletion=dep,tracking=tracking)
        for metric in PRIMARY:
            v=np.array([r[metric] for r in subset])
            o[metric+'_mean']=float(v.mean())
            o[metric+'_min']=float(v.min())
            o[metric+'_max']=float(v.max())
        o['positive_new_individual_runs']=int(sum(r['species_heldout_individual_gain_mean']>0 for r in subset))
        percell.append(o)
    # Pairwise control-referenced contrasts, same seed and other factors held constant.
    contrasts={}
    for label,a,b in [
        ('resource_preference_effect',(.30,0.,0.),(0.,0.,0.)),
        ('depletion_effect_with_resource_preference',(.30,.30,0.),(.30,0.,0.)),
        ('depletion_effect_without_resource_preference',(0.,.30,0.),(0.,0.,0.)),
        ('tracking_effect_with_pref_and_depletion',(.30,.30,.80),(.30,.30,0.)),
        ('tracking_effect_without_resource_preference',(0.,0.,.80),(0.,0.,0.)),
        ('depletion_effect_with_state_tracking',(.30,.30,.80),(.30,0.,.80)),
    ]:
        d={}
        for metric in PRIMARY:
            ds=np.array([lookup[(*a,s)][metric]-lookup[(*b,s)][metric] for s in SEEDS])
            d[metric]={'mean':float(ds.mean()),'range':[float(ds.min()),float(ds.max())],
                       'positive_seeds':int((ds>0).sum()),'negative_seeds':int((ds<0).sum())}
        contrasts[label]={'treated':dict(zip(('preference','depletion','tracking'),a)),
                          'control':dict(zip(('preference','depletion','tracking'),b)),
                          'paired_seed_differences':d}
    # Descriptive, NOT a data-derived formal phase transition threshold.
    # Avoid overlap-based claims about realized competition, prey segregation,
    # breeding components or synchronous displacement.
    return {
      'status':'known_truth_synthetic_not_empirical',
      'simulation_grid':{'preference':PREFS,'resource_depletion':DEPLETION,'state_tracking':TRACKING,'seeds':SEEDS},
      'settings':asdict(BASE),'n_runs':len(rows),'raw':rows,
      'cell_means':percell,'paired_contrasts':contrasts,
      'boundary':[
        'Species partition information can be high without spatial overlap segregation.',
        'Individual-out transfer is required to separate generality from fitted information.',
        'Shared resource consumption is not alone evidence of pairwise interference competition.',
        'Larger-scale and independent datasets are needed to infer a stable threshold.',
        'Penguin breeding-component concentration is not a flying-space voxel Hill number.',
        'Behaviorally chosen states, random availability and demographic states use different observation processes.'
      ]}

def main():
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(worker,ARMS,chunksize=3))
    out=analysis(rows)
    dest=Path(__file__).with_name('cross_repo_phase_scan.json')
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    for k,rec in out['paired_contrasts'].items():
        d=rec['paired_seed_differences']
        print(k,'delta_segregation',round(d['segregation_excess']['mean'],4),
          'delta_Ivertical',round(d['species_vertical_partition_information_nats']['mean'],4),
          'delta_buffer',round(d['state_buffering_advantage']['mean'],4))
    print('SAVED',dest)

if __name__=='__main__':main()
