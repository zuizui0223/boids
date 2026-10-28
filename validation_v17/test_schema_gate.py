"""v17-A2 format-only audit tests; all records below are artificial."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import schema_gate as g


class SchemaGateTests(unittest.TestCase):
    def test_observed_original_filename_example_and_reject_ambiguous(self):
        self.assertEqual(g.file_identity("Experiment 1 - GPS data/B01_1_1_GPS.csv"),
                         ("B01",1,1))
        self.assertEqual(g.file_identity("S30_4_6_GPS.csv"),("S30",4,6))
        self.assertIsNone(g.file_identity("unrecognized_B01.csv"))
        self.assertIsNone(g.file_identity("B01_5_1_GPS.csv"))

    def test_schema_summary_counts_not_animal_motion(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"GPS.zip"
            with zipfile.ZipFile(p,"w") as f:
                for bird in ("B01","S05"):
                    for phase in range(1,5):
                        for release in range(1,7):
                            table=",".join(g.EXPECTED_GPS_SCHEMA)+"\n"
                            for i in range(100):
                                columns=[
                                    str(i),"test", "FIXED", "2015/6/24", "13:01:10",
                                    "2015/6/24", "14:01:10", str(200),
                                    "51.88888","N","1.3351","W","50.0","19","234",
                                    "0","0","0"
                                ]
                                table+=",".join(columns)+"\n"
                            f.writestr(f"{bird}_{phase}_{release}_GPS.csv",table)
            d=g.original_gps_inventory(p)
        self.assertEqual(d["filenames_parsed"],48)
        self.assertEqual(d["unique_bird_ids"],2)
        self.assertEqual(d["individuals_in_all_four_phases"],2)
        self.assertEqual(len(d["phase_track_count"]),4)
        self.assertTrue(d["all_header_samples_match_original_18_columns"])
        self.assertFalse(d["GPS_course_target_read"])
        self.assertFalse(d["GPS_positions_exported"])
        self.assertNotIn("51.88888",json.dumps(d))
        self.assertNotIn("13:01:10",json.dumps(d))

    def test_2015_weather_dmy_and_ymd_parsers_not_choose_timezone(self):
        self.assertIn("%Y-%m-%d %H:%M:%S",
                      g.parse_datetime_candidates("2015-06-29 13:05:00"))
        self.assertIn("%d/%m/%Y %H:%M",
                      g.parse_datetime_candidates("29/06/2015 13:05"))
        self.assertEqual(g.parse_datetime_candidates("not a date"),())

    def test_weather_data_without_header_is_not_dropped(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"weather.csv"
            p.write_text("2015-06-29 13:05:00,2.3,189\n"
                         "2015-06-29 13:06:00,2.0,200\n"
                         "2015-06-29 13:07:00,2.7,210\n",encoding="utf-8")
            d=g.original_weather_format(p)
        self.assertFalse(d["first_line_is_named_header"])
        self.assertEqual(d["weather_physical_nonempty_data_rows"],3)
        self.assertEqual(d["field_count_histogram"],{"3":3} if False else {3:3})
        self.assertGreater(d["numeric_finite_counts"]["col2_finite"],0)
        self.assertFalse(d["source_weather_UTC_offset_verified"])
        self.assertFalse(d["weather_GPS_join_attempted"])
        self.assertNotIn("2015-06-29 13:05:00",json.dumps(d))
        self.assertNotIn("189",json.dumps(d))

    def test_named_header_weather_suppresses_only_header(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"weather.csv"
            p.write_text("Date time,wind speed,wind bearing\n"
                         "2015-06-29 13:05:00,2.3,189\n"
                         "2015-06-29 13:06:00,2.0,200\n",encoding="utf-8")
            d=g.original_weather_format(p)
        self.assertTrue(d["first_line_is_named_header"])
        self.assertEqual(d["weather_physical_nonempty_data_rows"],2)
        self.assertEqual(d["sample_rows_with_token_shapes"],1)


if __name__=="__main__":
    unittest.main()
