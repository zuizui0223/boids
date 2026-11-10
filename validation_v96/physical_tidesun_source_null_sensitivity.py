"""v96: sensitivity of tidal-form association to opportunity definitions and source selection.
POST-v95 exploratory, no independent wild animal inference, no newly acquired year.
A finite-hour shuffled-day null is only a sampling benchmark, not a realistic
tidal autocorrelation or solar-phase null; disclose limitations and all failures.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean,median
from math import isfinite
import argparse, json
import numpy as np
from aggregate_all_2019_physical import (
    macro_rows,coastal_clusters,spearman,heldout_band_models,within_band_permutation,SEED
)
MIN_CLUSTER_DAYS=120
def cluster_environment(sites):
    groups=coastal_clusters(sites)
    rows=[]
    for group in groups:
        source=[r for r in group if r['opportunity']['n_valid_day_low_2']>=MIN_CLUSTER_DAYS]
        if not source: continue
        site_mean=lambda fn:float(mean(fn(s) for s in source))
        F=site_mean(lambda s:s['form_factor_F'])
        absM=site_mean(lambda s:s['opportunity']['mean_daily_abs_M'])
        randomM=site_mean(lambda s:s['opportunity']['null_random_hour_baseline_abs_M'])
        low4=[s['opportunity']['mean_daily_abs_M_low4'] for s in source
              if s['opportunity']['mean_daily_abs_M_low4'] is not None]
        pair=[s['matched_fraction_delta_low_sun_ge_1h'] for s in source
              if s['matched_fraction_delta_low_sun_ge_1h'] is not None]
        rows.append({'source_ids':[s['uid'] for s in group],
          'n_eligible_sites':len(source),'abs_lat':site_mean(lambda s:abs(s['latitude'])),
          'hemisphere':'N' if site_mean(lambda s:s['latitude'])>=0 else 'S',
          'form_factor':F,'regime':('semidiurnal' if F<.25 else 'mixed_semidiurnal' if F<1.5
               else 'mixed_diurnal' if F<3 else 'diurnal'),
          'mean_abs_M':absM,'random_hour_sampling_reference_M':randomM,
          'actual_minus_random_hour_reference_M':absM-randomM,
          'mean_abs_M_low4':float(mean(low4)) if len(low4)>=1 else None,
          'fraction_of_days_abs_M_at_least_025':site_mean(
               lambda s:s['opportunity']['frac_days_absolute_M_ge_0_25']),
          'fraction_same_solar_daylength_pairs_diff_1h':float(mean(pair)) if pair else None})
    return rows

def exact_permutation_in_band(rows,endpoint,seed=SEED,nperm=10000):
    # same source-defined 15 degree solar latitude bands as existing v95;
    # within-band label shuffling, one region=one unit, abs(latitude), hemisphere adjusted.
    arr=[r for r in rows if r[endpoint] is not None]
    from aggregate_all_2019_physical import ranks,pearson
    x=np.array([r['form_factor'] for r in arr],dtype=float)
    y=np.array([r[endpoint] for r in arr],dtype=float)
    lat=np.array([r['abs_lat'] for r in arr])
    hemi=np.array([int(r['hemisphere']=='N') for r in arr])
    X=np.column_stack([np.ones(len(arr)),lat/60.,hemi])
    rx=ranks(x);ry=ranks(y)
    rry=ry-X@np.linalg.lstsq(X,ry,rcond=None)[0]
    rrx=rx-X@np.linalg.lstsq(X,rx,rcond=None)[0]
    obs=pearson(rrx,rry)
    groups=defaultdict(list)
    for i,row in enumerate(arr):
        band=int(row['abs_lat']//15)*15
        groups[(row['hemisphere'],band)].append(i)
    rng=np.random.default_rng(seed)
    exceed=0
    for _ in range(nperm):
        perm=rx.copy()
        for inds in groups.values():
            if len(inds)>=2: perm[inds]=rng.permutation(perm[inds])
        p_rx=perm-X@np.linalg.lstsq(X,perm,rcond=None)[0]
        v=pearson(p_rx,rry)
        if v is not None and abs(v)>=abs(obs)-1e-12: exceed+=1
    return {'n_geo_clusters':len(arr),'spearman':spearman(x,y),
       'rank_partial_r_adjust_abs_lat_hemisphere':obs,
       'band_restricted_permutation_p_exploratory':(exceed+1)/(nperm+1),
       'permutations':nperm}

def source_failure_summary(byband):
    problems=Counter(); failures=defaultdict(Counter)
    n=0
    for band,v in byband.items():
        for row in v['source_failures']:
            n+=1
            if row.get('stage')=='genuine_hourly_computation':
                key='computation_error'
            else:
                codes=[s.get('http_status') for s in row.get('errors',[]) if s.get('http_status') is not None]
                messages=[s.get('failure','') for s in row.get('errors',[])]
                if any(c==429 for c in codes): key='rate_limited_HTTP429'
                elif any(c==503 for c in codes):key='server_HTTP503'
                elif any('timed out' in m.lower() for m in messages): key='transport_timeout'
                elif any(c==404 for c in codes): key='HTTP404_missing_source'
                else:key='other_source_failure'
            problems[key]+=1;failures[band][key]+=1
    return {'n_total':n,'by_cause':dict(problems),
            'by_latitude_band':{k:dict(v) for k,v in sorted(failures.items())}}

def run(input_dir,outpath):
    paths=list(Path(input_dir).rglob('v94-2019-original-source-*.json'))
    if len(paths)!=12: raise ValueError('STOP: all 12 original source lat bands required')
    sites,bands,counts,regimes=macro_rows(paths)
    rows=cluster_environment(sites)
    if len(rows)<100:raise ValueError('STOP: missing known original geographic support')
    endpoints=['mean_abs_M','actual_minus_random_hour_reference_M','mean_abs_M_low4',
               'fraction_of_days_abs_M_at_least_025',
               'fraction_same_solar_daylength_pairs_diff_1h']
    results={k:exact_permutation_in_band(rows,k) for k in endpoints}
    means={k:{'n_supported_clusters':sum(x[k] is not None for x in rows),
              'mean':mean(x[k] for x in rows if x[k] is not None),
              'range':[min(x[k] for x in rows if x[k] is not None),
                       max(x[k] for x in rows if x[k] is not None)]}
           for k in endpoints}
    nreal=sum(r['actual_minus_random_hour_reference_M']>0 for r in rows)
    report={'analysis':'v96_2019_observed_UHSLC_tidal_solar_source_vs_random_hour_reference',
        'original_source_v94_run':42616065580,
        'parent_v95_run':42728163328,
        'status':'POST_V95_EXPLORATORY_MULTIPLE_OUTCOMES_CORRELATED_DO_NOT_RECAST_AS_INDEPENDENT_CONFIRMATION',
        'n_original_candidate_gauges':counts['candidate'],
        'n_original_2019_quality_eligible_gauges':counts['eligible'],
        'source_failures':source_failure_summary(bands),
        'n_100km_geographic_clusters':len(rows),
        'endpoints':results,'endpoint_cluster_means':means,
        'n_clusters_actual_daily_absM_exceeds_finite_hour_random_assignment_reference':nreal,
        'reference_boundary':'within-day independent random assignment of low hours does NOT preserve actual tide periodicity/autocorrelation, local hydrodynamics or spring neap timing; this is a sampling reference, not a physical mechanism null',
        'physical_vs_biological_boundary':'all 2019 tide-solar results are environmental GAUGE coincidence only, not observed habitat dryness, prey, foraging, time niche, a behavioral clock, or causal ecology'}
    Path(outpath).parent.mkdir(parents=True,exist_ok=True)
    Path(outpath).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V96_SOURCE_FAILURE_SUMMARY '+json.dumps(report['source_failures'],sort_keys=True),flush=True)
    print('V96_GLOBAL_PHYSICAL_SENSITIVITY '+json.dumps({
      'eligible_gauges':counts['eligible'],'geo_clusters':len(rows),
      'n_excess_over_finite_hour_reference':nreal,'endpoints':results,'means':means},sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--artifact-dir',required=True)
    p.add_argument('--output',required=True)
    x=p.parse_args();run(x.artifact_dir,x.output)
