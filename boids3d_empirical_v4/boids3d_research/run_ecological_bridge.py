"""Predeclared, synthetic known-truth comparison of niche mechanisms.

This file enumerates its treatment arms before running them. Outputs are NOT
empirical bat, rail, raptor or penguin inferences. Seeds are independent model
realizations; individual fixes are not independent biological replicates.
"""
from dataclasses import replace,asdict
from pathlib import Path
from collections import defaultdict
import json
import numpy as np
from eco_dynamics import (EcologicalRules,run,state_information,
                          species_partition_calibration)

SEEDS=[17,23,47,71,101]
BASE=EcologicalRules(steps=480,burn=180,nights=3,thin=4)
SCENARIOS={
 'M0_no_diff_no_social':dict(resource_contrast=0,social_strength=0,consumption=0),
 'M1_social_only':dict(resource_contrast=0,consumption=0),
 'M2_resource_preferences':dict(resource_contrast=.24,consumption=0),
 'M3_shared_depletion':dict(resource_contrast=.24,consumption=.2,resource_pool='shared'),
 'M3_private_counterfactual':dict(resource_contrast=.24,consumption=.2,resource_pool='private'),
 'M3_depletion_no_prefs':dict(resource_contrast=0,consumption=.2,resource_pool='shared'),
 'M3_depletion_weak':dict(resource_contrast=.24,consumption=.04),
 'M3_depletion_strong':dict(resource_contrast=.24,consumption=.35),
 'M3_strong_preferences':dict(resource_contrast=.4,consumption=.2),
 'L0_no_portfolio_no_tracking':dict(state_heterogeneity=0,state_tracking=0),
 'L1_no_portfolio_tracking':dict(state_heterogeneity=0,state_tracking=.8),
 'L2_portfolio_no_tracking':dict(state_heterogeneity=.55,state_tracking=0),
 'L3_portfolio_tracking_weak':dict(state_heterogeneity=.55,state_tracking=.3),
 'L4_portfolio_tracking_strong':dict(state_heterogeneity=.55,state_tracking=.8),
 'L5_diverse_portfolio_tracking':dict(state_heterogeneity=1.1,state_tracking=.8),
 'B1_personal_target':dict(state_heterogeneity=.55,state_tracking=.8,learning_strength=.8),
}
KEYS=['within_species_overlap','between_species_overlap','segregation_excess',
      'state_buffering_advantage','used_state_mismatch','matched_local_available_mismatch',
      'mean_effective_used_voxels','mean_uptake']

def summarize(rows):
    d=defaultdict(list)
    for row in rows:d[row['scenario']].append(row)
    summary={}
    for name,rs in d.items():
        rec={'seeds':[r['seed'] for r in rs], 'n_simulations':len(rs)}
        for key in KEYS+['thickness_effective_vertical_states','species_vertical_MI_nats',
                        'cross_night_species_gain_nats']:
            v=np.array([r[key] for r in rs],float)
            rec[key+'_mean']=float(v.mean())
            rec[key+'_sd_across_seeds']=float(v.std(ddof=1))
            rec[key+'_range']=[float(v.min()),float(v.max())]
        rec['heldout_night_all_positive_runs']=sum(all(v>0 for v in r['cross_night_species_gains']) for r in rs)
        summary[name]=rec
    return summary


def run_study():
    results=[]
    for scenario,params in SCENARIOS.items():
        for seed in SEEDS:
            settings=replace(BASE,**params,seed=seed)
            metrics,tr,states,alternatives,groups=run(settings,return_trajectories=True)
            info=state_information(tr,groups)
            row={'scenario':scenario,'seed':seed,'params':asdict(settings),
                 **{k:metrics[k] for k in KEYS},
                 'thickness_effective_vertical_states':info['effective_vertical_states'],
                 'species_vertical_MI_nats':info['species_vertical_partition_information_nats'],
                 'cross_night_species_gain_nats':float(np.mean(info['species_heldout_night_gains'])),
                 'cross_night_species_gains':info['species_heldout_night_gains']}
            results.append(row)
            print(f"{scenario:32s} {seed:3d} overlap={row['between_species_overlap']:.3f} "
                  f"within-between={row['segregation_excess']:+.3f} "
                  f"buffer={row['state_buffering_advantage']:+.3f} "
                  f"species_g={row['cross_night_species_gain_nats']:+.3f}",flush=True)
    ss=summarize(results)
    # Paired counterfactual differences: no outcome-based choices.
    contrasts={}
    for name,a,b,key in [
        ('shared_minus_private_depletion_segregation','M3_shared_depletion','M3_private_counterfactual','segregation_excess'),
        ('shared_minus_private_depletion_food','M3_shared_depletion','M3_private_counterfactual','mean_uptake'),
        ('shared_minus_resource_only_segregation','M3_shared_depletion','M2_resource_preferences','segregation_excess'),
        ('tracking_minus_no_tracking_buffer','L4_portfolio_tracking_strong','L2_portfolio_no_tracking','state_buffering_advantage'),
        ('social_only_minus_no_social_segregation','M1_social_only','M0_no_diff_no_social','segregation_excess'),
        ('pref_minus_social_only_segregation','M2_resource_preferences','M1_social_only','segregation_excess'),
    ]:
        x={r['seed']:r[key] for r in results if r['scenario']==a}
        y={r['seed']:r[key] for r in results if r['scenario']==b}
        dif=np.array([x[s]-y[s] for s in SEEDS])
        contrasts[name]={'mean':float(dif.mean()),'range':[float(dif.min()),float(dif.max())],
                         'per_seed':dict(zip(map(str,SEEDS),map(float,dif))),
                         'positive_seed_count':int((dif>0).sum()),
                         'definition':f'{a} minus {b}: {key}'}
    # Audit identical null vs demonstrably species-specific treated data;
    # calibration is performed on intact whole-individual identity labels.
    audit={}
    for name in ['M0_no_diff_no_social','M1_social_only','M2_resource_preferences',
                 'M3_shared_depletion','M3_private_counterfactual',
                 'L4_portfolio_tracking_strong','B1_personal_target']:
        for seed in (17,23,47):
            m,tr,a,alt,g=run(replace(BASE,**SCENARIOS[name],seed=seed),return_trajectories=True)
            audit[f'{name}__seed{seed}']=species_partition_calibration(tr,g,reps=199,seed=seed+121)
    return {'study':'ecological_boids_mechanism_bridge_v1',
            'status':'synthetic_dynamical_known_truth_not_observational_evidence',
            'predeclared_SEEDS':SEEDS,'base':asdict(BASE),'arms':SCENARIOS,
            'outputs':results,'summary':ss,'paired_differences':contrasts,
            'species_transfer_identity_permutation_audit':audit,
            'centered_shape_audit_correction':{'status':'external corrected assay',
                                              'method':'voxel-unit centered bins; conspecific-only peers',
                                              'script':'validate_behavioral_mixture.py',
                                              'results':'eco_dynamics_behavioral_mixture.json'},
            'limitations':[
                'Private resources are a mechanistic counterfactual, not a field-realistic animal population.',
                'Resource depletion without a private-resource comparison confounds self-depletion and competition.',
                'Conditional information and out-of-sample score do not prove competitive displacement.',
                'Spatial voxel use is not breeding-site patch abundance or penguin effective component number.',
                'Local available states are nearby snapshots, not movement-matched random trajectories.',
                'Larger design exploration and independent seeds needed before identifying a threshold.',
            ]}

if __name__=='__main__':
    out=run_study()
    path=Path(__file__).with_name('eco_dynamics_factorial_results.json')
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('SAVED',path)
    for k,v in out['summary'].items():
        print('SUM',k,round(v['segregation_excess_mean'],4),round(v['state_buffering_advantage_mean'],4),
              round(v['cross_night_species_gain_nats_mean'],4))
    print('CONTRASTS')
    for k,v in out['paired_differences'].items():print(k,v['mean'],v['positive_seed_count'])
