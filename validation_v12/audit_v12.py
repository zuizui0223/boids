#!/usr/bin/env python3
"""Fail-closed paired-seed audit of synthetic v12 hierarchy transfer results.

The unit of replication is an independent simulator RNG world (30 seeds),
NOT individual fixes, 12 model agents or 8 simulated days.
The manuscript-level interpretation is exploratory, not preregistered.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

MAIN = Path('validation_v12/results/endogenous_policy_v12.json')
NULL = Path('validation_v12/results/guild_relabel_null_v12.json')
FAMILY = Path('validation_v12/results/force_family_sensitivity_v12.json')
BOOT_B = 5000
BOOT_SEED = 20261029

COMPARISONS = (
 ('private_learning_only','neutral','patch_identity_gain_nats'),
 ('private_learning_only','neutral','vertical_identity_gain_given_xy_nats'),
 ('private_learning_plus_boids','private_learning_only','vertical_identity_gain_given_xy_nats'),
 ('learning_plus_social','private_learning_plus_boids','patch_identity_gain_nats'),
 ('learning_plus_social','private_learning_plus_boids','guild_patch_gain_nats'),
 ('learning_plus_social','private_learning_plus_boids','guild_vertical_gain_given_xy_nats'),
 ('learning_plus_social','private_learning_plus_boids','species_niche.horizontal_information_nats'),
 ('learning_plus_social','learning_plus_social_no_boids','guild_patch_gain_nats'),
 ('learning_plus_social','learning_plus_social_no_boids','species_niche.horizontal_information_nats'),
 ('learning_social_depletion','learning_plus_social','guild_patch_gain_nats'),
 ('learning_social_depletion','learning_plus_social','guild_vertical_gain_given_xy_nats'),
 ('learning_social_depletion','learning_plus_social','species_niche.horizontal_information_nats'),
 ('learning_social_history_reset','learning_plus_social','guild_patch_gain_nats'),
 ('learning_social_history_shuffle','learning_plus_social','guild_patch_gain_nats'),
 ('learning_mixed_species_social','learning_plus_social','guild_patch_gain_nats'),
 ('learning_mixed_species_social','learning_plus_social','species_niche.horizontal_information_nats')
)


def extract_metric(row, key):
    if key.startswith('species_niche.'):
        return float(row['species_niche'][key.split('.',1)[1]])
    return float(row[key])


def group_rows(document):
    rows={}
    for r in document['per_seed']:
        k=(r['condition'],str(r['alpha']),r['seed'])
        if k in rows:raise ValueError('Duplicate seed/condition')
        rows[k]=r
    return rows


def paired_seed_contrasts(main:dict, null:dict, family:dict,
                          boot_b:int=BOOT_B, boot_seed:int=BOOT_SEED):
    if main['status']!='EXPLORATORY_SIMULATOR_ONLY_NOT_WILD_EVIDENCE' or len(main['seeds'])<3:
        raise ValueError('Malformed or insufficient primary worlds')
    if null['status']!='SYNTHETIC_RELABELLING_CONTROL_NOT_FIELD_SPECIES_INFERENCE':
        raise ValueError('Malformed relabel null receipt')
    if main['seeds']!=family['seeds'] or len(null['per_seed'])==0:
        raise ValueError('Seed mismatch')
    if boot_b<100:raise ValueError('Too few bootstrap draws')
    rows=group_rows(main)
    rng=np.random.default_rng(boot_seed)
    seeds=main['seeds']; boots=rng.integers(0,len(seeds),size=(boot_b,len(seeds)))
    comparisons={}
    for a,b,metric in COMPARISONS:
        vals=np.asarray([extract_metric(rows[(a,'1.0',seed)],metric)-extract_metric(rows[(b,'1.0',seed)],metric) for seed in seeds])
        boot=vals[boots].mean(axis=1)
        comparisons[f'{a}__minus__{b}__{metric}']={
            'mean_paired_seed_change':float(vals.mean()),
            'independent_seed_bootstrap95':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
            'positive_seed_differences':int(np.sum(vals>0)),
            'negative_seed_differences':int(np.sum(vals<0)),
            'n_independent_simulation_seeds':len(seeds)}
    null_comp={}
    for condition in null['results']:
        relevant=sorted([r for r in null['per_seed'] if r['condition']==condition],key=lambda x:x['seed'])
        if [r['seed'] for r in relevant]!=seeds:raise ValueError('Permutation-null seed mismatch')
        vals=np.array([r['horizontal_excess_over_pair_null'] for r in relevant])
        boot=vals[boots].mean(axis=1)
        null_comp[condition]={
            'mean_excess_horizontal_info_over_pair_label_null':float(vals.mean()),
            'independent_seed_bootstrap95':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
            'excess_positive_seed_count':int(np.sum(vals>0)),
            'per_seed_min_exact_p':.1,
            'interpretation':'The actual guild split is compared with all 20 dyad-preserving alternatives; exact split-level p never below 0.1.'}
    sensitivity={}
    for cond in family['results']:
        vals={alpha:family['results'][cond][alpha] for alpha in ('0.0','1.0','2.0')}
        sensitivity[cond]={
         'horizontal_info_means_by_alpha':{a:float(x['species_niche.horizontal_information_nats']['mean']) for a,x in vals.items()},
         'guild_patch_gain_means_by_alpha':{a:float(x['guild_patch_gain_nats']['mean']) for a,x in vals.items()},
         'vertical_identity_gain_means_by_alpha':{a:float(x['vertical_identity_gain_given_xy_nats']['mean']) for a,x in vals.items()}}
    r=[rows[('learning_plus_social','1.0',seed)] for seed in seeds]
    lefts=sum(x['signed_species_x_gap_m']<0 for x in r)
    return {'study':'v12-ecological-hierarchy-driver-audit',
      'status':'EXPLORATORY_SYNTHETIC_PAIRED_SEED_COMPARISON',
      'independence_unit':'simulated RNG world; no biological population-level confidence',
      'bootstrap':{'draws':boot_b,'seed':boot_seed,'resample_unit':'paired stochastic seed, all models under same seed'},
      'species_orientation':{'n_positive_signed_x_separation':int(len(seeds)-lefts),'n_negative_signed_x_separation':int(lefts),
         'mean_absolute_group_x_separation_m':float(np.mean([x['absolute_species_x_gap_m'] for x in r])),
         'warning':'Stochastic guild polarity is not a predicted species-specific left or right habitat.'},
      'paired_differences':comparisons,'guild_relabel_excess':null_comp,
      'source_equivalent_force_sensitivity':sensitivity,
      'limits':['Not an independent empirical study; same simulator family and chosen strengths.',
                'The choice-conformity term is NOT a Reynolds separation/alignment/cohesion movement force.',
                'No fixed agent habitat targets are used; the habit reinforcement rule IS imposed.',
                'Resource depletion is an imposed dynamical equation; this does not identify wild competition.',
                'Condition strengths and 3D grain were explored within the simulator; do not claim confirmatory p values.',
                'Group membership is assortative social connectivity between identical synthetic guilds, not evolutionary species divergence.']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--main',type=Path,default=MAIN)
    parser.add_argument('--null',type=Path,default=NULL)
    parser.add_argument('--family',type=Path,default=FAMILY)
    parser.add_argument('--out',type=Path,default=Path('validation_v12/results/driver_audit_v12.json'))
    args=parser.parse_args()
    d=paired_seed_contrasts(json.loads(args.main.read_text()),json.loads(args.null.read_text()),json.loads(args.family.read_text()))
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(d,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    for key,x in d['paired_differences'].items():
        print(key,round(x['mean_paired_seed_change'],4),tuple(round(z,4) for z in x['independent_seed_bootstrap95']))

if __name__=='__main__':main()
