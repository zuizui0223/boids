"""v26-C1 no turtle step response or habitat-value original identity tests."""
from __future__ import annotations
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import turtle_pit_step_gate as s

class OriginalTurtlePITTimeSource(unittest.TestCase):
    def fixture(self,root):
        path=Path(root)/"synthetic.csv"
        with path.open("w",encoding="utf-8",newline="") as fp:
            writer=csv.DictWriter(fp,fieldnames=s.EXPECTED_SOURCE_FIELDS)
            writer.writeheader()
            for turtle in ("A-SECRET","B-SECRET"):
                for n in range(3):
                    for k in range(2):
                        writer.writerow({
                            "orgnl_pit":turtle,
                            "step_id":f"STEP{n}",
                            "step_length":200.5,
                            "log_step_length":5.0,
                            "turn_angle":0.2,
                            "cos_turn_angle":0.9,
                            "start_time":f"2018-06-{n+1:02d} 00:00:00",
                            "end_time":f"2018-06-{n+1:02d} 01:00:00",
                            "protected_status":"NO_TAKE",
                            "water_depth":27.11,
                            "chlorophyll":.453,
                        })
        return path

    def test_pin_and_col_schema_from_actual_original(self):
        self.assertEqual(s.PINNED_SHA256,
            "eef4d2dd16c97cd0d8722ed1cac8a031cf3dd336404b2e8e4c085cb2fadd4ec0")
        self.assertEqual(s.EXPECTED_SOURCE_ROWS,420365)
        self.assertEqual(len(s.EXPECTED_SOURCE_FIELDS),11)
        self.assertEqual(s.ID_FIELDS,
            ("orgnl_pit","step_id","start_time","end_time"))

    def test_true_PIT_step_time_source_grain_without_telemetry(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.fixture(root)
            with patch.object(s,"EXPECTED_SOURCE_ROWS",12):
                q=s.source_ids_only(p)
        self.assertEqual(q["source_original_rows"],12)
        self.assertEqual(q["n_distinct_original_PIT_tokens"],2)
        self.assertEqual(q["n_unique_PIT_by_step_id_keys"],6)
        self.assertEqual(q["n_unique_PIT_start_end_pair_keys"],6)
        self.assertEqual(q["original_PITs_with_at_least_3_distinct_calendar_dates"],2)
        self.assertEqual(q["source_original_PIT_step_id_group_size_distribution"],{"2":6})
        self.assertFalse(q["original_explicit_used_available_source_column_present"])
        self.assertFalse(q["source_prequential_choice_model_admitted"])
        self.assertFalse(q["original_step_lengths_angles_depth_chlorophyll_or_MPA_values_read"])
        self.assertNotIn("SECRET",json.dumps(q))
        self.assertNotIn("27.11",json.dumps(q))
        self.assertNotIn("NO_TAKE",json.dumps(q))

    def test_calendar_parser_does_not_guess_study_period(self):
        self.assertEqual(str(s.parse_calendar_day("2018-07-12 17:03:00")),"2018-07-12")
        self.assertEqual(str(s.parse_calendar_day("07/12/2018 17:03")),"2018-07-12")
        self.assertIsNone(s.parse_calendar_day("unknown"))

    def test_duplicate_or_changed_header_is_hard_stop(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.fixture(root)
            text=p.read_text()
            p.write_text(text.replace("orgnl_pit","id_instead_of_pit",1))
            with patch.object(s,"EXPECTED_SOURCE_ROWS",12):
                with self.assertRaisesRegex(ValueError,"header changed"):
                    s.source_ids_only(p)

if __name__=="__main__":
    unittest.main()
