"""v128 synthetic source-read tests ONLY, not real 2018 behavioral result."""
from datetime import datetime,timedelta
from io import StringIO
from unittest.mock import patch
import csv,gzip,unittest
import original_Vlieland_2018_ACC_GPS_year_source as v

def gz(rows,header):
    buf=StringIO();w=csv.writer(buf);w.writerow(header);w.writerows(rows)
    return gzip.compress(buf.getvalue().encode())

class Genuine2018HistoricalSourceKnownTruth(unittest.TestCase):
    def test_original_year_fixed_md5_both_sensors_and_reference(self):
        self.assertEqual(v.YEAR,2018)
        self.assertEqual(v.FROZEN_MONTHS,(6,7,8,9))
        self.assertEqual(v.FROZEN_RADIUS,25.)
        self.assertEqual(v.NATIVE_MD5[v.ORIGINAL_2018_ACC],
                         '2b079f5504a692a02db57dc7116e5a67')
        self.assertEqual(v.NATIVE_MD5[v.ORIGINAL_2018_GPS],
                         '113a796ab087234f4282b97af02e7559')
        self.assertEqual(v.MIN_BIRD_ELIGIBLE,8)
    def test_native_2018_true_GPS_bird_and_2019_source_are_separate_calendar_years(self):
        hdr=['timestamp','individual-local-identifier','visible','location-lat','location-long']
        source=gz([
            ['2018-06-01T12:00:00Z','A','TRUE',53.3,5.09],
            ['2018-06-01T12:15:00Z','B','TRUE',53.3,5.09],
            ['2018-06-01T13:00:00Z','A','FALSE',53.3,5.09],
            ['2019-06-01T12:00:00Z','C','TRUE',53.3,5.09]],hdr)
        index,birds,qa=v.original_GPS_bird_year(source,2018,{},True)
        self.assertEqual(birds,{'A','B'})
        self.assertEqual(qa['genuine_original_GPS_rows'],4)
        self.assertEqual(qa['original_annual_independent_genuine_birds_with_GPS'],2)
        self.assertIn('A',index)
        self.assertNotIn('C',index)
    def test_gps_acc_nearest_same_animal_with_no_interpolation_and_source_15min(self):
        gpshead=['timestamp','individual-local-identifier','visible','location-lat','location-long']
        gps=gz([
            ['2018-06-01T12:00:00Z','A','TRUE',53.3,5.09],
            ['2018-07-01T12:00:00Z','A','TRUE',53.3,5.09],
            ['2018-06-01T12:00:00Z','B','TRUE',60.0,7.0]],gpshead)
        index,birds,src=v.original_GPS_bird_year(gps,2018,{},True)
        acchead=['timestamp','individual-local-identifier','behavioural-classification','visible']
        acc=gz([
            ['2018-06-01T12:05:00Z','A','forage','TRUE'],
            ['2018-06-01T12:08:00Z','A','inactive','TRUE'],
            ['2018-07-01T12:06:00Z','A','forage','TRUE'],
            ['2018-07-01T12:07:00Z','A','inactive','TRUE'],
            ['2018-06-01T12:05:00Z','B','inactive','TRUE'],
            ['2018-06-01T12:28:00Z','A','forage','TRUE'],
            ['2018-08-01T13:00:00Z','A','walk','TRUE']],acchead)
        qa,eligible=v.original_2018_ACC_GPS_source_feasibility(acc,{},index)
        self.assertEqual(qa['original_2018_ACC_full_year_raw_rows'],7)
        self.assertEqual(qa['source_2018_original_gps_acc_15min_classified_source_QA'][
            'ACC_original_2018_samebird_GPS_match_within15min'],5)
        self.assertEqual(qa['source_original_2018_bird_quarterhour_binary_classes_25km_n'],2)
        self.assertEqual(qa['source_original_genuine_birds_ge100_EACH_class_two_2018_months'],0)
        self.assertFalse(qa['source_frozen_YEAR2018_bird_ge8_15minute_bins_ge1000_eligible'])
        self.assertEqual(qa['future_genuine_2018_RWS_tide_sun_or_behavioral_effect'],'NOT_ESTIMATED_SOURCE_ONLY')
    def test_2018_2019_tag_overlap_is_not_independent_new_birds(self):
        a={'B1','B2','B3'};b={'B2','B3','B4'}
        self.assertEqual(len(a&b),2)
        self.assertNotEqual(len(a)+len(b),len(a|b))
    def test_original_second_year_without_nonsource_label_never_forced_positive(self):
        gpshead=['timestamp','individual-local-identifier','location-lat','location-long']
        gps=gz([['2018-06-01T12:00:00Z','A',53.3,5.09]],gpshead)
        index,_,_=v.original_GPS_bird_year(gps,2018,{},True)
        acc=gz([['2018-06-01T12:02:00Z','A','walk']],
                  ['timestamp','individual-local-identifier','behavioural-classification'])
        with self.assertRaisesRegex(v.SourceStop,'LITERAL_FORAGE_OR_INACTIVE'):
            v.original_2018_ACC_GPS_source_feasibility(acc,{},index)
    def test_frozen_original_2019_GPS_source_replay_cannot_accept_2018_fixture(self):
        gps=gz([['2019-01-01T12:00:00Z','B1',53.3,5.09]],
               ['timestamp','individual-local-identifier','location-lat','location-long'])
        with self.assertRaisesRegex(v.SourceStop,'2019_ORIGINAL_GPS_SOURCE_NOT_EXACT'):
            v.original_GPS_bird_year(gps,2019,{},False)
if __name__=='__main__':unittest.main()
