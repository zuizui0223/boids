"""v28-B1 source-only Nyctalus bat full MD5, independent animal/flight units."""
from __future__ import annotations
import csv
import json
import tempfile
import unittest
from pathlib import Path
import three_file_source_gate as s


class BatSourceOnly(unittest.TestCase):
    def test_exact_original_three_source_MD5_size_pins(self):
        a=s.PINS["Model_dataset_RSFFlight_Complete_EPSG25833.csv"]
        self.assertEqual(a["size"],17582302)
        self.assertEqual(a["md5"],"fb0d7967d552b855ab530eeedcede7ff")
        self.assertEqual(s.PINS["Observed_GPS_locations.csv"]["md5"],
                         "a1583b48487a78259f7e63937af232e5")
        self.assertEqual(s.PINS["Individual_Characteristics_Capture.csv"]["md5"],
                         "84e78242135fc50b12e5e2ffff91bcb5")
        self.assertEqual(len(s.PINS),3)

    def test_source_file_integrity_requires_exact_provider_values(self):
        src={"filename":"Observed_GPS_locations.csv",
             "source_exact_bytes":3080045,
             "provider_original_checksum":"md5:a1583b48487a78259f7e63937af232e5",
             "file_download_url":"https://zenodo.org/api/records/7535030/files/Observed_GPS_locations.csv/content"}
        pin=s.select_pin(src)
        self.assertEqual(pin["size"],3080045)
        changed={**src,"source_exact_bytes":999}
        with self.assertRaisesRegex(ValueError,"length"):
            s.select_pin(changed)

    def test_recording_random_locations_does_not_inflate_independent_bats(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"synthetic.csv"
            cols=["batid","trackid","case_","response_rvso",
                  "field_period","sex","age_class","move_state",
                  "x_","y_","mindist_WKA","clc20m"]
            with p.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=cols)
                w.writeheader()
                for b in range(9):
                    for trip in range(3):
                        for k in range(8):
                            used=k<2
                            w.writerow({"batid":f"PRIVATE_BAT_ID_{b}",
                                "trackid":f"PATH_{b}_{trip}",
                                "case_":"TRUE" if used else "FALSE",
                                "response_rvso":"1" if used else "0",
                                "field_period":"one","sex":"f","age_class":"ad",
                                "move_state":"ARM","x_":"532213.49",
                                "y_":"5912345.91","mindist_WKA":"17.8",
                                "clc20m":"235"})
            profile,ids=s.source_csv_ids_only(p,"mock_source")
        self.assertEqual(len(ids),9)
        self.assertEqual(profile["original_physical_csv_rows"],216)
        self.assertEqual(profile["original_distinct_track_ID_tokens_with_bat"],27)
        self.assertEqual(profile["bats_with_3_or_more_original_tracks"],9)
        self.assertEqual(profile["source_track_groups_with_both_TRUE_and_FALSE"],27)
        self.assertEqual(profile["source_track_groups_exactly_one_TRUE_and_one_or_more_FALSE"],0)
        self.assertEqual(profile["original_use_availability_label_counts"],
                         {"FALSE":162,"TRUE":54})
        self.assertEqual(profile["original_binary_case_column_mismatch_count"],0)
        self.assertFalse(profile["original_Utm_X_Y_altitude_turbine_distance_or_habitat_values_read"])
        self.assertFalse(profile["model_or_ecological_effects_fitted"])
        self.assertNotIn("PRIVATE_BAT_ID",json.dumps(profile))
        self.assertNotIn("5912345.91",json.dumps(profile))

    def test_original_GPS_bat_id_alias_is_recognized_as_same_individual(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"observed.csv"
            p.write_text("bat_id,trackid,field_period,x,y,Height\n"
                         "A167581,21519_2085_A167581,one,521234,5900123,67\n")
            q, ids=s.source_csv_ids_only(p,"Observed_GPS_locations.csv")
        self.assertEqual(q["original_declared_bat_ID_column"],"bat_id")
        self.assertEqual(q["original_distinct_bat_id_tokens"],1)
        self.assertEqual(q["original_distinct_track_ID_tokens_with_bat"],1)
        self.assertIn("A167581",ids)
        self.assertFalse(q["original_Utm_X_Y_altitude_turbine_distance_or_habitat_values_read"])

    def test_unmatched_use_source_label_is_diagnostic_not_invented(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"malformed.csv"
            p.write_text("batid,trackid,case_,response_rvso\nB1,T1,unknown,1\n")
            d,_=s.source_csv_ids_only(p,"synthetic")
        self.assertEqual(d["original_use_availability_label_counts"],{"unknown":1})
        self.assertEqual(d["source_track_groups_with_both_TRUE_and_FALSE"],0)
        self.assertEqual(d["source_track_groups_exactly_one_TRUE_and_one_or_more_FALSE"],0)

if __name__=="__main__":
    unittest.main()
