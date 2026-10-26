"""Is ecological structure caused by local Boids forces or by resource/environment rules?
Three nested local-force arms; ecological parameters and seed held fixed within pairs.
No species-calibrated parameters; all results are synthetic counterfactuals.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from itertools import product
from pathlib import Path
from collections import defaultdict
import json
import numpy as np
from eco_dynamics import EcologicalRules, run,state_information

ROOT=Path(__file__).parent
SEEDS=(17,23,47,71,101)
ARMS={
  'no_social':{'social_strength':0.0,'separation_strength':0.,'cohesion_strength':0.},
  'separation_alignment':{'social_strength':.06,'separation_strength':.12,'cohesion_strength':0.},
  'separation_alignment_cohesion':{'social_strength':.06,'separation_strength':.12,'cohesion_strength':.045},
}
CONTEXTS={
  'neutral':{'resource_contrast':0.,'consumption':0.,'state_tracking':0.},
  'resource_contrast':{'resource_contrast':.30,'consumption':0.,'state_tracking':0.},
  'depleted_resource':{'resource_contrast':.30,'consumption':.30,'state_tracking':0.},
  'state_tracking':{'resource_contrast':.30,'consumption':.30,'state_tracking':.80},
}
BASE=EcologicalRules(steps=300,burn=100,thin=4,nights=3)
METRICS=('I_species_XY','I_species_Z_given_XY','alignment','conspecific_nearest_distance','state_buffering','uptake')

def kinematic_summary(tr, group, domain=(16.,16.,8.)):
    # Same time regular tracking, no interpolation of unsynchronized animals.
    d=np.diff(tr,axis=2)
    for j in range(2):
        d[...,j]=(d[...,j]+domain[j]/2)%domain[j]-domain[j]/2
    nrm=np.linalg.norm(d,axis=-1,keepdims=True)
    unit=d/np.maximum(1e-8,nrm)
    aligns=[]
    for s in range(2):
        mask=group==s
        mean_direction=np.linalg.norm(unit[:,mask].mean(axis=1),axis=-1).mean()
        aligns.append(mean_direction)
    nearest=[]
    for t in range(tr.shape[0]):
        for j in range(tr.shape[2]):
            positions=tr[t,:,j,:]
            dist=positions[None,:,:]-positions[:,None,:]
            for axis in (0,1):
                dist[:,:,axis]=(dist[:,:,axis]+domain[axis]/2)%domain[axis]-domain[axis]/2
            dmat=np.linalg.norm(dist,axis=-1)
            dmat[group[:,None]!=group[None,:]]=np.inf
            np.fill_diagonal(dmat,np.inf)
            nearest.append(np.min(dmat,axis=1).mean())
    return {'alignment':float(np.mean(aligns)), 'conspecific_nearest_distance':float(np.mean(nearest))}

def worker(spec):
    context,arm,seed=spec
    params=dict(CONTEXTS[context]);params.update(ARMS[arm]);params['seed']=seed
    cfg=replace(BASE,**params)
    stats,tr,_,_,groups=run(cfg,return_trajectories=True)
    inf=state_information(tr,groups,bins_xy=4)
    kin=kinematic_summary(tr,groups)
    return {'context':context,'arm':arm,'seed':seed,
            'I_species_XY':inf['species_horizontal_partition_information_nats'],
            'I_species_Z_given_XY':inf['species_vertical_partition_information_nats'],
            'state_buffering':stats['state_buffering_advantage'],
            'uptake':stats['mean_uptake'],**kin}

def main():
    cases=list(product(CONTEXTS,ARMS,SEEDS))
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(worker,cases,chunksize=2))
    output={'scope':'synthetic ablation only, not an empirical validation',
            'boids_note':'Earlier resource-depletion simulator implemented repulsion/alignment but not cohesion; this ablation adds an optional cohesion force with default 0, so archived results are unaltered.',
            'arms':ARMS,'contexts':CONTEXTS,'seeds':SEEDS,'n_worlds':len(rows),'results':rows}
    paired={}
    def get(ctx,arm,seed):
        return next(x for x in rows if x['context']==ctx and x['arm']==arm and x['seed']==seed)
    for ctx in CONTEXTS:
        for target,base in [('separation_alignment','no_social'),('separation_alignment_cohesion','separation_alignment'),('separation_alignment_cohesion','no_social')]:
            diffs={}
            for key in METRICS:
                d=np.array([get(ctx,target,seed)[key]-get(ctx,base,seed)[key] for seed in SEEDS])
                diffs[key]={'mean_difference':float(d.mean()),'range':[float(d.min()),float(d.max())],
                            'positive_seeds':int(sum(d>0))}
            paired[f'{ctx}:{target}_minus_{base}']=diffs
    output['paired_differences']=paired
    fname=ROOT/'boids_ablation.json'
    fname.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    for ctx in CONTEXTS:
        print(ctx,flush=True)
        for arm in ARMS:
            o=[r for r in rows if r['context']==ctx and r['arm']==arm]
            print('  ',arm,*(f'{m}={np.mean([r[m] for r in o]):.3f}' for m in METRICS),flush=True)
    print('SAVED',fname,flush=True)

if __name__=='__main__':main()
