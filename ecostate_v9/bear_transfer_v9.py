#!/usr/bin/env python3
"""Original public polar-bear matched-choice, whole-bear heldout energetic vs habitat model.

Pre-registered after viewing only archive member names and CSV headers, BEFORE
opening the original habitat, energetic or used-choice numeric values.
Not a test of origin-state retention (no source start-state covariate).
"""
from __future__ import annotations
import csv,hashlib,io,json,math,sys,urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp

RECORD='https://zenodo.org/api/records/6319709'
ORIGINAL='data/model_comparison_data.csv'
MD5='20bcf2babfc97c088f9b5948db23b5f1'
SHA256='943254e09a6043da98545832b0f2dab4f15130a71e91fe2445ef424f8fe6de7e'
NROWS=174804
NUM=['obs','GPS_step','bear_step','angle','gain','cost','ice','drift','depth']
KEYS=['bearID','trackID','stratum']
MIN_BEAR=15; MIN_EVENTS=50; MIN_CAND=5
L2=0.02
SEED=20261116
BOOT=10000
FEATURES={
 'movement':['log_gps','log_bear','cos_angle'],
 'environment':['log_gps','log_bear','cos_angle','ice','ice2','drift','depth'],
 'energetics':['log_gps','log_bear','cos_angle','gain','cost'],
 'combined':['log_gps','log_bear','cos_angle','ice','ice2','drift','depth','gain','cost']}

def original_archive():
    with urllib.request.urlopen(urllib.request.Request(RECORD,headers={'User-Agent':'ecostate-v9-animal-transfer/1.0'}),timeout=90) as r:
        metadata=json.loads(r.read())
    f=[x for x in metadata.get('files',[]) if x.get('key')=='ESF_Rcodes.zip']
    if len(f)!=1 or f[0].get('checksum')!='md5:'+MD5:raise ValueError('SOURCE_STOP_ORIGINAL_FILE_ANNOUNCED_DIGEST')
    url=f[0].get('links',{}).get('self') or f[0].get('links',{}).get('content')
    if not url or not url.startswith('https://zenodo.org/'):raise ValueError('SOURCE_STOP_NOT_OFFICIAL_URI')
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ecostate-v9-animal-transfer/1.0'}),timeout=120) as r:
        b=r.read(25_000_001)
    if len(b)>25_000_000 or hashlib.md5(b).hexdigest()!=MD5 or hashlib.sha256(b).hexdigest()!=SHA256:
        raise ValueError('SOURCE_STOP_ORIGINAL_BYTES_DIFFER')
    return b

def open_source(b):
    import zipfile
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        df=pd.read_csv(z.open(ORIGINAL),low_memory=False,dtype={k:'string' for k in KEYS})
    if len(df)!=NROWS or any(x not in df.columns for x in KEYS+NUM):
        raise ValueError('SOURCE_SCHEMA_STOP_SOURCE_DOMAIN')
    # Original observed field is explicit, not a proxy inferred from counts or row ordering.
    obs=df['obs'].astype('string').str.lower().str.strip().map({'1':1,'0':0,'true':1,'false':0,'t':1,'f':0})
    if obs.isna().any():raise ValueError('SOURCE_SCHEMA_STOP_UNKNOWN_OBS_FLAG')
    df['obs']=obs.to_numpy(dtype=int)
    for name in NUM[1:]:df[name]=pd.to_numeric(df[name],errors='coerce')
    qc={'raw_rows':int(len(df)),'raw_bear_ids':int(df['bearID'].nunique()),'raw_groups':int(df.groupby(KEYS,dropna=True).ngroups)}
    # Common data support across all four models. Entire strata excluded on any missing candidate.
    source_group=df.groupby(KEYS,sort=False,dropna=False)
    def valid_stratum(g):
        if g[KEYS].isna().any().any():return False
        if len(g)<MIN_CAND or g['obs'].sum()!=1:return False
        if not np.isfinite(g[NUM[1:]].to_numpy(dtype=float)).all():return False
        if (g['GPS_step']<0).any() or (g['bear_step']<0).any():return False
        if (g['ice']<0).any() or (g['ice']>1.000001).any():return False
        if (g['angle'].abs()>math.pi*2+0.00001).any():return False
        return True
    # Efficient vectorized stratum gates avoid a python per-stratum loop.
    validrow=np.isfinite(df[NUM[1:]].to_numpy(dtype=float)).all(axis=1)
    validrow&=(df['GPS_step'].to_numpy(dtype=float)>=0)&(df['bear_step'].to_numpy(dtype=float)>=0)
    validrow&=df['ice'].between(0,1.000001).to_numpy(dtype=bool)
    validrow&=(np.abs(df['angle'].to_numpy(dtype=float))<=math.pi*2+0.00001)
    validrow&=df[KEYS].notna().all(axis=1).to_numpy()
    df['_goodrow']=validrow
    agg=df.groupby(KEYS,dropna=False,sort=False).agg(n=('obs','size'),cases=('obs','sum'),allgood=('_goodrow','all'))
    eligible=agg[(agg.n>=MIN_CAND)&(agg.cases==1)&agg.allgood].reset_index()[KEYS]
    df=df.merge(eligible,on=KEYS,how='inner',validate='many_to_one').drop(columns='_goodrow')
    validcounts=df.groupby(KEYS,dropna=False).size().reset_index(name='n').groupby('bearID').size()
    selected=validcounts[validcounts>=MIN_EVENTS].index
    df=df[df.bearID.isin(selected)].copy()
    qc.update({'eligible_rows':int(len(df)),'eligible_groups':int(df.groupby(KEYS).ngroups),'eligible_bears':int(len(selected)),
               'source_eligible_loss_rows':int(NROWS-len(df)),'min_events_per_bear':int(validcounts.loc[selected].min()) if len(selected)>0 else 0})
    if qc['eligible_bears']<MIN_BEAR or qc['eligible_groups']<1000:raise ValueError('SOURCE_SCHEMA_STOP_INDEPENDENT_BEAR_SUPPORT '+str(qc))
    return df,qc

def prepare(df):
    df=df.sort_values(KEYS,kind='stable').reset_index(drop=True)
    grp=df.groupby(KEYS,sort=False).agg(n=('obs','size'),cases=('obs','sum')).reset_index()
    if (grp.cases!=1).any():raise ValueError('INTERNAL_INVALID_GROUP')
    sizes=grp.n.to_numpy(dtype=int)
    starts=np.r_[0,np.cumsum(sizes)[:-1]]
    used=starts+np.flatnonzero(df.obs.to_numpy().reshape(-1)==1)[0] if False else np.array([
        i + np.flatnonzero(df.obs.to_numpy()[i:i+n])[0] for i,n in zip(starts,sizes)],dtype=int)
    X=pd.DataFrame({
       'log_gps':np.log1p(df['GPS_step'].to_numpy(dtype=float)),
       'log_bear':np.log1p(df['bear_step'].to_numpy(dtype=float)),
       'cos_angle':np.cos(df['angle'].to_numpy(dtype=float)),
       'ice':df['ice'].to_numpy(dtype=float),
       'ice2':df['ice'].to_numpy(dtype=float)**2,
       'drift':df['drift'].to_numpy(dtype=float),
       'depth':df['depth'].to_numpy(dtype=float),
       'gain':df['gain'].to_numpy(dtype=float),
       'cost':df['cost'].to_numpy(dtype=float)})
    group_bear=grp.bearID.to_numpy(dtype=str)
    return X,grp,sizes,starts,used,group_bear

def matrices(X,cols,train_rows):
    a=X[cols].to_numpy(dtype=float)
    mean=a[train_rows].mean(axis=0)
    std=a[train_rows].std(axis=0)
    std[std<1e-7]=1.0
    return np.clip((a-mean)/std,-9,9)

def conditional_nll(theta, x, sizes, starts, used, weights, alpha=L2,deriv=False):
    eta=x@theta
    m=np.maximum.reduceat(eta,starts)
    shifted=eta-np.repeat(m,sizes)
    exp=np.exp(shifted)
    sums=np.add.reduceat(exp,starts)
    nll=(m+np.log(sums))-eta[used]
    loss=float(np.dot(weights,nll)+alpha*np.dot(theta,theta)/2)
    if not deriv:return loss
    per_row=np.repeat(weights/sums,sizes)*exp
    grad=(x.T@per_row)-(x[used].T@weights)+alpha*theta
    return loss,grad

def evaluate(df, boot=BOOT):
    X,grp,sizes,starts,used,bears=prepare(df)
    unique=sorted(set(bears))
    if len(unique)<MIN_BEAR:raise ValueError('insufficient independent animals')
    # Precommitted deterministic source-ID fold assignment, not random rows.
    fold={b:int(hashlib.sha256(b.encode()).hexdigest(),16)%5 for b in unique}
    if min(sum(fold[b]==k for b in unique) for k in range(5))<2:
        raise ValueError('SOURCE_SCHEMA_STOP_TOO_FEW_ANIMALS_PER_FOLD')
    scores={b:{k:[] for k in FEATURES} for b in unique}
    for k in range(5):
        train_g=np.flatnonzero(np.array([fold[b]!=k for b in bears]))
        test_g=np.flatnonzero(np.array([fold[b]==k for b in bears]))
        def sliced(gg):
            inds=np.concatenate([np.arange(starts[i],starts[i]+sizes[i]) for i in gg]);cnt=sizes[gg]
            st=np.r_[0,np.cumsum(cnt)[:-1]]
            cases=np.array([np.flatnonzero(df['obs'].to_numpy()[starts[i]:starts[i]+sizes[i]])[0]+st[j] for j,i in enumerate(gg)])
            return inds,cnt,st,cases
        tr_i,tr_n,tr_st,tr_used=sliced(train_g)
        te_i,te_n,te_st,te_used=sliced(test_g)
        tr_b=bears[train_g];te_b=bears[test_g]
        train_rows=np.repeat(False,len(df));train_rows[tr_i]=True
        cntbear={b:int((tr_b==b).sum()) for b in set(tr_b)}
        w=np.array([1.0/(len(cntbear)*cntbear[b]) for b in tr_b])
        for name,cols in FEATURES.items():
            xf=matrices(X,cols,train_rows)
            train=xf[tr_i];test=xf[te_i]
            f=lambda coef:conditional_nll(coef,train,tr_n,tr_st,tr_used,w,deriv=True)
            fit=minimize(f,np.zeros(len(cols)),method='L-BFGS-B',jac=True,
                         options={'maxiter':140,'ftol':1e-9,'gtol':1e-7})
            if not fit.success and np.linalg.norm(fit.jac)>0.0003:
                raise ValueError('FITTING_STOP_NONCONVERGENCE '+name+str(k)+' '+fit.message)
            eta=test@fit.x
            m=np.maximum.reduceat(eta,te_st)
            ll=(m+np.log(np.add.reduceat(np.exp(eta-np.repeat(m,te_n)),te_st)))-eta[te_used]
            for b in set(te_b):
                scores[b][name].extend(ll[te_b==b].tolist())
    result={}
    for b in unique:
        result[b]={name:float(np.mean(values)) for name,values in scores[b].items()}
        result[b]['n_groups']=int(len(scores[b]['environment']))
        if result[b]['n_groups']<MIN_EVENTS:raise ValueError('score missing bear '+b)
    names={'environment_over_movement':('movement','environment'),
           'energy_over_environment':('environment','energetics'),
           'combined_over_environment':('environment','combined'),
           'combined_over_energetics':('energetics','combined')}
    rng=np.random.default_rng(SEED)
    out={'replication_unit':'bearID','bootstrap_resamples':boot,'model_features':FEATURES,
         'n_bears':len(unique),'n_strata':int(sum(x['n_groups'] for x in result.values())),
         'fold_ids':{k:sum(fold[b]==k for b in unique) for k in range(5)},
         'average_logloss_nats':{k:float(np.mean([r[k] for r in result.values()])) for k in FEATURES},
         'contrasts':{}}
    for label,(a,b) in names.items():
        values=np.array([result[x][a]-result[x][b] for x in unique])
        vals=rng.choice(values,(boot,len(values)),replace=True).mean(axis=1)
        ci=np.quantile(vals,[.025,.975]);out['contrasts'][label]={
            'gain_nats_per_step':float(values.mean()),'group_bootstrap_95':ci.tolist(),
            'positive_bears':int((values>0).sum()),'negative_bears':int((values<0).sum()),
            'median_bear_gain':float(np.median(values)),
            'fixed_direction_gate':'PASS' if ci[0]>0 and (values>0).sum()>=math.ceil(len(values)*.65) else 'FAIL'}
    # No re-identifiable original tags published; anonymized labels are stable only in result receipt.
    out['per_bear']=[{'label':'B'+format(i+1,'02'),
                       'n_events':result[b]['n_groups'],
                       'energy_over_env':result[b]['environment']-result[b]['energetics'],
                       'env_over_move':result[b]['movement']-result[b]['environment']}
                     for i,b in enumerate(unique)]
    return out

def main(output):
    target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
    result={'schema':'ecostate.v9.polarbear_original_group_transfer_v1','source_doi':'10.5281/zenodo.6319709',
            'source_original_sha256':SHA256,'status':'SOURCE_STOP','primary_gate':'NOT_EVALUATED',
            'model_training_target':'whole-bear heldout matched-choice probabilistic logloss',
            'claim_limits':['Does not test origin-state retention, no start-state in source.',
              'Generated candidates are a source-author defined movement reference, not all physically reachable habitats.',
              '23 polar bears from one source; no cross-species universality or causal mechanism inferred.']}
    try:
        b=original_archive()
        df,qc=open_source(b)
        result['qc']=qc
        scores=evaluate(df)
        result.update({'status':'ORIGINAL_FIELD_COMPUTED','primary_gate':scores['contrasts']['energy_over_environment']['fixed_direction_gate'],'scores':scores})
    except Exception as e:
        result.update({'status':'SOURCE_OR_MODEL_STOP','reason':str(e)[:1200]})
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('V9_POLAR_BEAR_ORIGINAL',result['status'],result['primary_gate'],result.get('reason',''),result.get('scores',{}).get('contrasts',{}))
    return result
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v9/results/original_bear_transfer_v9.json')
