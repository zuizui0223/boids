"""Known-truth invariants; passing does not validate any field result."""
import unittest
from .metrics import conditional_information, matched_availability_buffering, origin_to_destination_state_retention


class TestStateRegimes(unittest.TestCase):
    def test_identity_information_same_context(self):
        segregated = [{"context": "site1", "identity": i, "state": i} for i in ("a", "b") for _ in range(20)]
        mixed = [{"context": "site1", "identity": i, "state": s} for i in ("a", "b") for s in ("a", "b") for _ in range(10)]
        self.assertAlmostEqual(conditional_information(segregated), 0.6931471805599453)
        self.assertAlmostEqual(conditional_information(mixed), 0.0)

    def test_used_state_buffered_against_availability(self):
        events = []
        for j in range(12):
            for i in ("railA", "railB"):
                depth = 10.0 + 3.0 * j
                events.append({"individual": i, "event_id": str(j), "time": j,
                               "used": 14.0, "alternatives": [depth - 1.0, depth + 1.0]})
        r = matched_availability_buffering(events, draws=999)
        self.assertEqual((r["n_individuals"], r["n_events"]), (2, 24))
        self.assertAlmostEqual(r["observed_equal_individual_slope"], 0.0)
        self.assertGreater(r["pseudo_use_null_median_slope"], 0.9)
        self.assertLessEqual(r["lower_tail_monte_carlo_p"], 0.002)

    def test_no_origin_no_claim(self):
        source_like = [{"individual": "waterbird1", "step_id": "1", "observed_destination_state": "wetland",
                        "available_destination_states": ["field", "wetland"], "species": "GWFG", "timestamp": "2022-01-01 12:00"}]
        with self.assertRaisesRegex(ValueError, "origin/destination schema STOP"):
            origin_to_destination_state_retention(source_like)

    def test_origin_matched_retention_and_group_weighting(self):
        steps = [
            {"individual": "w1", "step_id": "1", "origin_state": "wetland", "observed_destination_state": "wetland", "available_destination_states": ["wetland", "field", "field"], "species": "GWFG", "timestamp": "2022-01-01 12:00"},
            {"individual": "w1", "step_id": "2", "origin_state": "field", "observed_destination_state": "wetland", "available_destination_states": ["field", "field"], "species": "GWFG", "timestamp": "2022-01-02 12:00"},
            {"individual": "w2", "step_id": "1", "origin_state": "field", "observed_destination_state": "field", "available_destination_states": ["wetland", "wetland"], "species": "NOPI", "timestamp": "2022-01-01 12:00"},
        ]
        r = origin_to_destination_state_retention(steps)
        self.assertEqual(r["n_individuals"], 2)
        self.assertAlmostEqual(r["per_individual_retention_excess"]["w1"], -1/6)
        self.assertAlmostEqual(r["per_individual_retention_excess"]["w2"], 1.0)
        self.assertAlmostEqual(r["equal_individual_retention_excess"], 5/12)

    def test_mismatched_availability_rejected(self):
        with self.assertRaises(ValueError):
            matched_availability_buffering([{"individual": "a", "event_id": 1, "time": 1, "used": 3, "alternatives": []}])


if __name__ == "__main__":
    unittest.main()

