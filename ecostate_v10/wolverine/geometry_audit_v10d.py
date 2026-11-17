#!/usr/bin/env python3
"""POST-RESULT v10d geometry audit of v10c.

Not a change to v10c frozen test, and not proof of causal state regulation.
Original workbook downloaded with exact published checksum, never redistributed.

(A) used-versus-pseudo-used length-matched exposure continuity ranks;
(B) a new whole-animal-heldout stream-divergence baseline followed by road divergence.
"""
from __future__ import annotations
import collections, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from field_v10c import (source,build,group_admit,design,condloss,FEATURES,L2,SEED,MIN_STEPS)

BOOT=10000
MATCH_LOW=0.8
MATCH_HIGH=1.2
MIN_OPTIONS=2

def length_matched_rank(d,groups):
    allvals={}
    for key in ('road','traffic','stream'):
        allvals[key]=np.abs(np.log1p(d[key+'_end'])-np.log1p(d[key+'_start']))
    accum=collections.defaultdict(lambda:collections.defaultdict(list))
    eligible_count=collections.Counter()
    road_ineq_count=collections.Counter()
    for (sheet,animal,stratum),idx in groups:
        idx=np.asarray(idx,dtype=int)
        lens=d['sl'][idx]
        start_road=d['road_start'][idx];end_road=d['road_end'][idx]
        # Diagnostic geometric sanity check only, not evidence of behavioral selection.
        road_ineq_count['rows']+=len(idx)
        road_ineq_count['road_diff_gt_step']+=int(np.sum(np.abs(end_road-start_road)>lens+1e-5))
        mat=(lens[None,:]>=MATCH_LOW*lens[:,None]) & (lens[None,:]<=MATCH_HIGH*lens[:,None])
        np.fill_diagonal(mat,False)
        counts=mat.sum(axis=1)
        valid=counts>=MIN_OPTIONS
        used=np.flatnonzero(d['used'][idx]==1)
        if len(used)!=1:raise ValueError('SOURCE_SCHEMA_STOP_INVALID_USED_AFTER_ADMISSION')
        u=int(used[0]);eligible_count['total_groups']+=1
        if not valid[u]:continue
        if valid.sum()<3:continue
        eligible_count['matched_groups']+=1
        for key,v in allvals.items():
            x=v[idx]
            # rank of each hypothetical pseudo-used candidate relative to its
            # own distance-matched alternatives (exact within-step null).
            comp=(x[None,:]>x[:,None])+.5*(x[None,:]==x[:,None])
            score=np.sum(comp*mat,axis=1)/np.maximum(counts,1)
            null=float(np.mean(score[valid]))
            obs=float(score[u])
            accum[animal][key].append((obs,null))
    per={}
    for animal,metrics in sorted(accum.items()):
        v={}
        for key,pairs in metrics.items():
            o=np.asarray(pairs,dtype=float)
            v[key]={'used_rank':float(o[:,0].mean()),'pseudo_used_rank':float(o[:,1].mean()),
                     'calibrated_rank_excess':float((o[:,0]-o[:,1]).mean()),'n_matched_steps':len(pairs)}
        per[animal]=v
    if len(per)<10:raise ValueError('SOURCE_SCHEMA_STOP_TOO_FEW_LENGTH_MATCHED_ANIMALS')
    rng=np.random.default_rng(SEED ^ 0x01AC)
    result={}
    for key in ('road','traffic','stream'):
        vals=np.array([v[key]['calibrated_rank_excess'] for v in per.values() if key in v],dtype=float)
        if len(vals)<10:raise ValueError('SOURCE_SCHEMA_STOP_FEW_ANIMALS_'+key)
        bs=rng.choice(vals,(BOOT,len(vals)),replace=True).mean(axis=1)
        result[key]={'equal_animal_calibrated_rank_excess':float(vals.mean()),
             'animal_bootstrap95':list(map(float,np.quantile(bs,[.025,.975]))),
             'positive_animals':int(sum(vals>0)),'animals':len(vals),
             'median_rank_excess':float(np.median(vals))}
    return {'status':'POSTRESULT_MATCHED_LENGTH_DESCRIPTIVE','match_ratio':[MATCH_LOW,MATCH_HIGH],
        'source_only_alternatives':True,'min_matched_alternatives':MIN_OPTIONS,
        'counts':dict(eligible_count),'geometric_source_sanity':dict(road_ineq_count),
        'rank_excess':result,'anonymous_animal_n_matched_steps':sorted([v['road']['n_matched_steps'] for v in per.values()])}

def stream_baseline_transfer(d,groups):
    base,feature_names=design(d)
    # New null comparison: all v10c destination predictors + a non-road
    # origin-to-endpoint continuity (distance to a stream) vs + road continuity.
    v_stream=np.abs(np.log1p(d['stream_end'])-np.log1p(d['stream_start']))
    jroad=feature_names.index('road_start_end_divergence')
    x_full=np.column_stack((base[:,:len(FEATURES['destination'])],v_stream,base[:,jroad]))
    sizes=np.array([len(idx) for _,idx in groups],dtype=int)
    starts=np.r_[0,np.cumsum(sizes)[:-1]]
    rows=np.concatenate([np.asarray(idx,dtype=int) for _,idx in groups]);X=x_full[rows]
    used=np.array([int(starts[i]+np.flatnonzero(d['used'][idx]==1)[0]) for i,(_,idx) in enumerate(groups)],dtype=int)
    animals=np.array([k[1] for k,_ in groups],dtype=object)
    ids=sorted(set(animals),key=lambda t:hashlib.sha256(t.encode()).hexdigest())
    folds={a:i%5 for i,a in enumerate(ids)}
    score={a:{'stream':[],'stream_road':[]} for a in ids}
    slopes=[]
    for i in range(5):
        tr=np.flatnonzero(np.array([folds[a]!=i for a in animals]))
        te=np.flatnonzero(np.array([folds[a]==i for a in animals]))
        def index(gg):
            ii=np.concatenate([np.arange(starts[j],starts[j]+sizes[j]) for j in gg]);n=sizes[gg]
            st=np.r_[0,np.cumsum(n)[:-1]]
            chosen=used[gg]-starts[gg]+st
            return ii,n,st,chosen
        train,n,st,u=index(tr);test,en,es,eu=index(te)
        train_animals=animals[tr];eval_animals=animals[te]
        counts=collections.Counter(train_animals)
        w=np.array([1/(len(counts)*counts[a]) for a in train_animals],float)
        mean=X[train].mean(0);sd=X[train].std(0);sd[sd<1e-8]=1
        z=np.clip((X-mean)/sd,-10,10)
        for kind,p in [('stream',X.shape[1]-1),('stream_road',X.shape[1])]:
            xt=z[train,:p];xe=z[test,:p]
            opt=minimize(lambda theta:condloss(theta,xt,n,st,u,w,True),np.zeros(p),
                         jac=True,method='L-BFGS-B',options={'maxiter':180,'gtol':1e-7,'ftol':1e-9})
            if not opt.success and np.linalg.norm(opt.jac)>0.0005:
                raise ValueError('MODEL_STOP_NONCONVERGENCE_'+kind+'_'+str(i))
            q=xe@opt.x;m=np.maximum.reduceat(q,es)
            l=m+np.log(np.add.reduceat(np.exp(q-np.repeat(m,en)),es))-q[eu]
            for a in set(eval_animals):score[a][kind].extend(l[eval_animals==a].tolist())
            if kind=='stream_road':slopes.append(float(opt.x[-1]))
    vals=np.array([np.mean(score[a]['stream'])-np.mean(score[a]['stream_road']) for a in ids])
    rng=np.random.default_rng(SEED ^ 0x02BC)
    bt=rng.choice(vals,(BOOT,len(vals)),replace=True).mean(1)
    return {'status':'POSTRESULT_STREAM_AS_SPATIAL_CONTINUITY_CONTROL',
        'base_model':'M0 destination geometry and environmental covariates plus absolute start-end stream-distance difference',
        'added_model':'same model plus absolute start-end road-distance difference',
        'source_heldout_31_animal_units':len(ids),'groups':len(groups),
        'equal_animal_nats_per_movement':float(vals.mean()),
        'ci95_animal_bootstrap':list(map(float,np.quantile(bt,[.025,.975]))),
        'positive_animals':int(sum(vals>0)),
        'road_divergence_coefficient_negative_folds':int(sum(x<0 for x in slopes)),
        'anonymous_bear_gain_range':[float(vals.min()),float(vals.max())],
        'evidence_class':'postresult_exploratory_not_frozen_primary_v10c'}

def main(output):
    receipt={'schema':'ecostate.v10d.wolverine_postresult_geometry_audit',
      'evidence_class':'postresult_exploratory_audit_not_frozen_v10c',
      'original_source_sha256':'979a362af1acaff069a7c53dfabf5284eb68d0c448899858ae18be999513b1bd',
      'status':'SOURCE_OR_MODEL_STOP',
      'claim_ceiling':('Length-matched candidate references and stream continuity do not remove all geometric, '
                       'road-network or generator biases. A statistical residual is not active state buffering, '
                       'adaptation, or fitness-related regulation.')}
    try:
        t,p=source()
        try:d,qc=build(p)
        finally:t.cleanup()
        groups,qc=group_admit(d,qc)
        receipt['source_qc']=qc
        receipt['matched_length_rank']=length_matched_rank(d,groups)
        receipt['nonroad_stream_baseline']=stream_baseline_transfer(d,groups)
        receipt['status']='POSTRESULT_FIELD_DIAGNOSTIC_COMPUTED'
    except Exception as e:
        receipt['reason']=str(e)[:1500]
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('WOLVERINE_V10D',receipt['status'])
    if receipt['status']=='POSTRESULT_FIELD_DIAGNOSTIC_COMPUTED':
        print('GEOM_AUDIT',json.dumps({'ranks':receipt['matched_length_rank']['rank_excess'],
                                     'model':receipt['nonroad_stream_baseline']},separators=(',',':')))
    else:print('SOURCE_OR_MODEL_STOP',receipt.get('reason'))

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v10/results/wolverine_postresult_geometry_v10d.json')
