"""Offline positive and fail-closed tests for published v8 receipt reproducibility."""
import json
import unittest
from pathlib import Path
from audit_v8_receipt import validate_and_summarize,DEFAULT_SOURCE

class TestFrozenV8Receipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=DEFAULT_SOURCE.read_bytes()
    def test_pinned_archived_receipt_passes(self):
        x=validate_and_summarize(self.data)
        self.assertEqual(x['n_paired_flights'],197)
        self.assertEqual(x['n_bird_connected_components'],10)
        self.assertEqual(x['status'],'PASS_FROZEN_RECEIPT_REPLAY_ONLY')
    def test_unmodified_primary_remains_unsupported(self):
        x=validate_and_summarize(self.data)
        self.assertEqual(x['positive_connected_groups']['actual_vs_stale'],6)
        self.assertFalse(x['reported_primary_supported'])
        self.assertGreater(x['primary_exact_one_sided_sign_p'],.05)
    def test_negative_secondary_is_not_hidden(self):
        x=validate_and_summarize(self.data)
        self.assertEqual(x['positive_connected_groups']['actual_vs_own'],9)
        self.assertLess(x['equal_connected_component_mse']['real'],x['equal_connected_component_mse']['own'])
    def test_pinned_bytes_not_replaced(self):
        amended=self.data.replace(b'EXPLORATORY_PIGEON_PAIRED_FORECAST_V8',b'EXPLORATORY_PIGEON_PAIRED_FORECAST_V0')
        with self.assertRaisesRegex(ValueError,'STOP_V8_RECEIPT_CHANGED'):
            validate_and_summarize(amended)
    def test_changed_metric_detected_without_hash_check(self):
        obj=json.loads(self.data);obj['per_component'][0]['actual_vs_stale']+=1.0
        with self.assertRaisesRegex(ValueError,'STOP_V8_AGGREGATION_MISMATCH'):
            validate_and_summarize(json.dumps(obj).encode(),check_pinned_source=False)
    def test_duplicate_flight_detected_without_hash_check(self):
        obj=json.loads(self.data);obj['per_flight'].append(obj['per_flight'][0]);obj['n_paired_flights']+=1
        with self.assertRaisesRegex(ValueError,'STOP_V8_DUPLICATED_FLIGHT'):
            validate_and_summarize(json.dumps(obj).encode(),check_pinned_source=False)

if __name__=='__main__':unittest.main()
