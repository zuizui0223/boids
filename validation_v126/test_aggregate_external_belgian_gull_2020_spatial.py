"""v126 synthetic source-only adult panel aggregation controls.
The true report must be source-verified; synthetic fixtures are never field data.
"""
import json,tempfile,unittest
from pathlib import Path
import aggregate_external_belgian_gull_2020_spatial as a
from original_2020_belgium_gull_source import PANELS
def doc(panel,val=0.1,status=a.PASS):
    return {'analysis':a.ANALYSIS,
      'original_tracking_study':panel,
      '2020_original_Zenodo_publisher_record':PANELS[panel]['record'],
      '2020_original_publisher_GPS_source_MD5_frozen':PANELS[panel]['md5'],
      'source_and_ecology_status':status,
      'v125_authentic_2020_bird_source_replay':{
        'all_v125_real_2020_source_animal_counts_and_hour_steps_replayed_exactly':True},
      'original_native_JulOct_source_and_JulAug_frozen_steps':{
        'original_2020_JulAug_first_tag_hour_valid_source_step_count':1500},
      'original_genuine_2020_GIC_eight_source_gate':{
        'original_native_GIC_source_complete_fraction':1.0},
      'new_external_belgium_true_bird_spatial_result':{
        'original_2020_true_independent_birds_scored':5,
        'primary_per_bird_equal_month_equal_B_GIC_RF50_step_enrichment':val,
        'primary_10000_original_tagged_bird_bootstrap95':[val,val],
        'original_tagged_birds_with_positive_spatial_enrichment':5 if val>0 else 0,
        'primary_original_B_bootstrap_draws_anonymized_cohort_aggregate':[val]*10000,
        'secondary_solar_DAY_NIGHT_source_scored_with_own_missingness_gate':{
            'status':'NOT_ESTIMATED_SOLAR_DAY_NIGHT_SOURCE_GATE'}}}
class IndependentThreePanelsSourceConclusions(unittest.TestCase):
    def test_three_complete_original_studies_required(self):
        with self.assertRaisesRegex(ValueError,'REQUIRE_ALL_THREE'):
            a.merge([])
    def test_bird_group_bootstrap_contrast_without_new_pseudorep(self):
        with tempfile.TemporaryDirectory() as d:
            files=[]
            for panel in PANELS:
                z=doc(panel,0.2 if panel=='HG_OOSTENDE' else 0.0)
                p=Path(d)/(panel+'.json');p.write_text(json.dumps(z));files.append(p)
            result=a.merge(files)
        c=result['source_adult_HG_vs_LBBG_preselected_two_panel_comparison']
        self.assertAlmostEqual(c['2020_original_HG_OOSTENDE_minus_LBBG_ZEEBRUGGE_bird_equal_spatial_B_step'],0.2)
        self.assertEqual(c['nominal_unadjusted_2020_B_Spatial_H_vs_L_direction'],'POSITIVE')
        self.assertTrue(c['source_taxon_confounded_with_study_instrument_and_geographic_area'])
        self.assertTrue(result['NO_INDIRECT_LOCAL_TIDE_INFERENCE_TRUE_2020_DRY_HOURS_OR_FEEDING_LABELS'])
    def test_adult_source_missing_does_not_claim_positive(self):
        with tempfile.TemporaryDirectory() as d:
            files=[]
            for panel in PANELS:
                z=doc(panel)
                if panel=='HG_OOSTENDE':z['source_and_ecology_status']='SOURCE_STOP'
                p=Path(d)/(panel+'.json');p.write_text(json.dumps(z));files.append(p)
            result=a.merge(files)
        self.assertEqual(result['source_adult_HG_vs_LBBG_preselected_two_panel_comparison']['status'],
                         'NOT_ESTIMATED_BOTH_2020_ADULT_STUDIES_REQUIRED')
    def test_fake_publisher_MD5_identity_rejected_before_scoring(self):
        with tempfile.TemporaryDirectory() as d:
            files=[]
            for panel in PANELS:
                z=doc(panel)
                if panel=='LBBG_JUVENILE':z['2020_original_publisher_GPS_source_MD5_frozen']='wrong'
                p=Path(d)/(panel+'.json');p.write_text(json.dumps(z));files.append(p)
            with self.assertRaisesRegex(ValueError,'STUDY_ID_OR_FROZEN_MD5_CHANGED'):
                a.merge(files)
if __name__=='__main__':unittest.main()
