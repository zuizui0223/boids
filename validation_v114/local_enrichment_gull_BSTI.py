"""v114 bird-equal local-wetland **enrichment** around original used GPS points.

Z = valid source native USED GIC RF>=50 indicator - mean of eight fixed
1km (or frozen 500m/2km) compass-neighbor RF>=50 indicators.
B/S/T/I refer to Z, not wet/dry tidalflat accessibility or true habitat
selection; same original 2020 two Larus species and tide×solar 4cells.
"""
from __future__ import annotations
from collections import defaultdict
from statistics import mean
import numpy as np
from original_delta_2020_gull_source import FOCAL
from gull_GIC_native_tidesolar_occupancy import (
    source_fourcell_only,MIN_SOURCE_ORIGINAL_BIRDS,
    WHOLE_BIRD_BOOTSTRAP_REPS,RNG_SEED)
from orthogonal_tide_solar_gull_GIC_used_pixel import (
    BASIS,verify_previous_v112_original_replay,
    summarize_source_orthogonal_BSTI)
from authenticated_gull_local_wetland_background import (
    RADII_M,PRIMARY_RADIUS_M,EXPECTED_N_RAYS)

FIXED_MAYJUL=(5,6,7)
ORIGINAL_V113_MATCHED_SOURCE={
 'Larus argentatus':{'birds':24,'strata':263,'fixes':14384,
    'I':0.007784661958477007,'B':0.12180704610188964},
 'Larus fuscus':{'birds':15,'strata':71,'fixes':3401,
    'I':0.01635330434982338,'B':0.028090868477984664}}
HARD_REPLAY_TOL=1e-10

def verify_original_v113_MayJuly_source_then_effect(orig_four,source):
    """Replay the exact 2020 GIC USED pixel B/I before any new Z scoring."""
    if not source.get('original_raster_and_fourcell_gates_pass'):
        raise ValueError('STOP_V114_PREVIOUS_MATCHED_TWO_GULL_SOURCE_FAILS')
    for species in sorted(FOCAL):
        old=ORIGINAL_V113_MATCHED_SOURCE[species]
        actual=source['per_species_native_source'][species]
        if (actual['original_2020_source_independent_birds']!=old['birds'] or
            actual['original_2020_native_birdmonth_0p25m_fourcell_groups']!=old['strata'] or
            actual['original_2020_native_GPS_points_in_original_4cells']!=old['fixes']):
            raise ValueError('STOP_V114_ORIGINAL_MAYJUL_SOURCE_COUNTS_DRIFT')
    previous=summarize_source_orthogonal_BSTI(orig_four,source,
            source_label='SOURCE_REPLAY_2020_V113_MATCHED_MAY_JUL')
    if previous['status']!='EXPLORATORY_FROZEN_FOURCELL_ORIGINAL_SOURCE_BSTI_ESTIMATED':
        raise ValueError('STOP_V114_ORIGINAL_V113_BSTI_SOURCE_NOT_ADMITTED')
    for species in sorted(FOCAL):
        d=previous['individual_original_species'][species]['B_S_T_I_original_bird_equal_results']
        for key in ('B','I'):
            name='B_balanced_spatial_source' if key=='B' else 'I_tide_by_sun'
            if abs(d[name]['original_bird_equal_value']-
                 ORIGINAL_V113_MATCHED_SOURCE[species][key])>HARD_REPLAY_TOL:
                raise ValueError('STOP_V114_OLD_V113_MATCHED_SOURCE_BIOTIC_COEFFICIENT_DRIFT')
    return {'source_replay_status':'ORIGINAL_2020_V113_MAYJUL_BIOTIC_I_B_EXACTLY_REPLAYED',
       'original_v113_real_source_run':42769137644,
       'native_source_counts':ORIGINAL_V113_MATCHED_SOURCE,
       'old_B_and_I_source_replay':{
          s:{k:previous['individual_original_species'][s][
           'B_S_T_I_original_bird_equal_results'][name]['original_bird_equal_value']
           for k,name in [('B','B_balanced_spatial_source'),('I','I_tide_by_sun')]}
          for s in sorted(FOCAL)},
       'no_original_animal_fixes_or_bird_IDs_exported':True}

def original_ring_source_gate(original_events,original_RWS,radius_m,shift_days=0):
    """Do not inspect original Y or neighborhood RF scores to form source
    strata; only original tide/sun/time and whether all 8 original GIC
    neighbor source pixels + real GPS used pixel are valid and unmasked.
    """
    if radius_m not in RADII_M:raise ValueError('STOP_V114_UNFROZEN_GIC_NEIGHBOR_DISTANCE')
    key=f'v114_r{radius_m}_original_GIC_8ray_native_RF'
    clipped=[]
    for e in original_events:
        item=dict(e)
        if item.get(key) is None:
            item['source_original_GIC_valid_RF']=None
        clipped.append(item)
    groups,source=source_fourcell_only(clipped,original_RWS,
       phase_shift_days=shift_days,require_GIC_pixel=True)
    source['context_radius_m']=radius_m
    source['source_GIC_all_eight_neighbor_source_pixels_required']=True
    source['original_ring_validity_is_missingness_ONLY_not_RF_score_threshold']=True
    return groups,source

def per_group_BSTI_local_Z(cells,radius_m):
    if radius_m not in RADII_M:raise ValueError('STOP_V114_UNFROZEN_LOCAL_RADIUS')
    if set(cells)!={(1,'day'),(1,'night'),(-1,'day'),(-1,'night')}:
        raise ValueError('STOP_V114_TRUE_ORIGINAL_FOURCELL_SOURCE_MISSING')
    k=f'v114_r{radius_m}_original_GIC_8ray_native_RF'
    means={}
    for cell,events in cells.items():
        vals=np.array([x['source_original_GIC_valid_RF'] for x in events],dtype=float)
        background=np.array([x[k] for x in events],dtype=float)
        if (background.ndim!=2 or background.shape!=(len(events),EXPECTED_N_RAYS) or
            not np.isfinite(background).all() or not np.isfinite(vals).all() or
            np.max(background)>100 or np.min(background)<0 or np.max(vals)>100 or np.min(vals)<0):
            raise ValueError('STOP_V114_ORIGINAL_NATIVE_GIC_EIGHT_RAY_SOURCE_INVALID')
        Z=(vals>=50.).astype(float)-np.mean(background>=50.,axis=1)
        if (Z<-1-1e-10).any() or (Z>1+1e-10).any():
            raise ValueError('STOP_V114_GIC_LOCAL_ENRICHMENT_OUTSIDE_MINUS1_PLUS1')
        means[cell]=float(np.mean(Z))
    fd,fn,ed,en=(
        means[(1,'day')],means[(1,'night')],
        means[(-1,'day')],means[(-1,'night')])
    return {'B_balanced_spatial_source':(fd+fn+ed+en)/4.,
            'S_night_minus_day':((fn-fd)+(en-ed))/2.,
            'T_rising_minus_falling':((fn-en)+(fd-ed))/2.,
            'I_tide_by_sun':(fn-fd)-(en-ed)}

def summarize_original_bird_local_Z(groups,source,radius_m,seed=RNG_SEED):
    if not source.get('original_raster_and_fourcell_gates_pass'):
        return {'source_status':'NOT_ESTIMATED_REAL_2020_EIGHT_NEIGHBOR_AND_4CELL_GATES'}
    if radius_m not in RADII_M:raise ValueError('STOP_V114_NON_FROZEN_DISTANCE')
    birds=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    # Group = true tagged bird × calendar month × original 0.25m RWS measured stage
    for (species,bird,month,height),cells in groups.items():
        coef=per_group_BSTI_local_Z(cells,radius_m)
        for endpoint in BASIS:
            birds[species][bird][month].append({endpoint:coef[endpoint]})
    rng=np.random.default_rng(seed)
    outcomes={};draws={}
    for species in sorted(FOCAL):
        original_bird=[]
        for tag,months in birds[species].items():
            vals=[]
            for endpoint in BASIS:
                # equal original height groups within month,
                # equal original months within genuine tagged bird.
                vals.append(float(np.mean([
                    np.mean([z[endpoint] for z in rows if endpoint in z])
                    for rows in months.values()])))
            original_bird.append(vals)
        x=np.array(original_bird,dtype=float)
        if x.ndim!=2 or x.shape[0]<MIN_SOURCE_ORIGINAL_BIRDS or x.shape[1]!=len(BASIS):
            raise ValueError('STOP_V114_TRUE_ORIGINAL_ANIMAL_BOOTSTRAP_SOURCE')
        bootstrap=x[rng.integers(0,len(x),size=(WHOLE_BIRD_BOOTSTRAP_REPS,len(x)))].mean(axis=1)
        draws[species]=bootstrap
        outcomes[species]={
          'native_original_2020_true_tagged_birds':len(x),
          'original_GIC_used_minus_8ray_RF50_BSTI':{
            endpoint:{
              'equal_original_bird_location_enrichment_value':float(np.mean(x[:,i])),
              'original_true_bird_bootstrap_CI95':np.quantile(bootstrap[:,i],[.025,.975]).tolist(),
              'original_birds_with_positive_coefficients':int(np.sum(x[:,i]>0))}
            for i,endpoint in enumerate(BASIS)},
          'individual_bird_ID_and_source_local_GIC_pixels_NOT_exported':True}
    first,second=sorted(FOCAL)
    contrasts={}
    delta=draws[first]-draws[second]
    for i,endpoint in enumerate(BASIS):
        val=outcomes[first]['original_GIC_used_minus_8ray_RF50_BSTI'][endpoint][
            'equal_original_bird_location_enrichment_value']-outcomes[second][
            'original_GIC_used_minus_8ray_RF50_BSTI'][endpoint][
            'equal_original_bird_location_enrichment_value']
        lo,hi=np.quantile(delta[:,i],[.025,.975])
        contrasts[endpoint]={
          'true_original_bird_equal_species_contrast_L_argentatus_minus_L_fuscus':float(val),
          'original_independent_bird_bootstrap95':[float(lo),float(hi)],
          'exploratory_unadjusted_confidence_interval_sign':('POSITIVE' if lo>0 else
                'NEGATIVE' if hi<0 else 'NOT_ESTABLISHED')}
    return {'source_status':'EXPLORATORY_TRUE_2020_ORIGINAL_LOCAL_NEIGHBOR_ENRICHMENT_BSTI_EVALUATED',
      'source_radius_m':radius_m,
      'source_real_GIC_used_minus_8ray_local_background':True,
      'not_animal_movement_availability_or_true_selective_preference':True,
      'post_v113_exploratory_correlated_no_multiplicity_confirmation':True,
      'original_bird_species_location_enrichment':outcomes,
      'true_original_bird_species_contrasts':contrasts}
