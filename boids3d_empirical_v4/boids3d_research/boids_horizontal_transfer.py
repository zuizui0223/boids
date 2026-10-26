"""ODSP-style falsification: does species XY sorting transfer to future nights?
Same ecological rules, fresh initial locations every night; no empirical source.
"""
from dataclasses import replace
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path
from collections import defaultdict
import numpy as np
import json
from eco_dynamics import EcologicalRules,run,state_information
from boids_ablation import SEEDS,ARMS,CONTEXTS,BASE
ROOT=Path(__file__).parent
TEST_CONTEXTS=('neutral','resource_contrast','depleted_resource')
N_XY=4
PRIOR=.5

def xy_transfer(tr, group):
    nights,n,ntime,_=tr.shape
    ix=np.floor(tr[...,0]*N_XY/16).astype(int).clip(0,N_XY-1)
    iy=np.floor(tr[...,1]*N_XY/16).astype(int).clip(0,N_XY-1)
    counts=np.empty((nights,n,N_XY*N_XY),dtype=float)
    for t in range(nights):
        for i in range(n):
            counts[t,i]=np.bincount(ix[t,i]*N_XY+iy[t,i],minlength=N_XY*N_XY)
    gains=[]
    pernight_mi=[]
    for hold in range(nights):
        train=counts[np.arange(nights)!=hold]
        pergroup=np.stack([train[:,group==s].sum(axis=(0,1)) for s in (0,1)])
        pool=pergroup.sum(axis=0)
        P=(pergroup+PRIOR)/(pergroup.sum(axis=1,keepdims=True)+N_XY*N_XY*PRIOR)
        P0=(pool+PRIOR)/(pool.sum()+N_XY*N_XY*PRIOR)
        lograt=np.log(P/P0)
        gains.extend([float((counts[hold,i]*lograt[group[i]]).sum()/counts[hold,i].sum()) for i in range(n)])
        by_species=np.stack([counts[hold,group==s].sum(axis=0) for s in (0,1)])
        total=by_species.sum()
        p_sx=by_species/total;p_s=p_sx.sum(axis=1,keepdims=True);p_x=p_sx.sum(axis=0,keepdims=True)
        info=float(np.sum(np.where(p_sx>0,p_sx*np.log(np.maximum(p_sx,1e-300)/np.maximum(p_s*p_x,1e-300)),0)))
        pernight_mi.append(info)
    return {'mean_heldout_night_xy_log_gain':float(np.mean(gains)),
            'fraction_positive_individual_nights':float(np.mean(np.array(gains)>0)),
            'mean_within_night_I_species_XY':float(np.mean(pernight_mi))}

def worker(spec):
    ctx,arm,seed=spec
    params={**CONTEXTS[ctx],**ARMS[arm],'seed':seed}
    stats,tr,_,_,g=run(replace(BASE,**params),return_trajectories=True)
    transfer=xy_transfer(tr,g)
    info=state_information(tr,g,bins_xy=N_XY)
    return {'context':ctx,'arm':arm,'seed':seed,
            'pooled_I_species_XY':info['species_horizontal_partition_information_nats'],
            **transfer}

def main():
    jobs=list(product(TEST_CONTEXTS,ARMS,SEEDS))
    with ProcessPoolExecutor(max_workers=4) as pool:
        raw=list(pool.map(worker,jobs,chunksize=2))
    sums={}
    for ctx in TEST_CONTEXTS:
        for arm in ARMS:
            rr=[r for r in raw if r['context']==ctx and r['arm']==arm]
            sums[f'{ctx}/{arm}']={key:float(np.mean([row[key] for row in rr])) for key in (
                'pooled_I_species_XY','mean_within_night_I_species_XY',
                'mean_heldout_night_xy_log_gain','fraction_positive_individual_nights')}
    out={'status':'synthetic, exploratory ODSP-type cross-night transfer audit',
         'notes':['Species labels differ only by conspecific interactions in neutral setting.',
                  'Pooled or within-night identity information is not alone a replicable niche.',
                  'Night-out gain evaluated with training nights only and equal individual weights.'],
         'settings':{'seeds':SEEDS,'contexts':TEST_CONTEXTS,'arms':ARMS,'horizontal_grid':'4x4', 'smooth':PRIOR},
         'summary':sums,'raw':raw}
    dest=ROOT/'boids_horizontal_transfer.json';dest.write_text(json.dumps(out,indent=2),encoding='utf-8')
    for k,v in sums.items():print(k,*[f'{n}={val:.3f}' for n,val in v.items()],flush=True)
    print('SAVED',dest,flush=True)

if __name__=='__main__':main()
