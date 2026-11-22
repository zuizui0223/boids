"""Output admission and paired-history invariants, without running a sweep."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import numpy as np


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name('run_audit.py')
        cls.module = None
        if path.exists():
            spec = importlib.util.spec_from_file_location('v14_runner_test_target', path)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def api(self, name):
        self.assertIsNotNone(self.module, 'v14 runner is not implemented')
        return getattr(self.module, name)

    def valid_arrays(self):
        arrays = {}
        for mechanism in ('intact', 'motor_cut', 'hearing_cut', 'both_cut'):
            for timing in ('none', 'pulse'):
                prefix = mechanism + '__' + timing + '__'
                cue = np.zeros(16000)
                if timing == 'pulse':
                    cue[1000:1040] = .8
                arrays[prefix + 'call_fraction'] = np.broadcast_to(0., (24, 16000))
                arrays[prefix + 'hull_area'] = np.broadcast_to(1., (24, 16000))
                arrays[prefix + 'cue'] = np.broadcast_to(cue, (24, 16000))
                arrays[prefix + 'snapshot_pos'] = np.broadcast_to(0., (24, 4, 32, 2))
                arrays[prefix + 'snapshot_velocity'] = np.broadcast_to(0., (24, 4, 32, 2))
                arrays[prefix + 'snapshot_calling'] = np.broadcast_to(0., (24, 4, 32))
        return arrays

    def test_wrong_shape_nonfinite_and_nonbinary_snapshots_are_rejected(self):
        validate = self.api('validate_trace_arrays')
        arrays = self.valid_arrays()
        validate(arrays)
        for key, value in [
            ('intact__none__call_fraction', np.zeros((24, 15999))),
            ('intact__none__hull_area', np.broadcast_to(np.nan, (24, 16000))),
            ('intact__none__snapshot_calling', np.broadcast_to(.5, (24, 4, 32))),
            ('intact__none__call_fraction', np.broadcast_to(1.1, (24, 16000))),
        ]:
            bad = dict(arrays)
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(bad)
        bad = dict(arrays)
        del bad['both_cut__pulse__hull_area']
        with self.assertRaises(ValueError):
            validate(bad)

    def test_invalid_save_preserves_existing_archive(self):
        save = self.api('save_trace_archive')
        arrays = self.valid_arrays()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'traces.npz'
            save(path, arrays)
            original = path.read_bytes()
            bad = dict(arrays)
            bad['intact__none__hull_area'] = np.zeros((24, 16000))
            with self.assertRaises(ValueError):
                save(path, bad)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ['traces.npz'])

    def test_wrong_playback_timing_is_rejected(self):
        validate = self.api('validate_trace_arrays')
        arrays = self.valid_arrays()
        arrays['intact__pulse__cue'] = np.zeros((24, 16000))
        with self.assertRaises(ValueError):
            validate(arrays)

    def test_invariant_detects_intervention_before_scheduled_cut(self):
        check = self.api('verify_invariants')
        arrays = self.valid_arrays()
        check(arrays)
        bad = dict(arrays)
        changed = np.array(bad['motor_cut__none__hull_area'])
        changed[0, 100] = 2.
        bad['motor_cut__none__hull_area'] = changed
        with self.assertRaises(AssertionError):
            check(bad)

    def test_invariant_detects_nonmatching_post_cut_iid_calls(self):
        check = self.api('verify_invariants')
        arrays = self.valid_arrays()
        changed = np.array(arrays['hearing_cut__pulse__call_fraction'])
        changed[0, 1040] = 1. / 32.
        arrays['hearing_cut__pulse__call_fraction'] = changed
        with self.assertRaises(AssertionError):
            check(arrays)


if __name__ == '__main__':
    unittest.main()
