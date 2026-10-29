"""v25-B2 original full USGS source pinned bytes and header-only tests."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
import usgs_step_schema_gate as s


class TestSourceOnly(unittest.TestCase):
    def fixture(self):
        return {"source_item_id":s.original.SOURCE_ID,
                "file_manifest":[{
                    "name":n,"reported_bytes":size,
                    "provider_checksum":{"type":"MD5","value":md5},
                    "official_download_url":"https://www.sciencebase.gov/catalog/file/get/"+
                                            s.original.SOURCE_ID+"?f=original.csv"}
                  for n,(size,md5) in s.PINNED.items()]}

    def test_exact_original_USGS_published_bytes_and_md5_pin(self):
        self.assertEqual(s.PINNED["Data Release P9ELSUHN.csv"],
                         (27997528,"78eb6064eca992225d6907d6e46f5bef"))
        self.assertEqual(s.PINNED["Data Release P9ELSUHN.xml"],
                         (26316,"170cf76948ef8604ae41f268bc3bf4f0"))
        files=s.select_files(self.fixture())
        self.assertEqual(len(files),2)
        self.assertLess(files["Data Release P9ELSUHN.csv"]["size"],s.MAX_SINGLE)

    def test_wrong_provider_md5_and_download_domain_fail(self):
        x=self.fixture()
        x["file_manifest"][0]["provider_checksum"]["value"]="f"*32
        with self.assertRaisesRegex(ValueError,"MD5"):
            s.select_files(x)
        x=self.fixture()
        x["file_manifest"][0]["official_download_url"]="https://attacker.example/file.csv"
        with self.assertRaisesRegex(ValueError,"Unexpected"):
            s.select_files(x)

    def test_original_source_schema_never_records_choice_results(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"example.csv"
            with path.open("w",encoding="utf-8",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=[
                    "Animal ID","Time","Start_X","Used","StepID","HabitatScore"])
                writer.writeheader()
                writer.writerow({"Animal ID":"SENSITIVE-123",
                                 "Time":"2019-07-06T18:20:00",
                                 "Start_X":-122.345678,
                                 "Used":1,"StepID":"1234",
                                 "HabitatScore":.8899})
                writer.writerow({"Animal ID":"SENSITIVE-123",
                                 "Time":"2019-07-06T18:20:00",
                                 "Start_X":-122.3344,
                                 "Used":0,"StepID":"1234",
                                 "HabitatScore":.2})
            d=s.csv_schema_only(path)
        self.assertEqual(d["original_physical_lines_after_header"],2)
        self.assertEqual(d["n_original_column_names"],6)
        self.assertFalse(d["categorical_values_or_step_IDs_opened"])
        self.assertFalse(d["GPS_start_end_coordinates_or_choice_numeric_values_read"])
        self.assertNotIn("SENSITIVE-123",str(d))
        self.assertNotIn("122.345678",str(d))

    def test_FGDC_original_labels_are_not_animal_data(self):
        raw=("<metadata><eainfo><detailed><attr><attrlabl>StepID</attrlabl>"
             "<attrdef>Original step identifier</attrdef></attr></detailed>"
             "</eainfo></metadata>")
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"original.xml"
            p.write_text(raw)
            x=s.fgdc_schema_only(p)
        self.assertEqual(x["number_of_documented_source_fields"],1)
        self.assertEqual(x["source_field_definitions"][0]["field"],"StepID")
        self.assertFalse(x["original_movement_or_landcover_values_opened"])


if __name__=="__main__":
    unittest.main()
