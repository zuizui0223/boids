"""v129 genuine historical 2018 Vlieland ACC forage-share × original RWS tide × true sun.

Freeze: docs/V129_FROZEN_VLIELAND_2018_2019_HISTORICAL_ACC_SOLAR_TIDE_TRANSFER.md.
2018 was selected AFTER observing 2019 results. SAME cohort overlaps by tag.
Source audit replays original v128 before any tidal/solar response score. No
tag, real animal coordinates, original ACC timestamps, or raw tide exported.
"""
from __future__ import annotations
import argparse
import json
from datetime import timezone
from pathlib import Path

from original_2019_Vlieland_behaviour_source import _reference_anonymous_identity, SourceStop
from original_Vlieland_2018_ACC_GPS_year_source import (
    immutable_original_manifest, original_bytes, original_GPS_bird_year,
    original_2018_ACC_GPS_source_feasibility, ORIGINAL_REFERENCE,
    ORIGINAL_2018_GPS, ORIGINAL_2019_GPS, ORIGINAL_2018_ACC)
from real_2018_vlieland_RWS_measured import (
    original_2018_vlieland_fourmonth_measured_tide, NativeSourceStop)
from vlieland_acc_forage_tide_sun_fourway import (
    source_real_tide_sun_fourway, original_true_bird_BSTI_from_ACC_source,
    BASIS, GHOST_DAYS, RNG_SEED)

PRIOR_V128_RUN=43463270204
PRIOR_V127_RUN=43461048062
FROZEN_SPEC='docs/V129_FROZEN_VLIELAND_2018_2019_HISTORICAL_ACC_SOLAR_TIDE_TRANSFER.md'
EXPECTED={
    'GPS_2018_rows':1787112,'GPS_2018_birds':72,
    'GPS_2019_rows':1193728,'GPS_2019_birds':42,'overlap':42,
    'ACC_2018_rows':2675982,'ACC_2018_birds':73,
    'ACC_GPS_25km_events':643510,'ACC_GPS_25km_quarterhours':243403,
    'ACC_both_100_two_month_birds':34,
    'ACC_GPS_25km_any_birds':35
}
ORIGINAL_2019_S=-0.1138426
ORIGINAL_2019_I=-0.0459232

def source_only_replay(previous,gps18,gps19,acc,overlap,receipts):
    """Frozen v128 *exact* source replay before true 2018 behavior score."""
    if (previous.get('analysis')!='V128_ORIGINAL_VLIELAND_2018_INDEPENDENT_CALENDAR_YEAR_ACC_GPS_SOURCE_GATE'
        or previous.get('source_status')!='TRUE_PUBLISHER_2018_VLIELAND_GPS_ACC_BIN_FEASIBILITY_ADMITTED'):
        raise SourceStop('STOP_V129_PRIOR_ORIGINAL_V128_NOT_ADMITTED')
    prior18=previous['source_original_2018_GPS_true_source_QA']
    prior19=previous['source_original_2019_GPS_unchanged_source_replay_for_bird_overlap']
    prioracc=previous['original_2018_samebird_ACC_class_and_GPS_25km_source_QA']
    prioroverlap=previous['source_anonymous_true_2018_vs_2019_GPS_individual_overlap']
    k18=('genuine_original_GPS_rows','original_annual_independent_genuine_birds_with_GPS','native_real_GPS_birds_per_month','original_source_rejected_GPS_QA')
    kacc=('original_2018_ACC_full_year_raw_rows',
          'original_2018_classification_original_native_label_counts',
          'original_2018_original_annual_birds_with_identity_for_ACC',
          'source_original_2018_bird_quarterhour_binary_classes_25km_n',
          'source_original_genuine_birds_ge100_EACH_class_two_2018_months',
          'source_original_genuine_birds_with_any_binary_25km_source',
          'source_original_2018_25km_monthly_true_bird_binary_classes',
          'source_original_2018_alternate_radius_binary_class_event_n',
          'source_2018_original_gps_acc_15min_classified_source_QA',
          'source_frozen_YEAR2018_bird_ge8_15minute_bins_ge1000_eligible')
    if (any(gps18.get(k)!=prior18.get(k) or gps19.get(k)!=prior19.get(k) for k in k18)
        or any(acc.get(k)!=prioracc.get(k) for k in kacc)
        or overlap!=prioroverlap):
        raise SourceStop('STOP_V129_ORIGINAL_2018_2019_SOURCE_COUNTS_OR_BIRD_OVERLAP_DRIFT')
    expected_numbers=[
       (gps18['genuine_original_GPS_rows'],EXPECTED['GPS_2018_rows']),
       (gps18['original_annual_independent_genuine_birds_with_GPS'],EXPECTED['GPS_2018_birds']),
       (gps19['genuine_original_GPS_rows'],EXPECTED['GPS_2019_rows']),
       (gps19['original_annual_independent_genuine_birds_with_GPS'],EXPECTED['GPS_2019_birds']),
       (overlap['same_true_tagged_birds_recorded_in_BOTH_2018_and2019_GPS_years'],EXPECTED['overlap']),
       (acc['original_2018_ACC_full_year_raw_rows'],EXPECTED['ACC_2018_rows']),
       (acc['original_2018_original_annual_birds_with_identity_for_ACC'],EXPECTED['ACC_2018_birds']),
       (acc['source_original_2018_bird_quarterhour_binary_classes_25km_n'],EXPECTED['ACC_GPS_25km_quarterhours']),
       (acc['source_original_genuine_birds_ge100_EACH_class_two_2018_months'],EXPECTED['ACC_both_100_two_month_birds']),
       (acc['source_original_genuine_birds_with_any_binary_25km_source'],EXPECTED['ACC_GPS_25km_any_birds']),
       (acc['source_original_2018_alternate_radius_binary_class_event_n']['25.0'],EXPECTED['ACC_GPS_25km_events'])
    ]
    if any(a!=b for a,b in expected_numbers) or not acc['source_frozen_YEAR2018_bird_ge8_15minute_bins_ge1000_eligible']:
        raise SourceStop('STOP_V129_PRIOR_NATIVE_SOURCE_FROZEN_COUNTS_FAILED')
    for newkey,oldkey in (
        (ORIGINAL_REFERENCE,'original_reference_source_MD5_proof'),
        (ORIGINAL_2018_GPS,'source_original_2018_publisher_GPS_receipt'),
        (ORIGINAL_2019_GPS,'source_original_2019_GPS_MD5_receipt'),
        (ORIGINAL_2018_ACC,'original_2018_ACC_publisher_full_MD5_receipt')):
        if receipts[newkey]['source_SHA256_for_original_content']!=previous[oldkey]['source_SHA256_for_original_content']:
            raise SourceStop('STOP_V129_ORIGINAL_PUBLISHER_BYTES_DRIFT_'+newkey)
    return {'original_2018_v128_run':PRIOR_V128_RUN,
      'source_replay_status':'EXACT_2018_GPS_ACC_2019_OVERLAP_AND_NATIVE_SHA_REPLAYED',
      'frozen_original_source_counts':EXPECTED,
      'source_ge100_EACH_binary_class_two_months_2018_birds':34,
      'true_tagged_bird_overlap_2018_2019':42,
      'calendar_year_is_NOT_an_independent_animal_replication':True,
      'NO_private_tag_or_GPS_time_exported':True}

def bins_2018_exact_v127_schema(private,source):
    """Translate only names/year to the EXACT UNCHANGED v127 numerical estimator."""
    out=[]
    for (bird,binutc),r in private.items():
        if (binutc.year!=2018 or binutc.month not in (6,7,8,9)
            or r['native_UTC_15min_bin']!=binutc or r['private_bird']!=bird):
            raise SourceStop('STOP_V129_PRIVATE_2018_BIRD_UTC_SOURCE_MISMATCH')
        event=r['earliest_true_classification_UTC']
        if not (0<=(event-binutc).total_seconds()<900):
            raise SourceStop('STOP_V129_EARLIEST_GPS_ACC_EVENT_NOT_IN_15MIN_WINDOW')
        lat=float(r['original_same_bird_GPS_latitude'])
        lon=float(r['original_same_bird_GPS_longitude'])
        if not (-90<=lat<=90 and -180<=lon<=180):
            raise SourceStop('STOP_V129_PRIVATE_GPS_LOCATION_INVALID')
        n_f=r['n_native_forage_classifier_events']
        n_i=r['n_native_inactive_classifier_events']
        if not (isinstance(n_f,int) and isinstance(n_i,int)
                and n_f>=0 and n_i>=0 and n_f+n_i>0):
            raise SourceStop('STOP_V129_NATIVE_LITERAL_ACC_BINARY_LABEL_INVALID')
        out.append({'private_bird':bird,'source_month':binutc.month,
          'source_utc_event':event.replace(tzinfo=timezone.utc),
          'source_lat':lat,'source_lon':lon,
          'original_acc_forage_events':n_f,'original_acc_inactive_events':n_i})
    if len(out)!=source['source_original_2018_bird_quarterhour_binary_classes_25km_n']:
        raise SourceStop('STOP_V129_V128_ORIGINAL_2018_QUARTERHOUR_SOURCE_N_DRIFT')
    return out,{'original_2018_true_bird_ACC_GPS_15min_bins':len(out),
        'original_2018_25km_original_forage_events':sum(x['original_acc_forage_events'] for x in out),
        'original_2018_25km_original_inactive_events':sum(x['original_acc_inactive_events'] for x in out),
        'same_real_GPS_nearest_ACC_15min_and_literal_class_as_v128':True,
        'v127_original_B_S_T_I_numerical_estimator_UNCHANGED':True,
        'GPS_exact_UTC_or_animal_identity_NOT_exported':True}

def anonymous_gate(src):
    q=src['true_original_source_all_four_conditions']
    return {'2018_source_complete_fourcells_admitted_before_Y':src[
       'true_original_source_admitted_before_forage_share_Y'],
       '2018_true_tagged_birds':q['true_original_unique_birds_in_complete_fourcell_source'],
       '2018_true_bird_month_stage_fourcells':q['true_original_bird_month_0p25m_RWS_height_fourcell_groups'],
       '2018_original_quarterhour_bins_used':q['true_original_15minute_bins_in_complete_fourcell_source'],
       '2018_supported_months':q['true_original_supported_2019_months'],
       '2018_original_source_counts_by_month':src['source_2019_months_fourcell_support'],
       '2018_raw_original_RWS_solar_time_join_QA':src['source_2019_RWS_tide_sun_link_QA'],
       '2018_original_solar_sampling_effort':src['source_UTC_daylight_night_twilight_effort_by_month'],
       'GPS_RWS_sun_source_only_before_behavior_Y':True}

def anonymous_effect(raw):
    """Do not write v127 2019-named keys/status for genuine 2018 effects."""
    if raw.get('outcome_status','').startswith('NOT_ESTIMATED'):
        return {'2018_status':'NOT_ESTIMATED_SOURCE_GATE'}
    return {'2018_status':'OBSERVED_2018_ACC_CLASSIFIED_FORAGE_SHARE_EVALUATED',
       'source_year':2018,
       'original_real_tagged_bird_n':raw['original_independent_tagged_birds_N'],
       '2018_original_complete_bird_month_stage_fourcells':raw[
           'original_complete_fourway_bird_month_height_groups'],
       'same_v127_unchanged_B_S_T_I_true_bird_bootstrap':raw['original_true_bird_B_S_T_I_results'],
       'source_original_ACC_classifier_binary_classes_NOT_foraging_minutes':True,
       'whole_bird_bootstrap_within_year_ONLY':True}

def write(report,out):
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    real=report.get('2018_original_true_RWS_ACC_SUN_main_effect') or {}
    print('V129_GENUINE_2018_VLIELAND_ACC_FORAGE_RWS_SUN_HISTORICAL_YEAR '+json.dumps({
      'status':report['source_and_field_status'],
      'original_2018_fourcell_source':report.get('2018_original_true_RWS_SUN_fourcell_source_gate'),
      'original_2018_observed_S':real.get('same_v127_unchanged_B_S_T_I_true_bird_bootstrap',{}).get(BASIS[1]),
      'original_2018_observed_I':real.get('same_v127_unchanged_B_S_T_I_true_bird_bootstrap',{}).get(BASIS[3]),
      'wrong_tide_stage_ghost_diagnostic':report.get('2018_wrong_RWS_calendar_day_ghost_comparison'),
      'source_stop':report.get('source_stop_reason'),
      'independent_birds_across_2018_2019':False,
      'ACC_label_is_not_direct_feeding_or_internal_clock':True},sort_keys=True),flush=True)
    return report

def run(previous_v128_json,out):
    report={'analysis':'V129_ORIGINAL_VLIELAND_2018_HISTORICAL_YEAR_ACC_FORAGE_RWS_SOLAR_TRANSFER',
      'source_and_field_status':'SOURCE_PENDING',
      'preoutcome_frozen_spec':FROZEN_SPEC,
      'historical_2018_year_selected_after_2019_findings':True,
      'independent_cross_year_birds':False,
      'original_v127_2019_success_run':PRIOR_V127_RUN,
      '2019_reference_solely_prior_published_same_site_S':ORIGINAL_2019_S,
      '2019_reference_solely_prior_published_same_site_I':ORIGINAL_2019_I,
      '2018_foraging_event_share_not_consumption_minutes_or_internal_clock':True,
      'original_animal_tags_GPS_and_original_times_not_exported':True}
    try:
        previous=json.loads(Path(previous_v128_json).read_text())
        files,manifest=immutable_original_manifest()
        refraw,pref=original_bytes(files[ORIGINAL_REFERENCE])
        identities,refqa=_reference_anonymous_identity(refraw)
        gpsraw18,p18=original_bytes(files[ORIGINAL_2018_GPS])
        indexed,b18,gps18=original_GPS_bird_year(gpsraw18,2018,identities,True)
        del gpsraw18
        gpsraw19,p19=original_bytes(files[ORIGINAL_2019_GPS])
        _,b19,gps19=original_GPS_bird_year(gpsraw19,2019,identities,False)
        del gpsraw19
        overlap={'original_2018_genuine_GPS_birds':len(b18),
          'original_2019_genuine_GPS_birds':len(b19),
          'same_true_tagged_birds_recorded_in_BOTH_2018_and2019_GPS_years':len(b18&b19),
          'original_2018_only_tagged_birds':len(b18-b19),
          'original_2019_only_tagged_birds':len(b19-b18),
          'source_new_2018_year_not_independent_2019_bird_replicates':len(b18&b19)>0}
        rawacc,pacc=original_bytes(files[ORIGINAL_2018_ACC])
        acc,qualified,private=original_2018_ACC_GPS_source_feasibility(
             rawacc,identities,indexed,return_private_quarterhour_bins=True)
        del rawacc,indexed,identities
        report['2018_2019_native_original_first_party_source_replay']=source_only_replay(
            previous,gps18,gps19,acc,overlap,{
             ORIGINAL_REFERENCE:pref,ORIGINAL_2018_GPS:p18,
             ORIGINAL_2019_GPS:p19,ORIGINAL_2018_ACC:pacc})
        if len(qualified)<8 or not acc['source_frozen_YEAR2018_bird_ge8_15minute_bins_ge1000_eligible']:
            report['source_and_field_status']='NOT_ESTIMATED_2018_ORIGINAL_ACC_GPS_SOURCE_GATE'
            return write(report,out)
        bins,proof=bins_2018_exact_v127_schema(private,acc)
        report['2018_original_15min_source_2019_v127_numeric_schema']=proof
        del private
        print('V129_SOURCE_FIRST_NATIVE_2018_REPLAY_PASS '+json.dumps({
            'v128_source_replay':report['2018_2019_native_original_first_party_source_replay'],
            '15min_bins':proof,
            'real_original_2018_RWS_solar_ACC_field_Y_NOT_ESTIMATED_YET':True},
            sort_keys=True),flush=True)
    except (SourceStop,NativeSourceStop,ValueError,TypeError,KeyError,OSError,
            TimeoutError,UnicodeDecodeError,json.JSONDecodeError) as e:
        report['source_and_field_status']='SOURCE_STOP_2018_ORIGINAL_ACC_GPS_REPLAY'
        report['source_stop_reason']=str(e)[:260]
        return write(report,out)
    try:
        RWS,proof=original_2018_vlieland_fourmonth_measured_tide()
        report['2018_original_4_month_10min_measured_RWS_harbour_tide']=proof
    except (SourceStop,NativeSourceStop,ValueError,TypeError,KeyError,OSError,
            TimeoutError,json.JSONDecodeError) as e:
        report['source_and_field_status']='SOURCE_STOP_2018_ORIGINAL_RWS_4_MONTH_TIDE'
        report['source_stop_reason']=str(e)[:260]
        return write(report,out)
    try:
        cells,gate=source_real_tide_sun_fourway(bins,RWS,ghost_shift_days=0)
        report['2018_original_true_RWS_SUN_fourcell_source_gate']=anonymous_gate(gate)
        print('V129_2018_ORIGINAL_TRUE_RWS_SUN_4CELL_BEFORE_Y '+json.dumps(
            report['2018_original_true_RWS_SUN_fourcell_source_gate'],sort_keys=True),flush=True)
        if not gate['true_original_source_admitted_before_forage_share_Y']:
            report['source_and_field_status']='NOT_ESTIMATED_2018_ORIGINAL_RWS_SUN_4CELL_SOURCE_GATE'
            return write(report,out)
        real=anonymous_effect(original_true_bird_BSTI_from_ACC_source(cells,gate,seed=RNG_SEED))
        report['2018_original_true_RWS_ACC_SUN_main_effect']=real
        report['source_and_field_status']='2018_GENUINE_OBSERVED_SAME_TAXON_SITE_HISTORICAL_YEAR_S_T_I_ESTIMATED'
        report['2018_original_ghosts']={}
        I=real['same_v127_unchanged_B_S_T_I_true_bird_bootstrap'][BASIS[3]][
             'true_original_individual_equal_weight_mean']
        bigger=[]
        for days in GHOST_DAYS:
            gc,gs=source_real_tide_sun_fourway(bins,RWS,ghost_shift_days=days)
            gsrc=anonymous_gate(gs)
            gr=anonymous_effect(original_true_bird_BSTI_from_ACC_source(gc,gs,seed=RNG_SEED))
            if gsrc['2018_source_complete_fourcells_admitted_before_Y']:
                gi=gr['same_v127_unchanged_B_S_T_I_true_bird_bootstrap'][BASIS[3]][
                   'true_original_individual_equal_weight_mean']
                if abs(gi)>=abs(I):bigger.append(days)
            report['2018_original_ghosts'][f'+{days}days']={
                'original_2018_wrong_real_RWS_calendar_day_shift':days,
                'original_real_ACC_solar_behavior_clock_UNSHIFTED':True,
                'source_fourcell':gsrc,'effect':gr}
            print('V129_2018_WRONG_TIDE_GHOST '+json.dumps({
                'days':days,'source_admitted':gsrc['2018_source_complete_fourcells_admitted_before_Y'],
                'I_if_admitted':gr.get('same_v127_unchanged_B_S_T_I_true_bird_bootstrap',{}).get(BASIS[3]),
                'note_ghosts_change_source_grouping_not_formal_p_value':True},sort_keys=True),flush=True)
        report['2018_wrong_RWS_calendar_day_ghost_comparison']={
            'real_2018_observed_tide_by_sun_I':I,
            'admitted_wrong_calendar_day_shifts_with_equal_or_larger_abs_I':bigger,
            'unique_measured_tide_phase_effect_supported_by_this_ghost_diagnostic':not bool(bigger),
            'this_is_a_diagnostic_not_a_formal_tide_phase_specificity_test':True}
        return write(report,out)
    except (SourceStop,NativeSourceStop,ValueError,TypeError,KeyError,OSError,
            TimeoutError) as e:
        report['source_and_field_status']='STOP_ORIGINAL_2018_RWS_SUN_4CELL_OR_SCORE'
        report['source_stop_reason']=str(e)[:260]
        return write(report,out)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v128-original-2018-source',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    run(args.v128_original_2018_source,args.output)
