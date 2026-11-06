"""Replay original tidal next-vector forecasts; audit bearing versus magnitude.

No terrain, additional predictors, model tuning, or social-force estimates.
Original tracks and bird identifiers remain on the ephemeral source runner.
"""
from __future__ import annotations
import argparse, json, os, tempfile
from collections import defaultdict
from pathlib import Path
import numpy as np
from bearing_decomposition import decompose_predictions, summarize_rows, UndefinedBearing

BASE_COMMIT='23290eb35e1945265d6b85235708c105fbdd5bed'
REF={
    'schiermonnikoog':(7911,4948,13,.4491437063035975,.41370693859833235),
    'ameland':(3753,4678,5,.5107931836556263,.43464618382116776),
}
SHA={
    ('schiermonnikoog',2010):'8d7d0ac9cef0935e7351bcf9a525c0f9eeb7605dc603d227f9b09744dadd532d',
    ('schiermonnikoog',2011):'297938bade48ca5502a4325105a64f0d6e0124a268bbcf2caa49676449f7946f',
    ('ameland',2010):'c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c',
    ('ameland',2011):'f1fe4bc16eb8081ab0073326e3494af0ed4798a6044db3327b3fd0dcf9559875',
}

def require_original(manifest,site,year):
    verified=manifest.get('provider_md5_match',manifest.get('provider_original_md5_matched'))
    if verified is not True or manifest.get('original_sha256')!=SHA[(site,year)]:
        raise ValueError('SOURCE_STOP_ORIGINAL_GPS_HASH_OR_PROVIDER_CHECK_DRIFT')
    return True

def check_replay(rows, truth, p0, p1, *, site, train_count):
    if site not in REF: raise ValueError('Unfrozen site')
    nt,n,nb,ref0,ref1=REF[site]
    if train_count!=nt or len(rows)!=n or any(r['t'].year!=2011 for r in rows):
        raise ValueError('SOURCE_STOP_ORIGINAL_V43_YEAR_OR_COUNT_DRIFT')
    y,a,b=[np.asarray(x,dtype=float) for x in (truth,p0,p1)]
    if any(x.shape!=(n,2) or not np.isfinite(x).all() for x in (y,a,b)):
        raise ValueError('SOURCE_STOP_ORIGINAL_FORECAST_SHAPE_OR_FINITE')
    birds=defaultdict(list)
    for i,r in enumerate(rows): birds[r['id']].append(i)
    errors0=.5*np.square(y-a).sum(1)
    errors1=.5*np.square(y-b).sum(1)
    m0=float(np.mean([np.mean(errors0[ix]) for ix in birds.values()]))
    m1=float(np.mean([np.mean(errors1[ix]) for ix in birds.values()]))
    if len(birds)!=nb or abs(m0-ref0)>1e-9 or abs(m1-ref1)>1e-9:
        raise ValueError('SOURCE_STOP_ORIGINAL_V43_FULL_FORECAST_NOT_REPLAYED')
    return {'original_v43_replay_verified':True,'training_rows':nt,'test_rows':n,
            'test_birds':nb,'M0_equal_bird_vector_half_MSE':m0,
            'M1_equal_bird_vector_half_MSE':m1}

def run(site,output):
    # Source-dependent imports are lazy so pure tests never need network/legacy modules.
    from source_preflight import download_and_pin
    from ameland_external_site import original_gps
    from source_fetch_resilience import observed_rws_year
    from original_heading_tide import original_three_fix_heading_episodes, forecast
    if site not in REF: raise ValueError('Unfrozen site')
    station={'schiermonnikoog':'schiermonnikoog.waddenzee','ameland':'ameland.nes'}[site]
    data={};receipt={}
    with tempfile.TemporaryDirectory(prefix='boids_v52_original_') as folder:
        for year in (2010,2011):
            file=Path(folder)/f'{site}_{year}.csv.gz'
            manifest=download_and_pin(year,file) if site=='schiermonnikoog' else original_gps(year,file)
            require_original(manifest,site,year)
            tide,gauge=observed_rws_year(station,year)
            if gauge['gauge_rows']!=52561:
                raise ValueError('SOURCE_STOP_ORIGINAL_RWS_ANNUAL_COVERAGE_DRIFT')
            data[year],qa=original_three_fix_heading_episodes(file,tide,site,clock_shift_s=0)
            if any(r['t'].year!=year for r in data[year]):
                raise ValueError('SOURCE_STOP_GPS_YEAR_SPLIT')
            receipt[str(year)]={'GPS_provider_MD5_verified':True,
                'GPS_original_SHA256':manifest['original_sha256'],
                'original_RWS_station':station,'RWS_measured_NAP_rows':gauge['gauge_rows'],
                'source_three_fix_audit':qa}
            file.unlink(missing_ok=True)
    train,test=data[2010],data[2011]
    truth=np.asarray([[r['target_e'],r['target_n']] for r in test])
    p0,p1=forecast(train,test,0),forecast(train,test,1)
    replay=check_replay(test,truth,p0,p1,site=site,train_count=len(train))
    try:
        losses=decompose_predictions(truth,p0,p1)
        angular=summarize_rows(test,losses)
        status='OBSERVED_ANGULAR_FORECAST_AND_EXACT_VECTOR_LOSS_DECOMPOSITION'
    except UndefinedBearing as error:
        status='NOT_ADMITTED_UNDEFINED_BEARING'
        angular={'reason':str(error),'no_source_rows_dropped':True}
    result={'analysis':'V52_ORIGINAL_TIDAL_BEARING_VS_VECTOR_MAGNITUDE','site':site,
        'base_commit':BASE_COMMIT,'executed_commit':os.environ.get('GITHUB_SHA','local'),
        'status':status,'evidence_status':'POST_V51_EXPLORATORY_SAME_HISTORICAL_COHORT',
        'full_original_v43_replay':replay,'original_source_receipts':receipt,
        'angular_and_magnitude_results':angular,
        'source_GPS_clock':'NATIVE_PROVISIONALLY_UTC_UNVERIFIED',
        'biological_limits':'No physical acceleration, local exposure front, prey or social force identified'}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--site',choices=tuple(REF),required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    print(json.dumps(run(a.site,a.output),sort_keys=True))
