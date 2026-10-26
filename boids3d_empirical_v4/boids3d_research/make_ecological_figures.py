"""Render research diagnostic figures from saved synthetic output receipts."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).parent
V=json.loads((D/'eco_dynamics_independent_validation.json').read_text())['summary']
F=json.loads((D/'eco_dynamics_factorial_results.json').read_text())['summary']
B=json.loads((D/'eco_dynamics_behavioral_mixture.json').read_text())['summary']

names={
 'negative_no_species_difference':'No species differences',
 'social_no_preference_difference':'Social rules only',
 'resource_preference_only':'Resource preferences',
 'resource_shared_depletion':'Shared depletion',
 'resource_private_depletion':'Private-resource control',
 'state_tracking':'Environmental tracking',
}
fig,ax=plt.subplots(figsize=(8.5,5.4))
for i,(name,label) in enumerate(names.items()):
    x=V[name]['grid_8x8x4_segregation_mean']
    y=V[name]['vertical_conditional_information_nats_mean']
    ax.scatter(x,y,s=70)
    offsets={
        'negative_no_species_difference':(12,18),
        'social_no_preference_difference':(12,-16),
        'resource_preference_only':(-7,12),
        'resource_shared_depletion':(8,-16),
        'resource_private_depletion':(-8,10),
        'state_tracking':(-7,-17),
    }
    off=offsets[name]
    ax.annotate(label,(x,y),xytext=off,textcoords='offset points',fontsize=8,
                ha='right' if name in ('resource_preference_only','resource_private_depletion','state_tracking') else 'left')
ax.axvline(0,color='.7',lw=.8)
ax.set_xlim(-.035,.68);ax.set_ylim(-.035,.46)
ax.set_xlabel('Spatial segregation: within-species minus between-species 3D overlap')
ax.set_ylabel('Conditional vertical partition: I(Species; Z | X,Y) [nats]')
ax.set_title('Spatial separation and conditional vertical differentiation diverge')
ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(D/'fig_spatial_vs_vertical_information.png',dpi=170)
plt.close(fig)

selected=[('L0_no_portfolio_no_tracking','Uniform; no tracking'),
          ('L1_no_portfolio_tracking','Uniform; tracking'),
          ('L2_portfolio_no_tracking','Diverse; no tracking'),
          ('L3_portfolio_tracking_weak','Diverse; weak tracking'),
          ('L4_portfolio_tracking_strong','Diverse; strong tracking'),
          ('L5_diverse_portfolio_tracking','Highly diverse; tracking')]
fig,ax=plt.subplots(figsize=(9.6,4.4))
mu=[F[n]['state_buffering_advantage_mean'] for n,_ in selected]
sd=[F[n]['state_buffering_advantage_sd_across_seeds'] for n,_ in selected]
x=np.arange(len(selected));ax.bar(x,mu,yerr=sd,capsize=4)
ax.set_xticks(x);ax.set_xticklabels([s for _,s in selected],rotation=18,ha='right',fontsize=8)
ax.set_ylabel('Relative reduction in target-state mismatch vs local alternatives')
ax.set_title('Environmental-state buffering requires accessible local heterogeneity')
ax.axhline(0,linewidth=.8,color='.6')
fig.tight_layout();fig.savefig(D/'fig_local_portfolio_tracking.png',dpi=170)
plt.close(fig)

selected=[('shared_rule_no_personal_mixture','Shared rule'),
          ('stable_personal_mixture','Personal mode mixture'),
          ('night_swapped_personal_mixture','Night-swapped mixture'),
          ('stable_personal_mixture_plus_depletion','Mixture + depletion'),
          ('no_personal_mixture_plus_depletion','No mixture + depletion')]
fig,ax=plt.subplots(figsize=(9.6,4.4))
mu=[B[n]['individual_identity_null_centered_gain_mean'] for n,_ in selected]
minv=[B[n]['gain_range'][0] for n,_ in selected]
maxv=[B[n]['gain_range'][1] for n,_ in selected]
x=np.arange(len(selected));ax.bar(x,mu,yerr=np.array([np.array(mu)-np.array(minv),np.array(maxv)-np.array(mu)]),capsize=4)
ax.set_xticks(x);ax.set_xticklabels([s for _,s in selected],rotation=18,ha='right',fontsize=8)
ax.set_ylabel('Null-calibrated centered-height identity gain [nats/fix]')
ax.set_title('Stable behavioral-state mixtures yield repeatable individual shapes')
ax.axhline(0,linewidth=.9,color='.5')
fig.tight_layout();fig.savefig(D/'fig_personal_mixture_identity.png',dpi=170)
plt.close(fig)
A=json.loads((D/'annual_breeding_patch_bridge.json').read_text())['summary']
keys=['fixed_share_downsampling','homogeneous_habitat_high_mobility',
      'heterogeneous_habitat_low_mobility','heterogeneous_habitat_high_mobility']
labels=['Fixed shares','Uniform substrate','Patchy; low retargeting','Patchy; high retargeting']
fig,ax=plt.subplots(figsize=(8.2,4.6))
values=[100*A[k]['mean_relative_change'] for k in keys]
ax.bar(np.arange(len(keys)),values)
ax.set_xticks(np.arange(len(keys)));ax.set_xticklabels(labels,rotation=12,ha='right',fontsize=9)
ax.set_ylabel('Change in effective breeding-component number [%]')
ax.set_title('Annual patch redistribution exceeds fixed-share count thinning only with local filtering')
ax.axhline(0,lw=.8,color='.5')
for i,k in enumerate(keys):
    ytext=(values[i]/2 if values[i]<-8 else values[i]-2.1)
    ax.text(i,ytext,f"{A[k]['significant_excess_contraction_count']}/20 null tests",
            ha='center',va='center',fontsize=8)
fig.tight_layout();fig.savefig(D/'fig_annual_effective_components.png',dpi=170)
plt.close(fig)
print('Figures rendered')
