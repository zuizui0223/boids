"""v94 ALL ORIGINAL UHSLC 2019 stations, source-first by latitude band.
A *physical* tide × sun worldwide descriptive panel, not biological niche evidence.
Fixed before opening any all-station 2019 water-level results.
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from collections import defaultdict,Counter
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from statistics import mean
from math import comb
import numpy as np
from astral import Observer
from astral.sun import elevation
from original_UHSLC_2019_tide_solar import (
    START,YEAR,N,PROVIDERS,native_hourly,parse_native,choose_original_segment,
    harmonic_form)
from compare_equal_daylength_opportunity import daylength_matching
BANDS=[f'{hem}_{lo:02d}_{lo+15:02d}' for hem in ('N','S') for lo in (0,15,30,45,60,75)]
QC_YEAR_MONTH=.80
MAX_GAP_HOURS=72
THRESHOLD_SUN_DEG=3
def exact_random_hour_abs_M(n,k,a):
    """Pure hypergeometric reference: choose k low hours from n observed slots at random.
    This destroys tide temporal autocorrelation and is an illustrative *sampling baseline*, not a physical null.
    """
    if not (0<=a<=n and 0<k<=n and n<=24):raise ValueError('invalid observed discrete hours')
    denom=comb(n,k)
    lo=max(0,k-(n-a)); hi=min(k,a)
    return sum(abs(x/k-a/n)*comb(a,x)*comb(n-a,k-x)/denom for x in range(lo,hi+1))

def analyze_hourly(data,lat,lon):
    """No assumptions on wet/dry habitat. Relative gauge low water from native same-datum Q25."""
    obs=Observer(latitude=lat,longitude=lon,elevation=0)
    q25=float(np.quantile(list(data.values()),.25))
    bydate=defaultdict(Counter)
    month=defaultdict(Counter)
    year=Counter()
    solar_local_shift=timedelta(hours=lon/15.)
    for hour,level in sorted(data.items()):
        utc=START+timedelta(hours=hour)
        alpha=elevation(obs,utc)
        day=(utc+solar_local_shift).date()
        date_key=day.isoformat()
        n_low=level<=q25
        n_bright=alpha>THRESHOLD_SUN_DEG
        n_dark=alpha< -THRESHOLD_SUN_DEG
        item=Counter({'observed':1,'low':int(n_low),'light':int(n_bright),
            'dark':int(n_dark),'twilight':int(not (n_bright or n_dark)),
            'low_light':int(n_low and n_bright),'low_dark':int(n_low and n_dark)})
        bydate[date_key].update(item)
        month[utc.month].update(item)
        year.update(item)
    valid=[]
    reference=[]
    for d,c in sorted(bydate.items()):
        # Each solar day: original measured coverage >=80% of 24h, genuine low hours>=2.
        if c['observed']<19 or c['low']<2:continue
        o=c['low_light']/c['low'];a=c['light']/c['observed']
        baseline=exact_random_hour_abs_M(c['observed'],c['low'],c['light'])
        valid.append({'date':d,'O':o,'A':a,'M':o-a,
            'joint_original_hours':int(c['low_light']),
            'n_observed':int(c['observed']),'n_low':int(c['low']),
            'n_daylight':int(c['light']),'finite_hour_assignment_baseline_abs_M':baseline})
        reference.append(baseline)
    if not valid:
        return {'Q25_mm':q25,'n_valid_day_low_2':0,'n_valid_day_low_4':0,
            'source_eligible_hourly':len(data),'status':'NO_WITHIN_DAY_LOW_SUPPORT'}
    m=np.array([r['M'] for r in valid])
    m4=np.array([r['M'] for r in valid if r['n_low']>=4])
    return {'Q25_mm':q25,'n_valid_day_low_2':len(valid),'n_valid_day_low_4':len(m4),
        'source_eligible_hourly':len(data),
        'mean_daily_abs_M':float(np.mean(abs(m))),
        'mean_daily_abs_M_low4':float(np.mean(abs(m4))) if len(m4)>=20 else None,
        'mean_daily_signed_M':float(np.mean(m)),
        'null_random_hour_baseline_abs_M':float(np.mean(reference)),
        'difference_actual_vs_random_hour_reference':float(np.mean(abs(m))-np.mean(reference)),
        'frac_days_absolute_M_ge_0_25':float(np.mean(abs(m)>=.25)),
        'monthly':{str(k):{'low_hours':v['low'],'day_low_hours':v['low_light'],
               'night_low_hours':v['low_dark'],
               'observed_hours':v['observed'],
               'sun_hours':v['light']}
             for k,v in sorted(month.items())},
        'low_sun_hours_annual':year['low_light'],
        'low_dark_hours_annual':year['low_dark'],
        'daylight_hours_annual':year['light'],
        'solar_twilight_excluded_annual':year['twilight'],
        'daily':valid, 'status':'ACTUAL_ORIGINAL_HOURLY_SOURCE'}

def condense_source(d,loc,rec,datum,provider,raw):
    phy=analyze_hourly(d,float(loc['latitude']),float(loc['longitude_signed']))
    if phy['status']!='ACTUAL_ORIGINAL_HOURLY_SOURCE':return {'qc':'NO_DAILY_SUPPORT'}
    rank=harmonic_form(d)
    daily=phy.pop('daily')
    stub={'latitude':float(loc['latitude']),'longitude':float(loc['longitude_signed']),
          'physical':{'daily':daily,'n_valid_days':len(daily),
             'daily_mean_abs_M':phy['mean_daily_abs_M']}}
    paired=daylength_matching(stub)
    deviations=[r['absolute_low_sunlit_hours_difference'] for r in paired]
    return {'qc':'ADMITTED_2019_ORIGINAL_HOURLY_PHYSICAL',
      'uid':loc['uhslc_id'],'record_id':rec,'station_name':loc['original_station_name'],
      'country':loc['original_station_country'],
      'latitude':loc['latitude'],'longitude_signed':loc['longitude_signed'],
      'year':YEAR,'provider':provider,'raw_2019_source_SHA256':sha256(raw).hexdigest(),
      'gauge_datum_version_uncrossed':True,'max_missing_gap_h':datum,'hourly_n':len(d),
      'form_factor_F':rank['F'],'regime':rank['regime'],
      'harmonic_four_constituent_R2':rank['four_constituent_R2'],
      'harmonics_mm':rank['constituents_amplitude_mm'],
      'matched_daylength_pairs':len(paired),
      'matched_fraction_delta_low_sun_ge_1h':sum(x>=1 for x in deviations)/len(deviations) if deviations else None,
      'matched_median_abs_delta_low_sun_hr':float(np.median(deviations)) if deviations else None,
      'opportunity':phy}

def run(manifest_path,band,outpath):
    if band not in BANDS:raise ValueError('invalid official 15 degree band')
    obj=json.loads(Path(manifest_path).read_text())
    records=obj['original_public_UHSLC_stations_and_datum_segments']
    if obj['source_original_provider']!='primary_UHSLC' or len({r['uhslc_id'] for r in records})!=564 or len(records)!=719:
        raise ValueError('STOP expected authenticated immutable true UHSLC v89 source station list')
    grouped=defaultdict(list)
    from real_global_UHSLC_hourly_station_manifest import _latitude_band
    for row in records:
        if _latitude_band(row['latitude'])==band:grouped[row['uhslc_id']].append(row)
    out={'analysis':'V94_ALL_STATIONS_2019_ORIGINAL_UHSLC_HOURLY_TIDE_SOLAR_PHYSICAL',
         'band':band,'year':YEAR,'source_original_v89_manifest_SHA':obj['source_original_manifest_raw_SHA'],
         'source_version':'station record not pooled across benchmarks',
         'outcome':'low relative gauge height and astronomical light NOT observed intertidal exposed habitat',
         'candidate_unique_UHSLC_station_ids':len(grouped),'raw_station_outcomes':[],
         'quality_coverage':'80percent every month and year; <=72h continuous gap, quality=4',
         'source_failures':[],'source_skipped_qc':[],
         'source_candidates_attempted':0,
         'rules_pre_frozen_before_all_station_2019_source_results':True}
    for i,(uid,meta) in enumerate(sorted(grouped.items()),start=1):
        out['source_candidates_attempted']+=1
        admissible=None
        invalid=None
        attempted_provider=[]
        for n,base in PROVIDERS:
            try:
                raw=native_hourly(base,uid)
                recmap=parse_native(raw,uid)
                hit=choose_original_segment(recmap,{m['record_id'] for m in meta})
                if hit is None:
                    invalid={'uid':uid,'reason':'2019 monthly/year/hourly QC, no eligible single datum segment',
                             'n_segments_with_any_quality4_data':len(recmap)}
                    break
                rec,levels,gap=hit
                admissible=(levels,rec,gap,n,raw)
                break
            except HTTPError as e:
                attempted_provider.append({'provider':n,'http_status':e.code})
                if e.code==404:
                    invalid={'uid':uid,'reason':'primary original ERDDAP returned HTTP404, no eligible 2019 record','source':n}
                    break
            except (OSError,URLError,TimeoutError,ValueError) as e:
                attempted_provider.append({'provider':n,'failure':str(e)[:130]})
        if admissible is None:
            if invalid is not None:out['source_skipped_qc'].append(invalid)
            else:out['source_failures'].append({'uid':uid,'errors':attempted_provider})
            continue
        data,rec,gap,n,raw=admissible
        try:
            result=condense_source(data,meta[0],rec,gap,n,raw)
            if result['qc']!='ADMITTED_2019_ORIGINAL_HOURLY_PHYSICAL':
                out['source_skipped_qc'].append({'uid':uid,'reason':'insufficient daily source support'})
            else:
                out['raw_station_outcomes'].append(result)
                print('V94_ADMITTED '+json.dumps({'band':band,'id':uid,
                  'lat':result['latitude'],'F':round(result['form_factor_F'],4),
                  'mean_abs_M':round(result['opportunity']['mean_daily_abs_M'],5),
                  'n_days':result['opportunity']['n_valid_day_low_2'],
                  'pair_1hour_fraction':result['matched_fraction_delta_low_sun_ge_1h']},sort_keys=True),flush=True)
        except Exception as e:
            out['source_failures'].append({'uid':uid,'stage':'genuine_hourly_computation','error':repr(e)[:190]})
    out['summary']={'n_eligible_site':len(out['raw_station_outcomes']),
        'n_qc_not_admitted':len(out['source_skipped_qc']),
        'n_source_failures':len(out['source_failures']),
        'fraction_station_source_admitted':len(out['raw_station_outcomes'])/max(len(grouped),1),
        'regimes':dict(Counter(x['regime'] for x in out['raw_station_outcomes']))}
    if out['raw_station_outcomes']:
        vals=[x['opportunity']['mean_daily_abs_M'] for x in out['raw_station_outcomes']]
        out['summary']['mean_site_daily_abs_M']=float(mean(vals))
        out['summary']['min_max_site_daily_abs_M']=[min(vals),max(vals)]
    out['status']='SOURCE_AND_PHYSICS_ADMITTED' if out['raw_station_outcomes'] else 'SOURCE_NO_2019_ADMITTED_STATIONS'
    Path(outpath).parent.mkdir(parents=True,exist_ok=True)
    Path(outpath).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print('V94_BAND_FINAL '+json.dumps({'band':band,'status':out['status'],
       'candidate_stations':len(grouped),'summary':out['summary']},sort_keys=True),flush=True)
    return out

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--v89-source-manifest',required=True)
    a.add_argument('--band',required=True,choices=BANDS)
    a.add_argument('--output',required=True)
    x=a.parse_args()
    run(x.v89_source_manifest,x.band,x.output)
