#!/usr/bin/env python3
"""v10: held-out *synthetic-seed* test of individual conditional vertical profiles.

No data-driven tuning, no observed animal observations. The only training/test
separation is stochastic simulator seed, at fixed known species/resource world.
This is not a wild-bat (batter) shape-identity inferential replication.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import niche_identified_set as boids

PROFILE_SMOOTHING=0.5
SHARED_MIN_TRAIN_FIXES=5
TEST_WORLD_NAMES=("source_spacing_shared_resources", "novel_spacing_reassembled_resources")
ALPHA_SUBSET=(0.,1.,2.)


def heldout_seed_vertical_gain(seed_agent_probabilities, recorded_points: int,
                              pseudo: float=PROFILE_SMOOTHING,
                              min_self_support: int=SHARED_MIN_TRAIN_FIXES):
    """Score self vs pooled-species P(z|xy) using exactly matched held-out cells.

    For each held-out independent simulated seed, self and species conditionals
    are fit only from the OTHER seeds. Comparisons are equal-individual, and
    conditional on xy. Training zeros are smoothed identically to avoid log(0).
    """
    cube=np.asarray(seed_agent_probabilities,dtype=float)
    if cube.ndim!=5 or cube.shape[1]!=boids.N_AGENTS or len(cube)<2:
        raise ValueError('Expected >=2 seeds, each with 12 individual XYZ profiles')
    if pseudo<=0 or min_self_support<1 or recorded_points<1:
        raise ValueError('Invalid predeclared pseudo/support settings')
    if not np.allclose(cube.sum(axis=(2,3,4)),1.,atol=1e-12):
        raise ValueError('Malformed categorical input')
    count=cube*recorded_points
    ng=boids.N_PAIRS_PER_SPECIES*2
    nz=cube.shape[-1]
    means=[];coverage=[]
    seed_scores=[]
    for held in range(len(count)):
        train=count.sum(axis=0)-count[held]
        test=count[held]
        vals=[];cov=[]
        for i in range(boids.N_AGENTS):
            source=train[i]
            pooled=train[(i//ng)*ng:((i//ng)+1)*ng].sum(axis=0)
            src_xy=source.sum(axis=2)
            pool_xy=pooled.sum(axis=2)
            ok=(src_xy>=min_self_support)&(pool_xy>=min_self_support)
            target=test[i]*ok[:,:,None]
            count_scored=float(target.sum())
            if count_scored<=0:
                raise ValueError('STOP_NO_SHARED_HORIZONTAL_SUPPORT_FOR_INDIVIDUAL')
            own=(source+pseudo)/(src_xy[:,:,None]+pseudo*nz)
            other=(pooled+pseudo)/(pool_xy[:,:,None]+pseudo*nz)
            vals.append(float(np.sum(target*np.log(own/other))/count_scored))
            cov.append(float(count_scored/test[i].sum()))
        seed_scores.append({'gain':float(np.mean(vals)), 'coverage':float(np.mean(cov))})
        means.append(np.mean(vals));coverage.append(np.mean(cov))
    return {
      'mean_heldout_self_minus_pooled_nats_per_fix':float(np.mean(means)),
      'heldout_seed_gains':list(map(float,means)),
      'heldout_seed_gain_min':float(np.min(means)),
      'heldout_seed_gain_max':float(np.max(means)),
      'positive_heldout_seeds':int(np.sum(np.asarray(means)>0)),
      'n_heldout_independent_simulation_seeds':len(means),
      'mean_xy_supported_fraction':float(np.mean(coverage)),
      'training_pseudocount_per_z_state':pseudo,
      'minimum_self_training_count_per_xy':min_self_support,
      'score_unit':'equal simulated individual, then equal heldout stochastic world; NOT biological individual'
    }


def experiment(n_seeds: int=10,steps: int=boids.N_STEPS,burn_in: int=boids.BURN_IN) -> dict:
    if n_seeds<3:raise ValueError('Need at least 3 independent seeds')
    obs=len(range(burn_in,steps,boids.RECORD_EVERY))
    outputs={}
    for context in TEST_WORLD_NAMES:
        world=boids.WORLDS[context]
        alpha_out={}
        for alpha in ALPHA_SUBSET:
            distributions={grain:[] for grain in boids.GRAINS}
            for i in range(n_seeds):
                records=boids.simulate(world,alpha,boids.SEED_START+i,steps=steps,burn_in=burn_in)
                for grain,cut in boids.GRAINS.items():
                    distributions[grain].append(boids.categorical_uses(records,cut))
            alpha_out[str(alpha)]={grain:heldout_seed_vertical_gain(np.stack(xs),obs)
                                  for grain,xs in distributions.items()}
        outputs[context]=alpha_out
    # Mechanistic negative control in the same artificial world and same
    # reference theta. The population-level z-target distribution is preserved,
    # but individual assignment of those targets changes independently by seed.
    # This control is NOT a biological causal study of memory or learning.
    control={}
    for context in TEST_WORLD_NAMES:
        world=boids.WORLDS[context]
        outcomes={grain:[] for grain in boids.GRAINS}
        for i in range(n_seeds):
            traj=boids.simulate(world,1.,boids.SEED_START+i,steps=steps,burn_in=burn_in,
                                shuffle_individual_z_targets=True)
            for g,bins in boids.GRAINS.items():
                outcomes[g].append(boids.categorical_uses(traj,bins))
        control[context]={g:heldout_seed_vertical_gain(np.stack(reps),obs)
                          for g,reps in outcomes.items()}
    return {'status':'SYNTHETIC_SIMULATION_SEED_GENERALIZATION_ONLY',
            'n_seeds':n_seeds,
            'source_distance_m':boids.SOURCE_DISTANCE_M,
            'candidate_alpha_subset':list(ALPHA_SUBSET),
            'worlds':outputs,
            'policy_reshuffle_negative_control':control,
            'claim_limits':[
              'This is individual identity in toy repeated state-use simulations with known fixed individual resource offsets, not independent biological individuals.',
              'Independent random seeds share exactly the same known simulator and environment; cannot establish cross-habitat, cross-taxon or wild-individual transfer.',
              'Pooled conspecific profile includes target individual; the two models always score identical heldout XYZ events under exactly the same XY support.',
              'A fixed-XY conditional gain does not identify memory, learning, competition, or a social-Boids force.' ]}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seeds',type=int,default=10)
    parser.add_argument('--out',type=Path,default=Path('validation_v10/results/profile_seed_transfer_v10.json'))
    opts=parser.parse_args()
    result=experiment(n_seeds=opts.seeds)
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    opts.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    for name,g in result['worlds'].items():
        for a,b in g.items():
            print(name,'alpha',a,'coarse gain',round(b['coarse']['mean_heldout_self_minus_pooled_nats_per_fix'],5),'supported',round(b['coarse']['mean_xy_supported_fraction'],3))

if __name__=='__main__':main()
