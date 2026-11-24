"""v39 completely constructed one-way circular following exact-known-truth tests."""
import math,unittest
from validation_fish_school_v39.circular_gain_bound import (
 exact_phase_lag,exact_steady_orbit,required_kappa,run,TheoryStop
)
class CircularOneWayFollower(unittest.TestCase):
    def test_exact_nonreciprocal_phase_lag_and_equal_linear_speed(self):
        v=10;R=15;k=1.
        o=exact_steady_orbit(R,v,k)
        self.assertAlmostEqual(o["stable_angular_phase_lag_rad"],2/3)
        self.assertEqual(o["steady_speed_difference_cm_s"],0)
        self.assertEqual(o["reciprocal_real_to_virtual_feedback_strength"],0)

    def test_exact_circle_chord_and_tangent_heading(self):
        o=exact_steady_orbit(15,10,1)
        self.assertAlmostEqual(o["steady_real_virtual_chord_separation_cm"],30*math.sin(1/3))
        self.assertAlmostEqual(o["steady_heading_alignment_cos"],math.cos(2/3))

    def test_exact_exponential_tracking_solution_without_fitting_fish(self):
        self.assertAlmostEqual(exact_phase_lag(0,15,15,1,delta_initial=0),0)
        self.assertAlmostEqual(exact_phase_lag(40,15,15,1,delta_initial=0),1,delta=1e-14)
        self.assertAlmostEqual(exact_phase_lag(1,15,15,1,delta_initial=1),1,delta=1e-14)

    def test_gain_required_for_cohesion_distance_bound(self):
        r=required_kappa(15,15,.8,5)
        o=exact_steady_orbit(15,15,r["minimum_gain_for_both_per_s"])
        self.assertLessEqual(o["steady_real_virtual_chord_separation_cm"],5+1e-12)
        self.assertGreaterEqual(o["steady_heading_alignment_cos"],.8-1e-12)
        self.assertEqual(r["dominant_constraint"],"cohesion")

    def test_speed_triples_requires_minimum_response_gain_to_triple(self):
        lo=required_kappa(15,5,.8,5)["minimum_gain_for_both_per_s"]
        hi=required_kappa(15,15,.8,5)["minimum_gain_for_both_per_s"]
        self.assertAlmostEqual(hi/lo,3)

    def test_fixed_gain_speed_increase_reduces_heading_alignment(self):
        x=[exact_steady_orbit(15,v,1) for v in (5,7.5,10,11.67,13.33,15)]
        self.assertTrue(all(a["steady_heading_alignment_cos"]>b["steady_heading_alignment_cos"] for a,b in zip(x,x[1:])))
        self.assertTrue(all(a["steady_real_virtual_chord_separation_cm"]<b["steady_real_virtual_chord_separation_cm"] for a,b in zip(x,x[1:])))

    def test_unwrapped_model_not_extrapolated_beyond_pi_branch(self):
        with self.assertRaises(TheoryStop):
            exact_steady_orbit(15,15,.2)
        with self.assertRaises(TheoryStop):
            exact_phase_lag(-1,15,5,1)
        with self.assertRaises(TheoryStop):
            required_kappa(15,10,.8,31)

    def test_six_cases_all_explicitly_math_not_original_fish(self):
        d=run()
        self.assertEqual(len(d["example_constructed_orbits_not_real_fish"]),6)
        self.assertTrue(d["fixed_response_gain_alignment_decreases_with_speed"])
        self.assertTrue(d["fixed_response_gain_following_distance_increases_with_speed"])
        self.assertFalse(d["source_original_fish_heading_or_distance_observations_used"])
        self.assertFalse(d["fish_acoustics_or_causal_Boids_behavior_identified"])
        self.assertAlmostEqual(d["exact_required_gain_ratio_for_both_constraints_low_to_high"],3)

if __name__=="__main__":unittest.main()
