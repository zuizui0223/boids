"""Tests protect the seed-level estimand, pairing and ablation signs."""
import unittest
import numpy as np
from analysis import paired_summary, interaction_contrast, window_mean


class SummaryTests(unittest.TestCase):
    def test_paired_seed_bootstrap_not_frames(self):
        indices = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        out = paired_summary(np.array([0., 1.]), np.array([2., 4.]), indices)
        self.assertEqual(out['n_seed_pairs'], 2)
        self.assertEqual(out['no_pulse_mean'], .5)
        self.assertEqual(out['pulse_mean'], 3.)
        self.assertEqual(out['mean_difference'], 2.5)
        # Sorted bootstrap means [2, 2.5, 2.5, 3]; linear quantiles at
        # ranks 0.075 and 2.925 are 2.0375 and 2.9625.
        self.assertEqual(out['bootstrap_95_interval'], [2.0375, 2.9625])
        self.assertEqual(out['per_seed_difference'], [2., 3.])

    def test_zero_difference_is_exact(self):
        a = np.array([3., 9., -2.])
        out = paired_summary(a, a, np.array([[0, 1, 2], [2, 2, 2]]))
        self.assertEqual(out['bootstrap_95_interval'], [0., 0.])
        self.assertEqual(out['zero_seed_pairs'], 3)

    def test_factorial_signs(self):
        out = interaction_contrast(np.array([5., 8.]), np.array([2., 3.]),
                                   np.array([1., 4.]), np.array([.5, 2.]))
        np.testing.assert_array_equal(out, [2.5, 3.])

    def test_windows_average_each_seed_separately(self):
        a = np.array([[1., 2., 3., 4.], [10., 20., 30., 40.]])
        np.testing.assert_array_equal(window_mean(a, 1, 3), [2.5, 25.])

    def test_bad_pairing_or_nonfinite_rejected(self):
        for a, b in [([1.], [1., 2.]), ([], []), ([np.nan], [1.]), ([[1.]], [[1.]])]:
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                paired_summary(np.array(a), np.array(b), np.array([[0]]))
        with self.assertRaises(ValueError):
            paired_summary(np.array([1., 2.]), np.array([1., 2.]), np.array([[0, 2]]))
        with self.assertRaises(ValueError):
            window_mean(np.zeros((2, 4)), 3, 5)


if __name__ == '__main__':
    unittest.main()
