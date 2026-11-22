"""Pre-outcome v20 regression tests: old/unreserved fixture seeds only."""
import unittest
import numpy as np
from validation_fish_boids_v15 import simulation as v15
from validation_fish_boids_v19 import crossed_simulation as v19
from validation_fish_boids_v20 import two_pathway_simulation as v20
from validation_fish_boids_v20.score_two_pathways import (
    SEEDS,ARMS,PHYS,RANGE,N,physical_scene,acoustic_kernel,
    _assert_source_equal,decompose_cell,call_counts,summarize,pre_one
)

class TwoPathwayKnownTruth(unittest.TestCase):
    def setUp(self):
        self.orig=v15.initialize(44,N)
        self.new=v20.State(self.orig.pos,self.orig.velocity,self.orig.calling,0,self.orig.rng_state)

    def test_locked_roster_and_factorial_arms(self):
        self.assertEqual((len(SEEDS),SEEDS[0],SEEDS[-1]),(768,7000,7767))
        self.assertEqual(len(ARMS),16)
        self.assertTrue(set(SEEDS).isdisjoint(set(range(6000,6768))))

    def test_physical_scaling_with_source_class_and_no_mutation(self):
        a=physical_scene(self.orig,.65);b=physical_scene(self.orig,1.35)
        self.assertTrue(np.array_equal(a.velocity,self.orig.velocity))
        self.assertTrue(np.array_equal(b.calling,self.orig.calling))
        self.assertEqual(a.rng_state,self.orig.rng_state)
        np.testing.assert_allclose(a.pos.mean(0),b.pos.mean(0),rtol=0,atol=1e-12)

    def test_initial_sound_weights_equal_across_physical_scenes(self):
        x=physical_scene(self.orig,.65);y=physical_scene(self.orig,1.35)
        for h,scale in RANGE.items():
            expected=acoustic_kernel(self.new,scale)
            np.testing.assert_allclose(acoustic_kernel(x,scale/.65),
                                       expected,rtol=0,atol=1e-13)
            np.testing.assert_allclose(acoustic_kernel(y,scale/1.35),
                                       expected,rtol=0,atol=1e-13)

    def test_same_motor_and_calling_kernel_exactly_replays_v19(self):
        previous=v19.State(self.orig.pos,self.orig.velocity,self.orig.calling,0,self.orig.rng_state)
        for ratio in (1.,.65/1.35,1.35/.65):
            for cue in (None,10):
                a=v20.advance(self.new,45,pulse_start=cue,
                   motor_acoustic_ratio=ratio,calling_acoustic_ratio=ratio)
                b=v19.advance(previous,45,pulse_start=cue,acoustic_ratio=ratio)
                _assert_source_equal(a,b,"nonreserved_fixture")

    def test_original_v15_exactly_replayed(self):
        a=v20.advance(self.new,45,motor_acoustic_ratio=1.,calling_acoustic_ratio=1.)
        b=v15.advance(self.orig,45)
        _assert_source_equal(a,b,"original_v15")

    def test_motor_kernel_only_does_not_change_initial_call_draw(self):
        # Force one caller in an old, non-reserved fixture to make the motor force nonzero.
        call=np.zeros(N,dtype=float);call[1]=1.
        src=v20.State(self.orig.pos,self.orig.velocity,call,0,self.orig.rng_state)
        a=v20.advance(src,3,motor_acoustic_ratio=.65/1.35,calling_acoustic_ratio=1.)
        b=v20.advance(src,3,motor_acoustic_ratio=1.35/.65,calling_acoustic_ratio=1.)
        self.assertEqual(a["call_fraction"][0],b["call_fraction"][0])
        self.assertFalse(np.array_equal(a["final_state"].pos,b["final_state"].pos))

    def test_invalid_acoustic_ratio_rejected(self):
        with self.assertRaises(ValueError):
            v20.advance(self.new,2,motor_acoustic_ratio=0.)
        with self.assertRaises(ValueError):
            v20.advance(self.new,2,calling_acoustic_ratio=-1.)

    def test_binary_call_count_grid_rejection(self):
        x=np.zeros(3040);x[40]=.013
        with self.assertRaises(RuntimeError):
            call_counts(x)

    def test_exact_inclusion_exclusion_and_shapley_closure(self):
        nums={"compact_long_long":170,"compact_long_short":90,
              "compact_short_long":60,"compact_short_short":10}
        result=decompose_cell(nums,"compact")
        self.assertAlmostEqual(result["both_long_minus_both_short"],160/96000.)
        self.assertAlmostEqual(result["pathway_interaction"],30/96000.)
        self.assertAlmostEqual(result["shapley_motor"]+result["shapley_vocal"],160/96000.)

    def test_no_low_seed_stops_without_false_effect(self):
        census={int(s):1. for s in SEEDS}
        result=summarize(census,[])
        self.assertEqual(result["support_gate"],"INSUFFICIENT_LOW_SEEDS")
        self.assertIsNone(result["primary"]["mean"])

    def test_unreserved_realistic_original_source_checkpoint(self):
        seed,q,source=pre_one(44)
        self.assertEqual(seed,44)
        self.assertGreaterEqual(q,0.)
        if source is not None:
            self.assertEqual(source.completed_steps,1000)

if __name__=="__main__":
    unittest.main()
