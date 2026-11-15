"""Tests check algebra and synthetic outputs, not biological truth."""
import unittest
from dataclasses import replace
from bat_acoustic_game import (Environment, ACTIONS, actions, success, payoff,
    pure_nash, quantal_response, run_examples, jammer_indifference_contestability)
from sweep_v1 import audit

class AcousticToyTests(unittest.TestCase):
    def test_action_support(self):
        self.assertNotIn("DETOUR",actions(Environment(routes=1)))
        self.assertIn("DETOUR",actions(Environment(routes=4)))
        with self.assertRaises(ValueError):
            success("DETOUR","EMIT",Environment(routes=1))
    def test_probability_bounds(self):
        for b in (0,1,3):
            for m in (0,1,4):
                e=Environment(public_info=b,masking=m)
                for a in ACTIONS:
                    for z in ACTIONS:
                        self.assertTrue(0<success(a,z,e)<1)
    def test_mask_increase_hurts_emitter(self):
        e=Environment(public_info=0,masking=.2)
        self.assertGreater(success("EMIT","EMIT",e),
                           success("EMIT","EMIT",replace(e,masking=2)))
    def test_jam_stronger_hurts_rival(self):
        e=Environment(jam_strength=0)
        self.assertGreater(success("EMIT","JAM",e),
                           success("EMIT","JAM",replace(e,jam_strength=5)))
    def test_public_signal_helps_listener(self):
        e=Environment(public_info=0)
        self.assertLess(success("LISTEN","EMIT",e),
                        success("LISTEN","EMIT",replace(e,public_info=2)))
    def test_jam_contestability_slope(self):
        e=Environment(public_info=.2,masking=.2,jam_strength=3,contestability=0)
        v0=payoff("JAM","EMIT",e)-payoff("EMIT","EMIT",e)
        e9=replace(e,contestability=.9)
        v9=payoff("JAM","EMIT",e9)-payoff("EMIT","EMIT",e9)
        self.assertGreater(v9,v0)
    def test_add_route_cannot_hurt_available_best_response(self):
        e=Environment(public_info=0,masking=4,routes=1)
        f=replace(e,routes=4)
        self.assertGreaterEqual(
            max(payoff(a,"EMIT",f) for a in actions(f)),
            max(payoff(a,"EMIT",e) for a in actions(e)))
    def test_nash_exact_best_response(self):
        e=Environment(public_info=0,masking=0,contestability=0)
        self.assertIn(("EMIT","EMIT"),pure_nash(e))
        for a,b in pure_nash(e):
            self.assertGreaterEqual(payoff(a,b,e),
                                    max(payoff(z,b,e) for z in actions(e))-1e-9)
            self.assertGreaterEqual(payoff(b,a,e),
                                    max(payoff(z,a,e) for z in actions(e))-1e-9)
    def test_response_valid_multiple_starts(self):
        e=Environment(public_info=.5,masking=1)
        for start in (None,*ACTIONS):
            r=quantal_response(e,starting_action=start)
            self.assertTrue(r["converged"])
            self.assertAlmostEqual(sum(r["probabilities"].values()),1,10)
    def test_example_result_marked_synthetic(self):
        r=run_examples()
        self.assertEqual(r["status"],"SYNTHETIC_ONLY_NOT_FITTED")
        self.assertTrue(all(v["all_starts_converged"] for v in r["scenarios"].values()))
    def test_jam_threshold_exact_indifference(self):
        e=Environment(public_info=.2,masking=.2,jam_strength=3)
        cstar=jammer_indifference_contestability(e)
        self.assertAlmostEqual(cstar,.2589663968716714,places=10)
        e0=replace(e,contestability=cstar)
        self.assertAlmostEqual(payoff("JAM","EMIT",e0),
                               payoff("EMIT","EMIT",e0),places=10)
    def test_jam_threshold_direction(self):
        e=Environment(public_info=.2,masking=.2,jam_strength=3)
        cstar=jammer_indifference_contestability(e)
        for c,sign in ((cstar-.05,-1),(cstar+.05,+1)):
            e1=replace(e,contestability=c)
            difference=payoff("JAM","EMIT",e1)-payoff("EMIT","EMIT",e1)
            self.assertGreater(difference*sign,0)
    def test_toy_strategy_switch(self):
        e=Environment(public_info=0,masking=4,contestability=.2,routes=4)
        self.assertIn(("EMIT","DETOUR"),pure_nash(e))
        self.assertIn(("EMIT","LISTEN"),pure_nash(replace(e,public_info=1)))
    def test_sweep_direction(self):
        r=audit()
        self.assertEqual(r["status"],"SYNTHETIC_ONLY_NOT_EMPIRICAL")
        self.assertEqual(r["social_info_delta_detour"]["count_negative"],27)
        self.assertEqual(r["contestability_delta_jam"]["count_positive"],27)
        self.assertEqual(r["nonconverged"],[])
    def test_nonnumeric_negative_param_rejected(self):
        with self.assertRaises(ValueError):
            Environment(masking=-.1)

if __name__=="__main__":
    unittest.main()
