"""One original-2010 policy with ALL future evaluation identities excluded.

Identity-disjoint means source identifier separation within each study. It is
not an independent recapture audit, new field cohort, or causal tidal model.
"""
from __future__ import annotations
from datetime import datetime
import numpy as np
from angular_phase_control import replace_phase, summarize_models
from bearing_decomposition import UndefinedBearing

MIN_TRAIN_ROWS=1000
MIN_TRAIN_BIRDS=3
MIN_TEST_ROWS=1000
MIN_TEST_BIRDS=3
MIN_TEST_WEEKS=4


def validate_rows(records,year):
    """Validate the split without reading future outcome values."""
    keys=set()
    for r in records:
        identity=r.get('id');stamp=r.get('t')
        if not isinstance(identity,str) or not identity.strip() or identity!=identity.strip():
            raise ValueError('Missing or inconsistent source identity')
        if not isinstance(stamp,datetime) or stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError('Original episode time must be timezone-aware')
        if stamp.year!=year:raise ValueError('Original source chronological year changed')
        key=(identity,stamp)
        if key in keys:raise ValueError('Duplicate source episode')
        keys.add(key)


def validate_evaluations(evaluations):
    if not evaluations or not set(evaluations)<={2011,2012}:
        raise ValueError('Only predefined 2011/2012 test years')
    for year,records in evaluations.items():validate_rows(records,year)


def partition_training(train,evaluations):
    """Remove the UNION of evaluated source identities, not one fold at a time."""
    validate_rows(train,2010);validate_evaluations(evaluations)
    excluded={r['id'] for a in evaluations.values() for r in a}
    before={r['id'] for r in train}
    kept=[r for r in train if r['id'] not in excluded]
    after={r['id'] for r in kept}
    if after&excluded:raise AssertionError('SOURCE_IDENTITY_LEAKAGE')
    receipt={'training_year':2010,'evaluation_years':sorted(evaluations),
             'original_training_rows':len(train),'original_training_birds':len(before),
             'test_identity_count':len(excluded),
             'removed_training_rows':len(train)-len(kept),
             'removed_training_identities':len(before&excluded),
             'training_rows_after_exclusion':len(kept),
             'training_birds_after_exclusion':len(after),
             'train_test_identity_overlap_after_exclusion':len(after&excluded),
             'minimum_training_rows':MIN_TRAIN_ROWS,
             'minimum_training_birds':MIN_TRAIN_BIRDS,
             'training_admitted':len(kept)>=MIN_TRAIN_ROWS and len(after)>=MIN_TRAIN_BIRDS,
             'test_rows_unchanged':True,'no_original_identity_values_exported':True,
             'identity_basis':'provider individual-local-identifier, not re-tagging adjudication'}
    return kept,receipt


def test_gate(records,year):
    validate_rows(records,year)
    birds=len({r['id'] for r in records})
    weeks=len({r['t'].isocalendar()[:2] for r in records})
    return {'admitted':len(records)>=MIN_TEST_ROWS and birds>=MIN_TEST_BIRDS and weeks>=MIN_TEST_WEEKS,
            'test_year':year,'test_rows':len(records),'test_birds':birds,'test_weeks':weeks,
            'minimum_test_rows':MIN_TEST_ROWS,'minimum_test_birds':MIN_TEST_BIRDS,
            'minimum_test_weeks':MIN_TEST_WEEKS}


def forecast_fixed(train,evaluations,forecast_fn):
    """One fit call/model, same 2010 cohort, concatenated future-year forecast.

    Used for both known all-identity replay and the new disjoint policy. The
    caller performs identity exclusion before any new heldout model is fitted.
    """
    validate_rows(train,2010);validate_evaluations(evaluations)
    if not train:raise ValueError('Empty source training set')
    years=sorted(evaluations)
    test=[r for year in years for r in evaluations[year]]
    if not test:raise ValueError('Empty source test set')
    p={'M0':forecast_fn(train,test,0),'Mactual':forecast_fn(train,test,1),
       'M365':forecast_fn(replace_phase(train),replace_phase(test),1)}
    for key,value in p.items():
        a=np.asarray(value,dtype=float)
        if a.shape!=(len(test),2) or not np.isfinite(a).all():
            raise ValueError('Original forecast shape or finite-value violation')
        p[key]=a
    split={};start=0
    for year in years:
        stop=start+len(evaluations[year])
        split[year]={model:pred[start:stop] for model,pred in p.items()}
        start=stop
    return split


def evaluate_transfer(train,evaluations,forecast_fn,*,bird_draws=10000,week_draws=4000):
    kept,support=partition_training(train,evaluations)
    report={'status':'NOT_ADMITTED_TRAINING_IDENTITY_SUPPORT',
            'identity_split':support,'outcomes':{}}
    if not support['training_admitted']:return report
    gates={year:test_gate(records,year) for year,records in evaluations.items()}
    admitted={year:evaluations[year] for year in sorted(evaluations) if gates[year]['admitted']}
    forecasts=forecast_fixed(kept,admitted,forecast_fn) if admitted else {}
    report['status']='OBSERVED_IDENTITY_DISJOINT_YEAR_TRANSFER' if admitted else 'NOT_ADMITTED_TEST_SOURCE_SUPPORT'
    for year in sorted(evaluations):
        result={'source_gate':gates[year]}
        if year not in admitted:
            result['status']='NOT_ADMITTED_TEST_SOURCE_SUPPORT'
            result['outcome']='NOT_ESTIMATED'
        else:
            truth=np.asarray([[r['target_e'],r['target_n']] for r in evaluations[year]])
            try:
                result['metrics']=summarize_models(evaluations[year],truth,forecasts[year],
                            bird_draws=bird_draws,week_draws=week_draws,seed=20261106)
                result['status']='OBSERVED_UNSEEN_IDENTITY_AND_YEAR_ANGULAR_PREDICTION'
            except UndefinedBearing as error:
                result.update(status='NOT_ADMITTED_UNDEFINED_BEARING',
                              reason=str(error),no_source_rows_dropped=True)
        report['outcomes'][str(year)]=result
    report['limits']=['post-v54 exploratory source-identity holdout, not independent field study',
        'conditional test-bird bootstrap does not propagate training-fit uncertainty',
        'removing evaluation birds changes training sample size and covariate support',
        'same species and region; no actual prey-front or social force identified']
    return report
