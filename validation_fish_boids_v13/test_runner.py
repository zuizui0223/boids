"""A malformed trace must never replace an already valid saved result."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
import run_audit


class TraceOutputTests(unittest.TestCase):
    def fixture(self):
        arrays = {}
        for mechanism in run_audit.MECHANISMS:
            for timing in ('none', 'warmup') + (('early',) if mechanism == 'full' else ()):
                for metric in ('call_fraction', 'hull_area'):
                    value = .5 if metric == 'call_fraction' else 1.
                    arrays[f'{mechanism}__{timing}__{metric}'] = np.full((24, 4000), value)
        return arrays

    def test_invalid_shape_preserves_previous_file(self):
        self.assertTrue(hasattr(run_audit, 'save_trace_archive'), 'Missing validated atomic output')
        arrays = self.fixture()
        arrays['full__none__call_fraction'] = np.zeros((24, 4001))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'traces.npz'
            path.write_bytes(b'previous result')
            with self.assertRaises(ValueError):
                run_audit.save_trace_archive(path, arrays)
            self.assertEqual(path.read_bytes(), b'previous result')

    def test_trace_schema_and_physical_values_rejected(self):
        self.assertTrue(hasattr(run_audit, 'validate_trace_arrays'), 'Missing trace validation')
        arrays = self.fixture()
        for bad in ('extra', 'missing', 'nan', 'negative_area', 'invalid_probability'):
            with self.subTest(bad=bad):
                altered = arrays.copy()
                if bad == 'extra':
                    altered['extra'] = np.zeros((24, 4000))
                elif bad == 'missing':
                    del altered['full__none__call_fraction']
                else:
                    metric = 'hull_area' if bad == 'negative_area' else 'call_fraction'
                    value = {'nan': np.nan, 'negative_area': -1., 'invalid_probability': 1.1}[bad]
                    altered[f'full__none__{metric}'] = np.full((24, 4000), value)
                with self.assertRaises(ValueError):
                    run_audit.validate_trace_arrays(altered)

    def test_valid_output_roundtrips_with_seed_identity(self):
        self.assertTrue(hasattr(run_audit, 'save_trace_archive'), 'Missing validated atomic output')
        arrays = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'traces.npz'
            run_audit.save_trace_archive(path, arrays)
            with np.load(path, allow_pickle=False) as archive:
                np.testing.assert_array_equal(archive['seeds'], np.arange(1000, 1024))
                np.testing.assert_array_equal(archive['full__warmup__hull_area'], arrays['full__warmup__hull_area'])
            self.assertEqual(len(list(Path(directory).iterdir())), 1)


if __name__ == '__main__':
    unittest.main()
