"""v111 run authentic 2020 DELTATRACK two gull species × independent Roompot 2020 RWS
May–Aug 10-min tide × true native astronomic sunlight GPS movement proxy.

STRICT: original bird/tide source first, only estimate species activity-*proxy*
effect if BOTH taxa pass all frozen native fourcell source gates. Do not
export original bird IDs, GPS precise locations or clock, raw RWS water heights.
"""
from __future__ import annotations
from pathlib import Path
import argparse,json,os,time
from original_2020_gull_RWS_source import (
    fetch_original_gulls,original_2020_gauge_may_aug,OriginalSourceStop,
    SourceNotAdmitted,NATIVE_PRIMARY,NATIVE_SECONDARY)
from two_gull_tide_solar_fourway import (
    original_movement_opportunities,fourway_original_source,
    score_if_original_two_species_admitted,PHASE_GHOST_DAY_SHIFTS)
SOURCE_PROOF_V109=42746796941
SOURCE_PROOF_V110=42747546101
RUN_ANALYSIS='V111_ORIGINAL_2020_TWO_LARUS_TAXA_SOURCE_MATCHED_TRUE_RWS_TIDE_SOLAR_GPS_MOVEMENT'

def run(output):
    report={'analysis':RUN_ANALYSIS,
       'original_year':2020,'original_common_months':[5,6,7,8],
       'native_corrected_original_gull_source_v109':SOURCE_PROOF_V109,
       'native_original_RWS_Roompotsluis_source_v110':SOURCE_PROOF_V110,
       'frozen_protocol':'docs/V111_FROZEN_ORIGINAL_2020_TWO_GULL_TIDE_SOLAR_MATCHED_MOVEMENT.md',
       'evaluated_commit':os.environ.get('GITHUB_SHA','local'),
       'original_RWS_primary':NATIVE_PRIMARY,'original_RWS_secondary':NATIVE_SECONDARY,
       'source_or_effect_status':'NOT_YET_SCORED',
       'no_GPS_bird_identifiers_geography_native_clock_exported':True,
       'no_true_foraging_or_active_time_budget_scored':True}
    try:
        gps,receipt=fetch_original_gulls()
        if not receipt['2020_original_publisher_GPS_MD5_verified']:
            raise OriginalSourceStop('STOP_NO_GENUINE_ORIGINAL_GULL_GPS_PROVIDER_MD5')
        report['native_2020_gull_original_source_provenance']=receipt
        print('V111_GULL_ORIGINAL_NATIVESOURCE_AUTHENTICATED '+json.dumps({
          'year':2020,'original_real_birds_common_months':receipt[
            'source_MayAug_individual_and_hour_support']['original_birds_present_MayAug_by_species'],
          'actual_native_GPS_hours':receipt[
            'source_MayAug_individual_and_hour_support']['one_tag_hour_GPS_fixes_in_COMMON_MayAug_by_species'],
          'publisher_md5_verified':True},sort_keys=True),flush=True)
    except (SourceNotAdmitted,OriginalSourceStop,ValueError,TimeoutError) as e:
        report['source_or_effect_status']='NOT_ADMITTED_GULL_ORIGINAL_GPS_SOURCE'
        report['source_stop_gull_GPS']=str(e)[:300]
        return write_report(report,output)

    gauges={}
    gaugeproof={}
    for station in (NATIVE_PRIMARY,NATIVE_SECONDARY):
        try:
            original,receipt=original_2020_gauge_may_aug(station,sleeper=time.sleep)
            gauges[station]=original
            gaugeproof[station]={'source_status':'REAL_NATIVE_2020_FOUR_MONTH_RWS_NAP_ADMITTED',**receipt}
        except (OriginalSourceStop,ValueError,TimeoutError) as e:
            gaugeproof[station]={'source_status':'NOT_ADMITTED_OFFICIAL_2020_TIDE_SOURCE',
                                 'source_failure':str(e)[:280]}
        print('V111_REAL_2020_ROOMPO_GAUGE_SOURCE '+json.dumps({
            'station':station,'status':gaugeproof[station]['source_status'],
            'original_measured_10minute_n':gaugeproof[station].get('total_unique_actual_measured_NAP_10min_timestamps'),
            'source_failures':gaugeproof[station].get('source_failure')},sort_keys=True),flush=True)
    report['real_2020_official_RWS_May_Aug_source_provenance']=gaugeproof
    if NATIVE_PRIMARY not in gauges:
        report['source_or_effect_status']='NOT_ADMITTED_ORIGINAL_2020_PRIMARY_RWS_TIDE'
        return write_report(report,output)
    # Source-only movement step count is computed before reading event tide and solar.
    original_20km,qa=original_movement_opportunities(gps,radius=20.)
    report['original_tide_unread_GPS_20km_movement_source_quality']=qa
    print('V111_ORIGINAL_GULL_MOVEMENT_GPS_SOURCE_FIRST '+json.dumps(qa,sort_keys=True),flush=True)
    four,admit=fourway_original_source(original_20km,gauges[NATIVE_PRIMARY])
    report['source_tide_solar_fourcell_primary_outside_20km']=admit
    print('V111_ORIGINAL_RWS_TIDE_ASTRAL_SOURCE_4CELL_BEFORE_Y '+json.dumps(admit,sort_keys=True),flush=True)
    # Do not examine even original GPS displacements within the cells unless
    # BOTH species pass the pre-outcome independent-bird/phase/month thresholds.
    if not admit['source_each_species_admitted']:
        report['source_or_effect_status']='NOT_ADMITTED_BOTH_ORIGINAL_TAXA_TIDE_SUN_FOURCELL'
        # Continue source-only radius 10/30m QA WITHOUT movement Y scoring.
        for radius in (10.,30.):
            other,otherqa=original_movement_opportunities(gps,radius=radius)
            report.setdefault('source_QA_fixed_radius_sensitivity',{})[str(radius)]=otherqa
        return write_report(report,output)

    result=score_if_original_two_species_admitted(four,admit)
    report['source_or_effect_status']=result['status']
    report['original_2020_bird_equal_species_fourcell_movement_proxy_effect']=result
    report['source_preserving_RWS_phase_ghost_control']={}
    for days in PHASE_GHOST_DAY_SHIFTS:
        g,gate=fourway_original_source(original_20km,gauges[NATIVE_PRIMARY],
                 source_ghost_shift_days=days)
        res=score_if_original_two_species_admitted(g,gate)
        report['source_preserving_RWS_phase_ghost_control'][f'+{days}days']={
             'source_native_original_tide_phase_and_height_shift_days':days,
             'original_birds_and_4cell_source_gate':gate,
             'test_if_original_source_passes_not_force_ghost_effect':res}
        print('V111_GHOST_TRUE_RWS_PHASE_SOURCE '+json.dumps({
          'shift_days':days,'original_source_both_taxa':gate['source_each_species_admitted'],
          'source_status':res['status'],
          'original_2species_D_if_admitted':res.get('primary_two_species_bird_equal_D_difference')},
          sort_keys=True),flush=True)

    for radius in (10.,30.):
        other,sourceqa=original_movement_opportunities(gps,radius=radius)
        groups,gate=fourway_original_source(other,gauges[NATIVE_PRIMARY])
        report.setdefault('source_QA_fixed_radius_sensitivity',{})[str(radius)]={
            **sourceqa,'real_RWS_2020_source_fourway':gate}
        if gate['source_each_species_admitted']:
            report.setdefault('secondary_real_radius_species_score',{})[str(radius)]=(
                score_if_original_two_species_admitted(groups,gate))
        else:
            report.setdefault('secondary_real_radius_species_score',{})[str(radius)]={'status':'NOT_ESTIMATED_SOURCE_GATE'}
    print('V111_REAL_TWO_SPECIES_2020_TIDE_SUN_GPS_RESULT '+json.dumps({
       'biological_movement_proxy_status':report['source_or_effect_status'],
       'observed_original_bird_species_result':result.get('species_source_results'),
       'observed_species_contrast':result.get('primary_two_species_bird_equal_D_difference'),
       'real_bird_bootstrap95':result.get('primary_two_species_original_bird_cluster_bootstrap95'),
       'source_true_original_tide_ghosts':[
            {'days':k,'status':v['test_if_original_source_passes_not_force_ghost_effect']['status']}
            for k,v in report['source_preserving_RWS_phase_ghost_control'].items()],
       'NO_forage_time_or_genuine_local_dryflat_area_inferred':True},
       sort_keys=True),flush=True)
    return write_report(report,output)

def write_report(report,output):
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V111_ORIGINAL_FIELD_FINAL '+json.dumps({
       'status':report['source_or_effect_status'],
       'primary_RWS_source':report.get('real_2020_official_RWS_May_Aug_source_provenance',{}).get(NATIVE_PRIMARY,{}).get('source_status'),
       'source_primary_fourcell_gates':report.get('source_tide_solar_fourcell_primary_outside_20km',{}).get('original_source_all_species'),
       'effect_or_source_gate':'biological_result' if report['source_or_effect_status'].startswith('EXPLORATORY_REAL') else 'source_not_admitted_no_effect',
       'original_gull_GPS_md5_admitted':bool(report.get('native_2020_gull_original_source_provenance')),
       'no_animal_identifiers_or_precise_locations_exported':True},sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    v=parser.parse_args();run(v.output)
