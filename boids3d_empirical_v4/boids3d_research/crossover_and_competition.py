"""Synthetic dimensional crossover and interspecific-depletion counterfactual.

Distinguishes (1) per-individual self depletion, (2) conspecific resource
sharing, and (3) heterospecific sharing, as alternative environments.
The 'crossover' is where estimated descriptive I(S;Z|XY) overtakes I(S;XY),
NOT a physical phase transition, coexistence threshold or inferential p value.
"""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace,asdict
from pathlib import Path
from collections import defaultdict
import numpy as np
import json
from eco_dynamics import EcologicalRules,run,state_information

SEEDS=(17,23,47,71,101)
STRENGTHS=(0.,.015,.03,.05,.08,.11,.15,.20,.30)
POOLS=('shared','species','private')
BASE=EcologicalRules(steps=300,burn=100,thin=4,nights=3,resource_contrast=.30,
                     state_tracking=0.,state_heterogeneity=.55)
GRID=[(s,p,seed) for s in STRENGTHS for p in (POOLS if s in (0.,.08,.20,.30) else ('shared',)) for seed in SEEDS]

def worker(args):
    dep,pool,seed=args
    m,tr,a,alt,groups=run(replace(BASE,seed=seed,consumption=dep,resource_pool=pool),return_trajectories=True)
    info=state_information(tr,groups)
    return dict(consumption=dep,resource_pool=pool,seed=seed,
                between_species_overlap=m['between_species_overlap'],
                within_species_overlap=m['within_species_overlap'],
                segregation=m['segregation_excess'],
                I_species_XY=info['species_horizontal_partition_information_nats'],
                I_species_Z_given_XY=info['species_vertical_partition_information_nats'],
                unseen_individual_gain=float(np.mean(info['species_heldout_individual_gain'])),
                vertical_thickness=info['effective_vertical_states'],
                resource_uptake=m['mean_uptake'])

def summarise(rows):
    grouped=defaultdict(list)
    for r in rows:grouped[(r['consumption'],r['resource_pool'])].append(r)
    mean=[]
    for (dep,pool),rs in grouped.items():
        z={'consumption':dep,'resource_pool':pool}
        for key in ('I_species_XY','I_species_Z_given_XY','unseen_individual_gain',
                    'segregation','between_species_overlap','resource_uptake','vertical_thickness'):
            a=np.array([r[key] for r in rs]);z[key+'_mean']=float(a.mean());z[key+'_range']=[float(a.min()),float(a.max())]
        z['crossover_margin_nats']=z['I_species_Z_given_XY_mean']-z['I_species_XY_mean']
        mean.append(z)
    individual_crossings={}
    for seed in SEEDS:
        rr=sorted([r for r in rows if r['seed']==seed and r['resource_pool']=='shared'],key=lambda z:z['consumption'])
        threshold=None
        for a,b in zip(rr[:-1],rr[1:]):
            x=a['I_species_Z_given_XY']-a['I_species_XY']
            y=b['I_species_Z_given_XY']-b['I_species_XY']
            if x<0<=y:
                threshold={'bracket':[a['consumption'],b['consumption']],
                           'interpolated':float(a['consumption']+(-x/(y-x))*(b['consumption']-a['consumption']))}
                break
        individual_crossings[str(seed)]=threshold
    # A direct interspecific resource-depletion comparison. Same initial
    # resource concentrations, same stochastic seeds; 'species' pool excludes
    # heterospecific uptake but does not match total ecosystem resource stock.
    contrasts={}
    idx={(r['consumption'],r['resource_pool'],r['seed']):r for r in rows}
    for dep in (0.,.08,.20,.30):
        for a,b in [('shared','species'),('species','private')]:
            entry={}
            for key in ('segregation','I_species_XY','I_species_Z_given_XY','unseen_individual_gain','resource_uptake'):
                delta=np.array([idx[dep,a,seed][key]-idx[dep,b,seed][key] for seed in SEEDS])
                entry[key]={'mean':float(delta.mean()),'positive_seeds':int((delta>0).sum()),
                            'range':[float(delta.min()),float(delta.max())]}
            contrasts[f'{dep:.3f}_{a}_minus_{b}']=entry
    return {'status':'synthetic_model_experiment',
            'settings':asdict(BASE),'consumption_grid':STRENGTHS,'seeds':SEEDS,
            'resources':'shared/all taxa vs separate species vs individual stocks',
            'raw':rows,'summaries':mean,'individual_crossover_intervals':individual_crossings,
            'pool_contrasts':contrasts,
            'warnings':[
              'Equal-dimensional descriptive mutual informations can cross without a true phase transition.',
              'Species-only pools duplicate the physical stock and remove cross-species depletion, not merely change encounters.',
              'Observation nulls, limited data, and arbitrary discretization can shift a crossover.',
              'Unseen-individual gain is the primary confirmation of repeatable taxon-level state organization.',
              'Time-synchronous vertical displacement, actual resources and interspecific competition are not empirically established.'
            ]}

def main():
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(worker,GRID,chunksize=2))
    if any(r['consumption']==0 for r in rows):
        idx={(r['consumption'],r['resource_pool'],r['seed']):r for r in rows}
        for seed in SEEDS:
            for key in ['segregation','I_species_XY','I_species_Z_given_XY']:
                assert abs(idx[0.,'shared',seed][key]-idx[0.,'species',seed][key])<1e-10
                assert abs(idx[0.,'species',seed][key]-idx[0.,'private',seed][key])<1e-10
    out=summarise(rows)
    path=Path(__file__).with_name('crossover_and_competition.json')
    path.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print('RUNS',len(rows),'CROSSOVERS',out['individual_crossover_intervals'])
    for q in out['summaries']:
      if q['resource_pool']=='shared':
        print('CONSUMPTION',q['consumption'],
          'IXY',round(q['I_species_XY_mean'],3),
          'IZ',round(q['I_species_Z_given_XY_mean'],3),
          'unseen',round(q['unseen_individual_gain_mean'],3),
          'overlap',round(q['between_species_overlap_mean'],3))
    print('POOL CONTRAST (shared minus species at .3)',out['pool_contrasts']['0.300_shared_minus_species'])
    print('SAVED',path)
if __name__=='__main__':main()
