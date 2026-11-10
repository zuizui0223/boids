"""v112 TRUE 2020 Larus native GPS location × verified 2017–2019 GIC
TIDAL WETLAND static RF score × original measured 2020 RWS tide × sun.

EXPLORATORY POST v111 NEGATIVE GPS SPEED RESULT. Not true tide-flat
dry hours, prey, active feeding, roost or internal circatidal clock.
No original bird ID/GPS positions/precise timestamp leaves ephemeral runner.
"""
from __future__ import annotations
from bisect import bisect_left
from collections import Counter,defaultdict
from datetime import timedelta,timezone
from math import floor
import json
import numpy as np
from astral import Observer
from astral.sun import elevation
from two_gull_tide_solar_fourway import (
    great_circle_km,nearest_original_rws,sunlight_label_at_native_gps,
    CELL_CLASSES,MIN_FIXES_PER_SOURCE_CELL,MIN_UTC_DATES_PER_CELL,
    WHOLE_BIRD_BOOTSTRAP_REPS,RNG_SEED,MIN_SOURCE_ORIGINAL_BIRDS,
    MIN_SOURCE_FOURCELL_GROUPS,MIN_SOURCE_MOVEMENTS,MIN_SOURCE_MONTHS)
from original_2020_gull_RWS_source import GEO_PRIMARY,SOURCE_MONTHS
from original_delta_2020_gull_source import FOCAL

GPS_POINT_RADIUS_PRIMARY_KM=20.
ALT_RADII_KM=(10.,30.)
MIN_PER_SPECIES_VALID_NATIVE_GIC_SOURCE_PIXELS=.9
GIC_PRIMARY_THRESHOLD=50.
GIC_SECONDARY_THRESHOLD=20.
HEIGHT_SOURCE_BAND_METRES=.25
PHASE_GHOST_DAY_SHIFTS=(3,7,11)
SCIENTIFIC_PRE_REG_YEAR=2020

def original_gull_position_opportunity(bird_hour, radius=GPS_POINT_RADIUS_PRIMARY_KM):
    """Every ORIGINAL earliest GPS location / bird hour, not displacement pairs.
    Select solely on true position, native year/month and 20 km gauge radius.
    """
    if radius not in (10.,20.,30.):
        raise ValueError('STOP_V112_ORIGINAL_GULL_POINT_GEO_RADIUS_POST_OUTCOME_CHANGE')
    out=[]; qa=Counter()
    bytaxon=defaultdict(set)
    for (species,animal),row in bird_hour.items():
        if species not in FOCAL: continue
        for dt,lat,lon in row.values():
            if dt.year!=SCIENTIFIC_PRE_REG_YEAR or dt.month not in SOURCE_MONTHS:
                qa['source_time_outside_fixed_2020_MayAug']+=1
                continue
            if great_circle_km(lat,lon,*GEO_PRIMARY)>radius:
                qa['source_GPS_gauge_distance_outside_fixed_radius']+=1
                continue
            utc=dt.replace(tzinfo=timezone.utc)
            out.append({'species':species,'private_bird':animal,'utc':utc,
                        'month':dt.month,'latitude':lat,'longitude':lon})
            bytaxon[species].add(animal)
    return out,{'original_source_point_count':len(out),
         'source_bird_counts_within_fixed_radius':
            {species:len(bytaxon[species]) for species in sorted(FOCAL)},
         'original_source_QA':dict(qa),
         'not_original_bird_activity_or_foraging':True}

def source_fourcell_only(original_with_RFp, native_RWS,
                         phase_shift_days=0, require_GIC_pixel=False):
    """Native exposure source: bird × month × original 0.25 m measured
    NAP band × flood/ebb × solar DAY/NIGHT. Do not inspect RF *value*
    to decide source eligibility; optional GIC mask check uses only missingness.
    """
    if phase_shift_days not in (0,)+PHASE_GHOST_DAY_SHIFTS:
        raise ValueError('STOP_V112_SOURCE_TIDE_GHOST_NOT_FROZEN')
    sorted_RWS=sorted(native_RWS)
    grouped=defaultdict(list)
    qa=Counter()
    daylight=defaultdict(Counter)
    source_pixel=defaultdict(Counter)
    for e in original_with_RFp:
        species=e['species']
        hasRF=(e.get('source_original_GIC_valid_RF') is not None)
        source_pixel[species]['all_original_GPS_near_gauge']+=1
        if hasRF:source_pixel[species]['original_native_GIC_valid_pixel']+=1
        else:source_pixel[species]['no_valid_original_GIC_native_pixel']+=1
        sun=sunlight_label_at_native_gps(e['utc'],e['latitude'],e['longitude'])
        daylight[species][sun]+=1
        if sun=='twilight':qa['original_astral_twilight_excluded']+=1;continue
        stage=nearest_original_rws(native_RWS,sorted_RWS,
              e['utc']+timedelta(days=phase_shift_days))
        if stage is None:
            qa['true_RWS_tide_source_unmatched_or_slope_ambiguous']+=1
            continue
        qa['original_valid_tide_solar_mapped_GPS_source_all_RF_states']+=1
        if not hasRF and require_GIC_pixel:
            qa['GIC_native_mask_or_source_missing_after_tide_sun']+=1
            continue
        key=(species,e['private_bird'],e['month'],stage['source_height_bin'])
        cell=(stage['source_phase'],sun)
        grouped[(key,cell)].append(e)
    complete={}
    per_species=defaultdict(lambda:Counter())
    all_keys={key for key,_ in grouped}
    for key in all_keys:
        cells={c:grouped.get((key,c),[]) for c in CELL_CLASSES}
        if not all(len(vals)>=MIN_FIXES_PER_SOURCE_CELL and
                   len({p['utc'].date() for p in vals})>=MIN_UTC_DATES_PER_CELL
                   for vals in cells.values()):
            continue
        complete[key]=cells
        per_species[key[0]]['fourcell_source_groups']+=1
        per_species[key[0]]['actual_original_native_GPS_fix_cells']+=sum(len(x) for x in cells.values())
    speciesgate={}
    for species in sorted(FOCAL):
        keys=[k for k in complete if k[0]==species]
        birds={k[1] for k in keys};months={k[2] for k in keys}
        n=sum(sum(len(v) for v in complete[k].values()) for k in keys)
        sourceconditions={
            'original_tagged_birds_ge8':len(birds)>=MIN_SOURCE_ORIGINAL_BIRDS,
            'original_full_4cell_birdmonthstage_groups_ge20':
                len(keys)>=MIN_SOURCE_FOURCELL_GROUPS,
            'original_native_hour_GPS_fixes_in_4cells_ge1000':n>=MIN_SOURCE_MOVEMENTS,
            'original_tide_solar_source_months_ge2':len(months)>=MIN_SOURCE_MONTHS}
        speciesgate[species]={'original_2020_source_independent_birds':len(birds),
          'original_2020_native_birdmonth_0p25m_fourcell_groups':len(keys),
          'original_2020_native_GPS_points_in_original_4cells':n,
          'original_2020_months_with_frozen_fourcell_support':sorted(months),
          'source_gate_predeclared_conditions':sourceconditions,
          'fourcell_source_admitted':all(sourceconditions.values())}
    # GIC pixel support must be evaluated after original environmental source
    # admission, not after observing Y's numerical value.
    coverage={}
    for s in sorted(FOCAL):
        d=source_pixel[s]
        coverage[s]={'original_genuine_2020_GPS_points_in_source_radius':
                          d['all_original_GPS_near_gauge'],
          'native_GIC_2017_2019_valid_source_pixel_points':
                          d['original_native_GIC_valid_pixel'],
          'native_GIC_missing_or_outside_source_point_count':
                          d['no_valid_original_GIC_native_pixel'],
          'original_native_GIC_pixel_coverage_fraction':(
                 d['original_native_GIC_valid_pixel']/d['all_original_GPS_near_gauge']
                 if d['all_original_GPS_near_gauge'] else None)}
    validcoverage=all(coverage[s]['original_native_GIC_pixel_coverage_fraction'] is not None and
       coverage[s]['original_native_GIC_pixel_coverage_fraction']>=MIN_PER_SPECIES_VALID_NATIVE_GIC_SOURCE_PIXELS
       for s in FOCAL)
    admitted=all(s['fourcell_source_admitted'] for s in speciesgate.values())
    summary={'n_original_2020_source_point_time_tide_sun_4cell_groups':len(complete),
      'phase_ghost_original_RWS_day_shift':phase_shift_days,
      'source_expected_only_original_time_tide_solar':not require_GIC_pixel,
      'per_species_native_source':speciesgate,
      'source_genuine_GIC_RF_pixel_coverage':coverage,
      'original_source_pixel_coverage_ge90pct_each_species':validcoverage,
      'original_two_species_source_fourcell_admitted':admitted,
      'original_raster_and_fourcell_gates_pass':admitted and validcoverage,
      'source_sunrise_and_detection_qa':{s:dict(d) for s,d in daylight.items()},
      'source_reason_counts':dict(qa),
      'no_true_exposed_habitat_or_foraging_time_inferred':True}
    return complete,summary

def individual_original_GIC_4cell_effects(complete,species,threshold=GIC_PRIMARY_THRESHOLD):
    if threshold not in (20.,50.,'continuous'):
        raise ValueError('STOP_V112_NEW_GIC_THRESHOLD_NOT_FROZEN')
    av=defaultdict(lambda:defaultdict(list))
    for (taxon,bird,month,band),cells in complete.items():
        if taxon!=species:continue
        score={}
        for c,events in cells.items():
            vals=np.array([p['source_original_GIC_valid_RF'] for p in events],dtype=float)
            if not np.isfinite(vals).all():raise ValueError('STOP_V112_GIC_SOURCE_MASK_NOT_FILTERED')
            y=(vals/100.) if threshold=='continuous' else (vals>=threshold)
            score[c]=float(np.mean(y))
        d=(score[(1,'night')]-score[(1,'day')])-(score[(-1,'night')]-score[(-1,'day')])
        av[bird][month].append(d)
    return {bird:float(np.mean([np.mean(v) for v in months.values()]))
            for bird,months in av.items()}

def original_bird_bootstrap_GIC_occupancy(complete, source,threshold=GIC_PRIMARY_THRESHOLD,
                                           seed=RNG_SEED):
    if not source['original_raster_and_fourcell_gates_pass']:
        return {'result_status':'NOT_ESTIMATED_TWO_SPECIES_ORIGINAL_TIDE_SOLAR_PIXEL_SOURCE_GATE',
            'original_native_source_no_effect_estimated':True}
    rng=np.random.default_rng(seed)
    draw={}
    results={}
    for species in sorted(FOCAL):
        b=individual_original_GIC_4cell_effects(complete,species,threshold)
        vals=np.asarray(list(b.values()),dtype=float)
        if len(vals)<MIN_SOURCE_ORIGINAL_BIRDS:
            raise ValueError('STOP_V112_ONE_SPECIES_NATIVE_BIRD_SOURCE_CHANGED_AFTER_GATE')
        boot=vals[rng.integers(0,len(vals),size=(WHOLE_BIRD_BOOTSTRAP_REPS,len(vals)))].mean(axis=1)
        draw[species]=boot
        results[species]={'original_independent_birds':len(vals),
          'true_original_bird_equal_D':float(np.mean(vals)),
          'whole_true_bird_bootstrap_95pct':np.quantile(boot,[.025,.975]).tolist(),
          'original_bird_D_positive_count':int(np.sum(vals>0)),
          'original_per_bird_values_not_exported':True}
    names=sorted(FOCAL)
    diff=draw[names[0]]-draw[names[1]]
    obs=results[names[0]]['true_original_bird_equal_D']-results[names[1]]['true_original_bird_equal_D']
    lo,hi=np.quantile(diff,[.025,.975])
    return {'result_status':'EXPLORATORY_TRUE_2020_GULL_NATIVE_GIC_SPATIAL_USE_TIDE_SOLAR_OBSERVED',
       'original_source_tidal_wetland_RF_threshold':threshold,
       'original_source_Y_unit':'fraction of USED GIC tidal-wetland high-RF original source GPS cells',
       'original_species':results,
       'primary_species_contrast_order':f'{names[0]} minus {names[1]}',
       'species_contrast_true_original_bird_equal_D':float(obs),
       'species_contrast_independent_whole_bird_bootstrap_95pct':[float(lo),float(hi)],
       'species_contrast_source_sign_status':(
           'EXPLORATORY_POSITIVE' if lo>0 else
           'EXPLORATORY_NEGATIVE' if hi<0 else 'NOT_ESTABLISHED'),
       'no_actual_feeding_or_tidal_dry_time_observed':True}

def descriptive_real_RF_location_use(original_with_RF):
    r={}
    for taxon in sorted(FOCAL):
        vals=np.asarray([e['source_original_GIC_valid_RF'] for e in original_with_RF
            if e['species']==taxon and e.get('source_original_GIC_valid_RF') is not None],dtype=float)
        r[taxon]={'native_original_GPS_points_with_original_GIC_RF_pixels':len(vals),
          'fraction_native_real_GPS_in_GIC_tidalwetland_RF_ge50':
             float(np.mean(vals>=50)) if len(vals) else None,
          'fraction_native_real_GPS_in_GIC_tidalwetland_RF_ge20':
             float(np.mean(vals>=20)) if len(vals) else None,
          'mean_native_static_GIC_RF_score_of_used_GPS_points':
             float(np.mean(vals)) if len(vals) else None,
          'not_actual_occupied_tidal_flat_exposed_habitat':True}
    return r
