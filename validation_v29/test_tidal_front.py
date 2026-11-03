"""Physical/synthetic tests only. No published GPS or gauge claim."""
import math
import unittest
import csv
import tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone

from tidal_front import TideSeries, compare_levels, known_truth, run_known_truth, social_free_alignment, utc_timestamp, load_hourly_gps_steps

UTC = timezone.utc


def sample_gauge():
    start = datetime(2020, 1, 1, tzinfo=UTC)
    return TideSeries([(start+timedelta(minutes=10*k), math.cos(2*math.pi*k/72))
                       for k in range(160)], datum="NAP_m", provenance="synthetic"), start


class TestTidalFront(unittest.TestCase):
    def test_timezones_must_be_explicit(self):
        with self.assertRaises(ValueError):
            utc_timestamp("2020-01-01T09:00:00")
        self.assertEqual(utc_timestamp("2020-01-01T09:00:00+09:00").hour, 0)

    def test_datum_and_sorted_source(self):
        with self.assertRaises(ValueError):
            TideSeries([("2020-01-01T00:00Z", 1)]*3, datum="NAP_m", provenance="observed")
        with self.assertRaises(ValueError):
            TideSeries([("2020-01-01T00:00Z", 1)]*3, datum="MSL_m", provenance="observed")

    def test_same_height_hysteresis_and_past_only_phase(self):
        tide, start = sample_gauge()
        ebb = start + timedelta(hours=3, minutes=10)
        flood = start + timedelta(hours=8, minutes=50)
        h1, phase1, _ = tide.at_with_phase(ebb)
        h2, phase2, _ = tide.at_with_phase(flood)
        self.assertAlmostEqual(h1, h2, places=12)
        self.assertEqual(phase1, -1)
        self.assertEqual(phase2, 1)
        age1 = tide.exposure_age_hours(ebb, elevation_nap_m=0.0)
        age2 = tide.exposure_age_hours(flood, elevation_nap_m=0.0)
        self.assertIsNotNone(age1)
        self.assertIsNotNone(age2)
        self.assertGreater(age2 - age1, 5.5)

    def test_missing_crossing_is_unknown_not_zero(self):
        tide, start = sample_gauge()
        now = start + timedelta(hours=4)
        self.assertIsNone(tide.exposure_age_hours(now, elevation_nap_m=2.))
        self.assertIsNone(tide.exposure_age_hours(now, elevation_nap_m=-2.))
        p = tide.patch_features(now, elevation_nap_m=2., slope_m_per_m=0.01)
        self.assertEqual(p["exposed"], 1)
        self.assertEqual(p["exposure_age_known"], 0)

    def test_gap_rejected_and_no_outside_extrapolation(self):
        g = TideSeries([("2020-01-01T00:00Z", 0), ("2020-01-01T01:00Z", 1),
                        ("2020-01-01T02:00Z", 0)], datum="NAP_m", provenance="observed")
        with self.assertRaises(ValueError):
            g.at("2020-01-01T00:30Z")
        with self.assertRaises(ValueError):
            g.at("2019-12-31T23:50Z")

    def test_observed_join_contract_and_speed_unit(self):
        tide, start = sample_gauge()
        with tempfile.TemporaryDirectory() as directory:
            gps = Path(directory) / "gps.csv"
            with gps.open("w", newline="", encoding="utf-8") as dest:
                w = csv.writer(dest)
                w.writerow(["individual_id", "timestamp_utc", "x_rd_m", "y_rd_m", "elevation_nap_m", "slope_m_per_m"])
                for hour, x in ((4, 200000), (5, 201000), (6, 202000)):
                    t = start + timedelta(hours=hour)
                    w.writerow(["tag_1", t.isoformat(), x, 600000, 2., 0.006])
            rows, audit = load_hourly_gps_steps(gps, tide)
            self.assertEqual(audit["raw_fixes"], 3)
            self.assertEqual(audit["retained_steps"], 2)
            self.assertAlmostEqual(rows[0]["response"], math.log1p(1.0))
            self.assertEqual(audit["n_individuals_retained"], 1)

    def test_environment_alone_produces_alignment(self):
        r = social_free_alignment(seed=29)
        self.assertEqual(r["social_interaction_coefficient"], 0)
        self.assertGreater(r["same_tide_alignment"], r["asynchronous_phase_alignment"] + 0.5)

    def test_known_truth_withheld_age_increment(self):
        r = run_known_truth()
        self.assertEqual(r["evidence"], "SYNTHETIC_KNOWN_TRUTH_ONLY")
        self.assertGreater(r["gain_M0_M1"], 0)
        self.assertGreater(r["gain_M1_M2"], 0)
        self.assertGreaterEqual(r["n_week_blocks"], 8)
        self.assertEqual(r["embargo_week_blocks"], 1)
        self.assertFalse(r["gps_observed"])

    def test_negative_control_no_age_mechanism(self):
        _, rows = known_truth(seed=51, age_effect=0.)
        result = compare_levels(rows)
        # An unconstrained larger model need not win on independent test blocks.
        self.assertLess(result["gain_M1_M2"], 0.002)


if __name__ == "__main__":
    unittest.main()