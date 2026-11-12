"""v125 cross-panel source-only summary; no habitat Y or tidal effect.
Each original 2020 publisher accession is fixed and independently audited.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from original_2020_belgium_gull_source import PANELS,FOCAL
SOURCE_ANALYSIS='V125_ORIGINAL_2020_BELGIUM_THREE_PANELS_INDEPENDENT_GULL_GPS_SOURCE_ONLY'
SUCCESS='ORIGINAL_2020_BELGIAN_GULL_ANNUAL_BIRD_SOURCE_AUTHENTICATED'

def aggregate(files):
    if len(files)!=len(PANELS):
        raise ValueError('STOP_V125_REQUIRED_3_PUBLIC_GULL_STUDIES_NOT_PRESENT')
    checked={}
    for path in files:
        item=json.loads(Path(path).read_text())
        study=item.get('panel')
        if (study not in PANELS or study in checked or
            item.get('analysis')!=SOURCE_ANALYSIS or
            item.get('original_archive_record_id')!=PANELS[study]['record'] or
            item.get('source_2020_GPS_publisher_md5_frozen')!=PANELS[study]['md5']):
            raise ValueError('STOP_V125_SOURCE_PANEL_STUDY_OR_YEAR_IDENTITY_CHANGED')
        if item.get('source_status')==SUCCESS:
            doc=item.get('native_source_2020_birds_hour_and_movement_QA') or {}
            raw=doc.get('source_2020_by_actual_original_taxon') or {}
            tax={}
            for s in FOCAL:
                d=raw.get(s) or {}
                tax[s]={
                    'real_2020_ge20_hourly_gps_birds':d.get('true_2020_original_birds_with_ge20_coastal_hours'),
                    'real_2020_original_coastal_hour_observations':d.get('native_original_2020_JulOct_coastal_bird_hours_in_eligible_tags'),
                    'month_support':d.get('source_months_meeting_3_birds_150_hours'),
                    'true_2020_source_cohort_gate':bool(d.get('fixed_bird_hour_source_admitted')),
                    'original_gps_step_source_gate':bool(d.get('fixed_step_source_gate_admitted'))}
            checked[study]={'study_status':'AUTHENTIC_ORIGINAL_2020_GPS_MD5_AND_NATIVE_SOURCE',
                            'native_GPS_original_2020_calendar_JulOct_rows':
                               doc.get('original_native_2020_JulyOctober_rows'),
                            'true_focal_species_annual_bird_source':tax,
                            'both_original_study_taxa_source_admitted':
                               bool(doc.get('source_both_focal_species_admitted_IN_THIS_ONE_STUDY'))}
        else:
            checked[study]={'study_status':'PUBLISHER_SOURCE_NOT_ADMITTED',
                'original_source_blocker':item.get('source_failure'),
                'NO_ANIMAL_OUTCOME_IS_ZERO_FROM_THIS_FAILURE':True}
    if set(checked)!=set(PANELS):
        raise ValueError('STOP_V125_MISSING_OR_DUPLICATED_ORIGINAL_SOURCE')
    juvenile=checked['LBBG_JUVENILE']
    a=checked['HG_OOSTENDE']
    b=checked['LBBG_ZEEBRUGGE']
    juvenile_both=juvenile.get('both_original_study_taxa_source_admitted',False)
    adult_between=(a.get('true_focal_species_annual_bird_source',{}).get('Larus argentatus',{})
                   .get('true_2020_source_cohort_gate',False) and
                   b.get('true_focal_species_annual_bird_source',{}).get('Larus fuscus',{})
                   .get('true_2020_source_cohort_gate',False))
    return {'analysis':'V125_BELGIAN_2020_SOURCE_ONLY_3_FIXED_EXTERNAL_STUDY_COHORTS',
        'source_panel_n':3,
        'original_2020_juvenile_TWO_TAXA_same_tracking_project_admitted':bool(juvenile_both),
        'original_2020_ADULT_2_different_studies_one_taxon_each_admitted':bool(adult_between),
        'priority_next_scientific_source_strategy':(
          'JUVENILE_2TAXA_WITHIN_ONE_STUDY_SOURCE' if juvenile_both else
          'ADULT_TWO_PROJECTS_CONFUNDED_BY_COLONY_AND_TRACKING_METHOD' if adult_between else
          'NO_TWO_TAXON_SOURCE_ADMITTED_IN_2020_BELGIAN_PANEL'),
        'separate_2020_original_source_panels':checked,
        'new_2020_GIC_habitat_tide_solar_behavior_Y':'NOT_ESTIMATED_SOURCE_FEASIBILITY_ONLY',
        'source_juveniles_vs_adults_NOT_RANDOMIZED_OR_TAXON_POPULATION_TRANSFER':True,
        'source_2020_Belgian_coast_not_independent_ocean_basin_from_Zeeland':True,
        'NO_PRIVATE_BIRD_ID_GPS_LOCATION_OR_TIMESTAMP':True}
def run(source,out):
    files=list(Path(source).rglob('v125-2020-original-Belgian-*-GPS-source-only.json'))
    a=aggregate(files)
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(a,indent=2,sort_keys=True)+'\n')
    print('V125_AUTHENTIC_BELGIAN_2020_THREE_TRACKING_PROJECTS_SOURCE_GATE '+json.dumps({
      'status':a['priority_next_scientific_source_strategy'],
      'juveniles_both_taxa':a['original_2020_juvenile_TWO_TAXA_same_tracking_project_admitted'],
      'adults_from_two_studies':a['original_2020_ADULT_2_different_studies_one_taxon_each_admitted'],
      'per_study':a['separate_2020_original_source_panels'],
      'NO_BIOLOGICAL_EFFECT':True},sort_keys=True),flush=True)
    return a
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True)
    p.add_argument('--output',required=True);x=p.parse_args();run(x.source,x.output)
