#!/usr/bin/env python3
"""v10: identified-set propagation into explicit *synthetic* 3D state-use niches.

No observed birds, bats, penguins or other animal data are loaded. The coefficients
are not fitted to nature: all candidates share an exactly equal social force at
one calibration distance, but need not agree out of context. This is a bounded
3D paired-agent known-truth counterexample, not a realistic flight model.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np

SOURCE_DISTANCE_M = 10.0
KAPPA0_PER_S2 = -0.003
ALPHAS = (0.0, 0.5, 1.0, 1.5, 2.0)
N_SPECIES = 2
N_PAIRS_PER_SPECIES = 3
N_AGENTS = N_SPECIES * N_PAIRS_PER_SPECIES * 2
DT = 0.10
N_STEPS = 1100
BURN_IN = 250
RECORD_EVERY = 5
DRAG = 0.38
ENV_K_XY = 0.015
ENV_K_Z = 0.023
ORBIT_STRENGTH = 0.002
ACC_NOISE_SD = 1.05
MIN_SOCIAL_D = 1.0
DEFAULT_SEEDS = 10
SEED_START = 20261028

# Main grains predeclared before numerical results are opened. All bin tails are
# pooled into the outermost category; this is a finite categorical state study.
GRAINS = {
    "coarse": {
        "x": (-18., 0., 18.), "y": (-18., 0., 18.), "z": (-12., 0., 12.)
    },
    "fine": {
        "x": (-32., -16., -6., 6., 16., 32.),
        "y": (-32., -16., -6., 6., 16., 32.),
        "z": (-25., -12., -4., 4., 12., 25.)
    }
}
WORLDS = {
    "source_spacing_shared_resources": {
        "initial_pair_distance_m": 10.,
        "species_xy_centers_m": ((0., 0.), (0., 0.)),
        "species_z_centers_m": (-8., 8.),
    },
    "novel_spacing_shared_resources": {
        "initial_pair_distance_m": 25.,
        "species_xy_centers_m": ((0., 0.), (0., 0.)),
        "species_z_centers_m": (-8., 8.),
    },
    "novel_spacing_reassembled_resources": {
        "initial_pair_distance_m": 25.,
        "species_xy_centers_m": ((-9., 0.), (9., 0.)),
        "species_z_centers_m": (-4., 4.),
    },
}


def gamma(alpha: float) -> float:
    return KAPPA0_PER_S2 + alpha / SOURCE_DISTANCE_M**3


def effective_coefficient(alpha: float, distance: float) -> float:
    if distance <= 0:
        raise ValueError("Distance must be positive")
    return gamma(alpha) - alpha / max(MIN_SOCIAL_D, distance)**3


def targets_and_initial_positions(world: dict) -> tuple[np.ndarray, np.ndarray]:
    """Build fixed 12-agent 3D world of six *intraspecific* dyads.

    This model has no interspecific social force and no resource depletion;
    differences in synthetic species niches are NOT competition evidence.
    """
    if world["initial_pair_distance_m"] <= 1:
        raise ValueError("Initial pair separation must exceed the collision floor")
    centers = np.zeros((N_AGENTS, 3), dtype=float)
    start = np.zeros_like(centers)
    idx = 0
    for s in range(N_SPECIES):
        sx, sy = world["species_xy_centers_m"][s]
        sz = world["species_z_centers_m"][s]
        for p in range(N_PAIRS_PER_SPECIES):
            y0 = sy + (p-1)*5.0
            # Fixed pair axis in horizontal plane. Individual-level z preference
            # differs within species but does NOT alter source pair separation.
            angle = 2.*math.pi*p/N_PAIRS_PER_SPECIES + 0.3*s
            direction = np.array([math.cos(angle), math.sin(angle), 0.])
            origin = np.array([sx, y0, sz])
            for role in (0, 1):
                target_offset = np.array([0.8*(role-.5), 0., 3.0*(2.*role-1.)])
                centers[idx] = origin + target_offset
                start[idx] = origin + ((-0.5 if role==0 else 0.5)*world["initial_pair_distance_m"]*direction)
                idx += 1
    for i in range(0,N_AGENTS,2):
        if not np.isclose(np.linalg.norm(start[i+1]-start[i]),world["initial_pair_distance_m"],atol=1e-12):
            raise AssertionError("Not all initial social distances equal the declared context")
    return centers, start


def simulate(world: dict, alpha: float, seed: int, social_on: bool = True,
             steps: int = N_STEPS, burn_in: int = BURN_IN, record_every: int = RECORD_EVERY,
             noise_scale: float = ACC_NOISE_SD,
             shuffle_individual_z_targets: bool=False) -> np.ndarray:
    """Euler-integrated pair-restricted 3D motion, common random numbers per seed.

    Returns (records, 12 agents, xyz). The stochastic acceleration and all
    non-social forces are identical across alpha choices for a given seed.
    """
    if steps<=burn_in or burn_in<0 or record_every<1:
        raise ValueError("Invalid time window")
    if alpha not in ALPHAS:
        raise ValueError("Alpha candidate outside frozen identified set")
    rng = np.random.default_rng(seed)
    noise = rng.normal(size=(steps,N_AGENTS,3)) * noise_scale
    targets, x = targets_and_initial_positions(world)
    if shuffle_individual_z_targets:
        # Negative control: the distribution of individual environment targets
        # stays unchanged within species, but the bird/bat *label* assigned to
        # each z target varies independently with each simulation seed.
        n = N_PAIRS_PER_SPECIES*2
        for species in range(N_SPECIES):
            sl = slice(species*n,(species+1)*n)
            perm = np.random.default_rng(seed + 18037 + species).permutation(n)
            targets[sl,2] = targets[sl,2][perm]
    v = np.zeros_like(x)
    pairs = np.arange(N_AGENTS)^1
    points = []
    for t in range(steps):
        # Restoring force towards individual-specific resource target plus
        # horizontal deflection; not a modeled aerodynamic flight constraint.
        off = x-targets
        env = np.empty_like(x)
        env[:,:2] = -ENV_K_XY*off[:,:2]
        env[:,2] = -ENV_K_Z*off[:,2]
        env[:,0] += -ORBIT_STRENGTH*off[:,1]
        env[:,1] += ORBIT_STRENGTH*off[:,0]
        a = env - DRAG*v + noise[t]
        if social_on:
            r = x[pairs]-x
            d = np.maximum(np.linalg.norm(r,axis=1),MIN_SOCIAL_D)
            a += (gamma(alpha) - alpha/d**3)[:,None]*r
        v = v + DT*a
        x = x + DT*v
        if t>=burn_in and (t-burn_in)%record_every==0:
            points.append(x.copy())
        if not np.isfinite(x).all():
            raise ArithmeticError("Divergent trajectory")
    return np.asarray(points)


def categorical_uses(records: np.ndarray, grain: dict) -> np.ndarray:
    """Per-individual normalized categorical 3D state use; no smoothing or drops.

    Outer bins contain everything below/above the extreme cutpoints. All agents
    contribute equal numbers of fixes, not independent sample replicates.
    """
    a=np.asarray(records,dtype=float)
    if a.ndim!=3 or a.shape[1:]!=(N_AGENTS,3) or not np.isfinite(a).all() or len(a)<1:
        raise ValueError("Expected finite record×agent×xyz cube")
    cuts=[np.asarray(grain[axis],float) for axis in ('x','y','z')]
    if any(not np.all(np.diff(c)>0) for c in cuts):
        raise ValueError("Bin cutpoints must increase")
    shapes=tuple(len(c)+1 for c in cuts)
    hist=np.zeros((N_AGENTS,*shapes),dtype=float)
    idx=[np.searchsorted(c,a[:,:,j],side='right') for j,c in enumerate(cuts)]
    for agent in range(N_AGENTS):
        np.add.at(hist[agent],tuple(x[:,agent] for x in idx),1)
    hist/=float(a.shape[0])
    if not np.allclose(hist.sum(axis=(1,2,3)),1.,atol=1e-12):
        raise AssertionError("Probability mass not preserved")
    return hist


def mutual_information_equal_groups(conditional_distributions: np.ndarray) -> float:
    """Mutual info I(label;state) in nats with uniform label prior; zero-safe."""
    p=np.asarray(conditional_distributions,dtype=float)
    if p.ndim<2 or not np.isfinite(p).all() or np.any(p<0):
        raise ValueError("Invalid conditional probability tensor")
    totals=p.reshape(len(p),-1).sum(axis=1)
    if not np.allclose(totals,1.,atol=1e-10):
        raise ValueError("Every conditional probability array must sum to one")
    mean=p.mean(axis=0)
    # zero categories contribute exactly 0, not NaN; no arbitrary pseudocount.
    nz=p>0
    ratio=np.ones_like(p)
    np.divide(p,mean[None,...],out=ratio,where=nz)
    return float(np.sum(np.where(nz,p*np.log(ratio),0.))/len(p))


def conditional_z_thickness(probability_xyz: np.ndarray) -> float:
    """exp(H(Z | X,Y)) of normalized pooled realized-use support."""
    p=np.asarray(probability_xyz,dtype=float)
    if p.ndim!=3 or not np.isclose(p.sum(),1.,atol=1e-10):
        raise ValueError("Expected normalized XYZ support")
    xy=p.sum(axis=2)
    cond=np.divide(p,xy[:,:,None],out=np.zeros_like(p),where=xy[:,:,None]>0)
    mask=(p>0)&(cond>0)
    h=-float(np.sum(np.where(mask,p*np.log(np.where(mask,cond,1.)),0.)))
    return float(np.exp(h))


def ecological_metrics(agent_probs: np.ndarray) -> dict:
    """Separate species-level and within-species realized niche descriptors."""
    p=np.asarray(agent_probs,dtype=float)
    if p.ndim!=4 or p.shape[0]!=N_AGENTS or not np.allclose(p.sum(axis=(1,2,3)),1.,atol=1e-10):
        raise ValueError("Expected 12 individual probability distributions")
    b=N_PAIRS_PER_SPECIES*2
    species=np.stack([p[:b].mean(axis=0),p[b:].mean(axis=0)])
    xy=species.sum(axis=3)
    i_xy=mutual_information_equal_groups(xy)
    i_all=mutual_information_equal_groups(species)
    i_z=float(max(0.,i_all-i_xy))
    i_ind=[]
    for s in range(N_SPECIES):
        current=p[s*b:(s+1)*b]
        i_ind.append(max(0.,mutual_information_equal_groups(current)-mutual_information_equal_groups(current.sum(axis=3))))
    overlap=float(np.sqrt(xy[0]*xy[1]).sum())
    thickness=conditional_z_thickness(species.mean(axis=0))
    return {
      'species_horizontal_information_nats':i_xy,
      'species_vertical_information_given_xy_nats':i_z,
      'within_species_individual_vertical_information_given_xy_nats':float(np.mean(i_ind)),
      'species_horizontal_bhattacharyya_overlap':overlap,
      'effective_vertical_states_given_xy':thickness,
    }


def joint_species_state(agent_probs: np.ndarray) -> np.ndarray:
    n=N_PAIRS_PER_SPECIES*2
    return np.stack([agent_probs[:n].mean(axis=0), agent_probs[n:].mean(axis=0)]) / 2.


def total_variation(p: np.ndarray,q: np.ndarray) -> float:
    if p.shape!=q.shape or not np.isclose(p.sum(),1.,atol=1e-10) or not np.isclose(q.sum(),1.,atol=1e-10):
        raise ValueError("TV requires comparable normalized distributions")
    return float(0.5*np.abs(p-q).sum())


def metric_envelopes(mean_agent_probs: dict[float,np.ndarray]) -> dict:
    """Parameter uncertainty envelope of replicate-averaged distributions.

    A finite 5-point grid is not guaranteed to bound any continuum of valid
    parameter values! This is explicitly a *tested candidate-set envelope*.
    """
    metrics={str(a):ecological_metrics(p) for a,p in mean_agent_probs.items()}
    joint={a:joint_species_state(p) for a,p in mean_agent_probs.items()}
    metric_names=tuple(next(iter(metrics.values())))
    spans={k:{'min':float(min(r[k] for r in metrics.values())),
              'max':float(max(r[k] for r in metrics.values()))}
           for k in metric_names}
    for item in spans.values(): item['width']=item['max']-item['min']
    distance={f'{a}:{b}':total_variation(joint[a],joint[b])
              for a,b in itertools.combinations(sorted(joint),2)}
    return {'metrics_by_candidate':metrics,'metric_ranges':spans,
        'maximum_joint_species_xyz_total_variation':max(distance.values(),default=0.),
        'maximum_joint_species_xyz_tv_pair':max(distance,key=distance.get) if distance else None,
        'pairwise_joint_species_xyz_total_variation':distance}


def experiment(seeds: int=DEFAULT_SEEDS, worlds: dict|None=None,
               alphas: tuple[float,...]=ALPHAS,
               steps: int=N_STEPS,burn_in: int=BURN_IN) -> dict:
    if seeds<2 or len(alphas)<2:
        raise ValueError("Need >=2 process seeds and >=2 candidate coefficients")
    if any(a not in ALPHAS for a in alphas):
        raise ValueError("Parameter candidate outside the frozen set")
    worlds=WORLDS if worlds is None else worlds
    for a in alphas:
        if abs(effective_coefficient(a,SOURCE_DISTANCE_M)-KAPPA0_PER_S2)>1e-14:
            raise AssertionError("Identified-set calibration contract failed")
    result={}
    seed_ids=[SEED_START+i for i in range(seeds)]
    for world_name,world in worlds.items():
        group={}
        for a in alphas:
            collected={g:[] for g in GRAINS}
            for seed in seed_ids:
                records=simulate(world,a,seed,steps=steps,burn_in=burn_in)
                for grain_name,grain in GRAINS.items():
                    collected[grain_name].append(categorical_uses(records,grain))
            group[a]={grain_name:np.stack(lst,axis=0) for grain_name,lst in collected.items()}
        grain_out={}
        for grain_name in GRAINS:
            mean_probs={a:np.mean(group[a][grain_name],axis=0) for a in alphas}
            envelope=metric_envelopes(mean_probs)
            # Distinguish stochastic replicate noise from uncertainty over alpha.
            replicate_mi={str(a):{
                'species_horizontal_information_sd':float(np.std([ecological_metrics(p)['species_horizontal_information_nats'] for p in group[a][grain_name]],ddof=1)),
                'species_vertical_information_given_xy_sd':float(np.std([ecological_metrics(p)['species_vertical_information_given_xy_nats'] for p in group[a][grain_name]],ddof=1))
            } for a in alphas}
            grain_out[grain_name]={**envelope,'within_candidate_seed_variability':replicate_mi}
        result[world_name]={'initial_pair_distance_m':world['initial_pair_distance_m'],'grains':grain_out}
    return {
       'id':'boids-v10-finite-identified-set-to-3d-niche-known-truth',
       'status':'SYNTHETIC_CANDIDATE_SET_PROPAGATION_NOT_OBSERVED_ECOLOGICAL_FORECAST',
       'calibration':{'distance_m':SOURCE_DISTANCE_M,'effective_steering_per_s2':KAPPA0_PER_S2,
                      'candidate_alpha_m3_s2':list(alphas),
                      'candidate_gamma_per_s2':[gamma(a) for a in alphas],
                      'source_mechanism':'all 5 candidates have exactly equal instantaneous social force when paired distance is 10 m; not fitted to animals'},
       'simulation':{'n_species':N_SPECIES,'individuals_per_species':N_PAIRS_PER_SPECIES*2,
                     'dyads_within_each_species':N_PAIRS_PER_SPECIES,
                     'steps':steps,'burn_in':burn_in,'dt_seconds':DT,'record_every':RECORD_EVERY,
                     'seeds':seed_ids,'field':'fixed species-specific 3D target locations, individual offsets, harmonic restoring force, horizontal orbital term, Gaussian acceleration noise, and pair-restricted social force',
                     'competition':'NO modeled resource consumption or interspecific competition',
                     'spatial_bins':GRAINS},
       'worlds':result,
       'interpretation_boundary':[
        'A finite grid of 5 candidate parameters is NOT a confidence region or continuous identified-set bound; effects beyond sampled alphas are not excluded.',
        'Information values and probability differences refer solely to synthetic realized state use, not empirical niche widths, resource specialization or competition.',
        'The model does not contain realistic aerodynamics, collision resolution, or measured resource fields.',
        'Each stochastic simulation seed is a paired computational replicate. The 12 generated individuals are not 12 independent biological replicates.',
        'Grid resolution and source calibration geometry are stipulated; there are no independently held-out real species, nights, sites or instrument error calibrations.' ]
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seeds',type=int,default=DEFAULT_SEEDS)
    parser.add_argument('--out',type=Path,default=Path('validation_v10/results/niche_identified_set_v10.json'))
    args=parser.parse_args()
    output=experiment(seeds=args.seeds)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    for name,world in output['worlds'].items():
        a=world['grains']['coarse']
        v=a['metric_ranges']['species_vertical_information_given_xy_nats']
        h=a['metric_ranges']['species_horizontal_information_nats']
        print(f"{name}: I(S;XY) [{h['min']:.4f},{h['max']:.4f}]; I(S;Z|XY) [{v['min']:.4f},{v['max']:.4f}]; joint TV max {a['maximum_joint_species_xyz_total_variation']:.4f}")

if __name__=='__main__':
    main()
