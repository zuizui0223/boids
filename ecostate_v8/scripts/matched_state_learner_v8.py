"""Original-choice model *only after* a source-hash/schema gate admits its input.

Independent animal holdouts, matched step strata, prospective M0 vs M1 comparison.
This module contains no original observations and no observed biological effects.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
from typing import Sequence
import numpy as np
from scipy.optimize import minimize

ALPHA = 0.02
FOLDS = 5
BOOTSTRAPS = 10000
SEED = 20261116
MIN_BIRDS = 20
MIN_STEPS_PER_BIRD = 30
MIN_TOTAL_STEPS = 2000
MIN_ALTERNATIVES = 2

@dataclass(frozen=True)
class StepSet:
    animal: str
    step: str
    origin: str
    destinations: tuple[str, ...]
    lengths: tuple[float, ...]
    turns: tuple[float, ...]
    chosen: int


def parse_case(x):
    if x is True or str(x).strip().lower() in ('true','t','1'):
        return True
    if x is False or str(x).strip().lower() in ('false','f','0'):
        return False
    raise ValueError('SOURCE_SCHEMA_STOP case_ not exact boolean')


def from_source_rows(rows: Sequence[dict]):
    """Fail closed on all group inconsistencies, never infer an origin from row order.

    Adapter is for a source-verified, source-defined flattened iSSA table with:
      id, burst_, step_id_, t1_, t2_, case_, landUse_start, landUse_end,
      sl_, cos_ta_. Do not use unverified raw spatial joins.
    """
    groups = defaultdict(list)
    for r in rows:
        required = ('id','burst_','step_id_','t1_','t2_','case_',
                    'landUse_start','landUse_end','sl_','cos_ta_')
        if any(k not in r for k in required):
            raise ValueError('SOURCE_SCHEMA_STOP absent original fields')
        animal=str(r['id']).strip()
        if not animal:raise ValueError('SOURCE_SCHEMA_STOP empty animal ID')
        key=(animal,str(r['burst_']),str(r['step_id_']),str(r['t1_']),str(r['t2_']))
        groups[key].append(r)
    out=[]
    for key,rs in sorted(groups.items()):
        used=[i for i,r in enumerate(rs) if parse_case(r['case_'])]
        if len(used)!=1 or len(rs)<MIN_ALTERNATIVES+1:
            raise ValueError('SOURCE_SCHEMA_STOP incomplete used/available choice set')
        origin={str(r['landUse_start']).strip() for r in rs}
        if len(origin)!=1 or not next(iter(origin)):
            raise ValueError('SOURCE_SCHEMA_STOP candidate origins not identical')
        dest=tuple(str(r['landUse_end']).strip() for r in rs)
        if not all(dest):raise ValueError('SOURCE_SCHEMA_STOP blank endpoint class')
        sl=np.array([float(r['sl_']) for r in rs],float)
        turn=np.array([float(r['cos_ta_']) for r in rs],float)
        if (not np.all(np.isfinite(sl)) or not np.all(np.isfinite(turn)) or
            np.any(sl<=0) or np.any(np.abs(turn)>1+1e-6)):
            raise ValueError('SOURCE_SCHEMA_STOP invalid movement covariate')
        step='|'.join(key[1:])
        out.append(StepSet(key[0],step,next(iter(origin)),dest,
                           tuple(np.log(sl)),tuple(turn),used[0]))
    return out


def validate(steps: Sequence[StepSet],classes: Sequence[str],strict=True):
    if len(classes)<3 or len(set(classes))!=len(classes):
        raise ValueError('SOURCE_SCHEMA_STOP invalid exclusive category roster')
    cats=set(classes); seen=set(); counts=Counter()
    for s in steps:
        k=(s.animal,s.step)
        if k in seen:raise ValueError('SOURCE_SCHEMA_STOP duplicate group key')
        seen.add(k);counts[s.animal]+=1
        n=len(s.destinations)
        if n<MIN_ALTERNATIVES+1 or len(s.lengths)!=n or len(s.turns)!=n or not 0<=s.chosen<n:
            raise ValueError('SOURCE_SCHEMA_STOP invalid choice-set dimensions')
        if s.origin not in cats or any(t not in cats for t in s.destinations):
            raise ValueError('SOURCE_SCHEMA_STOP unknown or overlapping land-use class')
        if not np.all(np.isfinite(s.lengths)) or not np.all(np.isfinite(s.turns)):
            raise ValueError('SOURCE_SCHEMA_STOP nonfinite movement model feature')
    if strict:
        if sum(v>=MIN_STEPS_PER_BIRD for v in counts.values())<MIN_BIRDS:
            raise ValueError('SCIENTIFIC_STOP too few independent animals')
        if sum(v for v in counts.values() if v>=MIN_STEPS_PER_BIRD)<MIN_TOTAL_STEPS:
            raise ValueError('SCIENTIFIC_STOP too few independent matched steps')
    return counts


def fold(animal):
    return int(hashlib.sha256(str(animal).encode('utf8')).hexdigest()[:8],16)%FOLDS


def transform(steps, classes, include_origin, means, sds):
    """Features known before choosing; destination one-hot plus movement kernel.

    The first source class is the omitted reference, to avoid arbitrary intercept.
    Only training candidates are used for movement scaling moments.
    """
    p=(len(classes)-1)+2+int(include_origin)
    mapcat={k:i for i,k in enumerate(classes)}
    sizes=np.fromiter((len(s.destinations) for s in steps),int,count=len(steps))
    starts=np.r_[0,np.cumsum(sizes)[:-1]]
    n=int(sizes.sum())
    X=np.zeros((n,p),float)
    chosen=np.empty(len(steps),int)
    position=len(classes)-1
    for si,s in enumerate(steps):
        start=int(starts[si]);chosen[si]=start+s.chosen
        for j,d in enumerate(s.destinations):
            z=X[start+j];k=mapcat[d]
            if k: z[k-1]=1.0
            z[position]=(s.lengths[j]-means[0])/sds[0]
            z[position+1]=(s.turns[j]-means[1])/sds[1]
            if include_origin:z[-1]=float(s.origin==d)
    return X, starts, sizes, chosen


def movement_moments(steps):
    a=np.array([[v,w] for s in steps for v,w in zip(s.lengths,s.turns)],float)
    means=a.mean(axis=0);sds=a.std(axis=0)
    sds=np.maximum(sds,1e-8)
    return means,sds


def conditional_losses(beta,X,starts,sizes,chosen):
    score=X@beta
    mx=np.maximum.reduceat(score,starts)
    exp=np.exp(score-np.repeat(mx,sizes))
    denom=np.add.reduceat(exp,starts)
    return mx+np.log(denom)-score[chosen]


def fit(train,classes,include_origin,means,sds):
    X,starts,sizes,chosen=transform(train,classes,include_origin,means,sds)
    birds=Counter(s.animal for s in train)
    weights=np.array([1.0/(len(birds)*birds[s.animal]) for s in train])
    p=X.shape[1]
    def obj(beta):
        score=X@beta
        mx=np.maximum.reduceat(score,starts)
        expo=np.exp(score-np.repeat(mx,sizes))
        den=np.add.reduceat(expo,starts)
        loss=mx+np.log(den)-score[chosen]
        prob=expo/np.repeat(den,sizes)
        y=np.zeros_like(prob);y[chosen]=1
        delta=(prob-y)*np.repeat(weights,sizes)
        grad=X.T@delta+ALPHA*beta
        val=np.dot(weights,loss)+ALPHA*0.5*np.dot(beta,beta)
        return val,grad
    result=minimize(obj,np.zeros(p),method='L-BFGS-B',jac=True,
                    options={'maxiter':180,'ftol':1e-10})
    if not result.success and np.linalg.norm(result.jac)>1e-4:
        raise ValueError('ESTIMATOR_STOP optimizer did not converge')
    return result.x


def evaluate(steps: Sequence[StepSet],classes: Sequence[str],bootstrap=BOOTSTRAPS,strict=True):
    counts=validate(steps,classes,strict=strict)
    kept=set(i for i,n in counts.items() if n>=MIN_STEPS_PER_BIRD) if strict else set(counts)
    eligible=[s for s in steps if s.animal in kept]
    birds=sorted(kept)
    fids={b:fold(b) for b in birds}
    gains={}
    per_fold=[]
    for fd in range(FOLDS):
        train=[s for s in eligible if fids[s.animal]!=fd]
        test=[s for s in eligible if fids[s.animal]==fd]
        if not train or not test:
            raise ValueError('SCIENTIFIC_STOP empty leave-animal-out validation fold')
        moments=movement_moments(train)
        b0=fit(train,classes,False,*moments)
        b1=fit(train,classes,True,*moments)
        x0,st,sz,ch=transform(test,classes,False,*moments)
        x1,_,_,_=transform(test,classes,True,*moments)
        l0=conditional_losses(b0,x0,st,sz,ch)
        l1=conditional_losses(b1,x1,st,sz,ch)
        for bird in sorted(set(s.animal for s in test)):
            inds=[i for i,s in enumerate(test) if s.animal==bird]
            gains[bird]=float(np.mean(l0[inds]-l1[inds]))
        per_fold.append({'fold':fd,'test_birds':len(set(s.animal for s in test)),
                         'test_steps':len(test)})
    values=np.array([gains[b] for b in birds],float)
    rng=np.random.default_rng(SEED)
    boot=np.mean(rng.choice(values,size=(bootstrap,len(birds)),replace=True),axis=1)
    lo,hi=np.quantile(boot,[.025,.975])
    npos=int((values>0).sum())
    return {'schema':'ecostate.v8.matched_destination_origin_state',
            'model_classes':[str(x) for x in classes],
            'reference_class':classes[0],
            'number_of_animals':len(birds),
            'number_of_groups':len(eligible),
            'mean_equal_bird_logscore_gain_nats':float(values.mean()),
            'interval_95_bird_bootstrap':[float(lo),float(hi)],
            'positive_birds':npos,
            'gate':'PASS' if lo>0 and npos>=0.6*len(birds) else 'FAIL',
            'per_bird_gains':gains,'folds':per_fold,
            'claim_boundary':('Biological association of origin class beyond static destination '+
                              'preference and observed movement-kernel features in source-matched '+
                              'choices, not memory, proof of movement optimality, or full reachable-state census.')}
