#!/usr/bin/env python3
"""v24-A3 independent *source design* identifiability, no habitat model scores.

Verify original USGS habitat use/available sample strata and radio-tagged
brood IDs. This reads only brood, year, chosen/available label, wetland ID,
water-map period and source Duckling Age; NEVER opens numeric vegetation,
salinity, area, distance-from-nest or precise animal locations.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import tempfile
from pathlib import Path

import sciencebase_source_gate as usgs
import source_file_schema_gate as original

SELECTION_FILE = "Duckling_Habitat_Selection_Dataset.csv"
MOVEMENT_FILE = "Duckling_Movement_Dataset.csv"
EXPECTED_LABELS = ("0", "1")
MIN_HISTORY_DATES_PER_BROOD = 3
MIN_FUTURE_DATED_CHOICES = 200
MIN_INDEPENDENT_BROODS = 8


def summarize_counts(x: list[int]) -> dict:
    if not x:
        return {"n": 0, "min": None, "median": None, "max": None}
    sorted_count = sorted(x)
    return {"n": len(sorted_count), "min": sorted_count[0],
            "median": sorted_count[len(sorted_count)//2],
            "max": sorted_count[-1]}


def source_use_avail_structure(selection: Path) -> tuple[dict, set[str]]:
    per_brood = collections.defaultdict(collections.Counter)
    used_wetlands = collections.defaultdict(set)
    source_years = collections.Counter()
    period_counts = collections.Counter()
    group_years = collections.defaultdict(set)
    label_counts = collections.Counter()
    missing_wetland = collections.Counter()
    with selection.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        expected = {
            "Species", "Used", "Weight", "Brood ID", "Wetland ID",
            "Wetland Type", "Dominant Veg Category", "Percent Veg of Unit",
            "Salinity Concentration", "Wetland Area", "Year",
            "Water Map Time Period",
        }
        names = set(reader.fieldnames or [])
        if names != expected:
            raise ValueError("Pinned original 12-column habitat design changed")
        for r in reader:
            brood = (r["Brood ID"] or "").strip()
            lab = (r["Used"] or "").strip()
            year = (r["Year"] or "").strip()
            wetland = (r["Wetland ID"] or "").strip()
            period = (r["Water Map Time Period"] or "").strip()
            if not brood or lab not in EXPECTED_LABELS or not year:
                raise ValueError("Incomplete original brood or used/available label")
            per_brood[brood][lab] += 1
            group_years[brood].add(year)
            label_counts[lab] += 1
            source_years[year] += 1
            period_counts[period] += 1
            if not wetland or wetland.lower() in ("na", "nan", "null", "missing"):
                missing_wetland[lab] += 1
            elif lab == "1":
                used_wetlands[brood].add(wetland)
    both = [b for b in per_brood if per_brood[b]["1"] > 0 and
            per_brood[b]["0"] > 0]
    only_used = sum(x["1"] > 0 and x["0"] == 0 for x in per_brood.values())
    only_available = sum(x["0"] > 0 and x["1"] == 0 for x in per_brood.values())
    # Per-use event date/day/age does not exist in source's 12 columns.
    visit_timestamp_fields = [c for c in names if c.lower() in (
        "visit_date", "date", "visit_time", "utc", "timestamp",
        "duckling age", "duckling_age", "age", "day")]
    return {
        "study": "SOURCE_USE_VS_AVAILABLE_BROOD_GRANULARITY_ONLY",
        "source_brood_count": len(per_brood),
        "source_used_and_available_rows": {
            "used": label_counts["1"], "available": label_counts["0"]},
        "source_year_row_counts": dict(sorted(source_years.items())),
        "source_water_map_period_count": len(period_counts),
        "source_broods_with_both_used_and_available": len(both),
        "source_broods_only_used": only_used,
        "source_broods_only_available": only_available,
        "per_brood_used_row_summary": summarize_counts([
            x["1"] for x in per_brood.values()]),
        "per_brood_available_row_summary": summarize_counts([
            x["0"] for x in per_brood.values()]),
        "wetland_ID_missing_counts_by_original_label": {
            "used": missing_wetland["1"],
            "available": missing_wetland["0"]},
        "broods_with_2_or_more_original_used_wetland_IDs": sum(
            len(v) >= 2 for v in used_wetlands.values()),
        "broods_with_multiple_source_years": sum(
            len(years) >= 2 for years in group_years.values()),
        "per_visit_dated_observation_field_names": visit_timestamp_fields,
        "original_visit_dates_or_ages_present_in_selection": bool(visit_timestamp_fields),
        "record_level_wetland_or_environment_numeric_values_read": False,
        "actual_brood_ID_and_wetland_ID_values_exported": False,
    }, set(per_brood)


def source_movement_structure(movement: Path,
                              selection_ids: set[str]) -> dict:
    broods = collections.defaultdict(set)
    age_count = collections.Counter()
    years = collections.Counter()
    with movement.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        expected = {
            "Species", "Year", "Species Year",
            "Brood ID", "Duckling Age", "Distance from Nest"}
        names = set(reader.fieldnames or [])
        if names != expected:
            raise ValueError("Original movement source column schema changed")
        rows = 0
        for r in reader:
            rows += 1
            brood = (r["Brood ID"] or "").strip()
            age = (r["Duckling Age"] or "").strip()
            if not brood or not age:
                raise ValueError("Movement source is missing brood/age label")
            broods[brood].add(age)
            age_count[age] += 1
            years[r["Year"]] += 1
    return {
        "source_movement_rows": rows,
        "source_unique_movement_broods": len(broods),
        "source_broods_present_in_both_original_tables":
            len(set(broods).intersection(selection_ids)),
        "source_broods_only_movement":
            len(set(broods) - selection_ids),
        "source_broods_only_selection":
            len(selection_ids - set(broods)),
        "movement_broods_with_3_or_more_age_categories": sum(
            len(a) >= 3 for a in broods.values()),
        "distinct_original_duckling_ages": len(age_count),
        "source_year_counts": dict(sorted(years.items())),
        "source_has_wetland_ID": ("Wetland ID" in names),
        "source_has_habitat_cover_salinity_and_area": all(
            x in names for x in (
                "Percent Veg of Unit", "Salinity Concentration", "Wetland Area")),
        "raw_distance_from_nest_values_read": False,
        "original_brood_identifiers_exported": False,
    }


def run() -> dict:
    item = None
    errs = []
    for url in usgs.SCIENCEBASE_ITEM_URLS:
        try:
            item = usgs.extract_item_metadata(usgs.bounded_json(url))
            break
        except Exception as exc:
            errs.append({"url": url, "reason": usgs.safe_failure(exc)})
    out = {
        "study": "v24-pinned-original-USGS-wetland-brood-time-grain-source-A3",
        "source_doi": usgs.SOURCE_DOI,
        "status": "NOT_ADMITTED_ORIGINAL_SOURCE_UNAVAILABLE",
        "source_access_errors": errs,
        "source_original_integrity": {},
        "source_use_available_structure": None,
        "source_movement_age_structure": None,
        "n_dated_original_future_wetland_choice_events_admitted": 0,
        "future_habitat_history_forecast_fitted": False,
        "source_habitat_effects_or_original_numeric_values_exported": False,
    }
    if item is None:
        return out
    files = original.select_original_files(item)
    with tempfile.TemporaryDirectory() as d:
        paths = {}
        for name in (SELECTION_FILE, MOVEMENT_FILE):
            file = Path(d) / name
            result = original.download_exact(files[name], file)
            paths[name] = file
            out["source_original_integrity"][name] = result
        sel, ids = source_use_avail_structure(paths[SELECTION_FILE])
        move = source_movement_structure(paths[MOVEMENT_FILE], ids)
    out["source_use_available_structure"] = sel
    out["source_movement_age_structure"] = move
    # No timed wetland identity in the movement table; no visit date/age
    # in the selection table. Matching only Brood ID creates a many-to-many
    # join and MUST NOT be interpreted as a dated wetland choice.
    can_match_future = (
        sel["original_visit_dates_or_ages_present_in_selection"] and
        move["source_has_wetland_ID"]
    )
    out["status"] = (
        "TEMPORAL_WETLAND_CHOICE_SCHEMA_ELIGIBLE_FOR_SEPARATE_PROTOCOL"
        if can_match_future else
        "NOT_ADMITTED_NO_DATED_WETLAND_CHOICE_OR_MATCHED_TEMPORAL_AVAILABILITY"
    )
    out["n_dated_original_future_wetland_choice_events_admitted"] = 0
    out["separate_undated_used_available_habitat_analysis_may_be_possible"] = (
        sel["source_broods_with_both_used_and_available"] >= MIN_INDEPENDENT_BROODS
        and sel["source_used_and_available_rows"]["used"] > 0
        and sel["source_used_and_available_rows"]["available"] > 0
    )
    out["warnings"] = [
        "USGS habitat-selection original rows contain Year and hatch-associated Water Map Time Period, not dates/ages of each used wetland point.",
        "USGS movement original rows contain Duckling Age and Distance from Nest, not Wetland ID or per-wetland habitat attributes.",
        "A Brood-ID-only join is many-to-many and CANNOT supply source-documented chronological wetland visits.",
        "USGS available sample points are generated within 2.4 km of original nest; they are not observed never-visited wetlands.",
        "The published available-point weight (1000) has a distinct survey-model meaning; never treat 74,000 generated points as independent animals."
    ]
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path,
        default=Path("validation_v24/results/used_available_temporal_design_v24.json"))
    a = p.parse_args()
    data = run()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(data, indent=2, sort_keys=True,
                                allow_nan=False) + "\n")
    print("V24_A3_SOURCE_DESIGN", json.dumps(data, sort_keys=True))
    print("V24_A3_NO_HABITAT_CHOICE_FORECAST")


if __name__ == "__main__":
    main()
