#!/usr/bin/env python3
"""Publication-style plots of only synthetic v12 receipts, no invented animals."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RESULTS = Path('validation_v12/results')
FIGURES = Path('validation_v12/figures')

def render():
    a=json.loads((RESULTS/'endogenous_policy_v12.json').read_text())
    b=json.loads((RESULTS/'social_influence_scan_v12.json').read_text())
    c=json.loads((RESULTS/'crossover_bootstrap_v12.json').read_text())
    FIGURES.mkdir(exist_ok=True,parents=True)
    selected=[
      ('neutral','No history'),
      ('private_learning_only','Private habit'),
      ('learning_plus_social','Assortative learning'),
      ('learning_social_depletion','Resource depletion'),
      ('learning_mixed_species_social','Mixed social contacts')]
    individual=np.array([a['results'][key]['1.0']['vertical_identity_gain_given_xy_nats']['mean'] for key,_ in selected])
    guild=np.array([a['results'][key]['1.0']['guild_vertical_gain_given_xy_nats']['mean'] for key,_ in selected])
    ix=np.arange(len(selected))
    f,ax=plt.subplots(figsize=(10.5,5.2))
    ax.bar(ix-.18,individual,.35,label='Within-guild individual: held-out Z | XY')
    ax.bar(ix+.18,guild,.35,label='Guild label: held-out Z | XY')
    ax.axhline(0.,lw=1)
    ax.set_xticks(ix,[name for _,name in selected],rotation=12,ha='right')
    ax.set_ylabel('Predictive log-score improvement (nats / fix)')
    ax.set_title('From private habits to guild-level 3D-use predictions\nSynthetic 3D agent model, 30 independent RNG worlds')
    ax.legend(loc='upper right',fontsize=9)
    ax.text(.02,.02,'Identical innate resource preferences; fixed learning/choice rules.\nNot evidence of learning or competition in wild animals.',transform=ax.transAxes,fontsize=8)
    f.tight_layout()
    f.savefig(FIGURES/'fig_v12_individual_vs_group_3d_gain.png',dpi=175)
    plt.close(f)

    xs=np.array(b['strengths'])
    individual=np.array([v['scores']['patch_personal']['mean'] for v in b['worlds']])
    guild=np.array([v['scores']['patch_guild']['mean'] for v in b['worlds']])
    f,ax=plt.subplots(figsize=(9.4,5.2))
    ax.plot(xs,individual,'o-',label='Individual history')
    ax.plot(xs,guild,'s-',label='Assortative guild history')
    xcross=c['estimated_gain_crossover'];lo,hi=c['bootstrap_interpolated_95pct_range']
    ax.axhline(0.,lw=.9)
    ax.axvline(xcross,ls='--',lw=1,label='Interpolated gain crossing')
    ax.axvspan(lo,hi,alpha=.12,label='RNG-seed bootstrap range (model only)')
    ax.set_xlabel('Assortative social-choice feedback strength (arbitrary model units)')
    ax.set_ylabel('Held-out patch-choice log-score gain (nats / choice)')
    ax.set_title('Which level carries predictive information?\nKnown-truth synthetic simulator, 30 RNG worlds')
    ax.legend(loc='upper left',fontsize=9)
    ax.text(.02,.02,'The crossing is not a physical or biological phase transition.',transform=ax.transAxes,fontsize=8)
    f.tight_layout()
    f.savefig(FIGURES/'fig_v12_social_coupling_prediction_crossover.png',dpi=175)
    plt.close(f)
    return [str(p) for p in sorted(FIGURES.glob('*.png'))]

if __name__=='__main__':print('\n'.join(render()))
