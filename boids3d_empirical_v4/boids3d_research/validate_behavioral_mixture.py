"""Predeclared prospective synthetic ablation of persistent behavioural mixture.

Biological unit=individual, heldout unit=whole night, same-species comparison.
Fitted outcome must be centered in simulation *voxel* units, not metres.
"""
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
import json
import numpy as np
from eco_dynamics import EcologicalRules,run
from individual_shape_assay import calibrated
from validate_ecological_bridge import binned_overlap

SEEDS=(17,23,47,71,101)
ARMS={
  'shared_rule_no_personal_mixture':dict(),
  'stable_personal_mixture':dict(behavioral_mixture_var=1.0),
  'night_swapped_personal_mixture':dict(behavioral_mixture_var=1.0,swap_personal_between_nights=True),
  'stable_personal_mixture_plus_depletion':dict(behavioral_mixture_var=1.0,consumption=.2),
  'no_personal_mixture_plus_depletion':dict(consumption=.2),
}

def main():
  rows=[]
  for arm,params in ARMS.items():
    for seed in SEEDS:
      rules=EcologicalRules(steps=800,burn=180,nights=4,thin=4,seed=seed,**params)
      result,tr,a,av,g=run(rules,return_trajectories=True)
      within=calibrated(tr,g,seed=seed+500,reps=199)
      metric=binned_overlap(tr,g,(4,4,4))
      rows.append({'arm':arm,'seed':seed,'centered_identity':within,
                   'coarse_spatial_within_species_overlap':metric['within'],
                   'coarse_spatial_between_species_overlap':metric['between'],
                   'state_buffering_advantage':result['state_buffering_advantage']})
      print(arm,seed,'identity_gain',round(within['null_centered_gain'],3),'p',within['p_one_sided'],
            'same-species_spatial_overlap',round(metric['within'],3),flush=True)
  summary={}
  for arm in ARMS:
    r=[x for x in rows if x['arm']==arm]
    summary[arm]={'individual_identity_null_centered_gain_mean':float(np.mean([x['centered_identity']['null_centered_gain'] for x in r])),
                  'gain_range':[float(np.min([x['centered_identity']['null_centered_gain'] for x in r])),float(np.max([x['centered_identity']['null_centered_gain'] for x in r]))],
                  'passes_0.05_of_5':sum(x['centered_identity']['p_one_sided']<=.05 for x in r),
                  'same_species_spatial_overlap':float(np.mean([x['coarse_spatial_within_species_overlap'] for x in r]))}
  out={'status':'exploratory_synthetic_known_truth',
       'measurement':'same-species leave-one-night-out centered z shape; whole-agent-night label permutation',
       'predeclared_seeds':SEEDS,'parameters':asdict(EcologicalRules(steps=800,burn=180,nights=4,thin=4)),
       'scenarios':ARMS,'rows':rows,'summary':summary}
  dest=Path(__file__).with_name('eco_dynamics_behavioral_mixture.json')
  dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
  print('SAVED',dest)
  for k,v in summary.items():print('SUM',k,v,flush=True)

if __name__=='__main__':main()
