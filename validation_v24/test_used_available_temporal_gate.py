"""v24-A3 original brood use/available vs age-only source contradiction tests."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import used_available_temporal_gate as v


class TestTemporalChoiceAdmission(unittest.TestCase):
    def synth(self, d: str):
        use = Path(d) / v.SELECTION_FILE
        move = Path(d) / v.MOVEMENT_FILE
        with use.open("w", newline="") as file:
            fields = [
                "Species", "Used", "Weight", "Brood ID", "Wetland ID",
                "Wetland Type", "Dominant Veg Category", "Percent Veg of Unit",
                "Salinity Concentration", "Wetland Area", "Year",
                "Water Map Time Period",
            ]
            wr = csv.DictWriter(file, fieldnames=fields)
            wr.writeheader()
            for b in ("B1", "B2"):
                for lab in ("1", "0", "0"):
                    wr.writerow({
                        "Species": "Mallard", "Used": lab,
                        "Weight": 1 if lab == "1" else 1000,
                        "Brood ID": b, "Wetland ID": "W1" if lab == "1" else "",
                        "Wetland Type": "seasonal",
                        "Dominant Veg Category": "cattail",
                        "Percent Veg of Unit": 80, "Salinity Concentration": 13,
                        "Wetland Area": 10000, "Year": 2018,
                        "Water Map Time Period": "Spring",
                    })
        with move.open("w", newline="") as file:
            fields = ["Species", "Year", "Species Year", "Brood ID",
                      "Duckling Age", "Distance from Nest"]
            wr = csv.DictWriter(file, fieldnames=fields)
            wr.writeheader()
            for b in ("B1", "B2", "B3"):
                for age in (2, 5, 9):
                    wr.writerow({"Species": "Mallard", "Year": 2018,
                                 "Species Year": "Mallard 2018",
                                 "Brood ID": b, "Duckling Age": age,
                                 "Distance from Nest": 1234.56})
        return use, move

    def test_original_source_separates_habitat_choice_from_dated_movement(self):
        with tempfile.TemporaryDirectory() as temp:
            u, m = self.synth(temp)
            sel, ids = v.source_use_avail_structure(u)
            move = v.source_movement_structure(m, ids)
        self.assertEqual(sel["source_used_and_available_rows"],
                         {"used": 2, "available": 4})
        self.assertFalse(sel["original_visit_dates_or_ages_present_in_selection"])
        self.assertEqual(sel["wetland_ID_missing_counts_by_original_label"],
                         {"used": 0, "available": 4})
        self.assertFalse(move["source_has_wetland_ID"])
        self.assertEqual(move["source_broods_present_in_both_original_tables"], 2)
        self.assertTrue(move["movement_broods_with_3_or_more_age_categories"] == 3)
        self.assertFalse(sel["record_level_wetland_or_environment_numeric_values_read"])
        self.assertFalse(move["raw_distance_from_nest_values_read"])

    def test_all_original_brood_labels_must_be_binary(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = self.synth(d)
            content = a.read_text()
            # Modifying only the source label column is enough to stop.
            a.write_text(content.replace("Mallard,1,", "Mallard,maybe,", 1))
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                v.source_use_avail_structure(a)

    def test_original_filename_and_stop_threshold_pins(self):
        self.assertEqual(v.MIN_HISTORY_DATES_PER_BROOD, 3)
        self.assertEqual(v.MIN_FUTURE_DATED_CHOICES, 200)
        self.assertEqual(v.MIN_INDEPENDENT_BROODS, 8)
        self.assertEqual(v.SELECTION_FILE,
                         "Duckling_Habitat_Selection_Dataset.csv")
        self.assertEqual(v.MOVEMENT_FILE,
                         "Duckling_Movement_Dataset.csv")


if __name__ == "__main__":
    unittest.main()
