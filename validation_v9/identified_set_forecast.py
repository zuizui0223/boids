#!/usr/bin/env python3
"""Explicit known-truth Boids identified-set transfer counterexample.

This is a deterministically specified pair-motion mathematical test, not a
fit to any observed bat/pigeon. Under one calibration distance d0 the
cohesion and separation forces are algebraically collinear. All theta along
an identified line make exactly the same one-step prediction there, but can
predict different spatial use and spacing when the context changes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

D0_M=10.0
CALIBRATED_EFFECTIVE_COEFFICIENT=-0.003   # 1/s^2 for candidate acceleration per unit separation
ALPHAS=(0.0,0.5,1.0,1.5,2.0)             # m^3/s^2 for this particular inverse-cubic kernel
INITIAL_DISTANCES_M=(6.0,10.0,15.0,25.0)
T_SECONDS=30.0
DT_SECONDS=.02
DRAG_S_INV=.5
MIN_DISTANCE_M=1.0


def gamma_on_identified_set(alpha:float) -> float:
    """Every (alpha,gamma) combination has κ(d0) equal to the calibrated κ."""
    return CALIBRATED_EFFECTIVE_COEFFICIENT+alpha/D0_M**3


def effective_steering(alpha:float,gamma:float,distance:float) -> float:
    return gamma-alpha/max(MIN_DISTANCE_M,distance)**3


def simulate_pair_distance(initial_distance:float, alpha:float,
                           duration:float=T_SECONDS, step:float=DT_SECONDS) -> dict:
    if initial_distance<=MIN_DISTANCE_M or step<=0 or duration<=0 or abs(round(duration/step)-duration/step)>1e-8:
        raise ValueError('Invalid simulation frame or distance')
    gamma=gamma_on_identified_set(alpha)
    a=np.array([-initial_distance/2,0.,0.]);b=-a
    va=np.zeros(3);vb=np.zeros(3)
    distances=[initial_distance]
    for _ in range(int(round(duration/step))):
        r=b-a;d=float(np.linalg.norm(r));kernel=effective_steering(alpha,gamma,d)
        accel=kernel*r
        va+=step*(accel-DRAG_S_INV*va)
        vb+=step*(-accel-DRAG_S_INV*vb)
        a+=step*va;b+=step*vb
        distances.append(float(np.linalg.norm(b-a)))
    return {'initial_distance_m':initial_distance,
            'final_distance_m':distances[-1],
            'mid_to_end_mean_distance_m':float(np.mean(distances[len(distances)//2:])),
            'maximum_absolute_speed_m_s':float(max(np.linalg.norm(va),np.linalg.norm(vb)))}


def experiment() -> dict:
    for alpha in ALPHAS:
        v=effective_steering(alpha,gamma_on_identified_set(alpha),D0_M)
        if abs(v-CALIBRATED_EFFECTIVE_COEFFICIENT)>1e-15:
            raise RuntimeError('ALGORITHMIC_FROZEN_CALIBRATION_MISMATCH')
    out={}
    for d in INITIAL_DISTANCES_M:
        traj={str(alpha):simulate_pair_distance(d,alpha) for alpha in ALPHAS}
        endpoint=np.array([z['final_distance_m'] for z in traj.values()])
        mid=np.array([z['mid_to_end_mean_distance_m'] for z in traj.values()])
        out[str(d)]={
          'candidate_final_distances_m':{k:v['final_distance_m'] for k,v in traj.items()},
          'endpoint_identified_set_range_m':[float(endpoint.min()),float(endpoint.max())],
          'endpoint_forecast_width_m':float(endpoint.max()-endpoint.min()),
          'mid_to_end_mean_range_m':[float(mid.min()),float(mid.max())],
          'mid_to_end_mean_width_m':float(mid.max()-mid.min())
        }
    return {
      'id':'boids-v9-identified-set-out-of-context-stress-test',
      'evidence_status':'MATHEMATICAL_KNOWN_TRUTH_ONLY_NOT_WILD_ANIMAL_DATA',
      'steering_kernels':'social acceleration on i = [gamma - alpha/d**3] * (x_j - x_i); acceleration on j is opposite',
      'source_calibration_distance_m':D0_M,
      'known_calibrated_effective_coefficient':CALIBRATED_EFFECTIVE_COEFFICIENT,
      'theta_definition':'For every listed alpha, gamma = kappa0 + alpha / source_distance**3; the entire set fits one fixed source-distance force exactly',
      'alphas':list(ALPHAS),
      'gammas':[gamma_on_identified_set(a) for a in ALPHAS],
      'simulator':{'duration_seconds':T_SECONDS,'dt_seconds':DT_SECONDS,'drag_s_inv':DRAG_S_INV,
       'initial_velocities':'zero','initial_position':'±initial_distance/2 along the 3D x axis',
       'noise':'none; exact deterministic equation integration'},
      'unseen_initial_distance_contexts_m':list(INITIAL_DISTANCES_M),
      'worlds':out,
      'claim_boundary':[
       'A perfect one-step fit at one neighbor distance cannot separately identify alpha and gamma for this pair of specified social kernels.',
       'The model-predicted spacing across other distances varies over that identified set, so an apparently predictive microscopic law can fail to determine a unique out-of-context spatial pattern.',
       'Numerical units, finite coefficient range and 30-second horizon were chosen for illustration; results are not fitted to bats, pigeons, or a species-specific niche.',
       'The distance and social force are movement state variables, not by themselves realized environmental or resource niche distributions.' ]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path('validation_v9/results/identified_set_spatial_transfer_v9.json'))
    args=parser.parse_args()
    result=experiment()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
    for d,r in result['worlds'].items():
        print(f"init {d} m, identical calibrated κ at {D0_M} m → 30-s final distance envelope {r['endpoint_identified_set_range_m']}, width {r['endpoint_forecast_width_m']:.3f} m")

if __name__=='__main__':main()
