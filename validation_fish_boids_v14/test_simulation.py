"""Replay, intervention-boundary, and state-recording tests for synthetic v14."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np
from scipy.spatial import ConvexHull


HERE = Path(__file__).resolve().parent
TRACE_KEYS = ("call_fraction", "hull_area", "cue")
STATE_KEYS = ("snapshot_pos", "snapshot_velocity", "snapshot_calling")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ORIGINAL = load_module(
    "simulation_v13_reference_for_v14",
    HERE.parent / "validation_fish_boids_v13" / "simulation.py",
)
SIMULATION_PATH = HERE / "simulation.py"
SIMULATE = (
    load_module("simulation_v14_under_test", SIMULATION_PATH).simulate
    if SIMULATION_PATH.is_file()
    else None
)


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(SIMULATE, "The v14 simulate API has not been implemented")
        self.simulate = SIMULATE

    def test_full_feedback_is_bitwise_v13_with_and_without_playback(self):
        # Catches changed equations, RNG consumption, or update order.
        for pulse_start in (None, 80):
            for intervention_step in (None, 120):
                with self.subTest(pulse_start=pulse_start,
                                  intervention_step=intervention_step):
                    expected = ORIGINAL.simulate(
                        seed=2, steps=300, pulse_start=pulse_start
                    )
                    actual = self.simulate(
                        seed=2, steps=300, pulse_start=pulse_start,
                        intervention_step=intervention_step,
                    )
                    self.assertEqual(
                        set(actual), set(TRACE_KEYS + STATE_KEYS + ("snapshot_steps",))
                    )
                    for key in TRACE_KEYS:
                        np.testing.assert_array_equal(actual[key], expected[key])

    def test_intervention_at_zero_matches_v13_weighted_dynamics(self):
        # Catches an ignored pathway weight or a delayed intervention boundary.
        for audio_weight, heard_weight in ((0.0, 3.0), (5.0, 0.0),
                                           (0.0, 0.0), (0.5, 1.25)):
            with self.subTest(audio_weight=audio_weight, heard_weight=heard_weight):
                expected = ORIGINAL.simulate(
                    seed=17, steps=100, pulse_start=20,
                    audio_weight=audio_weight, heard_weight=heard_weight,
                )
                actual = self.simulate(
                    seed=17, steps=100, pulse_start=20, intervention_step=0,
                    audio_weight_after=audio_weight, heard_weight_after=heard_weight,
                )
                for key in TRACE_KEYS:
                    np.testing.assert_array_equal(actual[key], expected[key])

    def test_short_run_is_exact_prefix_even_with_a_future_intervention(self):
        # Catches horizon-dependent RNG, initialization, or anticipatory intervention.
        for seed in (2, 17):
            with self.subTest(seed=seed):
                kwargs = dict(
                    seed=seed, pulse_start=80, intervention_step=200,
                    audio_weight_after=0.25, heard_weight_after=1.25,
                    snapshot_steps=(300, 175, 100, 0, 200),
                )
                long_run = self.simulate(steps=300, **kwargs)
                prefix = self.simulate(steps=175, **kwargs)
                for key in TRACE_KEYS:
                    np.testing.assert_array_equal(prefix[key], long_run[key][:175])
                np.testing.assert_array_equal(prefix["snapshot_steps"], [0, 100, 175])
                for key in STATE_KEYS:
                    np.testing.assert_array_equal(prefix[key], long_run[key][:3])

    def test_before_cut_state_and_trace_are_unchanged(self):
        # Catches changing weights before t == intervention_step or losing state.
        snapshots = (0, 80, 120, 121, 300)
        baseline = self.simulate(
            seed=2, steps=300, pulse_start=80, snapshot_steps=snapshots
        )
        for audio_weight, heard_weight in ((0.0, 3.0), (5.0, 0.0), (0.0, 0.0)):
            with self.subTest(audio_weight=audio_weight, heard_weight=heard_weight):
                intervention = self.simulate(
                    seed=2, steps=300, pulse_start=80, intervention_step=120,
                    audio_weight_after=audio_weight, heard_weight_after=heard_weight,
                    snapshot_steps=snapshots,
                )
                for key in TRACE_KEYS:
                    np.testing.assert_array_equal(
                        intervention[key][:120], baseline[key][:120]
                    )
                for key in STATE_KEYS:
                    np.testing.assert_array_equal(intervention[key][:3], baseline[key][:3])
                if audio_weight == 0.0:
                    self.assertFalse(np.array_equal(
                        intervention["snapshot_velocity"][3],
                        baseline["snapshot_velocity"][3],
                    ))

    def test_no_intervention_and_beyond_horizon_leave_afterweights_unused(self):
        # Catches applying valid afterweights when no intervention is scheduled yet.
        baseline = self.simulate(seed=17, steps=150, pulse_start=40, snapshot_steps=(0, 150))
        for intervention_step in (None, 150, 300):
            with self.subTest(intervention_step=intervention_step):
                actual = self.simulate(
                    seed=17, steps=150, pulse_start=40,
                    intervention_step=intervention_step,
                    audio_weight_after=0.125, heard_weight_after=12.5,
                    snapshot_steps=(0, 150),
                )
                for key in baseline:
                    np.testing.assert_array_equal(actual[key], baseline[key])

    def test_removing_hearing_at_pulse_end_immediately_gives_common_bernoulli_calls(self):
        # Catches residual hearing, extra RNG draws, or a one-step late removal.
        seed, steps, n, pulse_start, pulse_end = 2, 300, 32, 80, 120
        rng = np.random.default_rng(seed)
        rng.normal(size=(n, 2))
        rng.uniform(-np.pi, np.pi, n)
        rng.binomial(1, 0.08, n)
        draws = rng.random((steps, n))
        baseline_probability = 0.057324175898868755  # logistic(-2.8)
        expected_calling = (draws < baseline_probability).astype(float)
        expected_fraction = expected_calling.mean(axis=1)

        for audio_weight in (5.0, 0.0):
            with self.subTest(audio_weight=audio_weight):
                kwargs = dict(
                    seed=seed, steps=steps, n=n, intervention_step=pulse_end,
                    audio_weight_after=audio_weight, heard_weight_after=0.0,
                    snapshot_steps=(pulse_end, pulse_end + 1, steps),
                )
                control = self.simulate(pulse_start=None, **kwargs)
                pulse = self.simulate(pulse_start=pulse_start, **kwargs)
                for result in (control, pulse):
                    np.testing.assert_array_equal(
                        result["call_fraction"][pulse_end:], expected_fraction[pulse_end:]
                    )
                    np.testing.assert_array_equal(
                        result["snapshot_calling"][1], expected_calling[pulse_end]
                    )
                np.testing.assert_array_equal(
                    pulse["call_fraction"][pulse_end:], control["call_fraction"][pulse_end:]
                )
                self.assertFalse(np.array_equal(
                    pulse["snapshot_pos"][0], control["snapshot_pos"][0]
                ))
                self.assertFalse(np.array_equal(
                    pulse["snapshot_pos"][-1], control["snapshot_pos"][-1]
                ))

    def test_snapshots_are_sorted_completed_update_states_with_float64_data(self):
        # Catches off-by-one snapshots, aliased state, wrong shapes, and lost n.
        seed, n, steps = 17, 7, 50
        result = self.simulate(
            seed=seed, n=n, steps=steps, pulse_start=5, intervention_step=25,
            audio_weight_after=0.5, heard_weight_after=1.25,
            snapshot_steps=(50, 1, 75, 0, 25),
        )
        np.testing.assert_array_equal(result["snapshot_steps"], [0, 1, 25, 50])
        self.assertTrue(np.issubdtype(result["snapshot_steps"].dtype, np.integer))
        self.assertEqual(result["snapshot_pos"].shape, (4, n, 2))
        self.assertEqual(result["snapshot_velocity"].shape, (4, n, 2))
        self.assertEqual(result["snapshot_calling"].shape, (4, n))
        for key in TRACE_KEYS:
            self.assertEqual(result[key].shape, (steps,))
        for key in TRACE_KEYS + STATE_KEYS:
            self.assertEqual(result[key].dtype, np.dtype("float64"))
            self.assertTrue(np.all(np.isfinite(result[key])))

        rng = np.random.default_rng(seed)
        initial_pos = rng.normal(size=(n, 2)) * 4.0
        headings = rng.uniform(-np.pi, np.pi, n)
        initial_velocity = np.stack((np.cos(headings), np.sin(headings)), 1) * 1.7
        initial_calling = rng.binomial(1, 0.08, n).astype(float)
        np.testing.assert_array_equal(result["snapshot_pos"][0], initial_pos)
        np.testing.assert_array_equal(result["snapshot_velocity"][0], initial_velocity)
        np.testing.assert_array_equal(result["snapshot_calling"][0], initial_calling)
        np.testing.assert_array_equal(
            result["snapshot_pos"][1], initial_pos + 0.06 * result["snapshot_velocity"][1]
        )
        for index, completed_steps in enumerate(result["snapshot_steps"][1:], start=1):
            self.assertEqual(
                float(result["snapshot_calling"][index].mean()),
                result["call_fraction"][completed_steps - 1],
            )
            self.assertEqual(
                float(ConvexHull(result["snapshot_pos"][index]).volume),
                result["hull_area"][completed_steps - 1],
            )

    def test_default_snapshots_outside_short_horizon_are_filtered(self):
        # Catches treating the long-run default snapshot schedule as an error.
        result = self.simulate(seed=2, steps=300)
        self.assertEqual(result["snapshot_steps"].shape, (0,))
        self.assertEqual(result["snapshot_pos"].shape, (0, 32, 2))
        self.assertEqual(result["snapshot_velocity"].shape, (0, 32, 2))
        self.assertEqual(result["snapshot_calling"].shape, (0, 32))

    def test_pulse_interval_is_half_open_and_clipped_to_run(self):
        # Catches cue endpoint changes and preserves the v13 minimum n of three.
        cases = (
            (None, 40, [0.0, 0.0, 0.0, 0.0, 0.0]),
            (0, 2, [0.8, 0.8, 0.0, 0.0, 0.0]),
            (3, 40, [0.0, 0.0, 0.0, 0.8, 0.8]),
            (5, 40, [0.0, 0.0, 0.0, 0.0, 0.0]),
        )
        for pulse_start, duration, expected in cases:
            with self.subTest(pulse_start=pulse_start, duration=duration):
                result = self.simulate(
                    seed=2, steps=5, n=3,
                    pulse_start=pulse_start, pulse_duration=duration,
                )
                np.testing.assert_array_equal(result["cue"], expected)
                self.assertTrue(np.all(result["hull_area"] > 0.0))

    def test_invalid_integer_inputs_are_rejected(self):
        # Catches implicit truncation, invalid hull sizes, and invalid schedules.
        cases = {
            "seed": (-1, 1.5, True),
            "steps": (0, -1, 1.5, True),
            "n": (0, 2, 3.5, True),
            "pulse_start": (-1, 1.5, True),
            "pulse_duration": (0, -1, 1.5, True),
            "intervention_step": (-1, 1.5, True),
        }
        for key, values in cases.items():
            for value in values:
                with self.subTest(parameter=key, value=value):
                    kwargs = {"seed": 2, "steps": 5}
                    kwargs[key] = value
                    with self.assertRaisesRegex(ValueError, key):
                        self.simulate(**kwargs)

    def test_invalid_afterweights_are_rejected_even_without_an_intervention(self):
        # Catches validation deferred until an intervention is actually reached.
        for key in ("audio_weight_after", "heard_weight_after"):
            for value in (-0.1, np.nan, np.inf, -np.inf, None, "3", 1j):
                for intervention_step in (None, 10):
                    with self.subTest(parameter=key, value=value,
                                      intervention_step=intervention_step):
                        kwargs = {"seed": 2, "steps": 5,
                                  "intervention_step": intervention_step, key: value}
                        with self.assertRaisesRegex(ValueError, key):
                            self.simulate(**kwargs)

    def test_invalid_snapshot_entries_are_rejected_before_horizon_filtering(self):
        # Catches invalid entries silently removed because they exceed the horizon.
        cases = ((-1,), (1.0,), (True,), (0, 0), (100, 100), (100.5,), None)
        for snapshot_steps in cases:
            with self.subTest(snapshot_steps=snapshot_steps):
                with self.assertRaisesRegex(ValueError, "snapshot_steps"):
                    self.simulate(seed=2, steps=5, snapshot_steps=snapshot_steps)


if __name__ == "__main__":
    unittest.main()
