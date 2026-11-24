"""A stale or mislabeled archive must fail before existing figures are touched."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import numpy as np


class PlotInputTests(unittest.TestCase):
    def test_bad_trace_receipt_preserves_existing_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            np.savez_compressed(root / 'full_traces.npz', seeds=np.arange(1000, 1024))
            metadata = {'status': 'SYNTHETIC_ONLY_NOT_FIELD_RESULT',
                'version': 'v14_post_pulse_maintenance', 'seeds': list(range(1000, 1024)),
                'individuals': 32, 'steps': 16000, 'trajectories': 192,
                'protocol_commit': 'd56e0de00d2a1bc11da434aedda00251049f0418',
                'trace_receipt': {'sha256': '0' * 64}}
            (root / 'audit_result.json').write_text(json.dumps(metadata))
            (root / 'geometry_diagnostics.json').write_text('{"records": []}')
            (root / 'figures').mkdir()
            previous = root / 'figures/maintenance_audit.png'
            previous.write_bytes(b'previous verified figure')
            done = subprocess.run([sys.executable, str(Path(__file__).with_name('plot_audit.py')),
                                   '--results', str(root)], capture_output=True, text=True)
            self.assertNotEqual(done.returncode, 0)
            self.assertIn('Trace archive checksum does not match', done.stderr)
            self.assertEqual(previous.read_bytes(), b'previous verified figure')

    def test_changed_seed_manifest_cannot_pass_with_a_correct_archive_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            np.savez_compressed(root / 'full_traces.npz', seeds=np.array([999]))
            metadata = {'status': 'SYNTHETIC_ONLY_NOT_FIELD_RESULT',
                'version': 'v14_post_pulse_maintenance', 'seeds': [999],
                'individuals': 32, 'steps': 16000, 'trajectories': 192,
                'protocol_commit': 'd56e0de00d2a1bc11da434aedda00251049f0418',
                'trace_receipt': {'sha256': hashlib.sha256((root/'full_traces.npz').read_bytes()).hexdigest()}}
            (root / 'audit_result.json').write_text(json.dumps(metadata))
            (root / 'geometry_diagnostics.json').write_text('{"records": []}')
            done = subprocess.run([sys.executable, str(Path(__file__).with_name('plot_audit.py')),
                                   '--results', str(root)], capture_output=True, text=True)
            self.assertNotEqual(done.returncode, 0)
            self.assertIn('Result metadata differs from the fixed v14 experiment', done.stderr)
            self.assertFalse((root / 'figures').exists())


if __name__ == '__main__':
    unittest.main()
