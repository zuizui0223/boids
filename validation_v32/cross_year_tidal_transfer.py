"""V32: independent-year transfer of the *observed* tide-phase signal.

Original Zenodo GPS 2009-2011 (provider-MD5 pinned per annual gzip) and RWS
Schiermonnikoog Waddenzee measured WATHTE, cm/NAP, fixed UTC+01. Study-clock
uncertainty is explicit: naive GPS clock interpreted as UTC or GPS(-15s).
No DEM, local shoreline tidal lag, prey, Boids forces or causal interpretation.
"""
from __future__ import annotations
import argparse, json, tempfile
from collections import defaultdict
from pathlib import Path
import numpy as np
from source_preflight import download_and_pin
from observed_phase import (real_rws_tide, gps_hourly_steps,
                            predict, same_height_hysteresis)

def _score(train, test):
    if len(train)<1000 or len(test)<1000:raise ValueError('Few observation steps')
    targets=np.asarray([x['response'] for x in test])
    p0=predict(train,test,0)
    p1=predict(train,test,1)
    e0=(targets-p0)**2;e1=(targets-p1)**2
    per_bird=defaultdict(list);per_week=defaultdict(list)
    for i, r in enumerate(test):
        per_bird[r['id']].append(i)
        per_week[(r['t'].isocalendar().year,r['t'].isocalendar().week)].append(i)
    bird_diffs=[];bird_scores=[];week_diffs=[]
    for bird,ix in per_bird.items():
        m0=float(np.mean(e0[ix]));m1=float(np.mean(e1[ix]))
        bird_scores.append((m0,m1));bird_diffs.append(m0-m1)
    for ix in per_week.values():
        ix_by_bird=defaultdict(list)
        for i in ix:ix_by_bird[test[i]['id']].append(i)
        week_diffs.append(float(np.mean([np.mean(e0[j]-e1[j]) for j in ix_by_bird.values()])))
    m0=float(np.mean([x[0] for x in bird_scores]))
    m1=float(np.mean([x[1] for x in bird_scores]))
    rng=np.random.default_rng(20261102)
    bird_boot=rng.choice(bird_diffs,size=(4000,len(bird_diffs)),replace=True).mean(axis=1)
    week_boot=rng.choice(week_diffs,size=(4000,len(week_diffs)),replace=True).mean(axis=1)
    return {
      'n_train_steps':len(train), 'n_test_steps':len(test),
      'n_heldout_birds':len(per_bird), 'n_heldout_weeks':len(per_week),
      'M0_equal_bird_MSE':m0, 'M1_equal_bird_MSE':m1,
      'M0_minus_M1_gain':m0-m1,
      'percent_gain':100*(m0-m1)/m0,
      'birds_positive':sum(x>0 for x in bird_diffs),
      'weeks_positive':sum(x>0 for x in week_diffs),
      'bird_bootstrap_95':np.quantile(bird_boot,[.025,.975]).tolist(),
      'week_bootstrap_95':np.quantile(week_boot,[.025,.975]).tolist(),
      'mean_week_gain':float(np.mean(week_diffs)),
      'claim':'Observed cross-year temporal transfer conditional on source clock and proxy gauge; no causal front or social inference'
    }

def run(output, *, years=(2009,2010,2011), clock_shifts=(0,-15)):
    if tuple(years)!=(2009,2010,2011):
        raise ValueError('V32 original admission pre-frozen to 2009-2011')
    source={}
    data={}
    with tempfile.TemporaryDirectory() as folder:
        for year in years:
            gz=Path(folder)/f'{year}.csv.gz'
            pin=download_and_pin(year,gz)
            tide,gauge=real_rws_tide(year)
            source[str(year)]={'GPS_provider_manifest':pin,'RWS_measured_NAP_audit':gauge}
            data[year]={}
            for clock in clock_shifts:
                rows,audit=gps_hourly_steps(gz,tide,clock_shift_s=clock)
                if len(rows)<1000:raise ValueError(f'Year {year} source-joined sample insufficient')
                data[year][clock]=rows
                source[str(year)][f'clock_{clock}s_join']=audit
            gz.unlink(missing_ok=True)
    results={}
    for shift in clock_shifts:
        r={y:data[y][shift] for y in years}
        results[f'clock_{shift}s']={
          'train_2009_test_2010':_score(r[2009],r[2010]),
          'train_2010_test_2011':_score(r[2010],r[2011]),
          'train_2009_2010_test_2011':_score(r[2009]+r[2010],r[2011]),
          'same_level_matched_by_year':{str(y):same_height_hysteresis(r[y]) for y in years}
        }
    out={'evidence':'ORIGINAL_GPS_MEASURED_RWS_RETROSPECTIVE_TEMPORAL_TRANSFER',
         'years':list(years),'source':source,'scenarios':results,
         'source_clock':'UNKNOWN_UTC_OR_GPS_TIME; 0_and_minus15s_sensitivity',
         'cohort_independence':'Held-out year, not necessarily disjoint bird IDs; test-year environmental conditions and repeated populations',
         'front_causation':'NOT_ADMITTED_no_measured_DEM_local_exposure_or_prey',
         'social_causation':'NOT_ADMITTED_no_ghost_partner_comparison'}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    a=p.parse_args()
    report=run(a.output)
    print(json.dumps({'evidence':report['evidence'],'clock':report['source_clock'],
                      'sources':{y:{'original_gps_rows':sum(s['raw_original_rows'] for k,s in rec.items() if k.endswith('_join'))//2,
                                    'gauge_rows':rec['RWS_measured_NAP_audit']['gauge_rows']}
                                 for y,rec in report['source'].items()},
                      'scenarios':report['scenarios']},sort_keys=True))
