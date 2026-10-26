"""Out-of-sample grain sensitivity for the synthetic dimension crossover.

Same trajectories at different horizontal grains (2, 4, 8 bins per axis)
to quantify whether a 'threshold' is robust to spatial aggregation.
All scenarios are defined before the results are opened.
"""
from dataclasses import replace,asdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json
import numpy as np
from eco_dynamics import EcologicalRules,run,state_information

LEVELS=(0.,.03,.05,.08,.11,.15,.30)
BINS_XY=(2,4,8)
SEEDS=(17,23,47,71,101)
BASE=EcologicalRules(steps=300,burn=100,thin=4,nights=3,resource_contrast=.30,state_tracking=0)

def worker(job):
    depletion,seed=job
    metrics,tr,actual,available,groups=run(replace(BASE,seed=seed,consumption=depletion),return_trajectories=True)
    ans=[]
    for bx in BINS_XY:
        info=state_information(tr,groups,bins_xy=bx)
        ans.append(dict(depletion=depletion,seed=seed,grid=f'{bx}x{bx}x8',bin_xy=bx,
                        I_XY=info['species_horizontal_partition_information_nats'],
                        I_Z_given_XY=info['species_vertical_partition_information_nats'],
                        margin=info['species_vertical_partition_information_nats']-info['species_horizontal_partition_information_nats'],
                        out_individual_gain=float(np.mean(info['species_heldout_individual_gain'])),
                        positive_individuals=int(np.sum(np.array(info['species_heldout_individual_gain'])>0)),
                        H_Z_given_XY=info['vertical_thickness_entropy_nats']))
    return ans

def main():
    with ProcessPoolExecutor(max_workers=4) as p:
        results=list(p.map(worker,[(dep,seed) for dep in LEVELS for seed in SEEDS],chunksize=2))
    rows=sum(results,[])
    grids={}
    for bx in BINS_XY:
        by=[]
        crossings={}
        for dep in LEVELS:
            r=[x for x in rows if x['bin_xy']==bx and x['depletion']==dep]
            by.append({'depletion':dep,
                       'I_XY_mean':float(np.mean([x['I_XY'] for x in r])),
                       'I_Z_given_XY_mean':float(np.mean([x['I_Z_given_XY'] for x in r])),
                       'margin_mean':float(np.mean([x['margin'] for x in r])),
                       'out_individual_gain_mean':float(np.mean([x['out_individual_gain'] for x in r]))})
        for seed in SEEDS:
            r=sorted([x for x in rows if x['bin_xy']==bx and x['seed']==seed],key=lambda x:x['depletion'])
            bracket=None
            for a,b in zip(r[:-1],r[1:]):
                if a['margin']<0<=b['margin']:
                    bracket=[a['depletion'],b['depletion']]
                    break
            crossings[str(seed)]=bracket
        grids[f'{bx}x{bx}x8']={'means':by,'crossover_brackets':crossings}
    out={'status':'synthetic_granularity_robustness_audit','base':asdict(BASE),
         'resolution_grid':BINS_XY,'consumption_grid':LEVELS,'seeds':SEEDS,
         'analysis':grids,'rows':rows,
         'limitation':'Entropy and information are descriptive plug-in estimates, and the crossover is not a validated universal ecological threshold.'}
    path=Path(__file__).with_name('crossover_resolution_audit.json')
    path.write_text(json.dumps(out,indent=2),encoding='utf-8')
    for k,v in grids.items():
        print(k,'brackets',v['crossover_brackets'])
        for q in v['means']:
            if q['depletion'] in (0.,.08,.30):
                print(' ',q['depletion'],'Ixy',round(q['I_XY_mean'],3),'Iz',round(q['I_Z_given_XY_mean'],3),'unseen',round(q['out_individual_gain_mean'],3))
    print('SAVED',path)
if __name__=='__main__':main()
