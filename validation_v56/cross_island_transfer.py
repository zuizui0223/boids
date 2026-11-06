"""Chronological cross-island transfer with pre-fixed translation-only alignment.

Target 2010 positions define an unlabeled location anchor, not target behavior
coefficients. No 2011 label or location defines the geographic transformation.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
import numpy as np
from angular_phase_control import replace_phase,summarize_models
from bearing_decomposition import UndefinedBearing

MIN_ROWS=1000
MIN_BIRDS=3
MIN_WEEKS=4
SUPPORT_FEATURES=('h','lat','lon','previous_speed_log')


def validate_rows(records,year):
    seen=set()
    for r in records:
        t=r.get('t');identity=r.get('id')
        if not isinstance(identity,str) or not identity.strip():raise ValueError('Missing source id')
        if not isinstance(t,datetime) or t.tzinfo is None or t.utcoffset() is None or t.year!=year:
            raise ValueError('Original source year/time changed')
        if (identity,t) in seen:raise ValueError('Duplicate original source episode')
        seen.add((identity,t))
        for k in ('lat','lon'):
            if not np.isfinite(float(r[k])):raise ValueError('Nonfinite source location')
        if not (-90<=r['lat']<=90 and -180<=r['lon']<=180):raise ValueError('Invalid WGS84 location')


def bird_equal_center(records):
    validate_rows(records,2010)
    if not records:raise ValueError('Empty 2010 position reference')
    bybird=defaultdict(list)
    for r in records:bybird[r['id']].append((r['lat'],r['lon']))
    center=np.mean([np.mean(v,axis=0) for v in bybird.values()],axis=0)
    return tuple(map(float,center))


def translate_rows(records,source_center,target_center):
    delta=np.asarray(source_center,dtype=float)-np.asarray(target_center,dtype=float)
    if delta.shape!=(2,) or not np.isfinite(delta).all():raise ValueError('Invalid alignment centers')
    return [{**r,'lat':float(r['lat']+delta[0]),'lon':float(r['lon']+delta[1])} for r in records]


def prepare_transfer(source_train,target_reference,test):
    validate_rows(source_train,2010);validate_rows(target_reference,2010);validate_rows(test,2011)
    target_ids={r['id'] for r in test};source_ids={r['id'] for r in source_train}
    kept=[r for r in source_train if r['id'] not in target_ids]
    remaining={r['id'] for r in kept}
    gate={'source_original_training_rows':len(source_train),
          'source_original_training_birds':len(source_ids),
          'removed_training_rows':len(source_train)-len(kept),
          'removed_literal_identities':len(source_ids&target_ids),
          'training_rows':len(kept),'training_birds':len(remaining),
          'training_test_literal_overlap':len(remaining&target_ids),
          'target2010_reference_rows':len(target_reference),
          'target2010_reference_birds':len({r['id'] for r in target_reference}),
          'test_rows':len(test),'test_birds':len(target_ids),
          'test_weeks':len({r['t'].isocalendar()[:2] for r in test}),
          'minimum_rows':MIN_ROWS,'minimum_birds':MIN_BIRDS,'minimum_test_weeks':MIN_WEEKS}
    gate['admitted']=(gate['training_rows']>=MIN_ROWS and gate['training_birds']>=MIN_BIRDS
        and gate['target2010_reference_rows']>=MIN_ROWS and gate['target2010_reference_birds']>=MIN_BIRDS
        and gate['test_rows']>=MIN_ROWS and gate['test_birds']>=MIN_BIRDS and gate['test_weeks']>=MIN_WEEKS)
    if remaining&target_ids:raise AssertionError('Source identity collision survived exclusion')
    return kept,gate


def covariate_support(train,test):
    if not train or not test:raise ValueError('Empty support audit')
    a=np.asarray([[r[k] for k in SUPPORT_FEATURES] for r in train],dtype=float)
    b=np.asarray([[r[k] for k in SUPPORT_FEATURES] for r in test],dtype=float)
    if not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('Nonfinite support feature')
    lo,hi=np.quantile(a,[.01,.99],axis=0)
    # Tolerance only for floating translation roundoff, not ecological trimming.
    outside=(b<lo-1e-12)|(b>hi+1e-12)
    return {'per_feature_outside_1_99':dict(zip(SUPPORT_FEATURES,map(float,outside.mean(0)))),
            'fraction_outside_any_marginal_range':float(outside.any(1).mean()),
            'descriptive_only_no_rows_filtered':True,
            'not_a_joint_covariate_or_habitat_support_test':True}


def evaluate_transfer(source_train,target_reference,test,forecast_fn,*,bird_draws=10000,week_draws=4000):
    train,gate=prepare_transfer(source_train,target_reference,test)
    if not gate['admitted']:return {'status':'NOT_ADMITTED_CROSS_ISLAND_SOURCE','source_gate':gate}
    source_center=bird_equal_center(train);target_center=bird_equal_center(target_reference)
    translated=translate_rows(test,source_center,target_center)
    all_inputs=list(test)+translated
    predictions={'M0':forecast_fn(train,all_inputs,0),
                 'Mactual':forecast_fn(train,all_inputs,1),
                 'M365':forecast_fn(replace_phase(train),replace_phase(all_inputs),1)}
    n=len(test)
    for model,pred in predictions.items():
        a=np.asarray(pred,dtype=float)
        if a.shape!=(2*n,2) or not np.isfinite(a).all():raise ValueError('Invalid cross-site forecast shape/value')
        predictions[model]=a
    truth=np.asarray([[r['target_e'],r['target_n']] for r in test],dtype=float)
    results={}
    for name,start,inputs in (('native',0,test),('translated',n,translated)):
        result={'covariate_support':covariate_support(train,inputs)}
        try:
            result.update(status='OBSERVED_CROSS_ISLAND_ANGULAR_TRANSFER',
                metrics=summarize_models(test,truth,{m:p[start:start+n] for m,p in predictions.items()},
                    bird_draws=bird_draws,week_draws=week_draws,seed=20261106))
        except UndefinedBearing as e:
            result.update(status='NOT_ADMITTED_UNDEFINED_BEARING',reason=str(e),no_rows_dropped=True)
        results[name]=result
    return {'status':'OBSERVED_CROSS_ISLAND_YEAR_TRANSFER','source_gate':gate,
            'primary_condition':'translated','primary_contrast':'M365_minus_Mactual',
            'primary_endpoint':'cosine_loss_gain','conditions':results,
            'same_source_fit_across_coordinate_conditions':True,
            'target2010_positions_only_used_for_translation':True,
            'no_target_behavior_response_used_for_model_fit':True,
            'limits':['translation is not coastline/foraging-habitat registration',
                      'no target2011 coordinate or target heading used to choose alignment',
                      'paired test-bird intervals do not include training-fit uncertainty',
                      'same species and nearby region; no true front or social force estimated']}
