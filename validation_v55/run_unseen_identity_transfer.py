"""Original-source v55 identity-disjoint, year-held-out angular tide prediction."""
from __future__ import annotations
import argparse,json,math,os,tempfile
from pathlib import Path
import numpy as np
from angular_phase_control import attach_yearago_phase,summarize_models
from run_phase_control_transfer import check_manifest,merge_gauges
from run_bearing_audit import check_replay
from unseen_identity_transfer import forecast_fixed,evaluate_transfer

BASE_COMMIT='09e6e28ef9c6c0b3e59cb1490cacfc22c6f58a7c'
STATIONS={'ameland':'ameland.nes','schiermonnikoog':'schiermonnikoog.waddenzee'}
FIXED_2012={'M0':69.62997611500825,'Mactual':59.66726851878847,'M365':67.34326266351121}


def source_years(site):
    if site not in STATIONS:raise ValueError('Unfrozen original site')
    return (2010,2011,2012) if site=='ameland' else (2010,2011)


def check_gauge_count(year,metadata):
    if year not in (2009,2010,2011,2012):raise ValueError('Unfrozen gauge year')
    expected=52705 if year==2012 else 52561
    if metadata.get('gauge_rows')!=expected:raise ValueError('SOURCE_STOP_ORIGINAL_GAUGE_COUNT_DRIFT')
    return expected


def check_fixed2012_replay(summary):
    if summary['n_rows']!=1186 or summary['n_birds']!=3:
        raise ValueError('SOURCE_STOP_V54_FIXED2012_COUNTS_CHANGED')
    for model,expected in FIXED_2012.items():
        got=float(summary['equal_bird']['model_mean_losses'][model]['absolute_angle_degrees'])
        if not math.isfinite(got) or abs(got-expected)>1e-9:
            raise ValueError('SOURCE_STOP_V54_FIXED2012_ANGULAR_DRIFT')
    return True


def run(site,output):
    from source_preflight import download_and_pin
    from ameland_external_site import original_gps
    from source_gate_2012 import get_ameland_original
    from source_fetch_resilience import observed_rws_year
    from heldout_2012_tidal_lag import original_2012_gauge
    from tidal_front import TideSeries
    from original_heading_tide import original_three_fix_heading_episodes,forecast
    years=source_years(site);station=STATIONS[site]
    gauges={};sources={}
    for year in (2009,)+years:
        tide,meta=original_2012_gauge(station) if year==2012 else observed_rws_year(station,year)
        count=check_gauge_count(year,meta)
        gauges[year]=tide
        sources[str(year)]={'original_RWS_NAP_rows':count,'original_station':station}
    history,hreceipt=merge_gauges(gauges,TideSeries)
    data={};joins={}
    with tempfile.TemporaryDirectory(prefix='boids_v55_original_') as folder:
        for year in years:
            path=Path(folder)/f'{site}_{year}.csv.gz'
            manifest=(download_and_pin(year,path) if site=='schiermonnikoog' else
                      get_ameland_original(path) if year==2012 else original_gps(year,path))
            check_manifest(manifest,site,year)
            rows,qa=original_three_fix_heading_episodes(path,gauges[year],site,clock_shift_s=0)
            data[year],joins[str(year)]=attach_yearago_phase(rows,history)
            if joins[str(year)]['removed_missing_history']:
                raise ValueError('SOURCE_STOP_ORIGINAL_FULL_ROWS_CHANGED_BY_HISTORY_JOIN')
            sources[str(year)].update({'original_GPS_MD5_and_SHA256_verified':True,
                                      'original_GPS_SHA256':manifest['original_sha256'],
                                      'original_three_fix_source_QA':qa})
            path.unlink(missing_ok=True)
    tests={year:data[year] for year in years if year!=2010}
    # Known all-identity models are replayed first; not new holdout findings.
    old=forecast_fixed(data[2010],tests,forecast)
    truth11=np.asarray([[r['target_e'],r['target_n']] for r in data[2011]])
    replay=check_replay(data[2011],truth11,old[2011]['M0'],old[2011]['Mactual'],
                        site=site,train_count=len(data[2010]))
    known={}
    for year,rows in tests.items():
        truth=np.asarray([[r['target_e'],r['target_n']] for r in rows])
        known[str(year)]=summarize_models(rows,truth,old[year])
    replay12=check_fixed2012_replay(known['2012']) if site=='ameland' else None
    strict=evaluate_transfer(data[2010],tests,forecast)
    report={'analysis':'V55_ORIGINAL_UNSEEN_IDENTITIES_AND_YEAR_ANGULAR_TIDE_TRANSFER',
            'site':site,'base_commit':BASE_COMMIT,'executed_commit':os.environ.get('GITHUB_SHA','local'),
            'source_receipts':sources,'source_history_merge':hreceipt,'original_history_joins':joins,
            'old_2011_full_source_vector_replay':replay,
            'old_v54_fixed2010_on_2012_angular_replay':replay12,
            'known_all_identity_2010_policy':known,'identity_disjoint_validation':strict,
            'status_scope':'post-v54 exploratory original-source identity block, not new population',
            'source_clock':'native provisionally UTC, GPS time standard unresolved',
            'no_raw_individuals_positions_or_tide_records_exported':True}
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--site',choices=tuple(STATIONS),required=True)
    p.add_argument('--output',required=True);a=p.parse_args()
    print(json.dumps(run(a.site,a.output),sort_keys=True))
