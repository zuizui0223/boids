"""v126 external original Belgian 2020 gull GPS source and independent GIC
static-wetland same-length 7 rotated endpoints. NO local Belgian tide series,
true dry-flat habitat, feeding labels, or causal species niche conclusion.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import timezone
from math import isfinite
from statistics import mean
import numpy as np
from astral import Observer
from astral.sun import elevation
from original_2020_belgium_gull_source import (
    PANELS,YEAR,MONTHS,RADIUS_KM,FOCAL,MIN_BIRD_HOURS,
    MIN_TAXON_BIRDS,MIN_MONTH_BIRDS,MIN_MONTH_HOURS,
    MIN_STEP_HOURS,MAX_STEP_HOURS,MAX_DISPLACEMENT_KMH,
    great_circle)
SEASON=(7,8)
GIC_CLASS_RF_THRESHOLD=50.
SOURCE_GIC_ALL8_MIN_VALID=.90
MIN_2020_SOURCE_GIC_STEPS=1000
MIN_2020_TAGGED_BIRDS=5
MIN_BIRD_COMPLETE_GIC_STEPS=20
BOOT_REPS=10000
BOOT_SEED_BASE=20261112
SUN_DAY_GT=3.
SUN_NIGHT_LT=-3.
RAYS=7

def original_hourly_steps_from_v125_eligible_tracks(private_tracks,panel):
    """Recreate EXACT original 2020 July-Oct v125 source step counts before
    keeping only Jul-Aug. No source/GIC pixel or geographic endpoint score.
    """
    colony=PANELS[panel]['colony']
    source_season=[];full_source=[]
    bytaxon=Counter();hours=Counter();source_birds=defaultdict(set)
    for (taxon,bird),source_fix in private_tracks.items():
        if taxon not in FOCAL:continue
        ordered=sorted(source_fix.values(),key=lambda item:item[0])
        hours[taxon]+=len(ordered);source_birds[taxon].add(bird)
        for old,new in zip(ordered,ordered[1:]):
            t0,la0,lo0=old;t1,la1,lo1=new
            elapsed=(t1-t0).total_seconds()/3600
            if not MIN_STEP_HOURS<=elapsed<=MAX_STEP_HOURS:continue
            # Original v125 source radius has already been checked before
            # eligibility, but recompute to detect source-only drift.
            if (great_circle(la0,lo0,*colony)>RADIUS_KM or
                great_circle(la1,lo1,*colony)>RADIUS_KM):
                raise ValueError('STOP_V126_ORIGINAL_GPS_2020_COLONY_RADIUS_CHANGED')
            length=great_circle(la0,lo0,la1,lo1)
            if length/elapsed>MAX_DISPLACEMENT_KMH:continue
            e={'taxon':taxon,'bird':bird,'month':t0.month,
                'original_UTC':t0.replace(tzinfo=timezone.utc),
                'GPS_departure_lat':la0,'GPS_departure_lon':lo0,
                'GPS_arrival_lat':la1,'GPS_arrival_lon':lo1,
                'original_elapsed_hours':elapsed,
                'original_km_per_hour':length/elapsed}
            full_source.append(e)
            bytaxon[taxon]+=1
            if t0.month in SEASON:source_season.append(e)
    return source_season,{'original_2020_JulOct_original_source_step_counts_by_taxon':
                            dict(bytaxon),
                         'original_2020_JulOct_original_source_coastal_eligible_hours_by_taxon':
                            dict(hours),
                         'original_2020_JulOct_original_eligible_bird_counts_by_taxon':
                            {k:len(v) for k,v in source_birds.items()},
                         'original_2020_JulAug_first_tag_hour_valid_source_step_count':
                            len(source_season),
                         'NO_GIC_SOURCE_PIXEL_SCORED_YET':True}

def check_original_v125_source_replay(panel,fixed_v125,parsed,full_source_qa):
    """Native original yearly study admission results must EXACTLY replay
    before ANY new Belgian GPS native RF map is fetched or scored.
    """
    spec=PANELS[panel]
    if (fixed_v125.get('panel')!=panel or
        fixed_v125.get('original_archive_record_id')!=spec['record'] or
        fixed_v125.get('source_2020_GPS_publisher_md5_frozen')!=spec['md5'] or
        fixed_v125.get('source_status')!=
              'ORIGINAL_2020_BELGIAN_GULL_ANNUAL_BIRD_SOURCE_AUTHENTICATED'):
        raise ValueError('STOP_V126_PRIOR_V125_RECORD_SOURCE_NOT_ADMITTED')
    old=fixed_v125['native_source_2020_birds_hour_and_movement_QA']
    if parsed['original_native_2020_JulyOctober_rows']!=old['original_native_2020_JulyOctober_rows']:
        raise ValueError('STOP_V126_ORIGINAL_NATIVE_2020_JulOct_SOURCE_ROWS_CHANGED')
    for taxon in FOCAL:
        a=parsed['source_2020_by_actual_original_taxon'][taxon]
        b=old['source_2020_by_actual_original_taxon'][taxon]
        for key in ('true_2020_original_birds_with_ge20_coastal_hours',
                    'native_original_2020_JulOct_coastal_bird_hours_in_eligible_tags',
                    'source_original_consecutive_bird_hour_steps_0p75_to_1p5_h_in_40km'):
            if a[key]!=b[key]:
                raise ValueError('STOP_V126_PRIOR_ORIGINAL_GPS_BIRD_HOUR_STEP_COUNTS_DRIFT_'+key)
        if (full_source_qa['original_2020_JulOct_original_source_step_counts_by_taxon'].get(taxon,0)!=b[
            'source_original_consecutive_bird_hour_steps_0p75_to_1p5_h_in_40km'] or
            full_source_qa['original_2020_JulOct_original_source_coastal_eligible_hours_by_taxon'].get(taxon,0)!=b[
              'native_original_2020_JulOct_coastal_bird_hours_in_eligible_tags'] or
            full_source_qa['original_2020_JulOct_original_eligible_bird_counts_by_taxon'].get(taxon,0)!=b[
                'true_2020_original_birds_with_ge20_coastal_hours']):
            raise ValueError('STOP_V126_2020_TRUE_BIRD_STEP_GENERATOR_CHANGED_FROM_V125')
    return {'prior_source_run':43216441141,'original_panel':panel,
            'all_v125_real_2020_source_animal_counts_and_hour_steps_replayed_exactly':True,
            'no_original_gull_GIC_Y_inspected_before_replay':True}

def get_gic_source_gate(events,panel,parsed):
    """Only missingness, not score sign, drives panel admission.
    Biological values are not scored until 90% GIC and bird gates pass.
    """
    if not len(events):
        return {'status':'NOT_ADMITTED_NO_REAL_2020_JUL_AUG_SOURCE_STEP',
                'source_gic_all8_fraction':None}
    spec=FOCAL
    true_bird_months=defaultdict(lambda:defaultdict(int))
    original_bird_steps=defaultdict(int)
    good_bird_steps=defaultdict(int)
    nvalid=0
    for e in events:
        species=e['taxon'];bird=e['bird'];month=e['month']
        true_bird_months[(species,bird)][month]+=1
        original_bird_steps[(species,bird)]+=1
        valid=(e.get('v115_real_2020_GPS_destination_native_GIC_RF') is not None
             and e.get('v115_7_original_same_step_rotated_GIC_RF') is not None)
        if valid:good_bird_steps[(species,bird)]+=1;nvalid+=1
    expected=FOCAL[0] if panel=='HG_OOSTENDE' else FOCAL[1]
    actual_birds={bird for taxon,bird in true_bird_months if taxon==expected}
    native_birds_with20={bird for (taxon,bird),n in good_bird_steps.items()
                         if taxon==expected and n>=MIN_BIRD_COMPLETE_GIC_STEPS}
    support_months=[]
    for month in SEASON:
        num=sum(true_bird_months[(expected,bird)].get(month,0)>0 for bird in actual_birds)
        hours=sum(true_bird_months[(expected,bird)].get(month,0) for bird in actual_birds)
        # A month is source-admissible by movement-step sample only if >=3
        # real bird IDs and >=150 original steps; no map Y threshold.
        if num>=MIN_MONTH_BIRDS and hours>=MIN_MONTH_HOURS:
            support_months.append(month)
    fraction=nvalid/len(events)
    passed=(len(native_birds_with20)>=MIN_2020_TAGGED_BIRDS and
        len(events)>=MIN_2020_SOURCE_GIC_STEPS and len(support_months)>=2
        and fraction>=SOURCE_GIC_ALL8_MIN_VALID)
    return {'status':'ORIGINAL_PUBLISHED_GIC_2020_EIGHT_PIXEL_SOURCE_ADMITTED' if passed
                            else 'NOT_ESTIMATED_SOURCE_BIRD_OR_GIC_PIXELS',
       'frozen_panel':panel,'fixed_original_expected_taxon':expected,
       'original_year_source_steps_JulAug_total':len(events),
       'original_native_GIC_all8_valid_steps':nvalid,
       'original_native_GIC_source_complete_fraction':fraction,
       'original_independent_2020_birds_with_real_JulAug_source_steps':len(actual_birds),
       'original_2020_birds_with_ge20_native_complete_GIC_step_controls':len(native_birds_with20),
       'original_months_with_ge3_birds_and_150_source_steps':support_months,
       'source_gic_valid_atleast90pct':fraction>=SOURCE_GIC_ALL8_MIN_VALID,
       'source_true_bird_support_minimum5':len(native_birds_with20)>=MIN_2020_TAGGED_BIRDS,
       'source_no_actual_dry_substrate_or_local_tide_information':True}

def source_sun_label(event):
    solar=float(elevation(Observer(latitude=event['GPS_departure_lat'],
             longitude=event['GPS_departure_lon']),event['original_UTC']))
    return 'day' if solar>SUN_DAY_GT else 'night' if solar<SUN_NIGHT_LT else 'twilight'

def compute_bird_equal_original_Z(events,gate,panel):
    if gate.get('status')!='ORIGINAL_PUBLISHED_GIC_2020_EIGHT_PIXEL_SOURCE_ADMITTED':
        return {'status':'NOT_ESTIMATED_BELGIAN_GIC_OR_BIRD_SOURCE_GATE'}
    expected=FOCAL[0] if panel=='HG_OOSTENDE' else FOCAL[1]
    monthly=defaultdict(lambda:defaultdict(list))
    original_solar=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    solar_dates=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
    nvalid=0
    for e in events:
        if e['taxon']!=expected:continue
        used=e.get('v115_real_2020_GPS_destination_native_GIC_RF')
        alternative=e.get('v115_7_original_same_step_rotated_GIC_RF')
        if used is None or alternative is None:continue
        other=np.array(alternative,dtype=float)
        if len(other)!=RAYS or not np.isfinite(other).all() or not isfinite(used):
            raise ValueError('STOP_V126_GIC_SOURCE_EIGHT_ENDPOINTS_NOT_VALID')
        if not (0<=used<=100 and np.all((0<=other)&(other<=100))):
            raise ValueError('STOP_V126_GIC_NATIVE_RF_OUTSIDE_0_100')
        Z=float(used>=GIC_CLASS_RF_THRESHOLD)-float(np.mean(other>=GIC_CLASS_RF_THRESHOLD))
        if not -1.00000001<=Z<=1.00000001:
            raise ValueError('STOP_V126_LOCAL_GIC_STEP_ENRICHMENT_OUTSIDE_MINUS1_PLUS1')
        monthly[e['bird']][e['month']].append(Z)
        label=source_sun_label(e)
        if label in ('day','night'):
            original_solar[e['bird']][e['month']][label].append(Z)
            solar_dates[e['bird']][e['month']][label].add(e['original_UTC'].date())
        nvalid+=1
    samples=[]
    for bird,months in monthly.items():
        if sum(len(x) for x in months.values())<MIN_BIRD_COMPLETE_GIC_STEPS:continue
        samples.append(float(mean(mean(Z) for Z in months.values())))
    if len(samples)<MIN_2020_TAGGED_BIRDS:
        raise ValueError('STOP_V126_SOURCE_BIRD_COUNT_CHANGED_AFTER_GIC_GATE')
    values=np.array(samples,dtype=float)
    seed=BOOT_SEED_BASE+{'HG_OOSTENDE':1,'LBBG_ZEEBRUGGE':2,'LBBG_JUVENILE':3}[panel]
    rng=np.random.default_rng(seed)
    draw=values[rng.integers(0,len(values),size=(BOOT_REPS,len(values)))].mean(axis=1)
    sun_samples=[]
    for bird,months in original_solar.items():
        per_month=[]
        for month,conditions in months.items():
            if (len(conditions.get('day',[]))>=5 and len(conditions.get('night',[]))>=5 and
                len(solar_dates[bird][month]['day'])>=3 and
                len(solar_dates[bird][month]['night'])>=3):
                per_month.append(float(mean(conditions['night'])-mean(conditions['day'])))
        if per_month:sun_samples.append(float(mean(per_month)))
    if len(sun_samples)>=MIN_2020_TAGGED_BIRDS:
        s=np.array(sun_samples)
        sd=s[rng.integers(0,len(s),size=(BOOT_REPS,len(s)))].mean(axis=1)
        solar={'status':'EXPLORATORY_BELGIAN_SOLAR_ONLY_LOCATION_ENRICHMENT',
           'source_birds_with_true_solar_DAY_NIGHT_per_month_support':len(s),
           'original_solar_night_minus_day_Zmean':float(s.mean()),
           'true_bird_bootstrap95':np.quantile(sd,[.025,.975]).tolist()}
    else:
        solar={'status':'NOT_ESTIMATED_SOLAR_DAY_NIGHT_SOURCE_GATE',
               'n_true_birds_with_valid_source_day_night':len(sun_samples)}
    return {'status':'EXPLORATORY_EXTERNAL_2020_BELGIAN_GULL_GIC_SAME_REAL_STEP_SPATIAL_ENRICHMENT',
       'original_2020_true_independent_birds_scored':len(values),
       'original_true_year_2020_JulAug_valid_GIC_used_plus_seven_source_steps':nvalid,
       'primary_per_bird_equal_month_equal_B_GIC_RF50_step_enrichment':float(values.mean()),
       'primary_10000_original_tagged_bird_bootstrap95':np.quantile(draw,[.025,.975]).tolist(),
       'original_tagged_birds_with_positive_spatial_enrichment':int(np.sum(values>0)),
       'primary_original_B_bootstrap_draws_anonymized_cohort_aggregate':draw.tolist(),
       'secondary_solar_DAY_NIGHT_source_scored_with_own_missingness_gate':solar,
       'source_original_2020_juvenile_vs_adult_category':('juvenile' if panel=='LBBG_JUVENILE' else 'adult'),
       'NO_TRUE_2020_TIDE_RISING_EBB_OR_SOLAR_INTERACTION_ESTIMATED':True,
       'NO_ORIGINAL_BIRD_ID_OR_GPS_TIME_OR_COORDINATES_EXPORTED':True}
