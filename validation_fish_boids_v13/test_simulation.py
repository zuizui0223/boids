"""Replay and causal-control tests for the synthetic v13 extension."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ORIGINAL = load_module(
    "acoustic_feedback_v12_reference",
    HERE.parent / "validation_fish_boids_v12" / "acoustic_feedback.py",
)
SIMULATION_PATH = HERE / "simulation.py"
SIMULATE = (
    load_module("simulation_v13_under_test", SIMULATION_PATH).simulate
    if SIMULATION_PATH.is_file()
    else None
)


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(SIMULATE, "The simulate API has not been implemented")
        self.simulate = SIMULATE

    def test_original_v12_replay_seed_2_with_and_without_playback(self):
        # Catches changes to equations, update order, initialization, or RNG use.
        for playback in (False, True):
            with self.subTest(playback=playback):
                original = ORIGINAL.microscopic(seed=2, playback=playback, steps=300)
                actual = self.simulate(
                    seed=2, steps=300, pulse_start=80 if playback else None
                )
                self.assertEqual(set(actual), {"call_fraction", "hull_area", "cue"})
                for key in actual:
                    expected = np.array([row[key] for row in original])
                    np.testing.assert_array_equal(actual[key], expected)

    def test_defaults_return_4000_steps_with_pulse_at_1000_to_1040(self):
        # Catches wrong defaults, output shape, or cue amplitude and endpoints.
        result = self.simulate(seed=2)
        self.assertEqual(set(result), {"call_fraction", "hull_area", "cue"})
        for values in result.values():
            self.assertIsInstance(values, np.ndarray)
            self.assertEqual(values.shape, (4000,))
            self.assertTrue(np.all(np.isfinite(values)))
        self.assertTrue(np.all(result["hull_area"] > 0.0))
        self.assertTrue(np.all((result["call_fraction"] >= 0.0)
                               & (result["call_fraction"] <= 1.0)))
        expected_cue = np.zeros(4000)
        expected_cue[1000:1040] = 0.8
        np.testing.assert_array_equal(result["cue"], expected_cue)

    def test_zero_audio_motor_keeps_geometry_identical_with_hearing_active(self):
        # Any direct cue-to-movement path would violate this causal control.
        control = self.simulate(
            seed=2, steps=240, pulse_start=None, audio_weight=0.0, heard_weight=3.0
        )
        pulse = self.simulate(
            seed=2, steps=240, pulse_start=40, audio_weight=0.0, heard_weight=3.0
        )
        np.testing.assert_array_equal(pulse["hull_area"], control["hull_area"])
        self.assertTrue(np.any(pulse["call_fraction"][40:80]
                               != control["call_fraction"][40:80]))

    def test_zero_hearing_uses_same_random_draws_and_resets_calls_at_pulse_end(self):
        # Independent Bernoulli thresholds catch shifted RNG draws in any arm.
        steps, n, pulse_start, pulse_end = 240, 32, 40, 80
        control = self.simulate(
            seed=2, steps=steps, pulse_start=None, heard_weight=0.0
        )
        pulse = self.simulate(
            seed=2, steps=steps, pulse_start=pulse_start, heard_weight=0.0
        )
        rng = np.random.default_rng(2)
        rng.normal(size=(n, 2))
        rng.uniform(-np.pi, np.pi, n)
        rng.binomial(1, 0.08, n)
        draws = rng.random((steps, n))
        baseline_probability = 0.057324175898868755  # logistic(-2.8)
        playback_probability = 0.11920292202211755  # logistic(-2.0)
        probabilities = np.full(steps, baseline_probability)
        probabilities[pulse_start:pulse_end] = playback_probability
        expected_control = (draws < baseline_probability).mean(axis=1)
        expected_pulse = (draws < probabilities[:, None]).mean(axis=1)
        np.testing.assert_array_equal(control["call_fraction"], expected_control)
        np.testing.assert_array_equal(pulse["call_fraction"], expected_pulse)
        np.testing.assert_array_equal(
            pulse["call_fraction"][pulse_end:], control["call_fraction"][pulse_end:]
        )

    def test_both_weights_zero_preserves_geometry_and_calls_outside_pulse(self):
        # Catches residual feedback when both acoustic pathways are disabled.
        control = self.simulate(
            seed=2, steps=240, pulse_start=None, audio_weight=0.0, heard_weight=0.0
        )
        pulse = self.simulate(
            seed=2, steps=240, pulse_start=40, audio_weight=0.0, heard_weight=0.0
        )
        np.testing.assert_array_equal(pulse["hull_area"], control["hull_area"])
        outside = np.r_[0:40, 80:240]
        np.testing.assert_array_equal(
            pulse["call_fraction"][outside], control["call_fraction"][outside]
        )

    def test_future_pulse_cannot_change_pre_onset_values(self):
        # Catches schedule-dependent initialization, RNG use, or anticipation.
        control = self.simulate(seed=2, steps=160, pulse_start=None)
        pulse = self.simulate(seed=2, steps=160, pulse_start=100)
        future = self.simulate(seed=2, steps=160, pulse_start=200)
        for key in control:
            np.testing.assert_array_equal(pulse[key][:100], control[key][:100])
            np.testing.assert_array_equal(future[key], control[key])

    def test_pulse_interval_is_half_open_and_clipped_to_run(self):
        # Catches off-by-one pulse endpoints and rejects an unnecessary n > 3 limit.
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
        # Catches implicit truncation, impossible hull sizes, and invalid schedules.
        cases = {
            "seed": (-1, 1.5, True),
            "steps": (0, -1, 1.5, True),
            "n": (0, 2, 3.5, True),
            "pulse_start": (-1, 1.5, True),
            "pulse_duration": (0, -1, 1.5, True),
        }
        for key, values in cases.items():
            for value in values:
                with self.subTest(parameter=key, value=value):
                    kwargs = {"seed": 2, "steps": 5}
                    kwargs[key] = value
                    with self.assertRaisesRegex(ValueError, key):
                        self.simulate(**kwargs)


if __name__ == "__main__":
    unittest.main()
