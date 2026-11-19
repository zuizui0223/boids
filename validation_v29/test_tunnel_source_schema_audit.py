"""Offline known-truth tests: structural HDF5 source gate, never wild outcomes."""
import hashlib
import tempfile
import unittest
from pathlib import Path

import h5py

from tunnel_source_schema_audit import git_blob_sha1, inspect_mat


class TunnelSourceSchemaTests(unittest.TestCase):
    def _write_synthetic(self, path: Path, include_beam: bool = True):
        with h5py.File(path, "w") as h:
            r = h.create_group("RESULTS")
            calls = r.create_group("calls")
            calls.create_dataset("tSec", data=[[0.05, 0.10, 0.20, 0.30]])
            calls.create_dataset("XYZ_sm", data=[[0.0] * 4, [1.0] * 4, [2.0] * 4])
            track = r.create_group("track")
            track.create_dataset("tSec", data=[[0.05, 0.10, 0.20, 0.30, 0.40]])
            track.create_dataset("pos_sm", data=[[0.0] * 5 for _ in range(3)])
            if include_beam:
                beam = r.create_group("beam")
                beam.create_dataset("rel_deg", data=[[1.0, 2.0, 3.0, 4.0]])
                beam.create_dataset("fitR", data=[[0.5, 0.6, 0.7, 0.8]])

    def test_structural_metadata_gate_does_not_require_reading_values(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "test.mat")
            self._write_synthetic(path)
            result = inspect_mat(path)
            self.assertTrue(result["hdf5_supported"])
            self.assertTrue(result["all_required_fields_present"])
            self.assertEqual(result["call_timestamp_array_length_from_shape"], 4)
            self.assertTrue(result["call_beam_shape_matched"])
            self.assertTrue(result["track_pos_sm_time_and_xyz_structurally_matched"])
            self.assertFalse(result["numeric_animal_or_sonar_dataset_values_accessed"])

    def test_missing_beam_is_not_silent_admission(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "test.mat")
            self._write_synthetic(path, include_beam=False)
            result = inspect_mat(path)
            self.assertFalse(result["all_required_fields_present"])
            self.assertIsNone(result["call_beam_shape_matched"])
            self.assertFalse(result["required_fields_present"]["RESULTS/beam/rel_deg"])

    def test_git_blob_hash_is_not_unprefixed_sha(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "example.bin")
            path.write_bytes(b"abc")
            self.assertEqual(git_blob_sha1(path), hashlib.sha1(b"blob 3\0abc").hexdigest())

    def test_non_hdf5_source_returns_explicit_stop(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "old.mat")
            path.write_bytes(b"MATLAB 5.0 fake header")
            result = inspect_mat(path)
            self.assertEqual(result["structure_status"], "NOT_HDF5")
            self.assertFalse(result["hdf5_supported"])


if __name__ == "__main__":
    unittest.main()
