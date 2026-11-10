"""v111 genuine 2020 two-gull movement *proxy* conditional on observed tide and solar altitude.

Source first, outcome later. Input: independently publisher-MD5 authenticated
DELTATRACK 2020 bird positions and Rijkswaterstaat original 10-minute NAP
heights from frozen Roompotsluis Buiten. Movement displacement is NOT true
foraging, flight, activity time budget, or internal circatidal clock.
"""
from __future__ import annotations

from bisect import bisect_left
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from math import atan2,cos,floor,log1p,radians,sin,sqrt
import json
import numpy as np
from astral import Observer
from astral.sun import elevation

from original_2020_gull_RWS_source import (
    SOURCE_MONTHS,GEO_PRIMARY,GEO_RADIUS_PRIMARY_KM,PHYSICAL_SPEED_QA_MAX_KMH,
    RWS_SLOPE_MIN_METRES_PER_H)
from original_delta_2020_gull_source import FOCAL

SOURCE_HALF_WINDOW_MIN=7.5
PREVIOUS_STAGE_MIN=20
MIN_PAIR_HOURS=.75
MAX_PAIR_HOURS=1.5
PRIMARY_GAUGE_RADIUS_KM=20.
HEIGHT_BAND_METRES=.25
DAY_SOLAR_GT=3.
NIGHT_SOLAR_LT=-3.
MIN_FIXES_PER_SOURCE_CELL=5
MIN_UTC_DATES_PER_CELL=3
MIN_SOURCE_ORIGINAL_BIRDS=8
MIN_SOURCE_FOURCELL_GROUPS=20
MIN_SOURCE_MOVEMENTS=1000
MIN_SOURCE_MONTHS=2
WHOLE_BIRD_BOOTSTRAP_REPS=10000
RNG_SEED=20261110
PHASE_GHOST_DAY_SHIFTS=(3,7,11)
CELL_CLASSES=((1,'day'),(1,'night'),(-1,'day'),(-1,'night'))

def great_circle_km(lat1,lon1,lat2,lon2):
    a1,a2=radians(lat1),radians(lat2)
    dl=radians(lon2-lon1)
    da=a2-a1
    aa=sin(da/2)**2+cos(a1)*cos(a2)*sin(dl/2)**2
    return 12742.*atan2(sqrt(max(0.,aa)),sqrt(max(0.,1-aa)))

def nearest_original_rws(tide,sorted_times,utc):
    """Nearest native measured original gauge stamp, NO interpolation, with source 20-min slope."""
    if utc.tzinfo is None:
        raise ValueError('STOP_GPS_UTC_NOT_OFFSET_AWARE_FOR_RWS_TIDE_MATCH')
    index=bisect_left(sorted_times,utc)
    candidates=[v for v in (index-1,index) if 0<=v<len(sorted_times)]
    if not candidates:return None
    t=min((sorted_times[i] for i in candidates),key=lambda x:abs((x-utc).total_seconds()))
    if abs((t-utc).total_seconds())>SOURCE_HALF_WINDOW_MIN*60:return None
    earlier=t-timedelta(minutes=PREVIOUS_STAGE_MIN)
    if earlier not in tide:return None
    h=tide[t]
    h0=tide[earlier]
    slope=(h-h0)*(60./PREVIOUS_STAGE_MIN)
    if abs(slope)<=RWS_SLOPE_MIN_METRES_PER_H:return None
    return {'source_stage_mNAP':h,'source_phase':1 if slope>0 else -1,
        'source_height_bin':int(floor(h/HEIGHT_BAND_METRES)),
        'native_observed_height_time':t,
        'native_real_20min_slope_mph':slope}

def sunlight_label_at_native_gps(dt_utc,lat,lon):
    if dt_utc.tzinfo is None:raise ValueError('STOP_GPS_UTC_SUN_TIMESTAMP_UNAWARE')
    solar=float(elevation(Observer(latitude=lat,longitude=lon,elevation=0.),dt_utc))
    return 'day' if solar>DAY_SOLAR_GT else 'night' if solar<NIGHT_SOLAR_LT else 'twilight'

def original_movement_opportunities(native_bird_hour,reference_center=GEO_PRIMARY,radius=PRIMARY_GAUGE_RADIUS_KM):
    """Check pre-declared original biological sample opportunities, before tidal response."""
    if radius not in (10.,20.,30.):
        raise ValueError('STOP_NONPREDECLARED_GPS_POINT_RADIUS')
    raw_pairs=0
    qa=Counter()
    events=[]
    birds=Counter()
    for (taxon,bird),hours in sorted(native_bird_hour.items()):
        if taxon not in FOCAL:continue
        positions=sorted(hours.values(),key=lambda p:p[0])
        for old,nxt in zip(positions,positions[1:]):
            raw_pairs+=1
            t0,lat0,lon0=old
            t1,lat1,lon1=nxt
            elapsed=(t1-t0).total_seconds()/3600
            if not MIN_PAIR_HOURS<=elapsed<=MAX_PAIR_HOURS:
                qa['original_GPS_elapsed_outside_0p75_to_1p5hours']+=1;continue
            if t0.month not in SOURCE_MONTHS or t1.month not in SOURCE_MONTHS:
                qa['outside_original_both_species_common_months']+=1;continue
            d0=great_circle_km(lat0,lon0,*reference_center)
            d1=great_circle_km(lat1,lon1,*reference_center)
            if d0>radius or d1>radius:
                qa['GPS_endpoint_outside_official_gauge_fixed_radius']+=1;continue
            km=great_circle_km(lat0,lon0,lat1,lon1)
            speed=km/elapsed
            if speed>PHYSICAL_SPEED_QA_MAX_KMH:
                qa['GPS_nonphysical_displacement_speed_above150kmh']+=1;continue
            dt=t0.replace(tzinfo=timezone.utc)
            events.append({'bird':bird,'taxon':taxon,'original_UTC':dt,'month':t0.month,
                'GPS_departure_lat':lat0,'GPS_departure_lon':lon0,
                'original_elapsed_hours':elapsed,'original_km_per_hour':speed})
            birds[taxon]+=1
    qa['original_all_consecutive_bird_hour_pairs']=raw_pairs
    qa['original_eligible_source_movement_pairs_before_tide_or_sun']=len(events)
    return events,{'source_qa_exclusion_and_opportunity_counts':dict(qa),
        'source_unique_original_birds_by_species_with_any_movement_opportunities':
         {species:len({v['bird'] for v in events if v['taxon']==species}) for species in sorted(FOCAL)},
        'source_radius_km':radius,'SOURCE_ONLY_no_speed_endpoint_statistic_scored':True}

def fourway_original_source(events,rws_real_tide,source_ghost_shift_days=0):
    """Cells are admitted from original *timestamps*, species, tide, day/night, NOT speed Y."""
    sorted_times=sorted(rws_real_tide)
    allcells=defaultdict(list)
    qa=Counter()
    n_solar_by_species=defaultdict(Counter)
    for e in events:
        loc_utc=e['original_UTC']
        sun=sunlight_label_at_native_gps(loc_utc,e['GPS_departure_lat'],e['GPS_departure_lon'])
        n_solar_by_species[e['taxon']][sun]+=1
        if sun=='twilight':
            qa['excluded_real_astro_twilight']+=1;continue
        gauge_match=nearest_original_rws(rws_real_tide,sorted_times,
            loc_utc+timedelta(days=source_ghost_shift_days))
        if gauge_match is None:
            qa['no_real_RWS_measured_source_with_20min_phase_in_7p5min']+=1;continue
        key=(e['taxon'],e['bird'],e['month'],gauge_match['source_height_bin'])
        k=(gauge_match['source_phase'],sun)
        allcells[key,k].append(e)
        qa['matched_original_GPS_speed_source_intervals']+=1
    admitted=defaultdict(dict)
    by_species=defaultdict(lambda:Counter())
    for key in {k[0] for k in allcells}:
        sub={cell:allcells.get((key,cell),[]) for cell in CELL_CLASSES}
        complete=(all(len(sub[cell])>=MIN_FIXES_PER_SOURCE_CELL and
            len({z['original_UTC'].date() for z in sub[cell]})>=MIN_UTC_DATES_PER_CELL
            for cell in CELL_CLASSES))
        if not complete:continue
        admitted[key]=sub
        by_species[key[0]]['source_fourcell_strata']+=1
        by_species[key[0]]['source_actual_GPS_hour_intervals_in_fourcell']+=sum(len(v) for v in sub.values())
    summaries={}
    for species in sorted(FOCAL):
        groups=[k for k in admitted if k[0]==species]
        tags={g[1] for g in groups}
        months={g[2] for g in groups}
        n_intervals=sum(sum(len(x) for x in admitted[g].values()) for g in groups)
        conditions={'source_min8_genuine_birds':len(tags)>=MIN_SOURCE_ORIGINAL_BIRDS,
             'source_min20_birdmonthheight_complete_strata':len(groups)>=MIN_SOURCE_FOURCELL_GROUPS,
             'source_min1000_original_true_move_intervals':n_intervals>=MIN_SOURCE_MOVEMENTS,
             'source_min2_original_calendar_months':len(months)>=MIN_SOURCE_MONTHS}
        summaries[species]={'source_fourcell_eligible_original_birds':len(tags),
            'source_fourcell_true_bird_month_height_strata':len(groups),
            'source_fourcell_original_GPS_hour_movements':n_intervals,
            'source_fourcell_distinct_calendar_months':len(months),
            'source_all_fixed_conditions':conditions,
            'SOURCE_ADMITTED_2020_TWO_GULL_MOVEMENT_TIDE_SUN':all(conditions.values())}
    final={
       'original_source_all_species':summaries,
       'source_each_species_admitted':all(z['SOURCE_ADMITTED_2020_TWO_GULL_MOVEMENT_TIDE_SUN']
                                          for z in summaries.values()),
       'native_source_gauge_phase_shift_days_NOT_GPS_time':source_ghost_shift_days,
       'source_twilight_tide_coverage_QA':dict(qa),
       'source_sunlight_GPS_opportunities_by_species':
           {k:dict(v) for k,v in n_solar_by_species.items()},
       'no_individual_GPS_event_or_bird_tags_exported':True}
    return admitted,final

def original_bird_mean_effects(admitted,species):
    """ONLY call after source gate for both taxa. Original full supported fourcell source."""
    bybird_month=defaultdict(lambda:defaultdict(list))
    for (taxon,bird,month,_height),cells in admitted.items():
        if taxon!=species:continue
        mu={(phase,sun):float(np.mean([log1p(z['original_km_per_hour']) for z in seq]))
            for (phase,sun),seq in cells.items()}
        D=(mu[(1,'night')]-mu[(1,'day')])-(mu[(-1,'night')]-mu[(-1,'day')])
        bybird_month[bird][month].append(D)
    values={}
    for bird,months in bybird_month.items():
        values[bird]=float(np.mean([np.mean(v) for v in months.values()]))
    return values

def score_if_original_two_species_admitted(admitted,source_summary,seed=RNG_SEED):
    if not source_summary.get('source_each_species_admitted'):
        return {'status':'NOT_ESTIMATED_ORIGINAL_BIOLOGICAL_SOURCE_GATE',
            'source_failures_include_valid_Schier_GIC_and_other_old_results':True}
    original={s:original_bird_mean_effects(admitted,s) for s in sorted(FOCAL)}
    names=sorted(FOCAL)
    rng=np.random.default_rng(seed)
    arrays={s:np.array(list(v.values()),dtype=float) for s,v in original.items()}
    boot={}
    report={}
    for s in names:
        a=arrays[s]
        draws=a[rng.integers(0,len(a),size=(WHOLE_BIRD_BOOTSTRAP_REPS,len(a)))].mean(axis=1)
        boot[s]=draws
        report[s]={'true_original_independent_birds':len(a),
           'real_original_bird_equal_tidal_phase_by_sun_interaction_D':float(a.mean()),
           'original_bird_whole_cluster_bootstrap_10000_CI95':np.quantile(draws,[.025,.975]).tolist(),
           'number_of_original_birds_with_positive_D':int(np.sum(a>0)),
           'original_bird_D_not_exported':True}
    contrast=boot[names[0]]-boot[names[1]]
    p=float(arrays[names[0]].mean()-arrays[names[1]].mean())
    return {'status':'EXPLORATORY_REAL_2020_TWO_SPECIES_MOVEMENT_PROXY_EFFECT_ESTIMATED',
        'species_source_results':report,
        'contrast_order':f'{names[0]} minus {names[1]}',
        'primary_two_species_bird_equal_D_difference':p,
        'primary_two_species_original_bird_cluster_bootstrap95':
            np.quantile(contrast,[.025,.975]).tolist(),
        'primary_two_species_source_sign_status': 'EXPLORATORY_BIRD_CLUSTER_POSITIVE' if
             np.quantile(contrast,.025)>0 else 'EXPLORATORY_BIRD_CLUSTER_NEGATIVE' if
             np.quantile(contrast,.975)<0 else 'NOT_ESTABLISHED',
        'source_measure':'log1p(original hourly GPS displacement km/hour), NOT observed foraging or activity',
        'source_no_raw_GPS_ID_or_times_exported':True}
