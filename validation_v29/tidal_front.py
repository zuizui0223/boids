"""v29 tide-front feature contract and known-truth ablation (NOT field evidence).

Uses UTC only and measured/predicted water heights in the SAME vertical datum as
patch elevation. A gauge observation interpolated using the next sample is for
retrospective description only, never a strictly prospective forecast.
"""
from __future__ import annotations

import bisect
import csv
import json
import math
import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

UTC = timezone.utc


def utc_timestamp(value: str) -> datetime:
    value = value.strip().replace("Z", "+00:00")
    stamp = datetime.fromisoformat(value)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone (UTC recommended)")
    return stamp.astimezone(UTC)


class TideSeries:
    """Strictly ordered 10-minute-ish gauge or astronomical-prediction series."""

    def __init__(self, pairs, *, datum: str, provenance: str):
        if datum != "NAP_m":
            raise ValueError("Use explicitly verified NAP metre levels and elevation")
        if provenance not in ("observed", "predicted", "synthetic"):
            raise ValueError("Unrecognized tide provenance")
        self.times = []
        self.heights = []
        self.provenance = provenance
        for stamp, height in pairs:
            t = utc_timestamp(stamp) if isinstance(stamp, str) else stamp
            if t.tzinfo is None or t.utcoffset() is None:
                raise ValueError("Naive timestamp")
            t = t.astimezone(UTC)
            if self.times and t <= self.times[-1]:
                raise ValueError("Gauge times must increase without duplicates")
            if not math.isfinite(float(height)):
                raise ValueError("Nonfinite water height")
            self.times.append(t)
            self.heights.append(float(height))
        if len(self.times) < 3:
            raise ValueError("At least three tide observations are required")

    @classmethod
    def read_csv(cls, path, *, datum: str, provenance: str):
        with open(path, newline="", encoding="utf-8") as inp:
            rows = csv.DictReader(inp)
            if not {"timestamp_utc", "water_level_nap_m"} <= set(rows.fieldnames or ()):
                raise ValueError("Expected timestamp_utc,water_level_nap_m")
            return cls(((r["timestamp_utc"], r["water_level_nap_m"]) for r in rows), datum=datum, provenance=provenance)

    def at(self, stamp, *, max_gap_minutes=30):
        t = utc_timestamp(stamp) if isinstance(stamp, str) else stamp.astimezone(UTC)
        j = bisect.bisect_left(self.times, t)
        if j < len(self.times) and self.times[j] == t:
            return self.heights[j]
        if j == 0 or j == len(self.times):
            raise ValueError("Outside the available tide record")
        t0, t1 = self.times[j - 1], self.times[j]
        interval = (t1 - t0).total_seconds()
        if interval > 60 * max_gap_minutes:
            raise ValueError("Tide data gap exceeds admission threshold")
        fraction = (t - t0).total_seconds() / interval
        return self.heights[j - 1] + fraction * (self.heights[j] - self.heights[j - 1])

    def at_with_phase(self, stamp, *, lookback_minutes=20, tolerance_m_per_hour=0.012):
        t = utc_timestamp(stamp) if isinstance(stamp, str) else stamp.astimezone(UTC)
        current = self.at(t)
        previous = self.at(t - timedelta(minutes=lookback_minutes))
        rate = (current - previous) * 60.0 / lookback_minutes
        phase = 1 if rate > tolerance_m_per_hour else (-1 if rate < -tolerance_m_per_hour else 0)
        return current, phase, rate   # +1 flooding, -1 ebbing

    def exposure_age_hours(self, stamp, *, elevation_nap_m, max_hours=15):
        """Time since most recent wet-to-dry crossing; None if unidentifiable/wet.

        For the observational retrospective, crossing interpolation can use the
        adjacent gauge sample; this must not be mistaken for a live forecast.
        """
        t = utc_timestamp(stamp) if isinstance(stamp, str) else stamp.astimezone(UTC)
        current = self.at(t)
        z = float(elevation_nap_m)
        if z <= current:
            return None
        start = t - timedelta(hours=max_hours)
        j = bisect.bisect_left(self.times, t)
        hi_t, hi_h = t, current
        for k in range(j - 1, -1, -1):
            lo_t, lo_h = self.times[k], self.heights[k]
            if lo_t < start:
                return None
            gap = (hi_t - lo_t).total_seconds()
            if gap > 30 * 60:
                return None
            if lo_h >= z > hi_h:
                weight = (lo_h - z) / (lo_h - hi_h)
                crossed = lo_t + (hi_t - lo_t) * weight
                return (t - crossed).total_seconds() / 3600.0
            hi_t, hi_h = lo_t, lo_h
        return None

    def patch_features(self, stamp, *, elevation_nap_m, slope_m_per_m):
        """Signed front distance: positive is currently dry, not prey availability."""
        if not (0.0001 <= slope_m_per_m <= 0.3):
            raise ValueError("Local shore slope must be measured, positive and plausible")
        h, phase, rate = self.at_with_phase(stamp)
        dry = elevation_nap_m > h
        age = self.exposure_age_hours(stamp, elevation_nap_m=elevation_nap_m)
        return dict(water_level_nap_m=h, ebb_flood_phase=phase, rate_m_per_h=rate,
                    patch_elevation_nap_m=elevation_nap_m,
                    front_distance_m=(elevation_nap_m - h) / slope_m_per_m,
                    exposed=int(dry), exposure_age_h=age,
                    exposure_age_known=int(age is not None))


def design(row, level):
    h = row["water_level_nap_m"]
    z = row["patch_elevation_nap_m"]
    phase = row["ebb_flood_phase"]
    out = [1., h, h*h, z, int(z > h), row["x_rd_m"] / 100000.,
           row["y_rd_m"] / 100000., row["solar_sin"], row["solar_cos"]]
    if level >= 1:
        out += [phase, phase*h, row["rate_m_per_h"]]
    if level >= 2:
        age = row["exposure_age_h"]
        out += [min(15., age if age is not None else 15.),
                0. if age is None else math.exp(-age / 1.5),
                row["exposure_age_known"], row["front_distance_m"] / 100.]
    return out


def _ridge_predict(train, test, level):
    x = np.array([design(r, level) for r in train], dtype=float)
    z = np.array([design(r, level) for r in test], dtype=float)
    y = np.array([r["response"] for r in train])
    means = x[:, 1:].mean(0)
    sd = x[:, 1:].std(0)
    sd[sd < 1e-9] = 1.0
    x[:, 1:] = (x[:, 1:] - means) / sd
    z[:, 1:] = (z[:, 1:] - means) / sd
    counts = Counter(r["individual_id"] for r in train)
    weights = np.array([1. / counts[r["individual_id"]] for r in train])
    weights *= len(train) / weights.sum()  # equal total weight per bird
    penalty = np.eye(x.shape[1]) * 1.0
    penalty[0, 0] = 0.
    betas = np.linalg.solve(x.T @ (x * weights[:, None]) + penalty, x.T @ (weights*y))
    return z @ betas


def compare_levels(rows):
    """Chronological block holdout, one-week embargo, equal-bird test MSE.

    No social M3: neighbor interaction is not observable from an hourly product.
    Same-source re-training & feature-selection after heldout outcomes is not
    a confirmatory test. This function is a v29 demonstration, not preregistered
    on any real GPS/gauge source.
    """
    rows = sorted(rows, key=lambda x: x["timestamp_utc"])
    blocks = sorted(set(r["timestamp_utc"].date().toordinal() // 7 for r in rows))
    if len(blocks) < 8:
        raise ValueError("At least eight distinct weekly blocks are necessary")
    split = int(0.7 * len(blocks))
    trainblocks = set(blocks[:split])
    testblocks = set(blocks[split + 1:])  # one-week embargo
    train = [r for r in rows if r["timestamp_utc"].date().toordinal() // 7 in trainblocks]
    test = [r for r in rows if r["timestamp_utc"].date().toordinal() // 7 in testblocks]
    if not train or not test:
        raise ValueError("Insufficient independent evaluation periods")
    reports = {}
    for level in range(3):
        preds = _ridge_predict(train, test, level)
        loss_per_bird = {}
        for bird in sorted({r["individual_id"] for r in test}):
            idx = [i for i, r in enumerate(test) if r["individual_id"] == bird]
            loss_per_bird[bird] = float(np.mean([(test[i]["response"] - preds[i])**2 for i in idx]))
        reports[f"M{level}"] = {"equal_bird_mse": float(np.mean(list(loss_per_bird.values()))),
                                "individual_losses": loss_per_bird}
    return {"n_train_rows": len(train), "n_test_rows": len(test),
            "n_test_individuals": len(reports["M0"]["individual_losses"]),
            "n_week_blocks": len(blocks), "embargo_week_blocks": 1,
            "models": reports, "gain_M0_M1": reports["M0"]["equal_bird_mse"] - reports["M1"]["equal_bird_mse"],
            "gain_M1_M2": reports["M1"]["equal_bird_mse"] - reports["M2"]["equal_bird_mse"]}


def known_truth(seed=29, *, months=3, age_effect=0.36):
    """Toy response generator with NO social/Boids force and explicit age effect."""
    rng = random.Random(seed)
    start = datetime(2020, 1, 1, tzinfo=UTC)
    n_ten_minutes = months * 30 * 24 * 6
    pairs = []
    for k in range(n_ten_minutes):
        hour = k / 6
        amplitude = 0.62 + 0.17 * math.cos(2*math.pi*hour / (14.77*24))
        h = 0.09 + amplitude*math.cos(2*math.pi*hour / 12.42) + 0.09*math.sin(2*math.pi*hour / (3.1*24))
        pairs.append((start + timedelta(minutes=k*10), h))
    tide = TideSeries(pairs, datum="NAP_m", provenance="synthetic")
    rows = []
    for k in range(48*6, n_ten_minutes-1, 6):
        t = pairs[k][0]
        solar = 2*math.pi * (t.hour + t.minute/60)/24
        for bird in range(12):
            elevation = -0.48 + 0.10 * bird
            p = tide.patch_features(t, elevation_nap_m=elevation, slope_m_per_m=0.006)
            age = p["exposure_age_h"]
            age_score = math.exp(-age/1.5) if age is not None else 0.
            # On purpose, the withheld mechanism contributes to the outcome.
            response = (0.90 + 0.14*p["water_level_nap_m"] + 0.12*p["ebb_flood_phase"]
                        + 0.05*p["water_level_nap_m"]*p["ebb_flood_phase"]
                        + age_effect*age_score + 0.025*math.sin(solar)
                        + (bird - 5.5)*0.006 + rng.gauss(0, 0.09))
            rows.append(dict(p, timestamp_utc=t, individual_id=f"toy_bird_{bird:02d}",
                             x_rd_m=200000. + bird*250., y_rd_m=600000. + bird*30.,
                             solar_sin=math.sin(solar), solar_cos=math.cos(solar), response=response))
    return tide, rows


def social_free_alignment(seed=29, n=64):
    """Independent agents share a phase-dependent target, no neighbor variables."""
    rng = random.Random(seed)
    def resultant(angles):
        return math.hypot(sum(math.cos(t) for t in angles),
                          sum(math.sin(t) for t in angles)) / len(angles)
    tide_synced = [rng.gauss(0., 0.24) for _ in range(n)]
    phase_shuffled = [rng.choice([0, math.pi]) + rng.gauss(0., 0.24) for _ in range(n)]
    return {"same_tide_alignment": resultant(tide_synced),
            "asynchronous_phase_alignment": resultant(phase_shuffled),
            "social_interaction_coefficient": 0.0}



def load_hourly_gps_steps(gps_path, tide: TideSeries):
    """Retrospective **observed horizontal displacement**, not feeding or flight.

    Input must already be projected in EPSG:28992 RD New metres and joined to
    measured LiDAR cell elevations in NAP metres and local shore gradients.
    Rejects absent schema, duplicated fix times, coordinates out of RD bounds,
    and uninterpretable gaps. Positions themselves are NEVER stored in receipts.
    """
    required = {"individual_id", "timestamp_utc", "x_rd_m", "y_rd_m",
                "elevation_nap_m", "slope_m_per_m"}
    fixes = {}
    with open(gps_path, newline="", encoding="utf-8") as file:
        source = csv.DictReader(file)
        if not required <= set(source.fieldnames or ()):
            raise ValueError(f"GPS standardized CSV missing: {sorted(required - set(source.fieldnames or ())) }")
        for r in source:
            ident = r["individual_id"].strip()
            if not ident:
                raise ValueError("Empty individual ID")
            t = utc_timestamp(r["timestamp_utc"])
            x, y = float(r["x_rd_m"]), float(r["y_rd_m"])
            z, slope = float(r["elevation_nap_m"]), float(r["slope_m_per_m"])
            if not all(map(math.isfinite, (x, y, z, slope))):
                raise ValueError("Nonfinite GPS, DEM or gradient")
            if not (-7000. <= x <= 300000. and 289000. <= y <= 630000.):
                raise ValueError("Coordinates not plausible as EPSG:28992 RD New metres")
            fixes.setdefault(ident, []).append((t, x, y, z, slope))
    results = []
    dropped = Counter()
    for ident, tracks in fixes.items():
        tracks.sort(key=lambda r: r[0])
        if len(set(t for t, *_ in tracks)) != len(tracks):
            raise ValueError("Duplicate GPS time for one animal")
        for a, b in zip(tracks, tracks[1:]):
            t, x, y, z, slope = a
            t2, x2, y2, _, _ = b
            dt_hours = (t2-t).total_seconds() / 3600.
            if not 0.5 <= dt_hours <= 2.:
                dropped["wrong_fix_gap"] += 1
                continue
            kmph = math.hypot(x2-x, y2-y) / (1000*dt_hours)
            if kmph > 120.:
                dropped["implausible_displacement"] += 1
                continue
            try:
                row = tide.patch_features(t, elevation_nap_m=z, slope_m_per_m=slope)
            except ValueError:
                dropped["unmatched_gauge_or_dem"] += 1
                continue
            solar = 2*math.pi * (t.hour + t.minute/60.) / 24.
            results.append(dict(row, individual_id=ident, timestamp_utc=t,
                                x_rd_m=x, y_rd_m=y, solar_sin=math.sin(solar), solar_cos=math.cos(solar),
                                response=math.log1p(kmph)))
    return results, {"raw_fixes": sum(map(len, fixes.values())),
                     "retained_steps": len(results),
                     "n_individuals_retained": len({r["individual_id"] for r in results}),
                     "dropped": dict(dropped),
                     "outcome_unit": "log1p(projected_horizontal_displacement_km_per_hour)",
                     "movement_not_feeding": True}


def run_real(gps_csv, tide_csv, *, path=None):
    tide = TideSeries.read_csv(tide_csv, datum="NAP_m", provenance="observed")
    rows, audit = load_hourly_gps_steps(gps_csv, tide)
    if not rows:
        raise ValueError("No admitted observed GPS steps")
    report = compare_levels(rows)
    report.update({"source_status": "OBSERVED_RETROSPECTIVE_ASSOCIATION_ONLY",
                   "water_gauge_source": "caller_supplied_observed_unverified_bytes",
                   "gps_source": "caller_supplied_projected_unverified_bytes",
                   "social_M3": "NOT_ADMITTED_hourly_synchronous_neighbor_gate",
                   "data_audit": audit})
    if path is not None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    return report

def run_known_truth(path=None):
    tide, rows = known_truth()
    result = compare_levels(rows)
    result.update({"evidence": "SYNTHETIC_KNOWN_TRUTH_ONLY",
                   "gps_observed": False, "tide_observed": False,
                   "generator_has_social_interactions": False,
                   "source_tide_points": len(tide.times),
                   "social_free_alignment": social_free_alignment(),
                   "no_social_model_M3": "NOT_ADMITTED_without_synchronized_neighbors"})
    if path is not None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="validation_v29/results/tidal_front_known_truth_v29.json")
    parser.add_argument("--gps-csv", help="projected+DEM-joined validated GPS rows; real data only")
    parser.add_argument("--tide-csv", help="10-min measured NAP tide, UTC; real data only")
    args = parser.parse_args()
    if bool(args.gps_csv) != bool(args.tide_csv):
        parser.error("--gps-csv and --tide-csv must both be supplied")
    r = run_real(args.gps_csv, args.tide_csv, path=args.output) if args.gps_csv else run_known_truth(args.output)
    print(json.dumps({"M0": r["models"]["M0"]["equal_bird_mse"],
                      "M1": r["models"]["M1"]["equal_bird_mse"],
                      "M2": r["models"]["M2"]["equal_bird_mse"],
                      "gain_M1_M2": r["gain_M1_M2"],
                      "status": r.get("evidence", r.get("source_status"))}, sort_keys=True))