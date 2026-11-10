"""v112 REAL original 2020 gull GPS×2017–2019 native GIC RF wetland
site-use × measured 2020 Roompot Buiten/Binnen tide × Astral SUN source.
Only exploratory POST-v111 independent spatial response; no foraging or
actual tide-exposed habitat. All source/QC before observed animal scores.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse,json,os,time
from original_2020_gull_RWS_source import (
    fetch_original_gulls,original_2020_gauge_may_aug,
    NATIVE_PRIMARY,NATIVE_SECONDARY,OriginalSourceStop,SourceNotAdmitted)
from real_2020_gull_GIC_native_pixels import (
    source_2020_original_gull_GIC_pixels,radius_subset)
from gull_GIC_native_tidesolar_occupancy import (
    source_fourcell_only,original_bird_bootstrap_GIC_occupancy,
    descriptive_real_RF_location_use,PHASE_GHOST_DAY_SHIFTS,
    GIC_PRIMARY_THRESHOLD,GIC_SECONDARY_THRESHOLD)
from original_delta_2020_gull_source import FOCAL

PREVIOUS_V111_ORIGINAL_BIOLOGICAL_MOVEMENT_NULL=42748780612
ORIGINAL_GIC_FIRST_TILE_SOURCE=42737124600
ORIGINAL_V110_SOURCE=42747546101
PHASE_RWS_MAIN=NATIVE_PRIMARY
RUN_TITLE='V112_ORIGINAL_2020_TWO_GULL_GIC_STATIC_TIDALWETLAND_USED_GPS_PIXEL_TIDE_LIGHT_EXPLORATORY'
def write(report,path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V112_REAL_ORIGINAL_GULL_HABITAT_TIDE_SUN_FINAL '+json.dumps({
       'status':report.get('status'),
       'native_original_GIC_pixel_QA':(report.get('source_GIC_original_2020_GPS_pixel_proof') or {}).get(
           'source_GIC_pixel_gull_species_QA'),
       'source_RWS':{k:v.get('status') for k,v in report.get('source_RWS_official_2020_MayAug',{}).items()},
       'species_original_fourcell_source':(report.get('source_original_20km_tide_solar_GIC_valid_cells') or {}).get(
         'per_species_native_source'),
       'species_contrast':(report.get('primary_gull_GIC_tidalwetland_RF50_spatial_use') or {}).get(
          'species_contrast_true_original_bird_equal_D'),
       'species_contrast_95':(report.get('primary_gull_GIC_tidalwetland_RF50_spatial_use') or {}).get(
          'species_contrast_independent_whole_bird_bootstrap_95pct'),
       'source_no_actual_true_forage_or_dry_intertidal':True},sort_keys=True),flush=True)
    return report

def run(v105_original_raster_audit,output):
    report={'analysis':RUN_TITLE,'target_original_2020_common_months':[5,6,7,8],
        'corresponding_true_source_2020_gull_GPS_MD5_run':42746796941,
        'corresponding_true_2020_Roompot_tide_source_run':ORIGINAL_V110_SOURCE,
        'corresponding_original_GIC_2019_native_raster_source_run':ORIGINAL_GIC_FIRST_TILE_SOURCE,
        'frozen_protocol':'docs/V112_FROZEN_2020_GULL_NATIVE_GIC_OCCUPANCY_RWS_SOLAR.md',
        'POST_v111_original_movement_tide_solar_null_exploratory':True,
        'previous_real_v111_run':PREVIOUS_V111_ORIGINAL_BIOLOGICAL_MOVEMENT_NULL,
        'no_precise_GPS_locations_private_bird_IDs_or_RWS_water_height_arrays_exported':True,
        'science_boundary':'static source GIC tidal wetland RF agreement not actual tidalflat dry hours or observed bird feeding',
        'status':'SOURCE_PENDING'}
    try:
        birds,source=fetch_original_gulls()
        report['authentic_original_Zenodo_two_gull_2020_year_source']=source
        print('V112_SOURCE_ZENODO_TWO_GULLS '+json.dumps({
            'corrected_record':source['corrected_original_Zenodo_record'],
            'original_year_MayAug_tag_counts':source['source_MayAug_individual_and_hour_support'][
               'original_birds_present_MayAug_by_species'],
            'original_source_MD5_verified':source['2020_original_publisher_GPS_MD5_verified'],
            'new_behavioral_effect_scored':False},sort_keys=True),flush=True)
    except (SourceNotAdmitted,OriginalSourceStop,ValueError,TimeoutError,OSError) as e:
        report['status']='NOT_ADMITTED_2020_ORIGINAL_PUBLISHER_GPS'
        report['source_blocker']=repr(e)[:250]
        return write(report,output)

    gauges={}
    report['source_RWS_official_2020_MayAug']={}
    for name in (NATIVE_PRIMARY,NATIVE_SECONDARY):
        try:
            d,proof=original_2020_gauge_may_aug(name)
            gauges[name]=d
            report['source_RWS_official_2020_MayAug'][name]={
                'status':'VERIFIED_OFFICIAL_ORIGINAL_2020_RWS_Roompot_WATHTE_cm_NAP',
                **proof}
        except (OriginalSourceStop,ValueError,TimeoutError,OSError) as e:
            report['source_RWS_official_2020_MayAug'][name]={
                'status':'NOT_ADMITTED_OFFICIAL_ORIGINAL_2020_RWS_MEASURED_WATER',
                'source_blocker':repr(e)[:240]}
    if NATIVE_PRIMARY not in gauges:
        report['status']='NOT_ADMITTED_2020_ORIGINAL_RWS_ROOMPO_OUTSIDE_TIDE_SOURCE'
        return write(report,output)

    try:
        fixed_events,proof=source_2020_original_gull_GIC_pixels(
           birds,v105_original_raster_audit)
        report['source_GIC_original_2020_GPS_pixel_proof']=proof
    except (ValueError,OriginalSourceStop,SourceNotAdmitted,
            TimeoutError,OSError) as e:
        report['status']='NOT_ADMITTED_NATIVE_ORIGINAL_2017_2019_GIC_RASTER'
        report['source_GIC_error']=repr(e)[:240]
        return write(report,output)
    site=radius_subset(fixed_events,20.)
    report['original_20km_gull_bird_hour_GPS_count_before_source_tide']=len(site)
    report['source_2020_gull_GIC_RF_used_point_fraction_not_tide_interaction']=(
        descriptive_real_RF_location_use(site))
    print('V112_ORIGINAL_GULL_GIC_2019_PIXELS_SOURCE_ONLY '+json.dumps({
       'genuine_GIC_native_tiles':proof['source_original_GIC_tile_count'],
       'source_tile_byte_receipts':proof['source_original_GIC_TIFF_receipts_anonymized'],
       'n_original_2020_bird_hour_GPS_source_within20km':len(site),
       'original_GIC_RF50_used_point_descriptive_only':
           report['source_2020_gull_GIC_RF_used_point_fraction_not_tide_interaction'],
       'NO_animal_time_niche_effect_yet':True},sort_keys=True),flush=True)

    allgroups,allsource=source_fourcell_only(
        site,gauges[NATIVE_PRIMARY],require_GIC_pixel=False)
    report['source_original_20km_tide_solar_all_GPS_cells_no_GIC_mask_yet']=allsource
    print('V112_TRUE_GULL_TIDE_SOLAR_SOURCE_BEFORE_NATIVE_GIC_Y '+json.dumps({
        'native_RWS_real_tide_and_sun_group_n':allsource[
             'n_original_2020_source_point_time_tide_sun_4cell_groups'],
        'species':allsource['per_species_native_source'],
        'is_outcome_estimated':False},sort_keys=True),flush=True)

    groups,admit=source_fourcell_only(
        site,gauges[NATIVE_PRIMARY],require_GIC_pixel=True)
    report['source_original_20km_tide_solar_GIC_valid_cells']=admit
    print('V112_TRUE_GULL_TIDE_SOLAR_GIC_PIXEL_SOURCE_BEFORE_BIOLOGY '+json.dumps({
        'original_native_RWS_and_GIC_source_pass':admit['original_raster_and_fourcell_gates_pass'],
        'original_gull_species_bird_fossil_source':admit['per_species_native_source'],
        'genuine_GIC_RF_pixel_source_coverage':admit['source_genuine_GIC_RF_pixel_coverage'],
        'new_GIC_wetland_source_effect_NOT_YET_ESTIMATED':True},sort_keys=True),flush=True)
    if not admit['original_raster_and_fourcell_gates_pass']:
        report['status']='NOT_ESTIMATED_GULL_TIDE_SUN_GIC_SOURCE_GATES'
        return write(report,output)

    observed=original_bird_bootstrap_GIC_occupancy(groups,admit,GIC_PRIMARY_THRESHOLD)
    report['primary_gull_GIC_tidalwetland_RF50_spatial_use']=observed
    report['secondary_same_original_individuals_GIC_RF20_spatial_use']=(
        original_bird_bootstrap_GIC_occupancy(groups,admit,GIC_SECONDARY_THRESHOLD))
    report['secondary_same_original_individuals_GIC_RF_continuous_0_1']=(
        original_bird_bootstrap_GIC_occupancy(groups,admit,'continuous'))
    report['status']='EXPLORATORY_ORIGINAL_2020_TWO_GULL_GIC_SPATIAL_TIDE_SOLAR_ESTIMATED'
    report['original_native_RWS_phase_ghosts']={}
    for shift in PHASE_GHOST_DAY_SHIFTS:
        ghosts,source=source_fourcell_only(
            site,gauges[NATIVE_PRIMARY],phase_shift_days=shift,require_GIC_pixel=True)
        outcome=original_bird_bootstrap_GIC_occupancy(
            ghosts,source,GIC_PRIMARY_THRESHOLD)
        report['original_native_RWS_phase_ghosts'][f'{shift}day']={
            'original_tide_phase_source_shift_days':shift,
            'original_GPS_source_sun_and_GIC_static_values_unchanged':True,
            'original_native_ghost_tide_solar_source_QA':source,
            'original_ghost_species_RF50_contrast_only_if_source_passed':outcome}
        print('V112_REAL_2020_GIC_TIDE_GHOST '+json.dumps({
           'phase_shift_days':shift,
           'original_source_gate':source['original_raster_and_fourcell_gates_pass'],
           'ghost_status':outcome['result_status'],
           'original_ghost_bird_equal_species_contrast':
               outcome.get('species_contrast_true_original_bird_equal_D')},
           sort_keys=True),flush=True)
    if NATIVE_SECONDARY in gauges:
        inside,source=source_fourcell_only(
            site,gauges[NATIVE_SECONDARY],require_GIC_pixel=True)
        report['separate_original_RWS_Roompot_Binnen_WATERBODY_sensitivity']={
            'different_inside_Oosterschelde_water_body_not_original_primary':True,
            'original_tide_solar_source_QA':source,
            'original_species_RF50_if_both_native_source_gates_admitted':(
                original_bird_bootstrap_GIC_occupancy(
                    inside,source,GIC_PRIMARY_THRESHOLD))}
    for radius in (10.,30.):
        subset=radius_subset(fixed_events,radius)
        sourcecells,source=source_fourcell_only(
            subset,gauges[NATIVE_PRIMARY],require_GIC_pixel=True)
        report.setdefault('secondary_source_GEOGRAPHIC_RADIUS_SENSITIVITY',{})[str(radius)]={
            'radius_km':radius,
            'original_tag_hour_GPS_source_point_count':len(subset),
            'source_GIC_pixel_tide_solar_QA':source,
            'original_species_primary_RF50_if_source_admitted':(
                original_bird_bootstrap_GIC_occupancy(
                    sourcecells,source,GIC_PRIMARY_THRESHOLD))}
    print('V112_REAL_ORIGINAL_2020_GULL_GIC_TIDE_SOLAR_OBSERVED '+json.dumps({
        'status':report['status'],
        'species':observed.get('original_species'),
        'species_contrast':observed.get('species_contrast_true_original_bird_equal_D'),
        'whole_bird_CI95':observed.get('species_contrast_independent_whole_bird_bootstrap_95pct'),
        'original_phase_ghosts_source_and_bird_CI':{
            k:{'source_pass':v['original_native_ghost_tide_solar_source_QA'][
                'original_raster_and_fourcell_gates_pass'],
               'contrast':v['original_ghost_species_RF50_contrast_only_if_source_passed'].get(
                   'species_contrast_true_original_bird_equal_D')}
            for k,v in report['original_native_RWS_phase_ghosts'].items()},
        'no_direct_forage_or_actual_dry_flat':True},sort_keys=True),flush=True)
    return write(report,output)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v105-real-GIC-source-audit',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args();run(args.v105_real_GIC_source_audit,args.output)
