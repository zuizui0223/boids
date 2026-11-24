"""v37 synthetic-only exact equilibrium and no-virtual-feedback tests."""
import unittest
import numpy as np
from validation_fish_school_v37.nonreciprocal_alignment_cohesion import (
 original_analytic_equilibrium,exact_time_response,run,AnalyticStop
)

class DirectedLinearAttractionPhysics(unittest.TestCase):
    def test_nonreciprocal_exact_speed_alignment_with_nonzero_following_distance(self):
        A,f,eq,w=original_analytic_equilibrium(alpha=1,beta=.5,gamma=.4,delta=5)
        self.assertAlmostEqual(eq[0],-4.)
        self.assertAlmostEqual(eq[1],0.)
        np.testing.assert_allclose(A@eq+f,[0,0],atol=1e-12)
        self.assertTrue(all(z.real<0 for z in w))

    def test_one_way_fish_control_can_reach_cohesion_with_no_speed_mismatch(self):
        A,f,eq,w=original_analytic_equilibrium(alpha=1,beta=.5,gamma=.4,delta=0)
        self.assertAlmostEqual(eq[0],0.)
        self.assertAlmostEqual(eq[1],0.)
        self.assertTrue(all(z.real<0 for z in w))

    def test_attraction_fourfold_reduces_spacing_fourfold(self):
        slow=original_analytic_equilibrium(1,.5,.4,5)[2]
        fast=original_analytic_equilibrium(1,2.,.4,5)[2]
        self.assertAlmostEqual(slow[0]/fast[0],4.)
        self.assertEqual(slow[1],fast[1])

    def test_speed_mismatch_linear_scaling(self):
        a=original_analytic_equilibrium(1,.5,.4,2)[2]
        b=original_analytic_equilibrium(1,.5,.4,5)[2]
        self.assertAlmostEqual(b[0]/a[0],2.5)
        self.assertEqual(b[1],0.)

    def test_alignment_gain_alpha_changes_convergence_not_fixed_spacing(self):
        x=original_analytic_equilibrium(.2,.5,.4,5)[2]
        y=original_analytic_equilibrium(3.0,.5,.4,5)[2]
        np.testing.assert_array_equal(x,y)

    def test_independent_matrix_exponential_after_40sec_matches_fixed_point(self):
        result=exact_time_response(1,.5,.4,5,40.,initial=(0,0))
        np.testing.assert_allclose(result,[-4,0],atol=1e-8,rtol=0)
        initial=exact_time_response(1,.5,.4,5,0.,initial=(0,0))
        np.testing.assert_allclose(initial,[0,0],atol=1e-12,rtol=0)

    def test_zero_attraction_has_no_unique_cohesion_fixed_point_stop(self):
        with self.assertRaises(AnalyticStop):
            original_analytic_equilibrium(1,0,.4,5)

    def test_never_promote_constructed_to_original_fish_result(self):
        result=run()
        self.assertEqual(len(result["source_free_example_predeclared_grid"]),12)
        self.assertFalse(result["source_experimental_fish_rows_read"])
        self.assertFalse(result["experimental_C2_C3_manipulation_effect_estimated"])
        self.assertFalse(result["fish_origin_sounds_or_causal_social_intervention_identified"])
        self.assertTrue(all(z["virtual_leader_never_responds_to_real_fish"] for z in result["source_free_example_predeclared_grid"]))

if __name__=="__main__":
    unittest.main()
