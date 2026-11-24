"""Admission tests for real data boundaries, not scientific outcome choices."""
from pathlib import Path
import importlib
import importlib.util
import hashlib
import json
import tempfile
import unittest
import numpy as np

NAME = 'validation_fish_boids_v15.run_audit'
runner = importlib.import_module(NAME) if importlib.util.find_spec(NAME) else None


def small_block():
    pos = np.array([[-1., -1.], [1., -1.], [1., 1.], [-1., 1.]])
    return {
        'call_fraction': np.array([.5, .5]),
        'hull_area': np.array([4., 4.]),
        'cue': np.zeros(2),
        'snapshot_pos': pos[None].copy(),
        'snapshot_velocity': np.tile([1., 0.], (1, 4, 1)),
        'snapshot_calling': np.array([[1., 1., 0., 0.]]),
    }


def full_fixture():
    """Hand-constructed valid archive layout; no scientific seeds are run."""
    a = runner.allocate_arrays()
    angle = np.arange(32) * (2 * np.pi / 32)
    pos = np.column_stack((np.cos(angle), np.sin(angle)))
    area = 16 * np.sin(np.pi / 16)
    calling = np.zeros(32)
    calling[:4] = 1
    for label in runner.SOURCE_LABELS + runner.ARMS:
        a[label+'__call_fraction'].fill(.125)
        a[label+'__hull_area'].fill(area)
        a[label+'__cue'].fill(0)
        a[label+'__snapshot_pos'][:] = pos
        a[label+'__snapshot_velocity'][:] = np.array([1., 0.])
        a[label+'__snapshot_calling'][:] = calling
    a['source__pulse__cue'][:, 1000:1040] = .8
    # Direct draws independently verify the production jump-ahead RNG check.
    # These are metadata fixtures, not simulated Boids outcome trajectories.
    for i, seed in enumerate(runner.SEEDS):
        rng = np.random.default_rng(int(seed))
        rng.normal(size=(32, 2))
        rng.uniform(-np.pi, np.pi, 32)
        rng.binomial(1, .08, 32)
        rng.random((1040, 32))
        a['split_rng_state_json'][i] = json.dumps(rng.bit_generator.state, sort_keys=True)
        rng.random((4960, 32))
        a['end_rng_state_json'][i] = json.dumps(rng.bit_generator.state, sort_keys=True)
    return a


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(runner, 'v15 runner implementation is absent')

    def validate_small(self, block):
        return runner.validate_block(block, sample_count=2, n=4,
                                     snapshot_steps=np.array([2]), offset=0,
                                     expected_cue=np.zeros(2))

    def test_worker_scalar_cannot_broadcast_into_a_valid_trace(self):
        b = small_block()
        b['call_fraction'] = .5
        with self.assertRaises(ValueError):
            self.validate_small(b)

    def test_snapshot_call_vector_must_match_trace_fraction(self):
        b = small_block()
        b['snapshot_calling'][0] = [1., 0., 0., 0.]
        with self.assertRaises(ValueError):
            self.validate_small(b)

    def test_impossible_fraction_and_nonbinary_calls_are_rejected(self):
        for field, value in [('call_fraction', .51), ('snapshot_calling', .5)]:
            with self.subTest(field=field):
                b = small_block()
                b[field].flat[0] = value
                with self.assertRaises(ValueError):
                    self.validate_small(b)

    def test_wrong_snapshot_hull_cannot_pass_with_a_positive_trace_area(self):
        b = small_block()
        b['hull_area'][:] = 5.
        with self.assertRaises(ValueError):
            self.validate_small(b)

    def test_degenerate_snapshot_is_rejected(self):
        b = small_block()
        b['snapshot_pos'][0, :, 1] = 0.
        with self.assertRaises(ValueError):
            self.validate_small(b)

    def test_extra_fields_wrong_cue_and_nonfinite_values_are_rejected(self):
        for change in ('extra', 'cue', 'nan'):
            with self.subTest(change=change):
                b = small_block()
                if change == 'extra':
                    b['unexpected'] = 1
                elif change == 'cue':
                    b['cue'][0] = .8
                else:
                    b['snapshot_velocity'][0, 0, 0] = np.nan
                with self.assertRaises(ValueError):
                    self.validate_small(b)

    def test_changed_execution_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)/'source.py'
            f.write_text('old\n')
            paths = {'source.py': f}
            before = runner.capture_source_hashes(paths)
            f.write_text('changed\n')
            with self.assertRaises(RuntimeError):
                runner.verify_source_hashes(before, paths)

    def test_bad_archive_preserves_previous_destination(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)/'full_traces.npz'
            f.write_bytes(b'previous-valid-artifact')
            with self.assertRaises(ValueError):
                runner.save_arrays(f, {'seeds': np.arange(1999, 2095)})
            self.assertEqual(f.read_bytes(), b'previous-valid-artifact')

    def test_full_fixture_roundtrips_with_seed_identity_and_receipt(self):
        a = full_fixture()
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)/'full_traces.npz'
            receipt = runner.save_arrays(f, a)
            self.assertEqual(receipt['sha256'], hashlib.sha256(f.read_bytes()).hexdigest())
            with np.load(f, allow_pickle=False) as z:
                self.assertEqual(set(z.files), set(a))
                np.testing.assert_array_equal(z['seeds'], np.arange(2000, 2096))
                np.testing.assert_array_equal(z['intact__111__call_fraction'], a['intact__111__call_fraction'])

    def test_initial_corner_snapshot_must_keep_component_provenance(self):
        a = full_fixture()
        a['intact__100__snapshot_pos'][0, 0] += [2., 1.]
        with self.assertRaises(ValueError):
            runner.validate_arrays(a)

    def test_valid_rng_from_wrong_seed_is_rejected(self):
        a = full_fixture()
        a['split_rng_state_json'][0] = a['split_rng_state_json'][1]
        with self.assertRaises(ValueError):
            runner.validate_arrays(a)

    def test_end_rng_cannot_reuse_the_split_state(self):
        a = full_fixture()
        a['end_rng_state_json'][0] = a['split_rng_state_json'][0]
        with self.assertRaises(ValueError):
            runner.validate_arrays(a)

    def test_integer_additive_calls_have_no_false_interaction_signs(self):
        a = full_fixture()
        totals = [89037, 88955, 89180, 89098, 89143, 89061, 89286, 89204]
        for mask, total in enumerate(totals):
            arm = f'intact__{mask:03b}'
            counts = np.full(3000, total // 3000, dtype=np.int64)
            counts[:total % 3000] += 1
            a[arm+'__call_fraction'][:, :3000] = counts / 32
            for j, index in ((1, 199), (2, 2999)):
                a[arm+'__snapshot_calling'][:, j] = 0
                a[arm+'__snapshot_calling'][:, j, :counts[index]] = 1
        # The empty secondary cohort must have null cohort diagnostics.
        for source in runner.SOURCE_LABELS:
            a[source+'__call_fraction'][:, 800:1000] = 31 / 32
            a[source+'__snapshot_calling'][:, 0] = 0
            a[source+'__snapshot_calling'][:, 0, :31] = 1
        runner.validate_arrays(a)
        stats, windows, effects, arrivals = runner.analyze_arrays(a)
        primary = stats['windows']['primary']['cohorts']
        exact = primary['all']['call_fraction']['decomposition']
        for name in ('XV', 'XC', 'VC', 'XVC'):
            self.assertEqual(exact['mobius'][name]['mean'], 0.)
            self.assertEqual(exact['mobius'][name]['positive'], 0)
            self.assertEqual(exact['mobius'][name]['negative'], 0)
            self.assertEqual(exact['mobius'][name]['zero'], 96)
        for name, numerator in [('X', 106), ('V', 143), ('C', -82)]:
            self.assertAlmostEqual(exact['shapley'][name]['mean'], numerator / 96000)
        empty = primary['baseline_low']['call_fraction']['decomposition']
        self.assertIsNone(empty['max_mobius_closure_error'])
        self.assertIsNone(empty['max_shapley_closure_error'])
        self.assertIsNone(empty['shapley_X_minus_C']['mean'])
        self.assertEqual(len(windows), 6912)
        self.assertEqual(len(effects), 1920)
        self.assertEqual(len(arrivals), 3456)

    def test_wrong_worker_rng_does_not_partially_assign_any_blocks(self):
        a = full_fixture()
        worker = {
            'seed': 2000,
            'blocks': {label: {f: a[label+'__'+f][0].copy() for f in runner.FIELDS}
                       for label in runner.SOURCE_LABELS + runner.ARMS},
            'split_rng_state_json': str(a['split_rng_state_json'][1]),
            'end_rng_state_json': str(a['end_rng_state_json'][0]),
            'reference_matched': True,
        }
        a['source__none__call_fraction'][0] = -123.
        with self.assertRaises(ValueError):
            runner.store_worker(a, 0, worker)
        np.testing.assert_array_equal(a['source__none__call_fraction'][0], -123.)

    def test_invalid_last_worker_block_does_not_partially_assign_earlier_blocks(self):
        a = full_fixture()
        worker = {
            'seed': 2000,
            'blocks': {label: {f: a[label+'__'+f][0].copy() for f in runner.FIELDS}
                       for label in runner.SOURCE_LABELS + runner.ARMS},
            'split_rng_state_json': str(a['split_rng_state_json'][0]),
            'end_rng_state_json': str(a['end_rng_state_json'][0]),
            'reference_matched': True,
        }
        worker['blocks']['motor_cut__111']['hull_area'] = 4.
        a['source__none__call_fraction'][0] = -123.
        with self.assertRaises(ValueError):
            runner.store_worker(a, 0, worker)
        np.testing.assert_array_equal(a['source__none__call_fraction'][0], -123.)


if __name__ == '__main__':
    unittest.main()
