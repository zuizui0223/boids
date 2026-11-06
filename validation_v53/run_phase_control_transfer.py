"""Authentic-source v53 angular phase control and fixed 2012 temporal transfer.

Existing parsers, original forecasting functions and historical source helpers
are imported only in run(). No raw bird or tide observations are persisted.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,tempfile
from collections import defaultdict
from pathlib import Path
import numpy as np
from angular_phase_control import (attach_yearago_phase,replace_phase,
                                   source_admission,summarize_models)
from bearing_decomposition import UndefinedBearing
from run_bearing_audit import check_replay,require_original

BASE_COMMIT='459a40eefca981ba92551997fdfe074b6bee3775'
STATIONS={'ameland':'ameland.nes','schiermonnikoog':'schiermonnikoog.waddenzee'}
SHA2012={
 'ameland':'0b4d53cbe12437150425e7a36461485fe9d9e61b50486cf162aba3fbdb874c7a',
 'schiermonnikoog':'f9935a50a9b557795ecf38ebd77890f52566b8e9d6c5a6650b46b18b6cb6d3d0'}
SOURCE2012={'ameland':(8431,1186,3,50), 'schiermonnikoog':(12859,869,5,35)}


def check_manifest(manifest,site,year):
    if site not in STATIONS:raise ValueError('Unfrozen source site')
    if year in (2010,2011):return require_original(manifest,site,year)
    if year!=2012:raise ValueError('Unfrozen GPS source year')
    verified=manifest.get('provider_md5_match',manifest.get('provider_original_md5_matched'))
    if verified is not True or manifest.get('original_sha256')!=SHA2012[site]:
        raise ValueError('SOURCE_STOP_ORIGINAL_2012_GPS_HASH_OR_MD5_DRIFT')
    return True


def merge_gauges(gauges,factory):
    """Join real gauge years for fixed-duration history lookup across leap dates."""
    values={};duplicates=0
    for year in sorted(gauges):
        g=gauges[year]
        if len(g.times)!=len(g.heights):raise ValueError('SOURCE_GAUGE_ALIGNMENT')
        for t,h in zip(g.times,g.heights):
            if t.tzinfo is None or t.utcoffset() is None or not math.isfinite(float(h)):
                raise ValueError('SOURCE_GAUGE_INVALID_TIME_OR_HEIGHT')
            if t in values:
                duplicates+=1
                if abs(values[t]-float(h))>1e-9:
                    raise ValueError('SOURCE_STOP_GAUGE_BOUNDARY_CONFLICT')
            values[t]=float(h)
    if not values:raise ValueError('SOURCE_GAUGE_EMPTY')
    pairs=sorted(values.items())
    digest=hashlib.sha256()
    for t,h in pairs:digest.update((t.isoformat()+' '+float(h).hex()+'\n').encode())
    return factory(pairs,datum='NAP_m',provenance='observed'),{
        'merged_original_gauge_rows':len(pairs),
        'source_duplicate_boundaries_checked':duplicates,
        'canonical_merged_gauge_SHA256':digest.hexdigest(),
        'purpose':'Only genuine t-minus-365-day source lookup; true source cohorts unchanged'}


def compare_year(train,test,year,forecast_fn,*,bird_draws=10000,week_draws=4000):
    gate=source_admission(train,test,year)
    if not gate['admitted']:
        return {'status':'NOT_ADMITTED_SOURCE_SUPPORT','source_admission':gate,
                'outcome':'NOT_ESTIMATED'}
    p0=forecast_fn(train,test,0)
    pa=forecast_fn(train,test,1)
    pg=forecast_fn(replace_phase(train),replace_phase(test),1)
    truth=np.asarray([[r['target_e'],r['target_n']] for r in test])
    try:
        metrics=summarize_models(test,truth,{'M0':p0,'Mactual':pa,'M365':pg},
                                 bird_draws=bird_draws,week_draws=week_draws)
    except UndefinedBearing as error:
        return {'status':'NOT_ADMITTED_UNDEFINED_BEARING','source_admission':gate,
                'reason':str(error),'no_source_rows_dropped':True}
    return {'status':'OBSERVED_ANGULAR_PHASE_CONTROL','source_admission':gate,
            'metrics':metrics}


def replay_2012_source(train,test,site,forecast_fn):
    nt,n,nb,nw=SOURCE2012[site]
    groups=defaultdict(list)
    for i,r in enumerate(test):
        if r['t'].year!=2012:raise ValueError('SOURCE_STOP_2012_YEAR_DRIFT')
        groups[r['id']].append(i)
    if (len(train),len(test),len(groups),len({r['t'].isocalendar()[:2] for r in test}))!=(nt,n,nb,nw):
        raise ValueError('SOURCE_STOP_2012_ORIGINAL_DIRECTION_COHORT_DRIFT')
    receipt={'original_2012_source_counts_replayed':True,'train_rows':nt,
             'test_rows':n,'test_birds':nb,'test_weeks':nw}
    if n<1000:
        receipt['status']='NOT_ADMITTED_SOURCE_COUNTS_ONLY_NO_2012_MODEL_FIT'
        return receipt
    truth=np.asarray([[r['target_e'],r['target_n']] for r in test])
    mse=[]
    for level in (0,1):
        error=.5*np.square(truth-forecast_fn(train,test,level)).sum(1)
        mse.append(float(np.mean([np.mean(error[ix]) for ix in groups.values()])))
    if not np.allclose(mse,[.4389851852,.4101246782],atol=1e-9,rtol=0.):
        raise ValueError('SOURCE_STOP_ORIGINAL_V41_2012_AMELAND_PREDICTION_DRIFT')
    receipt['original_v41_2012_vector_replay_verified']=True
    receipt['M0_Mactual_equal_bird_vector_half_MSE']=mse
    return receipt


def run(site,output):
    from source_preflight import download_and_pin
    from source_gate_2012 import get_ameland_original
    from ameland_external_site import original_gps
    from source_fetch_resilience import observed_rws_year
    from heldout_2012_tidal_lag import original_2012_gauge
    from tidal_front import TideSeries
    from original_heading_tide import original_three_fix_heading_episodes,forecast
    if site not in STATIONS:raise ValueError('Unfrozen source site')
    station=STATIONS[site]
    water={};sources={}
    for year in (2009,2010,2011,2012):
        tide,meta=(original_2012_gauge(station) if year==2012 else observed_rws_year(station,year))
        expected=52705 if year==2012 else 52561
        if meta['gauge_rows']!=expected:raise ValueError('SOURCE_STOP_RWS_GAUGE_COUNT_DRIFT')
        water[year]=tide
        sources[str(year)]={'RWS_measured_NAP_rows':meta['gauge_rows'],'original_station':station}
    history,history_receipt=merge_gauges(water,TideSeries)
    data={}
    with tempfile.TemporaryDirectory(prefix='boids_v53_original_') as folder:
        for year in (2010,2011,2012):
            path=Path(folder)/f'{site}_{year}.csv.gz'
            manifest=(download_and_pin(year,path) if site=='schiermonnikoog' else
                      get_ameland_original(path) if year==2012 else original_gps(year,path))
            check_manifest(manifest,site,year)
            rows,qa=original_three_fix_heading_episodes(path,water[year],site,clock_shift_s=0)
            if any(r['t'].year!=year for r in rows):raise ValueError('SOURCE_STOP_GPS_YEAR_DRIFT')
            data[year]=rows
            sources[str(year)].update({'GPS_provider_MD5_verified':True,
                'original_GPS_SHA256':manifest['original_sha256'],'original_three_fix_QA':qa})
            path.unlink(missing_ok=True)
    y=np.asarray([[r['target_e'],r['target_n']] for r in data[2011]])
    old=check_replay(data[2011],y,forecast(data[2010],data[2011],0),
                     forecast(data[2010],data[2011],1),site=site,train_count=len(data[2010]))
    old2012=replay_2012_source(data[2010]+data[2011],data[2012],site,forecast)
    common={};support={}
    for year in (2010,2011,2012):
        common[year],support[str(year)]=attach_yearago_phase(data[year],history)
    results={
        'train_2010_test_2011':compare_year(common[2010],common[2011],2011,forecast),
        'train_2010_2011_test_2012':compare_year(common[2010]+common[2011],common[2012],2012,forecast)}
    result={'analysis':'V53_ORIGINAL_ANGULAR_REAL_VS_365DAY_PHASE_AND_2012_TRANSFER',
        'site':site,'base_commit':BASE_COMMIT,'executed_commit':os.environ.get('GITHUB_SHA','local'),
        'evidence':'POST_V52_EXPLORATORY_SAME_HISTORICAL_COHORTS',
        'original_source_receipts':sources,'historical_gauge_merge_receipt':history_receipt,
        'original_v52_full_2011_replay':old,'original_v41_2012_replay':old2012,
        'common_source_phase_support':support,'outcomes':results,
        'source_clock':'NATIVE_PROVISIONALLY_UTC_UNVERIFIED',
        'limits':'One fixed-duration historical phase control; no causal front, food or social force; few 2012 birds'}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--site',choices=tuple(STATIONS),required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.site,args.output),sort_keys=True))
