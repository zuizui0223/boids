"""Matched-clock 3D local co-use versus time-shifted pseudo-synchrony.

This is the temporally local counterpart to distribution-level niche overlap.
Time shifts break simultaneous movement but preserve each individual trajectory's
marginal occupancy and temporal autocorrelation (circular-shift null).
A positive difference cannot by itself identify aggression/competition because
shared environmental forcing or coordination may also generate it.
"""
from __future__ import annotations
from dataclasses import replace,asdict
from pathlib import Path
from itertools import combinations
import numpy as np
import json
from eco_dynamics import EcologicalRules,run

SEEDS=(17,23,47,71,101)
ARMS={'social_no_difference':dict(resource_contrast=0.,consumption=0),
      'preference_no_depletion':dict(resource_contrast=.3,consumption=0),
      'shared_depletion':dict(resource_contrast=.3,consumption=.3,resource_pool='shared'),
      'species_only_depletion':dict(resource_contrast=.3,consumption=.3,resource_pool='species'),
      'personal_state_mixture':dict(resource_contrast=.0,consumption=0,behavioral_mixture_var=1.)}
BASE=EcologicalRules(nights=3,steps=460,burn=140,thin=4)


def sample_local(track,group,dxy_max=2.0):
    # [night,individual,time,xyz], 16x16 periodic horizontal domain.
    n=track.shape[1]
    result={}
    for label,pairs in [('conspecific',[(i,j) for i,j in combinations(range(n),2) if group[i]==group[j]]),
                        ('heterospecific',[(i,j) for i,j in combinations(range(n),2) if group[i]!=group[j]])]:
        avg=[];total_fixes=0
        for i,j in pairs:
            diff=track[:,i,:,:2]-track[:,j,:,:2]
            diff=(diff+8)%16-8
            close=np.linalg.norm(diff,axis=-1)<=dxy_max
            count=int(close.sum())
            if count>=3:
                absz=np.abs(track[:,i,:,2]-track[:,j,:,2])
                avg.append(float(absz[close].mean()))
                total_fixes+=count
        result[label]={'mean_nearby_absolute_height_difference':float(np.mean(avg)) if avg else None,
                       'eligible_pairs':len(avg),'nearby_pair_times':total_fixes}
    return result


def permutation(tr,group,seed=1,reps=199):
    rng=np.random.default_rng(seed)
    obs=sample_local(tr,group)
    n,t=tr.shape[1:3]
    nrep=[]
    for _ in range(reps):
        shifted=tr.copy()
        for night in range(tr.shape[0]):
            for i in range(n):
                amount=int(rng.integers(1,t))
                shifted[night,i]=np.roll(tr[night,i],amount,axis=0)
        nrep.append(sample_local(shifted,group))
    out={}
    for kind in ('conspecific','heterospecific'):
        q=obs[kind]['mean_nearby_absolute_height_difference']
        vals=np.array([x[kind]['mean_nearby_absolute_height_difference'] for x in nrep if x[kind]['mean_nearby_absolute_height_difference'] is not None])
        out[kind]={'observed':q,'eligible_pairs':obs[kind]['eligible_pairs'],
                   'nearby_pair_times':obs[kind]['nearby_pair_times'],
                   'null_mean':float(np.mean(vals)) if len(vals) else None,
                   'null_centered_excess':float(q-vals.mean()) if q is not None and len(vals) else None,
                   'p_upper':float((1+np.sum(vals>=q))/(len(vals)+1)) if q is not None and len(vals) else None,
                   'n_null':int(len(vals))}
    return out


def main():
    rows=[]
    for arm,params in ARMS.items():
        for seed in SEEDS:
            m,tr,a,av,group=run(replace(BASE,seed=seed,**params),return_trajectories=True)
            results=permutation(tr,group,seed=seed+900,reps=99)
            rows.append({'arm':arm,'seed':seed,'results':results})
            print(arm,seed,'same-group-excess',results['conspecific']['null_centered_excess'],
                 'different-group-excess',results['heterospecific']['null_centered_excess'],flush=True)
    summ={}
    for arm in ARMS:
        rr=[r['results'] for r in rows if r['arm']==arm]
        summ[arm]={}
        for pair in ('conspecific','heterospecific'):
            vals=np.array([x[pair]['null_centered_excess'] for x in rr
                           if x[pair]['null_centered_excess'] is not None],dtype=float)
            summ[arm][pair]={'mean_null_centered_excess':float(np.mean(vals)) if len(vals) else None,
               'valid_seed_count':len(vals),
               'positive_seeds':int(np.sum(vals>0)),
               'mean_eligible_pairs':float(np.mean([x[pair]['eligible_pairs'] for x in rr])),
               'p_below_005_runs':int(sum(x[pair]['p_upper'] is not None and x[pair]['p_upper']<=.05 for x in rr))}
    out={'status':'synthetic_time_alignment_diagnostic',
         'boundary':'Random circular shifts change local encounters and preserve marginal location; detected synchrony is not identified as interference competition.',
         'parameters':asdict(BASE),'seeds':SEEDS,'arms':ARMS,'results':rows,'summary':summ}
    path=Path(__file__).with_name('synchronous_local_test.json')
    path.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print('SAVED',path)
if __name__=='__main__':main()
