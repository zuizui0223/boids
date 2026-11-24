"""Synthetic v15 restart/transplant fixtures; never use reserved audit seeds."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

import numpy as np
from scipy.spatial import ConvexHull


HERE = Path(__file__).resolve().parent
TRACE_KEYS = ("call_fraction", "hull_area", "cue")
SNAPSHOT_KEYS = ("snapshot_pos", "snapshot_velocity", "snapshot_calling")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REFERENCE = load_module(
    "v14_reference_for_v15_simulation",
    HERE.parent / "validation_fish_boids_v14" / "simulation.py",
)
SIMULATION = (
    load_module("v15_simulation_under_test", HERE / "simulation.py")
    if (HERE / "simulation.py").is_file() else None
)


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(SIMULATION, "The v15 state/restart API is not implemented")
        self.sim = SIMULATION

    def assert_state_equal(self, actual, expected):
        for name in ("pos", "velocity", "calling"):
            np.testing.assert_array_equal(getattr(actual, name), getattr(expected, name))
        self.assertEqual(actual.completed_steps, expected.completed_steps)
        self.assertEqual(actual.rng_state, expected.rng_state)

    def state_kwargs(self):
        return dict(
            pos=np.array([[-2., 0.], [2., 0.], [0., 3.]]),
            velocity=np.array([[1., 0.], [0., 1.], [-1., 0.]]),
            calling=np.array([0., 1., 0.]),
            completed_steps=7,
            rng_state=deepcopy(np.random.default_rng(43).bit_generator.state),
        )

    def paired_sources(self):
        initial = self.sim.initialize(2)
        none = self.sim.advance(initial, 120)["final_state"]
        pulse = self.sim.advance(initial, 120, pulse_start=80)["final_state"]
        return none, pulse

    def test_initialization_matches_known_binomial_fixture_and_v14_state(self):
        # Replacing binomial with a uniform threshold, reordering draws, or
        # consuming an extra draw changes this independently known fixture.
        state = self.sim.initialize(2, n=7)
        expected = REFERENCE.simulate(2, n=7, steps=1, snapshot_steps=(0,))
        for field, key in zip(("pos", "velocity", "calling"), SNAPSHOT_KEYS):
            np.testing.assert_array_equal(getattr(state, field), expected[key][0])
        np.testing.assert_array_equal(state.calling, [0., 0., 0., 0., 1., 0., 0.])
        rng = np.random.default_rng(2)
        rng.normal(size=(7, 2))
        rng.uniform(-np.pi, np.pi, 7)
        rng.binomial(1, .08, 7)
        self.assertEqual(state.rng_state, rng.bit_generator.state)
        self.assertEqual(state.completed_steps, 0)

    def test_uninterrupted_replay_is_bitwise_v14(self):
        # Catches any changed equation, identity/order, initialization, or draw.
        schedule = (0, 1000, 1040, 1041, 1240, 1280)
        for seed, n in ((2, 32), (17, 7)):
            for pulse_start in (None, 1000):
                with self.subTest(seed=seed, n=n, pulse_start=pulse_start):
                    expected = REFERENCE.simulate(
                        seed, steps=1280, n=n, pulse_start=pulse_start,
                        snapshot_steps=schedule,
                    )
                    actual = self.sim.advance(
                        self.sim.initialize(seed, n=n), 1280,
                        pulse_start=pulse_start, snapshot_steps=schedule,
                    )
                    self.assertEqual(
                        set(actual), set(TRACE_KEYS + SNAPSHOT_KEYS +
                                         ("snapshot_steps", "final_state")),
                    )
                    for key in TRACE_KEYS + SNAPSHOT_KEYS + ("snapshot_steps",):
                        np.testing.assert_array_equal(actual[key], expected[key])
                    final = actual["final_state"]
                    self.assertEqual(final.completed_steps, 1280)
                    for field, key in zip(("pos", "velocity", "calling"), SNAPSHOT_KEYS):
                        np.testing.assert_array_equal(getattr(final, field), expected[key][-1])

    def test_split_replay_keeps_absolute_pulse_time_and_rng_state(self):
        # An accidental reseed, relative cue clock, lost RNG cache, or off-by-one
        # resume changes at least one trace, state, or next random draw.
        initial = self.sim.initialize(17, n=7)
        whole = self.sim.advance(initial, 150, pulse_start=80, snapshot_steps=(70, 95, 120, 150))
        state = initial
        pieces = []
        for stop in (70, 95, 120, 150):
            piece = self.sim.advance(state, stop, pulse_start=80, snapshot_steps=(stop,))
            pieces.append(piece)
            state = piece["final_state"]
        for key in TRACE_KEYS:
            np.testing.assert_array_equal(np.concatenate([part[key] for part in pieces]), whole[key])
        for key in SNAPSHOT_KEYS:
            np.testing.assert_array_equal(np.concatenate([part[key] for part in pieces]), whole[key])
        self.assert_state_equal(state, whole["final_state"])
        rng = np.random.default_rng(17)
        rng.normal(size=(7, 2))
        rng.uniform(-np.pi, np.pi, 7)
        rng.binomial(1, .08, 7)
        rng.random((150, 7))
        self.assertEqual(state.rng_state, rng.bit_generator.state)

    def test_restart_at_1040_matches_v14_timed_cut(self):
        # Catches cuts applied during the intact prefix or one update too late.
        for audio_weight, heard_weight in ((0., 3.), (5., 0.), (0., 0.), (.5, 1.25)):
            with self.subTest(audio_weight=audio_weight, heard_weight=heard_weight):
                expected = REFERENCE.simulate(
                    2, steps=1280, pulse_start=1000, intervention_step=1040,
                    audio_weight_after=audio_weight, heard_weight_after=heard_weight,
                    snapshot_steps=(1040, 1041, 1240, 1280),
                )
                prefix = self.sim.advance(self.sim.initialize(2), 1040, pulse_start=1000)
                actual = self.sim.advance(
                    prefix["final_state"], 1280,
                    audio_weight=audio_weight, heard_weight=heard_weight,
                    snapshot_steps=(1040, 1041, 1240, 1280),
                )
                for key in TRACE_KEYS:
                    np.testing.assert_array_equal(actual[key], expected[key][1040:])
                for key in SNAPSHOT_KEYS + ("snapshot_steps",):
                    np.testing.assert_array_equal(actual[key], expected[key])

    def test_transplant_all_eight_component_origins_keep_fish_identity(self):
        # Catches bit reversal, recentering, rotation, reordering, or reshuffling.
        none, pulse = self.paired_sources()
        self.assertEqual(none.rng_state, pulse.rng_state)
        for field in ("pos", "velocity", "calling"):
            self.assertFalse(np.array_equal(getattr(none, field), getattr(pulse, field)))
        for mask in range(8):
            with self.subTest(mask=mask):
                hybrid = self.sim.transplant(none, pulse, mask)
                for field, bit in (("pos", 4), ("velocity", 2), ("calling", 1)):
                    source = pulse if mask & bit else none
                    np.testing.assert_array_equal(getattr(hybrid, field), getattr(source, field))
                self.assertEqual(hybrid.completed_steps, 120)
                self.assertEqual(hybrid.rng_state, none.rng_state)

    def test_natural_corners_restart_their_original_histories_exactly(self):
        # Catches transplant changes even when no hybrid component is selected.
        none, pulse = self.paired_sources()
        for mask, pulse_start in ((0, None), (7, 80)):
            with self.subTest(mask=mask):
                original = REFERENCE.simulate(
                    2, steps=200, pulse_start=pulse_start, snapshot_steps=(120, 121, 200),
                )
                resumed = self.sim.advance(
                    self.sim.transplant(none, pulse, mask), 200,
                    snapshot_steps=(120, 121, 200),
                )
                for key in TRACE_KEYS:
                    np.testing.assert_array_equal(resumed[key], original[key][120:])
                for key in SNAPSHOT_KEYS:
                    np.testing.assert_array_equal(resumed[key], original[key])

    def test_first_resumed_calls_are_independent_of_velocity_provenance(self):
        # Recomputing perceived sound after movement makes calls depend on V.
        none, pulse = self.paired_sources()
        self.assertFalse(np.array_equal(none.velocity, pulse.velocity))
        for mask in (0, 1, 4, 5):
            with self.subTest(fixed_xc=mask):
                arms = [self.sim.advance(self.sim.transplant(none, pulse, m), 121,
                                         snapshot_steps=(121,)) for m in (mask, mask | 2)]
                np.testing.assert_array_equal(arms[0]["snapshot_calling"], arms[1]["snapshot_calling"])

    def test_motor_cut_motion_is_independent_of_calling_provenance(self):
        # A residual acoustic motor term would change X/V with changed C.
        none, pulse = self.paired_sources()
        self.assertFalse(np.array_equal(none.calling, pulse.calling))
        for mask in (0, 2, 4, 6):
            with self.subTest(fixed_xv=mask):
                arms = [self.sim.advance(self.sim.transplant(none, pulse, m), 160,
                                         audio_weight=0., snapshot_steps=(121, 160))
                        for m in (mask, mask | 1)]
                for key in ("hull_area", "snapshot_pos", "snapshot_velocity"):
                    np.testing.assert_array_equal(arms[0][key], arms[1][key])
                self.assertEqual(arms[0]["final_state"].rng_state, arms[1]["final_state"].rng_state)

    def test_state_constructor_deep_copies_arrays_and_nested_rng(self):
        # Retaining any caller-owned array or nested RNG dictionary changes state.
        values = self.state_kwargs()
        expected = deepcopy(values)
        state = self.sim.State(**values)
        for name in ("pos", "velocity", "calling"):
            self.assertEqual(getattr(state, name).dtype, np.dtype("float64"))
            values[name][...] = 99.
            np.testing.assert_array_equal(getattr(state, name), expected[name])
        values["rng_state"]["state"]["state"] = 0
        self.assertEqual(state.rng_state, expected["rng_state"])

    def test_advance_never_mutates_or_aliases_input_or_its_snapshots(self):
        # In-place update of input arrays or sharing final/snapshot buffers is a bug.
        state = self.sim.initialize(43, n=7)
        saved = self.sim.State(state.pos, state.velocity, state.calling,
                               state.completed_steps, state.rng_state)
        result = self.sim.advance(state, 5, snapshot_steps=(0, 1, 5))
        self.assert_state_equal(state, saved)
        final_before = deepcopy(result["final_state"].__dict__)
        for key in SNAPSHOT_KEYS:
            result[key][...] = 99.
        for field in ("pos", "velocity", "calling"):
            np.testing.assert_array_equal(getattr(result["final_state"], field), final_before[field])
            self.assertFalse(np.shares_memory(getattr(result["final_state"], field), getattr(state, field)))
        result["final_state"].rng_state["state"]["state"] = 0
        self.assert_state_equal(state, saved)

    def test_transplant_never_aliases_sources_or_other_corners(self):
        # Two corners sharing selected components would contaminate later arms.
        none, pulse = self.paired_sources()
        saved_none, saved_pulse = deepcopy(none.__dict__), deepcopy(pulse.__dict__)
        corners = [self.sim.transplant(none, pulse, mask) for mask in range(8)]
        untouched = [deepcopy(state.__dict__) for state in corners]
        for index, corner in enumerate(corners):
            for field in ("pos", "velocity", "calling"):
                for other in (none, pulse, *corners[:index], *corners[index + 1:]):
                    self.assertFalse(np.shares_memory(getattr(corner, field), getattr(other, field)))
            corner.pos[0, 0] = 99.
            corner.velocity[0, 0] = 99.
            corner.calling[0] = 99.
            corner.rng_state["state"]["state"] = 0
            for other_index in range(index + 1, 8):
                for field in ("pos", "velocity", "calling"):
                    np.testing.assert_array_equal(getattr(corners[other_index], field), untouched[other_index][field])
                self.assertEqual(corners[other_index].rng_state, untouched[other_index]["rng_state"])
        for source, saved in ((none, saved_none), (pulse, saved_pulse)):
            for field in ("pos", "velocity", "calling"):
                np.testing.assert_array_equal(getattr(source, field), saved[field])
            self.assertEqual(source.rng_state, saved["rng_state"])

    def test_snapshots_include_both_absolute_boundaries_and_match_trace(self):
        # Catches relative indexing, t versus t+1 confusion, and boundary omission.
        state = self.sim.advance(self.sim.initialize(17, n=7), 7)["final_state"]
        result = self.sim.advance(state, 11, snapshot_steps=(12, 11, 8, 0, 7, 6))
        np.testing.assert_array_equal(result["snapshot_steps"], [7, 8, 11])
        self.assertTrue(np.issubdtype(result["snapshot_steps"].dtype, np.integer))
        for key in TRACE_KEYS:
            self.assertEqual(result[key].shape, (4,))
        for field, key in zip(("pos", "velocity", "calling"), SNAPSHOT_KEYS):
            np.testing.assert_array_equal(result[key][0], getattr(state, field))
            np.testing.assert_array_equal(result[key][-1], getattr(result["final_state"], field))
        for index, completed in ((1, 8), (2, 11)):
            self.assertEqual(result["snapshot_calling"][index].mean(), result["call_fraction"][completed - 8])
            self.assertEqual(ConvexHull(result["snapshot_pos"][index]).volume,
                             result["hull_area"][completed - 8])
        for key in TRACE_KEYS + SNAPSHOT_KEYS:
            self.assertEqual(result[key].dtype, np.dtype("float64"))
            self.assertTrue(np.isfinite(result[key]).all())
        self.assertTrue((result["hull_area"] > 0.).all())

    def test_zero_length_advance_preserves_state_and_rng_without_aliasing(self):
        # A forced update or rejecting stop == start breaks exact checkpoints.
        state = self.sim.State(**self.state_kwargs())
        result = self.sim.advance(state, 7, snapshot_steps=(8, 7, 0))
        for key in TRACE_KEYS:
            self.assertEqual(result[key].shape, (0,))
        np.testing.assert_array_equal(result["snapshot_steps"], [7])
        self.assert_state_equal(result["final_state"], state)
        self.assertIsNot(result["final_state"], state)
        for field, key in zip(("pos", "velocity", "calling"), SNAPSHOT_KEYS):
            np.testing.assert_array_equal(result[key][0], getattr(state, field))
            self.assertFalse(np.shares_memory(getattr(result["final_state"], field), getattr(state, field)))
        result["final_state"].rng_state["state"]["state"] = 0
        self.assertNotEqual(result["final_state"].rng_state, state.rng_state)

    def test_empty_snapshot_schedule_has_correct_shapes(self):
        # Empty schedules must not accidentally return a state or lose N.
        result = self.sim.advance(self.sim.initialize(17, n=3), 1)
        self.assertEqual(result["snapshot_steps"].shape, (0,))
        self.assertEqual(result["snapshot_pos"].shape, (0, 3, 2))
        self.assertEqual(result["snapshot_velocity"].shape, (0, 3, 2))
        self.assertEqual(result["snapshot_calling"].shape, (0, 3))

    def test_cue_interval_uses_absolute_half_open_updates(self):
        # Start/end off-by-one or treating pulse_start as relative breaks literals.
        state = self.sim.advance(self.sim.initialize(2, n=3), 7)["final_state"]
        for pulse_start, duration, expected in (
            (None, 40, [0., 0., 0., 0., 0.]),
            (6, 3, [.8, .8, 0., 0., 0.]),
            (8, 2, [0., .8, .8, 0., 0.]),
            (12, 40, [0., 0., 0., 0., 0.]),
        ):
            with self.subTest(pulse_start=pulse_start):
                result = self.sim.advance(state, 12, pulse_start=pulse_start, pulse_duration=duration)
                np.testing.assert_array_equal(result["cue"], expected)

    def test_state_rejects_shapes_that_would_broadcast_or_change_fish_identity(self):
        # Never flatten, squeeze, or broadcast a malformed state into acceptance.
        cases = {
            "pos": (np.zeros((2, 2)), np.zeros((3, 3)), np.zeros(6), np.zeros((1, 3, 2))),
            "velocity": (np.zeros((1, 2)), np.zeros(2), np.zeros((3, 1)), np.zeros((3, 2, 1))),
            "calling": (np.zeros((3, 1)), np.zeros((1, 3)), np.zeros(1), np.zeros(4)),
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, shape=value.shape):
                    kwargs = self.state_kwargs()
                    kwargs[field] = value
                    with self.assertRaisesRegex(ValueError, field):
                        self.sim.State(**kwargs)

    def test_state_rejects_nonfinite_complex_and_nonbinary_values(self):
        # NaNs, imaginary parts, and nonbinary C must fail before dynamics.
        for field in ("pos", "velocity", "calling"):
            for value in (np.nan, np.inf, -np.inf, 1j):
                with self.subTest(field=field, value=value):
                    kwargs = self.state_kwargs()
                    array = kwargs[field].astype(complex if value == 1j else float)
                    array.flat[0] = value
                    kwargs[field] = array
                    with self.assertRaisesRegex(ValueError, field):
                        self.sim.State(**kwargs)
        for value in (-1., .25, 2.):
            kwargs = self.state_kwargs()
            kwargs["calling"][0] = value
            with self.assertRaisesRegex(ValueError, "calling"):
                self.sim.State(**kwargs)

    def test_state_rejects_invalid_completed_count(self):
        # Reject floats/bools instead of silently truncating a restart clock.
        for completed in (-1, 1.5, True, "7", None):
            with self.subTest(completed=completed):
                kwargs = self.state_kwargs()
                kwargs["completed_steps"] = completed
                with self.assertRaisesRegex(ValueError, "completed_steps"):
                    self.sim.State(**kwargs)

    def test_state_rejects_non_pcg64_or_inexact_rng_schema(self):
        # NumPy's setter can ignore fields: require exact saved PCG64 state.
        valid = self.state_kwargs()["rng_state"]
        invalid = [None, [], {}, np.random.MT19937(43).state]
        for key in valid:
            candidate = deepcopy(valid)
            del candidate[key]
            invalid.append(candidate)
        candidate = deepcopy(valid)
        candidate["unexpected"] = 1
        invalid.append(candidate)
        for nested in ({"state": 3}, {"inc": 3}, {"state": 3, "inc": 3, "extra": 1}, []):
            candidate = deepcopy(valid)
            candidate["state"] = nested
            invalid.append(candidate)
        for field, values in (
            ("bit_generator", ("PCG64DXSM", "MT19937", None)),
            ("has_uint32", (-1, 2, True, 0., None)),
            ("uinteger", (-1, 2**32, True, 0., None)),
        ):
            for value in values:
                candidate = deepcopy(valid)
                candidate[field] = value
                invalid.append(candidate)
        for field, values in (
            ("state", (-1, 2**128, True, 1.5, None)),
            ("inc", (-1, 0, 2, 2**128, True, 1.5, None)),
        ):
            for value in values:
                candidate = deepcopy(valid)
                candidate["state"][field] = value
                invalid.append(candidate)
        for candidate in invalid:
            with self.subTest(rng_state=candidate):
                kwargs = self.state_kwargs()
                kwargs["rng_state"] = candidate
                with self.assertRaisesRegex(ValueError, "rng_state"):
                    self.sim.State(**kwargs)

    def test_valid_pcg64_cached_uint32_state_restarts_without_extra_draws(self):
        # Clearing has_uint32/uinteger or rebuilding from a seed loses state.
        kwargs = self.state_kwargs()
        rng = np.random.default_rng(43)
        rng.integers(0, 2**32, dtype=np.uint32)
        self.assertEqual(rng.bit_generator.state["has_uint32"], 1)
        kwargs["rng_state"] = deepcopy(rng.bit_generator.state)
        result = self.sim.advance(self.sim.State(**kwargs), 8, heard_weight=0., audio_weight=0.,
                                  snapshot_steps=(8,))
        expected_calling = (rng.random(3) < .057324175898868755).astype(float)
        np.testing.assert_array_equal(result["snapshot_calling"][0], expected_calling)
        self.assertEqual(result["final_state"].rng_state, rng.bit_generator.state)

    def test_advance_revalidates_mutated_state_and_rejects_non_state(self):
        # Public state attributes can change; continuation must not trust old admission.
        with self.assertRaisesRegex(ValueError, "state"):
            self.sim.advance(self.state_kwargs(), 8)
        mutations = (("calling", np.array([0., .5, 0.])), ("velocity", np.zeros((1, 2))),
                     ("completed_steps", -1), ("rng_state", {}))
        for field, value in mutations:
            with self.subTest(field=field):
                state = self.sim.State(**self.state_kwargs())
                setattr(state, field, value)
                with self.assertRaises(ValueError):
                    self.sim.advance(state, 8)

    def test_transplant_rejects_unequal_times_shapes_rng_and_invalid_masks(self):
        # Different times, fish sets, or streams cannot be paired legitimately.
        state = self.sim.State(**self.state_kwargs())
        for mask in (-1, 8, 1.5, True, "001", None):
            with self.subTest(mask=mask):
                with self.assertRaisesRegex(ValueError, "mask"):
                    self.sim.transplant(state, state, mask)
        different_time = self.sim.State(**{**self.state_kwargs(), "completed_steps": 8})
        different_n = self.sim.initialize(43, n=4)
        different_n.completed_steps = 7
        different_rng = self.sim.State(**{**self.state_kwargs(),
                                         "rng_state": np.random.default_rng(17).bit_generator.state})
        for other, message in ((different_time, "completed_steps"), (different_n, "shape"),
                               (different_rng, "rng_state")):
            with self.subTest(mismatch=message):
                with self.assertRaisesRegex(ValueError, message):
                    self.sim.transplant(state, other, 0)
        malformed = self.sim.State(**self.state_kwargs())
        malformed.calling = np.zeros((3, 1))
        with self.assertRaisesRegex(ValueError, "calling"):
            self.sim.transplant(state, malformed, 0)

    def test_initialization_rejects_invalid_seed_and_fish_count(self):
        # Do not silently coerce seed/fish counts or allow fewer than three fish.
        for seed in (-1, 1.5, True, None):
            with self.subTest(seed=seed):
                with self.assertRaisesRegex(ValueError, "seed"):
                    self.sim.initialize(seed)
        for n in (0, 2, 3.5, True, None):
            with self.subTest(n=n):
                with self.assertRaisesRegex(ValueError, "n"):
                    self.sim.initialize(2, n=n)

    def test_advance_rejects_invalid_times_weights_and_snapshots(self):
        # Validate even unused pulse/weight options and excluded snapshot entries.
        state = self.sim.State(**self.state_kwargs())
        cases = {
            "stop_step": (6, -1, 8.5, True, None),
            "pulse_start": (-1, 1.5, True),
            "pulse_duration": (0, -1, 1.5, True, None),
            "audio_weight": (-.1, np.nan, np.inf, -np.inf, None, "3", 1j),
            "heard_weight": (-.1, np.nan, np.inf, -np.inf, None, "3", 1j),
            "snapshot_steps": ((-1,), (1.,), (True,), (7, 7), (100, 100), (100.5,), None),
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    kwargs = {"stop_step": 8, field: value}
                    with self.assertRaisesRegex(ValueError, field):
                        self.sim.advance(state, **kwargs)


if __name__ == "__main__":
    unittest.main()
