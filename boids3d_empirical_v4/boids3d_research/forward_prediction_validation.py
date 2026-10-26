"""Frozen synthetic prediction: new parameter cells AND new random seeds.
This evaluates predictability of the toy simulator, not wild animals.
"""
from dataclasses import replace
from itertools import product
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from eco_dynamics import EcologicalRules, run, state_information

ROOT=Path(__file__).parent
BASE=EcologicalRules(steps=300,burn=100,thin=4,nights=3)
PREF=(.06,.21)
DEP=(.04,.16)
TRACK=(.30,.65)
SEEDS=(131,137,149)
TARGETS={'species_horizontal_partition_information_nats':'I_species_XY',
         'species_vertical_partition_information_nats':'I_species_Z_given_XY',
         'state_buffering_advantage':'buffering', 'mean_uptake':'uptake'}


def fit_interpolators(rows):
    axes=[sorted(set(r[key] for r in rows)) for key in ('preference','depletion','tracking')]
    assert [len(a) for a in axes]==[3,3,2] and len(rows)==90
    out={}
    for original,new in TARGETS.items():
        cube=np.empty([len(a) for a in axes])
        within=[]
        for idx in np.ndindex(cube.shape):
            p,d,t=[axes[k][idx[k]] for k in range(3)]
            obs=[r[original] for r in rows if (r['preference'],r['depletion'],r['tracking'])==(p,d,t)]
            assert len(obs)==5
            cube[idx]=np.mean(obs)
            within.extend(np.array(obs)-cube[idx])
        residual_sd=float(np.sqrt(np.sum(np.square(within))/(len(rows)-cube.size)))
        out[new]={'linear':RegularGridInterpolator(axes,cube,method='linear'),
                  'nearest':RegularGridInterpolator(axes,cube,method='nearest'),
                  'overall':np.mean(cube), 'resid_sd':residual_sd}
    return out


def sample_world(params):
    p,d,t,seed=params
    r=replace(BASE,resource_contrast=p,consumption=d,state_tracking=t,seed=seed)
    m,trajectory,_,_,group=run(r,return_trajectories=True)
    inf=state_information(trajectory,group,bins_xy=4)
    return {'preference':p,'depletion':d,'tracking':t,'seed':seed,
            'I_species_XY':inf['species_horizontal_partition_information_nats'],
            'I_species_Z_given_XY':inf['species_vertical_partition_information_nats'],
            'buffering':m['state_buffering_advantage'], 'uptake':m['mean_uptake']}


def main():
    src=json.loads((ROOT/'cross_repo_phase_scan.json').read_text())
    fits=fit_interpolators(src['raw'])
    designs=list(product(PREF,DEP,TRACK,SEEDS))
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(sample_world,designs,chunksize=2))
    metrics={}
    for name,model in fits.items():
        truth=np.array([r[name] for r in results]); x=np.array([[r['preference'],r['depletion'],r['tracking']] for r in results]);
        p={'linear':model['linear'](x).reshape(-1),'nearest':model['nearest'](x).reshape(-1),
           'global_mean':np.full(len(results),model['overall'])}
        scores={}
        for mode,pred in p.items():
            scores[mode]={'rmse':float(np.sqrt(np.mean((truth-pred)**2))),
                          'mae':float(np.mean(abs(truth-pred))),
                          'bias':float(np.mean(pred-truth)),
                          'r2':float(1-np.sum((truth-pred)**2)/np.sum((truth-truth.mean())**2))}
        half=1.645*model['resid_sd']
        scores['approx_90pct_interval_coverage']=float(np.mean(abs(truth-p['linear'])<=half))
        scores['range_truth']=[float(truth.min()),float(truth.max())]
        scores['intervention_direction']={}
        # matched contrast: higher tracking vs lower tracking at fixed other parameters
        high=[]; low=[];pred_high=[];pred_low=[]
        for pref,dep,seed in product(PREF,DEP,SEEDS):
            h=next(r for r in results if (r['preference'],r['depletion'],r['seed'],r['tracking'])==(pref,dep,seed,TRACK[-1]))
            l=next(r for r in results if (r['preference'],r['depletion'],r['seed'],r['tracking'])==(pref,dep,seed,TRACK[0]))
            high.append(h[name]);low.append(l[name]);
            pred_high.append(float(model['linear']([pref,dep,TRACK[-1]])))
            pred_low.append(float(model['linear']([pref,dep,TRACK[0]])))
        real_delta=np.array(high)-np.array(low)
        pred_delta=np.array(pred_high)-np.array(pred_low)
        scores['intervention_direction']={'matching_signs':int(sum(np.sign(real_delta)==np.sign(pred_delta))),
                                          'pairs':len(real_delta),
                                          'predicted_delta_mean':float(np.mean(pred_delta)),
                                          'realized_delta_mean':float(np.mean(real_delta))}
        metrics[name]=scores
    out={'status':'synthetic_never_fit_to_wild_data',
         'claim':'Predict simulator-generated ecological-state patterns at unseen parameter settings and seeds.',
         'training':{'worlds':len(src['raw']),'seeds':[17,23,47,71,101], 'parameter_cells':18},
         'test':{'worlds':len(results),'seeds':SEEDS, 'preference':PREF,'consumption':DEP,'tracking':TRACK},
         'primary':'trilinear surrogate, fixed before test, compared to nearest-cell and global-mean baselines',
         'fixed_grain':'4x4 horizontal cells and 8 altitude states',
         'metrics':metrics,'test_worlds':results,
         'limitations':['Simulator parameter knowledge is supplied, not inferred from real trajectories.',
                        'This is interpolation within known parameter ranges, not extrapolation or field validation.',
                        'Estimated intervals include seed variability but exclude model/parameter uncertainty.',
                        'No synchronized wild co-flight data here for estimating Boids social interaction coefficients.']}
    dest=ROOT/'forward_prediction_validation.json'
    dest.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
    for k,v in metrics.items():
        print(k, 'RMSE', {t:round(v[t]['rmse'],4) for t in ('linear','nearest','global_mean')},
              'coverage',v['approx_90pct_interval_coverage'],flush=True)
    print('SAVED',dest,flush=True)

if __name__=='__main__':main()
