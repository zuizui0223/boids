"""v33 exact Gaussian covariance no-social-arrow negative known-truth fixtures."""
import unittest
from validation_fish_school_v33.non_social_spatial_common_driver import run,POSITIONS

class SpatiallyCorrelatedCommonSource(unittest.TestCase):
    def test_near_predictive_advantage_without_fish_social_edges(self):
        r=run()
        self.assertEqual(r["status"],"EXACT_CONSTRUCTED_ZERO_SOCIAL_ARROW_SPATIAL_COMMON_DRIVER_COUNTEREXAMPLE")
        self.assertFalse(r["fish_or_boid_field_data_read"])
        self.assertFalse(r["social_fish_force_or_acoustic_causal_effect_identified"])
        self.assertEqual(len(r["results"]),8)
        for label in ("non_social_near_additional_MSE_gain",
                      "non_social_true_vs_rotated_MSE_gain",
                      "non_social_true_near_vs_far_MSE_gain"):
            value=r["comparisons"][label]
            self.assertEqual(value["n_focals_with_positive_gain"],8)
            self.assertGreater(value["mean_population_optimal_MSE_gain"],0)

    def test_original_frozen_2021_data_never_used_in_null(self):
        r=run()
        self.assertEqual(len(POSITIONS),8)
        self.assertIn("zero fish-fish",r["model"])
        self.assertNotIn("2021",r["model"])
        self.assertTrue(all(z["MSE_global_nearest_true_after_focal"]>0 for z in r["results"]))

if __name__=="__main__":unittest.main()
