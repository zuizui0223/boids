import math
import unittest
from pathlib import Path
from source_effort_audit import audit, hypothetical_rate_ratio, four_cell_log_did

class SourceEffortTests(unittest.TestCase):
    def test_frozen_counts_and_meta_guard(self):
        out = audit(Path(__file__).resolve().parents[1])
        self.assertEqual(out["frozen_counts"]["primary_studies"], 118)
        self.assertEqual(out["joint_model_tiers"]["NO_RETAINED_CROSS"], 15)
        self.assertEqual(out["global_pooled_tide_solar_interaction"], "NOT_ESTIMATED")

    def test_unobserved_effort_can_reverse_rate(self):
        self.assertAlmostEqual(hypothetical_rate_ratio(324 / 5436), 1)
        self.assertGreater(hypothetical_rate_ratio(0.05), 1)
        self.assertLess(hypothetical_rate_ratio(0.10), 1)

    def test_known_truth_synthetic_log_did(self):
        cells = {
            "flooded|day": {"events": 10, "effort_hours": 10},
            "dry|day": {"events": 10, "effort_hours": 10},
            "flooded|night": {"events": 40, "effort_hours": 10},
            "dry|night": {"events": 10, "effort_hours": 10},
        }
        self.assertAlmostEqual(four_cell_log_did(cells), math.log(4))
        del cells["dry|night"]["effort_hours"]
        with self.assertRaises(ValueError):
            four_cell_log_did(cells)
        cells["dry|night"]["effort_hours"] = 0
        with self.assertRaises(ValueError):
            four_cell_log_did(cells)
        cells["dry|night"]["effort_hours"] = 10
        cells["dry|night"]["events"] = 0
        with self.assertRaises(ValueError):
            four_cell_log_did(cells)
        del cells["dry|night"]
        with self.assertRaises(ValueError):
            four_cell_log_did(cells)

if __name__ == "__main__":
    unittest.main()
