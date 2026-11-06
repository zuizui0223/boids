"""v54 fixed-policy, paired-identity annual diagnostic; no original data export.

All statistics reuse v52 angular losses. This is post-v53 exploratory, not a
causal decomposition or independent ecological replication.
"""
from __future__ import annotations
from collections import defaultdict
import numpy as np
from angular_phase_control import replace_phase
from bearing_decomposition import decompose_predictions

MODELS=('M0','Mactual','M365')
METRICS=('cosine_loss','absolute_angle_degrees','vector_half_MSE')
CONTRASTS={'M365_minus_Mactual':(2,1),'M0_minus_Mactual':(0,1),'M0_minus_M365':(0,2)}
SEED=20261106


def _check_rows(rows, year):
    if not rows:raise ValueError('Empty source rows')
    seen=set()
    for r in rows:
        t=r['t']
        if t.year!=year or t.tzinfo is None or t.utcoffset() is None:
            raise ValueError('Invalid chronological source year or clock')
        if not isinstance(r['id'],str) or not r['id']:raise ValueError('Missing source identity')
        key=(r['id'],t)
        if key in seen:raise ValueError('Duplicate original identity/time key')
        seen.add(key)


def _check_losses(rows, values):
    a=np.asarray(values,dtype=float)
    if a.shape!=(len(rows),3,3) or not np.isfinite(a).all():
        raise ValueError('Unaligned or nonfinite original angular losses')
    if np.any(a < -1e-12):raise ValueError('Negative prediction loss')
    return a


def loss_tensor(rows,predictions):
    """N x model(M0,actual,365) x metric(cosine,degree,vector) losses."""
    if set(predictions)!=set(MODELS):raise ValueError('Exactly three fixed models required')
    truth=np.asarray([[r['target_e'],r['target_n']] for r in rows],dtype=float)
    actual=decompose_predictions(truth,predictions['M0'],predictions['Mactual'])
    ghost=decompose_predictions(truth,predictions['M0'],predictions['M365'])
    result=np.stack([np.column_stack([x['cosine_loss'+s],x['angle_degrees'+s],x['vector_loss'+s]])
                     for x,s in ((actual,'0'),(actual,'1'),(ghost,'1'))],axis=1)
    return _check_losses(rows,result)


def forecast_policies(train2010,test2011,test2012,forecast_fn):
    """The fixed model sees only 2010; updated model never scores training 2011."""
    for rows,year in ((train2010,2010),(test2011,2011),(test2012,2012)):_check_rows(rows,year)
    def predict(train,test):
        out={'M0':forecast_fn(train,test,0),'Mactual':forecast_fn(train,test,1),
             'M365':forecast_fn(replace_phase(train),replace_phase(test),1)}
        for key,val in out.items():
            val=np.asarray(val,dtype=float)
            if val.shape!=(len(test),2) or not np.isfinite(val).all():
                raise ValueError('Unaligned source prediction')
            out[key]=val
        return out
    both=test2011+test2012
    fixed=predict(train2010,both)
    n=len(test2011)
    return {'F10':{2011:{k:v[:n] for k,v in fixed.items()},
                    2012:{k:v[n:] for k,v in fixed.items()}},
            'F1011':{2012:predict(train2010+test2011,test2012)}}


def _paired_summary(first,second,draws,seed):
    """Pair all original model errors at the SAME identity, never independently."""
    first=np.asarray(first,dtype=float);second=np.asarray(second,dtype=float)
    if first.shape!=second.shape or first.ndim!=3 or first.shape[1:]!=(3,3):
        raise ValueError('Paired identities require aligned model/metric arrays')
    if len(first)<3 or draws<1 or not np.isfinite(first).all() or not np.isfinite(second).all():
        raise ValueError('Insufficient or invalid paired identity losses')
    idx=np.random.default_rng(seed).integers(len(first),size=(draws,len(first)))
    def stat(per_identity):
        return {metric:{'mean':float(per_identity[:,j].mean()),
                        'CI95':np.quantile(per_identity[idx,j].mean(1),[.025,.975]).tolist(),
                        'positive_identities':int(np.sum(per_identity[:,j]>0))}
                for j,metric in enumerate(METRICS)}
    gains_first={name:stat(first[:,a]-first[:,b]) for name,(a,b) in CONTRASTS.items()}
    gains_second={name:stat(second[:,a]-second[:,b]) for name,(a,b) in CONTRASTS.items()}
    change={name:stat((second[:,a]-second[:,b])-(first[:,a]-first[:,b]))
            for name,(a,b) in CONTRASTS.items()}
    def means(x):
        return {model:dict(zip(METRICS,map(float,x[:,j].mean(0)))) for j,model in enumerate(MODELS)}
    return {'first_model_mean_losses':means(first),'second_model_mean_losses':means(second),
            'first_gains':gains_first,'second_gains':gains_second,
            'change_in_gain_second_minus_first':change,
            'model_loss_reduction_first_minus_second':
                {model:stat(first[:,j]-second[:,j]) for j,model in enumerate(MODELS)},
            'resampling':'paired whole original identities, all models/years together',
            'bootstrap_draws':draws,'seed':seed}


def paired_years(rows_by_year,losses_by_year,*,month_matched=False,draws=10000,seed=SEED):
    if set(rows_by_year)!={2011,2012} or set(losses_by_year)!={2011,2012}:
        raise ValueError('Exactly the two fixed evaluation years are required')
    arrays={};indices={}
    for year in (2011,2012):
        rows=rows_by_year[year];_check_rows(rows,year)
        arrays[year]=_check_losses(rows,losses_by_year[year])
        groups=defaultdict(list)
        for i,r in enumerate(rows):groups[r['id']].append(i)
        indices[year]=groups
    shared=sorted(set(indices[2011])&set(indices[2012]))
    eligible=[]
    for bird in shared:
        if all(len(indices[y][bird])>=50 and
               len({rows_by_year[y][i]['t'].isocalendar()[:2] for i in indices[y][bird]})>=4
               for y in (2011,2012)):
            eligible.append(bird)
    receipt={'n_source_identities_2011':len(indices[2011]),
             'n_source_identities_2012':len(indices[2012]),
             'n_shared_source_identifiers':len(shared),
             'n_eligible_recurrent_identities':len(eligible),
             'source_identity_basis':'exact within-study individual-local-identifier; biological identity not independently adjudicated',
             'no_original_identity_values_exported':True}
    if len(eligible)<3:
        return {'status':'NOT_ADMITTED_RECURRENT_IDENTITY_SUPPORT',**receipt}
    first=[];second=[];retained=[0,0];month_counts=[]
    for bird in eligible:
        if month_matched:
            monthly={}
            for year in (2011,2012):
                d=defaultdict(list)
                for i in indices[year][bird]:d[rows_by_year[year][i]['t'].month].append(i)
                monthly[year]=d
            months=sorted(m for m in set(monthly[2011])&set(monthly[2012])
                          if len(monthly[2011][m])>=10 and len(monthly[2012][m])>=10)
            if len(months)<2:continue
            month_counts.append(len(months))
            for k,(year,target) in enumerate(((2011,first),(2012,second))):
                target.append(np.stack([arrays[year][monthly[year][m]].mean(0) for m in months]).mean(0))
                retained[k]+=sum(len(monthly[year][m]) for m in months)
        else:
            for k,(year,target) in enumerate(((2011,first),(2012,second))):
                ix=indices[year][bird];target.append(arrays[year][ix].mean(0));retained[k]+=len(ix)
    receipt.update({'n_paired_identities':len(first),'paired_source_rows_first':retained[0],
                    'paired_source_rows_second':retained[1],
                    'weighting':'equal common months within identity, then equal identities' if month_matched else 'equal identities of within-year pooled episodes'})
    if month_matched:
        receipt['retained_months_per_identity_min_max']=[min(month_counts),max(month_counts)] if month_counts else []
        if len(first)<3 or min(retained)<100:
            return {'status':'NOT_ADMITTED_SHARED_MONTH_SUPPORT',**receipt}
    return {'status':'OBSERVED_PAIRED_COMMON_MONTHS' if month_matched else 'OBSERVED_PAIRED_RECURRENT_IDENTITIES',
            **receipt,'first_label':'2011 under fixed 2010 training','second_label':'2012 under fixed 2010 training',
            'paired':_paired_summary(first,second,draws,seed),
            'limits':'Prediction contrast; same month is not same route/activity/environment; few recurrent identities'}


def paired_update(rows,fixed_losses,updated_losses,*,draws=10000,seed=SEED):
    _check_rows(rows,2012)
    a=_check_losses(rows,fixed_losses);b=_check_losses(rows,updated_losses)
    groups=defaultdict(list)
    for i,r in enumerate(rows):groups[r['id']].append(i)
    receipt={'n_paired_identities':len(groups),'n_identical_2012_test_rows':len(rows)}
    if len(groups)<3:return {'status':'NOT_ADMITTED_UPDATE_IDENTITY_SUPPORT',**receipt}
    first=np.stack([a[ix].mean(0) for ix in groups.values()])
    second=np.stack([b[ix].mean(0) for ix in groups.values()])
    return {'status':'OBSERVED_SAME_ROWS_PAIRED_TRAINING_UPDATE',**receipt,
            'first_label':'F10 on 2012','second_label':'F1011 on 2012',
            'paired':_paired_summary(first,second,draws,seed),
            'limits':'Different fitted policy on identical test records, not causal environmental change'}
