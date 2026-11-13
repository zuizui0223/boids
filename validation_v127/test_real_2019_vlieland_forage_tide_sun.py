"""v127 known-truth unit tests ONLY. No synthetic bird data are field evidence."""
from datetime import datetime,timedelta,timezone
from collections import Counter
from unittest.mock import patch
import unittest,math
import numpy as np
import real_2019_vlieland_RWS_fourmonths as tide
import vlieland_acc_forage_tide_sun_fourway as s
import run_original_2019_vlieland_forage_tide_solar as runner

def _native_tide_sample(n,unit='cm',datum='NAP'):
    dt=datetime(2019,6,1,tzinfo=timezone(timedelta(hours=1)))
    rec=[{'Tijdstip':(dt+timedelta(minutes=10*i)).isoformat(),
          'Meetwaarde':{'Waarde_Numeriek':int(100*math.sin(i/37.))}}
          for i in range(n)]
    return {'Succesvol':True,'WaarnemingenLijst':[{'AquoMetadata':{
        'Grootheid':{'Code':'WATHTE'},'Eenheid':{'Code':unit},
        'Hoedanigheid':{'Code':datum}},'MetingenLijst':rec}]}

class TrueOriginalVlieland2019FieldTests(unittest.TestCase):
    def test_real_2019_month_native_10minute_fixed_cmNAP_and_gauge_clock(self):
        result,proof=tide.parse_native_month(6,_native_tide_sample(4321))
        self.assertEqual(proof['true_original_2019_10min_unique_count'],4321)
        self.assertAlmostEqual(proof['source_native_month_coverage'],4321/4320)
        self.assertEqual(min(result).isoformat(),'2019-05-31T23:00:00+00:00')
        self.assertLessEqual(max(abs(v) for v in result.values()),1.)
        self.assertEqual(proof['real_waterheight_cmNAP_to_metres_divide_by100_only'],True)
    def test_real_RWS_month_low_coverage_or_wrong_datum_rejected(self):
        with self.assertRaisesRegex(tide.NativeTideSourceStop,'COVERAGE_LT80PCT'):
            tide.parse_native_month(6,_native_tide_sample(200))
        with self.assertRaisesRegex(tide.NativeTideSourceStop,'COVERAGE_LT80PCT'):
            tide.parse_native_month(6,_native_tide_sample(4321,datum='NOT_NAP'))
        with self.assertRaisesRegex(tide.NativeTideSourceStop,'UNFROZEN_RWS_MONTH'):
            tide.parse_native_month(4,_native_tide_sample(4321))
    def test_prior_real_2019_RWS_48hour_source_gate(self):
        old={'analysis':'V126_RWS_2019_ORIGINAL_VLIELAND_HAVEN_JUNE_48H_TRUE_MEASURED_TIDAL_SOURCE',
            'source_status':'ORIGINAL_RWS_2019_VLIELAND_HAVEN_MEASURED_TIDE_SOURCE_ADMITTED',
            'original_publisher_RWS_station_identity':{'original_native_RWS_station_code':'vlieland.haven'},
            'original_2019_true_tide_source_quality':{'native_original_2019_waterheight_observed_10min_n':289}}
        self.assertEqual(tide.validate_previous_RWS_48h_pilot(old)[
            'native_true_48h_10min_measurements'],289)
        old['source_status']='SOURCE_NOT_ADMITTED'
        with self.assertRaisesRegex(tide.NativeTideSourceStop,'SOURCE_IDENTITY_DRIFT'):
            tide.validate_previous_RWS_48h_pilot(old)
    def test_original_same_bird_quarterhour_15min_not_raw_classifier_bursts(self):
        t=datetime(2019,6,3,12,15)
        private={('bird_A',t):{'private_bird':'bird_A',
                 'native_UTC_15min_bin':t,'earliest_true_classification_UTC':t+timedelta(minutes=1),
                 'original_same_bird_GPS_latitude':53.3,
                 'original_same_bird_GPS_longitude':5.1,
                 'n_native_forage_classifier_events':7,
                 'n_native_inactive_classifier_events':3}}
        e,source=s.original_2019_gps_acc_quarterhour_source(private)
        self.assertEqual(len(e),1)
        self.assertEqual(source['source_classes_from_original_same_bird_GPS'][
           'source_native_forage_class_events_in_all_15minute_bins'],7)
        self.assertEqual(source['original_2019_true_source_bin_n'],1)
        self.assertEqual(e[0]['source_utc_event'].tzinfo,timezone.utc)
    def test_predeclared_source_fourcell_cannot_admit_one_day_or_one_bird(self):
        dt=datetime(2019,6,2,12,tzinfo=timezone.utc)
        one=[{'private_bird':'fake_bird','source_month':6,'source_utc_event':dt,
              'source_lat':53.3,'source_lon':5.09,
              'original_acc_forage_events':500,'original_acc_inactive_events':1}]
        with patch.object(s,'_solar_label',return_value='day'),patch.object(
             s,'nearest_original_rws',return_value={
              'source_phase':1,'source_height_bin':2}):
            groups,source=s.source_real_tide_sun_fourway(one,{dt:.5})
        self.assertFalse(source['true_original_source_admitted_before_forage_share_Y'])
        self.assertEqual(s.original_true_bird_BSTI_from_ACC_source(groups,source)[
             'outcome_status'],'NOT_ESTIMATED_ORIGINAL_2019_BEHAVIOUR_TIDE_SUN_SOURCE_GATE')
    def test_exact_fourway_behaviour_share_math_original_bird_not_15min_event_n(self):
        dt=datetime(2019,6,1,12,tzinfo=timezone.utc)
        cells={}
        for bird in range(8):
            for mon in (6,7):
                for height in (1,2):
                    group={}
                    for phase,sun in s.SOURCE_CELL_CLASSES:
                        n_f=10 if (phase==1 and sun=='night') else 0
                        group[(phase,sun)]=[
                          {'private_bird':str(bird),'source_month':mon,
                           'source_utc_event':dt+timedelta(days=i%3),
                           'original_acc_forage_events':n_f,
                           'original_acc_inactive_events':10-n_f}
                           for i in range(8)]
                    cells[(str(bird),mon,height)]=group
        admit={'true_original_source_admitted_before_forage_share_Y':True,
               'true_original_source_all_four_conditions':{
                'true_original_unique_birds_in_complete_fourcell_source':8}}
        z=s.original_true_bird_BSTI_from_ACC_source(cells,admit)
        self.assertEqual(z['original_independent_tagged_birds_N'],8)
        self.assertEqual(z['original_complete_fourway_bird_month_height_groups'],32)
        results=z['original_true_bird_B_S_T_I_results']
        self.assertAlmostEqual(results[s.BASIS[0]]['true_original_individual_equal_weight_mean'],.25)
        self.assertAlmostEqual(results[s.BASIS[1]]['true_original_individual_equal_weight_mean'],.5)
        self.assertAlmostEqual(results[s.BASIS[2]]['true_original_individual_equal_weight_mean'],.5)
        self.assertAlmostEqual(results[s.BASIS[3]]['true_original_individual_equal_weight_mean'],1.)
        self.assertEqual(results[s.BASIS[3]]['genuine_10000_independent_tagged_bird_bootstrap_CI95'],[1.,1.])
        self.assertNotIn('bird_A',str(z))
    def test_ghosts_are_strictly_predeclared_not_selected_by_outcome(self):
        with self.assertRaisesRegex(ValueError,'GHOST_SHIFT_NOT_FROZEN'):
            s.source_real_tide_sun_fourway([],{datetime(2019,6,1,tzinfo=timezone.utc):0.},ghost_shift_days=5)
        self.assertEqual(s.GHOST_DAYS,(3,7,11))
    def test_real_prior_v126_source_replay_cannot_accept_fake_class_metadata(self):
        old={'analysis':'V126_ORIGINAL_2019_VLIELAND_NATIVE_FORAGE_INACTIVE_GPS_TIME_GEO_SOURCE_QA',
             'source_status':'SOURCE_STOP'}
        with self.assertRaisesRegex(Exception,'IDENTITY'):
             runner.verify_previous_original_v126_source(old,{}, {})
    def test_original_label_source_not_measured_minutes(self):
        self.assertIn('NOT observed prey ingestion',s.__doc__)
        self.assertIn('harbour tide PROXY',tide.__doc__)
        self.assertIn('15min_BIN_is_not_15minutes_of_foraging',
             runner.run.__code__.co_consts.__str__())
if __name__=='__main__':unittest.main()
