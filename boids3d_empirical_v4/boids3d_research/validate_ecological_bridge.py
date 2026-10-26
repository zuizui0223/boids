"""Cross-scale robustness and never-before-seen-individual heldout validation."""
from dataclasses import replace,asdict
from pathlib import Path
from collections import defaultdict
import numpy as np
import json
from eco_dynamics import run,EcologicalRules,state_information

SEEDS=[17,23,47,71,101]
ARMS={
 'negative_no_species_difference':{'resource_contrast':0.,'social_strength':0.},
 'social_no_preference_difference':{'resource_contrast':0.},
 'resource_preference_only':{'resource_contrast':.24},
 'resource_shared_depletion':{'resource_contrast':.24,'consumption':.20},
 'resource_private_depletion':{'resource_contrast':.24,'consumption':.20,'resource_pool':'private'},
 'state_no_tracking':{'resource_contrast':.24,'state_tracking':0},
 'state_tracking':{'resource_contrast':.24,'state_tracking':.8},
}


def binned_overlap(tr,groups,bins):
    n=tr.shape[1]
    ps=[]
    for i in range(n):
        a=tr[:,i].reshape(-1,3)
        h=np.histogramdd(a,bins=[np.linspace(0,16,bins[0]+1),
                                  np.linspace(0,16,bins[1]+1),
                                  np.linspace(0,8,bins[2]+1)])[0]
        p=h.flatten()+.1
        ps.append(p/p.sum())
    p=np.array(ps)
    BC=np.sqrt(p[:,None,:]*p[None,:,:]).sum(axis=2)
    i,j=np.triu_indices(n,1)
    same=groups[i]==groups[j]
    return {'within':float(BC[i[same],j[same]].mean()),
            'between':float(BC[i[~same],j[~same]].mean()),
            'segregation':float(BC[i[same],j[same]].mean()-BC[i[~same],j[~same]].mean())}


def main():
    rows=[]
    for arm,params in ARMS.items():
        for seed in SEEDS:
            r=EcologicalRules(steps=480,burn=180,nights=3,seed=seed,**params)
            main,tr,a,av,g=run(r,return_trajectories=True)
            inf=state_information(tr,g)
            row={'arm':arm,'seed':seed,
                 'new_individual_gain':float(np.mean(inf['species_heldout_individual_gain'])),
                 'new_individual_positive_count':int(np.sum(np.array(inf['species_heldout_individual_gain'])>0)),
                 'night_gain':float(np.mean(inf['species_heldout_night_gains'])),
                 'horizontal_information_nats':inf['species_horizontal_partition_information_nats'],
                 'vertical_conditional_information_nats':inf['species_vertical_partition_information_nats'],
                 'vertical_effective_states':inf['effective_vertical_states'],
                 'grid_4x4x4':binned_overlap(tr,g,(4,4,4)),
                 'grid_8x8x4':binned_overlap(tr,g,(8,8,4)),
                 'grid_16x16x8':binned_overlap(tr,g,(16,16,8))}
            rows.append(row)
            print(arm,seed,'new_indiv',round(row['new_individual_gain'],3),
                  'Ixy',round(row['horizontal_information_nats'],3),
                  'Iz|xy',round(row['vertical_conditional_information_nats'],3),
                  'segrids',*(round(row[x]['segregation'],3) for x in ('grid_4x4x4','grid_8x8x4','grid_16x16x8')),flush=True)
    by=defaultdict(list)
    for row in rows:by[row['arm']].append(row)
    aggregates={}
    for name,subset in by.items():
        vals={}
        for metric in ('new_individual_gain','night_gain','horizontal_information_nats',
                       'vertical_conditional_information_nats','vertical_effective_states'):
            v=np.array([r[metric] for r in subset])
            vals[metric+'_mean']=float(v.mean())
            vals[metric+'_range']=[float(v.min()),float(v.max())]
        for g in ('grid_4x4x4','grid_8x8x4','grid_16x16x8'):
            v=np.array([r[g]['segregation'] for r in subset]);vals[g+'_segregation_mean']=float(v.mean())
        vals['individual_gain_positive_runs']=int(sum(r['new_individual_gain']>0 for r in subset))
        aggregates[name]=vals
    results={'metadata':{'status':'synthetic', 'individuals_per_simulation':14,'nights':3,
                         'candidate_grid_sizes':[[4,4,4],[8,8,4],[16,16,8]],
                         'individual': 'independent replication unit for out-of-individual holdout'},
             'raw':rows,'summary':aggregates}
    out=Path(__file__).with_name('eco_dynamics_independent_validation.json')
    out.write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('SAVED',out)

if __name__=='__main__':main()
