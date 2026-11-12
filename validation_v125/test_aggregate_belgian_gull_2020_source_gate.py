"""v125 three independent study source aggregation tests (synthetic receipts)."""
from pathlib import Path
import tempfile,json,unittest
import aggregate_belgian_gull_2020_source_gate as a
import original_2020_belgium_gull_source as m

def record(panel,status='ORIGINAL_2020_BELGIAN_GULL_ANNUAL_BIRD_SOURCE_AUTHENTICATED'):
    tax={
      s:{'true_2020_original_birds_with_ge20_coastal_hours':5,
         'native_original_2020_JulOct_coastal_bird_hours_in_eligible_tags':1200,
         'source_months_meeting_3_birds_150_hours':[7,8],
         'fixed_bird_hour_source_admitted':True,
         'fixed_step_source_gate_admitted':True}
      for s in m.FOCAL}
    return {'analysis':a.SOURCE_ANALYSIS,'panel':panel,
      'original_archive_record_id':m.PANELS[panel]['record'],
      'source_2020_GPS_publisher_md5_frozen':m.PANELS[panel]['md5'],
      'source_status':status,
      'native_source_2020_birds_hour_and_movement_QA':{
        'original_native_2020_JulyOctober_rows':30000,
        'source_2020_by_actual_original_taxon':tax,
        'source_both_focal_species_admitted_IN_THIS_ONE_STUDY':True}}
class ThreeOriginalStudiesSourceAudit(unittest.TestCase):
    def test_three_source_panels_are_required_before_any_ecological_guess(self):
        with self.assertRaisesRegex(ValueError,'REQUIRED_3'):
            a.aggregate([])
    def test_complete_authentic_studies_source_only_not_new_biological_effect(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for p in m.PANELS:
                f=Path(d)/(p+'.json');f.write_text(json.dumps(record(p)));paths.append(f)
            r=a.aggregate(paths)
        self.assertEqual(r['source_panel_n'],3)
        self.assertTrue(r['original_2020_juvenile_TWO_TAXA_same_tracking_project_admitted'])
        self.assertEqual(r['new_2020_GIC_habitat_tide_solar_behavior_Y'],
                         'NOT_ESTIMATED_SOURCE_FEASIBILITY_ONLY')
    def test_juvenile_source_missing_both_taxa_does_not_forge_annual_gulls(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for p in m.PANELS:
                v=record(p)
                if p=='LBBG_JUVENILE':
                    v['native_source_2020_birds_hour_and_movement_QA'][
                       'source_both_focal_species_admitted_IN_THIS_ONE_STUDY']=False
                f=Path(d)/(p+'.json');f.write_text(json.dumps(v));paths.append(f)
            r=a.aggregate(paths)
        self.assertFalse(r['original_2020_juvenile_TWO_TAXA_same_tracking_project_admitted'])
        self.assertTrue(r['original_2020_ADULT_2_different_studies_one_taxon_each_admitted'])
        self.assertEqual(r['priority_next_scientific_source_strategy'],
            'ADULT_TWO_PROJECTS_CONFUNDED_BY_COLONY_AND_TRACKING_METHOD')
    def test_duplicate_native_source_receipt_not_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for i,p in enumerate(('LBBG_JUVENILE','HG_OOSTENDE','LBBG_ZEEBRUGGE')):
                v=record(p)
                if i==2:v['panel']='HG_OOSTENDE'
                f=Path(d)/(p+'.json');f.write_text(json.dumps(v));paths.append(f)
            with self.assertRaisesRegex(ValueError,'STUDY_OR_YEAR_IDENTITY'):
                a.aggregate(paths)
if __name__=='__main__':unittest.main()
