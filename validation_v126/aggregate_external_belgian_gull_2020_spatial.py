"""v126 independent Belgian original tagged-bird source cohorts aggregate.
No field tide; between-adult-study differences are descriptive and confounded.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from original_2020_belgium_gull_source import PANELS,FOCAL
ANALYSIS='V126_TRUE_EXTERNAL_2020_BELGIAN_GULL_2017_2019_GIC_EQUAL_REAL_STEP_RF50'
PASS='EXPLORATORY_AUTHENTIC_2020_BELGIUM_EIGHT_STEP_GIC_SPATIAL_SOURCE_ESTIMATED'
PANELS_REQUIRED=set(PANELS)

def merge(files):
    if len(files)!=len(PANELS):
        raise ValueError('STOP_V126_REQUIRE_ALL_THREE_PREDECLARED_INDEPENDENT_TRACKING_PROJECTS')
    rows={}
    for path in files:
        d=json.loads(Path(path).read_text())
        study=d.get('original_tracking_study')
        if (study not in PANELS or study in rows or d.get('analysis')!=ANALYSIS or
            d.get('2020_original_Zenodo_publisher_record')!=PANELS[study]['record'] or
            d.get('2020_original_publisher_GPS_source_MD5_frozen')!=PANELS[study]['md5']):
            raise ValueError('STOP_V126_ORIGINAL_STUDY_ID_OR_FROZEN_MD5_CHANGED')
        score=d.get('new_external_belgium_true_bird_spatial_result') or {}
        rec={'source_study':study,'source_status':d.get('source_and_ecology_status'),
             'native_2020_Zenodo_full_original_year_replay':(
              d.get('v125_authentic_2020_bird_source_replay') or {}).get(
               'all_v125_real_2020_source_animal_counts_and_hour_steps_replayed_exactly',False),
             'native_2020_JulAug_original_true_GPS_moves':(
               d.get('original_native_JulOct_source_and_JulAug_frozen_steps') or {}).get(
                'original_2020_JulAug_first_tag_hour_valid_source_step_count'),
             'original_GIC_2017_2019_all8_pixel_source_fraction':(
               d.get('original_genuine_2020_GIC_eight_source_gate') or {}).get(
                'original_native_GIC_source_complete_fraction'),
             'original_true_birds_scored':score.get('original_2020_true_independent_birds_scored'),
             'year_2020_JulAug_original_bird_equal_B_step':score.get(
                'primary_per_bird_equal_month_equal_B_GIC_RF50_step_enrichment'),
             'original_true_independent_bird_bootstrap95':score.get(
                'primary_10000_original_tagged_bird_bootstrap95'),
             'n_original_birds_with_positive_B_step':score.get(
                'original_tagged_birds_with_positive_spatial_enrichment'),
             'original_solar_ONLY_secondary':score.get(
                'secondary_solar_DAY_NIGHT_source_scored_with_own_missingness_gate'),
             'source_no_local_belgium_tide_RWS_or_real_flat_activity':True}
        if d.get('source_and_ecology_status')==PASS:
            if (not rec['native_2020_Zenodo_full_original_year_replay'] or
                len(score.get('primary_original_B_bootstrap_draws_anonymized_cohort_aggregate') or [])!=10000 or
                rec['original_true_birds_scored']<5):
                raise ValueError('STOP_V126_PUBLIC_ORIGINAL_TRUE_BIRD_BOOTSTRAP_IS_NOT_AUTHENTIC')
            rec['bootstrap']=score['primary_original_B_bootstrap_draws_anonymized_cohort_aggregate']
        rows[study]=rec
    if set(rows)!=PANELS_REQUIRED:
        raise ValueError('STOP_V126_SOMETHING_MISSING_OR_DUPLICATED')
    H=rows['HG_OOSTENDE'];L=rows['LBBG_ZEEBRUGGE'];J=rows['LBBG_JUVENILE']
    adult_comparison={'status':'NOT_ESTIMATED_BOTH_2020_ADULT_STUDIES_REQUIRED',
                      'not_randomized_independent_coast_or_tracking_protocol':True}
    if H['source_status']==PASS and L['source_status']==PASS:
        diff=np.asarray(H.pop('bootstrap'))-np.asarray(L.pop('bootstrap'))
        observation=H['year_2020_JulAug_original_bird_equal_B_step']-(
            L['year_2020_JulAug_original_bird_equal_B_step'])
        adult_comparison={
            'status':'EXPLORATORY_ORIGINAL_2020_TWO_INDEPENDENT_ADULT_STUDIES_SOURCE_COMPLETE',
            '2020_original_HG_OOSTENDE_minus_LBBG_ZEEBRUGGE_bird_equal_spatial_B_step':float(observation),
            'independent_genuine_tagged_bird_group_bootstrap_10000_CI95':
                np.quantile(diff,[.025,.975]).tolist(),
            'nominal_unadjusted_2020_B_Spatial_H_vs_L_direction':(
                'POSITIVE' if np.quantile(diff,.025)>0 else
                'NEGATIVE' if np.quantile(diff,.975)<0 else 'NOT_ESTABLISHED'),
            'same_2020_original_year_JulyAugust_but_different_colony_and_GPS_study':True,
            'source_taxon_confounded_with_study_instrument_and_geographic_area':True,
            'NOT_2020_TIDE_SUN_OR_TIDAL_FLAT_FORAGING_CAUSAL_EVIDENCE':True}
    # Remove bootstrap draw arrays from public display except aggregate results.
    for row in rows.values():row.pop('bootstrap',None)
    return {'analysis':'V126_TRUE_INDEPENDENT_2020_BELGIUM_GULLS_EXTERNAL_GIC_SPATIAL_COHORT_AUDIT',
       'source_studies_all_three_original':rows,
       'source_adult_HG_vs_LBBG_preselected_two_panel_comparison':adult_comparison,
       'source_juvenile_L_fuscus_age_control_independently_of_adults':{
          'status':J['source_status'],'n_real_birds':J['original_true_birds_scored'],
          'original_2020_juvenile_spatial_B':J['year_2020_JulAug_original_bird_equal_B_step'],
          'original_bird_bootstrap95':J['original_true_independent_bird_bootstrap95']},
       'source_original_neeltje_2020_old_B_tide_balanced_same_length_rotated':0.0428166,
       'WARNING_OLD_NEW_DIFFERENT_CALENDAR_AND_TIDE_CONDITIONING':True,
       'NO_INDIRECT_LOCAL_TIDE_INFERENCE_TRUE_2020_DRY_HOURS_OR_FEEDING_LABELS':True,
       'NO_ORIGINAL_TAG_ID_GPS_TIME_OR_POSITION':True}

def run(source,out):
    files=list(Path(source).rglob('v126-original-2020-Belgium-*-GIC-same-real-step.json'))
    doc=merge(files)
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(doc,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V126_BELGIUM_THREE_PROJECTS_EXTERNAL_GIC_SPATIAL_VALIDATION '+json.dumps({
      'adult_study_contrast':doc['source_adult_HG_vs_LBBG_preselected_two_panel_comparison'],
      'per_original_study':doc['source_studies_all_three_original'],
      'juvenile':doc['source_juvenile_L_fuscus_age_control_independently_of_adults'],
      'NOT_LOCAL_TIDE_OR_BIOLOGICAL_TIME_NICHE':True
    },sort_keys=True),flush=True)
    return doc
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True)
    p.add_argument('--output',required=True);x=p.parse_args();run(x.source,x.output)
