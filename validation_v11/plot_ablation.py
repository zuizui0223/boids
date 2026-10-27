#!/usr/bin/env python3
"""Plot source-checked synthetic v11 receipt; no empirical animal values."""
import argparse, json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ORDER=('no_species_resource_contrast','vertical_resource_contrast',
       'horizontal_resource_contrast','both_resource_contrasts')
LABELS=('No species resource difference','Vertical resource difference',
        'Horizontal resource difference','Both resource differences')


def plots(receipt:dict,dest:Path):
    dest.mkdir(parents=True,exist_ok=True)
    # Graph 1: four models at each environment - effects without/in social Boids.
    x=np.arange(4,dtype=float);width=.19
    fig,ax=plt.subplots(figsize=(12.8,5.2))
    for shift,part,k,label in [(-1.5,'social_off','I_species_XY','XY, social off'),
                                (-.5,'social_on','I_species_XY','XY, social on'),
                                (.5,'social_off','I_species_Z_given_XY','Z | XY, social off'),
                                (1.5,'social_on','I_species_Z_given_XY','Z | XY, social on')]:
        y=[receipt['niche_by_world'][world]['coarse']['by_candidate'][part]['1.0'][k]
           for world in ORDER]
        ax.bar(x+shift*width,y,width=width,label=label)
    ax.set_xticks(x,LABELS,rotation=11,ha='right')
    ax.set_ylabel('Species identity information (nats)')
    ax.set_title('Species niche-axis differentiation is mainly imposed by resource targets')
    ax.legend(frameon=False,ncol=2)
    ax.grid(axis='y',alpha=.2)
    fig.tight_layout()
    f=dest/'fig_v11_driver_by_niche_axis.png';fig.savefig(f,dpi=175)
    plt.close(fig)

    # Graph 2: separate within-species target-offset negative control.
    fig,ax=plt.subplots(figsize=(8.6,4.7))
    w=.3;x=np.arange(2)
    for shift,social,label in [(-.5,'social_off','social off'),(.5,'social_on','social on')]:
        a=receipt['role_specific_vertical_target_control'][f'{social}:coarse']
        vals=[a['zero_role_target_offset_individual_information'],a['imposed_target_role_offset_individual_information']]
        ax.bar(x+shift*w,vals,width=w,label=label)
    ax.set_xticks(x,['No individual z-target offsets','±2.5 m target offsets'])
    ax.set_ylabel('I(individual; Z | XY, species) (nats)')
    ax.set_title('Within-species identity depends mainly on imposed individual targets')
    ax.legend(frameon=False)
    ax.grid(axis='y',alpha=.2)
    fig.tight_layout()
    q=dest/'fig_v11_individual_target_ablation.png';fig.savefig(q,dpi=175)
    plt.close(fig)
    return (f,q)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--receipt',type=Path,default=Path('validation_v11/results/environment_ablation.json'))
    parser.add_argument('--out-dir',type=Path,default=Path('validation_v11/figures'))
    args=parser.parse_args()
    r=json.loads(args.receipt.read_text());p=plots(r,args.out_dir)
    for v in p:print(v)

if __name__=='__main__':main()
