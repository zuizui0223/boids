"""v114 real original 2020 two-gull GIC local background spatial comparison.

Original 2020 Zenodo bird + official RWS tide + native 2017–2019
publisher-MD5 GIC wetland pixels. MUST reproduce old v112 and v113 before
new "USED minus 8 nearby pixels" enrichment B/S/T/I is scored.
The eight nearby pixels are geographic controls, NOT actual animal
reachable-habitat choice or true active feeding/foraging/time niche.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import argparse,json,os
import numpy as np
from original_2020_gull_RWS_source import (
    fetch_original_gulls,original_2020_gauge_may_aug,
    NATIVE_PRIMARY,OriginalSourceStop,SourceNotAdmitted)
from real_2020_gull_GIC_native_pixels import (
    source_2020_original_gull_GIC_pixels,radius_subset)
from gull_GIC_native_tidesolar_occupancy import (
    source_fourcell_only,PHASE_GHOST_DAY_SHIFTS)
from authenticated_gull_local_wetland_background import (
    attach_true_GIC_local_neighbors,RADII_M,PRIMARY_RADIUS_M)
from local_enrichment_gull_BSTI import (
    verify_original_v113_MayJuly_source_then_effect,
    original_ring_source_gate,summarize_original_bird_local_Z,FIXED_MAYJUL)
from orthogonal_tide_solar_gull_GIC_used_pixel import verify_previous_v112_original_replay
SOURCE_PREVIOUS_V112_RUN=42767959138
SOURCE_PREVIOUS_V113_RUN=42769137644
SOURCE_GIC_GEO_AUDIT_RUN=42737124600
FROZEN_DOC='docs/V114_FROZEN_2020_GULL_USED_VS_NEARBY_WETLAND_SOURCE.md'

def report_and_save(report,output):
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    result=(report.get('main_original_2020_1km_8ray_bird_enrichment') or {}).get('true_original_bird_species_contrasts') or {}
    print('V114_ORIGINAL_TRUE_TWO_GULL_LOCAL_RF_NEIGHBOR_RESULT '+json.dumps({
       'status':report['source_status'],
       'replayed_v112':(report.get('previous_original_v112_true_interaction_replay') or {}).get('status'),
       'replayed_v113':(report.get('previous_original_v113_true_MayJuly_replay') or {}).get('source_replay_status'),
       'original_two_species_1km_source_gate':(report.get('local_1000m_RWS_true_phase_fourcell_source') or {}).get(
          'original_raster_and_fourcell_gates_pass'),
       'new_primary_1km_species_B_Z_diff':result.get('B_balanced_spatial_source'),
       'new_primary_1km_species_solar_S_Z_diff':result.get('S_night_minus_day'),
       'original_1km_ghost_B_S_source_and_contrasts':{
          k:{'admitted':v['source']['original_raster_and_fourcell_gates_pass'],
              'B':(v.get('outcome') or {}).get('true_original_bird_species_contrasts',{}).get('B_balanced_spatial_source'),
              'S':(v.get('outcome') or {}).get('true_original_bird_species_contrasts',{}).get('S_night_minus_day')}
           for k,v in (report.get('phase_ghost_original_RWS_1km_local_GIC') or {}).items()},
       'source_no_real_accessibility_prey_or_active_feeding_or_actual_time_niche':True},
       sort_keys=True),flush=True)
    return report

def run(v105_original_affine,output):
    report={'analysis':'V114_GENUINE_2020_TWO_GULLS_GIC_USED_SITE_MINUS_EIGHT_NEARBY_RF50_TIDE_SOLAR_BSTI',
       'source_status':'SOURCE_PENDING',
       'original_research_year':2020,
       'source_corrected_Zenodo_original_Publisher_MD5':True,
       'native_WGS84_GIC_2017_2019_classifier':'twprobabilityEnd tidal WETLAND not bare dry tidalflat',
       'previous_original_bird_source_v112':SOURCE_PREVIOUS_V112_RUN,
       'previous_original_bird_source_v113':SOURCE_PREVIOUS_V113_RUN,
       'original_GIC_geo_source_v105':SOURCE_GIC_GEO_AUDIT_RUN,
       'source_radii_m':[500,1000,2000],
       'source_8_compass_geodesic_azimuths_deg':[0,45,90,135,180,225,270,315],
       'frozen_method':FROZEN_DOC,
       'source_scientific_limit':'used-site spatial enrichment vs used-site-centered 8 ray local GIC map; NOT independent availability choice, actual dry flat, prey, foraging, circadian physiology or animal time niche',
       'source_original_bird_identifiers_and_native_coordinates_NAP_water_arrays_NOT_exported':True}
    try:
        birds,publisher=fetch_original_gulls()
        rws,rwsreceipt=original_2020_gauge_may_aug(NATIVE_PRIMARY)
        report['authentic_2020_original_gull_source_proof']=publisher
        report['original_real_2020_Roompot_RWS_tide_source_proof']=rwsreceipt
    except (OriginalSourceStop,SourceNotAdmitted,ValueError,TimeoutError,OSError) as e:
        report['source_status']='SOURCE_STOP_ORIGINAL_GULL_OR_RWS_2020'
        report['source_failure_type']=type(e).__name__
        report['original_source_failure']=str(e)[:200]
        return report_and_save(report,output)

    # Phase 1: authenticate original used GIC pixels. Replay two previous
    # field native GPS pixel source/outcome results BEFORE any new availability.
    try:
        original30,usedproof=source_2020_original_gull_GIC_pixels(birds,v105_original_affine)
        original20=radius_subset(original30,20.)
        allv112,gatev112=source_fourcell_only(original20,rws,require_GIC_pixel=True)
        oldv112=verify_previous_v112_original_replay(allv112,gatev112)
        report['previous_original_v112_true_interaction_replay']=oldv112
        common=[x for x in original20 if x['month'] in FIXED_MAYJUL]
        oldv113,gatev113=source_fourcell_only(common,rws,require_GIC_pixel=True)
        oldv113replay=verify_original_v113_MayJuly_source_then_effect(oldv113,gatev113)
        report['previous_original_v113_true_MayJuly_replay']=oldv113replay
        report['verified_old_gull_GIC_real_original_source_MD5']=usedproof[
             'source_original_GIC_TIFF_receipts_anonymized']
        print('V114_OLD_SOURCE_GPS_GIC_RWS_AND_FIELD_RESULTS_EXACT_REPLAYED '+json.dumps({
          'true_old_v112_result':oldv112['status'],
          'true_old_v113_MayJuly_B_and_I':oldv113replay['source_replay_status'],
          'original_birds_and_genuine_fourcells':oldv113replay['native_source_counts'],
          'NEW_2020_local_available_habitat_Z_NOT_YET_CALCULATED':True},sort_keys=True),flush=True)
    except (ValueError,OriginalSourceStop,SourceNotAdmitted,TimeoutError,OSError) as e:
        report['source_status']='STOP_PREVIOUS_TRUE_2020_GULL_SOURCE_OR_EFFECT_DRIFT'
        report['previous_source_error']=str(e)[:260]
        return report_and_save(report,output)

    # Phase 2: read new 8-radii native pixel *source records* only, exact old
    # USED pixel per GPS point is re-verified against another original GIC TIFF.
    try:
        annotated,neighborhood_source=attach_true_GIC_local_neighbors(
             birds,v105_original_affine,original30,usedproof)
        report['original_all_native_GIC_8_ray_source_proof']=neighborhood_source
    except (ValueError,OriginalSourceStop,SourceNotAdmitted,TimeoutError,OSError) as e:
        report['source_status']='SOURCE_STOP_NEW_LOCAL_GIC_NEIGHBOR_PIXELS'
        report['original_GIC_background_error']=str(e)[:240]
        return report_and_save(report,output)

    actual20=radius_subset(annotated,20.)
    actual_common=[x for x in actual20 if x['month'] in FIXED_MAYJUL]
    main_group,main_source=original_ring_source_gate(
        actual_common,rws,PRIMARY_RADIUS_M)
    report['local_1000m_RWS_true_phase_fourcell_source']=main_source
    print('V114_TRUE_GIC_NEIGHBOR_SOURCE_BEFORE_NEW_Z '+json.dumps({
        'radius_m':PRIMARY_RADIUS_M,
        'source_two_species_admitted':main_source['original_raster_and_fourcell_gates_pass'],
        'source_original_native_birds_4cells':main_source['per_species_native_source'],
        'source_8ray_valid_against_real_2020_tide_sun':main_source['source_genuine_GIC_RF_pixel_coverage'],
        'NEW_bird_enrichment_Z_NOT_YET_CALCULATED':True},sort_keys=True),flush=True)
    if not main_source['original_raster_and_fourcell_gates_pass']:
        report['source_status']='NOT_ESTIMATED_LOCAL_1KM_GIC_8RAY_ORIGINAL_SOURCE_GATE'
        return report_and_save(report,output)

    # Phase 3: actual field-local-enrichment endpoint. Same genuine
    # original bird hierarchy, not a new biological sample.
    main=summarize_original_bird_local_Z(main_group,main_source,PRIMARY_RADIUS_M)
    report['main_original_2020_1km_8ray_bird_enrichment']=main
    report['source_status']='EXPLORATORY_ORIGINAL_2020_USED_MINUS_NEIGHBOR_WETLAND_ENRICHMENT_EVALUATED'
    report['secondary_original_GIC_map_radius_sensitivity']={}
    for radius in (500,2000):
        selected,gate=original_ring_source_gate(actual_common,rws,radius)
        outcome=summarize_original_bird_local_Z(selected,gate,radius)
        report['secondary_original_GIC_map_radius_sensitivity'][f'{radius}m']={
             'original_ring_source':gate,'source_admitted_outcome_only':outcome}
        print('V114_ORIGINAL_STATIC_WETLAND_NEIGHBOR_RADIUS_SENSITIVITY '+json.dumps({
           'radius_m':radius,
           'source_pass':gate['original_raster_and_fourcell_gates_pass'],
           'B_Z_taxon_contrast':(outcome.get('true_original_bird_species_contrasts') or {}).get(
              'B_balanced_spatial_source')},sort_keys=True),flush=True)

    report['phase_ghost_original_RWS_1km_local_GIC']={}
    for shift in PHASE_GHOST_DAY_SHIFTS:
        selected,gate=original_ring_source_gate(actual_common,rws,PRIMARY_RADIUS_M,
                                                shift_days=shift)
        outcome=summarize_original_bird_local_Z(
           selected,gate,PRIMARY_RADIUS_M)
        report['phase_ghost_original_RWS_1km_local_GIC'][f'+{shift}days']={
           'original_real_tide_shift_not_GPS_or_solar_or_map':shift,
           'source':gate,'outcome':outcome}
        print('V114_REAL_TIDE_SOURCE_GHOST_1KM_LOCAL_GIC '+json.dumps({
          'shift_days':shift,'source_pass':gate['original_raster_and_fourcell_gates_pass'],
          'B_Z':(outcome.get('true_original_bird_species_contrasts') or {}).get('B_balanced_spatial_source'),
          'S_Z':(outcome.get('true_original_bird_species_contrasts') or {}).get('S_night_minus_day')},
          sort_keys=True),flush=True)
    return report_and_save(report,output)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v105-original-GIC-source',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    run(a.v105_original_GIC_source,a.output)
