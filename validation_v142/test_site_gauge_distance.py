import unittest
from site_gauge_distance import haversine,run
class SiteGaugeTest(unittest.TestCase):
    def test_geometry(self):
        self.assertAlmostEqual(haversine((0,0),(0,0)),0)
        self.assertGreater(haversine((0,0),(0,1)),100)
        self.assertLess(haversine((0,0),(0,1)),120)
    def test_source_site_count(self):
        d=run()
        self.assertEqual(d["n_source_acoustic_sites"],9)
        self.assertEqual(d["sites_with_nearest_gauge_more_than_80_km"],2)
        self.assertEqual(d["global_tide_by_solar_effect"],"NOT_ESTIMATED")
if __name__=="__main__":unittest.main()
