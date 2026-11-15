"""Small deterministic fixtures: never masquerade as real Raposa field output."""
import unittest
from appendix_site_macro import site_summary

class SiteSummaryTest(unittest.TestCase):
    def test_rai_habitat_pairing_synthetic(self):
        sheets={
            "Station metadata": {
                1:{"D":"Site code", "R":"Total deployment time (hours) ***"},
                2:{"D":"A","F":"1","E":"A reserve","G":"Salt marsh","R":"100",
                   "M":"30.0","N":"-85.0"},
                3:{"D":"A","F":"2","E":"A reserve","G":"Ecotone","R":"100",
                   "M":"30.1","N":"-85.1"},
            },
            "Site means": {
                4:{"G":"A reserve","H":"A reserve"},
                5:{"E":"Species","G":"Wetland","H":"Ecotone"},
                6:{"A":"Mammalia","E":"Species_one","G":"2.0","H":"8.0"},
                7:{"A":"Aves","E":"Species_two","G":"8.0","H":"1.0"},
            }
        }
        result=site_summary(sheets)
        self.assertEqual(result["station_metadata"]["valid_positive_hours_stations"],2)
        self.assertEqual(result["site_mean_raI"]["paired_site_labels_with_both_habitats"],1)
        self.assertGreater(result["site_mean_raI"]["paired_ecotone_minus_wetland_log_rai_pseudocount"]["Mammalia"]["median_log_pseudocount_ratio"],0)
        self.assertLess(result["site_mean_raI"]["paired_ecotone_minus_wetland_log_rai_pseudocount"]["Aves"]["median_log_pseudocount_ratio"],0)
        self.assertEqual(result["tide_by_solar_ecological_rate_effect"],"NOT_ESTIMATED")
if __name__=="__main__":
    unittest.main()
