"""Offline v21 tests. No original fish data are used or downloaded."""
import unittest

from validation_fish_boids_v21.phase_counterexample import SoundField, constructed_pair


class PhaseBlindnessTests(unittest.TestCase):
    def test_polarity_reversal_leaves_two_amplitudes_equal(self):
        x = SoundField(1 + 2j, 0.3 + 0.4j)
        y = x.counterphase()
        self.assertEqual(x.phase_blind_signature(), y.phase_blind_signature())
        self.assertEqual(x.directional_cross_term(), -y.directional_cross_term())

    def test_known_truth_identical_scalar_opposite_direction(self):
        x = SoundField(1 + 0j, 1 + 0j)
        y = SoundField(1 + 0j, -1 + 0j)
        self.assertEqual(x.phase_blind_signature(), y.phase_blind_signature())
        self.assertGreater(x.directional_cross_term(), 0)
        self.assertLess(y.directional_cross_term(), 0)

    def test_zero_sole_channel_has_no_phase_cross_term(self):
        self.assertEqual(SoundField(1, 0).directional_cross_term(), 0)
        self.assertEqual(SoundField(0, 1).directional_cross_term(), 0)

    def test_balanced_matched_pair_bound(self):
        report = constructed_pair()
        self.assertEqual(report["equal_phase_blind_pairs"], 1000)
        self.assertEqual(report["opposite_phase_cross_term_pairs"], 1000)
        self.assertEqual(report["phase_blind_balanced_accuracy_bound"], 0.5)
        self.assertEqual(report["phase_aware_constructed_label_accuracy"], 1.0)

    def test_any_seed_gives_same_logical_contradiction(self):
        for s in (0, 1, 18):
            r = constructed_pair(s, 8)
            self.assertEqual(r["phase_blind_balanced_accuracy_bound"], .5)

    def test_reject_nonfinite_and_invalid(self):
        for bad in (float("nan"), float("inf"), complex(0, float("inf")), "abc"):
            with self.assertRaises(ValueError):
                SoundField(bad, 1)
        for bad in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                constructed_pair(n_pairs=bad)


if __name__ == "__main__":
    unittest.main()
