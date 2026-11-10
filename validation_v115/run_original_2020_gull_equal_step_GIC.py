"""v115 ORIGINAL two 2020 Larus species true GPS step-endpoint versus
seven SAME-STEP-LENGTH rotated native GIC tidal-WETLAND source destinations.

Strictly reproduce old original 2020 v111 RWS×astral×GPS displacement
source and D effects FIRST; then evaluate post-v114 exploratory B/S/T/I
on 2020 May–July true bird GIC class endpoint spatial enrichment.
Not real 2020 tidalflat drying, food, accessible movement or true selection.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import argparse,json,time
import numpy as np
from original_2020_gull_RWS_source import (
    fetch_original_gulls,original_2020_gauge_may_aug,
    NATIVE_PRIMARY,OriginalSourceStop,SourceNotAdmitted)
from two_gull_tide_solar_fourway import original_movement_opportunities
from original_GIC_equal_step_rotated_destinations import (
    native_GIC_same_step_endpoint_pixels)
from true_original_gull_equal_step_BSTI import (
    hard_replay_original_v111_genuine_movement_effects,
    true_original_fourcell_source_with_endpoints,
    evaluate_real_original_bird_two_gull_step_BSTI,COMMON_SOURCE_MONTHS)
from original_delta_2020_gull_source import FOCAL

SOURCE_OLD_V111=42748780612
SOURCE_OLD_V114=42787244258
SOURCE_V105_AUTHENTIC_GIC=42737124600
FROZEN_PRE_OUTCOME_DOC='docs/V115_FROZEN_2020_TWO_GULL_GIC_EQUAL_STEP_ALTERNATIVES.md'
GHOSTS=(3,7,11)

def finish(report,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    q=(report.get('new_original_two_species_equal_step_endpoint_enrichment') or {}).get('original_genuine_2species_contrasts') or {}
    print('V115_TRUE_GULL_EQUAL_STEP_GIC_FIELD_RESULT '+json.dumps({
        'status':report['source_and_effect_status'],
        'old_v111_movement_exactly_replayed':(
           report.get('old_v111_original_genuine_GPS_movement_source_and_Y_replay') or {}).get('source_status'),
        'true_2020_GIC_real_vs_7rotated_source_coverage':(
           report.get('native_original_GIC_same_length_rotated_GPS_pixel_source') or {}).get('original_GIC_native_source_coverage'),
        '2020_MayJuly_original_new_RWS_true_fourcell_source_admitted':(
           report.get('new_2020_MayJuly_true_RWS_birdstep_GIC_source_gate') or {}).get('original_bird_and_all_GIC_source_admitted'),
        'new_primary_B_step_species_diff':q.get('B_balanced_endpoint_enrichment'),
        'new_solar_S_step_species_diff':q.get('S_solar_night_minus_day'),
        'new_tidal_T_step_species_diff':q.get('T_tide_rising_minus_falling'),
        'new_interaction_I_step_species_diff':q.get('I_tide_by_solar'),
        'phase_ghosts_source_contrasts':{
            k:{'source_admitted':v['source']['original_bird_and_all_GIC_source_admitted'],
                'B':(v.get('effect') or {}).get('original_genuine_2species_contrasts',{}).get('B_balanced_endpoint_enrichment'),
                'S':(v.get('effect') or {}).get('original_genuine_2species_contrasts',{}).get('S_solar_night_minus_day')}
                for k,v in report.get('native_original_RWS_ghosts',{}).items()},
        'scientific_boundary_NOT_real_food_accessibility_or_clock':True},
        sort_keys=True),flush=True)
    return report

def transport_only_source_retry(call, source_label, max_attempts=3):
    """Retry same SOURCE and checksums only after original provider 429/504/timeout;
    do not relax biological source gates, season or expected source hashes.
    """
    errors=[]
    for k in range(max_attempts):
        try:
            return call(),{'original_publisher_same_source_attempts':k+1,
                'source_transport_failures_before_original_success':errors}
        except (SourceNotAdmitted,OriginalSourceStop,TimeoutError,OSError) as e:
            desc=str(e)
            if not any(t in desc for t in (
                 'SOURCE_UNAVAILABLE','RATE_LIMITED','HTTP Error 429',
                 'HTTP Error 504','timed out','TimeoutError')):
                raise
            errors.append({'attempt':k+1,'source':source_label,
                           'transport_error':desc[:160]})
            if k==max_attempts-1:raise
            time.sleep(3.*(2**k))
    raise AssertionError('unreachable transport retry')


def run(v105_geo,outfile):
    report={'analysis':'V115_TRUE_2020_TWO_GULLS_REAL_GPS_STEP_EQUAL_LENGTH_7ROTATED_GIC_TIDAL_WETLAND_RWS_TIDE_SUN',
       'source_and_effect_status':'SOURCE_PENDING',
       'original_year':2020,'source_original_true_GPS_gull':SOURCE_OLD_V111,
       'source_original_verified_used_GIC_prior':SOURCE_OLD_V114,
       'source_original_static_GIC_v105_audit':SOURCE_V105_AUTHENTIC_GIC,
       'frozen_after_v114_original_observed_spatial_difference':True,
       'original_movement_matched_calendar_months':[5,6,7],
       'source_7_same_length_rotated_geodesic_heading_shifts_degrees':[45,90,135,180,225,270,315],
       'NO_original_bird_ID_GPS_coordinates_native_waterlevels_or_original_GIC_pixels_exported':True,
       'NO_true_dry_tidalflat_food_available_path_behavior_or_clock_measured':True,
       'protocol':FROZEN_PRE_OUTCOME_DOC}
    try:
        (birds,gpsproof),gtransport=transport_only_source_retry(
             fetch_original_gulls,'CORRECTED_ZENODO_DELTATRACK_2020')
        (rws,rwsproof),rtransport=transport_only_source_retry(
             lambda:original_2020_gauge_may_aug(NATIVE_PRIMARY),
             'TRUE_RWS_ROOMPO_BUITEN_2020')
        report['original_native_source_transport_unchanged_scientific_retries']={
             'GPS':gtransport,'RWS':rtransport}
        report['original_corrected_2020_two_species_Zenodo_GPS_MD5_provenance']=gpsproof
        report['original_RWS_2020_true_measured_tide_NAP_provenance']=rwsproof
    except (OriginalSourceStop,SourceNotAdmitted,ValueError,TimeoutError,OSError) as e:
        report['source_and_effect_status']='SOURCE_STOP_ORIGINAL_GPS_OR_REAL_RWS_2020'
        report['original_source_blocker']=repr(e)[:240]
        return finish(report,outfile)

    allmoves,sourcebefore=original_movement_opportunities(birds,radius=20.)
    report['original_real_2020_gull_two_species_movement_source_before_tide_and_GIC']=sourcebefore
    try:
        replay=hard_replay_original_v111_genuine_movement_effects(allmoves,rws)
        report['old_v111_original_genuine_GPS_movement_source_and_Y_replay']=replay
        print('V115_ORIGINAL_PREVIOUS_V111_GPS_RWS_TIDE_SUN_MOVEMENT_EXACT_REPLAY_BEFORE_NEW_Y '+json.dumps(replay,sort_keys=True),flush=True)
    except ValueError as e:
        report['source_and_effect_status']='STOP_ORIGINAL_V111_GULL_MOVEMENT_Y_AND_4CELL_DRIFT'
        report['previous_biological_source_replay_failure']=repr(e)[:240]
        return finish(report,outfile)

    common=[e for e in allmoves if e['month'] in COMMON_SOURCE_MONTHS]
    report['original_new_true_GPS_movement_source_preselected_MayJuly_n']=len(common)
    try:
        original_native,source=native_GIC_same_step_endpoint_pixels(common,v105_geo)
        report['native_original_GIC_same_length_rotated_GPS_pixel_source']=source
    except (ValueError,OriginalSourceStop,SourceNotAdmitted,TimeoutError,OSError) as e:
        report['source_and_effect_status']='SOURCE_STOP_ORIGINAL_GIC_2020_GPS_STEP_NATIVE_ENDPOINTS'
        report['original_native_GIC_pixel_source_blocker']=repr(e)[:240]
        return finish(report,outfile)
    print('V115_TRUE_GULL_GIC_SEVEN_EQUAL_MOVE_LENGTH_SOURCE_ONLY '+json.dumps({
        'source_MayJuly_genuine_GPS_steps':len(common),
        'real_native_GIC_source_status':source['original_GIC_native_source_coverage'],
        'native_2017_2019_GIC_provider_MD5_verified':all(
             x['source_publisher_MD5_verified'] for x in source['original_GIC_provider_MD5_receipts']),
        'NO_2020_GULL_STEP_GIC_CLASS_ENRICHMENT_Y_YET':True},sort_keys=True),flush=True)

    groups,gate=true_original_fourcell_source_with_endpoints(original_native,rws)
    report['new_2020_MayJuly_true_RWS_birdstep_GIC_source_gate']=gate
    print('V115_REAL_TWO_SPECIES_MATCHED_GIC_GAUGE_SUN_SOURCE_BEFORE_NEW_USED_ENDPOINT_Y '+json.dumps({
        'both_true_original_2020_Larus_GIC_and_RWS_source_admitted':
            gate['original_bird_and_all_GIC_source_admitted'],
        'native_bird_month_height_groups':gate['original_source_all_species'],
        'native_original_GIC_rotated_sourcing':gate['real_RWS_and_solar_GIC_original_source_coverage'],
        'NEW_step_endpoint_enrichment_source_not_scored_yet':True},sort_keys=True),flush=True)
    if not gate['original_bird_and_all_GIC_source_admitted']:
        report['source_and_effect_status']='NOT_ESTIMATED_2020_ORIGINAL_7ROTATED_STEP_RWS_SOURCE_GATE'
        return finish(report,outfile)

    effects=evaluate_real_original_bird_two_gull_step_BSTI(groups,gate)
    report['new_original_two_species_equal_step_endpoint_enrichment']=effects
    report['source_and_effect_status']='EXPLORATORY_2020_TWO_GULL_NATIVE_GIC_EQUAL_STEP_ROTATED_HABITAT_ENRICHMENT'
    report['native_original_RWS_ghosts']={}
    for shift in GHOSTS:
        group,source=true_original_fourcell_source_with_endpoints(original_native,rws,ghost=shift)
        out=evaluate_real_original_bird_two_gull_step_BSTI(group,source)
        report['native_original_RWS_ghosts'][f'+{shift}days']={
            'native_source_tide_phase_shift_calendar_days':shift,
            'native_original_gull_GPS_and_GIC_same_length_alternatives_UNSHIFTED':True,
            'source':source,'effect':out}
        print('V115_GENUINE_ORIGINAL_TIDE_PHASE_GHOST_AFTER_SOURCE_GATE '+json.dumps({
           'shift_days':shift,'source_admitted':source['original_bird_and_all_GIC_source_admitted'],
           'species_B_step':(out.get('original_genuine_2species_contrasts') or {}).get('B_balanced_endpoint_enrichment'),
           'species_S_step':(out.get('original_genuine_2species_contrasts') or {}).get('S_solar_night_minus_day')},sort_keys=True),flush=True)
    return finish(report,outfile)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v105-genuine-original-GIC-georeference',required=True)
    p.add_argument('--output',required=True)
    x=p.parse_args();run(x.v105_genuine_original_GIC_georeference,x.output)
