"""v126 synthetic known-truth tests, not real ecological field observations."""
import unittest,json
from datetime import datetime,timedelta
import external_belgian_gull_step_statistics as m
from original_2020_belgium_gull_source import PANELS,FOCAL

def prior(panel):
    species=FOCAL[0] if panel=='HG_OOSTENDE' else FOCAL[1]
    source={
      s:{'true_2020_original_birds_with_ge20_coastal_hours':5 if s==species else 0,
         'native_original_2020_JulOct_coastal_bird_hours_in_eligible_tags':2000 if s==species else 0,
         'source_original_consecutive_bird_hour_steps_0p75_to_1p5_h_in_40km':1900 if s==species else 0}
      for s in FOCAL}
    return {
     'analysis':'V125_ORIGINAL_2020_BELGIUM_THREE_PANELS_INDEPENDENT_GULL_GPS_SOURCE_ONLY',
     'panel':panel,
     'original_archive_record_id':PANELS[panel]['record'],
     'source_2020_GPS_publisher_md5_frozen':PANELS[panel]['md5'],
     'source_status':'ORIGINAL_2020_BELGIAN_GULL_ANNUAL_BIRD_SOURCE_AUTHENTICATED',
     'native_source_2020_birds_hour_and_movement_QA':{
        'original_native_2020_JulyOctober_rows':2500,
        'source_2020_by_actual_original_taxon':source}}
def faux_event(taxon,bird,month,valid=True):
    return {'taxon':taxon,'bird':bird,'month':month,
      'original_UTC':datetime(2020,month,1,12,tzinfo=__import__('datetime').timezone.utc),
      'GPS_departure_lat':51.341,'GPS_departure_lon':3.182,
      'v115_real_2020_GPS_destination_native_GIC_RF':80. if valid else None,
      'v115_7_original_same_step_rotated_GIC_RF':(0.,)*7 if valid else None}
class IndependentGullSourceAndMetricTruth(unittest.TestCase):
    def test_original_v125_2020_cohort_replay_exact_before_GIC_Y(self):
        panel='HG_OOSTENDE'
        old=prior(panel)
        qa={'original_2020_JulOct_original_source_step_counts_by_taxon':{FOCAL[0]:1900},
            'original_2020_JulOct_original_source_coastal_eligible_hours_by_taxon':{FOCAL[0]:2000},
            'original_2020_JulOct_original_eligible_bird_counts_by_taxon':{FOCAL[0]:5}}
        src=old['native_source_2020_birds_hour_and_movement_QA']
        got=m.check_original_v125_source_replay(panel,old,src,qa)
        self.assertTrue(got['all_v125_real_2020_source_animal_counts_and_hour_steps_replayed_exactly'])
        old['source_2020_GPS_publisher_md5_frozen']='bad'
        with self.assertRaisesRegex(ValueError,'RECORD_SOURCE_NOT_ADMITTED'):
            m.check_original_v125_source_replay(panel,old,src,qa)
    def test_real_original_tag_count_not_seven_rotated_endpoints(self):
        tax='Larus fuscus'
        events=[faux_event(tax,f'b{i}',7) for i in range(5) for k in range(5)]
        q=m.get_gic_source_gate(events,'LBBG_ZEEBRUGGE',{})
        self.assertEqual(q['original_year_source_steps_JulAug_total'],25)
        self.assertEqual(q['original_native_GIC_all8_valid_steps'],25)
        self.assertEqual(q['original_native_GIC_source_complete_fraction'],1)
        self.assertEqual(q['status'],'NOT_ESTIMATED_SOURCE_BIRD_OR_GIC_PIXELS')
    def test_source_missing_GIC_pixel_is_not_zero_wetland(self):
        a=faux_event('Larus fuscus','b',7,valid=True)
        b=faux_event('Larus fuscus','b',7,valid=False)
        q=m.get_gic_source_gate([a,b],'LBBG_ZEEBRUGGE',{})
        self.assertAlmostEqual(q['original_native_GIC_source_complete_fraction'],.5)
        self.assertFalse(q['source_gic_valid_atleast90pct'])
    def test_exact_eight_source_GIC_RFs_unambiguous_same_step_enrichment(self):
        events=[]
        for b in range(5):
            for month in m.SEASON:
                for hour in range(30):
                    e=faux_event('Larus argentatus',f'b{b}',month)
                    e['original_UTC']+=timedelta(hours=hour%12)
                    events.append(e)
        gate={'status':'ORIGINAL_PUBLISHED_GIC_2020_EIGHT_PIXEL_SOURCE_ADMITTED'}
        r=m.compute_bird_equal_original_Z(events,gate,'HG_OOSTENDE')
        self.assertEqual(r['original_2020_true_independent_birds_scored'],5)
        self.assertEqual(r['primary_per_bird_equal_month_equal_B_GIC_RF50_step_enrichment'],1.)
        self.assertEqual(r['primary_10000_original_tagged_bird_bootstrap95'],[1.,1.])
        self.assertEqual(r['original_tagged_birds_with_positive_spatial_enrichment'],5)
        self.assertNotIn('b0',json.dumps(r))
    def test_original_y_zero_without_source_scoring_when_missing(self):
        r=m.compute_bird_equal_original_Z([],{'status':'NOT_ADMITTED'},'HG_OOSTENDE')
        self.assertEqual(r['status'],'NOT_ESTIMATED_BELGIAN_GIC_OR_BIRD_SOURCE_GATE')
    def test_fixed_original_gps_time_period_and_solar_detection_source(self):
        self.assertEqual(m.SEASON,(7,8))
        self.assertEqual(m.SUN_DAY_GT,3.)
        self.assertEqual(m.SUN_NIGHT_LT,-3.)
        self.assertEqual(m.RAYS,7)
        self.assertEqual(m.SOURCE_GIC_ALL8_MIN_VALID,.90)
if __name__=='__main__':unittest.main()
