"""Synthetic-only 3D niche overlap, within/between group decomposition."""
import json
import numpy as np
from boids3d_bridge import simulate


def profiles(traces, bins=(7,7,8), smooth=0.5):
    xyz=traces.transpose(1,0,2,3).reshape(traces.shape[1],-1,3)
    edges=[np.linspace(-210,210,bins[0]+1),np.linspace(-210,210,bins[1]+1),np.linspace(5,200,bins[2]+1)]
    result=[]
    for track in xyz:
        counts=np.histogramdd(track,bins=edges)[0].ravel()+smooth
        result.append(counts/counts.sum())
    return np.stack(result)


def overlap_matrix(p):
    return np.sqrt(p[:,None,:]*p[None,:,:]).sum(axis=2)


def partition_summary(p, groups):
    mat=overlap_matrix(p)
    i,j=np.triu_indices(len(groups),1)
    same=np.array(groups)[i]==np.array(groups)[j]
    return {'within_group_mean_3d_overlap':float(mat[i[same],j[same]].mean()),
            'between_group_mean_3d_overlap':float(mat[i[~same],j[~same]].mean()),
            'between_minus_within':float(mat[i[~same],j[~same]].mean()-mat[i[same],j[same]].mean())}


def main():
    out={}
    for seed in [17,23,47,71,101]:
        tr,g=simulate(model='boids_personal',method='topological',seed=seed,n=14,steps=900,burn=180)
        p=profiles(tr)
        # Deliberate artificial labels: groups are sorted by vertical-response gain.
        labels=np.arange(14)>=7
        out[str(seed)]={'random_taxon_labels':partition_summary(p,np.random.default_rng(seed).permutation(labels)),
                        'gain_sorted_pseudotaxa':partition_summary(p,labels)}
    with open('niche_partition_synthetic.json','w') as f:json.dump(out,f,indent=2)
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
