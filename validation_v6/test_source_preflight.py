"""Known-truth structural gate tests (no animal GPS or MATLAB archive required)."""
from __future__ import annotations
import unittest
from unittest.mock import patch
from scipy.io import savemat
from io import BytesIO
import numpy as np
import source_preflight as p


class TestBatPairSourcePreflight(unittest.TestCase):
    def test_metadata_accepts_exact_pinned_identity(self):
        meta = {"id": 14097077, "doi": p.DOI, "is_public": True, "license": {"name": "CC BY 3.0 US"},
                "files": [{"id": p.EXPECTED_ID, "name": p.EXPECTED_NAME,
                          "size": p.EXPECTED_SIZE, "computed_md5": p.EXPECTED_MD5,
                          "download_url": p.DIRECT_URL, "is_link_only": False}]}
        self.assertEqual(p.verify_remote_metadata(meta)["file_id"], p.EXPECTED_ID)

    def test_metadata_rejects_wrong_file_hash(self):
        meta = {"id": 14097077, "doi": p.DOI, "is_public": True,
                "files": [{"id": p.EXPECTED_ID, "name": p.EXPECTED_NAME,
                          "size": p.EXPECTED_SIZE, "computed_md5": "bad",
                          "download_url": p.DIRECT_URL, "is_link_only": False}]}
        with self.assertRaises(ValueError): p.verify_remote_metadata(meta)

    def test_short_or_fake_bytes_fail_closed(self):
        for raw in [b"", b"x"*p.EXPECTED_SIZE, b"abc"]:
            with self.assertRaises(ValueError): p.verify_bytes(raw)

    def test_schema_reveals_shapes_only_without_value_disclosure(self):
        buf = BytesIO()
        savemat(buf, {"positions": np.array([[37.1234, 44.9999, 12.0], [99.007, -7.12, 0.04]]),
                      "pair_id": np.array([[1, 2]])})
        raw = buf.getvalue()
        with patch.object(p, "verify_bytes", return_value={"bytes": len(raw)}):
            obj = p.inspect_mat(raw)
        self.assertEqual(obj["top_level"]["positions"]["shape"], [2, 3])
        text = str(obj)
        self.assertNotIn("37.1234", text)
        self.assertNotIn("99.007", text)

    def test_no_raw_source_persisted_in_schema(self):
        buf = BytesIO()
        savemat(buf, {"reconstruction": np.array([[-9001.25]])})
        with patch.object(p, "verify_bytes", return_value={}):
            out = p.inspect_mat(buf.getvalue())
        self.assertNotIn("-9001.25", str(out))


if __name__ == "__main__":
    unittest.main()
