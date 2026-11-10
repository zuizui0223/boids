"""Known truth 2018 target year and immutable 2019 reference frame."""
import unittest,csv,io,math
from datetime import timedelta
import original_UHSLC_2018_holdout as m
class Original2018Holdout(unittest.TestCase):
    def test_true_year_boundary_in_request(self):
        uri=m.source_uri(m.PROVIDERS[0][1],137)
        self.assertIn('2018-01-01',uri)
        self.assertIn('2019-01-01',uri)
        self.assertNotIn('2020-01-01',uri)
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED'):
            m.source_uri('https://example.invalid/a',3)
    def test_record_id_unmixed_and_quality_filtered(self):
        io1=io.StringIO();w=csv.writer(io1)
        w.writerow(['uhslc_id','record_id','time','sea_level','quality'])
        w.writerow(['','','UTC','mm',''])
        for h in range(100):
            dt=m.TEST_START+timedelta(hours=h)
            stamp=dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            w.writerow([15,101,stamp,100*math.sin(h/4),4])
            w.writerow([15,102,stamp,-9900,4])
            w.writerow([15,101,stamp,9999,1])
        valid=m.parse_real_2018(io1.getvalue().encode(),15,101)
        self.assertEqual(len(valid),100)
        self.assertTrue(abs(valid[5])<100)
        admitted,reason=m.quality_admitted(valid)
        self.assertFalse(admitted);self.assertEqual(reason,'2018_YEAR_COVERAGE_LT80PCT')
    def test_complete_source_low_period_real_solar_geometry(self):
        # Synthetic 12.4h water cycle, actual 2018 UTC astronomy at true geocoordinates.
        d={h:100*math.sin(2*math.pi*h/12.4206012) for h in range(8760)}
        self.assertEqual(m.quality_admitted(d),(True,0))
        result=m.score_2018_real_tide_sun(d,0,0)
        self.assertEqual(result['status'],'VALID_2018_ORIGINAL_DAILY_TIDE_SOLAR_OPPORTUNITY')
        self.assertGreater(result['2018_n_source_lowwater_day_records'],300)
        self.assertTrue(.05<result['2018_mean_daily_abs_M']<.5)
        self.assertTrue(0<=result['2018_fraction_abs_M_at_least_025']<=1)
    def test_2018_missing_day_and_month_cannot_fabricate(self):
        d={h:0 for h in range(8760) if (m.TEST_START+timedelta(hours=h)).month!=8}
        ok,reason=m.quality_admitted(d)
        self.assertFalse(ok)
        self.assertEqual(reason,'2018_MONTH_SOURCE_COVERAGE_LT80PCT')
    def test_separate_source_datums_and_outcomes(self):
        self.assertEqual(m.TEST_YEAR,2018)
        self.assertEqual(m.SOURCE_RUN_V94,42616065580)
        self.assertEqual(m.DAY_ALT_DEG,3)
if __name__=='__main__':unittest.main()
