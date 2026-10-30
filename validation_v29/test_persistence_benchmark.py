"""Invented tracks only: these tests provide no biological outcomes."""
import copy
import datetime as dt
import importlib
import importlib.util
import hashlib
import io
from contextlib import redirect_stdout
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import duck_daily_era5_forecast as v23

DAY = dt.date(2020, 1, 1)
BIRD = ("private-study", "private-animal")


def event(day, bird=BIRD, site="baikka_beel", response=.2):
    return {"bird": bird, "date": DAY + dt.timedelta(days=day),
            "site": site, "response": response, "taxon": "invented duck",
            "weather_class": (0, 0)}


def record(day, bird=BIRD, site="baikka_beel", n=3):
    return {"bird": bird, "date": DAY + dt.timedelta(days=day),
            "site": site, "taxon": "invented duck", "n_previous_own_days": n,
            "weather_class": (0, 0), "matching_weather_fallback": False,
            "error_M0": 1., "error_ME": 2., "error_MI": 3., "error_MEI": 4.}


def admitted_fixture():
    events = [event(j, bird=("invented-study", f"private-{i:03d}"),
                    response=.2 + .01 * i + .1 * (j % 2))
              for j in range(22) for i in range(25)]
    records, _ = v23.prequential_predictions(events)
    evaluated = v23.evaluate(records)
    expected = {
        "original_independent_ducks": 25,
        "original_future_duck_day_targets": len(records),
        "absolute_equal_individual_MSE_M0_ME_MI_MEI": evaluated["mean_MSE_M0_ME_MI_MEI"],
        "anonymized_all_bird_results": evaluated["per_original_individual_anonymized"],
    }
    return events, records, expected


class PersistenceKnownTruth(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("persistence_benchmark"),
                             "Persistence comparator is not implemented")
        self.p = importlib.import_module("persistence_benchmark")

    def test_exact_calendar_lag_across_eligible_gap_preserves_original_errors(self):
        # Substituting latest eligible event (.2) would give zero; raw t-1 is .7.
        events = [event(j) for j in (0, 2, 3, 6, 7)]
        original = [record(6)]
        before = copy.deepcopy(original)
        daily = {(BIRD, DAY + dt.timedelta(days=5)): {"radius_log1p_km": .7}}
        enriched, audit = self.p.add_persistence(original, events, daily)
        self.assertAlmostEqual(enriched[0]["error_MP"], .25)
        self.assertEqual(original, before)
        self.assertEqual({k: v for k, v in enriched[0].items() if k != "error_MP"}, before[0])
        self.assertEqual(audit["eligible_prior_observations"]["min"], 3)
        self.assertEqual(audit["oldest_calendar_age_days"]["max"], 6)
        self.assertEqual(audit["newest_calendar_age_days"]["min"], 3)
        self.assertEqual(audit["targets_exact_previous_day_in_MI"], 0)
        self.assertEqual(audit["targets_no_previous_day_eligible_event"], 1)

    def test_missing_raw_exact_prior_day_raises_instead_of_falling_back(self):
        events = [event(j) for j in (0, 2, 3, 6)]
        with self.assertRaisesRegex(ValueError, "exact previous"):
            self.p.add_persistence([record(6)], events,
                                  {(BIRD, DAY + dt.timedelta(days=3)): {"radius_log1p_km": .2}})

    def test_same_date_future_and_other_site_do_not_enter_MI_audit(self):
        events = [event(j) for j in (0, 2, 3, 6, 7)]
        events.append(event(5, site="tanguar_haor"))
        daily = {(BIRD, DAY + dt.timedelta(days=5)): {"radius_log1p_km": .7}}
        enriched, audit = self.p.add_persistence([record(6)], list(reversed(events)), daily)
        changed = [dict(e, response=9999.) if e["date"] >= DAY + dt.timedelta(days=6) else e
                   for e in events]
        # Only target response changes MP error; audit must remain identical.
        _, changed_audit = self.p.add_persistence([record(6)], changed, daily)
        self.assertEqual(audit, changed_audit)
        self.assertEqual(audit["targets_previous_day_eligible_event_different_site"], 1)
        self.assertEqual(audit["targets_no_previous_day_eligible_event"], 0)
        self.assertEqual(audit["eligible_prior_observations"]["max"], 3)

    def test_fourteen_item_history_and_exact_previous_membership(self):
        events = [event(j) for j in range(23)]
        daily = {(BIRD, DAY + dt.timedelta(days=19)): {"radius_log1p_km": .2}}
        _, audit = self.p.add_persistence([record(20, n=14)], events, daily)
        self.assertEqual(audit["eligible_prior_observations"]["min"], 14)
        self.assertEqual(audit["oldest_calendar_age_days"]["max"], 14)
        self.assertEqual(audit["newest_calendar_age_days"]["min"], 1)
        self.assertEqual(audit["targets_exact_previous_day_in_MI"], 1)

    def test_audit_history_mismatch_fails_instead_of_silently_changing_cohort(self):
        daily = {(BIRD, DAY + dt.timedelta(days=5)): {"radius_log1p_km": .7}}
        with self.assertRaisesRegex(ValueError, "history"):
            self.p.add_persistence([record(6, n=4)], [event(j) for j in (0, 2, 3, 6)], daily)

    def test_equal_bird_weighting_with_unequal_days_and_all_contrasts(self):
        rows = [dict(record(6), error_MP=8.)]
        rows += [dict(record(j, bird=("private-study", "private-second")), error_MP=0.)
                 for j in (6, 7, 8)]
        result = self.p.summarize(rows)
        self.assertEqual(result["mean_MSE_M0_ME_MI_MEI_MP"], [1., 2., 3., 4., 4.])
        effects = result["frozen_contrasts"]
        self.assertEqual(list(effects), ["primary_MP_minus_MEI", "secondary_MP_minus_MI",
                                         "descriptive_MP_minus_ME", "descriptive_MP_minus_M0"])
        primary = effects["primary_MP_minus_MEI"]
        self.assertEqual(primary["equal_individual_mean_MSE_gain_log_km_squared"], 0.)
        self.assertEqual(effects["secondary_MP_minus_MI"]["equal_individual_mean_MSE_gain_log_km_squared"], 1.)
        self.assertEqual(effects["descriptive_MP_minus_ME"]["equal_individual_mean_MSE_gain_log_km_squared"], 2.)
        self.assertEqual(effects["descriptive_MP_minus_M0"]["equal_individual_mean_MSE_gain_log_km_squared"], 3.)
        self.assertEqual(primary["individual_bootstrap_95_percentile"], [-4., 4.])
        self.assertEqual(primary["individuals_with_positive_gain"], 1)
        self.assertEqual(primary["individuals_with_nonzero_gain"], 2)
        self.assertEqual(primary["exact_one_sided_sign_tail_probability"], .75)
        self.assertEqual(result["bootstrap_resamples"], 10000)
        self.assertEqual(result["bootstrap_seed"], 20261030)
        self.assertEqual(result, self.p.summarize(rows))

    def test_zero_gains_and_empty_records_explicitly_handled(self):
        result = self.p.summarize([dict(record(6), error_MP=4.)])
        primary = result["frozen_contrasts"]["primary_MP_minus_MEI"]
        self.assertEqual(primary["individuals_with_nonzero_gain"], 0)
        self.assertEqual(primary["exact_one_sided_sign_tail_probability"], 1.)
        self.assertEqual(primary["individual_bootstrap_95_percentile"], [0., 0.])
        empty = self.p.summarize([])
        self.assertEqual(empty["status"], "NO_TARGET_RECORDS")
        self.assertFalse(empty["any_forecast_score_exported"])
        self.assertNotIn("frozen_contrasts", empty)

    def test_aggregate_output_omits_raw_ids_dates_and_targets(self):
        rows = [dict(record(6), error_MP=.25)]
        encoded = json.dumps(self.p.summarize(rows), allow_nan=False)
        for secret in ("private-study", "private-animal", "2020-01-07", '"response"', '"date"', '"bird"'):
            self.assertNotIn(secret, encoded)
        self.assertIn("duck_001", encoded)

    def test_saved_receipt_schema_all_birds_and_errors_verified(self):
        _, records, expected = admitted_fixture()
        gate = self.p.verify_v23_receipt(records, expected)
        self.assertEqual(gate["status"], "V23_FROZEN_RECEIPT_MATCH")
        for mutation in ("birds", "days", "per_bird_count", "error", "metadata", "global_error"):
            bad = copy.deepcopy(expected)
            if mutation == "birds": bad["original_independent_ducks"] += 1
            elif mutation == "days": bad["original_future_duck_day_targets"] += 1
            elif mutation == "per_bird_count": bad["anonymized_all_bird_results"]["duck_001"]["future_days_scored"] += 1
            elif mutation == "error": bad["anonymized_all_bird_results"]["duck_001"]["mean_squared_log_spread_error_M0_ME_MI_MEI"][2] += 1e-6
            elif mutation == "metadata": bad["anonymized_all_bird_results"]["duck_001"]["taxon"] = "wrong taxon"
            else: bad["absolute_equal_individual_MSE_M0_ME_MI_MEI"][1] += 1e-6
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, "v23 receipt"):
                self.p.verify_v23_receipt(records, bad)

    def test_receipt_mismatch_stops_cli_before_new_export(self):
        events, _, expected = admitted_fixture()
        expected["original_future_duck_day_targets"] += 1
        daily = {(e["bird"], e["date"]): {"radius_log1p_km": e["response"]} for e in events}
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "unchanged.json"
            out.write_text("existing artifact\n")
            frozen = Path(folder) / "receipt.json"
            frozen.write_text(json.dumps(expected))
            # External acquisition boundary only; actual v23 predictor/evaluate and new gate run.
            with mock.patch.object(self.p, "RECEIPT_PATH", frozen), \
                 mock.patch.object(self.p, "load_sources", return_value=(daily, events, {}, {}, {}, {})), \
                 mock.patch("sys.argv", ["persistence_benchmark.py", "--out", str(out)]):
                with self.assertRaisesRegex(ValueError, "v23 receipt"):
                    self.p.main()
            self.assertEqual(out.read_text(), "existing artifact\n")

    def test_successful_synthetic_cli_writes_only_aggregate_after_receipt_match(self):
        events, _, expected = admitted_fixture()
        daily = {(e["bird"], e["date"]): {"radius_log1p_km": e["response"]} for e in events}
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "result.json"
            frozen = Path(folder) / "receipt.json"
            frozen.write_text(json.dumps(expected))
            with mock.patch.object(self.p, "RECEIPT_PATH", frozen), \
                 mock.patch.object(self.p, "load_sources", return_value=(daily, events, {}, {}, {}, {})), \
                 mock.patch("sys.argv", ["persistence_benchmark.py", "--out", str(out)]), \
                 redirect_stdout(io.StringIO()):
                self.p.main()
            encoded = out.read_text()
            result = json.loads(encoded)
            self.assertEqual(result["v23_preservation_receipt"]["frozen_receipt_sha256"],
                             hashlib.sha256(frozen.read_bytes()).hexdigest())
            self.assertEqual(result["chronology_audit"]["target_records_audited"], 475)
            self.assertEqual(result["observed_outcome"]["original_independent_ducks"], 25)
            self.assertEqual(len(result["observed_outcome"]["frozen_contrasts"]), 4)
            self.assertEqual(list(Path(folder).glob(".duck-persistence-*")), [])
            for forbidden in ("private-000", "invented-study", "2020-01-04", '"response"'):
                self.assertNotIn(forbidden, encoded)

    def test_local_file_wrong_size_is_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "not-original.csv"
            path.write_bytes(b"not the original GPS")
            with self.assertRaisesRegex(ValueError, "bytes"):
                self.p.verify_local_gps(path)


if __name__ == "__main__":
    unittest.main()
