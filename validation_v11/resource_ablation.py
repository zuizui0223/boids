#!/usr/bin/env python3
"""v11: predeclared known-truth ecological-driver ablation of a paired 3D Boids toy.

Synthetic ONLY: this is not inference about birds, bats, competition or real resource
fields. The experiment separates *imposed species-specific habitat targets* from
within-dyad separation/cohesion. All true generated individuals have equal effort.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
import numpy as np

# Keep v9/v10 illustrative inverse-force family and coarse/fine cutpoints fixed.
SOURCE_D = 10.0
KAPPA0 = -0.003
ALPHAS = (0.0, 1.0, 2.0)
N_AGENTS = 12  # two pseudo-species, three same-species pairs each, two roles/pair
SEEDS = tuple(range(20261028, 20261040))
STEPS = 650
BURN_IN = 200
RECORD_EVERY = 4
DT = 0.1
DRAG = 0.38
ENV_K_XY = 0.015
ENV_K_Z = 0.023
ORBIT = 0.002
ACC_NOISE = 1.05
INITIAL_DISTANCE = 25.0  # a fixed novel distance not used to calibrate force family
SMOOTHING = 0.5
BOOTSTRAP_B = 1200
BOOTSTRAP_SEED = 20261027
N_TRAIN_SEEDS = 8
GRAINS = {
    'coarse': {'x': (-18., 0., 18.), 'y': (-18., 0., 18.), 'z': (-12., 0., 12.)},
    'fine': {'x': (-32.,-16.,-6.,6.,16.,32.), 'y': (-32.,-16.,-6.,6.,16.,32.),
             'z': (-25.,-12.,-4.,4.,12.,25.)},
}
SCENARIOS = {
    'no_species_resource_contrast': (0.0, 0.0),
    'vertical_resource_contrast': (0.0, 8.0),
    'horizontal_resource_contrast': (9.0, 0.0),
    'both_resource_contrasts': (9.0, 8.0),
}


def gamma(alpha: float) -> float:
    return KAPPA0 + alpha / SOURCE_D**3


def force_coefficient(alpha: float, d: np.ndarray | float):
    return gamma(alpha) - alpha / np.maximum(d, 1.0)**3


def targets_and_starts(x_difference: float, z_difference: float, role_z_offset:float=2.5):
    """Species only differ in targeted habitat, not initial pair configurations.

    Synthetic species s has center ±x_difference, ±z_difference. All six pairs
    begin at the SAME species-neutral positions and target-offset pattern.
    """
    targets = np.empty((N_AGENTS, 3), float)
    starts = np.empty_like(targets)
    k=0
    for s in range(2):
        sign=-1.0 if s==0 else 1.0
        for pair in range(3):
            y=(pair-1)*5.0
            angle=2*math.pi*pair/3
            direction=np.array([math.cos(angle),math.sin(angle),0.])
            for role in range(2):
                role_sign=-1.0 if role==0 else 1.0
                # Individual fixed vertical offsets are identical in both species.
                targets[k]=[sign*x_difference + .4*role_sign, y,
                            sign*z_difference + role_z_offset*role_sign]
                starts[k]=[0., y, 0.] + .5*role_sign*INITIAL_DISTANCE*direction
                k+=1
    # No species label information in starts or dyad geometry.
    np.testing.assert_array_equal(starts[:6],starts[6:])
    np.testing.assert_allclose(np.linalg.norm(starts[1::2]-starts[::2],axis=1),INITIAL_DISTANCE)
    return targets, starts


def simulate(x_difference: float,z_difference: float,alpha: float,seed: int,
             social_on: bool,steps: int=STEPS,burn_in: int=BURN_IN,
             record_every: int=RECORD_EVERY,
             role_z_offset:float=2.5) -> np.ndarray:
    if steps <= burn_in or record_every <= 0 or alpha not in ALPHAS:
        raise ValueError('STOP_INVALID_EXPERIMENT')
    centers,x=targets_and_starts(x_difference,z_difference,role_z_offset)
    rng=np.random.default_rng(seed)
    noise=rng.normal(0.0, ACC_NOISE, size=(steps,N_AGENTS,3))
    v=np.zeros_like(x)
    pairs=np.arange(N_AGENTS)^1
    snapshots=[]
    for it in range(steps):
        off=x-centers
        env=np.empty_like(x)
        env[:,:2]=-ENV_K_XY*off[:,:2]
        env[:,2]=-ENV_K_Z*off[:,2]
        env[:,0]+=-ORBIT*off[:,1]
        env[:,1]+=ORBIT*off[:,0]
        acceleration=env-DRAG*v+noise[it]
        if social_on:
            displacement=x[pairs]-x
            dist=np.linalg.norm(displacement,axis=1)
            acceleration+=force_coefficient(alpha,dist)[:,None]*displacement
        v+=DT*acceleration
        x+=DT*v
        if it>=burn_in and (it-burn_in)%record_every==0:
            snapshots.append(x.copy())
    record=np.asarray(snapshots)
    if not np.isfinite(record).all():
        raise ArithmeticError('STOP_NONFINITE_TRAJECTORY')
    return record


def categorical_probabilities(points: np.ndarray,cutpoints:dict):
    if points.ndim!=3 or points.shape[1:]!=(N_AGENTS,3):
        raise ValueError('STOP_TRAJECTORY_DIMENSION')
    cuts=[np.array(cutpoints[d],dtype=float) for d in ('x','y','z')]
    bins=[np.searchsorted(c,points[:,:,j],side='right') for j,c in enumerate(cuts)]
    hist=np.zeros((N_AGENTS,*(len(c)+1 for c in cuts)),float)
    for i in range(N_AGENTS):
        np.add.at(hist[i],tuple(b[:,i] for b in bins),1)
    hist/=len(points)
    np.testing.assert_allclose(hist.sum(axis=(1,2,3)),1.,atol=1e-12)
    return hist


def mi_equal_groups(p: np.ndarray) -> float:
    if len(p)<2 or not np.allclose(p.sum(axis=tuple(range(1,p.ndim))),1):
        raise ValueError('STOP_GROUP_PROBABILITY')
    mu=p.mean(axis=0)
    with np.errstate(divide='ignore',invalid='ignore'):
        ratio=np.divide(p,mu,where=p>0,out=np.ones_like(p))
        return float(np.sum(np.where(p>0,p*np.log(ratio),0.))/len(p))


def niche_metrics(agent_p: np.ndarray, pair_perm: tuple[int,...]|None=None):
    if agent_p.shape[0]!=N_AGENTS:
        raise ValueError('STOP_INCORRECT_AGENT_COUNT')
    if pair_perm is not None:
        if sorted(pair_perm)!=list(range(6)):
            raise ValueError('STOP_BAD_PAIR_PERMUTATION')
        agent_p=agent_p[np.array([[2*j,2*j+1] for j in pair_perm]).reshape(-1)]
    sp=np.stack([agent_p[:6].mean(axis=0),agent_p[6:].mean(axis=0)])
    xy=sp.sum(axis=-1)
    i_xy=mi_equal_groups(xy)
    i_xyz=mi_equal_groups(sp)
    i_z=max(0.,i_xyz-i_xy)
    within=[]
    for s in range(2):
        a=agent_p[6*s:6*(s+1)]
        within.append(max(0.,mi_equal_groups(a)-mi_equal_groups(a.sum(axis=-1))))
    return {'I_species_XY':i_xy,'I_species_Z_given_XY':i_z,
            'I_individual_Z_given_XY_species':float(np.mean(within))}


def joint_species_xyz(agent_p:np.ndarray):
    return species_distribution(agent_p)/2.0


def total_variation(a:np.ndarray,b:np.ndarray)->float:
    if a.shape!=b.shape or not np.isclose(a.sum(),1.) or not np.isclose(b.sum(),1.):
        raise ValueError('STOP_TV_NORMALIZATION')
    return float(0.5*np.abs(a-b).sum())


def overlap_oracle(source: np.ndarray,target: np.ndarray,pseudo:float=SMOOTHING):
    """Equal-species log-score of held-out state use for a categorical predictor."""
    if source.shape!=target.shape or source.shape[0]!=2:
        raise ValueError('STOP_DISTRIBUTION_MISMATCH')
    nstates=source[0].size
    # Equivalent to Dirichlet pseudo on an 8-seed x 6-agent categorical forecast.
    n_ref=N_TRAIN_SEEDS*6*((STEPS-BURN_IN-1)//RECORD_EVERY+1)
    prob=(source*n_ref+pseudo)/(n_ref+nstates*pseudo)
    return float(np.mean(np.sum(target*np.log(prob),axis=(1,2,3))))


def species_distribution(p:np.ndarray) -> np.ndarray:
    return np.stack([p[:6].mean(axis=0),p[6:].mean(axis=0)])


def experiment(seed_ids=SEEDS, steps=STEPS,burn_in=BURN_IN,alpha_values=ALPHAS,
               scenario_names=tuple(SCENARIOS),grain_names=tuple(GRAINS)):
    if len(seed_ids)<N_TRAIN_SEEDS+2 or any(s not in SCENARIOS for s in scenario_names):
        raise ValueError('STOP_INVALID_REPLICATION_DESIGN')
    if any(a not in ALPHAS for a in alpha_values) or any(g not in GRAINS for g in grain_names):
        raise ValueError('STOP_NONPREDECLARED_SCENARIO')
    # Source equivalence must be checked before all outcome opening.
    for a in alpha_values:
        if abs(force_coefficient(a,SOURCE_D)-KAPPA0)>1e-14:
            raise AssertionError('STOP_IDENTIFIED_SET_SOURCE_MISMATCH')
    groups={}
    for name in scenario_names:
        delta_x,delta_z=SCENARIOS[name]
        groups[name]={}
        for social in (False,True):
            for alpha in alpha_values:
                per_grain={g:[] for g in grain_names}
                for seed in seed_ids:
                    tracks=simulate(delta_x,delta_z,alpha,seed,social,steps,burn_in)
                    for grain in grain_names:
                        per_grain[grain].append(categorical_probabilities(tracks,GRAINS[grain]))
                for grain in grain_names:
                    groups[name][(social,alpha,grain)]=np.stack(per_grain[grain])

    results={}
    for name in scenario_names:
        contrasts={}
        for grain in grain_names:
            field={}
            for social in (False,True):
                byalpha={}
                for alpha in alpha_values:
                    p=groups[name][(social,alpha,grain)].mean(axis=0)
                    byalpha[str(alpha)]=niche_metrics(p)
                field['social_on' if social else 'social_off']=byalpha
            ranges={}
            for social in ('social_on','social_off'):
                ranges[social]={}
                for key in next(iter(field[social].values())):
                    values=[v[key] for v in field[social].values()]
                    ranges[social][key]=[float(min(values)),float(max(values))]
            pairs=[]
            on_joint={};off_joint={}
            for alpha in alpha_values:
                yes=field['social_on'][str(alpha)]
                no=field['social_off'][str(alpha)]
                pairs.append({str(alpha):{key:yes[key]-no[key] for key in yes}})
                on_joint[alpha]=joint_species_xyz(groups[name][(True,alpha,grain)].mean(axis=0))
                off_joint[alpha]=joint_species_xyz(groups[name][(False,alpha,grain)].mean(axis=0))
            pairwise_tv={f'{a}:{b}':total_variation(on_joint[a],on_joint[b])
                         for a,b in itertools.combinations(alpha_values,2)}
            contrasts[grain]={'by_candidate':field,'finite_alpha_ranges':ranges,
                'on_minus_off':pairs,
                'source_equivalent_alpha_joint_xyz_total_variation':pairwise_tv,
                'max_source_equivalent_alpha_joint_xyz_total_variation':max(pairwise_tv.values(),default=0.),
                'social_on_vs_off_joint_xyz_total_variation_by_alpha':{
                    str(alpha):total_variation(on_joint[alpha],off_joint[alpha])
                    for alpha in alpha_values}}
        results[name]=contrasts

    # Additional controlled individual target ablation: the default individual
    # vertical role offset is externally stipulated, not spontaneously learned.
    # Only the species-equal environment and alpha1 are evaluated here; both
    # variants share paired random seeds and social force configuration.
    individual_target_control={}
    if 'no_species_resource_contrast' in scenario_names and 1.0 in alpha_values:
        for social in (False,True):
            zero_records={g:[] for g in grain_names}
            for seed in seed_ids:
                t=simulate(0.0,0.0,1.0,seed,social,steps,burn_in,
                           role_z_offset=0.0)
                for grain in grain_names:
                    zero_records[grain].append(categorical_probabilities(t,GRAINS[grain]))
            for grain in grain_names:
                actual=groups['no_species_resource_contrast'][(social,1.0,grain)].mean(axis=0)
                zero=np.stack(zero_records[grain]).mean(axis=0)
                key=f'{"social_on" if social else "social_off"}:{grain}'
                individual_target_control[key]={
                    'imposed_role_target_offset_m':2.5,
                    'imposed_target_role_offset_individual_information':niche_metrics(actual)['I_individual_Z_given_XY_species'],
                    'zero_role_target_offset_individual_information':niche_metrics(zero)['I_individual_Z_given_XY_species'],
                    'note':'Same pseudolabels, same environmental centers, same initial coordinates and random seeds; only imposed vertical target offset differs.'}

    # Monte-Carlo uncertainty in one *synthetic simulator* (NOT field confidence).
    # Seed is the resampling unit; social toggles share exactly the same seed,
    # so differences are computed on matched replicate resamples.
    seed_bootstrap={}
    if 1.0 in alpha_values and 'no_species_resource_contrast' in scenario_names:
        rng=np.random.default_rng(BOOTSTRAP_SEED)
        picks=rng.integers(0,len(seed_ids),size=(BOOTSTRAP_B,len(seed_ids)))
        for grain in grain_names:
            reference=groups['no_species_resource_contrast'][(True,1.0,grain)]
            for name in scenario_names:
                on=groups[name][(True,1.0,grain)]
                off=groups[name][(False,1.0,grain)]
                keys=('I_species_XY','I_species_Z_given_XY')
                delta_social=[];delta_env=[]
                for pick in picks:
                    met_on=niche_metrics(on[pick].mean(axis=0))
                    met_off=niche_metrics(off[pick].mean(axis=0))
                    met_reference=niche_metrics(reference[pick].mean(axis=0))
                    delta_social.append([met_on[k]-met_off[k] for k in keys])
                    delta_env.append([met_on[k]-met_reference[k] for k in keys])
                delta_social=np.asarray(delta_social)
                delta_env=np.asarray(delta_env)
                seed_bootstrap[f'{name}:{grain}']={
                    'resource_effect_vs_no_species_difference':{
                        k:[float(np.quantile(delta_env[:,j],.025)),float(np.quantile(delta_env[:,j],.975))]
                        for j,k in enumerate(keys)},
                    'social_on_minus_off':{
                        k:[float(np.quantile(delta_social[:,j],.025)),float(np.quantile(delta_social[:,j],.975))]
                        for j,k in enumerate(keys)},
                    'unit':'stochastic simulator seed (matched intervention replicate)',
                    'not_field_uncertainty':True}

    # Holdout scoring: TRUE generator alpha=1, social on. 8 Monte Carlo source
    # seeds supply probabilistic forecasts; last seeds supply independent noise.
    scores={}
    if 'no_species_resource_contrast' in scenario_names and 1.0 in alpha_values:
        for grain in grain_names:
            base=groups['no_species_resource_contrast'][(True,1.0,grain)]
            source_predictor=species_distribution(base[:N_TRAIN_SEEDS].mean(axis=0))
            for name in scenario_names:
                held=groups[name][(True,1.0,grain)][N_TRAIN_SEEDS:]
                per_alpha={str(alpha):[] for alpha in alpha_values}
                for held_seed in held:
                    target=species_distribution(held_seed)
                    blind=overlap_oracle(source_predictor,target)
                    for alpha in alpha_values:
                        env_pred=species_distribution(groups[name][(True,alpha,grain)][:N_TRAIN_SEEDS].mean(axis=0))
                        per_alpha[str(alpha)].append(overlap_oracle(env_pred,target)-blind)
                scores[f'{name}:{grain}']={
                    'known_environment_forward_gain_by_alpha_nats_per_fix':{k:float(np.mean(v)) for k,v in per_alpha.items()},
                    'known_environment_forward_minmax_nats_per_fix':[float(min(np.mean(v) for v in per_alpha.values())),float(max(np.mean(v) for v in per_alpha.values()))],
                    'heldout_noise_seeds':len(held),
                    'baseline':'source no-species-resource-difference model, same alpha1',
                    'evaluation':'known synthetic target environment and simulator dynamics, not observed habitat external forecast'}
    return {'id':'boids-v11-environment-intervention-vs-social-force-ablation',
            'status':'SYNTHETIC_KNOWN_TRUTH_ONLY_NOT_SPECIES_OR_COMPETITION_EVIDENCE',
            'fixed_design':{'seed_ids':list(seed_ids),'train_seed_count':N_TRAIN_SEEDS,
              'n_agents':N_AGENTS,'source_identified_distance_m':SOURCE_D,
              'novel_initial_spacing_m':INITIAL_DISTANCE,'alphas':list(alpha_values),
              'source_kappa_per_s2':KAPPA0,'steps':steps,'burn_in':burn_in,
              'record_every':RECORD_EVERY,'resource_contrasts_m':SCENARIOS,'grains':GRAINS,
              'noise_common_across_social_on_off':True,
              'bootstrap_repetitions':BOOTSTRAP_B,'bootstrap_seed':BOOTSTRAP_SEED,
              'source_target_positions_identical_initially_across_pseudo_species':True},
            'niche_by_world':results,
            'known_environment_vs_blind_forward_scores':scores,
            'matched_simulation_seed_bootstrap95_alpha1':seed_bootstrap,
            'role_specific_vertical_target_control':individual_target_control,
            'boundaries':[
              'The imposed species habitat centers are part of the simulation design; a positive information value cannot reveal that ecological resources cause partition in nature.',
              'Within-species individual vertical identity can reflect the stipulated role-specific z-target offsets; their removal must be examined separately.',
              'This simulator has no interspecific interactions, resource consumption, observed food preferences or airfoil physics. Social coupling is only within dyads.',
              'Ablation on/off is a model intervention with common random numbers, not a wild causal experiment.',
              'The forward predictor receives the correct toy environmental targets and uses Monte Carlo trajectories from the same simulator family; not a novel species forecast.',
              'Bootstrap resamples stochastic seed realizations of the stipulated simulator. These intervals are neither independent animal samples nor biological confidence intervals.',
              'Candidate min/max ranges cover only specified three points on one illustrative structural identified line; they are not confidence intervals.',
              'Individual and species category labels in a toy system are not independent biological replicates.']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path('validation_v11/results/environment_ablation.json'))
    parser.add_argument('--seeds',type=int,default=len(SEEDS))
    args=parser.parse_args()
    if args.seeds<10 or args.seeds>len(SEEDS):raise ValueError('10–12 seeds supported by frozen design')
    res=experiment(seed_ids=SEEDS[:args.seeds])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(res,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    for name,values in res['niche_by_world'].items():
        k=values['coarse']['finite_alpha_ranges']['social_on']
        print(name,'XY',k['I_species_XY'],'Z|XY',k['I_species_Z_given_XY'])
    return 0

if __name__=='__main__':raise SystemExit(main())
