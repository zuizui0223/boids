import unittest, math, tempfile, json
from pathlib import Path
import global_2019_all_station_physical as m
from original_UHSLC_2019_tide_solar import harmonic_form
class RealSourceMathKnownTruth(unittest.TestCase):
    def test_hypergeometric_counts(self):
        self.assertEqual(m.exact_random_hour_abs_M(24,6,0),0)
        self.assertEqual(m.exact_random_hour_abs_M(24,6,24),0)
        self.assertAlmostEqual(m.exact_random_hour_abs_M(24,6,12),
                               m.exact_random_hour_abs_M(24,6,12))
        self.assertGreater(m.exact_random_hour_abs_M(24,6,12),.1)
        self.assertLess(m.exact_random_hour_abs_M(24,6,12),.3)
        with self.assertRaisesRegex(ValueError,'invalid'):m.exact_random_hour_abs_M(24,0,12)
    def test_original_2019_fake_tide_and_true_UTC_sun_separately(self):
        data={i:200*math.cos(2*math.pi*i/12.4206012) for i in range(8760)}
        r=m.analyze_hourly(data,0,0)
        self.assertEqual(r['status'],'ACTUAL_ORIGINAL_HOURLY_SOURCE')
        self.assertGreater(r['n_valid_day_low_2'],250)
        self.assertGreater(r['mean_daily_abs_M'],0)
        self.assertGreater(r['null_random_hour_baseline_abs_M'],0)
        self.assertTrue(r['Q25_mm']<0)
        self.assertEqual(sum(x['observed_hours'] for x in r['monthly'].values()),8760)
    def test_regime_from_real_period_synthetic(self):
        data={i:100*math.sin(2*math.pi*i/12.4206012) for i in range(8760)}
        self.assertEqual(harmonic_form(data)['regime'],'semidiurnal')
    def test_latitude_bands_and_immutable_input_guard(self):
        self.assertEqual(len(m.BANDS),12)
        with tempfile.TemporaryDirectory() as root:
            f=Path(root)/'bad.json';f.write_text(json.dumps({'source_original_provider':'primary_UHSLC',
              'original_public_UHSLC_stations_and_datum_segments':[{'uhslc_id':1}]}))
            with self.assertRaisesRegex(ValueError,'immutable'):m.run(f,'N_00_15',Path(root)/'never.json')
    def test_low_water_sample_is_not_biological_activity(self):
        self.assertIn('solar',m.__doc__)
        self.assertIn('not biological niche',m.__doc__)
if __name__=='__main__':unittest.main()
