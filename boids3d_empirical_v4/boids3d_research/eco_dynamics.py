"""Mechanistic 3D Boids + renewable/depletable resources + ecological-state tracking.

Synthetic known-truth experiment, not a fit to wild animal telemetry.
Agent steps determine both occupancy and resource consumption. No post-hoc
height or clock displacement is applied. 3D geometry uses arbitrary voxel units.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class EcologicalRules:
    shape: tuple[int,int,int] = (16,16,8)
    n_per_species: int = 7
    nights: int = 3
    steps: int = 480
    burn: int = 180
    thin: int = 4
    regenerative_rate: float = .014
    consumption: float = .0
    resource_pool: str = "shared"  # shared, separate by species, or private per agent
    resource_contrast: float = .24
    state_tracking: float = .0
    state_heterogeneity: float = .55
    state_fluctuation: float = .95
    social_strength: float = .06
    separation_strength: float = .12
    cohesion_strength: float = .0
    neighbor_k: int = 4
    learning_strength: float = .0
    individual_response_var: float = .0
    behavioral_mixture_var: float = .0  # personal foraging/transit duty cycle
    swap_personal_between_nights: bool = False
    seed: int = 17


def fields(shape, heterogeneity=0.55):
    nx,ny,nz=shape
    x,y,z=np.meshgrid(np.arange(nx),np.arange(ny),np.arange(nz), indexing='ij')
    # Two renewable food-resource types; vertical structuring arises in the
    # ecological field, not in a post-hoc displacement of flight locations.
    xy=.7+.25*np.cos(2*np.pi*x/nx)*np.sin(2*np.pi*y/ny)
    a=(0.12+.92*np.exp(-.5*((z-2.1)/1.75)**2))*xy
    b=(0.12+.92*np.exp(-.5*((z-5.0)/1.75)**2))*(1.4-xy)
    # State with overlapping local alternatives: time changes mean conditions,
    # spatial heterogeneity creates room for movement-mediated state retention.
    local=(np.sin(2*np.pi*x/nx)+.8*np.cos(2*np.pi*y/ny)+.55*(z-(nz-1)/2))
    E_base=2.5+heterogeneity*local
    assert a.shape==shape and b.shape==shape
    return np.stack([a,b]),E_base


def neighbors_vectors(pos, vel, L, k, group):
    n=len(pos)
    diff=pos[None,:,:]-pos[:,None,:]  # neighbor - focal
    diff[:,:,:2]=(diff[:,:,:2]+L[None,None,:2]/2)%L[None,None,:2]-L[None,None,:2]/2
    dist=np.linalg.norm(diff,axis=2)
    np.fill_diagonal(dist,np.inf)
    # Only conspecifics align. Collision repulsion still spans both species.
    conspecific=group[:,None]==group[None,:]
    align_dist=np.where(conspecific,dist,np.inf)
    kn=min(k,min(int((group==s).sum())-1 for s in np.unique(group)))
    ids=np.argpartition(align_dist,kn-1,axis=1)[:,:kn]
    local_v=vel[ids].mean(axis=1)
    # Repel everyone at close distances, including the other species.
    close=(dist<1.35)&(dist>1.e-6)
    rep=(-(diff/np.maximum(dist[:,:,None],1.e-6)**2)*close[:,:,None]).sum(axis=1)
    return local_v-vel,rep


def conspecific_cohesion(pos,L,k,group):
    """Topological conspecific-neighbour steering for optional classic-Boids cohort."""
    disp=pos[None,:,:]-pos[:,None,:]
    disp[:,:,:2]=(disp[:,:,:2]+L[None,None,:2]/2)%L[None,None,:2]-L[None,None,:2]/2
    dist=np.linalg.norm(disp,axis=2)
    dist=np.where(group[:,None]==group[None,:],dist,np.inf)
    np.fill_diagonal(dist,np.inf)
    nn=min(k,min(int(sum(group==s))-1 for s in np.unique(group)))
    ids=np.argpartition(dist,nn-1,axis=1)[:,:nn]
    direction=disp[np.arange(len(pos))[:,None],ids].mean(axis=1)
    mag=np.linalg.norm(direction,axis=1,keepdims=True)
    return direction*np.minimum(1,1/np.maximum(mag,1e-8))

def wrap_positions(pos,vel,L):
    pos[:,:2]%=L[:2]
    low=pos[:,2]<.15
    high=pos[:,2]>L[2]-.15
    pos[:,2]=np.clip(pos[:,2],.15,L[2]-.15)
    vel[low,2]=np.abs(vel[low,2]); vel[high,2]=-np.abs(vel[high,2])


def calc_summary(traces,used_states,alt_states,uptake,group,grid_shape):
    """Pairwise spatial overlap and matched-local-state error for each night/animal."""
    # traces: [night,individual,time,3]
    n=traces.shape[1]
    counts=np.zeros((n,int(np.prod(grid_shape))))
    for i in range(n):
        q=traces[:,i,:,:].reshape(-1,3)
        idx=np.floor(q).astype(int)
        idx[:,:2]%=np.array(grid_shape[:2])
        idx[:,2]=np.clip(idx[:,2],0,grid_shape[2]-1)
        flat=np.ravel_multi_index(idx.T,grid_shape)
        counts[i]=np.bincount(flat,minlength=counts.shape[1])
    P=(counts+.06)/(counts.sum(axis=1,keepdims=True)+.06*counts.shape[1])
    bc=np.sqrt(P[:,None,:]*P[None,:,:]).sum(axis=2)
    i,j=np.triu_indices(n,1)
    same=group[i]==group[j]
    within=float(bc[i[same],j[same]].mean())
    between=float(bc[i[~same],j[~same]].mean())
    # Unsigned intensity of temporal niche information (within identical
    # positions: same time histogram for every species in this experiment).
    # ODSP partition claim requires held-out biological units, not this number.
    target=2.5
    err_used=float(np.mean(np.abs(used_states-target)))
    err_available=float(np.mean(np.abs(alt_states-target)))
    frac=(err_available-err_used)/max(err_available,1.e-9)
    mean_feed=np.array([uptake[group==s].mean() for s in range(2)])
    # Compositional Hill number of occupied spatial voxels: this is NOT
    # mina's breeding-component effective number.
    neff=(1/(P**2).sum(axis=1)).mean()
    return {
        'within_species_overlap':within,
        'between_species_overlap':between,
        'segregation_excess':within-between,
        'mean_effective_used_voxels':float(neff),
        'used_state_mismatch':err_used,
        'matched_local_available_mismatch':err_available,
        'state_buffering_advantage':float(frac),
        'mean_uptake_by_species':mean_feed.tolist(),
        'mean_uptake':float(uptake.mean()),
    }


def run(r:EcologicalRules,return_trajectories=False):
    rng=np.random.default_rng(r.seed)
    L=np.array(r.shape,dtype=float)
    K,E_base=fields(r.shape,r.state_heterogeneity)
    n=2*r.n_per_species
    group=np.repeat(np.arange(2),r.n_per_species)
    # Stable within-species response preferences; no imposed flight-height differences.
    preferences=np.zeros((n,2))
    preferences[group==0]=[.5+r.resource_contrast,.5-r.resource_contrast]
    preferences[group==1]=[.5-r.resource_contrast,.5+r.resource_contrast]
    persistent_individual=rng.normal(0,.09,size=n)
    # Persistent, species-centered individual responsiveness. This is the
    # generating mechanism that the centered-identity falsification can target.
    if r.individual_response_var > 0:
        person_gain=rng.uniform(-1.0,1.0,size=n)
        person_gain-=np.array([person_gain[group==group[i]].mean() for i in range(n)])
    else:
        person_gain=np.zeros(n)
    if r.behavioral_mixture_var>0:
        mode_trait=rng.uniform(-1,1,size=n)
        p_feed=np.clip(.55+.42*r.behavioral_mixture_var*mode_trait,.05,.95)
    else:
        p_feed=np.repeat(.55,n)
    snapshots=[];actual=[];available=[];total_feed=np.zeros(n)
    if r.resource_pool not in ("shared","species","private"):
        raise ValueError("resource_pool must be shared, species or private")
    if r.resource_pool=="shared":
        resource=K.copy()
    elif r.resource_pool=="species":
        resource=np.broadcast_to(K,(2,*K.shape)).copy()
    else:
        resource=np.broadcast_to(K,(n,*K.shape)).copy()
    for night in range(r.nights):
        # New initial conditions prevent artificially continuous nights.
        pos=rng.uniform(0,1,(n,3))*L
        vel=rng.normal(0,.13,(n,3))
        if r.swap_personal_between_nights:
            person_gain_night=person_gain.copy()
            target_offset=persistent_individual.copy()
            for s in (0,1):
                ix=np.where(group==s)[0]
                person_gain_night[ix]=person_gain[rng.permutation(ix)]
                target_offset[ix]=persistent_individual[rng.permutation(ix)]
        else:
            person_gain_night=person_gain
            target_offset=persistent_individual
        target=2.5+r.learning_strength*target_offset
        if r.behavioral_mixture_var>0:
            if r.swap_personal_between_nights:
                p_feed_night=p_feed.copy()
                for s in (0,1):
                    ix=np.where(group==s)[0]
                    p_feed_night[ix]=p_feed[rng.permutation(ix)]
            else:
                p_feed_night=p_feed
            forage_mode=rng.random(n)<p_feed_night
        individual_state_gain=r.state_tracking*np.maximum(.01,1+r.individual_response_var*person_gain_night)
        for t in range(r.steps):
            # The state is a time-varying scalar field; actual local state is
            # sampled at each position before movement decisions are made.
            state_offset=r.state_fluctuation*np.sin((t+night*137)/74.)
            E=E_base+state_offset
            gradient_E=np.gradient(E)
            xyz=np.floor(pos).astype(int)
            xyz=np.minimum(xyz,np.array(r.shape)-1)
            loc=tuple(xyz.T)
            # Habitat state tracking: direction of decreasing mismatch to a
            # biologically motivated target, using local environmental gradient.
            u=E[loc]
            gE=np.stack([g[loc] for g in gradient_E],axis=1)
            track=-individual_state_gain[:,None]*(u-target)[:,None]*gE
            # Dynamic food attraction uses an actual within-run resource map.
            if t%5==0:
                if r.resource_pool=="shared":
                    grads=[np.gradient(resource[k]) for k in range(2)]
                elif r.resource_pool=="species":
                    grads=[[np.gradient(resource[s,k]) for k in range(2)] for s in range(2)]
                else:
                    grads=[[np.gradient(resource[i,k]) for k in range(2)] for i in range(n)]
            if r.resource_pool=="shared":
                gfood=np.array([[g[loc] for g in grads[k]] for k in range(2)])
                food_force=np.einsum('ik,kji->ij',preferences,gfood)
            else:
                food_force=np.array([
                    sum(preferences[i,k]*np.array([g[loc[0][i],loc[1][i],loc[2][i]]
                    for g in grads[int(group[i]) if r.resource_pool=="species" else i][k]]) for k in range(2))
                    for i in range(n)])
            alignment,separation=neighbors_vectors(pos,vel,L,r.neighbor_k,group)
            cohesion=conspecific_cohesion(pos,L,r.neighbor_k,group) if r.cohesion_strength else 0.0
            if r.behavioral_mixture_var>0:
                off=forage_mode&(rng.random(n)<(.08*(1-p_feed_night)))
                on=(~forage_mode)&(rng.random(n)<(.08*p_feed_night))
                forage_mode[off]=False
                forage_mode[on]=True
                patch_weight=np.where(forage_mode,.90,.12)
                state_weight=np.where(forage_mode,1.,.20)
                noise_sd=np.where(forage_mode,.085,.25)
                mot_noise=rng.normal(0,1,size=(n,3))*noise_sd[:,None]
                # Individual duty cycle changes the fraction of time devoted
                # to search vs patch feeding, rather than imposing a height.
                force=(patch_weight[:,None]*food_force+state_weight[:,None]*track+
                       r.social_strength*alignment+r.separation_strength*separation+r.cohesion_strength*cohesion-.30*vel+mot_noise)
            else:
                force=(.72*food_force+track+
                       r.social_strength*alignment+r.separation_strength*separation+r.cohesion_strength*cohesion-
                       .30*vel+rng.normal(0,.09,size=(n,3)))
            # Acceleration, speed, vertical-rate constraints on all species.
            norm=np.linalg.norm(force,axis=1,keepdims=True)
            force*=np.minimum(1,.26/np.maximum(norm,1.e-10))
            vel+=force
            vel[:,2]=np.clip(vel[:,2],-.26,.26)
            sp=np.linalg.norm(vel,axis=1,keepdims=True)
            vel*=np.minimum(1,.55/np.maximum(sp,1.e-10))
            pos+=vel
            wrap_positions(pos,vel,L)
            # Resource uptake is realized at the current position (not an
            # externally imposed output shift). Consumption feeds back on R.
            newloc=tuple(np.floor(pos).astype(int).T)
            if r.resource_pool=="shared":
                q=resource[:,newloc[0],newloc[1],newloc[2]].T
            elif r.resource_pool=="species":
                q=resource[group,:,newloc[0],newloc[1],newloc[2]]
            else:
                q=resource[np.arange(n),:,newloc[0],newloc[1],newloc[2]]
            eat=r.consumption*preferences*q
            total_feed+=(preferences*q).sum(axis=1)
            resource+=r.regenerative_rate*(K-resource)
            if r.resource_pool=="shared":
                for k in range(2):
                    np.add.at(resource[k],newloc,-eat[:,k])
            elif r.resource_pool=="species":
                for s in range(2):
                    mask=(group==s)
                    subloc=tuple(v[mask] for v in newloc)
                    for k in range(2):
                        np.add.at(resource[s,k],subloc,-eat[mask,k])
            else:
                for i in range(n):
                    resource[i,:,newloc[0][i],newloc[1][i],newloc[2][i]]-=eat[i]
            resource=np.clip(resource,0,None)
            if t>=r.burn and (t-r.burn)%r.thin==0:
                snapshots.append((night,pos.copy()))
                actual.append((night,E[tuple(np.floor(pos).astype(int).T)].copy()))
                # Neighbouring available environmental state matched in time.
                offsets=rng.integers(-2,3,size=(n,3))
                loc_alt=np.floor(pos).astype(int)+offsets
                loc_alt[:,:2]%=np.array(r.shape[:2])
                loc_alt[:,2]=np.clip(loc_alt[:,2],0,r.shape[2]-1)
                available.append((night,E[tuple(loc_alt.T)].copy()))
    per_night=[];per_actual=[];per_available=[]
    for night in range(r.nights):
        per_night.append(np.stack([arr for k,arr in snapshots if k==night],axis=1))
        per_actual.append(np.stack([arr for k,arr in actual if k==night],axis=1))
        per_available.append(np.stack([arr for k,arr in available if k==night],axis=1))
    tr=np.stack(per_night)
    a=np.stack(per_actual)
    av=np.stack(per_available)
    ans=calc_summary(tr,a,av,total_feed/(r.nights*r.steps),group,r.shape)
    ans['parameters']={x:getattr(r,x) for x in ('consumption','resource_pool','resource_contrast','state_tracking','state_heterogeneity','learning_strength','individual_response_var','behavioral_mixture_var','swap_personal_between_nights','seed')}
    if return_trajectories:return ans,tr,a,av,group
    return ans


def state_information(traces,group, bins_xy=4, pseudocount=.25):
    """ODSP-style H(Z|XY), I(S;Z|XY), and leave-one-night-out log score.

    Identity is the synthetic species label; this does not imply competition.
    Equal numbers of fixes per individual and night in the known-truth design.
    All scores are in nats per point, not an inferred biological effect size.
    """
    nights,n,T,_=traces.shape
    assert set(group)=={0,1}
    L=np.array([16,16,8])
    ix=np.floor(traces[...,0]*bins_xy/L[0]).astype(int).clip(0,bins_xy-1)
    iy=np.floor(traces[...,1]*bins_xy/L[1]).astype(int).clip(0,bins_xy-1)
    iz=np.floor(traces[...,2]).astype(int).clip(0,7)
    bins=bins_xy*bins_xy*8
    hist=np.zeros((nights,n,bins),dtype=float)
    for t in range(nights):
        for i in range(n):
            idx=(ix[t,i]*bins_xy+iy[t,i])*8+iz[t,i]
            hist[t,i]=np.bincount(idx,minlength=bins)
    # Raw empirical conditional information; independently smoothed below for
    # probabilities in out-of-sample scoring.
    hs=hist.reshape(nights,n,bins_xy*bins_xy,8)
    species=np.stack([hs[:,group==s].sum(axis=(0,1)) for s in (0,1)])
    pooled=species.sum(axis=0)
    pxyz=pooled/pooled.sum()
    pxy=pxyz.sum(axis=-1)
    h=float(-np.sum(pxyz*np.log(np.maximum(pxyz/np.maximum(pxy[...,None],1e-300),1e-300)),where=pxyz>0))
    psxyz=species/species.sum()
    psxy=psxyz.sum(axis=-1)
    pz_sxy=psxyz/np.maximum(psxy[...,None],1e-300)
    pz_xy=pxyz/np.maximum(pxy[...,None],1e-300)
    mi=float(np.sum(psxyz*np.log(np.maximum(pz_sxy/np.maximum(pz_xy[None,...],1e-300),1e-300)),where=psxyz>0))
    p_sxy=psxyz.sum(axis=-1)
    p_s=psxyz.sum(axis=(1,2))
    i_sxy=float(np.sum(p_sxy*np.log(np.maximum(p_sxy/np.maximum(p_s[:,None]*pxy[None,:],1e-300),1e-300)),where=p_sxy>0))
    return {'species_horizontal_partition_information_nats':max(0,i_sxy),
            'vertical_thickness_entropy_nats':h,
            'effective_vertical_states':float(np.exp(h)),
            'species_vertical_partition_information_nats':max(0,mi),
            'species_heldout_night_gains':heldout_species_state_gain(hist,group,bins_xy,pseudocount),
            'species_heldout_individual_gain':heldout_individual_species_gain(hist,group,bins_xy,pseudocount)}


def heldout_species_state_gain(hist,group,bins_xy=4,pseudocount=.25):
    nights,n,flat=hist.shape
    assert flat==bins_xy*bins_xy*8
    hs=hist.reshape(nights,n,bins_xy*bins_xy,8)
    results=[]
    for night in range(nights):
        others=hs[np.arange(nights)!=night]
        train_species=np.stack([others[:,group==s].sum(axis=(0,1)) for s in (0,1)])
        train_pool=train_species.sum(axis=0)
        self_cond=(train_species+pseudocount)/(train_species.sum(axis=-1,keepdims=True)+8*pseudocount)
        pool_cond=(train_pool+pseudocount)/(train_pool.sum(axis=-1,keepdims=True)+8*pseudocount)
        test=hs[night]
        scores=np.zeros(n)
        for i in range(n):
            ratio=np.log(self_cond[group[i]]/pool_cond)
            scores[i]=np.sum(test[i]*ratio)/max(test[i].sum(),1)
        results.append(float(scores.mean()))
    return results


def species_partition_calibration(traces,group,reps=199,seed=100):
    """Identity-label null; does not represent model-based causal competition."""
    observed=state_information(traces,group)
    _,n,_,_=traces.shape
    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(reps):
        perm=rng.permutation(group)
        a=state_information(traces,perm)
        null.append(np.mean(a['species_heldout_night_gains']))
    obs=np.mean(observed['species_heldout_night_gains'])
    return {'observed_nats_per_fix':float(obs),'null_mean_nats_per_fix':float(np.mean(null)),
            'calibrated_excess_nats_per_fix':float(obs-np.mean(null)),
            'p_one_sided':float((1+np.sum(np.array(null)>=obs))/(reps+1)),
            'reps':reps,'night_scores':observed['species_heldout_night_gains'],
            'thickness':observed['effective_vertical_states'],
            'information':observed['species_vertical_partition_information_nats']}



def heldout_individual_species_gain(hist,group,bins_xy=4,pseudocount=.25):
    """Predict every unseen individual's all-night states from other animals.

    This is a harder transfer test than leaving a night out while retaining
    the target individual in training; n individuals are the replication units.
    """
    nights,n,bins=hist.shape
    assert bins==bins_xy*bins_xy*8
    h=hist.reshape(nights,n,bins_xy*bins_xy,8)
    gain=[]
    for i in range(n):
        train=h[:,np.arange(n)!=i]
        gtrain=np.asarray(group)[np.arange(n)!=i]
        spec=train[:,gtrain==group[i]].sum(axis=(0,1))
        pooled=train.sum(axis=(0,1))
        sp=(spec+pseudocount)/(spec.sum(axis=-1,keepdims=True)+8*pseudocount)
        po=(pooled+pseudocount)/(pooled.sum(axis=-1,keepdims=True)+8*pseudocount)
        test=h[:,i]
        gain.append(float(np.sum(test*np.log(sp/po))/max(test.sum(),1)))
    return gain
