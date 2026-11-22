"""Known-answer checks for pairing, time boundaries and right censoring."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name('analysis.py')
        cls.module = None
        if path.exists():
            spec = importlib.util.spec_from_file_location('v14_analysis_test_target', path)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def api(self, name):
        self.assertIsNotNone(self.module, 'v14 analysis is not implemented')
        return getattr(self.module, name)

    def test_seed_paired_summary_and_known_percentiles(self):
        indices = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        r = self.api('paired_summary')([2., 4.], [3., 7.], indices)
        self.assertEqual(r['per_seed_difference'], [1., 3.])
        self.assertEqual(r['mean_difference'], 2.)
        self.assertEqual(r['median_difference'], 2.)
        np.testing.assert_allclose(r['bootstrap_95_interval'], [1.075, 2.925])
        self.assertEqual(r['no_pulse_mean'], 3.)
        self.assertEqual(r['pulse_mean'], 5.)

    def test_cut_effect_uses_its_own_no_pulse_control(self):
        r = self.api('difference_in_differences')(
            [10., 20.], [13., 25.], [1., 2.], [2., 4.])
        np.testing.assert_array_equal(r, [-2., -3.])

    def test_window_bounds_exclude_end_and_keep_seed_rows(self):
        r = self.api('window_mean')(np.array([[1, 2, 3, 90], [7, 5, 3, 80]]), 1, 3)
        np.testing.assert_array_equal(r, [2.5, 4.])

    def test_confirmation_time_is_end_of_first_qualifying_window(self):
        r = self.api('first_high_window')([0, 0, 0, 0, 1, 1, 1, 1, 1, 1], 2, 4, 1.)
        self.assertEqual(r, {'confirmation_step': 8, 'event_observed': True,
                             'censored': False, 'restricted_latency': 6})

    def test_last_window_event_is_not_censored(self):
        r = self.api('first_high_window')([0, 0, 0, 0, 0, 0, 1, 1, 1, 1], 2, 4, 1.)
        self.assertEqual(r['confirmation_step'], 10)
        self.assertTrue(r['event_observed'])
        self.assertFalse(r['censored'])
        self.assertEqual(r['restricted_latency'], 8)

    def test_absent_event_retains_censor_flag_at_same_restricted_latency(self):
        r = self.api('first_high_window')([0] * 10, 2, 4, .9)
        self.assertIsNone(r['confirmation_step'])
        self.assertFalse(r['event_observed'])
        self.assertTrue(r['censored'])
        self.assertEqual(r['restricted_latency'], 8)

    def test_pre_search_high_activity_does_not_count_as_post_search_event(self):
        r = self.api('first_high_window')([1, 1, 1, 1, 0, 0, 0, 0], 4, 3, 1.)
        self.assertFalse(r['event_observed'])

    def test_malformed_inputs_cannot_silently_change_analysis_population(self):
        summary = self.api('paired_summary')
        with self.assertRaises(ValueError):
            summary([1, 2], [1], np.array([[0, 1]]))
        with self.assertRaises(ValueError):
            summary([1, 2], [2, 3], np.array([[0, 2]]))
        with self.assertRaises(ValueError):
            summary([1, np.nan], [2, 3], np.array([[0, 1]]))
        arrival = self.api('first_high_window')
        for args in [([0, 1], 0, 3, .9), ([0, np.nan], 0, 1, .9),
                     ([0, 1.1], 0, 1, .9), ([0, 1], 0, 1, 1.1),
                     ([0, 1], False, 1, .9), ([0, 1], 0, 1.5, .9)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                arrival(*args)


if __name__ == '__main__':
    unittest.main()
