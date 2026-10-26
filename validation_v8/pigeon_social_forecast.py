#!/usr/bin/env python3
"""v8 frozen external pigeon pair prediction: own past vs actual partner vs lagged partner.

Entire connected sets of birds are held out. Focus is 1-second horizontal turning,
NOT vertical social Boids force or proof of causal social influence.
"""
from __future__ import annotations
import argparse,io,json,math,statistics
from collections import defaultdict,Counter
from pathlib import Path
from urllib.request import urlopen,Request
from zipfile import ZipFile
import numpy as np
from pigeon_timing_gate import (SOURCE_URL,verify,group_archive,parse_csv,pair_match,
                                MAX_TIME_MISMATCH_S)

DT_LO=0.8
DT_HI=1.2
MIN_SPEED_M_S=4.0
STALE_PARTNER_FIXES=10
MIN_SOURCE_MATCHED_FIXES=30
MIN_PREDICTIVE_STEPS=20
MIN_INDEPENDENT_COMPONENTS=5
MAX_EXAMPLES_PER_ROLE_FLIGHT=500
ALPHA=30.0
BOOTSTRAP_B=10000
BOOTSTRAP_SEED=20261026


def signed_angle(a,b):
    cross=a[0]*b[1]-a[1]*b[0]
    dot=a[0]*b[0]+a[1]*b[1]
    return math.atan2(cross,dot)

def rel_features(own_position,other_position,own_velocity,other_velocity):
    speed=float(np.linalg.norm(own_velocity))
    forward=own_velocity/speed
    side=np.array([-forward[1],forward[0]])
    rel=other_position-own_position
    delta_v=other_velocity-own_velocity
    d=max(1.,float(np.linalg.norm(rel)))
    # Each column gets its training-only RMS scaling. Kernel choices frozen.
    return np.array([float(rel@forward)/50.,float(rel@side)/50.,
       float(rel@forward)*2500/(d+5)**3,float(rel@side)*2500/(d+5)**3,
       float(delta_v@forward)/10.,float(delta_v@side)/10.],dtype=float)

def extract_rows(matched):
    """Two target bird roles, same matched real/stale partner. No future partner info."""
    if len(matched)<MIN_SOURCE_MATCHED_FIXES:return None
    ts=np.array([0.5*(a[0]+b[0]) for a,b in matched],dtype=float)
    coords=np.asarray([[[a[1],a[2]],[b[1],b[2]]] for a,b in matched],dtype=float)
    latitude0=float(np.mean(coords[0,:,0]))
    longitude0=float(np.mean(coords[0,:,1]))
    xy=np.empty((len(matched),2,2),float)
    xy[:,:,0]=(coords[:,:,1]-longitude0)*111320*math.cos(math.radians(latitude0))
    xy[:,:,1]=(coords[:,:,0]-latitude0)*111320
    dt=np.diff(ts)
    vel=np.diff(xy,axis=0)/dt[:,None,None]
    own=[];real=[];stale=[];target=[];role=[]
    for k in range(max(3,STALE_PARTNER_FIXES+1),len(ts)-1):
        if not (np.all((dt[k-3:k+1]>=DT_LO)&(dt[k-3:k+1]<=DT_HI)) and DT_LO<=dt[k-STALE_PARTNER_FIXES-1]<=DT_HI
                and 8.0<=ts[k]-ts[k-STALE_PARTNER_FIXES]<=12.0):continue
        for id in (0,1):
            other=1-id
            v_prev=vel[k-2,id];v_now=vel[k-1,id];v_next=vel[k,id]
            v_partner_now=vel[k-1,other]
            v_partner_stale=vel[k-STALE_PARTNER_FIXES-1,other]
            if min(np.linalg.norm(v_prev),np.linalg.norm(v_now),
                   np.linalg.norm(v_partner_now),np.linalg.norm(v_partner_stale))<MIN_SPEED_M_S:continue
            heading=v_now/np.linalg.norm(v_now)
            # Position at t is observable; route start is the first observed own point.
            curr_xy=xy[k,id];init_xy=xy[0,id]
            self_vec=np.array([1.,signed_angle(v_prev,v_now),
                 np.log(max(1.,float(np.linalg.norm(v_now)))/12.),
                 heading[0],heading[1],(curr_xy[0]-init_xy[0])/1000.,
                 (curr_xy[1]-init_xy[1])/1000.,(ts[k]-ts[0])/600.],float)
            f_real=rel_features(xy[k,id],xy[k,other],v_now,v_partner_now)
            f_stale=rel_features(xy[k,id],xy[k-STALE_PARTNER_FIXES,other],v_now,v_partner_stale)
            own.append(self_vec);real.append(np.r_[self_vec,f_real]);stale.append(np.r_[self_vec,f_stale]);
            target.append(signed_angle(v_now,v_next));role.append(id)
    if len(target)<2*MIN_PREDICTIVE_STEPS:return None
    out={k:np.asarray(v,float) for k,v in {'own':own,'real':real,'stale':stale,'y':target}.items()}
    out['n_position_matches']=len(matched)
    out['two_roles']=(len(set(role))==2)
    if not out['two_roles']:return None
    # Equalize observation count of individual flights via deterministic thinning.
    mask=[]
    for id in (0,1):
        ix=np.flatnonzero(np.array(role)==id)
        if len(ix)>MAX_EXAMPLES_PER_ROLE_FLIGHT:
            ix=ix[np.unique(np.linspace(0,len(ix)-1,MAX_EXAMPLES_PER_ROLE_FLIGHT,dtype=int))]
        mask.extend(ix.tolist())
    mask=np.array(sorted(mask),dtype=int)
    return {k:(v[mask] if isinstance(v,np.ndarray) else v) for k,v in out.items()}

def components_of_birds(flights):
    graph=defaultdict(set)
    for x in flights:
        a,b=x['birds'];graph[a].add(b);graph[b].add(a)
    visited=set();group={}
    for bird in sorted(graph):
        if bird in visited:continue
        todo=[bird];members=[]
        while todo:
            x=todo.pop()
            if x in visited:continue
            visited.add(x);members.append(x);todo+=list(graph[x]-visited)
        name=';'.join(sorted(members))
        for j in members:group[j]=name
    return group

def fit_ridge(X,y,alpha=ALPHA):
    X=np.asarray(X,dtype=float);y=np.asarray(y,dtype=float)
    mu=X[:,1:].mean(axis=0);sd=X[:,1:].std(axis=0)
    sd=np.maximum(sd,1e-4)
    zs=np.column_stack((np.ones(len(X)),(X[:,1:]-mu)/sd))
    gram=zs.T@zs
    ridge=np.diag([0.]+[alpha]*(zs.shape[1]-1))
    beta=np.linalg.solve(gram+ridge,zs.T@y)
    return {'mu':mu,'sd':sd,'coef':beta}

def predict(fit,X):
    z=np.column_stack((np.ones(len(X)),(X[:,1:]-fit['mu'])/fit['sd']))
    return z@fit['coef']

def frozen_score(flights,seed=BOOTSTRAP_SEED):
    if not flights:raise ValueError('STOP_NO_PREDICTIVE_FLIGHTS')
    groups=components_of_birds(flights)
    for v in flights:v['group']=groups[v['birds'][0]]
    names=sorted(set(v['group'] for v in flights))
    if len(names)<MIN_INDEPENDENT_COMPONENTS:
        return {'status':'STOP_TOO_FEW_INDEPENDENT_BIRD_COMPONENTS','n_groups':len(names)}
    per_flight=[];per_group=[]
    for held in names:
        train=[f for f in flights if f['group']!=held]
        test=[f for f in flights if f['group']==held]
        Xtrain={m:np.concatenate([f['rows'][m] for f in train]) for m in ('own','real','stale')}
        ytrain=np.concatenate([f['rows']['y'] for f in train])
        fits={m:fit_ridge(Xtrain[m],ytrain) for m in ('own','real','stale')}
        # Structural identifiability diagnostic for two lateral neighbor kernels,
        # not an estimate of physical attraction or repulsion coefficients.
        kernels=Xtrain['real'][:,[9,11]]
        centered=kernels-kernels.mean(axis=0)
        rms=np.sqrt(np.mean(centered**2,axis=0))
        scaled=centered/np.maximum(rms,1e-12)
        sv=np.linalg.svd(scaled,compute_uv=False)
        kernel_condition=float(sv[0]/sv[-1]) if sv[-1]>1e-12 else None
        group_rows=[]
        for f in test:
            y=f['rows']['y'];mses={m:float(np.mean((predict(fits[m],f['rows'][m])-y)**2)) for m in fits}
            per_flight.append({'site':f['site'],'dyad':f['dyad'],'flight_release':f['release'],
                        'n_rows':len(y),'component':held,'mse':mses})
            group_rows.append(mses)
        mean={m:float(np.mean([v[m] for v in group_rows])) for m in fits}
        per_group.append({'component':held,'n_flights':len(test),
            'two_lateral_neighbor_kernels_training_condition':kernel_condition,'mse':mean,
            'actual_vs_own':mean['own']-mean['real'],'stale_vs_own':mean['own']-mean['stale'],
            'actual_vs_stale':mean['stale']-mean['real']})
    contrasts=['actual_vs_own','stale_vs_own','actual_vs_stale']
    X=np.array([[r[k] for k in contrasts] for r in per_group])
    rng=np.random.default_rng(seed)
    pick=rng.integers(0,len(X),size=(BOOTSTRAP_B,len(X)))
    boot=X[pick].mean(axis=1)
    primary=X[:,2];n_pos=int((primary>0).sum())
    # Exact one-sided sign test P(K>=n_pos | .5), independent connected groups.
    p=sum(math.comb(len(primary),i) for i in range(n_pos,len(primary)+1))/2**len(primary)
    return {'status':'EXPLORATORY_PIGEON_PAIRED_FORECAST_V8','n_bird_components':len(names),
       'n_paired_flights':len(per_flight),'per_component':per_group,'per_flight':per_flight,
       'equal_independent_bird_component_mse':{m:float(np.mean([r['mse'][m] for r in per_group])) for m in ('own','real','stale')},
       'equal_component_gain':{k:float(np.mean(X[:,i])) for i,k in enumerate(contrasts)},
       'cluster_bootstrap95':{k:[float(np.quantile(boot[:,i],.025)),float(np.quantile(boot[:,i],.975))] for i,k in enumerate(contrasts)},
       'actual_better_than_stale_groups':n_pos,'exact_one_sided_sign_p':p,
       'source_gate':'Source checksum matches Zenodo 5010830; only already-qualified v8 source flights considered',
       'claim_limit':'Predictive contrast only. No causal social force identification, no species niche or 3D distribution forecast. Lat/long position error unknown.'}

def evaluate_public_source(data,gate_only=False):
    integrity=verify(data)
    with ZipFile(io.BytesIO(data)) as arc:
        pairs=group_archive(arc)
        candidate=[];exclusions=Counter()
        for key,files in sorted(pairs.items()):
            bird1,bird2=key[1:3]
            a,ma=parse_csv(arc,files[bird1]);b,mb=parse_csv(arc,files[bird2]);matched=pair_match(a,b)
            if (len(matched)<MIN_SOURCE_MATCHED_FIXES or
                    (matched and matched[-1][0][0]-matched[0][0][0]<5)):
                exclusions['insufficient_time_support']+=1;continue
            rows=extract_rows(matched)
            if rows is None:
                exclusions['insufficient_motion_support']+=1;continue
            candidate.append({'site':key[0],'birds':(bird1,bird2),
                              'dyad':bird1+'-'+bird2,'release':key[3],'rows':rows})
    result=frozen_score(candidate)
    result.update({'source_sha256':integrity['sha256'],'structure':{'filename_matched_pair_episodes':len(pairs),
                'eligible_motion_flights':len(candidate),'motion_exclusions':dict(exclusions)},
                'fixed_parameters':{'DT_LO':DT_LO,'DT_HI':DT_HI,'MIN_SPEED_M_S':MIN_SPEED_M_S,
                'STALE_PARTNER_FIXES':STALE_PARTNER_FIXES,'ALPHA':ALPHA,'MIN_PREDICTIVE_STEPS':MIN_PREDICTIVE_STEPS,
                'MAX_EXAMPLES_PER_ROLE_FLIGHT':MAX_EXAMPLES_PER_ROLE_FLIGHT,'independence':'bird connected components across sites'}})
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--out',type=Path,default=Path('validation_v8/results/pigeon_social_forecast_v8.json'));a=p.parse_args()
    data=a.source.read_bytes() if a.source else urlopen(Request(SOURCE_URL,headers={'User-Agent':'boids-v8-frozen-social-forecast/1.0'}),timeout=180).read()
    result=evaluate_public_source(data)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('per_flight','per_component')},indent=2))
    return 0 if result['status'].startswith('EXPLORATORY_') else 3
if __name__=='__main__':raise SystemExit(main())
