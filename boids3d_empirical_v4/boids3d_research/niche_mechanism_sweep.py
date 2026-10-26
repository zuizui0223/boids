"""Synthetic factorial niche mechanisms; no empirical species inference."""
import json
import numpy as np
from boids3d_bridge import simulate
from niche_partition import profiles,partition_summary


def transform(traces, labels, mechanism, strength, seed):
    """Counterfactual occupancy transformations, not dynamical boids forces."""
    rng=np.random.default_rng(seed)
    out=traces.copy()
    n=out.shape[1]
    # Explicit ecological scenarios imposed on generated trajectories.
    if mechanism=='flight_envelope':
        # species-specific reachable height range; physical surrogate
        for i in range(n):
            if labels[i]:
                out[:,i,: ,2]=95+(out[:,i,:,2]-95)*(1-strength*.70)
            else:
                out[:,i,:,2]=95+(out[:,i,:,2]-95)*(1+strength*.25)
    elif mechanism=='resource_layers':
        for i in range(n):
            out[:,i,:,2]+=strength*(32 if labels[i] else -32)
    elif mechanism=='competition':
        # Phenomenological displacement, NOT emergent competition.
        for i in range(n):
            out[:,i,:,2]+=strength*(22 if labels[i] else -22)
    elif mechanism=='time_shift':
        # Temporal segregation is computed on the same spatial trajectories.
        pass
    elif mechanism!='baseline':
        raise ValueError(mechanism)
    out[...,2]=np.clip(out[...,2],5,200)
    return out


def temporal_overlap(traces,labels,strength):
    # Two synthetic activity profiles on common 24-bin daily clock
    t=np.arange(24)
    centers=[12-strength*6,12+strength*6]
    pp=[]
    for i in range(len(labels)):
        d=np.minimum(abs(t-centers[int(labels[i])]),24-abs(t-centers[int(labels[i])]))
        p=np.exp(-0.5*(d/3)**2);pp.append(p/p.sum())
    p=np.stack(pp)
    return partition_summary(p,labels)


def run(seeds=(17,23,47,71,101),strengths=(0,.25,.5,.75,1)):
    rows=[]
    for seed in seeds:
        tr,_=simulate(model='boids_personal',method='topological',seed=seed,n=14,steps=900,burn=180)
        labels=np.arange(14)>=7
        for mechanism in ('baseline','flight_envelope','resource_layers','competition','time_shift'):
            for strength in strengths:
                if mechanism=='time_shift':
                    p=profiles(tr)
                    spatial=partition_summary(p,labels)
                    temporal=temporal_overlap(tr,labels,strength)
                else:
                    tt=transform(tr,labels,mechanism,strength,seed)
                    spatial=partition_summary(profiles(tt),labels)
                    temporal=temporal_overlap(tr,labels,0)
                rows.append({'seed':seed,'mechanism':mechanism,'strength':strength,
                             'spatial_between_minus_within':spatial['between_minus_within'],
                             'spatial_between':spatial['between_group_mean_3d_overlap'],
                             'temporal_between_minus_within':temporal['between_minus_within'],
                             'temporal_between':temporal['between_group_mean_3d_overlap']})
    return rows

if __name__=='__main__':
    rows=run()
    with open('/mnt/data/boids3d_research/niche_mechanism_sweep.json','w') as f:json.dump({'status':'synthetic_counterfactual_not_fitted_dynamics','rows':rows},f,indent=2)
    for mechanism in sorted(set(r['mechanism'] for r in rows)):
        for strength in (0,0.5,1):
            rr=[r for r in rows if r['mechanism']==mechanism and r['strength']==strength]
            print(mechanism,strength,'3D',round(np.mean([r['spatial_between'] for r in rr]),4),'time',round(np.mean([r['temporal_between'] for r in rr]),4))
