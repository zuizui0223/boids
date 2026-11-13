"""v127 genuine original 2019 Vlieland Eurasian oystercatcher ACC-predicted
FORAGE/INACTIVE share from 15-minute same-bird GPS-linked source × original
Rijkswaterstaat Vlieland Haven 10-minute observed 2019 tide and true SUN.

The class labels are ACC algorithm inferences, NOT observed prey ingestion,
calibrated foraging minutes, local dry-flat availability, or an internal clock.
Do not pool events as independent animals. Old source records/bird IDs, GPS
coordinates and timestamps remain ephemeral, never in GitHub artifacts.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import timedelta,timezone
from math import floor
import numpy as np
from astral import Observer
from astral.sun import elevation
from two_gull_tide_solar_fourway import nearest_original_rws

ORIGINAL_YEAR=2019
COMMON_MONTHS=(6,7,8,9)
STATION_SOURCE='vlieland.haven'
FIXED_TIDE_HEIGHT_BAND_M=.25
SOLAR_DAY_GT=3.
SOLAR_NIGHT_LT=-3.
MIN_15MIN_BINS_PER_CONDITION=5
MIN_SOURCE_DATES_PER_CONDITION=3
MIN_BIRDS_FOR_FIELD_SCORE=8
MIN_BIRD_MONTH_STAGE_GROUPS=20
MIN_ORIGINAL_15MIN_BINS=1000
MIN_SOURCE_MONTHS=2
WHOLE_BIRD_BOOT_N=10000
RNG_SEED=20261112
GHOST_DAYS=(3,7,11)
SOURCE_CELL_CLASSES=((1,'day'),(1,'night'),(-1,'day'),(-1,'night'))
BASIS=('B_balanced_forage_share','S_night_minus_day',
       'T_rising_minus_falling','I_rising_vs_falling_by_night_vs_day')

def original_2019_gps_acc_quarterhour_source(private):
    """Only previous genuine-v126 same tagged bird ±15min GPS-linked bins,
    no new source refitting, and EXACT four fixed original 2019 months.
    """
    out=[];qa=Counter();orig_birds=set()
    for (bird,bin_time),row in private.items():
        if bin_time.year!=ORIGINAL_YEAR or bin_time.month not in COMMON_MONTHS:
            raise ValueError('STOP_V127_PRIVATE_SOURCE_NONFROZEN_YEAR_OR_MONTH')
        if bird!=row['private_bird'] or bin_time!=row['native_UTC_15min_bin']:
            raise ValueError('STOP_V127_2019_SOURCE_BIRD_QUARTERHOUR_INCONSISTENT')
        n_f=row['n_native_forage_classifier_events']
        n_i=row['n_native_inactive_classifier_events']
        if not (isinstance(n_f,int) and isinstance(n_i,int) and n_f>=0 and n_i>=0 and n_f+n_i>0):
            raise ValueError('STOP_V127_ORIGINAL_CLASSIFICATION_COUNT_NOT_POSITIVE')
        utc=row['earliest_true_classification_UTC'].replace(tzinfo=timezone.utc)
        la=float(row['original_same_bird_GPS_latitude'])
        lo=float(row['original_same_bird_GPS_longitude'])
        if not(-90<=la<=90 and -180<=lo<=180):
            raise ValueError('STOP_V127_ORIGINAL_GPS_WGS84_INVALID')
        if not (0<=(utc.replace(tzinfo=None)-bin_time).total_seconds()<900):
            raise ValueError('STOP_V127_ORIGINAL_UTC_QUARTERHOUR_EARLIEST_EVENT_DRIFT')
        out.append({'private_bird':bird,'source_month':bin_time.month,
            'source_utc_event':utc,'source_lat':la,'source_lon':lo,
            'original_acc_forage_events':n_f,'original_acc_inactive_events':n_i})
        qa['true_2019_original_linked_bird_quarterhour_source_bins']+=1
        qa['source_native_forage_class_events_in_all_15minute_bins']+=n_f
        qa['source_native_inactive_class_events_in_all_15minute_bins']+=n_i
        qa['native_15minute_bins_with_mixed_both_labels']+=int(n_f>0 and n_i>0)
        orig_birds.add(bird)
    return out,{'original_2019_true_source_bin_n':len(out),
          'source_classes_from_original_same_bird_GPS':dict(qa),
          'source_original_distinct_genuine_birds_6_9':len(orig_birds),
          'one_native_bin_per_original_bird_per_UTC_quarterhour':True,
          'no_private_original_bird_identifiers_or_UTC_GPS_exported':True}

def _solar_label(timestamp,lat,lon):
    if timestamp.tzinfo is None:
        raise ValueError('STOP_V127_UTC_TIME_NOT_TZ_AWARE')
    deg=float(elevation(Observer(latitude=lat,longitude=lon,elevation=0),timestamp))
    return 'day' if deg>SOLAR_DAY_GT else 'night' if deg<SOLAR_NIGHT_LT else 'twilight'

def source_real_tide_sun_fourway(original_bins,true_RWS,ghost_shift_days=0):
    """ALL SOURCE GATES depend on original UTC/date/observed RWS/astronomy
    and source bin count, NEVER observed class SHARE response Y.
    """
    if ghost_shift_days not in (0,)+GHOST_DAYS:
        raise ValueError('STOP_V127_TIDE_GHOST_SHIFT_NOT_FROZEN')
    tiderows=sorted(true_RWS)
    allcells=defaultdict(list)
    qa=Counter()
    by_month=defaultdict(Counter)
    effort=defaultdict(Counter)
    for e in original_bins:
        s=_solar_label(e['source_utc_event'],e['source_lat'],e['source_lon'])
        effort[e['source_month']][s]+=1
        if s=='twilight':
            qa['source_astronomical_twilight_excluded']+=1
            continue
        matched=nearest_original_rws(true_RWS,tiderows,
            e['source_utc_event']+timedelta(days=ghost_shift_days))
        if matched is None:
            qa['source_RWS_not_within_7p5min_or_slack_tide']+=1
            continue
        k=(e['private_bird'],e['source_month'],matched['source_height_bin'])
        cell=(matched['source_phase'],s)
        allcells[(k,cell)].append(e)
        qa['true_original_tide_solar_matched_gps_acc_15min_bins']+=1
        by_month[e['source_month']]['RWS_and_sun_source_matched_bins']+=1
    accepted={}
    source_n_by_month=defaultdict(Counter)
    for key in {k for k,_ in allcells}:
        cells={c:allcells.get((key,c),[]) for c in SOURCE_CELL_CLASSES}
        if not all(len(items)>=MIN_15MIN_BINS_PER_CONDITION and
                   len({v['source_utc_event'].date() for v in items})>=MIN_SOURCE_DATES_PER_CONDITION
                   for items in cells.values()):
            continue
        accepted[key]=cells
        source_n_by_month[key[1]]['native_bird_month_stage_fourcell_groups']+=1
        source_n_by_month[key[1]]['source_15minute_acc_gps_RWS_sun_bins']+=sum(len(v) for v in cells.values())
    birds={key[0] for key in accepted}
    months={key[1] for key in accepted}
    admitted_n=sum(sum(len(v) for v in cells.values()) for cells in accepted.values())
    gate={
      'true_original_unique_birds_in_complete_fourcell_source':len(birds),
      'true_original_bird_month_0p25m_RWS_height_fourcell_groups':len(accepted),
      'true_original_15minute_bins_in_complete_fourcell_source':admitted_n,
      'true_original_supported_2019_months':sorted(months),
      'birds_at_least_8':len(birds)>=MIN_BIRDS_FOR_FIELD_SCORE,
      'fourcell_groups_at_least_20':len(accepted)>=MIN_BIRD_MONTH_STAGE_GROUPS,
      'original_15minute_bins_at_least_1000':admitted_n>=MIN_ORIGINAL_15MIN_BINS,
      'original_source_months_at_least_2':len(months)>=MIN_SOURCE_MONTHS
    }
    eligible=all(gate[k] for k in ('birds_at_least_8','fourcell_groups_at_least_20',
         'original_15minute_bins_at_least_1000','original_source_months_at_least_2'))
    source={'source_status':'TRUE_2019_GPS_ACC_RWS_TIDE_SUN_FOURCELL_GATED',
      'original_2019_RWS_tide_clock_day_ghost_shift':ghost_shift_days,
      'original_2019_RWS_vlieland_haven_stage_not_local_h_x_t':True,
      'original_ACC_15min_not_actual_forage_minutes':True,
      'true_original_source_all_four_conditions':gate,
      'true_original_source_admitted_before_forage_share_Y':eligible,
      'source_UTC_daylight_night_twilight_effort_by_month':{
          str(k):dict(v) for k,v in sorted(effort.items())},
      'source_2019_months_fourcell_support':{str(k):dict(v)
            for k,v in sorted(source_n_by_month.items())},
      'source_2019_RWS_tide_sun_link_QA':dict(qa),
      'source_bird_and_native_full_fourcell_gates_not_based_on_Y':True}
    return accepted,source

def original_true_bird_BSTI_from_ACC_source(accepted,source,seed=RNG_SEED):
    if not source.get('true_original_source_admitted_before_forage_share_Y'):
        return {'outcome_status':'NOT_ESTIMATED_ORIGINAL_2019_BEHAVIOUR_TIDE_SUN_SOURCE_GATE',
                'none_of_the_original_ACC_foraging_15min_outcomes_scored':True}
    by_bird=defaultdict(lambda:defaultdict(list))
    all_classes=Counter(); group_QA=Counter()
    for (bird,month,height),cells in accepted.items():
        m={}
        for c,v in cells.items():
            Y=np.array([z['original_acc_forage_events']/
                         (z['original_acc_forage_events']+z['original_acc_inactive_events'])
                         for z in v],dtype=float)
            if len(Y)<MIN_15MIN_BINS_PER_CONDITION or not np.isfinite(Y).all():
                raise ValueError('STOP_V127_TRUE_BEHAVIOR_SOURCE_MISSING_OR_NONFINITE_15MIN_SHARE')
            m[c]=float(Y.mean())
            all_classes[f'{c[0]}_{c[1]}_original_15min_bins']+=len(Y)
            all_classes[f'{c[0]}_{c[1]}_original_forage_events']+=sum(x['original_acc_forage_events'] for x in v)
            all_classes[f'{c[0]}_{c[1]}_original_inactive_events']+=sum(x['original_acc_inactive_events'] for x in v)
        fd,fn,ed,en=m[(1,'day')],m[(1,'night')],m[(-1,'day')],m[(-1,'night')]
        by_bird[bird][month].append({
            BASIS[0]:(fd+fn+ed+en)/4.,
            BASIS[1]:((fn-fd)+(en-ed))/2.,
            BASIS[2]:((fn-en)+(fd-ed))/2.,
            BASIS[3]:(fn-fd)-(en-ed)})
        group_QA['true_bird_month_height_4cell_groups_scored']+=1
    birds={}
    for bird,months in by_bird.items():
        birds[bird]=[float(np.mean([
              np.mean([row[k] for row in month_rows])
              for month_rows in months.values()])) for k in BASIS]
    if len(birds)!=source['true_original_source_all_four_conditions'][
          'true_original_unique_birds_in_complete_fourcell_source']:
        raise ValueError('STOP_V127_TRUE_ORIGINAL_TAGGED_BIRD_ID_SOURCE_DRIFT_AFTER_GATE')
    vals=np.asarray(list(birds.values()),dtype=float)
    if vals.ndim!=2 or vals.shape[1]!=len(BASIS):
        raise ValueError('STOP_V127_ORIGINAL_SOURCE_BIRD_BSTI_DIMENSIONS')
    rng=np.random.default_rng(seed)
    boot=vals[rng.integers(0,len(vals),size=(WHOLE_BIRD_BOOT_N,len(vals)))].mean(axis=1)
    outputs={}
    for i,k in enumerate(BASIS):
        lo,hi=np.quantile(boot[:,i],[.025,.975])
        outputs[k]={
          'true_original_individual_equal_weight_mean':float(vals[:,i].mean()),
          'genuine_10000_independent_tagged_bird_bootstrap_CI95':[float(lo),float(hi)],
          'original_tagged_birds_with_positive_coefficient':int((vals[:,i]>0).sum()),
          'nominal_exploratory_sign_status':'POSITIVE' if lo>0 else 'NEGATIVE' if hi<0 else 'NOT_ESTABLISHED'}
    return {'outcome_status':'ORIGINAL_2019_VLIELAND_CLASSIFIED_FORAGE_SHARE_TIDE_SUN_OBSERVATIONAL_ESTIMATED',
      'original_independent_tagged_birds_N':len(birds),
      'original_complete_fourway_bird_month_height_groups':group_QA[
            'true_bird_month_height_4cell_groups_scored'],
      'source_response':'ACC-classified forage/(forage+inactive) per original GPS-linked bird×15min sensor window, not feeding minutes',
      'original_true_bird_B_S_T_I_results':outputs,
      'original_2019_fourcell_binary_class_raw_observation_effort':dict(all_classes),
      'native_ACC_bursty_event_count_not_bird_replicates':True,
      'original_bird_ID_or_exact_15min_source_Y_NOT_exported':True,
      'NO_causal_activity_or_food_intake_or_internal_clock_inferred':True}
