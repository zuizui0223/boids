import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from validation_v134.penguin_analysis import (
    CurrentGrid, aggregate_observations, fractional_objective,
    hierarchical_score, local_week, solar_sine, week_folds,
    run_scenario,
)


class PenguinAnalysisTests(unittest.TestCase):
    def test_scenario_selection_does_not_mutate_shared_inputs(self):
        seconds = pd.to_datetime(['2019-11-23T00:00:00Z', '2019-11-23T12:00:00Z',
                                  '2019-11-26T00:00:00Z', '2019-11-26T12:00:00Z']).astype('int64').to_numpy() / 1e9
        frame = pd.DataFrame({'ID': ['a', 'b', 'a', 'b'], 'time_seconds': seconds,
                              'common_support': [True] * 4, 'static_zero_vertices': [0, 0, 0, 1],
                              'n_seconds': [900] * 4, 'depth_gt_2': [300] * 4,
                              'longitude': [0.] * 4, 'latitude': [0.] * 4})
        with patch('validation_v134.penguin_analysis.week_folds', side_effect=RuntimeError('STOP_AFTER_SELECTION')):
            with self.assertRaisesRegex(RuntimeError, 'STOP_AFTER_SELECTION'):
                run_scenario(frame, 'primary')
        self.assertTrue(frame.common_support.all())

    def test_unique_observation_denominator_and_thresholds(self):
        data = pd.DataFrame({'ID': ['a'] * 4, 'Timestamp': ['2019-11-23 00:00:00', '2019-11-23 00:00:01', '2019-11-23 00:00:01', '2019-11-23 00:00:03'],
                             'Depth_sm': [0., 3., 3., 6.], 'DR_longitude': [-63.] * 4, 'DR_latitude': [-42.] * 4})
        windows, audit = aggregate_observations(data, minimum_seconds=1)
        self.assertEqual(audit['exact_duplicate_rows_removed'], 1)
        self.assertEqual(windows.iloc[0].n_seconds, 3)
        self.assertEqual(windows.iloc[0].depth_gt_2, 2)
        self.assertEqual(windows.iloc[0].depth_gt_5, 1)
        self.assertEqual(len(windows), 1)

    def test_conflicting_duplicates_fail(self):
        data = pd.DataFrame({'ID': ['a', 'a'], 'Timestamp': ['2019-11-23', '2019-11-23'], 'Depth_sm': [0., 2.], 'DR_longitude': [-63.] * 2, 'DR_latitude': [-42.] * 2})
        with self.assertRaisesRegex(ValueError, 'CONFLICTING'):
            aggregate_observations(data, minimum_seconds=1)

    def test_missing_depth_is_not_surface_observation(self):
        data = pd.DataFrame({'ID': ['a', 'a'], 'Timestamp': ['2019-11-23', '2019-11-23 00:00:01'], 'Depth_sm': [np.nan, 3.], 'DR_longitude': [-63.] * 2, 'DR_latitude': [-42.] * 2})
        windows, audit = aggregate_observations(data, minimum_seconds=1)
        self.assertEqual(windows.iloc[0].n_seconds, 1)
        self.assertEqual(windows.iloc[0].depth_gt_2, 1)
        self.assertEqual(audit['nonfinite_required_rows_excluded'], 1)

    def test_current_origin_linear_space_and_time(self):
        # Affine field U = x + 2*y + hour; V = 1.
        xy = np.array([[0., 0.], [1., 0.], [0., 1.]])
        uv = np.zeros((3, 3, 2))
        uv[:, :, 0] = xy[:, 0, None] + 2 * xy[:, 1, None] + np.arange(3)
        uv[:, :, 1] = 1
        grid = CurrentGrid(xy, uv, origin_seconds=10000)
        speed, mask, _ = grid.sample(np.array([[.2, .3]]), np.array([11800.]), mode='linear')
        self.assertTrue(mask[0])
        self.assertAlmostEqual(speed[0], np.hypot(1.3, 1))

    def test_current_no_extrapolation_or_wrapping(self):
        xy = np.array([[0., 0.], [1., 0.], [0., 1.]])
        grid = CurrentGrid(xy, np.ones((3, 3, 2)), origin_seconds=10000)
        speed, valid, _ = grid.sample(np.array([[.2, .2], [.2, .2], [2., 2.]]), np.array([9999., 17201., 10000.]))
        self.assertFalse(valid.any())
        self.assertTrue(np.isnan(speed).all())

    def test_static_zero_node_exclusion_is_explicit(self):
        xy = np.array([[0., 0.], [1., 0.], [0., 1.]])
        uv = np.ones((3, 3, 2)); uv[0] = 0
        grid = CurrentGrid(xy, uv, origin_seconds=0)
        xy_query = np.array([[.2, .2]])
        speed, valid, zero = grid.sample(xy_query, np.array([0.]), exclude_static_zero=True)
        self.assertEqual(zero[0], 1)
        self.assertFalse(valid[0])
        self.assertTrue(grid.sample(xy_query, np.array([0.]), exclude_static_zero=False)[1][0])

    def test_whole_local_weeks_and_calendar_boundary(self):
        seconds = pd.to_datetime(['2019-11-25 02:59:59Z', '2019-11-25 03:00:00Z', '2019-11-26 12:00:00Z']).astype('int64').to_numpy() / 1e9
        weeks = local_week(seconds)
        self.assertEqual(list(weeks), ['2019-W47', '2019-W48', '2019-W48'])
        folds = week_folds(weeks)
        for _, train, test in folds:
            self.assertFalse(set(weeks[train]) & set(weeks[test]))
            self.assertFalse(np.any(train & test))

    def test_hierarchy_is_animals_then_weeks_not_rows(self):
        frame = pd.DataFrame({'ID': ['a'] * 9 + ['b', 'c'], 'week': ['w1'] * 10 + ['w2'], 'loss': [0.] * 9 + [2., 4.]})
        self.assertAlmostEqual(hierarchical_score(frame, 'loss'), 2.5)

    def test_fractional_gradient_matches_finite_difference(self):
        x = np.array([[1., -1.], [1., .5], [1., 1.]])
        y = np.array([0., .4, 1.]); w = np.ones(3) / 3; beta = np.array([.1, -.4])
        loss, grad = fractional_objective(beta, x, y, w, .01)
        numeric = []
        for j in range(2):
            step = np.zeros(2); step[j] = 1e-6
            numeric.append((fractional_objective(beta + step, x, y, w, .01)[0] - fractional_objective(beta - step, x, y, w, .01)[0]) / 2e-6)
        np.testing.assert_allclose(grad, numeric, atol=1e-8)
        self.assertTrue(np.isfinite(loss))

    def test_solar_equator_equinox_noon_midnight(self):
        seconds = pd.to_datetime(['2019-03-20T12:00:00Z', '2019-03-20T00:00:00Z']).astype('int64').to_numpy() / 1e9
        elevation_sine = solar_sine(seconds, np.zeros(2), np.zeros(2))
        self.assertGreater(elevation_sine[0], .999)
        self.assertLess(elevation_sine[1], -.999)


if __name__ == '__main__':
    unittest.main()
