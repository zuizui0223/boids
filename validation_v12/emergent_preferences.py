#!/usr/bin/env python3
"""v12: symmetric starting agents, adaptive patch valuation, 3-D movement.

Known-truth synthetic counterfactuals ONLY: no animal data or inferred wild Boids
parameters. There are no genetically/individually preassigned habitat targets.
All candidate Boids coefficients have equal instantaneous force at 10 m.
"""
from __future__ import annotations
import argparse
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
import numpy as np

N_SPECIES = 2
N_PER_SPECIES = 6
N = N_SPECIES * N_PER_SPECIES
N_DAYS = 8
N_BLOCKS = 24
BURN_BLOCKS = 3
TRAIN_DAYS = 4
MICRO_STEPS = 8
DT = 0.25
PATCHES = np.array([[-12., 0., -13.], [-12., 0., 13.], [12., 0., -13.], [12., 0., 13.]])
ALPHAS = (0., 1., 2.)
SOURCE_DISTANCE = 10.
SOURCE_KAPPA = -0.003
SEED_START = 20261029
PRIMARY_GRAIN = {'x': [-7., 7.], 'y': [0.], 'z': [-7., 7.]}
FINE_GRAIN = {'x': [-14., -7., 0., 7., 14.], 'y': [-4., 0., 4.], 'z': [-14., -7., 0., 7., 14.]}


@dataclass(frozen=True)
class Condition:
    name: str
    private_learning: bool = False
    social_choice: bool = False
    boids: bool = False
    resource_depletion: bool = False
    history_shuffle: bool = False
    history_reset: bool = False
    cross_species_social: bool = False


CONDITIONS = (
    Condition('neutral'),
    Condition('boids_only', boids=True),
    Condition('private_learning_only', private_learning=True),
    Condition('private_learning_plus_boids',private_learning=True,boids=True),
    Condition('learning_plus_social_no_boids',private_learning=True,social_choice=True),
    Condition('social_choice_only', social_choice=True, boids=True),
    Condition('learning_plus_social', private_learning=True, social_choice=True, boids=True),
    Condition('learning_social_depletion', private_learning=True, social_choice=True, boids=True, resource_depletion=True),
    Condition('learning_social_history_shuffle', private_learning=True, social_choice=True, boids=True, history_shuffle=True),
    Condition('learning_social_history_reset', private_learning=True, social_choice=True, boids=True, history_reset=True),
    Condition('learning_mixed_species_social', private_learning=True, social_choice=True, boids=True, cross_species_social=True),
)


def boids_gamma(alpha: float) -> float:
    return SOURCE_KAPPA + alpha / SOURCE_DISTANCE**3


def source_equivalence() -> bool:
    return all(abs(boids_gamma(a) - a / SOURCE_DISTANCE**3 - SOURCE_KAPPA) < 1e-14 for a in ALPHAS)


def sample_categorical(rng: np.random.Generator, utility: np.ndarray, temperature: float=0.72) -> np.ndarray:
    if temperature <= 0 or utility.ndim != 2 or utility.shape[1] != len(PATCHES):
        raise ValueError('Invalid choice representation')
    # Stable Gumbel-max sampling: no categorical bin / boundary artefacts.
    u = np.clip(rng.random(utility.shape), 1e-12, 1-1e-12)
    noise = -np.log(-np.log(u))
    return np.argmax(utility / temperature + noise, axis=1)


def get_social_choice(chosen: np.ndarray, cross_species: bool=False) -> np.ndarray:
    """Observed group/cross-group patch fractions at *preceding* block only."""
    others=np.zeros((N,4))
    for i in range(N):
        ids=np.array([j for j in range(N) if j != i and (cross_species or j//N_PER_SPECIES == i//N_PER_SPECIES)],int)
        others[i] = np.bincount(chosen[ids],minlength=4)/len(ids)
    return others


def move(x: np.ndarray, v: np.ndarray, chosen: np.ndarray,
         rng: np.random.Generator, alpha: float, social_on: bool) -> tuple[np.ndarray,np.ndarray]:
    if alpha not in ALPHAS:
        raise ValueError('Unknown Boids identified-set candidate')
    mates = np.arange(N)^1
    for _ in range(MICRO_STEPS):
        goal=PATCHES[chosen]
        drift=0.12*(goal-x)-0.50*v
        drift[:,1]-=0.030*x[:,1]  # Common y confinement, not individual preference.
        if social_on:
            r=x[mates]-x
            d=np.maximum(1.0,np.linalg.norm(r,axis=1))
            drift+=(boids_gamma(alpha)-alpha/d**3)[:,None]*r
            drift+=0.065*(v[mates]-v)  # Fixed alignment, same for all alpha.
        drift+=rng.normal(0.,0.40,size=(N,3))
        v=np.clip(v + DT*drift,-7.,7.)
        x=x+DT*v
    return x,v


def simulate(condition: Condition, seed: int, alpha: float=1.,
             n_days: int=N_DAYS, n_blocks: int=N_BLOCKS,
             social_strength: float=2.0) -> dict:
    if alpha not in ALPHAS or n_days<2 or n_blocks<=BURN_BLOCKS:
        raise ValueError('Invalid simulation configuration')
    if not math.isfinite(social_strength) or social_strength < 0:
        raise ValueError('Invalid social imitation strength')
    if condition.history_shuffle and condition.history_reset:
        raise ValueError('Incompatible null policies')
    rng=np.random.default_rng(seed)
    q=np.zeros((N,4),float)
    all_xyz=np.empty((n_days,n_blocks-BURN_BLOCKS,N,3),float)
    all_choices=np.empty((n_days,n_blocks-BURN_BLOCKS,N),int)
    all_rewards=np.empty((n_days,n_blocks-BURN_BLOCKS,N),float)
    daily_q=[]
    for day in range(n_days):
        if day and condition.history_reset:
            q.fill(0.)
        if day and condition.history_shuffle:
            for s in range(N_SPECIES):
                idx=np.arange(s*N_PER_SPECIES,(s+1)*N_PER_SPECIES)
                q[idx]=q[rng.permutation(idx)].copy()
        # Identical initial positions and innate preferences across agents.
        x=rng.normal(0.,0.4,size=(N,3))
        v=np.zeros((N,3),float)
        chosen=rng.integers(0,4,size=N)
        stock=np.ones(4,float)
        for block in range(n_blocks):
            resource_cue=stock[None,:] if condition.resource_depletion else np.ones((1,4))
            travel=np.linalg.norm(x[:,None,:]-PATCHES[None,:,:],axis=-1)
            # All agents have exactly the same decision rule. No fixed agent/species target.
            utility=3.6*q + .50*resource_cue - .006*travel
            if condition.social_choice:
                utility=utility+social_strength*get_social_choice(chosen,condition.cross_species_social)
            next_choice=sample_categorical(rng,utility)
            crowd=np.bincount(next_choice,minlength=4)
            reward=stock[next_choice].copy()
            if condition.resource_depletion:
                reward/=1+0.055*(crowd[next_choice]-1)
            if condition.private_learning:
                # Private, reward-conditioned repetition/habit; not innate traits.
                q*=.94
                q[np.arange(N),next_choice]=.45*reward+.55*q[np.arange(N),next_choice]
            chosen=next_choice
            if condition.resource_depletion:
                stock=np.clip(stock + .13*(1.-stock)-.043*crowd,0.04,1.)
            x,v=move(x,v,chosen,rng,alpha,condition.boids)
            if block>=BURN_BLOCKS:
                ix=block-BURN_BLOCKS
                all_xyz[day,ix]=x
                all_choices[day,ix]=chosen
                all_rewards[day,ix]=reward
        daily_q.append(q.copy())
    assert np.isfinite(all_xyz).all()
    return {'xyz':all_xyz,'choices':all_choices,'rewards':all_rewards,
            'daily_q':np.array(daily_q),'condition':asdict(condition),'alpha':alpha,
            'seed':seed}


def categorical_xyz(xyz: np.ndarray, grain: dict=PRIMARY_GRAIN) -> np.ndarray:
    a=np.asarray(xyz)
    if a.ndim!=4 or a.shape[2:]!=(N,3):
        raise ValueError('Need day×block×agent×3 coordinates')
    cuts=[np.array(grain[k]) for k in ('x','y','z')]
    shape=tuple(len(k)+1 for k in cuts)
    out=np.empty(a.shape[:3],int)
    indices=np.zeros(a.shape[:3],dtype=int)
    for axis,k in enumerate(cuts):
        idx=np.searchsorted(k,a[:,:,:,axis],side='right')
        indices=indices*(len(k)+1)+idx
    return indices


def per_individual_patch_prob(choices: np.ndarray, days: slice) -> np.ndarray:
    patch=choices[days]
    p=np.stack([(patch==k).sum(axis=(0,1)) for k in range(4)],axis=1)
    return p.astype(float)


def paired_gain(train: np.ndarray, test: np.ndarray, pseudo: float=.50) -> float:
    """Same held-out observations; personal vs conspecific pooled probabilities."""
    if train.shape!=test.shape or train.shape[0]!=N or train.ndim!=2:
        raise ValueError('Malformed identity-prediction counts')
    nclass=train.shape[1]
    out=[]
    for i in range(N):
        species=i//N_PER_SPECIES
        pooled=train[species*N_PER_SPECIES:(species+1)*N_PER_SPECIES].sum(axis=0)
        personal=(train[i]+pseudo)/(train[i].sum()+nclass*pseudo)
        conspec=(pooled+N_PER_SPECIES*pseudo)/(pooled.sum()+nclass*N_PER_SPECIES*pseudo)
        if test[i].sum()==0:raise ValueError('Missing heldout individual')
        out.append(float(test[i]@np.log(personal/conspec)/test[i].sum()))
    return float(np.mean(out))


def patch_predictive_gain(choices: np.ndarray) -> float:
    return paired_gain(per_individual_patch_prob(choices,slice(0,TRAIN_DAYS)),
                       per_individual_patch_prob(choices,slice(TRAIN_DAYS,None)))

def guild_patch_gain(choices: np.ndarray, pseudo: float=.5) -> float:
    """Predict heldout patch choice from guild history versus both guilds pooled.

    A group-level prediction despite zero innate group differences is possible
    only if the stochastic acquired group state persists across days.
    """
    train=per_individual_patch_prob(choices,slice(0,TRAIN_DAYS))
    test=per_individual_patch_prob(choices,slice(TRAIN_DAYS,None))
    all_counts=train.sum(axis=0)
    baseline=(all_counts+N*pseudo)/(all_counts.sum()+4*N*pseudo)
    terms=[]
    for i in range(N):
        s=i//N_PER_SPECIES
        guild=train[s*N_PER_SPECIES:(s+1)*N_PER_SPECIES].sum(axis=0)
        target=(guild+N_PER_SPECIES*pseudo)/(guild.sum()+4*N_PER_SPECIES*pseudo)
        terms.append(float(test[i]@np.log(target/baseline)/test[i].sum()))
    return float(np.mean(terms))


def state_probabilities(indices: np.ndarray, nclass: int) -> np.ndarray:
    return np.array([np.bincount(indices[:,:,i].reshape(-1),minlength=nclass) for i in range(N)])


def vertical_gain(xyz: np.ndarray, grain: dict=PRIMARY_GRAIN,
                  min_self_xy: int=4, pseudo: float=.5) -> tuple[float,float]:
    ind=categorical_xyz(xyz,grain)
    nx,ny,nz=(*(len(grain[k])+1 for k in ('x','y','z')),)
    train=np.stack([np.bincount(ind[:TRAIN_DAYS,:,i].ravel(),minlength=nx*ny*nz).reshape(nx*ny,nz) for i in range(N)])
    test=np.stack([np.bincount(ind[TRAIN_DAYS:,:,i].ravel(),minlength=nx*ny*nz).reshape(nx*ny,nz) for i in range(N)])
    gains=[];coverage=[]
    for i in range(N):
        species=i//N_PER_SPECIES
        source=train[i]; pooled=train[species*N_PER_SPECIES:(species+1)*N_PER_SPECIES].sum(axis=0)
        own_count=source.sum(axis=1)
        pool_count=pooled.sum(axis=1)
        shared=(own_count>=min_self_xy)&(pool_count>=min_self_xy)
        # All held-out states must be scored; no outcome-contingent dropping of
        # individuals with unsupported XY cells. Return support as a separate
        # observability diagnostic, not an eligibility filter.
        targets=test[i]
        included=targets.sum(); total=test[i].sum()
        pown=(source+pseudo)/(own_count[:,None]+nz*pseudo)
        ppool=(pooled+N_PER_SPECIES*pseudo)/(pool_count[:,None]+nz*N_PER_SPECIES*pseudo)
        gains.append(float(np.sum(targets*np.log(pown/ppool))/included))
        coverage.append(float((test[i]*shared[:,None]).sum()/total))
    return float(np.mean(gains)),float(np.mean(coverage))


def guild_vertical_gain_given_xy(xyz: np.ndarray, grain: dict=PRIMARY_GRAIN, pseudo: float=.5) -> float:
    """Heldout P(z | x,y,guild) vs P(z | x,y), scored on all same records."""
    idx=categorical_xyz(xyz,grain)
    nx,ny,nz=(len(grain[k])+1 for k in ('x','y','z'))
    counts=np.stack([np.bincount(idx[:TRAIN_DAYS,:,i].ravel(),minlength=nx*ny*nz).reshape(nx*ny,nz) for i in range(N)])
    tests=np.stack([np.bincount(idx[TRAIN_DAYS:,:,i].ravel(),minlength=nx*ny*nz).reshape(nx*ny,nz) for i in range(N)])
    common=counts.sum(axis=0)
    common_cond=(common+N*pseudo)/(common.sum(axis=1,keepdims=True)+nz*N*pseudo)
    out=[]
    for i in range(N):
        sid=i//N_PER_SPECIES
        guild=counts[sid*N_PER_SPECIES:(sid+1)*N_PER_SPECIES].sum(axis=0)
        gcond=(guild+N_PER_SPECIES*pseudo)/(guild.sum(axis=1,keepdims=True)+nz*N_PER_SPECIES*pseudo)
        out.append(float(np.sum(tests[i]*np.log(gcond/common_cond))/tests[i].sum()))
    return float(np.mean(out))


def species_niche_information(xyz: np.ndarray, grain:dict=PRIMARY_GRAIN) -> dict:
    indices=categorical_xyz(xyz,grain)
    nx,ny,nz=(*(len(grain[k])+1 for k in ('x','y','z')),)
    counts=np.array([np.bincount(indices[:,:,i].ravel(),minlength=nx*ny*nz).reshape(nx,ny,nz) for i in range(N)],float)
    counts/=counts.sum(axis=(1,2,3),keepdims=True)
    species=np.array([counts[s*N_PER_SPECIES:(s+1)*N_PER_SPECIES].mean(axis=0) for s in range(N_SPECIES)])
    def info(p):
        avg=p.mean(axis=0);mask=p>0
        ratio=np.ones_like(p)
        np.divide(p,avg[None,...],out=ratio,where=mask)
        return float(np.sum(np.where(mask,p*np.log(ratio),0.))/len(p))
    horizontal=info(species.sum(axis=-1))
    whole=info(species)
    return {'horizontal_information_nats':horizontal,
            'vertical_information_given_xy_nats':float(max(whole-horizontal,0.))}


def inspect_single(condition: Condition, alpha:float, seed:int,
                   n_days:int=N_DAYS,n_blocks:int=N_BLOCKS,
                   social_strength:float=2.0) -> dict:
    sim=simulate(condition,seed,alpha,n_days=n_days,n_blocks=n_blocks,
                 social_strength=social_strength)
    hgain,coverage=vertical_gain(sim['xyz'])
    test_positions=sim['xyz'][TRAIN_DAYS:]
    x_gap=float(test_positions[:,:,N_PER_SPECIES:,0].mean()-test_positions[:,:,:N_PER_SPECIES,0].mean())
    return {
      'patch_identity_gain_nats':patch_predictive_gain(sim['choices']),
      'guild_patch_gain_nats':guild_patch_gain(sim['choices']),
      'guild_vertical_gain_given_xy_nats':guild_vertical_gain_given_xy(sim['xyz']),
      'vertical_identity_gain_given_xy_nats':hgain,
      'vertical_identity_support':coverage,
      'species_niche':species_niche_information(sim['xyz']),
      'mean_resource_reward':float(sim['rewards'].mean()),
      'signed_species_x_gap_m':x_gap,
      'absolute_species_x_gap_m':abs(x_gap),
      'end_policy_concentration':float(np.mean(np.max(sim['daily_q'][-1],axis=1)-np.mean(sim['daily_q'][-1],axis=1))),
    }


def experiment(seeds:int=20,seed_start:int=SEED_START,
               conditions:tuple[Condition,...]=CONDITIONS,alphas:tuple[float,...]=(1.,),
               n_days:int=N_DAYS,n_blocks:int=N_BLOCKS) -> dict:
    if seeds<3 or n_days!=N_DAYS:
        raise ValueError('Minimum 3 independent simulation worlds and 8 days')
    if not source_equivalence():raise AssertionError('Not source-equivalent')
    rows=[]
    for c in conditions:
        for alpha in alphas:
            for s in range(seed_start,seed_start+seeds):
                m=inspect_single(c,alpha,s,n_days,n_blocks)
                rows.append({'condition':c.name,'alpha':alpha,'seed':s,**m})
    grouped={}
    for c in conditions:
        byalpha={}
        for alpha in alphas:
            r=[x for x in rows if x['condition']==c.name and x['alpha']==alpha]
            keys=['patch_identity_gain_nats','guild_patch_gain_nats','guild_vertical_gain_given_xy_nats','vertical_identity_gain_given_xy_nats','vertical_identity_support',
                  'mean_resource_reward','end_policy_concentration','signed_species_x_gap_m','absolute_species_x_gap_m']
            keys+=['species_niche.horizontal_information_nats','species_niche.vertical_information_given_xy_nats']
            stats={}
            for k in keys:
                vals=np.array([x['species_niche'][k.split('.')[1]] if k.startswith('species_niche.') else x[k] for x in r])
                stats[k]={'mean':float(vals.mean()),'sd_between_seed':float(vals.std(ddof=1)),
                          'min':float(vals.min()),'max':float(vals.max()),
                          'positive_seeds':int((vals>0).sum())}
            byalpha[str(alpha)]=stats
        grouped[c.name]=byalpha
    return {'study':'v12-endogenous-policy-learning-3d-boids-known-truth',
            'status':'EXPLORATORY_SIMULATOR_ONLY_NOT_WILD_EVIDENCE',
            'source_calibration':{'distance_m':SOURCE_DISTANCE,'kappa_per_s2':SOURCE_KAPPA,
                                  'candidate_alphas':list(alphas),'note':'equal instantaneous dyadic force at source distance'},
            'protocol':{'n_species':N_SPECIES,'agents_per_species':N_PER_SPECIES,
                        'n_patches':4,'initial_individual_Q':'identically zero',
                        'initial_species_preferences':'identical; no assigned species-specific targets',
                        'days':n_days,'blocks_per_day':n_blocks,'train_days':TRAIN_DAYS,
                        'test_days':n_days-TRAIN_DAYS,'physics_substeps_per_block':MICRO_STEPS,
                        'source':'all choices, rewards, movement and niches are simulated',
                        'smoothing':'0.5 pseudo per state per training individual; pooled priors scale with 6/12 contributors; ALL heldout XY cells scored including unobserved training states',
                        'grain':PRIMARY_GRAIN,
                        'conditions':[asdict(c) for c in conditions],
                        'environment':'four patches with symmetric replenishment; 2 XY×2 Z'},
            'seeds':[seed_start+i for i in range(seeds)],
            'results':grouped,'per_seed':rows,
            'limits':['Self-reinforcement/forgetting and group social choice are explicitly modeled generative rules, not inferred wild mechanisms.',
                      'Equal innate conditions do not imply biological individuality spontaneously originated by natural evolution.',
                      'The finite parameter grid is not an uncertainty confidence region.',
                      'Repeated simulated days are not independent animals; infer across simulation seeds.',
                      'Species labels identify artificial assortative social cohorts with identical physiology and resources.',
                      'Moving among resources in this toy model does not establish competition or ecological niche separation in field populations.']}


def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=20)
    p.add_argument('--out',type=Path,default=Path('validation_v12/results/endogenous_policy_v12.json'))
    a=p.parse_args()
    result=experiment(seeds=a.seeds)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    print('EXPLORATORY_SYNTHETIC_V12')
    for c,vals in result['results'].items():
        v=vals['1.0']
        print(c,'patch',round(v['patch_identity_gain_nats']['mean'],4),
              '3D vertical',round(v['vertical_identity_gain_given_xy_nats']['mean'],4),
              'species XY',round(v['species_niche.horizontal_information_nats']['mean'],4),
              'species Z',round(v['species_niche.vertical_information_given_xy_nats']['mean'],4))

if __name__=='__main__':main()
