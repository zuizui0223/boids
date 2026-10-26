"""Audit spatial-overlap dependence on pseudocount and voxel grain.

With sparse high-dimensional trajectories, naive Bhattacharyya similarity
is downward biased by unobserved bins; large symmetric smoothing can push
it upward. Neither alone proves the biological absence of partitioning.
"""
from dataclasses import replace,asdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json
import numpy as np
from eco_dynamics import EcologicalRules,run

SEEDS=(17,23,47,71,101)
ARMS={'no_species_difference':{'resource_contrast':0.,'consumption':0.},
      'spatial_sorting':{'resource_contrast':.30,'consumption':0.},
      'state_sorting_shared_depletion':{'resource_contrast':.30,'consumption':.30}}
GRIDS={'xy_4x4':(4,4),'xy_8x8':(8,8),'xy_16x16':(16,16),
       'xyz_4x4x8':(4,4,8),'xyz_8x8x8':(8,8,8),'xyz_16x16x8':(16,16,8)}
PRIORS=(0.,.001,.06)
BASE=EcologicalRules(steps=300,burn=100,thin=4,nights=3)

def spatial_overlap(tr,groups,grid,pseudocount):
    n=tr.shape[1]
    hist=[]
    for i in range(n):
        track=tr[:,i].reshape(-1,3)
        if len(grid)==2:
            scaled=track[:,:2]/np.array([16,16])*np.array(grid)
        else:
            scaled=track/np.array([16,16,8])*np.array(grid)
        idx=np.floor(scaled).astype(int)
        idx=np.minimum(idx,np.array(grid)-1)
        idx=np.maximum(idx,0)
        flat=np.ravel_multi_index(idx.T,grid)
        h=np.bincount(flat,minlength=int(np.prod(grid)))
        hist.append(h)
    hist=np.array(hist,float)
    P=(hist+pseudocount)/np.maximum(hist.sum(axis=1,keepdims=True)+pseudocount*hist.shape[1],1e-9)
    bc=(np.sqrt(P[:,None,:]*P[None,:,:])).sum(axis=2)
    x,y=np.triu_indices(n,1)
    same=groups[x]==groups[y]
    return {'within':float(bc[x[same],y[same]].mean()),
            'between':float(bc[x[~same],y[~same]].mean()),
            'difference':float(bc[x[same],y[same]].mean()-bc[x[~same],y[~same]].mean())}

def job(j):
    arm,seed=j
    m,tr,_,_,g=run(replace(BASE,seed=seed,**ARMS[arm]),return_trajectories=True)
    rows=[]
    for name,grid in GRIDS.items():
        for p in PRIORS:
            stat=spatial_overlap(tr,g,grid,p)
            rows.append({'scenario':arm,'seed':seed,'grid':name,'prior_per_cell':p,**stat})
    return rows

def main():
    with ProcessPoolExecutor(max_workers=4) as ex:
        rows=sum(ex.map(job,[(arm,s) for arm in ARMS for s in SEEDS]),[])
    ss=[]
    for arm in ARMS:
        for grid in GRIDS:
            for p in PRIORS:
                x=[r for r in rows if r['scenario']==arm and r['grid']==grid and r['prior_per_cell']==p]
                ss.append({'scenario':arm,'grid':grid,'prior_per_cell':p,
                           **{key+'_mean':float(np.mean([r[key] for r in x])) for key in ('within','between','difference')}})
    out={'status':'synthetic_overlap_estimator_audit',
         'settings':asdict(BASE),'seeds':SEEDS,'grids':GRIDS,'priors':PRIORS,
         'rows':rows,'summary':ss,
         'caution':'Zero smoothing has unseen-support downward bias; large pseudocounts cause inflated overlap. Compare physical XY and XYZ, local synchronous co-use separately.'}
    path=Path(__file__).with_name('overlap_smoothing_audit.json')
    path.write_text(json.dumps(out,indent=2),encoding='utf-8')
    for row in ss:
        if row['grid'] in ('xy_4x4','xyz_16x16x8') and row['scenario']!='no_species_difference':
            print(row)
    print('SAVED',path)
if __name__=='__main__':main()
