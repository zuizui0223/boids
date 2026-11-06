"""Original Ameland fixed-policy transfer / paired years; prior results preserved."""
from __future__ import annotations
import argparse,json,os,tempfile
from pathlib import Path
import numpy as np
from angular_phase_control import attach_yearago_phase,source_admission,summarize_models
from run_phase_control_transfer import check_manifest,merge_gauges,replay_2012_source
from run_bearing_audit import check_replay
from paired_year_diagnostics import forecast_policies,loss_tensor,paired_years,paired_update

BASE_COMMIT='1e256592fb7b20d3fa9184aef0a1436684a9d8b5'
ANGLES={2011:{'M0':75.22439202732221,'Mactual':62.009059594352095,'M365':72.64143235714869},
        2012:{'M0':59.86051001221907,'Mactual':59.8033309479592,'M365':58.90134102050317}}


def check_known_angular(summary,year):
    if year not in ANGLES:raise ValueError('Unfrozen replay year')
    means=summary['equal_bird']['model_mean_losses']
    for model,value in ANGLES[year].items():
        got=float(means[model]['absolute_angle_degrees'])
        if not np.isfinite(got) or abs(got-value)>1e-9:
            raise ValueError('SOURCE_STOP_V53_ANGULAR_REPLAY_DRIFT')
    return True


def run(output):
    from ameland_external_site import original_gps
    from source_gate_2012 import get_ameland_original
    from source_fetch_resilience import observed_rws_year
    from heldout_2012_tidal_lag import original_2012_gauge
    from tidal_front import TideSeries
    from original_heading_tide import original_three_fix_heading_episodes,forecast
    site='ameland';station='ameland.nes'
    gauges={};source={}
    for year in (2009,2010,2011,2012):
        water,meta=(original_2012_gauge(station) if year==2012 else observed_rws_year(station,year))
        expected=52705 if year==2012 else 52561
        if meta['gauge_rows']!=expected:raise ValueError('SOURCE_STOP_ORIGINAL_GAUGE_COUNT_DRIFT')
        gauges[year]=water
        source[str(year)]={'RWS_original_NAP_rows':expected,'original_station':station}
    history,historical_receipt=merge_gauges(gauges,TideSeries)
    data={};joins={}
    with tempfile.TemporaryDirectory(prefix='boids_v54_original_') as directory:
        for year in (2010,2011,2012):
            path=Path(directory)/f'ameland_{year}.csv.gz'
            manifest=get_ameland_original(path) if year==2012 else original_gps(year,path)
            check_manifest(manifest,site,year)
            rows,qa=original_three_fix_heading_episodes(path,gauges[year],site,clock_shift_s=0)
            data[year],joins[str(year)]=attach_yearago_phase(rows,history)
            if joins[str(year)]['removed_missing_history']:
                raise ValueError('SOURCE_STOP_PRIOR_FULL_COHORT_CHANGED_BY_HISTORY_JOIN')
            source[str(year)].update({'GPS_provider_MD5_verified':True,
                                     'original_GPS_SHA256':manifest['original_sha256'],
                                     'original_three_fix_QA':qa})
            path.unlink(missing_ok=True)
    gates={str(y):source_admission(data[2010] if y==2011 else data[2010]+data[2011],data[y],y)
           for y in (2011,2012)}
    if not all(g['admitted'] for g in gates.values()):
        raise ValueError('SOURCE_STOP_ORIGINAL_FULL_YEAR_GATE_NOT_ADMITTED')
    # No parameters are ever fitted on 2012; all 2011 scores below use 2010 only.
    policies=forecast_policies(data[2010],data[2011],data[2012],forecast)
    truth2011=np.asarray([[r['target_e'],r['target_n']] for r in data[2011]])
    replay11=check_replay(data[2011],truth2011,policies['F10'][2011]['M0'],
                          policies['F10'][2011]['Mactual'],site=site,train_count=len(data[2010]))
    replay12=replay_2012_source(data[2010]+data[2011],data[2012],site,forecast)
    summaries={}
    for name,by_year in policies.items():
        summaries[name]={}
        for year,pred in by_year.items():
            truth=np.asarray([[r['target_e'],r['target_n']] for r in data[year]])
            summaries[name][str(year)]=summarize_models(data[year],truth,pred)
    check_known_angular(summaries['F10']['2011'],2011)
    check_known_angular(summaries['F1011']['2012'],2012)
    rows={y:data[y] for y in (2011,2012)}
    fixed_losses={y:loss_tensor(data[y],policies['F10'][y]) for y in (2011,2012)}
    updated_losses=loss_tensor(data[2012],policies['F1011'][2012])
    results={'fixed_2010_shared_identities':paired_years(rows,fixed_losses),
             'fixed_2010_shared_identities_and_months':paired_years(rows,fixed_losses,month_matched=True),
             'same_2012_test_training_update':paired_update(data[2012],fixed_losses[2012],updated_losses)}
    report={'analysis':'V54_FIXED_2010_POLICY_PAIRED_IDENTITIES_2011_2012',
            'site':site,'executed_commit':os.environ.get('GITHUB_SHA','local'),
            'base_commit':BASE_COMMIT,'source_receipts':source,
            'original_history_merge':historical_receipt,'same_source_history_joins':joins,
            'original_full_year_gates':gates,'original_v52_2011_vector_replay':replay11,
            'original_v41_2012_vector_replay':replay12,
            'v53_2011_and_updated2012_angular_replay_verified':True,
            'whole_cohort_policies':summaries,'paired_diagnostics':results,
            'scope':'Ameland only; Schier 2012 869 original episodes remains NOT_ADMITTED',
            'limits':['post-v53 exploratory, same historical species and source',
                      'native GPS clock provisionally UTC, unverified',
                      'source identity strings, not independent biological recapture adjudication',
                      'few paired identities; bootstrap conditional, not independent ecology populations',
                      'calendar matching is not full environment/route/activity matching',
                      'training and cohort contrasts are not an additive causal decomposition']}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(run(a.output),sort_keys=True))
