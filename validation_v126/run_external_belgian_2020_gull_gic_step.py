"""v126 genuine 2020 Belgian independent gull original pub-MD5 GPS + genuine
2017–2019 GIC static tidal-WETLAND equal-REAL-GPS-step 7 rotated controls.
SOURCE-only replay of v125 original bird/hour/step counts before new map Y.
TIDE-SOLAR SPECIES TIME NICHE NOT TESTED, no local Belgian sea level.
"""
from __future__ import annotations
from pathlib import Path
import argparse,json,os
from original_2020_belgium_gull_source import (
    PANELS,native_catalog,checked_original_file,source_reference_taxa,
    parse_native_gps,OriginalSourceStop)
from external_belgian_gull_step_statistics import (
    original_hourly_steps_from_v125_eligible_tracks,
    check_original_v125_source_replay,get_gic_source_gate,
    compute_bird_equal_original_Z,SEASON)
from original_GIC_equal_step_rotated_destinations import native_GIC_same_step_endpoint_pixels

SOURCE_OLD_V125=43216441141
SOURCE_NATIVE_GIC_V105=42737124600
PROTOCOL='docs/V126_FROZEN_2020_BELGIUM_EXTERNAL_GIC_EQUAL_STEP_HOLDOUT.md'

def emit(report,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    q=report.get('new_external_belgium_true_bird_spatial_result') or {}
    print('V126_ORIGINAL_INDEPENDENT_2020_BELGIUM_GULL_GIC_EQUAL_STEP_RESULT '+json.dumps({
       'panel':report['original_tracking_study'],'status':report['source_and_ecology_status'],
       'old_2020_bird_hour_and_step_source_replayed_exactly':(
            report.get('v125_authentic_2020_bird_source_replay') or {}).get(
               'all_v125_real_2020_source_animal_counts_and_hour_steps_replayed_exactly'),
       'new_original_2020_JulAug_movement_source_n':(
           report.get('original_native_JulOct_source_and_JulAug_frozen_steps') or {}).get(
               'original_2020_JulAug_first_tag_hour_valid_source_step_count'),
       'native_source_GIC_all8_fraction':(
           report.get('original_genuine_2020_GIC_eight_source_gate') or {}).get(
               'original_native_GIC_source_complete_fraction'),
       'source_true_tagged_bird_n_if_scored':q.get('original_2020_true_independent_birds_scored'),
       'external_B_step_RF50':q.get('primary_per_bird_equal_month_equal_B_GIC_RF50_step_enrichment'),
       'external_bird95':q.get('primary_10000_original_tagged_bird_bootstrap95'),
       'solar_only_secondary':q.get('secondary_solar_DAY_NIGHT_source_scored_with_own_missingness_gate'),
       'source_stop_reason':report.get('source_stop_reason'),
       'NO_LOCAL_TIDE_OR_REAL_2020_DRY_FLAT_OR_FORAGING_MEASURED':True
    },sort_keys=True),flush=True)
    return report

def run(panel,oldv125,v105,out):
    if panel not in PANELS:raise ValueError('STOP_V126_NONFROZEN_2020_STUDY_PANEL')
    spec=PANELS[panel]
    report={'analysis':'V126_TRUE_EXTERNAL_2020_BELGIAN_GULL_2017_2019_GIC_EQUAL_REAL_STEP_RF50',
       'original_tracking_study':panel,
       '2020_original_Zenodo_publisher_record':spec['record'],
       '2020_original_publisher_GPS_source_MD5_frozen':spec['md5'],
       'original_2017_2019_global_GIC_geography_source_run':SOURCE_NATIVE_GIC_V105,
       'previous_source_v125_original_true_Belgian_cohort_run':SOURCE_OLD_V125,
       'new_year_season_frozen_2020':list(SEASON),
       'original_2020_source_age_category':'juvenile' if panel=='LBBG_JUVENILE' else 'adult',
       'prespecified_original_colony_40km_scope':list(spec['colony']),
       'frozen_source_and_comparison_contract':PROTOCOL,
       'source_and_ecology_status':'SOURCE_PENDING',
       'NO_BELGIUM_TIDE_PHASE_OR_INTERACTION_FITTED':True,
       'NO_REAL_2020_INTERTIDAL_DRY_AREA_OR_BIRD_FORAGING_ANNOTATED':True,
       'NO_ORIGINAL_BIRD_ID_OR_PRECISE_GPS_TIME_COORDINATES_EXPORTED':True}
    try:
        original=json.loads(Path(oldv125).read_text())
        manifests,manifestproof=native_catalog(panel)
        report['original_2020_pub_metadata_MD5_source']=manifestproof
        ref,refproof=checked_original_file(manifests[panel+'-reference-data.csv'])
        taxa,taxonproof=source_reference_taxa(ref)
        schema,schemaproof=checked_original_file(manifests['datapackage.json'])
        native=json.loads(schema)
        if not isinstance(native,dict) or not isinstance(native.get('resources'),list):
            raise OriginalSourceStop('SOURCE_STOP_ORIGINAL_ZENODO_CORRECT_DATAPACKAGE')
        gps,gpsproof=checked_original_file(manifests[spec['gps']])
        report['new_authenticated_original_2020_GPS_MD5_source']=gpsproof
        parsed,private=parse_native_gps(gps,taxa,panel,return_private_eligible_tracks=True)
        original_events,originalqa=original_hourly_steps_from_v125_eligible_tracks(private,panel)
        report['original_native_JulOct_source_and_JulAug_frozen_steps']=originalqa
        replay=check_original_v125_source_replay(panel,original,parsed,originalqa)
        report['v125_authentic_2020_bird_source_replay']=replay
        print('V126_PREVIOUS_GENUINE_V125_SOURCE_REPLAY_BEFORE_ANY_GIC_RF '+json.dumps({
            'panel':panel,'status':replay,
            'new_frozen_season_native_source_steps':len(original_events),
            'GIC_NATIVE_RF_Y_NOT_READ_YET':True},sort_keys=True),flush=True)
    except (OriginalSourceStop,ValueError,KeyError,TimeoutError,OSError) as e:
        report['source_and_ecology_status']='SOURCE_STOP_ORIGINAL_V125_BIRD_OR_ZENODO_MD5_DRIFT'
        report['source_stop_reason']=str(e)[:260]
        return emit(report,out)
    if len(original_events)<1000:
        report['source_and_ecology_status']='NOT_ESTIMATED_2020_JUL_AUG_ORIGINAL_SOURCE_TOO_FEW_GPS_STEPS'
        return emit(report,out)

    try:
        events,proof=native_GIC_same_step_endpoint_pixels(original_events,v105)
        report['original_genuine_GIC_publisher_TIFF_MD5_and_all8_source_coverage']=proof
        print('V126_GENUINE_GIC_ALL8_PUBLISHER_SOURCE_BEFORE_ECOLOGICAL_SCORE '+json.dumps({
           'study':panel,
           'original_native_GIC_provider_MD5_verified':all(
                 x['source_publisher_MD5_verified']
                 for x in proof['original_GIC_provider_MD5_receipts']),
           'original_GIC_source_coverage':proof['original_GIC_native_source_coverage'],
           'NO_SPATIAL_OR_TIME_EFFECT_SCORED_YET':True},sort_keys=True),flush=True)
    except (OriginalSourceStop,ValueError,KeyError,OSError,TimeoutError) as e:
        report['source_and_ecology_status']='NOT_ESTIMATED_GENUINE_GIC_MAP_PIXEL_SOURCE'
        report['source_stop_reason']=str(e)[:260]
        return emit(report,out)
    gate=get_gic_source_gate(events,panel,parsed)
    report['original_genuine_2020_GIC_eight_source_gate']=gate
    if gate['status']!='ORIGINAL_PUBLISHED_GIC_2020_EIGHT_PIXEL_SOURCE_ADMITTED':
        report['source_and_ecology_status']='NOT_ESTIMATED_FIXED_GIC_SOURCE_COVERAGE_OR_TRUE_BIRDS'
        return emit(report,out)
    score=compute_bird_equal_original_Z(events,gate,panel)
    report['new_external_belgium_true_bird_spatial_result']=score
    report['source_and_ecology_status']='EXPLORATORY_AUTHENTIC_2020_BELGIUM_EIGHT_STEP_GIC_SPATIAL_SOURCE_ESTIMATED'
    return emit(report,out)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--panel',required=True,choices=sorted(PANELS))
    p.add_argument('--prior-v125-genuine-source',required=True)
    p.add_argument('--v105-native-GIC-raster-audit',required=True)
    p.add_argument('--output',required=True)
    x=p.parse_args()
    run(x.panel,x.prior_v125_genuine_source,x.v105_native_GIC_raster_audit,x.output)
