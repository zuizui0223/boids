import unittest
from validation_v189.independent_two_published_RWS_gauge_geometries import PUBLISHED_2006_RD,site_weights,run
from validation_v188.original_Wadden13_RWS_tide_LOO import STATIONS
from validation_v185.original_fifteen_wadden_gauge_inventory import ATLAS
class IndependentGeometry(unittest.TestCase):
    def test_15_original_2006_table_complete(self):
        self.assertEqual(set(PUBLISHED_2006_RD),set(x[0] for x in ATLAS))
    def test_no_hidden_site_in_geometric_idw_or_triangles(self):
        for name in STATIONS:
            geo=site_weights(name,PUBLISHED_2006_RD)
            self.assertNotIn(name,geo["idw3_sites"])
            self.assertAlmostEqual(sum(geo["idw3_weights_by_name"].values()),1)
            if geo["triangle_site_names"] is not None:
                self.assertNotIn(name,geo["triangle_site_names"])
    def test_report_not_native_2018_instrument(self):
        v=run("/tmp/v189-source-reference-test.json")
        self.assertEqual(v["published_2006_vs_2011_station_differences_m"]["n_stations"],15)
        self.assertFalse(v["RWS_2018_2019_water_level_values_retrieved"])
        self.assertTrue(v["reference_location_comparison_not_2019_native_instrument_coordinate_check"])
if __name__=="__main__":unittest.main()
