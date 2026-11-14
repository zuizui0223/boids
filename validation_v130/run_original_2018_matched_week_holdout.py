"""v130 genuine 2018 Vlieland original ACC × RWS × astronomy:
exact same source observations across true and +3,+7,+11d stage alignment,
out-of-ISO-week forecast against clock/solar baselines. EXPLORATORY after v129.

No animal identifiers, geographic coordinates, raw event UTC or tide values
exported. Frozen spec: docs/V130_FROZEN_MATCHED_SUPPORT_WEEK_HOLDOUT_RWS_PHASE_SOURCE.md.
"""
from __future__ import annotations
from collections import Counter
from datetime import timedelta
import argparse,json
from pathlib import Path
import numpy as np

from original_2019_Vlieland_behaviour_source import _reference_anonymous_identity, SourceStop
from original_Vlieland_2018_ACC_GPS_year_source import (
    immutable_original_manifest,original_bytes,original_GPS_bird_year,
    original_2018_ACC_GPS_source_feasibility,
    ORIGINAL_REFERENCE,ORIGINAL_2018_GPS,ORIGINAL_2019_GPS,ORIGINAL_2018_ACC)
from run_original_2018_vlieland_forage_tide_solar import (
    source_only_replay,bins_2018_exact_v127_schema,PRIOR_V128_RUN)
from real_2018_vlieland_RWS_measured import (
    original_2018_vlieland_fourmonth_measured_tide,NativeSourceStop)
from vlieland_acc_forage_tide_sun_fourway import _solar_label
from two_gull_tide_solar_fourway import nearest_original_rws

FROZEN_SPEC='docs/V130_FROZEN_MATCHED_SUPPORT_WEEK_HOLDOUT_RWS_PHASE_SOURCE.md'
ORIGINAL_V129_RUN=43579877533
STAGE_OFFSETS=(0,3,7,11)
RIDGE_LAMBDA=20.
WEEK_FOLDS=5
WEEK_BOOT_N=10000
BOOT_SEED=20261114
MIN_BIRDS=25
MIN_COMMON_QUARTERHOURS=150000
MIN_WEEKS=12
MIN_MONTHS=4
MIN_WEEK_PER_FOLD=2
MIN_BIRD_PER_FOLD=3
MIN_EACH_SOLAR_FRACTION=.2
MODEL_NAMES=('CLOCK','SOLAR','TIDE-0','TIDE-3','TIDE-7','TIDE-11')


def exact_previous_2018_source_proof(prior,proof):
    if (prior.get('analysis')!='V129_ORIGINAL_VLIELAND_2018_HISTORICAL_YEAR_ACC_FORAGE_RWS_SOLAR_TRANSFER'
         or prior.get('source_and_field_status')!='2018_GENUINE_OBSERVED_SAME_TAXON_SITE_HISTORICAL_YEAR_S_T_I_ESTIMATED'):
        raise SourceStop('STOP_V130_PRIOR_V129_ORIGINAL_BEHAVIOR_NOT_SUCCESSFUL')
    old=prior['2018_original_4_month_10min_measured_RWS_harbour_tide']
    new=proof
    if (old['total_distinct_original_10min_2018_RWS_measured_times']!=17569 or
         new['total_distinct_original_10min_2018_RWS_measured_times']!=17569 or
         old['2018_native_RWS_station']!='vlieland.haven' or
         new['2018_native_RWS_station']!='vlieland.haven'):
        raise SourceStop('STOP_V130_2018_GENUINE_RWS_TOTAL_COUNT_OR_STATION_DRIFT')
    a=old['native_original_real_RWS_months']
    b=new['native_original_real_RWS_months']
    if ([v['true_original_RWS_source_month'] for v in a]!=[6,7,8,9] or
         len(b)!=4 or any(
         (o['native_RWS_response_SHA256']!=n['native_RWS_response_SHA256'] or
          o['original_2018_native_observed_10minute_time_count']!=n['original_2018_native_observed_10minute_time_count'])
         for o,n in zip(a,b))):
        raise SourceStop('STOP_V130_RWS_PROVIDER_SHA256_OR_MONTH_DRIFT')
    previous_source=prior['2018_2019_native_original_first_party_source_replay']
    if (previous_source['source_replay_status']!='EXACT_2018_GPS_ACC_2019_OVERLAP_AND_NATIVE_SHA_REPLAYED'
         or previous_source['true_tagged_bird_overlap_2018_2019']!=42 or
         prior['2018_original_15min_source_2019_v127_numeric_schema'][
             'original_2018_true_bird_ACC_GPS_15min_bins']!=243403):
        raise SourceStop('STOP_V130_OLD_V129_OBSERVATIONAL_REPLAY_IDENTITY_DRIFT')
    return {'v129_first_party_success_run':ORIGINAL_V129_RUN,
            'source_status':'2018_RWS_FOURMONTH_PROVIDER_SHA256_COUNTS_EXACTLY_REPLAYED',
            'source_original_10min_measured_RWS_distinct':17569,
            'verified_source_months':[6,7,8,9],
            'prior_bird_2018_2019_tag_overlap':42,
            'no_precise_gauge_source_times_or_heights_exported':True}


def common_matched_source(original_bins,source_rws):
    """Sensor timestamps, GPS location and genuine gauge can gate SOURCE only.
    Crucially no use of forage share Y in filtering common observation rows.
    """
    rws_sorted=sorted(source_rws)
    qa=Counter()
    common=[]
    for e in original_bins:
        s=_solar_label(e['source_utc_event'],e['source_lat'],e['source_lon'])
        qa['original_all_2018_binary_acc_gps_bins']+=1
        if s=='twilight':
            qa['original_astronomical_twilight_excluded']+=1
            continue
        matches=[]
        for shift in STAGE_OFFSETS:
            stage=nearest_original_rws(source_rws,rws_sorted,e['source_utc_event']+timedelta(days=shift))
            if stage is None:
                qa[f'original_missing_or_slack_source_tide_shift_{shift}days']+=1
                matches.append(None)
            else:
                matches.append((float(stage['source_stage_mNAP']),int(stage['source_phase'])))
        if any(x is None for x in matches):
            qa['source_excluded_not_all_four_real_RWS_alignments_valid']+=1
            continue
        t=e['source_utc_event']
        common.append((e,s,tuple(matches),int(t.isocalendar().week)))
    birdset={e['private_bird'] for e,_,_,_ in common}
    monthset={e['source_month'] for e,_,_,_ in common}
    weekset={w for _,_,_,w in common}
    day=sum(s=='day' for _,s,_,_ in common)
    night=len(common)-day
    fold_weeks={str(k):len({w for w in weekset if w%WEEK_FOLDS==k})
                for k in range(WEEK_FOLDS)}
    fold_birds={str(k):len({e['private_bird'] for e,_,_,w in common if w%WEEK_FOLDS==k})
                for k in range(WEEK_FOLDS)}
    gates={
       'original_genuine_birds_ge25':len(birdset)>=MIN_BIRDS,
       'genuine_source_common_bins_ge150k':len(common)>=MIN_COMMON_QUARTERHOURS,
       'original_iso_calendar_weeks_ge12':len(weekset)>=MIN_WEEKS,
       'original_separate_source_months_ge4':len(monthset)>=MIN_MONTHS,
       'original_solar_day_and_night_each_ge20pct':len(common)>0 and min(day,night)>=MIN_EACH_SOLAR_FRACTION*len(common),
       'five_folds_each_ge2_whole_weeks':all(n>=MIN_WEEK_PER_FOLD for n in fold_weeks.values()),
       'five_folds_each_ge3_true_birds':all(n>=MIN_BIRD_PER_FOLD for n in fold_birds.values())
    }
    report={'original_2018_genuine_source_15min_quarterhour_rows':len(common),
       'original_same_bird_gps_acc_source_birds':len(birdset),
       'original_source_months':sorted(monthset),
       'original_source_ISO_weeks_count':len(weekset),
       'original_source_genuine_day_15min_bins':day,
       'original_source_genuine_night_15min_bins':night,
       'original_2018_source_fold_distinct_week_count':fold_weeks,
       'original_2018_source_fold_distinct_bird_count':fold_birds,
       'original_source_QA':dict(qa),
       'same_exact_observation_rows_for_clock_solar_and_every_true_or_wrong_tide':True,
       'native_source_gates_before_ANY_new_v130_predictive_Y':gates,
       'all_source_gates_pass':all(gates.values()),
       'source_year':'2018',
       'GPS_bird_ID_and_exact_original_event_UTC_not_exported':True}
    return common,report


def fixed_predictor_matrices(common):
    """Predictors do not depend on ACC response values."""
    n=len(common)
    if n==0:raise SourceStop('STOP_V130_EMPTY_MATCHED_ORIGINAL_RWS_SOURCE')
    birds=sorted({e['private_bird'] for e,_,_,_ in common})
    bird_idx={b:i for i,b in enumerate(birds)}
    bird_ids=np.fromiter((bird_idx[e['private_bird']] for e,_,_,_ in common),
                         dtype=np.int32,count=n)
    weeks=np.fromiter((w for _,_,_,w in common),dtype=np.int32,count=n)
    fold=weeks%WEEK_FOLDS
    month=np.fromiter((e['source_month'] for e,_,_,_ in common),dtype=np.int32,count=n)
    night=np.fromiter((s=='night' for _,s,_,_ in common),dtype=np.float64,count=n)
    hours=np.fromiter((
        e['source_utc_event'].hour+e['source_utc_event'].minute/60+
        e['source_utc_event'].second/3600 for e,_,_,_ in common),dtype=float,count=n)
    day=np.fromiter((e['source_utc_event'].day for e,_,_,_ in common),dtype=float,count=n)
    terms=[np.ones(n)]
    # One reference bird omitted. Model is within same source tagged bird cohort.
    terms.extend((bird_ids==b).astype(float) for b in range(1,len(birds)))
    terms.extend((month==m).astype(float) for m in (7,8,9))
    terms.extend(z for k in (1,2,3) for z in (
        np.sin(2*np.pi*k*hours/24),
        np.cos(2*np.pi*k*hours/24)))
    terms.append((day-15.5)/15.)
    Xclock=np.column_stack(terms)
    Xsolar=np.column_stack((Xclock,night))
    mats={'CLOCK':Xclock,'SOLAR':Xsolar}
    for shift_idx,shift in enumerate(STAGE_OFFSETS):
        height=np.fromiter((matches[shift_idx][0] for _,_,matches,_ in common),
                           dtype=float,count=n)
        phase=np.fromiter((matches[shift_idx][1] for _,_,matches,_ in common),
                          dtype=float,count=n)
        if not np.isfinite(height).all() or not np.isin(phase,(-1,1)).all():
            raise SourceStop('STOP_V130_SOURCE_STAGE_FINITE_OR_PHASE_INVALID')
        mats[f'TIDE-{shift}']=np.column_stack((
            Xsolar,height,phase,height*phase,night*phase,night*height))
    if (set(mats)!=set(MODEL_NAMES) or any(x.shape[0]!=n for x in mats.values())
       or len({mats[f'TIDE-{shift}'].shape[1] for shift in STAGE_OFFSETS})!=1):
        raise SourceStop('STOP_V130_ORIGINAL_MODEL_FEATURE_DIMENSION_MISMATCH')
    return mats,{'bird_index':bird_ids,'source_week':weeks,'fold':fold,'months':month}


def ridge_fit_predict(trainX,trainy,testX,lam=RIDGE_LAMBDA):
    if trainX.ndim!=2 or trainX.shape[0]!=len(trainy) or testX.shape[1]!=trainX.shape[1]:
        raise ValueError('STOP_V130_TRAIN_TEST_RIDGE_DIMENSION')
    if not np.isfinite(trainX).all() or not np.isfinite(trainy).all():
        raise ValueError('STOP_V130_NONFINITE_ORIGINAL_TRAINING_SOURCE')
    gram=trainX.T@trainX
    penalty=np.full(trainX.shape[1],lam,dtype=float);penalty[0]=0.
    gram.flat[::len(penalty)+1]+=penalty
    beta=np.linalg.solve(gram,trainX.T@trainy)
    return np.clip(testX@beta,0.,1.)


def weeks_bird_equal_scores(y,predictions,week,bird):
    if y.ndim!=1 or len(y)!=len(week) or len(y)!=len(bird) or not predictions:
        raise ValueError('STOP_V130_BAD_OBSERVATION_OR_PREDICTION_INDEX')
    weeks,wi=np.unique(week,return_inverse=True)
    birds,bi=np.unique(bird,return_inverse=True)
    nb=len(birds)
    pair=wi*nb+bi
    counts=np.bincount(pair,minlength=len(weeks)*nb).reshape(len(weeks),nb)
    nonzero=(counts>0)
    if not nonzero.all(axis=1).all():
        raise ValueError('STOP_V130_ORIGINAL_WEEK_WITH_NO_BIRDS')
    score=np.empty((len(weeks),len(MODEL_NAMES)),dtype=float)
    for m,name in enumerate(MODEL_NAMES):
        pred=predictions[name]
        if len(pred)!=len(y) or not np.isfinite(pred).all():
            raise ValueError('STOP_V130_BAD_SOURCE_PREDICTION_LENGTH_OR_NONFINITE')
        sq=(y-pred)**2
        sums=np.bincount(pair,weights=sq,minlength=len(weeks)*nb).reshape(len(weeks),nb)
        group=np.zeros_like(sums)
        group[nonzero]=sums[nonzero]/counts[nonzero]
        score[:,m]=group.sum(axis=1)/nonzero.sum(axis=1)
    return weeks,score,{'source_independent_calendar_weeks_n':len(weeks),
                        'original_distinct_tagged_birds_with_weekly_test_targets':len(birds),
                        'mean_true_birds_per_heldout_week':float(nonzero.sum(axis=1).mean()),
                        'source_genuine_bird_week_score_groups':int(nonzero.sum()),
                        'weeks_equal_weight_and_within_week_birds_equal_weight':True}


def effect_from_week_scores(weeks,score):
    if score.ndim!=2 or score.shape[1]!=len(MODEL_NAMES) or len(weeks)!=len(score):
        raise ValueError('STOP_V130_SCORES_BAD_DIMENSION')
    avg=score.mean(axis=0)
    solar=float(avg[0]-avg[1])
    gains={str(s):float(avg[1]-avg[k+2]) for k,s in enumerate(STAGE_OFFSETS)}
    phase=float(gains['0']-max(gains[str(s)] for s in (3,7,11)))
    deltas={'D_solar_clock_minus_solar':solar,'D_tide_real_solar_minus_real':gains['0'],
        'D_wrong_3_solar_minus_wrong':gains['3'],
        'D_wrong_7_solar_minus_wrong':gains['7'],
        'D_wrong_11_solar_minus_wrong':gains['11'],
        'D_phase_real_gain_minus_best_wrong_gain':phase}
    rng=np.random.default_rng(BOOT_SEED)
    indices=rng.integers(0,len(weeks),size=(WEEK_BOOT_N,len(weeks)))
    b=score[indices,:].mean(axis=1)
    bsolar=b[:,0]-b[:,1]
    btide=b[:,1]-b[:,2]
    bg=b[:,[3,4,5]]
    bphase=btide-(b[:,1,None]-bg).max(axis=1)
    ci={
        'D_solar':list(map(float,np.quantile(bsolar,(.025,.975)))),
        'D_tide_real':list(map(float,np.quantile(btide,(.025,.975)))),
        'D_phase_real_minus_best_wrong':list(map(float,np.quantile(bphase,(.025,.975))))
    }
    perweek_gains=score[:,1,None]-score[:,2:]
    week_real_minus_best=perweek_gains[:,0]-perweek_gains[:,1:].max(axis=1)
    pos_week=float((week_real_minus_best>0).mean())
    fold_summary={}
    for fold in range(WEEK_FOLDS):
        rows=np.where(weeks%WEEK_FOLDS==fold)[0]
        if len(rows)<MIN_WEEK_PER_FOLD:
            raise ValueError('STOP_V130_CV_FOLD_LOST_SOURCE_WEEKS')
        group=score[rows].mean(axis=0)
        fold_summary[str(fold)]={'whole_weeks_in_test_fold':len(rows),
            'D_solar':float(group[0]-group[1]),
            'D_real_tide':float(group[1]-group[2]),
            'D_phase_vs_best_wrong':float((group[1]-group[2])-max(group[1]-group[j] for j in (3,4,5)))}
    return {
      'model_week_and_bird_equal_heldout_MSE':{k:float(v) for k,v in zip(MODEL_NAMES,avg)},
      'predeclared_original_2018_heldout_week_solar_tide_and_phase_contrasts':deltas,
      'source_week_paired_bootstrap_CI95_descriptive_not_causal':ci,
      'source_calendar_weeks_positive_real_tide_vs_best_wrong_n':int((week_real_minus_best>0).sum()),
      'source_calendar_weeks_positive_real_tide_vs_best_wrong_fraction':pos_week,
      'source_calendar_weeks_positive_solar_over_clock_n':int((score[:,0]>score[:,1]).sum()),
      'source_calendar_weeks_positive_real_tide_over_solar_n':int((score[:,1]>score[:,2]).sum()),
      'five_predeclared_outofweek_folds_anonymous':fold_summary,
      'exploratory_solar_outofweek_gain_status':(
           'POSITIVE_CONDITIONAL_WEEK_INTERVAL' if solar>0 and ci['D_solar'][0]>0
           else 'NOT_ESTABLISHED_OUTOFWEEK'),
      'exploratory_correct_tide_phase_uniqueness_status':(
          'SUGGESTIVE_WITHIN_SOURCE_ONLY' if phase>0 and ci['D_phase_real_minus_best_wrong'][0]>0 and pos_week>=.6
          else 'NOT_ESTABLISHED_BY_MATCHED_WEEK_FORECAST'),
      'bootstrap_10000_whole_2018_week_score_vectors_NOT_independent_sites_or_years':True,
      'no_animal_ID_precise_time_or_raw_tide_values_exported':True}


def estimate_week_forecast(common):
    """Only call AFTER source has met complete no-Y source gate."""
    mats,labels=fixed_predictor_matrices(common)
    # Frozen scalar sensor event *share* and fixed matched observations.
    y=np.fromiter((e['original_acc_forage_events']/
                   (e['original_acc_forage_events']+e['original_acc_inactive_events'])
                   for e,_,_,_ in common),dtype=float,count=len(common))
    if not np.isfinite(y).all() or np.min(y)<0 or np.max(y)>1:
        raise SourceStop('STOP_V130_ORIGINAL_ACC_PREDICTED_SHARE_NOT_IN_ZERO_ONE')
    pred={m:np.full(len(common),np.nan,dtype=float) for m in MODEL_NAMES}
    folds=labels['fold']
    for fold in range(WEEK_FOLDS):
        test=(folds==fold)
        train=~test
        if not (test.sum()>0 and train.sum()>0):
            raise SourceStop('STOP_V130_WEEK_FOLD_HAS_NO_TEST_OR_TRAIN')
        for name in MODEL_NAMES:
            pred[name][test]=ridge_fit_predict(
                mats[name][train],y[train],mats[name][test],lam=RIDGE_LAMBDA)
        print('V130_ORIGINAL_HELDOUT_WEEK_FOLD_SCORED '+json.dumps({
            'fold':fold,'genuine_bird_15min_test_bins':int(test.sum()),
            'actual_whole_ISO_weeks_in_test':len(set(labels['source_week'][test])),
            'same_original_source_rows_across_all_six_predictors':True,
            'training_contains_NO_heldout_test_week_bins':True},sort_keys=True),flush=True)
    weeks,weekscore,source=weeks_bird_equal_scores(
        y,pred,labels['source_week'],labels['bird_index'])
    if len(weeks)<MIN_WEEKS:
        raise SourceStop('STOP_V130_SCORE_SOURCE_WEEKS_DISAPPEARED')
    return {**source,**effect_from_week_scores(weeks,weekscore),
        'original_2018_true_source_common_sample_bird_quarterhours':len(common),
        'Y_is_ACC_classifier_event_fraction_not_true_foraging_duration':True,
        'scoring_week_unit_NOT_200k_independent_behaviors':True,
        'tide_is_25km_harbour_stage_proxy_not_local_intertidal_exposure':True,
        'year_2018_chosen_after_2019_field_effects':True}


def write_report(report,path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    forecast=report.get('source_identical_rows_2018_week_holdout_forecast') or {}
    print('V130_REAL_ORIGINAL_2018_MATCHED_WEEK_HOLDOUT_SOURCE_RESULT '+json.dumps({
        'status':report['source_or_forecast_status'],
        'source_common_support':report.get('original_2018_common_RWS_phase_matches_before_Y'),
        'heldout_week_mse':forecast.get('model_week_and_bird_equal_heldout_MSE'),
        'original_week_score_contrasts':forecast.get('predeclared_original_2018_heldout_week_solar_tide_and_phase_contrasts'),
        'matched_phase_forecast_status':forecast.get('exploratory_correct_tide_phase_uniqueness_status'),
        'source_stop':report.get('source_stop_reason'),
        'NOT_causal_tidal_clock_or_foraging_minutes':True},sort_keys=True),flush=True)
    return report


def run(prior_v128_path,prior_v129_path,out):
    report={'analysis':'V130_ORIGINAL_2018_VLIELAND_GENUINE_ACC_RWS_SUN_MATCHED_WEEK_FORECAST',
        'source_or_forecast_status':'SOURCE_PENDING',
        'frozen_before_v130_week_prediction':FROZEN_SPEC,
        '2018_v130_post_original_v129_observed_effects_EXPLORATORY':True,
        'same_2018_GPS_ACC_2019_bird_overlap_42_NOT_independent_cross_year_birds':True,
        'real_RWS_harbour_stage_not_local_true_patch_flooding':True,
        'original_tag_ids_GPS_UTC_and_native_tide_height_NOT_exported':True}
    try:
        prior_v128=json.loads(Path(prior_v128_path).read_text())
        prior_v129=json.loads(Path(prior_v129_path).read_text())
        files,manifest=immutable_original_manifest()
        refraw,pref=original_bytes(files[ORIGINAL_REFERENCE])
        ref,refqa=_reference_anonymous_identity(refraw)
        raw18,p18=original_bytes(files[ORIGINAL_2018_GPS])
        indexed,b18,gps18=original_GPS_bird_year(raw18,2018,ref,True)
        del raw18
        raw19,p19=original_bytes(files[ORIGINAL_2019_GPS])
        _,b19,gps19=original_GPS_bird_year(raw19,2019,ref,False)
        del raw19
        overlap={'original_2018_genuine_GPS_birds':len(b18),
          'original_2019_genuine_GPS_birds':len(b19),
          'same_true_tagged_birds_recorded_in_BOTH_2018_and2019_GPS_years':len(b18&b19),
          'original_2018_only_tagged_birds':len(b18-b19),
          'original_2019_only_tagged_birds':len(b19-b18),
          'source_new_2018_year_not_independent_2019_bird_replicates':len(b18&b19)>0}
        rawacc,pacc=original_bytes(files[ORIGINAL_2018_ACC])
        acc,qualified,private=original_2018_ACC_GPS_source_feasibility(
            rawacc,ref,indexed,return_private_quarterhour_bins=True)
        del rawacc,indexed,ref
        report['original_Zenodo_2018_2019_GPS_ACC_source_identity_v128_exact_replay']=source_only_replay(
            prior_v128,gps18,gps19,acc,overlap,{
             ORIGINAL_REFERENCE:pref,ORIGINAL_2018_GPS:p18,
             ORIGINAL_2019_GPS:p19,ORIGINAL_2018_ACC:pacc})
        if len(qualified)<8 or not acc['source_frozen_YEAR2018_bird_ge8_15minute_bins_ge1000_eligible']:
            raise SourceStop('STOP_V130_ORIGINAL_ACC_GPS_YEAR_SOURCE_NOT_ADMITTED')
        bins,originalbinproof=bins_2018_exact_v127_schema(private,acc)
        del private
        report['original_2018_same_bird_ACC_GPS_15min_original_source_replay']=originalbinproof
        RWS,proof=original_2018_vlieland_fourmonth_measured_tide()
        report['original_2018_measured_RWS_and_v129_exact_source_SHA256_replay']=exact_previous_2018_source_proof(
            prior_v129,proof)
        print('V130_FIRST_PARTY_MD5_GPS_ACC_RWS_SOURCE_REPLAYED_BEFORE_NEW_WEEKLY_Y '+json.dumps({
            'v128_replayed':report['original_Zenodo_2018_2019_GPS_ACC_source_identity_v128_exact_replay'],
            'v129_RWS_replayed':report['original_2018_measured_RWS_and_v129_exact_source_SHA256_replay'],
            'native_source_original_2018_15min_bin_n':len(bins),
            'no_new_week_CV_behavior_scores_yet':True},sort_keys=True),flush=True)
    except (SourceStop,NativeSourceStop,ValueError,TypeError,KeyError,OSError,
            TimeoutError,UnicodeDecodeError,json.JSONDecodeError) as e:
        report['source_or_forecast_status']='SOURCE_STOP_2018_GPS_ACC_OR_RWS_EXACT_REPLAY'
        report['source_stop_reason']=str(e)[:260]
        return write_report(report,out)
    try:
        common,gate=common_matched_source(bins,RWS)
        report['original_2018_common_RWS_phase_matches_before_Y']=gate
        print('V130_TRUE_2018_IDENTICAL_OBSERVATION_SUPPORT_BEFORE_NEW_WEEKLY_Y '+json.dumps(
            gate,sort_keys=True),flush=True)
        del bins,RWS
        if not gate['all_source_gates_pass']:
            report['source_or_forecast_status']='NOT_ESTIMATED_2018_WEEK_FORECAST_SOURCE_GATE'
            return write_report(report,out)
        scores=estimate_week_forecast(common)
        del common
        report['source_identical_rows_2018_week_holdout_forecast']=scores
        report['source_or_forecast_status']='2018_ORIGINAL_MATCHED_WEEK_HELDOUT_EXPLORATORY_FORECAST_EVALUATED'
        return write_report(report,out)
    except (SourceStop,NativeSourceStop,ValueError,TypeError,KeyError,OSError,
            TimeoutError,np.linalg.LinAlgError) as e:
        report['source_or_forecast_status']='STOP_ORIGINAL_2018_MATCHED_FOUR_TIDE_WEEK_SCORE'
        report['source_stop_reason']=str(e)[:260]
        return write_report(report,out)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--v128-original-source',required=True)
    ap.add_argument('--v129-original-real-result',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    run(args.v128_original_source,args.v129_original_real_result,args.output)
