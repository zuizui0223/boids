import tempfile
import unittest
from pathlib import Path
from validation_v191.reanalyse_signed_v188_source_artifact import (
    ORIGINAL_JSON_SHA256, EXPECTED_WINDOWS, EXPECTED_SITES,
    SourceGateError, read_exact_original, close, valid_source_receipt, require
)
class FrozenSignedOriginalData(unittest.TestCase):
    def test_frozen_original_sha_shape(self):
        self.assertEqual(len(ORIGINAL_JSON_SHA256),64)
        self.assertEqual(len(EXPECTED_SITES),13)
        self.assertEqual(EXPECTED_WINDOWS,("2018-06","2018-09","2019-06","2019-09"))
    def test_modified_fake_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"original.json"
            p.write_text('{"status":"FAKE"}')
            with self.assertRaisesRegex(SourceGateError,"SHA256_NOT_FROZEN"):
                read_exact_original(p)
    def test_reject_unverified_native_publisher_SHA(self):
        self.assertFalse(valid_source_receipt({"native_RWS_code":"vlieland.haven","native_response_SHA256":"invalid","n_real_cmNAP_timestamps":289}))
        self.assertFalse(valid_source_receipt({"native_RWS_code":"vlieland.haven","native_response_SHA256":"a"*64,"n_real_cmNAP_timestamps":199}))
        self.assertTrue(valid_source_receipt({"native_RWS_code":"vlieland.haven","native_response_SHA256":"a"*64,"n_real_cmNAP_timestamps":289}))
    def test_rounded_nine_digit_source_aggregate_tolerance(self):
        self.assertTrue(close(.072700386,.07270038))
        self.assertFalse(close(.072700386,.0726))
    def test_require_stop_is_source_scoped(self):
        with self.assertRaisesRegex(SourceGateError,"NO_RAW_BIRDS"):
            require(False,"NO_RAW_BIRDS")
if __name__=="__main__":
    unittest.main()
