"""v100 REAL original UHSLC 2019 amplitudes vs four-constituent random-phase harmonic expectation.

IMPORTANT: environmental physics simulation; NO living organism niche observation,
NO true original historical phase null, NO actual 2019 water height replay, NO habitat.
Original observed F and original observed M are extracted unchanged from source-complete v94.
Null uses four real source harmonic amplitudes with 32 independent drawn phases.
"""
from __future__ import annotations
import argparse,json
from datetime import timedelta
from pathlib import Path
from collections import Counter,defaultdict
from statistics import mean
from math import floor
import numpy as np
from astral import Observer
from astral.sun import elevation
from original_UHSLC_2019_tide_solar import START,PERIODS,N
from aggregate_all_2019_physical import macro_rows,coastal_clusters,spearman
RUN_SOURCE_V94=42616065580
YEAR=2019
N_PHASE=32
SEED=20261110
SOLAR_ALT=3.
MIN_HOURS_DAY=19
MIN_LOW_HOURS_DAY=2
CANONICAL_PERIODS=('M2','S2','K1','O1')

def bins_at_native_local_solar_day(lon,hours):
    """Same UTC+longitude/15 fixed astronomical-day convention as v94 source."""
    return np.floor((hours.astype(float)+lon/15.)/24.).astype(np.int64)+1

def daily_absolute_gauge_M(heights,solar_daylight,day_index):
    """Q25 native synthetic year; the observed-gauge value is NEVER fitted here."""
    h=np.asarray(heights,dtype=float)
    daylight=np.asarray(solar_daylight,dtype=bool)
    day_index=np.asarray(day_index,dtype=np.int64)
    if not (len(h)==len(daylight)==len(day_index)==N and np.isfinite(h).all()
            and day_index.min()>=0):
        raise ValueError('V100 invalid genuine daily source-matching geometry')
    n_obs=np.bincount(day_index,minlength=370)
    n_light=np.bincount(day_index,weights=daylight.astype(float),minlength=370)
    q=float(np.quantile(h,.25))
    low=h<=q
    n_low=np.bincount(day_index,weights=low.astype(float),minlength=370)
    n_low_sun=np.bincount(day_index,weights=(low&daylight).astype(float),minlength=370)
    eligible=(n_obs>=MIN_HOURS_DAY)&(n_low>=MIN_LOW_HOURS_DAY)
    if eligible.sum()<120: raise ValueError('V100 original source solar day low-state support missing')
    m=n_low_sun[eligible]/n_low[eligible]-n_light[eligible]/n_obs[eligible]
    return float(np.mean(np.abs(m))),int(eligible.sum())

def solar2019_native_observed_location(lat,lon):
    """REAL 2019 astronomical sun altitude at ORIGINAL source coordinate and UTC hours."""
    observer=Observer(latitude=float(lat),longitude=float(lon),elevation=0.)
    bright=np.zeros(N,dtype=bool)
    for i in range(N):
        bright[i]=elevation(observer,START+timedelta(hours=int(i)))>SOLAR_ALT
    return bright

def synthetic_harmonic_timecourses(amplitudes,solar_bright,local_day_id,uid,nphase=N_PHASE):
    a=np.array([float(amplitudes[p]) for p in CANONICAL_PERIODS],dtype=float)
    if not (np.isfinite(a).all() and (a>=0).all() and a.sum()>0):
        raise ValueError('SOURCE_STOP_FOUR_HARMONIC_AMPLITUDE_SOURCE_BAD')
    h=np.arange(N,dtype=float)
    # Raw astronomical constituents, not imposed canonical tide phase.
    sine=np.column_stack([np.sin(2*np.pi*h/PERIODS[p]) for p in CANONICAL_PERIODS])
    cosine=np.column_stack([np.cos(2*np.pi*h/PERIODS[p]) for p in CANONICAL_PERIODS])
    rng=np.random.default_rng(SEED+int(uid))
    out=[]
    # Independent phases are randomized, so this is an intentionally simplified
    # four-harmonic _expectation_ and NOT a phase-autocorrelation-correct permutation
    # of actual 2019 sea level readings.
    for k in range(nphase):
        phase=rng.uniform(0,2*np.pi,size=4)
        heights=sine@(a*np.cos(phase))+cosine@(a*np.sin(phase))
        val,days=daily_absolute_gauge_M(heights,solar_bright,local_day_id)
        out.append(val)
    return np.array(out,dtype=float)

def source_gauge_table(source_files):
    if len(source_files)!=12: raise ValueError('STOP original world source all 12 bands required')
    stations,byband,counts,_=macro_rows(source_files)
    if counts['candidate']!=564 or counts['eligible']!=160:
        raise ValueError('STOP original worldwide 2019 source eligibility changed')
    uids={s['uid'] for s in stations}
    if len(uids)!=160:raise ValueError('STOP repeated original station IDs')
    return stations,counts

def correlation_by_exact_geo_components(groups,generated,quality_filter):
    realF=[];realM=[];surr=[]
    for cluster in groups:
        supported=[s for s in cluster if s['uid'] in generated and quality_filter(s)]
        if not supported:continue
        realF.append(float(np.mean([s['form_factor_F'] for s in supported])))
        realM.append(float(np.mean([s['opportunity']['mean_daily_abs_M'] for s in supported])))
        surr.append(np.mean([generated[s['uid']]['null_M'] for s in supported],axis=0))
    if len(realF)<20: return {'status':'NOT_ADMITTED_CLUSTER_N_LT20','n_clusters':len(realF)}
    surr=np.asarray(surr,dtype=float)
    rho_obs=spearman(realF,realM)
    rho_null=np.array([spearman(realF,surr[:,i]) for i in range(surr.shape[1])])
    average_null=surr.mean(axis=1)
    residual=np.array(realM)-average_null
    return {
       'status':'DESCRIPTIVE_FOUR_HARMONIC_SURROGATE_COMPARISON',
       'n_100km_geographic_source_clusters':len(realF),
       'observed_F_vs_daily_abs_M_spearman':float(rho_obs),
       'harmonic_phase_randomized_rho_distribution':{
            'min':float(np.min(rho_null)),
            'q05':float(np.quantile(rho_null,.05)),
            'median':float(np.median(rho_null)),
            'q95':float(np.quantile(rho_null,.95)),
            'max':float(np.max(rho_null)),
            'replicates':len(rho_null)},
       'observed_rho_minus_surrogate_mean_rho':float(rho_obs-np.mean(rho_null)),
       'fraction_harmonic_surrogates_rho_at_least_observed_descriptive':
            float(np.mean(rho_null>=rho_obs)),
       'F_vs_excess_daily_absM_over_expected_harmonic_spearman':
            float(spearman(realF,residual)),
       'mean_observed_daily_abs_M':float(np.mean(realM)),
       'mean_four_harmonic_surrogate_abs_M':float(np.mean(average_null)),
       'mean_observed_minus_harmonic_null_expected_abs_M':float(np.mean(residual)),
       'n_clusters_observed_absM_greater_than_harmonic_null_mean':
            int(np.sum(residual>0))
    }

def run(source_dir,output):
    paths=list(Path(source_dir).rglob('v94-2019-original-source-*.json'))
    sites,counts=source_gauge_table(paths)
    groups=coastal_clusters(sites)
    generated={}
    for i,s in enumerate(sorted(sites,key=lambda z:z['uid']),1):
        sun=solar2019_native_observed_location(s['latitude'],s['longitude_signed'])
        days=bins_at_native_local_solar_day(s['longitude_signed'],np.arange(N))
        try:
            nulls=synthetic_harmonic_timecourses(s['harmonics_mm'],sun,days,s['uid'])
        except ValueError as e:
            raise ValueError(f'STOP_null_scientific_basis_for_original_UHSLC_gauge_{s["uid"]}: '+str(e)) from e
        generated[s['uid']]={'null_M':nulls,'mean_null_M':float(np.mean(nulls)),
           'observed_M':float(s['opportunity']['mean_daily_abs_M']),
           'coverage':s['hourly_n']/N,'harmonic_R2':s['harmonic_four_constituent_R2']}
        if i%20==0:
            print('V100_ORIGINAL_GLOBAL_SOURCE_PROGRESS '+json.dumps({
                'original_sites_processed':i,'total_original_sites':len(sites),
                'source_R2_at_last':s['harmonic_four_constituent_R2'],
                'last_UHSLC_id':s['uid']},sort_keys=True),flush=True)
    filter_groups={
       'all_quality_eligible_2019_original_source':lambda s:True,
       'four_constituent_R2_at_least_0_6':lambda s:s['harmonic_four_constituent_R2']>=.6,
       'original_2019_hourly_coverage_at_least_95pct':lambda s:s['hourly_n']>=.95*N,
       'both_harmonic_R2_0_6_and_hourly_coverage95pct':lambda s:(
             s['harmonic_four_constituent_R2']>=.6 and s['hourly_n']>=.95*N)}
    results={name:correlation_by_exact_geo_components(groups,generated,fil)
             for name,fil in filter_groups.items()}
    out={'analysis':'V100_REAL_ORIGINAL_2019_UHSLC_GAUGE_F_VS_M_EXPECTED_FOUR_HARMONIC_PHASE_NULL',
       'source_run_v94':RUN_SOURCE_V94,
       'original_564_station_source_census':counts,
       'n_original_source_gauges_scored':len(generated),
       'n_connected_100km_geo_clusters':len(groups),
       'surrogate_n_phases':N_PHASE,
       'seed_UID_specific':SEED,
       '2019_UTC_genuine_astral_solar_altitude_classification':'>+3 degrees',
       'harmonic_amplitudes':'ORIGINAL 2019 UHSLC 4-constituent station-specific OLS amplitudes',
       'randomization':'INDEPENDENT_HARMONIC_INITIAL_PHASE_UNIFORM_0_TO_2PI; actual local phase missing from source result',
       'gauge_low_water_definition':'own full surrogate series annual 25th percentile',
       'source_year_temporal_missingness_not_preserved':True,
       'results':results,
       'scientific_biological_boundary':'NO animal, actual tide-flat exposure, prey, or causal behavioral evidence. Null explicitly simplified: no storm/sea-state/weather, station-correlated physical phases, local surge, or original missing timestamps.',
       'post_discovery_annotation':'v95 observed F correlation known before phase-surrogate diagnostic, 2019 same original environmental site observations.'}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('V100_REAL_FOUR_HARMONIC_NULL_SCIENCE_RESULT '+json.dumps(
       {'original_source_sites':len(sites),'geographical_clusters':len(groups),
        'primary':results['all_quality_eligible_2019_original_source'],
        'quality_subsets':{k:{'n':v.get('n_100km_geographic_source_clusters'),
            'observed_rho':v.get('observed_F_vs_daily_abs_M_spearman'),
            'null_rho_median':(v.get('harmonic_phase_randomized_rho_distribution') or {}).get('median'),
            'excess_rho':v.get('F_vs_excess_daily_absM_over_expected_harmonic_spearman')}
          for k,v in results.items()}},sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-dir',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.source_dir,a.output)
