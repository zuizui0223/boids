"""Observation-cadence sensitivity of recovering individual vertical-response gains.

Synthetic-only. Uses simulator's shared height field and finite differences; no social
parameters are inferred. Ground vertical speed equals air vertical speed in this model.
"""
import json
import numpy as np
from boids3d_bridge import simulate, Rules


def estimate(traces, stride, dt=0.5, damping=0.75, burn=350):
    # samples in simulate are already spaced 5 steps; effective cadence is 2.5 s
    spacing = dt * 5 * stride
    p = traces[:, :, ::stride, :]
    # central-difference velocity and acceleration on observation positions
    vz = (p[:, :, 2:, 2] - p[:, :, :-2, 2]) / (2 * spacing)
    az = (p[:, :, 2:, 2] - 2*p[:, :, 1:-1, 2] + p[:, :, :-2, 2]) / spacing**2
    # Observation time index: retained samples start at burn=350 in default simulation
    time = (burn + np.arange(p.shape[2])[1:-1] * 5 * stride) * dt
    x, y, z = p[:, :, 1:-1, 0], p[:, :, 1:-1, 1], p[:, :, 1:-1, 2]
    target = 95 + 19*np.sin(0.045*time)[None,None,:] + 19*np.sin(x/65) + 11*np.cos(y/50)
    predictor = target - z
    response = az + damping*vz
    # Acceleration saturation and velocity constraints make this an approximate, not exact, estimator.
    gain = (predictor*response).sum(axis=(0,2)) / np.maximum((predictor**2).sum(axis=(0,2)),1e-12)
    return gain


def run():
    out = {}
    for model in ('boids_shared','boids_personal'):
        tr, truth = simulate(model=model, method='topological', seed=17)
        cases = {}
        for stride in (1,2,4,8):
            pred = estimate(tr,stride)
            correlation = float(np.corrcoef(truth,pred)[0,1]) if np.std(truth)>1e-10 and np.std(pred)>1e-10 else None
            cases[stride*2.5] = {'corr_true_est':correlation,'estimated_range':list(map(float,[pred.min(),pred.max()])), 'estimated_sd':float(pred.std()),'true_sd':float(truth.std())}
        out[model]=cases
    return out

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
