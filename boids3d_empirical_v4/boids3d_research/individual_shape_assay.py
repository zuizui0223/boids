"""Within-species, whole-night label calibrated centered-height individuality.

No comparison to heterospecifics is allowed in the peer baseline.  Bin edges
are physical simulation voxel units (the older m-unit edges were unsuitable).
"""
from dataclasses import replace
import numpy as np
from eco_dynamics import run,EcologicalRules
from boids3d_bridge import centered_height_histories

EDGES=np.array([-np.inf,-2,-1.25,-.75,-.4,-.15,.15,.4,.75,1.25,2,np.inf])


def score(hist,group,labels=None,pseudocount=.5):
    nights,n,bins=hist.shape
    if labels is None:labels=np.tile(np.arange(n),(nights,1))
    out=np.zeros((nights,n))
    for t in range(nights):
        for i in range(n):
            target=labels[t,i]
            train=hist[np.arange(nights)!=t]
            trainlabels=labels[np.arange(nights)!=t]
            own=train[trainlabels==target].sum(axis=0)
            peer_labs=np.where(group==group[i])[0]
            other=train[np.isin(trainlabels,peer_labs)&(trainlabels!=target)].sum(axis=0)
            q=(own+pseudocount)/(own.sum()+bins*pseudocount)
            r=(other+pseudocount)/(other.sum()+bins*pseudocount)
            out[t,i]=np.dot(hist[t,i],np.log(q/r))/hist[t,i].sum()
    return float(out.mean())


def calibrated(tr,group,seed=1,reps=199):
    h=centered_height_histories(tr,edges=EDGES)
    obs=score(h,group)
    rng=np.random.default_rng(seed)
    null=[]
    for j in range(reps):
        labs=np.tile(np.arange(len(group)),(len(h),1))
        for t in range(len(h)):
            for s in (0,1):
                ix=np.where(group==s)[0]
                labs[t,ix]=rng.permutation(ix)
        null.append(score(h,group,labs))
    null=np.array(null)
    return {'raw_gain':obs,'null_mean':float(null.mean()),'null_centered_gain':float(obs-null.mean()),
            'p_one_sided':float((1+np.sum(null>=obs))/(reps+1)),
            'permutations':reps}

if __name__=='__main__':
    for name,params in {
        'shared':dict(state_tracking=.8),
        'heterogeneous':dict(state_tracking=.8,individual_response_var=1.25),
        'swapped':dict(state_tracking=.8,individual_response_var=1.25,swap_personal_between_nights=True),
        'target':dict(state_tracking=.8,learning_strength=.8),
    }.items():
        for seed in (17,23,47):
            m,tr,a,alt,g=run(EcologicalRules(steps=480,burn=180,nights=3,seed=seed,**params),return_trajectories=True)
            result=calibrated(tr,g,seed=seed+300,reps=99)
            print(name,seed,result,flush=True)
