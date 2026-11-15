"""Unit and source-linked tests. The normal critical value is only model-conditional."""
import math
import unittest
from pathlib import Path
from statistics import NormalDist
from validation_v135.source_consistency import build

ROOT = Path(__file__).resolve().parents[1]

class V135Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build(ROOT)
    def test_six_distinct_coasts_not_effects(self):
        s = self.result["sources"]
        self.assertEqual(s["interaction_casebook_coasts"], 6)
        self.assertEqual(s["interaction_records_with_reported_signed_beta_and_se"], 2)
        self.assertEqual(s["physically_and_endpoint_harmonized_cross_coast_effects"], 0)
        self.assertEqual(s["global_pooled_effect"], "NOT_ESTIMATED")
    def test_three_species_one_island(self):
        p = self.result["plover"]
        self.assertEqual(len(p["contrasts"]), 3)
        self.assertIn("One barrier island", p["study_units"])
        self.assertGreater(p["normal_critical_z_two_sided_bonferroni_three"], 2.39)
    def test_contrasts_computed_from_published_models(self):
        for row in self.result["plover"]["contrasts"]:
            self.assertAlmostEqual(row["beach_minus_mudflat_log_slope"], row["beach_tide_coefficient"]-row["mudflat_tide_coefficient"])
            self.assertAlmostEqual(row["relative_beach_to_mudflat_ratio_per_1sd_tide"], math.exp(row["beach_minus_mudflat_log_slope"]), places=5)
            self.assertGreater(row["simultaneous_rounding_sensitivity_ratio_lower"],1)
            self.assertLess(row["simultaneous_rounding_sensitivity_ratio_lower"],row["relative_beach_to_mudflat_ratio_per_1sd_tide"])
            self.assertGreater(row["simultaneous_rounding_sensitivity_ratio_upper"],row["relative_beach_to_mudflat_ratio_per_1sd_tide"])
    def test_conservative_covariance_max_se(self):
        p = self.result["plover"]
        z = NormalDist().inv_cdf(1-0.05/(2*3))
        for row in p["contrasts"]:
            upper = row["beach_reported_se"]+row["mudflat_reported_se"]
            self.assertAlmostEqual(row["unknown_covariance_se_upper"], upper)
            lo=math.exp(row["beach_minus_mudflat_log_slope"]-.01-z*(upper+.01))
            hi=math.exp(row["beach_minus_mudflat_log_slope"]+.01+z*(upper+.01))
            self.assertAlmostEqual(row["simultaneous_rounding_sensitivity_ratio_lower"],lo,places=5)
            self.assertAlmostEqual(row["simultaneous_rounding_sensitivity_ratio_upper"],hi,places=5)

if __name__ == "__main__":
    unittest.main()
