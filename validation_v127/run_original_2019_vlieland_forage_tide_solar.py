"""v127 execute first genuine 2019 Vlieland ACC-inferred FORAGE vs INACTIVE
quarterhour share × official measured RWS tide × actual GPS-location solar.

HARD REPLAY of original successful v125/v126 publisher native source counts
before opening any true tide × sun ACC response. Source first, bird-bootstrap
only if pre-frozen full fourcell, true RWS June-Sep and sun gates pass.
No original bird IDs, real coordinates, UTC timestamp, ACC events or water
heights exported. These are algorithm-inferred classes not feeding minutes.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from original_2019_Vlieland_behaviour_source import (
    original_publisher_manifest,original_native_file,
    _reference_anonymous_identity,SourceStop,TemporarySourceFailure)
from real_2019_Vlieland_foraging_GPS_source import (
    authenticate_original_gps_2019,original_2019_gps_source_index,
    true_original_2019_behaviour_gps_join,GPS_FILE,BEHAVIOUR_FILE)
from real_2019_vlieland_RWS_fourmonths import (
    fetch_all_2019_Vlieland_real_RWS_months,validate_previous_RWS_48h_pilot,
    NativeTideSourceStop,request_real_month)
from vlieland_acc_forage_tide_sun_fourway import (
    original_2019_gps_acc_quarterhour_source,
    source_real_tide_sun_fourway,original_true_bird_BSTI_from_ACC_source,
    GHOST_DAYS,RNG_SEED)

ORIGINAL_V125_YEAR_SOURCE=43028807892
ORIGINAL_V126_GPS_RWS_SOURCE=43030597916
PREVIOUS_V126_GPS_N=1193728
PREVIOUS_V126_GPS_BIRDS=42
PREVIOUS_V125_ACC_N=1817033
PREVIOUS_V125_ACC_BIRDS=43
PREVIOUS_V126_SOURCE_GPS_JOIN_N=1567093
PREVIOUS_V126_25KM_BINARY_N=792527
PREVIOUS_V126_BIRDS_WITH_SOURCE=39
PREVIOUS_V126_BIRDS_BOTH_BIAS_QC=37
FROZEN_SPEC='docs/V127_FROZEN_2019_VLIELAND_ACCEL_CLASSIFIED_FORAGE_INACTIVE_RWS_TIDE_SUN.md'

def verify_previous_original_v126_source(old,GPS_QA,anonymous):
    if old.get('analysis')!='V126_ORIGINAL_2019_VLIELAND_NATIVE_FORAGE_INACTIVE_GPS_TIME_GEO_SOURCE_QA' or (
        old.get('source_status')!='ADMITTED_PUBLISHER_2019_VLIELAND_FORAGE_GPS_15MIN_25KM_SOURCE_ONLY'):
        raise SourceStop('STOP_V127_OLD_2019_VLIELAND_V126_SOURCE_RESULT_IDENTITY')
    before=old['original_2019_native_samebird_ACC_classification_GPS_time_space_link']
    prevGPS=old['original_year2019_GPS_native_source_count_and_monthly_QA']
    if (GPS_QA['native_original_2019_GPS_full_source_rows']!=PREVIOUS_V126_GPS_N or
       GPS_QA['native_original_2019_genuine_GPS_birds']!=PREVIOUS_V126_GPS_BIRDS or
       anonymous['source_original_v125_2019_rows_exact_replayed']!=PREVIOUS_V125_ACC_N or
       anonymous['source_original_2019_tagged_birds_source_exact_replayed']!=PREVIOUS_V125_ACC_BIRDS or
       anonymous['original_source_identity_and_time_QA'][
           'original_behaviour_true_same_bird_GPS_within_15min']!=PREVIOUS_V126_SOURCE_GPS_JOIN_N):
        raise SourceStop('STOP_V127_GENUINE_PRIOR_SOURCE_COUNTS_NOT_EXACTLY_REPLAYED')
    ours=anonymous['original_2019_local_behavior_to_original_GPS_by_radii']['25.0']
    prev=before['original_2019_local_behavior_to_original_GPS_by_radii']['25.0']
    if (ours['source_geography_coverage_QA']['source_original_GPS_linked_binary_class_events']!=
          PREVIOUS_V126_25KM_BINARY_N or
        ours['genuine_original_birds_with_2019_foraging_OR_inactive_GPS_matched_near_station']!=
          PREVIOUS_V126_BIRDS_WITH_SOURCE or
        ours['genuine_original_birds_with_both_native_labels_ge100_each_in_ge2months']!=
          PREVIOUS_V126_BIRDS_BOTH_BIAS_QC or
        ours['native_original_month_source']!=prev['native_original_month_source'] or
        GPS_QA['native_original_2019_GPS_full_source_rows']!=prevGPS['native_original_2019_GPS_full_source_rows']):
        raise SourceStop('STOP_V127_OLD_V126_25KM_NATIVE_GPS_CLASSIFIER_SOURCE_DRIFT')
    return {'status':'ORIGINAL_V125_V126_ZENODO_2019_NATIVE_CLASS_GPS_SOURCE_EXACTLY_REPLAYED',
        'original_publisher_record_id':10053988,
        'original_2019_source_native_GPS_rows':PREVIOUS_V126_GPS_N,
        'original_2019_true_GPS_birds':PREVIOUS_V126_GPS_BIRDS,
        'original_2019_classifier_event_rows':PREVIOUS_V125_ACC_N,
        'original_2019_classification_source_birds':PREVIOUS_V125_ACC_BIRDS,
        'original_2019_same_bird_ACC_to_GPS_joined_native_events':PREVIOUS_V126_SOURCE_GPS_JOIN_N,
        'original_2019_source_binary_class_event_25km':PREVIOUS_V126_25KM_BINARY_N,
        'original_2019_25km_source_birds_any_binary_class':PREVIOUS_V126_BIRDS_WITH_SOURCE,
        'original_2019_25km_source_birds_with_both_classes_gt100_in2months':PREVIOUS_V126_BIRDS_BOTH_BIAS_QC,
        'no_original_ids_coordinates_events_exported':True}

def original_RWS_transport_retry(month,sleeper=time.sleep):
    errors=[]
    for i in range(3):
        try:
            val=request_real_month(month)
            return val,{'same_original_RWS_source_attempts':i+1,
                'same_2019_RWS_month_transport_errors':errors}
        except (NativeTideSourceStop,SourceStop) as e:
            v=str(e)
            if not any(x in v for x in ('SOURCE_UNAVAILABLE_OR_RATE_LIMITED',
                   'HTTP Error 429','HTTP Error 502','HTTP Error 503',
                   'HTTP Error 504','timed out','TimeoutError')):
                raise
            errors.append({'original_month':month,'attempt':i+1,
                           'unchanged_original_provider_transport_error':v[:150]})
            if i==2:raise
            sleeper((i+1)*4)
    raise AssertionError('unreachable')

def output_report(report,path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    main=report.get('genuine_2019_behaviour_classifier_forage_share_tide_solar') or {}
    source=report.get('fourcell_original_2019_GPS_ACC_RWS_sun_BEFORE_Y') or {}
    print('V127_REAL_2019_VLIELAND_FORAGE_INACTIVE_TIDE_SUN_FIELD_RESULT '+json.dumps({
        'status':report['source_or_field_status'],
        'old_source_replayed':(report.get('v126_original_native_GPS_ACC_source_replay') or {}).get('status'),
        'four_month_RWS_source':(report.get('original_2019_full_RWS_measured_fourmonths') or {}).get('source_status'),
        'original_true_birds_15min_4cell_gate':source.get('true_original_source_all_four_conditions'),
        'real_original_bird_equal_B_S_T_I':main.get('original_true_bird_B_S_T_I_results'),
        'ghost_2019_true_RWS_phase_controls':{
           x:{'source_pass':a['original_RWS_phase_shift_fourcell_gate'][
               'true_original_source_admitted_before_forage_share_Y'],
               'interaction':(a['native_ACC_forage_share_effect_if_source_admitted'] or {}).get(
                   'original_true_bird_B_S_T_I_results',{}).get(
                        'I_rising_vs_falling_by_night_vs_day')}
           for x,a in (report.get('original_true_RWS_phase_ghosts') or {}).items()},
        'source_stop':report.get('source_stop_reason'),
        'NO_visual_feeding_or_actual_forage_minutes_or_causal_internal_tide_clock':True},
       sort_keys=True),flush=True)
    return report

def run(prior_v126_gps,prior_v126_rws,output):
    report={'analysis':'V127_ORIGINAL_2019_VLIELAND_GENUINE_ACC_PREDICTED_FORAGE_INACTIVE_GPS_RWS_SOLAR',
       'source_or_field_status':'SOURCE_PENDING',
       'source_frozen_before_ANY_2019_tide_solar_behaviour_effect':FROZEN_SPEC,
       'original_YEAR':2019,'common_source_months':[6,7,8,9],
       'prior_source_v125_action':ORIGINAL_V125_YEAR_SOURCE,
       'prior_original_GPS_RWS_v126_action':ORIGINAL_V126_GPS_RWS_SOURCE,
       'native_ACC_foraging_label':'forage',
       'native_ACC_binary_comparator':'inactive',
       'original_15min_BIN_is_not_15minutes_of_foraging':True,
       'actual_2019_RWS_harbour_h_NOT_local_patch_elevation_or_prey':True,
       'source_animal_GPS_exact_latlon_timestamps_and_TAGs_NOT_exported':True}
    try:
        old=json.loads(Path(prior_v126_gps).read_text())
        oldRWS=json.loads(Path(prior_v126_rws).read_text())
        report['previous_official_RWS_2019_48hour_pilot_exact']=validate_previous_RWS_48h_pilot(oldRWS)
        files,manifest=original_publisher_manifest()
        ref,referenceproof=original_native_file(files['O_VLIELAND-reference-data.csv'])
        birds,refqa=_reference_anonymous_identity(ref)
        acc,accproof=original_native_file(files[BEHAVIOUR_FILE])
        gps,gpsproof=authenticate_original_gps_2019()
        indexed,gpsqa=original_2019_gps_source_index(gps,birds)
        anonymous,private=true_original_2019_behaviour_gps_join(
             acc,birds,indexed,return_private_quarterhour_bins=True)
        report['v126_original_native_GPS_ACC_source_replay']=verify_previous_original_v126_source(
             old,gpsqa,anonymous)
        report['source_authenticated_original_Zenodo_md5_sha_provenance']={
             'manifest':manifest,
             'original_2019_gps':gpsproof,
             'original_2019_acc_classes':accproof,
             'original_bird_reference':referenceproof,
             'native_bird_tag_reference_anonymous':refqa}
        original_bins,binproof=original_2019_gps_acc_quarterhour_source(private)
        report['source_2019_25km_15min_ACC_GPS_bin_counts_before_RWS_or_solar']=binproof
        del acc,gps,indexed,private
        print('V127_SOURCE_GENUINE_2019_VLIELAND_GPS_ACC_HARD_REPLAY '+json.dumps({
            'source':report['v126_original_native_GPS_ACC_source_replay'],
            'true_15min_GPS_and_ACC_bins_month6to9':binproof,
            'new_2019_tide_sun_classified_behavior_Y_NOT_YET_OPENED':True},sort_keys=True),flush=True)
    except (SourceStop,ValueError,OSError,TimeoutError,UnicodeDecodeError,json.JSONDecodeError) as e:
        report['source_or_field_status']='SOURCE_STOP_ORIGINAL_VLIELAND_2019_GPS_ACC_PUBLISHER_REPLAY'
        report['source_stop_reason']=str(e)[:260]
        return output_report(report,output)

    try:
        transport_receipts={}
        def real_month_with_same_transport(month):
            (result,proof),prooftransport=original_RWS_transport_retry(month)
            transport_receipts[str(month)]=prooftransport
            return result,proof
        # All FOUR measured 2019 original monthly source heights are authenticated
        # before ANY original behaviour response score.
        RWS,RWSproof=fetch_all_2019_Vlieland_real_RWS_months(
             oldRWS,request_fn=real_month_with_same_transport)
        report['original_2019_full_RWS_measured_fourmonths']={
            **RWSproof,'source_transport_attempts_by_original_month':transport_receipts}
    except (SourceStop,ValueError,OSError,TimeoutError) as e:
        report['source_or_field_status']='SOURCE_STOP_GENUINE_RWS_2019_JUNE_SEPT_FULL_MEASURED_MONTHS'
        report['source_stop_reason']=str(e)[:260]
        return output_report(report,output)

    try:
        primary,source=source_real_tide_sun_fourway(original_bins,RWS)
        report['fourcell_original_2019_GPS_ACC_RWS_sun_BEFORE_Y']=source
        print('V127_SOURCE_2019_REAL_GPS_ACC_RWS_SOLAR_FOURCELL_BEFORE_OUTCOME '+json.dumps({
            'source_true_2019_4condition_bird_month_height':source['true_original_source_all_four_conditions'],
            'source_QA':source['source_2019_RWS_tide_sun_link_QA'],
            'native_GPS_astronomy_source_effort_by_month':source[
                  'source_UTC_daylight_night_twilight_effort_by_month'],
            'effect_not_yet_scored':True},sort_keys=True),flush=True)
        if not source['true_original_source_admitted_before_forage_share_Y']:
            report['source_or_field_status']='NOT_ESTIMATED_2019_ACC_FORAGE_TIDE_SUN_4CELL_SOURCE_GATE'
            return output_report(report,output)

        original=original_true_bird_BSTI_from_ACC_source(primary,source)
        report['genuine_2019_behaviour_classifier_forage_share_tide_solar']=original
        report['source_or_field_status']='ORIGINAL_2019_VLIELAND_ACC_CLASSIFIED_FORAGE_FOURWAY_REAL_RWS_SOLAR_EVALUATED'
        print('V127_REAL_2019_VLIELAND_TAGGED_BIRD_CLASSIFIED_FORAGE_SHARE '+json.dumps({
           'original_tagged_bird_n':original['original_independent_tagged_birds_N'],
           'original_source_4cell_group_n':original['original_complete_fourway_bird_month_height_groups'],
           'real_bird_equal_B_S_T_I':original['original_true_bird_B_S_T_I_results'],
           'behavior_is_ACC_classification_not_duration':True},sort_keys=True),flush=True)

        report['original_true_RWS_phase_ghosts']={}
        for shift in GHOST_DAYS:
            joined,gate=source_real_tide_sun_fourway(original_bins,RWS,ghost_shift_days=shift)
            outcome=original_true_bird_BSTI_from_ACC_source(joined,gate)
            report['original_true_RWS_phase_ghosts'][f'+{shift}days']={
                'original_RWS_measured_stage_shift_calendar_days':shift,
                'original_GPS_ACC_classified_response_and_solar_time_UNSHIFTED':True,
                'original_RWS_phase_shift_fourcell_gate':gate,
                'native_ACC_forage_share_effect_if_source_admitted':outcome}
            print('V127_ORIGINAL_2019_RWS_PHASE_GHOST_SOURCE '+json.dumps({
               'ghost_days':shift,
               'source_pass':gate['true_original_source_admitted_before_forage_share_Y'],
               'primary_I_if_source_pass':outcome.get('original_true_bird_B_S_T_I_results',{}).get(
                    'I_rising_vs_falling_by_night_vs_day',{}).get(
                       'true_original_individual_equal_weight_mean'),
               'effect_status':outcome['outcome_status']},sort_keys=True),flush=True)
        return output_report(report,output)
    except (SourceStop,ValueError,OSError,TimeoutError) as e:
        report['source_or_field_status']='STOP_ORIGINAL_2019_VLIELAND_TRUE_4CELL_SOURCE_OR_INFERENCE'
        report['source_stop_reason']=str(e)[:260]
        return output_report(report,output)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v126-original-2019-ACC-GPS-source',required=True)
    p.add_argument('--v126-original-2019-RWS-48h-pilot',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args();run(args.v126_original_2019_ACC_GPS_source,
        args.v126_original_2019_RWS_48h_pilot,args.output)
