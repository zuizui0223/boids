#!/usr/bin/env python3
"""Exact-yesterday extension of frozen v23; exports anonymous aggregates only.

Same-source exploratory comparison, specified with the v23 results already known.
All original source, eligibility, prediction and admission routines remain in v23.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validation_v23"))
import duck_daily_era5_forecast as v23

PROTOCOL = "docs/V29_HISTORY_VERSUS_PERSISTENCE_PROTOCOL.md"
RECEIPT_PATH = ROOT / "validation_v23/results/independent_duck_daily_ERA5_forecast_v23.json"
ORIGINAL_GPS_BYTES = 46324165
BOOT_REPS = 10000
BOOT_SEED = 20261030
MODELS = ("M0", "ME", "MI", "MEI", "MP")
TOLERANCE = 1e-12


def _quantiles(values):
    if not values:
        return {"count": 0, "min": None, "p25": None, "median": None, "p75": None, "max": None}
    quantiles = np.quantile(values, [0., .25, .5, .75, 1.])
    return {"count": len(values), **dict(zip(
        ("min", "p25", "median", "p75", "max"), map(float, quantiles)))}


def add_persistence(records, events, daily):
    """Copy v23 errors and add MP using raw complete day exactly t-1.

    Reconstruct only history dates for the chronology audit, never predictions.
    A site's 14-item deque is updated after every date's targets are audited.
    """
    event_lookup = {}
    for event in events:
        key = event["bird"], event["date"]
        if key in event_lookup:
            raise ValueError("Duplicate eligible bird/date event")
        event_lookup[key] = event
    targets = collections.defaultdict(list)
    target_keys = set()
    for ix, row in enumerate(records):
        key = row["bird"], row["date"]
        if key in target_keys:
            raise ValueError("Duplicate v23 target bird/date")
        target_keys.add(key)
        event = event_lookup.get(key)
        if event is None or event["site"] != row["site"]:
            raise ValueError("v23 target missing from original eligible events")
        targets[row["date"]].append((ix, row))
    history = collections.defaultdict(lambda: collections.deque(maxlen=v23.MAX_OWN_HIST_DAYS))
    counts, oldest, newest = [], [], []
    previous_in_mi = different_site = no_previous_event = 0
    enriched = [None] * len(records)
    for day, block_iter in itertools.groupby(sorted(events, key=lambda x: (x["date"], x["bird"])),
                                            key=lambda x: x["date"]):
        block = list(block_iter)
        prior_date = day - dt.timedelta(days=1)
        for ix, row in targets.get(day, ()):
            bird, site = row["bird"], row["site"]
            prior = daily.get((bird, prior_date))
            if prior is None:
                raise ValueError("Missing raw complete exact previous calendar day for MP")
            yesterday = prior["radius_log1p_km"]
            today = event_lookup[(bird, day)]["response"]
            if not all(math.isfinite(value) for value in (yesterday, today)):
                raise ValueError("Nonfinite exact previous day or target value")
            dates = list(history[(site, bird)])
            if (len(dates) != row["n_previous_own_days"] or
                    len(dates) < v23.MIN_OWN_HIST_DAYS or any(date >= day for date in dates)):
                raise ValueError("Original v23 history count or chronology mismatch")
            counts.append(len(dates))
            oldest.append((day - dates[0]).days)
            newest.append((day - dates[-1]).days)
            previous_in_mi += prior_date in dates
            previous_event = event_lookup.get((bird, prior_date))
            no_previous_event += previous_event is None
            different_site += previous_event is not None and previous_event["site"] != site
            enriched[ix] = {**row, "error_MP": (today - yesterday) ** 2}
        for event in block:
            history[(event["site"], event["bird"])].append(day)
    return enriched, {
        "target_records_audited": len(records),
        "eligible_prior_observations": _quantiles(counts),
        "oldest_calendar_age_days": _quantiles(oldest),
        "newest_calendar_age_days": _quantiles(newest),
        "targets_exact_previous_day_in_MI": int(previous_in_mi),
        "targets_previous_day_eligible_event_different_site": int(different_site),
        "targets_no_previous_day_eligible_event": int(no_previous_event),
        "history_same_site_and_bird_only": True,
        "history_updated_after_all_targets_on_each_date": True,
        "current_or_future_events_in_history": False,
        "MP_uses_exact_previous_complete_raw_UTC_day": True,
    }


def _receipt_equal(actual, expected):
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(_receipt_equal(actual[k], expected[k]) for k in actual)
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(_receipt_equal(a, b) for a, b in zip(actual, expected))
    if isinstance(actual, float) and isinstance(expected, (int, float)):
        return math.isfinite(actual) and math.isfinite(expected) and abs(actual - expected) <= TOLERANCE
    return type(actual) is type(expected) and actual == expected


def verify_v23_receipt(records, expected):
    """Replay original evaluate, matching the actual saved receipt representation."""
    original = v23.evaluate(records)
    if not original["status"].startswith("EXPLORATORY"):
        raise ValueError("v23 receipt cannot match: original admission gate failed")
    checks = {
        "original_independent_ducks": original["original_independent_bird_count"],
        "original_future_duck_day_targets": original["source_future_original_duck_day_targets"],
        "absolute_equal_individual_MSE_M0_ME_MI_MEI": original["mean_MSE_M0_ME_MI_MEI"],
        # The frozen JSON differs in naming from the original live evaluator.
        "anonymized_all_bird_results": original["per_original_individual_anonymized"],
    }
    for key, actual in checks.items():
        if key not in expected or not _receipt_equal(actual, expected[key]):
            raise ValueError("Frozen v23 receipt mismatch: " + key)
    return {"status": "V23_FROZEN_RECEIPT_MATCH", "absolute_error_tolerance": TOLERANCE,
            "original_independent_ducks": checks["original_independent_ducks"],
            "original_future_duck_day_targets": checks["original_future_duck_day_targets"],
            "all_anonymous_bird_fields_and_four_original_errors_verified": True}


def summarize(records):
    """Equal-bird means and paired whole-bird inference for all fixed contrasts."""
    if not records:
        return {"status": "NO_TARGET_RECORDS", "any_forecast_score_exported": False,
                "original_independent_ducks": 0, "original_future_duck_day_targets": 0}
    by_bird = collections.defaultdict(list)
    for row in records:
        by_bird[row["bird"]].append(row)
    per_bird = {}
    matrix = []
    for ix, bird in enumerate(sorted(by_bird), 1):
        rows = by_bird[bird]
        errors = np.array([[row["error_" + model] for model in MODELS] for row in rows])
        if not np.isfinite(errors).all() or (errors < 0).any():
            raise ValueError("Nonfinite or negative squared error")
        means = errors.mean(axis=0)
        matrix.append(means)
        per_bird[f"duck_{ix:03d}"] = {
            "future_days_scored": len(rows), "study": v23.BANGLADESH_STUDY,
            "taxon": rows[0]["taxon"], "source_wetland_names": sorted({r["site"] for r in rows}),
            "weather_class_fallback_days": sum(r["matching_weather_fallback"] for r in rows),
            "mean_squared_log_spread_error_M0_ME_MI_MEI_MP": list(map(float, means)),
        }
    matrix = np.array(matrix)
    rng = np.random.default_rng(BOOT_SEED)
    samples = rng.integers(0, len(matrix), size=(BOOT_REPS, len(matrix)))
    comparisons = {}
    for name, col in (("primary_MP_minus_MEI", 3), ("secondary_MP_minus_MI", 2),
                      ("descriptive_MP_minus_ME", 1), ("descriptive_MP_minus_M0", 0)):
        gains = matrix[:, 4] - matrix[:, col]
        positive, nonzero = int((gains > 0).sum()), int((gains != 0).sum())
        tail = sum(math.comb(nonzero, k) for k in range(positive, nonzero + 1)) / 2 ** nonzero
        comparisons[name] = {
            "equal_individual_mean_MSE_gain_log_km_squared": float(gains.mean()),
            "individual_bootstrap_95_percentile": list(map(float, np.quantile(gains[samples].mean(axis=1), [.025, .975]))),
            "individuals_with_positive_gain": positive, "individuals_with_nonzero_gain": nonzero,
            "n_independent_original_ducks": len(matrix),
            "exact_one_sided_sign_tail_probability": tail,
        }
    return {"status": "EXPLORATORY_SAME_SOURCE_DUCK_HISTORY_VERSUS_PERSISTENCE",
            "any_forecast_score_exported": True,
            "original_independent_ducks": len(matrix), "original_future_duck_day_targets": len(records),
            "model_order": list(MODELS), "mean_MSE_M0_ME_MI_MEI_MP": list(map(float, matrix.mean(axis=0))),
            "per_original_individual_anonymized": per_bird, "frozen_contrasts": comparisons,
            "bootstrap_resamples": BOOT_REPS, "bootstrap_seed": BOOT_SEED,
            "bootstrap_unit": "whole bird, paired across all five models; equal bird weight",
            "positive_gain_means": "history comparator has lower MSE than MP",
            "sign_test_null": "independent equiprobable signs conditional on nonzero bird gains; zeros excluded"}


def verify_local_gps(path):
    """A local original is accepted only after exact original byte/hash checks."""
    if path.stat().st_size != ORIGINAL_GPS_BYTES:
        raise ValueError("Original GPS bytes mismatch")
    md5, sha = hashlib.md5(), hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            md5.update(chunk)
            sha.update(chunk)
    if md5.hexdigest() != v23.ducks.ORIGINAL_PROVIDER_MD5:
        raise ValueError("Original GPS provider MD5 mismatch")
    if sha.hexdigest() != v23.PINNED_GPS_SHA256:
        raise ValueError("Previously frozen GPS original source SHA256 drift")
    return {"status": "ORIGINAL_BYTES_VERIFIED", "bytes": ORIGINAL_GPS_BYTES,
            "provider_md5": md5.hexdigest(), "original_sha256": sha.hexdigest(),
            "provider_md5_and_exact_bytes_match": True}


def load_sources(gps_file=None):
    """Use unchanged v23 acquisition, quality and weather gates."""
    with tempfile.TemporaryDirectory() as folder:
        if gps_file is None:
            spec = v23.ducks.select_original(v23.ducks.fetch_metadata())
            if spec["size"] != ORIGINAL_GPS_BYTES:
                raise ValueError("Original GPS bytes mismatch in provider manifest")
            path = Path(folder) / v23.ducks.SOURCE_NAME
            original = v23.ducks.get_original_file(spec, path)
            if original["original_sha256"] != v23.PINNED_GPS_SHA256:
                raise ValueError("Previously frozen GPS original source SHA256 drift")
        else:
            path = Path(gps_file)
            original = verify_local_gps(path)
        era, era_qa = v23.load_exact_era5()
        daily, gps_qa = v23.parse_original_gps(path)
        events, source_qa = v23.eligible_daily_events(daily, era)
    return daily, events, original, era_qa, gps_qa, source_qa


def run(gps_file=None):
    receipt_bytes = RECEIPT_PATH.read_bytes()
    expected = json.loads(receipt_bytes)
    daily, events, original, era_qa, gps_qa, source_qa = load_sources(gps_file)
    records, forecast_qa = v23.prequential_predictions(events)
    gate = verify_v23_receipt(records, expected)  # Stop before opening the new comparator.
    gate["frozen_receipt_sha256"] = hashlib.sha256(receipt_bytes).hexdigest()
    gate["frozen_receipt_path"] = str(RECEIPT_PATH.relative_to(ROOT)) if RECEIPT_PATH.is_relative_to(ROOT) else RECEIPT_PATH.name
    enriched, audit = add_persistence(records, events, daily)
    outcome = summarize(enriched)
    return {
        "study": "v29-same-source-duck-history-versus-exact-yesterday-persistence",
        "protocol": PROTOCOL,
        "original_protocol_base_sha": "47cf12b51553c865027961ae5c162f1b479f5c8c",
        "code_base_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_GPS_integrity": original, "source_ERA5_integrity": era_qa,
        "original_GPS_quality": gps_qa, "wetland_prior_day_weather_source_support": source_qa,
        "forecast_target_support": forecast_qa, "v23_preservation_receipt": gate,
        "chronology_audit": audit, "status": outcome["status"], "observed_outcome": outcome,
        "previous_v13_through_v28_frozen_empirical_endpoints_unchanged": True,
        "no_raw_animal_GPS_coordinates_timestamps_targets_or_original_IDs_exported": True,
        "interpretation_limits": [
            "Same-source exploratory extension specified with positive v23 results already known; not independent replication or pre-data preregistration",
            "Future days for already-observed birds; not unseen-animal, future-climate or 3D niche prediction",
            "Shared study/wetland/year shocks: whole-bird confidence intervals do not establish independent environment, taxon or year replication",
            "ERA5 reanalysis at two coarse wetland grids is not direct local weather, food or prey measurement",
            "Predictive differences identify no learning, stable individuality, cognition, resource partition or causal social force",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("validation_v29/results/duck_persistence_v29.json"))
    parser.add_argument("--gps-file", type=Path, help="Locally downloaded original; exact bytes, MD5 and SHA256 required")
    args = parser.parse_args()
    result = run(args.gps_file)
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.out.parent,
                                         prefix=".duck-persistence-", suffix=".tmp", delete=False) as output:
            temporary = Path(output.name)
            output.write(payload)
        os.replace(temporary, args.out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print("V29_RECEIPT", json.dumps(result["v23_preservation_receipt"], sort_keys=True))
    print("V29_STATUS", result["status"])
    print("V29_ALL_FIXED_CONTRASTS", json.dumps(result["observed_outcome"]["frozen_contrasts"], sort_keys=True))


if __name__ == "__main__":
    main()
