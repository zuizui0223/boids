"""Rebuild the v135 source-matched interaction inventory and within-coast habitat contrasts.

No cross-coast pooled effect is estimated. Output is source-conditional, not a
replacement for original-data reanalysis or an across-site sampling variance.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import NormalDist

SOURCE_DOI = "10.3390/ani13223548"
SCALE = "Log expected count per1SD tide height at mean standardized wind"
PLOVERS = {
    "Piping": ("Piping mudflat tide", "Piping beach tide", (-0.40, 0.15), (0.89, 0.06)),
    "Snowy": ("Snowy mudflat tide", "Snowy beach tide", (-0.45, 0.07), (0.17, 0.07)),
    "Wilson": ("Wilson mudflat tide", "Wilson beach tide", (-0.11, 0.03), (0.71, 0.05)),
}
LEVELS = {
    "reported_signed_interaction_beta_se": 2,
    "derived_point_covariance_missing": 1,
    "omnibus_only_no_signed_contrast": 1,
    "retained_nonlinear_nonadditivity_no_common_beta_se": 1,
    "signed_z_test_no_beta_se": 1,
}

def build(root: Path) -> dict:
    v134 = root / "validation_v134"
    decisions = json.loads((v134 / "results/normalized_study_decisions.json").read_text())
    with (v134 / "results/reported_numeric_records.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    source_index = json.loads((root / "validation_v133/source_evidence_index.json").read_text())
    casebook = json.loads((root / "validation_v135/interaction_casebook.json").read_text())
    assert len(decisions) == len({r["doi"] for r in decisions}) == 118
    assert len(rows) == 311
    assert sum(r["decision"] == "FIELD_JOINT_TIDE_DIEL" for r in decisions) == 20
    assert len(casebook) == len({r["doi"] for r in casebook}) == 6
    assert len({r["coast"] for r in casebook}) == 6
    old_dois = {r["doi"] for r in source_index["studies"]}
    new_dois = {r["doi"] for r in decisions}
    assert all(c["doi"] in (old_dois if c["study_source"] == "v133" else new_dois) for c in casebook)
    assert all(c["physical_contrast_ready"] is False for c in casebook)
    levels = {k: sum(c["level"] == k for c in casebook) for k in LEVELS}
    assert levels == LEVELS
    exact = [c for c in casebook if c["level"] == "reported_signed_interaction_beta_se"]
    assert {c["doi"] for c in exact} == {"10.1371/journal.pone.0080962", "10.3354/meps13389"}
    bream = [r for r in rows if r["doi"] == exact[0]["doi"] and r["label"] == "Diel·Tide (actual PAR × tide height)"]
    assert len(bream) == 1 and float(bream[0]["estimate"]) == exact[0]["effect"] and float(bream[0]["reported_se"]) == exact[0]["se"]

    # Original GLMs: log E[N_h] = intercept_h + beta_h*T + gamma_h*W + delta_h*T*W.
    # Same standardized tide and wind at one 38-survey island; W=0 is mean wind.
    # Independent shorebird species are NOT independent coast studies.
    p_rows = [r for r in rows if r["doi"] == SOURCE_DOI]
    lookup = {r["label"]: r for r in p_rows}
    assert len(lookup) == len(p_rows) and len(p_rows) == 8
    z = NormalDist().inv_cdf(1 - 0.05 / (2 * len(PLOVERS)))
    values = []
    for species, (mud_label, beach_label, mud_expected, beach_expected) in PLOVERS.items():
        mud, beach = lookup[mud_label], lookup[beach_label]
        for record, expected in ((mud, mud_expected), (beach, beach_expected)):
            assert record["scale_or_units"] == SCALE and record["role_as_extracted"] == "PUBLISHED_EFFECT"
            assert (float(record["estimate"]), float(record["reported_se"])) == expected
            assert record["meta_included"] == "False"
        delta = beach_expected[0] - mud_expected[0]
        se_lower = abs(beach_expected[1] - mud_expected[1])
        se_upper = beach_expected[1] + mud_expected[1]
        # Two displayed coefficients and two displayed SEs are each rounded to 0.01.
        # Conservatively widen delta by 0.01 and the SE upper bound by 0.01.
        rounded_se_upper = se_upper + 0.01
        low_log = delta - 0.01 - z * rounded_se_upper
        high_log = delta + 0.01 + z * rounded_se_upper
        values.append({
            "species": species,
            "mudflat_tide_coefficient": mud_expected[0],
            "mudflat_reported_se": mud_expected[1],
            "beach_tide_coefficient": beach_expected[0],
            "beach_reported_se": beach_expected[1],
            "beach_minus_mudflat_log_slope": round(delta, 6),
            "relative_beach_to_mudflat_ratio_per_1sd_tide": round(math.exp(delta), 6),
            "unknown_covariance_se_lower": round(se_lower, 6),
            "unknown_covariance_se_upper": round(se_upper, 6),
            "simultaneous_rounding_sensitivity_ratio_lower": round(math.exp(low_log), 6),
            "simultaneous_rounding_sensitivity_ratio_upper": round(math.exp(high_log), 6),
        })
    assert all(v["simultaneous_rounding_sensitivity_ratio_lower"] > 1 for v in values)
    return {
        "version": "v135-within-coast-contrast-and-meta-gate-1",
        "sources": {
            "v134_decision_records": len(decisions),
            "v134_joint_field_classifications": 20,
            "v134_numerical_records": len(rows),
            "v133_original_study_index": len(old_dois),
            "interaction_casebook_coasts": len(casebook),
            "interaction_casebook_level_counts": levels,
            "interaction_records_with_reported_signed_beta_and_se": len(exact),
            "physically_and_endpoint_harmonized_cross_coast_effects": 0,
            "global_pooled_effect": "NOT_ESTIMATED",
        },
        "plover": {
            "source_doi": SOURCE_DOI,
            "source_table": "Table 1",
            "study_units": "One barrier island; 38 morning surveys, three species, two habitats per species",
            "outcome": "Poisson log expected count; 1 pooled-standardized-SD tide increment, at wind=0",
            "normal_critical_z_two_sided_bonferroni_three": round(z, 9),
            "covariance_and_rounding_method": "Cauchy SE upper = se_beach+se_mudflat; each printed beta and SE allowed ±0.005; Bonferroni alpha=0.05 over three model-conditional comparisons",
            "contrasts": values,
            "meta_ready": False,
            "not_addressed": [
                "Overdispersion and serial dependence in the 38-survey original Poisson fits",
                "Covariance of overlapping responses and direct within-individual habitat transitions",
                "Change in total island abundance rather than conditional habitat counts",
                "Independent multi-coast transferability and any tide-by-day-night contrast",
            ],
        },
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    actual = build(args.root)
    output = args.root / "validation_v135/results/meta_feasibility_and_habitat_contrasts.json"
    if args.check:
        assert actual == json.loads(output.read_text()), "Saved v135 result disagrees with source-ledger recomputation"
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(actual, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "coasts": actual["sources"]["interaction_casebook_coasts"],
                      "pooled_effect": actual["sources"]["global_pooled_effect"],
                      "plover_species": len(actual["plover"]["contrasts"])}, ensure_ascii=False))

if __name__ == "__main__":
    main()
