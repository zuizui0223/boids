"""v113 genuine publisher original 2020 two-Larus birds:
Post-v112 *exploratory* orthogonal balanced location use B, solar S,
measured tide phase T, tide×sun interaction I on genuine native
GIC RF>=50 used GPS pixels. Original v112 full source I MUST exactly replay
BEFORE NEW May–July matched-species months are scored.

Not actual prey, dry tidalflat availability, feeding, or internal clocks.
"""
from __future__ import annotations
from pathlib import Path
import argparse,json,os
from original_2020_gull_RWS_source import (
    fetch_original_gulls,original_2020_gauge_may_aug,
    NATIVE_PRIMARY,NATIVE_SECONDARY,OriginalSourceStop,SourceNotAdmitted)
from real_2020_gull_GIC_native_pixels import (
    source_2020_original_gull_GIC_pixels,radius_subset)
from gull_GIC_native_tidesolar_occupancy import (
    source_fourcell_only,PHASE_GHOST_DAY_SHIFTS)
from orthogonal_tide_solar_gull_GIC_used_pixel import (
    FIXED_SOURCE_MONTHS_COMMON,verify_previous_v112_original_replay,
    summarize_source_orthogonal_BSTI,BASIS)
SOURCE_OLD_V112_RUN=42767959138
FROZEN_V113_DOC='docs/V113_FROZEN_TWO_GULL_SOLAR_TIDE_MAIN_AND_INTERACTION.md'

def emit(report,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    p=report.get('new_2020_two_species_MayJuly_solar_tide_additive_components') or {}
    print('V113_REAL_ORIGINAL_GULL_B_S_T_I_FINAL '+json.dumps({
      'status':report['source_or_outcome_status'],
      'v112_full_MayAug_old_I_exactly_replayed':
          (report.get('v112_prior_original_source_interaction_replay') or {}).get('status'),
      'new_MayJuly_source_passed':
          (report.get('native_MayJuly_two_species_source_gate') or {}).get(
               'original_raster_and_fourcell_gates_pass'),
      'new_genuine_2020_source_species':
          p.get('individual_original_species'),
      'new_species_S_T_B_I_descriptive_contrasts':
          p.get('independent_two_species_contrasts'),
      'phase_ghosts':{
          k:{'source_pass':v['source']['original_raster_and_fourcell_gates_pass'],
             'S_taxon_difference':(v.get('effects') or {}).get(
               'independent_two_species_contrasts',{}).get('S_night_minus_day',{})}
             for k,v in (report.get('new_original_2020_RWS_phase_ghosts') or {}).items()},
      'no_individual_native_GPS_2020_or_tide_values_exported':True},
      sort_keys=True),flush=True)
    return report

def run(v105_geo,outpath):
    report={'analysis':'V113_ORIGINAL_2020_TWO_GULLS_GIC_RF50_FOURWAY_ORTHOGONAL_SOLAR_TIDE_MAIN_PLUS_INTERACTION',
       'source_original_GPS_year':2020,
       'original_source_RWS_outside':NATIVE_PRIMARY,
       'original_native_GIC_wetland_years':'2017-2019',
       'previous_original_real_v112_run':SOURCE_OLD_V112_RUN,
       'post_previous_field_null_result_exploratory':True,
       'frozen_protocol':FROZEN_V113_DOC,
       'new_equal_source_calendar_months':[5,6,7],
       'no_original_GPS_bird_identifiers_exact_geolocations_times_or_tide_arrays_exported':True,
       'NO_TRUE_TIDAL_FLAT_EXPOSURE_OR_FORAGING_OR_TIME_BUDGET_OBSERVED':True,
       'source_or_outcome_status':'SOURCE_PENDING'}
    try:
        birds,gpsproof=fetch_original_gulls()
        report['original_GPS_Zenodo_2020_publisher_MD5_source']=gpsproof
        original_tide,tidereceipt=original_2020_gauge_may_aug(NATIVE_PRIMARY)
        report['original_2020_RWS_OUTSIDE_MayAug_source_metadata']=tidereceipt
    except (SourceNotAdmitted,OriginalSourceStop,TimeoutError,ValueError,OSError) as e:
        report['source_or_outcome_status']='SOURCE_STOP_REAL_ORIGINAL_GPS_OR_TIDE'
        report['genuine_original_source_failure']=repr(e)[:220]
        return emit(report,outpath)
    try:
        original30, rasterproof=source_2020_original_gull_GIC_pixels(birds,v105_geo)
        report['original_GIC_2017_2019_RF_source_proof']=rasterproof
    except (OriginalSourceStop,SourceNotAdmitted,TimeoutError,ValueError,OSError) as e:
        report['source_or_outcome_status']='SOURCE_STOP_REAL_GIC_PUBLISHER_RASTER'
        report['genuine_GIC_original_error']=repr(e)[:220]
        return emit(report,outpath)
    original20=radius_subset(original30,20.)
    full,fullgate=source_fourcell_only(original20,original_tide,
                                         require_GIC_pixel=True)
    report['original_exact_v112_MayAug_Source_QA']=fullgate
    if not fullgate['original_raster_and_fourcell_gates_pass']:
        report['source_or_outcome_status']='SOURCE_STOP_V112_PREVIOUS_BIOLOGICAL_SOURCE_NOT_REPLAYED'
        return emit(report,outpath)
    try:
        replay=verify_previous_v112_original_replay(full,fullgate)
    except ValueError as e:
        report['source_or_outcome_status']='SOURCE_STOP_V112_PREVIOUS_FIELD_EFFECT_REPLAY_DRIFT'
        report['prior_source_replay_stop']=repr(e)[:220]
        return emit(report,outpath)
    report['v112_prior_original_source_interaction_replay']=replay
    print('V113_EXACT_PREVIOUS_V112_BIOTIC_GIC_INTERACTION_REPLAY_BEFORE_NEW_B_S_T '+json.dumps(replay,sort_keys=True),flush=True)
    prior_sensitivity=summarize_source_orthogonal_BSTI(full,fullgate,
         source_label='POST_V112_SECONDARY_ALL_ORIGINAL_MayAug')
    report['secondary_full_MayAug_BSTI_same_species_source_as_original_v112']=prior_sensitivity

    original_common=[x for x in original20 if x['month'] in FIXED_SOURCE_MONTHS_COMMON]
    cells,source=source_fourcell_only(original_common,original_tide,
                                     require_GIC_pixel=True)
    report['native_MayJuly_two_species_source_gate']=source
    print('V113_FIRST_NEW_COMMON_MayJuly_SOURCE_GATE '+json.dumps({
       'original_bird_true_fourcell_species':source['per_species_native_source'],
       'source_GIC_mask_original_species':source['source_genuine_GIC_RF_pixel_coverage'],
       'both_species_pass_original_MayJuly_4cell_source':source['original_raster_and_fourcell_gates_pass'],
       'new_BSTI_values_NOT_YET_SCORED':True},sort_keys=True),flush=True)
    if not source['original_raster_and_fourcell_gates_pass']:
        report['source_or_outcome_status']='NOT_ESTIMATED_MATCHED_2020_MAY_JULY_GENUINE_TWO_SPECIES_SOURCE'
        return emit(report,outpath)
    new=summarize_source_orthogonal_BSTI(cells,source,
          source_label='PRIMARY_NEW_POST_V112_MayJuly_BOTH_GULL_SPECIES')
    report['new_2020_two_species_MayJuly_solar_tide_additive_components']=new
    report['source_or_outcome_status']='EXPLORATORY_2020_TWO_SPECIES_MATCHED_MayJuly_BSTI_ORIGINAL_BIRDS_COMPUTED'
    report['new_original_2020_RWS_phase_ghosts']={}
    for days in PHASE_GHOST_DAY_SHIFTS:
        c,s=source_fourcell_only(original_common,original_tide,
                     phase_shift_days=days,require_GIC_pixel=True)
        result=summarize_source_orthogonal_BSTI(c,s,
                  source_label=f'GHOST_ORIGINAL_RWS_SHIFT_PLUS{days}_DAYS')
        report['new_original_2020_RWS_phase_ghosts'][f'+{days}days']={
           'days_tide_shifted_not_sun_or_GIC_or_GPS':days,
           'source':s,'effects':result}
        print('V113_REAL_RWS_TIDE_PHASE_GHOST_BSTI '+json.dumps({
           'shift_days':days,
           'fourcell_genuine_bird_source_admitted':s['original_raster_and_fourcell_gates_pass'],
           'effect_status':result['status'],
           'species_solar_S_contrast':(result.get('independent_two_species_contrasts') or {}).get('S_night_minus_day',{})},
           sort_keys=True),flush=True)
    # Two recorded water bodies separated by storm surge barrier:
    # IN-side tide is never automatically assigned as primary gauge for outside GPS.
    try:
        inside,insideproof=original_2020_gauge_may_aug(NATIVE_SECONDARY)
        c,s=source_fourcell_only(original_common,inside,require_GIC_pixel=True)
        report['separate_inside_Roompot_source_as_sensitivity_NOT_primary']={
          'RWS_inside_measured_source_proof':insideproof,
          'original_fourcell_bird_gauge_source':s,
          'secondary_BSTI_if_both_taxa_source_admitted':
             summarize_source_orthogonal_BSTI(c,s,
             source_label='SECONDARY_ROOMPOSLUIS_BINNEN_ANOTHER_WATERBODY')}
    except (OriginalSourceStop,ValueError,TimeoutError,OSError) as e:
        report['separate_inside_Roompot_source_as_sensitivity_NOT_primary']={
          'status':'SOURCE_UNAVAILABLE_SECONDARY_INLET_WATERBODY_ONLY',
          'reason':repr(e)[:200]}
    return emit(report,outpath)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v105-original-GIC-georeferencing-source',required=True)
    p.add_argument('--output',required=True)
    x=p.parse_args();run(x.v105_original_GIC_georeferencing_source,x.output)
