"""v25-B3 synthetic source-only chronology, categorical labels and no outcomes."""
from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import usgs_step_strata_gate as v


class FrozenStratumSourceTests(unittest.TestCase):
    def _generate(self, path, birds=25, dates=10, bad=False, dup_used=False):
        with path.open("w",encoding="utf-8",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=v.EXPECTED_COLUMNS)
            writer.writeheader()
            for i in range(birds):
                for j in range(dates):
                    for k in range(2):
                        lab="TRUE" if k==0 else "FALSE"
                        if bad and i==0 and j==0 and k==1:lab="label_unknown"
                        if dup_used and i==0 and j==0 and k==1:lab="TRUE"
                        writer.writerow({
                            "birdyear":f"SENSITIVE_DUCK_{i:03d}",
                            "timestamp":f"2020-01-{j+1:02d} 15:00:00",
                            "species":"Anas acuta","case":lab,
                            "season":"winter","photoperiod":"night",
                            "Corn":.55,"Field":.06,"Other":.0,
                            "Protected":1,"Rice":.25,
                            "Urban":.0,"Wetland":.14,
                        })
        return birds*dates*2

    def test_source_exact_SHA_and_header_fixed(self):
        self.assertEqual(v.SOURCE_SHA256,
           "1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15")
        self.assertEqual(v.ORIGINAL_SOURCE_ROWS,380578)
        self.assertEqual(len(v.EXPECTED_COLUMNS),13)
        self.assertFalse(any(n in v.METADATA_COLS for n in v.ENV_COLS))

    def test_source_birdyear_time_groups_with_one_used_per_three(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"synthetic.csv"
            n=self._generate(path)
            with patch.object(v,"ORIGINAL_SOURCE_ROWS",n):
                r=v.source_strata_only(path)
        self.assertEqual(r["source_birdyear_identifiers"],25)
        self.assertEqual(r["source_timestamp_birdyear_pairs"],250)
        self.assertEqual(r["exact_one_used_plus_controls_source_strata"],250)
        self.assertEqual(r["source_birdyears_with_3_or_more_distinct_timestamp_keys"],25)
        self.assertEqual(r["original_candidate_stratum_size_distribution"],{2:250})
        self.assertEqual(r["status"],"SOURCE_ORIGINAL_PAIRED_USE_AGGREGATED_AVAIL_SCHEMA_VERIFIED_NO_EFFECT")
        self.assertFalse(r["original_numeric_habitat_features_opened"])
        self.assertFalse(r["original_bird_ID_values_or_exact_times_exported"])
        self.assertNotIn("SENSITIVE_DUCK_001",json.dumps(r))
        self.assertNotIn(".55",json.dumps(r))
        self.assertNotIn("2020-01-02 15:00:00",json.dumps(r))

    def test_unrecognized_case_must_STOP_without_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"synthetic.csv"
            n=self._generate(path,bad=True)
            with patch.object(v,"ORIGINAL_SOURCE_ROWS",n):
                r=v.source_strata_only(path)
        self.assertEqual(r["status"],"NOT_ADMITTED_EXACT_SOURCE_CHOICE_STRATA_OR_LABELS")
        self.assertGreater(r["incompatible_or_ambiguous_source_strata"],0)

    def test_two_used_in_one_timestamp_cannot_be_assumed_one_original_choice(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"synthetic.csv"
            n=self._generate(path,dup_used=True)
            with patch.object(v,"ORIGINAL_SOURCE_ROWS",n):
                r=v.source_strata_only(path)
        self.assertEqual(r["incompatible_or_ambiguous_source_strata"],1)
        self.assertEqual(r["exact_one_used_plus_controls_source_strata"],249)
        # Cannot discard the unknown case if a strict complete cohort claim
        # is attempted; report counts explicitly.

    def test_UTC_source_time_shape_not_invented(self):
        self.assertTrue(v.parse_timestamp_syntax("2020-01-02 16:01:04"))
        self.assertFalse(v.parse_timestamp_syntax("not a date"))
        self.assertEqual(v.masked_shape("2020-01-02 16:01:04"),
                         "DDDD-DD-DD DD:DD:DD")


if __name__=="__main__":
    unittest.main()
