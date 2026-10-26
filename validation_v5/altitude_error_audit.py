#!/usr/bin/env python3
"""Known-truth identification audit for short-step GPS vertical-transition scores.

No wild animal records; simulator scenarios are explicitly illustrative, not
estimated device-error magnitudes. Reuses the frozen M0/M1 score definition.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

# Same 3-class bins and prior strengths as the observed v4 model.
def bin3(x: float, threshold: float = 0.5) -> int:
    return 0 if x < -threshold else (2 if x > threshold else 1)


def transition_probabilities(c):
    c = np.asarray(c, dtype=float)
    marginal = c.sum(axis=(0, 1))
    p0 = (marginal + 0.5) / (marginal.sum() + 1.5)
    prev = c.sum(axis=1)
    p1 = (prev + 12.0 * p0[None, :]) / (prev.sum(axis=1, keepdims=True) + 12.0)
    return p0, p1


def summarize_loo(counts, meta):
    """Hold out a whole individual x night and weight individuals equally."""
    keys = sorted(counts)
    out = {}
    for k in keys:
        train = sum((counts[j] for j in keys if j != k), np.zeros((3, 3, 3), dtype=int))
        p0, p1 = transition_probabilities(train)
        target = counts[k].astype(float)
        n = target.sum()
        if n <= 0:
            continue
        delta = float(np.sum(target * (np.log(p1[:, None, :]) - np.log(p0[None, None, :]))) / n)
        out.setdefault(meta[k]['id'], []).append(delta)
    return float(np.mean([np.mean(v) for v in out.values()]))


def simulate_one(seed, *, velocity_rho=0., gps_z_sigma_m=0., speed_sd_m_s=0.8,
                 dt_s=30., n_individuals=8, n_nights=3, n_steps=240):
    """True velocity is AR(1), GPS error is independent at each location.

    When rho=0 the TRUE successive velocities are independent: there is no
    biological inertia. Differenced observations share the middle GPS error.
    """
    if not -1 < velocity_rho < 1 or gps_z_sigma_m < 0 or dt_s <= 0 or n_steps < 6:
        raise ValueError('Invalid known-truth configuration')
    rng = np.random.default_rng(seed)
    counts, meta = {}, {}
    r1s, r2s, true_r1s = [], [], []
    for iid in range(n_individuals):
        for night in range(n_nights):
            true_v = np.empty(n_steps)
            true_v[0] = rng.normal(0, speed_sd_m_s)
            innovations = rng.normal(0, speed_sd_m_s * np.sqrt(1-velocity_rho**2), n_steps - 1)
            for t in range(1, n_steps):
                true_v[t] = velocity_rho * true_v[t-1] + innovations[t-1]
            true_z = np.r_[0., np.cumsum(true_v * dt_s)]
            z_obs = true_z + rng.normal(0, gps_z_sigma_m, n_steps + 1)
            observed_v = np.diff(z_obs) / dt_s
            states = np.where(observed_v < -0.5, 0, np.where(observed_v > 0.5, 2, 1))
            c = np.zeros((3, 3, 3), dtype=int)
            for a, b in zip(states[:-1], states[1:]):
                c[int(a), 1, int(b)] += 1  # wind not used in M0/M1
            k = f'I{iid:02d}::N{night:02d}'
            counts[k] = c
            meta[k] = {'id': f'I{iid:02d}', 'night': night}
            r1s.append(float(np.corrcoef(observed_v[:-1], observed_v[1:])[0, 1]))
            r2s.append(float(np.corrcoef(observed_v[:-2], observed_v[2:])[0, 1]))
            true_r1s.append(float(np.corrcoef(true_v[:-1], true_v[1:])[0, 1]))
    theo_noise_variance = (gps_z_sigma_m / dt_s)**2
    signal_var = speed_sd_m_s**2
    theoretical_r1 = (velocity_rho * signal_var - theo_noise_variance) / (signal_var + 2 * theo_noise_variance)
    theoretical_r2 = (velocity_rho**2 * signal_var) / (signal_var + 2 * theo_noise_variance)
    return {
        'heldout_M1_minus_M0_nats_per_transition': summarize_loo(counts, meta),
        'observed_climb_lag1_pearson': float(np.mean(r1s)),
        'observed_climb_lag2_pearson': float(np.mean(r2s)),
        'true_climb_lag1_pearson': float(np.mean(true_r1s)),
        'theoretical_climb_lag1': float(theoretical_r1),
        'theoretical_climb_lag2': float(theoretical_r2),
        'synthetic_transitions': n_individuals*n_nights*(n_steps-1),
    }


def evaluate(n_seeds=30, first_seed=20261027):
    configs = [
        ('iid_true_velocity_no_gps_error', 0., 0.),
        ('iid_true_velocity_10m_error', 0., 10.),
        ('iid_true_velocity_20m_error', 0., 20.),
        ('iid_true_velocity_40m_error', 0., 40.),
        ('persistent_velocity_no_gps_error', 0.7, 0.),
        ('persistent_velocity_20m_error', 0.7, 20.),
    ]
    result = {
        'study': 'boids-gps-altitude-error-known-truth-v5',
        'kind': 'synthetic identifiability stress test, not observed GPS-error estimation',
        'fixed_simulation': {'velocity_sd_m_s':0.8, 'sampling_seconds':30,
                             'individuals':8, 'nights_per_individual':3, 'steps_per_night':240,
                             'climb_threshold_m_s':0.5, 'M0_prior':0.5, 'M1_prior':12,
                             'gps_errors':'iid Gaussian errors on positions'},
        'n_random_seeds':n_seeds, 'first_seed': first_seed,
        'formula': {
            'lag1_corr':'(rho*sigma_v^2 - sigma_gps^2/dt^2)/(sigma_v^2 + 2*sigma_gps^2/dt^2)',
            'lag2_corr':'(rho^2*sigma_v^2)/(sigma_v^2 + 2*sigma_gps^2/dt^2)'},
        'scenarios':{},
        'claim_limits':[
            'A positive held-out M1-M0 score does not uniquely identify biological inertia.',
            'GPS position-error magnitude and its temporal correlation are not estimated from observed bats.',
            'Theoretical correlations assume stationary AR(1) true velocity, independent white GPS altitude error, and regular cadence.',
            'Synthetic outcomes cannot update the frozen v4 wild-data statistics or establish social Boids coefficients.'
        ]
    }
    keys=('heldout_M1_minus_M0_nats_per_transition','observed_climb_lag1_pearson',
          'observed_climb_lag2_pearson','true_climb_lag1_pearson')
    for label, rho, gps_sigma in configs:
        arr=[simulate_one(first_seed+i, velocity_rho=rho, gps_z_sigma_m=gps_sigma) for i in range(n_seeds)]
        r={'rho_true_velocity':rho,'gps_altitude_error_sd_m':gps_sigma,
           'theoretical_climb_lag1':arr[0]['theoretical_climb_lag1'],
           'theoretical_climb_lag2':arr[0]['theoretical_climb_lag2']}
        for key in keys:
            vals=np.array([a[key] for a in arr])
            r[key]={'mean':float(vals.mean()),'min':float(vals.min()),'max':float(vals.max()),
                    'q025':float(np.quantile(vals,0.025)),'q975':float(np.quantile(vals,0.975)),
                    'positive_replicates':int(np.sum(vals>0))}
        result['scenarios'][label]=r
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seeds',type=int,default=30)
    parser.add_argument('--out',type=Path,default=Path('results/gps_altitude_error_known_truth_v5.json'))
    args=parser.parse_args()
    if args.seeds < 1: parser.error('--seeds must be positive')
    report=evaluate(args.seeds)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    for name,x in report['scenarios'].items():
        print(name,'gain=',round(x['heldout_M1_minus_M0_nats_per_transition']['mean'],5),
              'observed r1=',round(x['observed_climb_lag1_pearson']['mean'],3),
              'r2=',round(x['observed_climb_lag2_pearson']['mean'],3))

if __name__=='__main__':main()
