"""Prospective second synthetic set to check empirical interval calibration.
The interpolated point-predictor is FROZEN from forward_prediction_validation.py.
Calibration errors use the first 24 unseen worlds. Second holdout uses separate
unseen parameter cells/seeds. These are structured synthetic tests: empirical
coverage is not distribution-free coverage for wildlife.
"""
import json
from itertools import product
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
from forward_prediction_validation import fit_interpolators, sample_world, ROOT

NEW_P=(.09,.24)
NEW_D=(.06,.23)
NEW_T=(.4,.75)
NEW_SEEDS=(163,167,173)
ALPHA=.10


def main():
    archive=json.loads((ROOT/'cross_repo_phase_scan.json').read_text())
    first=json.loads((ROOT/'forward_prediction_validation.json').read_text())
    fits=fit_interpolators(archive['raw'])
    # Pre-compute calibration residual thresholds before opening any new outcomes.
    q={}
    for name,fit in fits.items():
        residuals=[]
        for r in first['test_worlds']:
            x=[r['preference'],r['depletion'],r['tracking']]
            residuals.append(abs(r[name]-float(fit['linear'](x).item())))
        # With 24 calibration points, the split-conformal rank is ceil((n+1)*.9)=23.
        # Scenarios are not IID: this is an error-band heuristic, NOT formal coverage.
        quantile_rank=int(np.ceil((len(residuals)+1)*(1-ALPHA)))
        q[name]=float(sorted(residuals)[quantile_rank-1])
    settings=list(product(NEW_P,NEW_D,NEW_T,NEW_SEEDS))
    with ProcessPoolExecutor(max_workers=4) as pool:
        worlds=list(pool.map(sample_world,settings,chunksize=2))
    scores={}
    for name,fit in fits.items():
        a=np.array([r[name] for r in worlds])
        X=np.array([[r['preference'],r['depletion'],r['tracking']] for r in worlds])
        pred=fit['linear'](X).ravel()
        n0=np.full(len(worlds),fit['overall'])
        near=fit['nearest'](X).ravel()
        scores[name]={
            'calibration_abs_error_quantile_90pct':q[name],
            'coverage_24_new_worlds':float(np.mean(abs(pred-a)<=q[name])),
            'mean_interval_width':2*q[name],
            'rmse_interpolated':float(np.sqrt(np.mean((pred-a)**2))),
            'rmse_nearest':float(np.sqrt(np.mean((near-a)**2))),
            'rmse_global_mean':float(np.sqrt(np.mean((n0-a)**2))),
            'mean_bias':float(np.mean(pred-a)),
            'truth_range':[float(min(a)),float(max(a))],
            'n_worlds':len(worlds)
        }
    out={'status':'second_prospective_synthetic_test',
         'forecast_model':'same original 90-world trained trilinear predictor; no refitting',
         'first_test_used_for_error_calibration':24,
         'second_test':{'preferences':NEW_P,'depletions':NEW_D,'tracking':NEW_T,'seeds':NEW_SEEDS,'n':len(worlds)},
         'interval_method':'90% quantile of 24 absolute errors from first test; heuristic as fixed grid violates exchangeability',
         'scores':scores,'new_worlds':worlds,
         'limits':['No wild-animal tracks used.',
                   'Spatial grid fixed 4x4 horizontal, 8 vertical.',
                   'Simulated resources/flight times in arbitrary units.',
                   'Error calibration remains within same generating simulator and fixed environmental settings.',
                   'Point-forecast error vs baselines and interval coverage are different goals.']}
    dest=ROOT/'prediction_uncertainty_revalidation.json'
    dest.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
    for name,s in scores.items():
        print(name,'covered=',s['coverage_24_new_worlds'],'q=',round(s['calibration_abs_error_quantile_90pct'],4),
              'new RMSE=',round(s['rmse_interpolated'],4),'nearest=',round(s['rmse_nearest'],4),flush=True)
    print('SAVED',dest,flush=True)

if __name__=='__main__':main()
