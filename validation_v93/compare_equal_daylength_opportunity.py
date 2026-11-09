"""v93: independently pre-defined comparisons on v92 *observed* UHSLC hourly environmental-only artifact.
No animal outcome, no resource exposure, no inferred wetland availability.
Post-v92 exploratory mechanism: same-astronomical-daylength days can differ in true gauge low-water daylight hours.
"""
from __future__ import annotations
from datetime import date, datetime, timezone
from pathlib import Path
from collections import defaultdict
from itertools import permutations
from statistics import median, mean, pstdev
from math import sqrt, isfinite
import argparse, json
from astral import Observer
from astral.sun import sunrise, sunset

SOURCE_RUN=42612796642
EXPECTED_SOURCE_COUNTS=(564,719)
SOLSTICE_2019=date(2019,6,21)
MAX_PHOTOPERIOD_DIFF_MINUTES=10.0
MIN_CALENDAR_SEPARATION_DAYS=14

def _physical_daylength_min(lat,lon,d):
    obs=Observer(latitude=float(lat),longitude=float(lon),elevation=0)
    return (sunset(obs,date=d,tzinfo=timezone.utc)-sunrise(obs,date=d,tzinfo=timezone.utc)).total_seconds()/60

def _pearson(a,b):
    xa=[z-mean(a) for z in a];xb=[z-mean(b) for z in b]
    den=sqrt(sum(x*x for x in xa)*sum(x*x for x in xb))
    return sum(x*y for x,y in zip(xa,xb))/den if den else float('nan')

def _ranks(a):
    s=sorted(range(len(a)),key=lambda i:a[i]); ranks=[0.]*len(a)
    for k,i in enumerate(s):ranks[i]=float(k+1)
    return ranks

def spearman_exact(x,y):
    assert len(x)==len(y)
    n=len(x)
    if n<4 or n>9:raise ValueError('small-n exact permutation only')
    rx=_ranks(x);ry=_ranks(y);rho=_pearson(rx,ry)
    exceed=0;total=0
    for z in permutations(ry):
        total+=1
        if abs(_pearson(rx,z))+1e-12>=abs(rho):exceed+=1
    return {'rho':rho,'permutations':total,'two_sided_exact_p_exploratory':exceed/total}

def source_daily_audit(s):
    p=s['physical']
    daily=p['daily']
    assert len(daily)==p['n_valid_days']
    dates=[d['date'] for d in daily]
    if len(set(dates))!=len(dates):raise ValueError('duplicated daily date')
    for row in daily:
        if not (0<=row['O']<=1 and 0<=row['A']<=1 and -1<=row['M']<=1
                and abs(row['M']-(row['O']-row['A']))<1e-10):
            raise ValueError('physical source algebra changed')
    if abs(mean(abs(d['M']) for d in daily)-p['daily_mean_abs_M'])>1e-10:
        raise ValueError('physical source summary drift')
    return daily

def daylength_matching(s):
    """All source-eligible days, greedy 1:1 matching smallest known solar-daylength difference; no outcome used."""
    daily=source_daily_audit(s)
    north,south=[],[]
    for item in daily:
        d=date.fromisoformat(item['date'])
        if d==SOLSTICE_2019:continue
        L=_physical_daylength_min(s['latitude'],s['longitude'],d)
        row={'date':item['date'],'L':L,'joint_original_hours':item['joint_original_hours'],
             'M':item['M'],'O':item['O']}
        (north if d<SOLSTICE_2019 else south).append(row)
    candidates=[]
    for a in north:
        da=date.fromisoformat(a['date'])
        for b in south:
            db=date.fromisoformat(b['date'])
            delta=abs(a['L']-b['L'])
            if delta<=MAX_PHOTOPERIOD_DIFF_MINUTES and (db-da).days>=MIN_CALENDAR_SEPARATION_DAYS:
                candidates.append((delta,a['date'],b['date'],a,b))
    candidates.sort(key=lambda z:(z[0],z[1],z[2]))
    chosen=[];used_a=set();used_b=set()
    for delta,ad,bd,a,b in candidates:
        if ad in used_a or bd in used_b:continue
        used_a.add(ad);used_b.add(bd)
        chosen.append({'before':ad,'after':bd,'daylength_diff_min':delta,
                       'absolute_low_sunlit_hours_difference':
                           abs(a['joint_original_hours']-b['joint_original_hours']),
                       'absolute_M_difference':abs(a['M']-b['M'])})
    return chosen

def site_summary(s):
    daily=source_daily_audit(s)
    pairs=daylength_matching(s)
    dif=[x['absolute_low_sunlit_hours_difference'] for x in pairs]
    md=[d['M'] for d in daily]
    abs_m=mean(abs(x) for x in md)
    return {'id':s['uid'],'name':s['station'],'country':s['country'],
        'latitude':s['latitude'],'longitude':s['longitude'],
        'record_id':s['record_id'],'regime':s['harmonics']['regime'],
        'harmonic_form_F':s['harmonics']['F'],
        'four_harmonic_R2':s['harmonics']['four_constituent_R2'],
        'observed_quality_4_hours':s['physical']['source_hours'],
        'n_eligible_days':len(daily),
        'daily_signed_M_mean':mean(md),
        'daily_abs_M_mean':abs_m,
        'daily_abs_M_variation_sd':pstdev(md),
        'cancellation_fraction_within_days':1-abs(mean(md))/abs_m if abs_m else None,
        'matched_equal_daylength_pairs':len(pairs),
        'matched_daylength_difference_median_min':median([x['daylength_diff_min'] for x in pairs]) if pairs else None,
        'matched_abs_low_sunlit_hour_diff_median':median(dif) if pairs else None,
        'matched_abs_low_sunlit_hour_diff_mean':mean(dif) if pairs else None,
        'matched_fraction_at_least_1hr':sum(d>=1 for d in dif)/len(dif) if dif else None,
        'matched_fraction_at_least_2hr':sum(d>=2 for d in dif)/len(dif) if dif else None,
        'matched_max_diff_hr':max(dif) if dif else None,
        'n_sunlit_low_hours_year':s['physical']['sunlit_low_hours'],
        'n_dark_low_hours_year':s['physical']['dark_low_hours']}

def run(input_path,output_path):
    r=json.loads(Path(input_path).read_text())
    src=r.get('source') or {}
    if r.get('status')!='OBSERVED_PHYSICAL_PILOT' or (src.get('station_ids'),src.get('record_versions'))!=EXPECTED_SOURCE_COUNTS:
        raise ValueError('STOP: expected independently original UHSLC v92 pilot missing')
    if src.get('v89_authentic_source_workflow_run_id')!=42608393924:
        raise ValueError('STOP: UHSLC v89 authentic manifest provenance changed')
    sites=[v['selected'] for k,v in sorted(r['sites'].items()) if v['selected'] is not None]
    if len(sites)<6:raise ValueError('STOP: fewer than 6 physical source sites')
    rows=[site_summary(s) for s in sites]
    valid=[x for x in rows if x['matched_equal_daylength_pairs']>=15]
    by_regime=defaultdict(list)
    for x in rows:by_regime[x['regime']].append(x['daily_abs_M_mean'])
    out={'analysis':'V93_2019_GENUINE_UHSLC_TWO_CLOCK_EQUAL_DAYLENGTH_OBSERVATIONAL_PHYSICS',
       'source_V92_action_run':SOURCE_RUN,
       'source_original_UHSLC_manifest_SHA256':src['manifest_SHA256'],
       'science_claim_boundary':'NO_INFERRED_BIOLOGICAL_ACTIVITY_OR_TIDAL_FLAT_EXPOSURE',
       'analysis_status':'EXPLORATORY_V92_SOURCE_OUTCOME_ALREADY_KNOWN',
       'matching':'same_station_solar_year_before_vs_after_June21_minimum_daylength_error_one_to_one_without_outcome',
       'max_daylength_diff_minutes':MAX_PHOTOPERIOD_DIFF_MINUTES,
       'min_calendar_separation_days':MIN_CALENDAR_SEPARATION_DAYS,
       'n_sites':len(rows),'n_sites_with_15plus_pairs':len(valid),
       'original_latitude_bands_attempted':len(r['sites']),
       'n_source_bands_stopped':sum(v['selected'] is None for v in r['sites'].values()),
       'sites':rows,
       'description':'Differences in OBSERVED LOW GAUGE WATER-HEIGHT and astronomical sunlight. Not mudflat surface exposure. One station per preselected latitude band; exploratory convenience sample.',
       'regime':{k:{'n_sites':len(v),'equal_site_mean_absolute_daily_M':mean(v),'range':[min(v),max(v)]}
                 for k,v in by_regime.items()}}
    if valid:
        out['same_daylength']={'total_pairs_nonindependent':sum(x['matched_equal_daylength_pairs'] for x in valid),
           'equal_site_mean_fraction_at_least_1hr':mean(x['matched_fraction_at_least_1hr'] for x in valid),
           'equal_site_mean_median_hours_difference':mean(x['matched_abs_low_sunlit_hour_diff_median'] for x in valid),
           'site_fraction_at_least_1hr_range':[min(x['matched_fraction_at_least_1hr'] for x in valid),
                                               max(x['matched_fraction_at_least_1hr'] for x in valid)]}
    if len(rows)>=6:
        out['tidal_form_ratio_vs_abs_M']=spearman_exact(
           [x['harmonic_form_F'] for x in rows],
           [x['daily_abs_M_mean'] for x in rows])
        out['latitude_abs_vs_abs_M']=spearman_exact(
           [abs(x['latitude']) for x in rows],
           [x['daily_abs_M_mean'] for x in rows])
    Path(output_path).parent.mkdir(parents=True,exist_ok=True)
    Path(output_path).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    for x in rows:
        print('V93_OBSERVED_ORIGINAL_SITE '+json.dumps({k:x[k] for k in
          ['id','country','latitude','regime','harmonic_form_F','daily_abs_M_mean',
           'daily_signed_M_mean','cancellation_fraction_within_days',
           'matched_equal_daylength_pairs','matched_abs_low_sunlit_hour_diff_median',
           'matched_fraction_at_least_1hr']}),flush=True)
    print('V93_FINAL '+json.dumps({k:out[k] for k in
          ['analysis','n_sites','n_sites_with_15plus_pairs','n_source_bands_stopped',
           'same_daylength','regime','tidal_form_ratio_vs_abs_M','latitude_abs_vs_abs_M'] if k in out},sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--input',required=True);a.add_argument('--output',required=True)
    args=a.parse_args();run(args.input,args.output)
