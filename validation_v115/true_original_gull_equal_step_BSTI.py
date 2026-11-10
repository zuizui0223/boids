"""v115 original 2020 two-gull equal-real-step rotated GIC RF endpoint vs seven alternatives.

This is a geodesic KINEMATIC counterfactual map source, NOT real animal
reachability, actual tidalflat drying, active feeding, internal tide clock or
an independent sample of bird populations. Post-v114 exploratory.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from statistics import mean
from datetime import timedelta
import numpy as np
from original_delta_2020_gull_source import FOCAL
from two_gull_tide_solar_fourway import (
    CELL_CLASSES,original_movement_opportunities,
    fourway_original_source,score_if_original_two_species_admitted,
    sunlight_label_at_native_gps,nearest_original_rws,
    WHOLE_BIRD_BOOTSTRAP_REPS,RNG_SEED,MIN_SOURCE_ORIGINAL_BIRDS)
from original_GIC_equal_step_rotated_destinations import N_ALTERNATIVE_ENDPOINTS

ORIGINAL_V111_MOVEMENT_SOURCE={
    'Larus argentatus':{'birds':24,'strata':323,'fixes':17551,'D':-0.011272500645579784},
    'Larus fuscus':{'birds':15,'strata':64,'fixes':2985,'D':0.05520975431892319}}
ORIGINAL_V111_TAXON_CONTRAST=-0.06648225496450298
OLD_REPLAY_EPS=1e-10
COMMON_SOURCE_MONTHS=(5,6,7)
BASIS=('B_balanced_endpoint_enrichment','S_solar_night_minus_day',
       'T_tide_rising_minus_falling','I_tide_by_solar')

def hard_replay_original_v111_genuine_movement_effects(original_events,original_RWS):
    """Only the PREEXISTING true 2020 original bird movement source and effect, BEFORE new GIC endpoints."""
    groups,source=fourway_original_source(original_events,original_RWS)
    if not source['source_each_species_admitted']:
        raise ValueError('STOP_V115_OLD_2020_REAL_GULL_TIDE_SUN_MOVEMENT_SOURCE_NOT_ADMITTED')
    old=score_if_original_two_species_admitted(groups,source)
    if old.get('status')!='EXPLORATORY_REAL_2020_TWO_SPECIES_MOVEMENT_PROXY_EFFECT_ESTIMATED':
        raise ValueError('STOP_V115_OLD_GULL_SOURCE_MOVEMENT_EFFECT_NOT_REPLAYED')
    for name,ref in ORIGINAL_V111_MOVEMENT_SOURCE.items():
        q=source['original_source_all_species'][name]
        x=old['species_source_results'][name]
        if (q['source_fourcell_eligible_original_birds']!=ref['birds'] or
            q['source_fourcell_true_bird_month_height_strata']!=ref['strata'] or
            q['source_fourcell_original_GPS_hour_movements']!=ref['fixes']):
            raise ValueError('STOP_V115_OLD_GULL_NATIVE_BIRD_MONTH_STAGE_SOURCE_CHANGED')
        if abs(x['real_original_bird_equal_tidal_phase_by_sun_interaction_D']-ref['D'])>OLD_REPLAY_EPS:
            raise ValueError('STOP_V115_OLD_GULL_REAL_MOVEMENT_D_EFFECT_CHANGED')
    if abs(old['primary_two_species_bird_equal_D_difference']-
            ORIGINAL_V111_TAXON_CONTRAST)>OLD_REPLAY_EPS:
        raise ValueError('STOP_V115_OLD_GULL_REAL_MOVEMENT_SPECIES_CONTRAST_CHANGED')
    return {'source_status':'ORIGINAL_2020_V111_MOVEMENT_TWO_SPECIES_EXACT_SOURCE_AND_Y_REPLAY_BEFORE_NEW_GIC',
      'original_v111_public_source_action':42748780612,
      'original_native_previous_year_two_species_source':ORIGINAL_V111_MOVEMENT_SOURCE,
      'original_v111_true_species_movement_D_replayed':{
         k:v['real_original_bird_equal_tidal_phase_by_sun_interaction_D']
         for k,v in old['species_source_results'].items()},
      'true_original_species_contrast_D_replayed':old['primary_two_species_bird_equal_D_difference'],
      'no_individual_GPS_coordinates_source_tide_or_per_bird_D_exported':True}

def source_GIC_seven_control_coverage_on_RWS_matched(original_events,rws,day_shift=0):
    if day_shift not in (0,3,7,11):
        raise ValueError('STOP_V115_UNFROZEN_REAL_RWS_GHOST_SHIFT')
    times=sorted(rws)
    qa=defaultdict(Counter)
    kept=[]
    for e in original_events:
        s=e['taxon']
        solar=sunlight_label_at_native_gps(e['original_UTC'],
               e['GPS_departure_lat'],e['GPS_departure_lon'])
        if solar=='twilight':
            qa[s]['original_gps_tide_solar_twilight']+=1;continue
        matched=nearest_original_rws(rws,times,
                   e['original_UTC']+timedelta(days=day_shift))
        if matched is None:
            qa[s]['original_rws_measured_tide_source_not_matched']+=1;continue
        qa[s]['original_RWS_tide_solar_matched_movement_intervals']+=1
        valid=e.get('v115_real_2020_GPS_destination_native_GIC_RF') is not None and (
             e.get('v115_7_original_same_step_rotated_GIC_RF') is not None)
        if valid:
            kept.append(e)
            qa[s]['native_GIC_used_endpoint_and_7_true_provider_pixel_source_valid']+=1
        else:
            qa[s]['native_GIC_actual_or_rotated_pixel_source_masked_or_missing']+=1
    coverage={}
    for s in sorted(FOCAL):
        d=qa[s]
        n=d['original_RWS_tide_solar_matched_movement_intervals']
        yes=d['native_GIC_used_endpoint_and_7_true_provider_pixel_source_valid']
        coverage[s]={'original_RWS_tide_sun_matched_true_bird_movement_pairs':n,
          'genuine_GIC_used_and_7_rotated_endpoint_all_source_valid':yes,
          'source_valid_fraction':float(yes/n) if n else None,
          'original_source_failure_counts':dict(d)}
    pass90=all(coverage[s]['source_valid_fraction'] is not None and coverage[s]['source_valid_fraction']>=.9 for s in FOCAL)
    return kept,{'source_7_same_step_candidates_valid_ge90pct_each_species':pass90,
       'predeclared_measured_2020_RWS_ghost_shift_days':day_shift,
       'real_RWS_and_solar_GIC_original_source_coverage':coverage,
       'both_taxa_GIC_mask_source_sample_is_not_Y_score':True}

def true_original_fourcell_source_with_endpoints(events,RWS,ghost=0):
    kept,coverage=source_GIC_seven_control_coverage_on_RWS_matched(events,RWS,day_shift=ghost)
    groups,admit=fourway_original_source(kept,RWS,source_ghost_shift_days=ghost)
    source={**admit,**coverage,
       'source_genuine_step_equal_length_seven_rotated_native_GIC_RF':True,
       'original_bird_and_all_GIC_source_admitted':bool(
           admit['source_each_species_admitted'] and
           coverage['source_7_same_step_candidates_valid_ge90pct_each_species'])}
    return groups,source

def true_original_group_coefficients(cells):
    if set(cells)!=set(CELL_CLASSES):
        raise ValueError('STOP_V115_ORIGINAL_GULL_4CELL_NOT_COMPLETE')
    mu={}
    for cell,events in cells.items():
        original=np.array([e['v115_real_2020_GPS_destination_native_GIC_RF'] for e in events],dtype=float)
        other=np.array([e['v115_7_original_same_step_rotated_GIC_RF'] for e in events],dtype=float)
        if not(len(original)>=5 and other.shape==(len(original),N_ALTERNATIVE_ENDPOINTS)
          and np.isfinite(original).all() and np.isfinite(other).all()):
            raise ValueError('STOP_V115_MISSING_ORIGINAL_GIC_GEO_STEP_SOURCE')
        if (original.min()<0 or original.max()>100 or other.min()<0 or other.max()>100):
            raise ValueError('STOP_V115_STATIC_GIC_TIDAL_WETLAND_VALUE_NOT_0_100')
        y=(original>=50).astype(float)-np.mean(other>=50,axis=1)
        if (y.min() < -1.0000001 or y.max()>1.0000001):
            raise ValueError('STOP_V115_SOURCE_ORIGINAL_USED_MINUS7_OUTSIDE_MINUS1_PLUS1')
        mu[cell]=float(y.mean())
    fd,fn,ed,en=(mu[(1,'day')],mu[(1,'night')],
                  mu[(-1,'day')],mu[(-1,'night')])
    return {
       'B_balanced_endpoint_enrichment':(fd+fn+ed+en)/4.,
       'S_solar_night_minus_day':((fn-fd)+(en-ed))/2.,
       'T_tide_rising_minus_falling':((fn-en)+(fd-ed))/2.,
       'I_tide_by_solar':(fn-fd)-(en-ed)}

def evaluate_real_original_bird_two_gull_step_BSTI(groups,source,seed=RNG_SEED):
    if not source.get('original_bird_and_all_GIC_source_admitted'):
        return {'status':'NOT_ESTIMATED_GENUINE_2020_2SPECIES_RWS_7ROTATED_GIC_SOURCE_GATE'}
    perbird=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    for (taxon,bird,month,height),cells in groups.items():
        coef=true_original_group_coefficients(cells)
        perbird[taxon][bird][month].append(coef)
    out={};draw={}
    rng=np.random.default_rng(seed)
    for s in sorted(FOCAL):
        arr=np.array([[float(np.mean([
               np.mean([d[k] for d in groupsh]) for groupsh in months.values()]))
                    for k in BASIS] for months in perbird[s].values()],dtype=float)
        if arr.ndim!=2 or arr.shape[0]<MIN_SOURCE_ORIGINAL_BIRDS or arr.shape[1]!=len(BASIS):
            raise ValueError('STOP_V115_ORIGINAL_TRUE_GULL_BIRD_BOOTSTRAP_SOURCE_TOO_SMALL')
        boot=arr[rng.integers(0,len(arr),size=(WHOLE_BIRD_BOOTSTRAP_REPS,len(arr)))].mean(axis=1)
        draw[s]=boot
        out[s]={'original_true_independent_bird_n':len(arr),
          'original_genuine_fourcell_birdmonth_height_n':source['original_source_all_species'][s][
                'source_fourcell_true_bird_month_height_strata'],
          'genuine_source_geodesic_used_minus7_B_S_T_I':{
             k:{'original_independent_bird_equal_mean':float(arr[:,i].mean()),
               'original_10000_true_bird_cluster_CI95':np.quantile(boot[:,i],[.025,.975]).tolist(),
               'native_true_birds_positive_responding':int((arr[:,i]>0).sum())}
              for i,k in enumerate(BASIS)},
          'no_original_bird_ID_or_2020_GPS_coordinates_exported':True}
    a,b=sorted(FOCAL)
    diff=draw[a]-draw[b]
    contrasts={}
    for i,k in enumerate(BASIS):
        effect=out[a]['genuine_source_geodesic_used_minus7_B_S_T_I'][k]['original_independent_bird_equal_mean']-(
           out[b]['genuine_source_geodesic_used_minus7_B_S_T_I'][k]['original_independent_bird_equal_mean'])
        lo,hi=np.quantile(diff[:,i],[.025,.975])
        contrasts[k]={'original_species_A_minus_F_bird_equal_enrichment':float(effect),
          'original_independent_2020_bird_bootstrap_95':[float(lo),float(hi)],
          'nominal_exploratory_source_sign':('POSITIVE' if lo>0 else 'NEGATIVE' if hi<0 else 'NOT_ESTABLISHED')}
    return {'status':'EXPLORATORY_ACTUAL_2020_GULL_GIC_EQUAL_STEP_GEOGRAPHIC_ENRICHMENT_EVALUATED',
      'original_true_source_year':2020,'n_native_GIC_rotated_alternatives_per_genuine_GPS_step':N_ALTERNATIVE_ENDPOINTS,
      'source_not_real_animal_accessible_habitat_2020_or_feeding':True,
      'same_cohort_post_v114_exploratory_not_multiplicity_adjusted':True,
      'genuine_source_individual_gull_species':out,
      'original_genuine_2species_contrasts':contrasts}
