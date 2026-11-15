"""v147 source-real calendar-year stability of the v145 restricted day-shift chorus overlap.

EXPLORATORY AFTER v145/v146 SITE-LEVEL SIGNALS WERE SEEN.
Original 60 Dryad workbooks reacquired and each frozen v142 member SHA256 verified
via unchanged v144.full9_temporal.original(). No raw data redistributed.

No true acoustic source audibility calibration, physical tide, independent
biological coasts, or individual fish; no new p-values or inferred social force.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validation_v145"))
from v145_blockshift import (
    original, TYPES, eligible_complete_days, contiguous_runs,
    hour_mask, score_by_all_rotations
)

SOURCE_V145 = ROOT / "validation_v145/results/source_blockshift_cochorus_null.json"
SAVED_OUTPUT = Path(__file__).parent / "results/source_year_stability_v147.json"

# Chosen as a transparent exploratory opportunity rule, before the v147
# per-year observed/expected table was produced. NOT a confirmatory study gate.
MIN_YEAR_HOURS = 24 * 60
MIN_YEAR_TYPE_POSITIVE_HOURS = 50
MIN_YEAR_EXPECTED_PAIR_HOURS = 5.0
MIN_YEAR_MONTH_RUNS = 2

def pair_label(a, b):
    return a + " | " + b

def each_year_complete_run_masks(item):
    """Year is LOCAL calendar year; no run crosses local year/month."""
    filtered = item["nominal"] - item["off"] - item["noise"]
    days = eligible_complete_days(filtered)
    runs = contiguous_runs(days)
    out = defaultdict(list)
    for run in runs:
        assert len({(d.year, d.month) for d in run}) == 1
        year = run[0].year
        masks = {t: [hour_mask(days[d], item["fish"].get(t, set())) for d in run]
                 for t in TYPES}
        out[year].append(masks)
    return dict(out), runs

def score_year(site, year, mats):
    nhours = sum(24 * len(m[TYPES[0]]) for m in mats)
    positives = {t: sum(w.bit_count() for m in mats for w in m[t]) for t in TYPES}
    source = {"site": site, "local_year": year,
              "source_hours": nhours, "source_days": nhours // 24,
              "source_contiguous_yearmonth_runs": len(mats),
              "positive_hours_by_type": positives,
              "source_effort_is_not_audibility_calibrated": True}
    pairs = []
    for a, b in combinations(TYPES, 2):
        rotated = [score_by_all_rotations(m[a], m[b]) for m in mats]
        observed = sum(ss[0] for ss in rotated)
        expected = sum(sum(ss) / len(ss) for ss in rotated)
        supported = (nhours >= MIN_YEAR_HOURS
                     and len(mats) >= MIN_YEAR_MONTH_RUNS
                     and positives[a] >= MIN_YEAR_TYPE_POSITIVE_HOURS
                     and positives[b] >= MIN_YEAR_TYPE_POSITIVE_HOURS
                     and expected >= MIN_YEAR_EXPECTED_PAIR_HOURS)
        pairs.append({
            "site": site, "local_year": year, "chorus_A": a, "chorus_B": b,
            "source_hours": nhours, "source_yearmonth_runs": len(mats),
            "positive_A": positives[a], "positive_B": positives[b],
            "observed": observed, "exact_shift_expected": round(expected, 8),
            "observed_over_expected": round(observed / expected, 6) if expected > 0 else None,
            "admitted_exploratory_year": supported,
            "status": "SUPPORTED_DESCRIPTIVE_YEAR" if supported else "STOP_YEAR_SOURCE_SUPPORT",
        })
    return source, pairs

def analyze():
    frozen = json.loads(SOURCE_V145.read_text())
    if (frozen["screened_site_pairs"] != 32 or
        frozen["source_original_workbook_SHA_verified_all_60"] is not True or
        frozen["sites"] != 9 or frozen["original_deployments"] != 60):
        raise AssertionError("Frozen v145 source provenance and design changed")
    source = original()
    if set(source) != {row["site"] for row in frozen["source_site_block_qc"]}:
        raise AssertionError("Unexpected source site codes")
    sites, years, pairs = [], [], []
    for site, item in sorted(source.items()):
        year_mats, original_runs = each_year_complete_run_masks(item)
        site_hours = sum(24 * len(m[TYPES[0]]) for ms in year_mats.values() for m in ms)
        site_blocks = sum(len(ms) for ms in year_mats.values())
        ref_site = next(x for x in frozen["source_site_block_qc"] if x["site"] == site)
        if site_hours != ref_site["selected_source_eligible_hours"]:
            raise AssertionError("Source v145 7-day hour totals differ for " + site)
        if site_blocks != ref_site["continuous_local_yearmonth_run_blocks_7days_plus"]:
            raise AssertionError("Source v145 7-day run counts differ for " + site)
        if site_blocks != len(original_runs):
            raise AssertionError("Unexpected run partition")
        sites.append({"site": site, "retained_source_hours": site_hours,
                      "n_local_years": len(year_mats),
                      "source_7day_yearmonth_runs": site_blocks,
                      "years": sorted(year_mats)})
        for year, mats in sorted(year_mats.items()):
            y, pp = score_year(site, year, mats)
            years.append(y)
            pairs.extend(pp)

    # Lossless additive decomposition of all NINETY original v145 site-pairs:
    # no event-level source values or outcomes are changed, not merely selected
    # favorable 32 diagnostic comparisons.
    index = {(r["site"], r["chorus_A"], r["chorus_B"]): []
             for r in frozen["per_site_type_pair"]}
    if len(index) != 90:
        raise AssertionError("Source pair keys are not 9x10 unique")
    for r in pairs:
        index[(r["site"], r["chorus_A"], r["chorus_B"])].append(r)
    for fr in frozen["per_site_type_pair"]:
        key = fr["site"], fr["chorus_A"], fr["chorus_B"]
        sub = index[key]
        obs = sum(x["observed"] for x in sub)
        exp = sum(x["exact_shift_expected"] for x in sub)
        if obs != fr["observed_same_hour_chorusing_in_retained_blocks"]:
            raise AssertionError("Year decomposition changed original observed O " + str(key))
        if abs(exp - fr["exact_shift_null_expected_same_hour_hours"]) > 0.00004:
            raise AssertionError("Year decomposition changed original exact E " + str(key))

    evidence = []
    for fr in frozen["per_site_type_pair"]:
        key = (fr["site"], fr["chorus_A"], fr["chorus_B"])
        rr = sorted(index[key], key=lambda x: x["local_year"])
        eligible = [x for x in rr if x["admitted_exploratory_year"]]
        positive = sum(x["observed"] > x["exact_shift_expected"] for x in eligible)
        negative = sum(x["observed"] < x["exact_shift_expected"] for x in eligible)
        whole_o = fr["observed_same_hour_chorusing_in_retained_blocks"]
        whole_e = fr["exact_shift_null_expected_same_hour_hours"]
        leave_year_out = []
        for x in rr:
            o, e = whole_o - x["observed"], whole_e - x["exact_shift_expected"]
            others = [k for k in rr if k["local_year"] != x["local_year"]]
            leave_year_out.append({
                "excluded_year": x["local_year"],
                "other_years": len(others),
                "other_source_hours": sum(y["source_hours"] for y in others),
                "O": o,
                "E": round(e, 6),
                "O_over_E": round(o/e, 6) if e > 1e-7 else None,
            })
        evidence.append({
            "site": key[0], "chorus_A": key[1], "chorus_B": key[2],
            "frozen_v145_screened": fr["status"] == "SCREENED_RESTRICTED_SHIFT_NULL",
            "frozen_all_year_ratio": round(whole_o / whole_e, 6) if whole_e > 0 else None,
            "all_year_source_years": len(rr),
            "admitted_exploratory_years": len(eligible),
            "positive_admitted_years": positive,
            "negative_admitted_years": negative,
            "equal_admitted_years": len(eligible)-positive-negative,
            "calendar_years_supported": [x["local_year"] for x in eligible],
            "all_year_site_pair_detail": rr,
            "leave_one_calendar_year_out": leave_year_out,
            "interpretation": "year stability of acoustic coincidence only; no independent years/individuals as ecological studies",
        })

    chosen = {}
    for b in ("UF440", "White Seabass"):
        target = [r for r in evidence
                  if r["chorus_A"] == "Bocaccio"
                  and r["chorus_B"] == b and r["frozen_v145_screened"]]
        chosen[b] = {
            "sites_frozen_v145_screened": len(target),
            "sites_with_2_or_more_admitted_years": sum(r["admitted_exploratory_years"] >= 2 for r in target),
            "sites_with_2_or_more_admitted_years_all_same_positive":
                sum(r["admitted_exploratory_years"] >= 2
                    and r["positive_admitted_years"] == r["admitted_exploratory_years"] for r in target),
            "sites_with_2_or_more_admitted_years_all_same_negative":
                sum(r["admitted_exploratory_years"] >= 2
                    and r["negative_admitted_years"] == r["admitted_exploratory_years"] for r in target),
            "admitted_site_years": sum(r["admitted_exploratory_years"] for r in target),
            "positive_admitted_site_years": sum(r["positive_admitted_years"] for r in target),
            "negative_admitted_site_years": sum(r["negative_admitted_years"] for r in target),
            "per_site": [{"site": r["site"], "site_all_year_ratio": r["frozen_all_year_ratio"],
                          "n_years": r["admitted_exploratory_years"],
                          "positive_years": r["positive_admitted_years"],
                          "negative_years": r["negative_admitted_years"],
                          "admitted_years": [
                              {"year": z["local_year"], "ratio": z["observed_over_expected"],
                               "source_hours": z["source_hours"]}
                              for z in r["all_year_site_pair_detail"] if z["admitted_exploratory_year"]
                          ],
                          "leave_one_year_out": [
                              {"year_removed": z["excluded_year"], "remaining_ratio": z["O_over_E"]}
                              for z in r["leave_one_calendar_year_out"]]}
                         for r in target],
        }

    out = {
        "version": "v147_exploratory_original_60workbooks_calendar_year_stability_1",
        "source_Dryad_DOI": "10.5061/dryad.q2bvq83sw",
        "source_SHA_matches_v142_all_members": True,
        "already_seen_site_pairs_from_v145_v146": True,
        "status": "POST_HOC_WITHIN_STUDY_CALENDAR_YEAR_DIAGNOSTIC",
        "source_eligibility": {"min_7plusday_full_day_source_hours": MIN_YEAR_HOURS,
                               "min_7plusday_consecutive_month_runs": MIN_YEAR_MONTH_RUNS,
                               "min_positive_chorus_hours_each": MIN_YEAR_TYPE_POSITIVE_HOURS,
                               "min_null_expected_overlap_hours": MIN_YEAR_EXPECTED_PAIR_HOURS},
        "site_quality": sites,
        "site_year_quality": years,
        "all_site_pair_calendar_years": evidence,
        "target_pair_yearly_pattern": chosen,
        "year_model_no_new_pvalues": True,
        "source_v145_90_site_pair_observed_and_expected_rebuilt_exactly": True,
        "n_source_sites": len(sites),
        "n_source_local_site_years": len(years),
        "n_v145_original_site_pairs": len(evidence),
        "selected_contiguous_hour_total": sum(s["retained_source_hours"] for s in sites),
        "selected_contiguous_run_total": sum(s["source_7day_yearmonth_runs"] for s in sites),
        "independent_biological_coasts_added": 0,
        "causal_acoustic_social_forces": "NOT_IDENTIFIED",
        "tide_solar_global_pooled_effect": "NOT_ESTIMATED",
    }
    if out["selected_contiguous_hour_total"] != 136032 or out["selected_contiguous_run_total"] != 275:
        raise AssertionError("v145 hard source source hour/run totals differ")
    return out

def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", action="store_true", help="Run original source and emit source-safe output chunks in CI logs")
    g.add_argument("--check", action="store_true", help="Run original source and compare to committed frozen output")
    args = parser.parse_args()
    result = analyze()
    exact = json.dumps(result, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    if args.check:
        if not SAVED_OUTPUT.is_file():
            raise AssertionError("Must first commit original v147 source output; fail-closed")
        old = json.loads(SAVED_OUTPUT.read_text())
        if old != result:
            raise AssertionError("Original v147 source-year output changed")
        print("V147_FROZEN_SOURCE_YEAR_CHECK_PASS")
    else:
        SAVED_OUTPUT.parent.mkdir(exist_ok=True, parents=True)
        SAVED_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        # Compact line chunks let an auditing connector reconstruct the actual
        # original-source result; source is aggregate-only, no original timestamps.
        chunk = 1800
        for i in range(0, len(exact), chunk):
            print("V147_JSON_CHUNK_%05d=" % (i//chunk) + exact[i:i+chunk])
    print("V147_DIAGNOSTIC_SUMMARY_START")
    print(json.dumps({"n_years": result["n_source_local_site_years"],
                      "n_site_pairs": result["n_v145_original_site_pairs"],
                      "n_hours": result["selected_contiguous_hour_total"],
                      "target_pair_yearly_pattern": result["target_pair_yearly_pattern"]},
                     ensure_ascii=True, sort_keys=True))
    print("V147_DIAGNOSTIC_SUMMARY_END")

if __name__ == "__main__":
    main()
