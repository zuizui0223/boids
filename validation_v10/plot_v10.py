#!/usr/bin/env python3
"""Render two interpretable and separate figures from immutable synthetic JSON."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_axes(d, out):
    names=['source_spacing_shared_resources','novel_spacing_shared_resources',
           'novel_spacing_reassembled_resources']
    labels=['Shared resource\n10 m spacing','Shared resource\n25 m spacing',
            'Resource shift\n25 m spacing']
    keys=['species_horizontal_information_nats','species_vertical_information_given_xy_nats']
    x=np.arange(3)
    fig,ax=plt.subplots(figsize=(9,5.4))
    for j,key in enumerate(keys):
        gr=[d['worlds'][n]['grains']['coarse']['metric_ranges'][key] for n in names]
        lo=np.array([a['min'] for a in gr]);hi=np.array([a['max'] for a in gr]);v=(lo+hi)/2
        xx=x+(-.19 if j==0 else .19)
        ax.bar(xx,v,width=.36,yerr=np.vstack([v-lo,hi-v]),capsize=5,
               label=('Horizontal I(S;XY)' if j==0 else 'Vertical I(S;Z|XY)'))
    ax.set_xticks(x,labels)
    ax.set_ylabel('Mutual information (nats)')
    ax.set_ylim(0,.72)
    ax.set_title('Synthetic niche-axis predictions across five source-equivalent rules')
    ax.legend(frameon=False)
    fig.tight_layout();out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=170);plt.close(fig)


def plot_profiles(d,out):
    worlds=['source_spacing_shared_resources','novel_spacing_reassembled_resources']
    labels=['Shared resource','Shifted resource']
    stable=[d['worlds'][w]['1.0']['coarse']['mean_heldout_self_minus_pooled_nats_per_fix'] for w in worlds]
    shuffled=[d['policy_reshuffle_negative_control'][w]['coarse']['mean_heldout_self_minus_pooled_nats_per_fix'] for w in worlds]
    x=np.arange(2)
    fig,ax=plt.subplots(figsize=(7.5,4.7))
    ax.bar(x-.18,stable,width=.35,label='Stable individual target')
    ax.bar(x+.18,shuffled,width=.35,label='Target reassigned across seeds')
    ax.set_xticks(x,labels);ax.set_ylabel('Held-out seed self − conspecific log score (nats/fix)')
    ax.axhline(0,linewidth=.8,color='gray')
    ax.set_title('Synthetic individual-profile predictability: positive vs control')
    ax.legend(frameon=False)
    fig.tight_layout();out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=170);plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--niche',type=Path,default=Path('validation_v10/results/niche_identified_set_v10.json'))
    parser.add_argument('--profiles',type=Path,default=Path('validation_v10/results/profile_seed_transfer_v10.json'))
    parser.add_argument('--outdir',type=Path,default=Path('validation_v10/figures'))
    args=parser.parse_args()
    plot_axes(json.loads(args.niche.read_text()),args.outdir/'fig_v10_species_niche_axes.png')
    plot_profiles(json.loads(args.profiles.read_text()),args.outdir/'fig_v10_individual_profile_transfer.png')

if __name__=='__main__':main()
