"""v98 real cross-YEAR and cross-LATITUDE-BAND prediction of tidal-solar physical overlap.
Train ONLY on 2019 UHSLC source, score genuine observed 2018 gauge hourly
Q25×astronomical sunlight at previously unseen 15-degree source bands.
2018 recorded gauge outcomes MUST NOT enter fitting, standardization, or tuning.
Same-site 2019 physical persistence is a separate benchmark, not a training model.
The predicted outcome is GAUGE low-water coincidence, NEVER animal time use.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean
from math import log1p
import argparse,json
import numpy as np
from aggregate_all_2019_physical import (
    macro_rows,coastal_clusters,features,ridge_predict,spearman,SEED)
from real_global_UHSLC_hourly_station_manifest import _latitude_band
N_RESAMPLE=10000
V94_RUN=42616065580
V97_RUN=42729101678
BANDS_2019={'N_00_15','N_15_30','N_30_45','N_45_60','N_60_75',
            'S_00_15','S_30_45','S_45_60'}
def source_census(v94files,v97files):
    if len(v94files)!=12:raise ValueError('STOP v94 all candidate source frame missing')
    if len(v97files)!=8:raise ValueError('STOP 2018 8 pre-frozen band original source files missing')
    source,byband,counts,_=macro_rows(v94files)
    if counts['candidate']!=564 or counts['eligible']!=160:
        raise ValueError('STOP parent 2019 qualified-original geography changed')
    real2018={}
    actualband=set()
    source_failure=Counter();year_qc=Counter()
    for path in v97files:
        doc=json.loads(Path(path).read_text())
        if doc.get('analysis')!='V97_INDEPENDENT_2018_UHSLC_TIDE_SOLAR_ORIGINAL_HOURLY_HOLDOUT' or doc.get('year')!=2018:
            raise ValueError('STOP 2018 external physical source frame mismatch')
        b=doc['band']
        if b not in BANDS_2019 or b in actualband:raise ValueError('STOP duplicate/unknown 2018 latitude band')
        actualband.add(b)
        allowed={s['uid']:s for s in byband[b]['raw_station_outcomes']}
        if doc['original_preselected_2019_source_eligible_site_n']!=len(allowed):
            raise ValueError('STOP 2018 external station candidate source changed')
        if doc['summary']['2019_original_source_site_n']!=len(allowed) or (len(doc['site_outputs'])+len(doc['source_quality_not_admitted'])+len(doc['source_failures']))!=len(allowed):
            raise ValueError('STOP incomplete 2018 original source quality accounting')
        source_failure[b]=len(doc['source_failures']);year_qc[b]=len(doc['source_quality_not_admitted'])
        for row in doc['site_outputs']:
            uid=row['uid']
            if uid not in allowed or uid in real2018:raise ValueError('STOP 2018 original gauge identity duplicate or not in 2019 candidate frame')
            original=allowed[uid]
            if row['2019_record_id']!=original['record_id'] or abs(row['2019_form_factor_F']-original['form_factor_F'])>1e-10:
                raise ValueError('STOP original UHSLC datum source or fossil 2019 tide-form factor changed')
            outcome=row['2018_physical']
            if outcome.get('status')!='VALID_2018_ORIGINAL_DAILY_TIDE_SOLAR_OPPORTUNITY':
                raise ValueError('STOP qualified 2018 physical outcome not valid')
            real2018[uid]=row
    if actualband!=BANDS_2019:
        raise ValueError('STOP eight required independent 2018 original bands not represented')
    return source,real2018,counts,dict(source_failure),dict(year_qc)

def features_row(group,paired_only=False):
    rows=[s for s in group]
    if not rows:raise ValueError('empty source cluster')
    out={'abs_lat':mean(abs(x['latitude']) for x in rows),
        'hemisphere':int(mean(x['latitude'] for x in rows)>=0),
        'amp_4_const_mm':mean(sum(x['harmonics_mm'].values()) for x in rows),
        'F_mean':mean(x['form_factor_F'] for x in rows),
        'Y_2019_original':mean(x['opportunity']['mean_daily_abs_M'] for x in rows)}
    bands=Counter(_latitude_band(s['latitude']) for s in rows)
    out['band']=sorted(bands,key=lambda b:(-bands[b],b))[0]
    return out

def evaluate_heldout_geography_year(source_groups,valid2018):
    train_rows=[features_row(g) for g in source_groups]
    tests=[]
    for group in source_groups:
        matched=[s for s in group if s['uid'] in valid2018]
        if not matched:continue
        test=features_row(matched)
        test['Y_2018_original']=mean(
           valid2018[s['uid']]['2018_physical']['2018_mean_daily_abs_M'] for s in matched)
        test['n2018_same_datum_gauges']=len(matched)
        tests.append(test)
    if len(tests)<25: return {'source_gate':'NO_CROSS_YEAR_REGIONAL_SUPPORT_LT25','n_2018_geo_clusters':len(tests)}
    errors=[]; byband={}
    for b in sorted(set(t['band'] for t in tests)):
        train=[t for t in train_rows if t['band']!=b]
        test=[t for t in tests if t['band']==b]
        if len(train)<30:continue
        ytrain=np.asarray([x['Y_2019_original'] for x in train])
        ytest=np.asarray([x['Y_2018_original'] for x in test])
        pred0=ridge_predict(features(train,False),ytrain,features(test,False))
        pred1=ridge_predict(features(train,True),ytrain,features(test,True))
        ysite=np.asarray([x['Y_2019_original'] for x in test])
        vals=[]
        for z in range(len(test)):
            vals.append({'band':b,'err0':(pred0[z]-ytest[z])**2,
                    'err1':(pred1[z]-ytest[z])**2,'err_persistence':(ysite[z]-ytest[z])**2,
                    'pred0':float(pred0[z]),'pred1':float(pred1[z]),
                    'Y_2018':float(ytest[z]),'Y_2019':float(ysite[z])})
        byband[b]={'n_test_100km_clusters':len(test),
             'M0_mse':float(np.mean([x['err0'] for x in vals])),
             'M1_mse':float(np.mean([x['err1'] for x in vals])),
             'M_same_source_2019_persistence_mse':float(np.mean([x['err_persistence'] for x in vals]))}
        errors.extend(vals)
    if len(errors)<25:return {'source_gate':'NO_CROSS_YEAR_REGIONAL_SCORE_LT25','n_2018_geo_clusters':len(tests)}
    err0=np.array([x['err0'] for x in errors]);err1=np.array([x['err1'] for x in errors])
    errp=np.array([x['err_persistence'] for x in errors])
    improvement=err0-err1
    rng=np.random.default_rng(SEED)
    n=len(errors)
    idx=rng.integers(0,n,size=(N_RESAMPLE,n))
    ci=np.quantile(improvement[idx].mean(axis=1),[.025,.975]).tolist()
    mse0=float(np.mean(err0));mse1=float(np.mean(err1))
    return {'source_gate':'INDEPENDENT_2018_CALENDAR_YEAR_AND_UNSEEN_GEO_BANDS_EVALUATED',
       'assessment':'FIT_2019_NONTEST_15DEG_BAND_STATIONS_SCORE_2018_UNSEEN_BAND_ORIGINAL_HOURLY_GAUGES',
       'predictor_features_2019_original_and_2018_unseen':True,
       '2018_hourly_waterheights_never_used_in_training':True,
       'n_2018_heldout_geo_clusters':len(errors),
       'n_2018_admitted_original_sites':len(valid2018),
       'n_test_latitude_bands':len(byband),
       'M0_beyond_tidal_form':{'features':['2019_abs_lat','hemisphere','2019_harmonic_amplitude_mm'],
             'MSE':mse0},
       'M1_plus_tidal_form':{'features':['2019_abs_lat','hemisphere','2019_harmonic_amplitude_mm','2019_log1p_tidal_form_factor_F'],
             'MSE':mse1},
       'M0_minus_M1_gain':float(np.mean(improvement)),
       'relative_MSE_reduction_pct':100*(mse0-mse1)/mse0,
       '95CI_conditional_fixed_prediction_geo_cluster_resampling':ci,
       'n_coastal_clusters_positive_M0_minus_M1_gain':int(np.sum(improvement>0)),
       'benchmark_same_site_2019_environmental_persistence_MSE':float(np.mean(errp)),
       'matched_stations_site_opportunity_2019_versus_2018_spearman':spearman(
             [x['Y_2019'] for x in errors],[x['Y_2018'] for x in errors]),
       'band_outcome_2018':byband,
       'source_and_scientific_boundary':'not prospective chronology: 2018 is earlier than 2019 training, but an untouched external CALENDAR YEAR and geographic band; still pure physical gauge/coincidence, not animal temporal-niche behavior'}
def run(v94dir,v97dir,outfile):
    a=list(Path(v94dir).rglob('v94-2019-original-source-*.json'))
    b=list(Path(v97dir).rglob('v97-original-UHSLC-2018-*.json'))
    original,holdout,counts,failures,qc=source_census(a,b)
    groups=coastal_clusters(original)
    result=evaluate_heldout_geography_year(groups,holdout)
    out={'analysis':'V98_INDEPENDENT_2018_YEAR_AND_2019_UNSEEN_15DEG_GEO_BAND_HOURLY_UHSLC_PHYSICAL_TRANSFER',
      'frozen_2019_original_source_gauge_run':V94_RUN,
      'independent_2018_original_source_year_run':V97_RUN,
      '2019_candidates':counts,'2018_eligible_original_gauges':len(holdout),
      '2018_source_failure_by_band':failures,'2018_source_QC_failure_by_band':qc,
      'original_2019_100km_coastal_clusters':len(groups),
      'primary_2018_unseen_year_and_region':result,
      'do_not_claim':'NO observed animal activity, habitat exposure, temporal niche, prey, or internal circadian clocks; post-v95 new year checked independently'}
    Path(outfile).parent.mkdir(parents=True,exist_ok=True)
    Path(outfile).write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V98_REAL_2018_2019_CROSSYEAR_REGION '+json.dumps(out,sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--v94-dir',required=True)
    a.add_argument('--v97-dir',required=True)
    a.add_argument('--output',required=True)
    x=a.parse_args();run(x.v94_dir,x.v97_dir,x.output)
