"""Load original GPS/RWS sources once, replay local rules, transfer between islands."""
from __future__ import annotations
import argparse,json,os,tempfile
from copy import deepcopy
from pathlib import Path
import numpy as np
from angular_phase_control import attach_yearago_phase,replace_phase,summarize_models
from run_phase_control_transfer import check_manifest,merge_gauges
from run_bearing_audit import check_replay
from cross_island_transfer import evaluate_transfer

BASE_COMMIT='52402d646634566c1f4f171d6ee1da5cde2212a9'
STATIONS={'ameland':'ameland.nes','schiermonnikoog':'schiermonnikoog.waddenzee'}


def transfer_pairs():
    return (('schiermonnikoog','ameland'),('ameland','schiermonnikoog'))


def gauge_count(year,metadata):
    if year not in (2009,2010,2011) or metadata.get('gauge_rows')!=52561:
        raise ValueError('SOURCE_STOP_ORIGINAL_GAUGE_YEAR_OR_COUNT')
    return 52561


def compact_metrics(metric):
    keys=('n_rows','n_birds','n_weeks','equal_bird','equal_week_then_bird')
    return {key:deepcopy(metric[key]) for key in keys}


def load_site(site):
    from source_preflight import download_and_pin
    from ameland_external_site import original_gps
    from source_fetch_resilience import observed_rws_year
    from tidal_front import TideSeries
    from original_heading_tide import original_three_fix_heading_episodes,forecast
    if site not in STATIONS:raise ValueError('Unfrozen island')
    water={};receipt={}
    for year in (2009,2010,2011):
        tide,meta=observed_rws_year(STATIONS[site],year)
        receipt[str(year)]={'RWS_original_NAP_count':gauge_count(year,meta),
                            'original_station':STATIONS[site]}
        water[year]=tide
    history,hqa=merge_gauges(water,TideSeries)
    data={};joins={}
    with tempfile.TemporaryDirectory(prefix='boids_v56_original_') as root:
        for year in (2010,2011):
            path=Path(root)/f'{site}_{year}.gz'
            manifest=download_and_pin(year,path) if site=='schiermonnikoog' else original_gps(year,path)
            check_manifest(manifest,site,year)
            raw,qa=original_three_fix_heading_episodes(path,water[year],site,clock_shift_s=0)
            data[year],joins[str(year)]=attach_yearago_phase(raw,history)
            if joins[str(year)]['removed_missing_history']:
                raise ValueError('SOURCE_STOP_HISTORICAL_JOIN_CHANGED_ORIGINAL_COHORT')
            receipt[str(year)].update(original_GPS_MD5_and_SHA256_verified=True,
                                      original_GPS_SHA256=manifest['original_sha256'],
                                      original_three_fix_QA=qa)
            path.unlink(missing_ok=True)
    train,test=data[2010],data[2011]
    p0=forecast(train,test,0);pa=forecast(train,test,1)
    pg=forecast(replace_phase(train),replace_phase(test),1)
    truth=np.asarray([[r['target_e'],r['target_n']] for r in test])
    replay=check_replay(test,truth,p0,pa,site=site,train_count=len(train))
    old=summarize_models(test,truth,{'M0':p0,'Mactual':pa,'M365':pg})
    audit={'original_receipts':receipt,'history_gauge_merge':hqa,'history_joins':joins,
           'known_full_within_site_vector_replay':replay,
           'known_within_site_2010_2011_angular_metrics':compact_metrics(old)}
    return data,audit


def run(output):
    from original_heading_tide import forecast
    data={};audits={}
    for site in ('schiermonnikoog','ameland'):
        data[site],audits[site]=load_site(site)
        print('V56_SOURCE_REPLAY_OK '+site,flush=True)
    outcomes={}
    for source,target in transfer_pairs():
        result=evaluate_transfer(data[source][2010],data[target][2010],data[target][2011],forecast)
        result.update(source_island=source,target_island=target,training_year=2010,test_year=2011)
        outcomes[source+'_to_'+target]=result
    report={'analysis':'V56_ORIGINAL_RECIPROCAL_ISLAND_AND_YEAR_BEARING_TRANSFER',
            'executed_commit':os.environ.get('GITHUB_SHA','local'),'base_commit':BASE_COMMIT,
            'primary_transfer':'schiermonnikoog_to_ameland','primary_condition':'translated',
            'source_audits':audits,'transfers':outcomes,
            'limits':'Post-v55 exploratory. Unlabeled target2010 positions used only for translation. Same species/region, not new field population; no actual front or social force.'}
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    # Aggregate-only stdout receipt, complete uncertainty and all contrasts retained.
    summary={'analysis':report['analysis'],'executed_commit':report['executed_commit'],
             'old_within_site_mean_angles':{},'transfers':{}}
    for site,a in audits.items():
        summary['old_within_site_mean_angles'][site]={m:d['absolute_angle_degrees'] for m,d in
            a['known_within_site_2010_2011_angular_metrics']['equal_bird']['model_mean_losses'].items()}
    for key,r in outcomes.items():
        s={k:v for k,v in r.items() if k!='conditions'}
        if 'conditions' in r:
            s['conditions']={}
            for condition,c in r['conditions'].items():
                cc={k:v for k,v in c.items() if k!='metrics'}
                if 'metrics' in c:cc['metrics']=compact_metrics(c['metrics'])
                s['conditions'][condition]=cc
        summary['transfers'][key]=s
    print('V56_AGGREGATE_RESULT '+json.dumps(summary,sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
