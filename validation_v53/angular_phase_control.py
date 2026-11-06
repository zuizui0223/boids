"""Paired angular comparison using one original source cohort and three models.

Pure numerics / row handling only. The placebo is an exact 365-day offset,
not calendar-year replacement. Existing v52 angular normalization is reused.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import timedelta
import numpy as np
from bearing_decomposition import decompose_predictions

MODELS=('M0','Mactual','M365')
CONTRASTS=(('M365_minus_Mactual','M365','Mactual'),
           ('M0_minus_Mactual','M0','Mactual'),
           ('M0_minus_M365','M0','M365'))
METRICS=('cosine_loss','absolute_angle_degrees','vector_half_MSE')


def attach_yearago_phase(rows, original_water):
    common=[];missing=0;zero=0
    for row in rows:
        t=row['t']
        if t.tzinfo is None or t.utcoffset() is None:
            raise ValueError('Original source time must be timezone-aware')
        try:
            _,p,_=original_water.at_with_phase(t-timedelta(days=365))
        except ValueError:
            missing+=1
            continue
        if p not in (-1,0,1):
            raise ValueError('Historical gauge phase outside frozen states')
        common.append({**row,'ghost_phase':int(p)})
        zero+=int(p==0)
    return common,{'original_rows':len(rows),'common_rows':len(common),
                   'removed_missing_history':missing,'ghost_zero_rows':zero,
                   'offset_days':365,'actual_height_and_target_unchanged':True}


def replace_phase(rows):
    result=[]
    for row in rows:
        p=row.get('ghost_phase')
        if p not in (-1,0,1):
            raise ValueError('Missing or invalid source historical phase')
        result.append({**row,'phase':int(p)})
    return result


def source_admission(train,test,test_year):
    if test_year not in (2011,2012):
        raise ValueError('Unfrozen test year')
    expected={2010} if test_year==2011 else {2010,2011}
    for rows,years in ((train,expected),(test,{test_year})):
        keys=set()
        for r in rows:
            if r['t'].year not in years:
                raise ValueError('Chronological split changed')
            key=(r['id'],r['t'])
            if key in keys:raise ValueError('Duplicate original episode')
            keys.add(key)
        if rows and {r['t'].year for r in rows}!=years:
            raise ValueError('Missing prescribed source training year')
    birds=len({r['id'] for r in test})
    weeks=len({r['t'].isocalendar()[:2] for r in test})
    return {'admitted':len(train)>=1000 and len(test)>=1000 and birds>=3 and weeks>=4,
            'train_rows':len(train),'test_rows':len(test),
            'test_birds':birds,'test_weeks':weeks,'test_year':test_year,
            'minimum_train_rows':1000,'minimum_test_rows':1000,
            'minimum_test_birds':3,'minimum_test_weeks':4}


def summarize_models(rows,truth,predictions,*,bird_draws=10000,week_draws=4000,seed=20261106):
    """Same paired source clusters for all model contrasts and angular metrics."""
    if set(predictions)!=set(MODELS) or not rows:
        raise ValueError('Exactly three models and nonempty source rows required')
    if bird_draws<1 or week_draws<1:
        raise ValueError('Positive resampling count required')
    real=decompose_predictions(truth,predictions['M0'],predictions['Mactual'])
    ghost=decompose_predictions(truth,predictions['M0'],predictions['M365'])
    bymodel={
        'M0':(real,'0'), 'Mactual':(real,'1'), 'M365':(ghost,'1')}
    columns=[]
    for model in MODELS:
        data,suffix=bymodel[model]
        columns.extend([data['cosine_loss'+suffix],data['angle_degrees'+suffix],
                        data['vector_loss'+suffix]])
    raw=np.column_stack(columns)
    if raw.shape!=(len(rows),9) or not np.isfinite(raw).all():
        raise ValueError('Original rows and forecast losses not aligned')
    birds=defaultdict(list);weeks=defaultdict(list)
    for i,r in enumerate(rows):
        birds[r['id']].append(i)
        weeks[r['t'].isocalendar()[:2]].append(i)
    perbird=np.stack([raw[v].mean(0) for v in birds.values()])
    perweek=[]
    for indices in weeks.values():
        present=defaultdict(list)
        for i in indices:present[rows[i]['id']].append(i)
        perweek.append(np.stack([raw[v].mean(0) for v in present.values()]).mean(0))
    perweek=np.stack(perweek)
    model_index={name:i*3 for i,name in enumerate(MODELS)}
    def aggregate(clusters,draws,random_seed):
        point=clusters.mean(0)
        indices=np.random.default_rng(random_seed).integers(len(clusters),size=(draws,len(clusters)))
        boot=clusters[indices].mean(1)
        means={m:dict(zip(METRICS,map(float,point[i*3:i*3+3]))) for i,m in enumerate(MODELS)}
        contrasts={}
        for name,left,right in CONTRASTS:
            a,b=model_index[left],model_index[right]
            metrics={}
            for k,label in enumerate(('cosine_loss_gain','absolute_angle_gain_degrees','vector_half_MSE_gain')):
                delta=boot[:,a+k]-boot[:,b+k]
                metrics[label]={'mean':float(point[a+k]-point[b+k]),
                    'paired_bootstrap_CI95':np.quantile(delta,[.025,.975]).tolist(),
                    'positive_clusters':int(np.sum(clusters[:,a+k]>clusters[:,b+k]))}
            metrics['cosine_relative_error_reduction']=float((point[a]-point[b])/point[a]) if point[a]>0 else None
            contrasts[name]=metrics
        return {'n_clusters':len(clusters),'model_mean_losses':means,'contrasts':contrasts}
    diagnostics={}
    for name,p in predictions.items():
        norms=np.linalg.norm(np.asarray(p,dtype=float),axis=1)
        diagnostics[name]={'min_median_max_norm':np.quantile(norms,[0,.5,1]).tolist(),
                           'norm_above_one':int(np.sum(norms>1))}
    return {'n_rows':len(rows),'n_birds':len(birds),'n_weeks':len(weeks),
        'primary_contrast':'M365_minus_Mactual','primary_endpoint':'cosine_loss_gain',
        'equal_bird':aggregate(perbird,bird_draws,seed),
        'equal_week_then_bird':aggregate(perweek,week_draws,seed+1),
        'norm_diagnostics':diagnostics,
        'same_source_rows_all_models':True,
        'limits':'Historical control not a causal counterfactual; weeks may be serially dependent'}
