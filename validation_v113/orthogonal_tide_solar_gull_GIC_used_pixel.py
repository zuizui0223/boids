"""v113 POST-v112 exploratory four-cell ORTHOGONAL descriptive decomposition.

Original USED GPS native GIC high-RF tidal wetland (static 2017–19 source)
versus tide phase and astronomical day/night in actual 2020 two gull species.
Does NOT measure activity time, actual exposed tidal flat or causal choice.
"""
from __future__ import annotations
from collections import defaultdict
from statistics import mean
from math import isfinite
import numpy as np
from original_delta_2020_gull_source import FOCAL
from gull_GIC_native_tidesolar_occupancy import (
    CELL_CLASSES,original_bird_bootstrap_GIC_occupancy,
    MIN_SOURCE_ORIGINAL_BIRDS,WHOLE_BIRD_BOOTSTRAP_REPS,RNG_SEED)

FIXED_SOURCE_MONTHS_COMMON=(5,6,7)
SOURCE_MONTHS_V112=(5,6,7,8)
KNOWN_ORIGINAL_V112_I={
    'Larus argentatus':0.013484470770483046,
    'Larus fuscus':0.01635330434982338}
KNOWN_ORIGINAL_V112_C=-0.0028688335793403356
KNOWN_ORIGINAL_V112_BIRDS={'Larus argentatus':24,'Larus fuscus':15}
KNOWN_ORIGINAL_V112_STRATA={'Larus argentatus':342,'Larus fuscus':71}
KNOWN_ORIGINAL_V112_GPS={'Larus argentatus':18660,'Larus fuscus':3401}
REPLAY_TOLERANCE=1e-10
BASIS=('B_balanced_spatial_source','S_night_minus_day',
       'T_rising_minus_falling','I_tide_by_sun')

def verify_previous_v112_original_replay(source_grouped,source):
    """Must run before all NEW S,T,B calculations, exact old genuine source."""
    if not source.get('original_raster_and_fourcell_gates_pass'):
        raise ValueError('STOP_V113_PREVIOUS_SOURCE_V112_NEVER_ADMITTED')
    orig=original_bird_bootstrap_GIC_occupancy(source_grouped,source,threshold=50.)
    if orig.get('result_status')!='EXPLORATORY_TRUE_2020_GULL_NATIVE_GIC_SPATIAL_USE_TIDE_SOLAR_OBSERVED':
        raise ValueError('STOP_V113_SOURCE_ORIGINAL_V112_OUTCOME_NOT_ADMITTED')
    for species in sorted(FOCAL):
        if abs(orig['original_species'][species]['true_original_bird_equal_D']-
                KNOWN_ORIGINAL_V112_I[species])>REPLAY_TOLERANCE:
            raise ValueError('STOP_V113_OLD_V112_ORIGINAL_INTERACTION_EFFECT_NOT_REPRODUCED')
        if orig['original_species'][species]['original_independent_birds']!=KNOWN_ORIGINAL_V112_BIRDS[species]:
            raise ValueError('STOP_V113_OLD_V112_TRUE_BIRD_SOURCE_CHANGED')
        q=source['per_species_native_source'][species]
        if (q['original_2020_native_birdmonth_0p25m_fourcell_groups']!=
             KNOWN_ORIGINAL_V112_STRATA[species] or
           q['original_2020_native_GPS_points_in_original_4cells']!=
             KNOWN_ORIGINAL_V112_GPS[species]):
            raise ValueError('STOP_V113_OLD_V112_ORIGINAL_NATIVE_GPS_SOURCE_SUPPORT_CHANGED')
    if abs(orig['species_contrast_true_original_bird_equal_D']-KNOWN_ORIGINAL_V112_C)>REPLAY_TOLERANCE:
        raise ValueError('STOP_V113_PREVIOUS_TWO_GULL_SPECIES_CONTRAST_NOT_REPRODUCED')
    return {'status':'EXACT_REAL_PREVIOUS_2020_GULLS_NATIVE_GIC_INTERACTION_REPLAY_BEFORE_NEW_METRICS',
        'known_v112_original_source_run':42767959138,
        'exact_original_source_old_n':{
            s:{'true_original_birds':KNOWN_ORIGINAL_V112_BIRDS[s],
               'original_bird_month_height_4cell_strata':KNOWN_ORIGINAL_V112_STRATA[s],
               'source_original_GPS_used_pixels':KNOWN_ORIGINAL_V112_GPS[s]} for s in sorted(FOCAL)},
        'original_v112_species_I_true_bird_equals':{
            s:orig['original_species'][s]['true_original_bird_equal_D'] for s in sorted(FOCAL)},
        'original_v112_two_species_I_contrast':orig['species_contrast_true_original_bird_equal_D'],
        'original_bird_ID_GPS_source_not_exported':True}

def orthogonal_coefficients_of_original_4cells(group,threshold=50.):
    if threshold not in (50.,20.):
        raise ValueError('STOP_V113_NOT_A_PREDECLARED_NATIVE_GIC_RF_CLASS')
    if set(group)!=set(CELL_CLASSES):
        raise ValueError('STOP_V113_NOT_A_COMPLETE_GENUINE_SOURCE_FOURCELL')
    means={}
    for key,p in group.items():
        a=np.array([x['source_original_GIC_valid_RF'] for x in p],dtype=float)
        if len(a)<5 or not np.isfinite(a).all():
            raise ValueError('STOP_V113_SOURCE_NATIVE_GIC_MASK_NOT_ADMITTED')
        means[key]=float(np.mean(a>=threshold))
    fd,fn,ed,en=(means[(1,'day')],means[(1,'night')],
                 means[(-1,'day')],means[(-1,'night')])
    return {
        'B_balanced_spatial_source':(fd+fn+ed+en)/4.,
        'S_night_minus_day':((fn-fd)+(en-ed))/2.,
        'T_rising_minus_falling':((fn-en)+(fd-ed))/2.,
        'I_tide_by_sun':(fn-fd)-(en-ed)}

def bird_hierarchical_original_coefficients(native_groups,species):
    """All genuine bird observations within observed 4 cells → one bird mean
    per endpoint, equal height bins within original month, then original months."""
    birdmonth=defaultdict(lambda:defaultdict(list))
    for (taxon,bird,month,_height),cells in native_groups.items():
        if taxon!=species:continue
        coef=orthogonal_coefficients_of_original_4cells(cells)
        birdmonth[bird][month].append(coef)
    original={}
    for bird,months in birdmonth.items():
        coeff={}
        for key in BASIS:
            coeff[key]=float(mean(
                mean(row[key] for row in monthvals) for monthvals in months.values()))
        original[bird]=coeff
    return original

def summarize_source_orthogonal_BSTI(groups,gate,seed=RNG_SEED,source_label=''):
    if not gate.get('original_raster_and_fourcell_gates_pass'):
        return {'status':'NOT_ESTIMATED_SOURCE_GATE_NO_BIOLOGICAL_EFFECT',
                'source_label':source_label}
    rng=np.random.default_rng(seed)
    true={}
    bootstrap={}
    for s in sorted(FOCAL):
        original=bird_hierarchical_original_coefficients(groups,s)
        if len(original)<MIN_SOURCE_ORIGINAL_BIRDS:
            raise ValueError('STOP_V113_ORIGINAL_TRUE_BIRDS_LT_FROZEN_SOURCE_GATE')
        mat=np.array([[coeff[k] for k in BASIS] for coeff in original.values()],dtype=float)
        indices=rng.integers(0,len(mat),size=(WHOLE_BIRD_BOOTSTRAP_REPS,len(mat)))
        draws=mat[indices].mean(axis=1)
        bootstrap[s]=draws
        true[s]={'original_independent_native_GPS_birds':len(original),
          'source_n_native_fourcell_groups':gate['per_species_native_source'][s][
                  'original_2020_native_birdmonth_0p25m_fourcell_groups'],
          'original_supported_months':gate['per_species_native_source'][s][
                  'original_2020_months_with_frozen_fourcell_support'],
          'B_S_T_I_original_bird_equal_results':{
              k:{'original_bird_equal_value':float(mat[:,i].mean()),
                 'original_bird_cluster_bootstrap_CI95':
                    np.quantile(draws[:,i],[.025,.975]).tolist(),
                 'original_birds_with_positive_effect':int(np.sum(mat[:,i]>0))}
                 for i,k in enumerate(BASIS)},
          'individual_animal_IDs_and_values_NOT_exported':True}
    a,b=sorted(FOCAL)
    delta=bootstrap[a]-bootstrap[b]
    contrasts={}
    for i,k in enumerate(BASIS):
        v=true[a]['B_S_T_I_original_bird_equal_results'][k]['original_bird_equal_value']-(
           true[b]['B_S_T_I_original_bird_equal_results'][k]['original_bird_equal_value'])
        lo,hi=np.quantile(delta[:,i],[.025,.975])
        contrasts[k]={'original_bird_equal_taxon_contrast_'+a+'_minus_'+b:float(v),
           'original_tagged_bird_bootstrap_CI95':[float(lo),float(hi)],
           'unadjusted_exploratory_source_status':('EXPLORATORY_POSITIVE' if lo>0 else
                   'EXPLORATORY_NEGATIVE' if hi<0 else 'NOT_ESTABLISHED')}
    return {'status':'EXPLORATORY_FROZEN_FOURCELL_ORIGINAL_SOURCE_BSTI_ESTIMATED',
       'source_label':source_label,
       'source_GIC_tidal_wetland_RF_high_threshold':50,
       'source_BSTI_coefficients':list(BASIS),
       'source_is_post_v112_exploratory_no_multiple_tests_confirmatory_p':True,
       'individual_original_species':true,
       'independent_two_species_contrasts':contrasts,
       'source_no_actual_tidalflat_drying_or_feeding_time':True}
