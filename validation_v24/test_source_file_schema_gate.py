"""v24 A2 original USGS file pin, id-only CSV and FGDC source tests."""
from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import source_file_schema_gate as s
import sciencebase_source_gate as a


class USGSOriginalFileSourceTests(unittest.TestCase):
    def sample(self):
        files = []
        for name, info in s.EXPECTED.items():
            files.append({
                "original_name": name,
                "reported_bytes": info["bytes"],
                "published_checksum": {"type": "MD5", "value": info["md5"]},
                "source_download_uri": (
                    "https://www.sciencebase.gov/catalog/file/get/"
                    + a.SOURCE_ITEM + "?f=" + name),
            })
        return {"source_item_id": a.SOURCE_ITEM, "attachments": files}

    def test_original_usgs_source_only_pins_exact_three_files(self):
        self.assertEqual(len(s.EXPECTED), 3)
        self.assertEqual(s.EXPECTED[
          "Duckling_Habitat_Selection_Dataset.csv"]["bytes"], 7699152)
        self.assertEqual(s.EXPECTED[
          "Duckling_Movement_Dataset.csv"]["bytes"], 109492)
        found = s.select_original_files(self.sample())
        self.assertEqual(set(found), set(s.EXPECTED))

    def test_source_checksum_change_fails_closed(self):
        data = self.sample()
        data["attachments"][1]["published_checksum"]["value"] = "0" * 32
        with self.assertRaisesRegex(ValueError, "MD5"):
            s.select_original_files(data)

    def test_original_csv_header_and_categorical_counts_only(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "mock.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "BroodID", "Date", "Year", "WetlandID",
                    "Use_Status", "VegCover", "Salinity", "LATITUDE",
                ])
                writer.writeheader()
                for brood in ("A10", "A11"):
                    for status in ("used", "available", "available"):
                        writer.writerow({
                            "BroodID": brood,
                            "Date": "2018-06-01",
                            "Year": "2018",
                            "WetlandID": "W1" if status == "used" else "W2",
                            "Use_Status": status,
                            "VegCover": "72.3", "Salinity": "13.9",
                            "LATITUDE": "38.04123",
                        })
            result = s.source_csv_schema(path)
        self.assertEqual(result["physical_csv_data_rows"], 6)
        self.assertEqual(result["identifier_time_and_choice_label_fields"][
            "BroodID"]["n_distinct_observed_tokens"], 2)
        self.assertEqual(result["identifier_time_and_choice_label_fields"][
            "Use_Status"]["recognizable_generic_label_counts"],
            {"available": 4, "used": 2})
        self.assertFalse(result["GPS_coordinates_or_habitat_numerics_analyzed"])
        self.assertFalse(result["independent_matched_choice_sets_verified"])
        self.assertNotIn("38.04123", json.dumps(result))
        self.assertNotIn("72.3", json.dumps(result))

    def test_FGDC_extracts_attribute_definitions_not_numeric_records(self):
        xml = (
            "<metadata><eainfo><detailed><attr><attrlabl>Brood</attrlabl>"
            "<attrdef>Unique radio-tagged brood identity</attrdef></attr>"
            "<attr><attrlabl>Selected</attrlabl>"
            "<attrdef>Used or sampled available wetland</attrdef>"
            "</attr></detailed></eainfo></metadata>"
        )
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "source.xml"
            p.write_text(xml, encoding="utf-8")
            result = s.fgdc_xml_attributes(p)
        self.assertEqual(result["original_FGDC_attribute_count"], 2)
        self.assertFalse(result["original_animal_records_examined"])
        self.assertEqual(result["original_attribute_definitions"][1]["name"],
                         "Selected")

    def test_files_with_unknown_source_URL_fail_closed(self):
        data = self.sample()
        data["attachments"][0]["source_download_uri"] = (
            "https://evil.test/not-the-source.csv"
        )
        with self.assertRaisesRegex(ValueError, "not from ScienceBase"):
            s.select_original_files(data)


if __name__ == "__main__":
    unittest.main()
