#!/usr/bin/env python3
"""v30: held-out geographic cohorts within original duck GPS archive.

No Bangladesh outcome is re-opened in this script. Predictions are strictly
prequential for four predeclared other studies. This is not an independent
new source or a model of 3D ecological niches / animal cognition.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validation_v23"))
import source_gate as source

STUDIES = (
    "Dabbling duck migration Mongolia (2020)",
    "Dabbling duck migration Ottenby 2017 (Anas platyrhynchos, Anas acuta)",
    "Dabbling duck migration Portugal 2018--2022",
    "Eurasian wigeon (Mareca penelope) Netherlands Lithuania 2018-2019",
)
KNOWN_ID_COUNTS = dict(zip(STUDIES, (31, 34, 20, 38)))
KNOWN_FIX_COUNTS = dict(zip(STUDIES, (30173, 32781, 64438, 72967)))
PIN_SHA256 = "001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e"
PIN_BYTES = 46324165
MIN_DAY_FIXES = 6
MIN_SPAN_H = 8.
MAX_HDOP = 15.
MIN_OWN = 3
MAX_OWN = 14
MIN_OTHER_BIRDS = 5
MIN_OTHER_DAYS = 20
MIN_STUDY_BIRDS = 8
MIN_STUDY_TARGETS = 80
MIN_TOTAL_BIRDS = 60
MIN_TOTAL_TARGETS = 500
SEED = 20261030
REPS = 10000
MODELS = ("M0", "MS", "MI", "MP", "MH")
PROTOCOL = "docs/V30_CROSS_STUDY_PERSISTENCE_PROTOCOL.md"

def parse_gps(path: Path):
    """Parse original file; exclude both sides of same-bird UTC duplicates."""
    fixes = collections.defaultdict(list)
    seen = collections.Counter()
    bird_info = {}
    qa = {s: {"source_physical_rows": 0, "invalid_original_GPS_rows": 0,
              "duplicate_original_GPS_rows_discarded": 0,
              "qualifying_complete_UTC_days": 0, "bird_IDs_with_qualifying_days": 0}
          for s in STUDIES}
    total = 0
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(source.SOURCE_COLS).issubset(reader.fieldnames or ()):
            raise ValueError("Original telemetry header changed")
        for row in reader:
            total += 1
            study = row.get("study.name")
            if study not in qa:
                continue
            qa[study]["source_physical_rows"] += 1
            try:
                bird = (str(row["study.id"]).strip(), str(row["individual.id"]).strip())
                taxon = str(row["individual.taxon.canonical.name"]).strip()
                if not all(bird) or not taxon:
                    raise ValueError("Blank identity or taxon")
                stamp = dt.datetime.strptime(str(row["timestamp"]).strip(), "%Y-%m-%d %H:%M:%S")
                lat, lon, hdop = (float(row[col]) for col in
                    ("location.lat", "location.long", "gps.hdop"))
                if not (all(math.isfinite(v) for v in (lat, lon, hdop))
                    and -90 <= lat <= 90 and -180 <= lon <= 180
                    and 0 <= hdop <= MAX_HDOP):
                    raise ValueError("Invalid original GPS fix")
            except (KeyError, ValueError, TypeError):
                qa[study]["invalid_original_GPS_rows"] += 1
                continue
            old = bird_info.get(bird)
            if old is not None and old != (study, taxon):
                raise ValueError("One original source ID changes study or taxon")
            bird_info[bird] = (study, taxon)
            seen[bird, stamp] += 1
            fixes[bird, stamp.date()].append((stamp, lat, lon))
    days = {}
    for (bird, date), raw in fixes.items():
        good = [point for point in raw if seen[bird, point[0]] == 1]
        study, taxon = bird_info[bird]
        qa[study]["duplicate_original_GPS_rows_discarded"] += len(raw) - len(good)
        if len(good) < MIN_DAY_FIXES:
            continue
        good.sort(key=lambda p: p[0])
        span = (good[-1][0] - good[0][0]).total_seconds() / 3600.
        if span < MIN_SPAN_H:
            continue
        lat_mean = float(np.mean([p[1] for p in good]))
        lon_mean = float(np.mean([p[2] for p in good]))
        y = np.array([(p[1] - lat_mean) * 111.2 for p in good], dtype=float)
        x = np.array([(p[2] - lon_mean) * 111.2 * math.cos(math.radians(lat_mean))
                      for p in good], dtype=float)
        radius = float(np.sqrt(np.mean(x*x + y*y)))
        if not math.isfinite(radius):
            raise ValueError("Nonfinite GPS radius")
        days[bird, date] = {"study": study, "taxon": taxon, "y": math.log1p(radius)}
        qa[study]["qualifying_complete_UTC_days"] += 1
    for study in STUDIES:
        qa[study]["bird_IDs_with_qualifying_days"] = len({
            bird for (bird, date), x in days.items() if x["study"] == study})
    return days, {"source_rows_all_groups": total, "study_source_quality": qa,
                   "no_GPS_interpolation": True, "duplicate_policy": "drop every duplicated ID+UTC record"}

def make_events(days):
    """A target only when both day t and exact calendar day t-1 are complete."""
    events = []
    counts = {study: {"with_previous_complete_day": 0, "candidate_birds": 0}
              for study in STUDIES}
    for (bird, day), row in days.items():
        if (bird, day - dt.timedelta(days=1)) in days:
            events.append({"bird": bird, "date": day, **row})
            counts[row["study"]]["with_previous_complete_day"] += 1
    for study in STUDIES:
        counts[study]["candidate_birds"] = len({
            x["bird"] for x in events if x["study"] == study})
    return events, counts

def external_mean(by_bird, excluded):
    summaries = [float(np.mean(vals)) for bird, vals in by_bird.items()
                 if bird != excluded and vals]
    dates = sum(len(vals) for bird, vals in by_bird.items() if bird != excluded)
    return (float(np.mean(summaries)) if summaries else None, len(summaries), dates)

def predict(events, days):
    """Score complete future days without using same-day or future values."""
    by_study = collections.defaultdict(lambda: collections.defaultdict(list))
    by_taxon = collections.defaultdict(lambda: collections.defaultdict(list))
    own = collections.defaultdict(lambda: collections.deque(maxlen=MAX_OWN))
    targets = []
    audit = {s: {"candidate_events": 0, "insufficient_own_history": 0,
                 "insufficient_other_history": 0, "same_taxon_fallbacks": 0,
                 "predicted_targets": 0} for s in STUDIES}
    for day, group in itertools.groupby(
            sorted(events, key=lambda e: (e["date"], e["study"], e["bird"])),
            key=lambda e: e["date"]):
        block = list(group)
        for r in block:
            study, bird, taxon = r["study"], r["bird"], r["taxon"]
            audit[study]["candidate_events"] += 1
            hist = list(own[bird])
            if len(hist) < MIN_OWN:
                audit[study]["insufficient_own_history"] += 1
                continue
            m0, n_other, n_days = external_mean(by_study[study], bird)
            if n_other < MIN_OTHER_BIRDS or n_days < MIN_OTHER_DAYS:
                audit[study]["insufficient_other_history"] += 1
                continue
            ms, n_taxon, t_days = external_mean(by_taxon[study, taxon], bird)
            fallback = n_taxon < MIN_OTHER_BIRDS or t_days < MIN_OTHER_DAYS
            if fallback:
                ms = m0
                audit[study]["same_taxon_fallbacks"] += 1
            if (bird, day - dt.timedelta(days=1)) not in days:
                raise ValueError("Exact previous complete calendar day missing")
            mp = days[bird, day - dt.timedelta(days=1)]["y"]
            mi = float(np.mean(hist))
            mh = (mp + mi) / 2.
            vals = (m0, ms, mi, mp, mh)
            if not all(math.isfinite(v) for v in vals):
                raise ValueError("Nonfinite predictor")
            targets.append({"bird": bird, "study": study, "taxon": taxon,
                            "errors": [(r["y"]-v)**2 for v in vals],
                            "same_taxon_fallback": fallback,
                            "history_n": len(hist)})
            audit[study]["predicted_targets"] += 1
        # The block is appended AFTER all animals' day-t predictions.
        for r in block:
            by_study[r["study"]][r["bird"]].append(r["y"])
            by_taxon[r["study"], r["taxon"]][r["bird"]].append(r["y"])
            own[r["bird"]].append(r["y"])
    return targets, audit

def _sign_tail(pos, n):
    if n == 0:
        return 1.
    return sum(math.comb(n, k) for k in range(pos, n+1)) / (2 ** n)

def summarize(targets):
    """All-four-study admission and fixed equal-study inference."""
    per_bird = collections.defaultdict(list)
    for r in targets:
        per_bird[r["study"], r["bird"]].append(r)
    study_rows = []
    support = {}
    for study in STUDIES:
        birds = [(bird, rs) for (s, bird), rs in per_bird.items() if s == study]
        count = sum(len(rs) for _, rs in birds)
        support[study] = {"forecast_birds": len(birds), "future_bird_days": count,
                          "passes_source_support": len(birds) >= MIN_STUDY_BIRDS
                             and count >= MIN_STUDY_TARGETS}
        if birds:
            means = np.array([np.mean([r["errors"] for r in rs], axis=0) for _, rs in birds])
            taxa = collections.Counter(rs[0]["taxon"] for _, rs in birds)
            support[study]["taxon_bird_counts"] = dict(sorted(taxa.items()))
            support[study]["MS_source_fallback_targets"] = sum(
                int(r["same_taxon_fallback"]) for _, rs in birds for r in rs)
            study_rows.append((study, means.mean(axis=0)))
    total_birds = sum(v["forecast_birds"] for v in support.values())
    total_days = sum(v["future_bird_days"] for v in support.values())
    if (len(study_rows) != len(STUDIES) or
        any(not v["passes_source_support"] for v in support.values()) or
        total_birds < MIN_TOTAL_BIRDS or total_days < MIN_TOTAL_TARGETS):
        return {"status": "NOT_ADMITTED_FOUR_STUDY_SUPPORT", "support": support,
                "total_forecast_birds": total_birds, "total_future_bird_days": total_days,
                "any_predictive_score_exported": False}
    matrix = np.array([vec for _, vec in study_rows])
    means = matrix.mean(axis=0)
    indices = np.random.default_rng(SEED).integers(0, len(STUDIES), size=(REPS, len(STUDIES)))
    comparisons = {}
    for title, i, j in (
        ("primary_MS_minus_MP", 1, 3), ("secondary_MP_minus_MI", 3, 2),
        ("secondary_MP_minus_MH", 3, 4), ("descriptive_M0_minus_MS", 0, 1)
    ):
        gains = matrix[:, i] - matrix[:, j]
        positive = int(np.sum(gains > 0))
        nonzero = int(np.sum(gains != 0))
        comparisons[title] = {
            "equal_study_mean_MSE_gain": float(gains.mean()),
            "study_bootstrap_95_percentile": list(map(float,
                 np.quantile(gains[indices].mean(axis=1), [.025, .975]))),
            "study_signs_positive": positive, "study_signs_nonzero": nonzero,
            "number_of_original_studies": len(STUDIES),
            "one_sided_study_sign_tail": _sign_tail(positive, nonzero),
            "by_study_gain": {study: float(gain) for (study, _), gain in zip(study_rows, gains)},
        }
    return {"status": "EXPLORATORY_ALL_FOUR_STUDY_HOLDOUT",
            "any_predictive_score_exported": True,
            "total_forecast_birds": total_birds, "total_future_bird_days": total_days,
            "model_order": list(MODELS),
            "equal_study_absolute_MSE": list(map(float, means)),
            "study_absolute_MSE": {study: list(map(float, vec)) for study, vec in study_rows},
            "support": support, "frozen_comparisons": comparisons,
            "bootstrap_unit": "four study-level means, not original bird-day fixes",
            "bootstrap_reps": REPS, "bootstrap_seed": SEED}

def run():
    with tempfile.TemporaryDirectory() as tmp:
        spec = source.select_original(source.fetch_metadata())
        if spec["size"] != PIN_BYTES:
            raise ValueError("Original provider file byte count drift")
        path = Path(tmp) / source.SOURCE_NAME
        verified = source.get_original_file(spec, path)
        if verified["original_sha256"] != PIN_SHA256 or verified["bytes"] != PIN_BYTES:
            raise ValueError("Original MD5/SHA256/byte gate failed")
        # Source-only original ID/UTC audit BEFORE decoding non-Bangladesh positions.
        source_structure = source.inspect_source_ID_date_only(path)
        for study in STUDIES:
            if (source_structure["source_study_individual_counts"].get(study) != KNOWN_ID_COUNTS[study]
                or source_structure["source_study_GPS_fix_counts"].get(study) != KNOWN_FIX_COUNTS[study]):
                raise ValueError("Frozen original study ID/fix inventory drift: " + study)
        daily, qa = parse_gps(path)
        events, candidate_support = make_events(daily)
        scored, forecast_audit = predict(events, daily)
        outcome = summarize(scored)
    return {
        "study": "v30-frozen-four-non-Bangladesh-original-duck-study-movement-state-holdout",
        "protocol": PROTOCOL, "protocol_commit_before_new_outcome":
             "217f8268505347798cd124d37213c4ca366bc09d",
        "source_original_sha256": PIN_SHA256, "original_bytes": PIN_BYTES,
        "source_original_MD5": source.ORIGINAL_PROVIDER_MD5,
        "pre_outcome_source_ID_count_verification": {
             "study_ID_counts": KNOWN_ID_COUNTS, "source_valid_fix_counts": KNOWN_FIX_COUNTS},
        "source_quality": qa, "candidate_source_support": candidate_support,
        "forecast_history_gate": forecast_audit, "observed_result": outcome,
        "status": outcome["status"], "previous_v23_v29_results_unchanged": True,
        "no_animal_IDs_positions_timestamps_daily_values_exported": True,
        "claim_limits": [
            "Four previously unopened field studies from one published source archive, not four independent releases",
            "No measured food, prey, habitat availability, weather exposure or social contacts",
            "Only forecast of next-day GPS spatial spread for previously observed individuals, not animal choices or niche segregation",
            "Only four nonrandom study groups; study bootstrap cannot establish global transfer",
            "No tuned models, parameters, sectors, seasonal strata or post-result rescues",
        ]}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("validation_v30/results/four_study_holdout_v30.json"))
    a = ap.parse_args()
    result = run()
    data = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=a.out.parent,
                                     prefix=".v30-", delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(data)
    os.replace(temp_path, a.out)
    print("V30_SOURCE_AND_GATES", json.dumps(result["forecast_history_gate"], sort_keys=True))
    print("V30_STATUS", result["status"])
    if result["observed_result"].get("any_predictive_score_exported"):
        print("V30_FROZEN_COMPARISONS", json.dumps(
             result["observed_result"]["frozen_comparisons"], sort_keys=True))
    else:
        print("V30_NO_POOLED_SCORES", json.dumps(
             result["observed_result"]["support"], sort_keys=True))

if __name__ == "__main__":
    main()
