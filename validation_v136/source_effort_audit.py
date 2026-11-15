"""v136 effort-denominator and original-paper lineage gate (stdlib only)."""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from math import log
from pathlib import Path

FLOODED = 324
DRY = 5112
FOUR = {"flooded|day", "flooded|night", "dry|day", "dry|night"}
EXPECTED = {
    "RETAINED_SIGNED": 1,
    "RETAINED_OTHER_SCALE": 2,
    "TESTED_DROPPED": 2,
    "NO_RETAINED_CROSS": 15,
}

def hypothetical_rate_ratio(p):
    """Not observed effect: assumes common flooded effort proportion at all sites."""
    if not 0 < p < 1:
        raise ValueError("flooded effort proportion must be in (0,1)")
    return (FLOODED / DRY) * (1 - p) / p

def four_cell_log_did(cells):
    """Exploratory point statistic for complete four-cell event RATE data only.

    No uncertainty, zero-event model, detection correction, site weighting or
    ecological interpretation is supplied by this function.
    """
    if set(cells) != FOUR:
        raise ValueError("all four tide x diel cells required")
    r = {}
    for key in FOUR:
        c = cells[key]
        if not isinstance(c, dict) or "events" not in c or "effort_hours" not in c:
            raise ValueError("event counts AND effective sampled hours required")
        n, e = c["events"], c["effort_hours"]
        if (not isinstance(n, (int, float)) or not isinstance(e, (int, float))
                or n <= 0 or e <= 0):
            raise ValueError("positive counts and exposure required; zeros need model")
        r[key] = log(n / e)
    return r["flooded|night"] - r["dry|night"] - r["flooded|day"] + r["dry|day"]

def audit(root):
    studies = json.loads((root / "validation_v134/results/normalized_study_decisions.json").read_text())
    with (root / "validation_v134/results/reported_numeric_records.csv").open(newline="") as handle:
        numeric = list(csv.DictReader(handle))
    cases = json.loads((root / "validation_v135/interaction_casebook.json").read_text())
    labels = json.loads((root / "validation_v136/cross_cycle_classification.json").read_text())
    joint = [x for x in studies if x["decision"] == "FIELD_JOINT_TIDE_DIEL"]
    if (len(studies), len(numeric), len(cases), len(joint)) != (118, 311, 6, 20):
        raise AssertionError("Frozen source totals changed")
    original = {x["doi"].lower(): x for x in joint}
    if len(original) != 20 or len(labels) != 20 or set(original) != {x["doi"].lower() for x in labels}:
        raise AssertionError("20 distinct joint-study DOIs must match")
    for x in labels:
        prior = original[x["doi"].lower()]
        if (x["original_source_status"] != prior["joint_model_status"]
                or x["original_endpoint"] != prior["endpoint_family"]):
            raise AssertionError("Original model or endpoint changed")
    tiers = Counter(x["tier"] for x in labels)
    if dict(tiers) != EXPECTED:
        raise AssertionError("Cross model status requires source re-review")
    bools = sum(isinstance(x["joint_model_status"], bool) for x in joint)
    if bools != 5:
        raise AssertionError("Legacy boolean flags changed")
    if any(x["physical_contrast_ready"] for x in cases):
        raise AssertionError("v135 did not find common harmonizable physical interaction")
    return {
        "frozen_counts": {"primary_studies": 118, "reported_numeric_records": 311,
                          "joint_field_studies": 20, "v135_curated_coasts": 6,
                          "legacy_boolean_model_flags": bools},
        "joint_model_tiers": dict(sorted(tiers.items())),
        "corpus_exhaustive_or_unbiased": False,
        "raposa_2026": {
            "doi": "10.1002/ece3.72872", "study_sites": 32,
            "camera_stations": 109, "flood_comparison_sites": 26,
            "flooded_animal_observations": FLOODED, "dry_animal_observations": DRY,
            "observed_count_ratio_not_rate": round(FLOODED / DRY, 6),
            "hypothetical_flooded_effort_share_neutral_rate": round(FLOODED / (FLOODED + DRY), 6),
            "hypothetical_sensitivity": [
                {"flooded_effort_fraction": p,
                 "illustrative_count_rate_ratio": round(hypothetical_rate_ratio(p), 6)}
                for p in (0.03, 0.05, 0.10, 0.25, 0.50)],
            "verified_flood_dry_effort_hours": None,
            "verified_diel_by_tide_effort_hours": None,
            "appendix_s1_raw_verified": False,
            "empirical_rate_estimate": "NOT_ESTIMATED",
        },
        "global_pooled_tide_solar_interaction": "NOT_ESTIMATED",
        "admission_rule": "All four tide x night exposure hours; station, day, site IDs; detection and within-site uncertainty",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = audit(args.root)
    output = args.root / "validation_v136/results/effort_audit.json"
    if args.check:
        assert json.loads(output.read_text()) == result, "Saved results differ from frozen source regeneration"
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "joint": 20, "retained": 3,
                      "empirical_effect": result["raposa_2026"]["empirical_rate_estimate"],
                      "meta": result["global_pooled_tide_solar_interaction"]}))

if __name__ == "__main__":
    main()
