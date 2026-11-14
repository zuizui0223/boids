"""v129 known-truth tests; synthetic fixtures are NOT animal field evidence."""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timedelta,timezone
import math
import unittest
import run_original_2018_vlieland_forage_tide_solar as v
import real_2018_vlieland_RWS_measured as r
import vlieland_acc_forage_tide_sun_fourway as old

def measured_month(month=6,n=4321,unit='cm',datum='NAP',year=2018):
    dt=datetime(year,month,1,tzinfo=timezone(timedelta(hours=1)))
    obs=[{'Tijdstip':(dt+timedelta(minutes=10*i)).isoformat(),
          'Meetwaarde':{'Waarde_Numeriek':int(90*math.sin(i/37.))}}
         for i in range(n)]
    return {'Succesvol':True,'WaarnemingenLijst':[{
        'AquoMetadata':{'Grootheid':{'Code':'WATHTE'},
                        'Eenheid':{'Code':unit},'Hoedanigheid':{'Code':datum}},
        'MetingenLijst':obs}]}

class Frozen2018VlielandHindcastKnownTruth(unittest.TestCase):
    def test_original_2018_month_real_10minute_clock_cmNAP_gate(self):
        data,proof=r.parse_true_original_RWS_2018_month(6,measured_month())
        self.assertEqual(len(data),4321)
        self.assertAlmostEqual(proof['original_2018_native_RWS_valid_fraction'],4321/4320)
        self.assertEqual(min(data).isoformat(),'2018-05-31T23:00:00+00:00')
        self.assertLessEqual(max(abs(x) for x in data.values()),.9)

    def test_refuse_mislabeled_year_wrong_datum_and_unfrozen_month(self):
        for src in (measured_month(n=100),measured_month(unit='m'),
                    measured_month(datum='NOT_NAP'),measured_month(year=2019)):
            with self.assertRaises(r.NativeSourceStop):
                r.parse_true_original_RWS_2018_month(6,src)
        with self.assertRaises(r.NativeSourceStop):
            r.request_month_original_RWS(5)

    def test_original_2018_bird_quarterhour_to_unchanged_2019_estimator_schema(self):
        t=datetime(2018,6,3,9,15)
        d={('secret-A',t):{'private_bird':'secret-A','native_UTC_15min_bin':t,
              'earliest_true_classification_UTC':t+timedelta(minutes=5),
              'original_same_bird_GPS_latitude':53.3,
              'original_same_bird_GPS_longitude':5.09,
              'n_native_forage_classifier_events':2,
              'n_native_inactive_classifier_events':8}}
        converted,proof=v.bins_2018_exact_v127_schema(
              d,{'source_original_2018_bird_quarterhour_binary_classes_25km_n':1})
        self.assertEqual(converted[0]['source_utc_event'].year,2018)
        self.assertEqual(converted[0]['original_acc_forage_events'],2)
        self.assertEqual(converted[0]['original_acc_inactive_events'],8)
        self.assertEqual(converted[0]['source_utc_event'].tzinfo,timezone.utc)
        self.assertEqual(proof['original_2018_true_bird_ACC_GPS_15min_bins'],1)
        self.assertNotIn('secret-A',str(proof))
        with self.assertRaises(v.SourceStop):
            v.bins_2018_exact_v127_schema(
              d,{'source_original_2018_bird_quarterhour_binary_classes_25km_n':2})

    def test_bad_original_2018_bin_date_and_class_count_fail_closed(self):
        t=datetime(2019,6,3,9,15)
        e={'private_bird':'a','native_UTC_15min_bin':t,
           'earliest_true_classification_UTC':t,
           'original_same_bird_GPS_latitude':53.3,
           'original_same_bird_GPS_longitude':5.09,
           'n_native_forage_classifier_events':10,
           'n_native_inactive_classifier_events':0}
        with self.assertRaisesRegex(v.SourceStop,'SOURCE_MISMATCH'):
            v.bins_2018_exact_v127_schema(
                {('a',t):e},{'source_original_2018_bird_quarterhour_binary_classes_25km_n':1})
        t=t.replace(year=2018)
        e['native_UTC_15min_bin']=t;e['earliest_true_classification_UTC']=t
        e['n_native_forage_classifier_events']=-1
        with self.assertRaisesRegex(v.SourceStop,'BINARY_LABEL_INVALID'):
            v.bins_2018_exact_v127_schema(
                {('a',t):e},{'source_original_2018_bird_quarterhour_binary_classes_25km_n':1})

    def test_previous_2018_original_source_has_hard_replay_stop(self):
        with self.assertRaisesRegex(v.SourceStop,'NOT_ADMITTED'):
            v.source_only_replay({'source_status':'PENDING'}, {},{},{},{},{})
        oldsource={'analysis':'V128_ORIGINAL_VLIELAND_2018_INDEPENDENT_CALENDAR_YEAR_ACC_GPS_SOURCE_GATE',
                   'source_status':'TRUE_PUBLISHER_2018_VLIELAND_GPS_ACC_BIN_FEASIBILITY_ADMITTED',
                   'source_original_2018_GPS_true_source_QA':{},
                   'source_original_2019_GPS_unchanged_source_replay_for_bird_overlap':{},
                   'original_2018_samebird_ACC_class_and_GPS_25km_source_QA':{},
                   'source_anonymous_true_2018_vs_2019_GPS_individual_overlap':{}}
        with self.assertRaisesRegex(v.SourceStop,'SOURCE_COUNTS'):
            v.source_only_replay(oldsource,{}, {}, {}, {'altered':True}, {})

    def test_genuine_2018_gate_before_Y_and_unaltered_bird_weighting(self):
        # Same old v127 original numerical estimator; synthetic 8 birds and
        # 2 months, each two height-band fourcell groups.
        accepted={}
        for bird in range(8):
            for month in (6,7):
                for stage in (1,2):
                    cells={}
                    for phase,sun in old.SOURCE_CELL_CLASSES:
                        f=10 if (phase==1 and sun=='night') else 0
                        cells[(phase,sun)]=[{
                          'private_bird':str(bird),'source_month':month,
                          'source_utc_event':datetime(2018,month,2+i%3,tzinfo=timezone.utc),
                          'original_acc_forage_events':f,
                          'original_acc_inactive_events':10-f} for i in range(6)]
                    accepted[(str(bird),month,stage)]=cells
        gate={'true_original_source_admitted_before_forage_share_Y':True,
              'true_original_source_all_four_conditions':{
               'true_original_unique_birds_in_complete_fourcell_source':8}}
        result=v.anonymous_effect(old.original_true_bird_BSTI_from_ACC_source(
                         accepted,gate,seed=old.RNG_SEED))
        self.assertEqual(result['source_year'],2018)
        self.assertEqual(result['original_real_tagged_bird_n'],8)
        self.assertAlmostEqual(result['same_v127_unchanged_B_S_T_I_true_bird_bootstrap'][
            old.BASIS[1]]['true_original_individual_equal_weight_mean'],.5)
        self.assertAlmostEqual(result['same_v127_unchanged_B_S_T_I_true_bird_bootstrap'][
            old.BASIS[3]]['true_original_individual_equal_weight_mean'],1.)
        self.assertNotIn('secret-A',str(result))

    def test_source_only_no_2018_field_effect_when_fourcell_not_admitted(self):
        source={'true_original_source_admitted_before_forage_share_Y':False}
        self.assertEqual(v.anonymous_effect(
            old.original_true_bird_BSTI_from_ACC_source({},source))['2018_status'],
            'NOT_ESTIMATED_SOURCE_GATE')
        self.assertEqual(old.GHOST_DAYS,(3,7,11))
        self.assertEqual(v.ORIGINAL_2019_S,-.1138426)
        self.assertEqual(v.ORIGINAL_2019_I,-.0459232)

if __name__=='__main__':
    unittest.main()
