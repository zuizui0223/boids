"""Offline original USGS FGDC / Zenodo author README source-only known truth."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import hashlib

import source_dictionaries as s

class SourceDictionaries(unittest.TestCase):
    def test_exact_original_two_source_dictionary_pins(self):
        self.assertEqual(s.TURTLE_XML,"iSSA data release V3.xml")
        self.assertEqual(s.TURTLE_BYTES,22606)
        self.assertEqual(s.TURTLE_MD5,"bb23daf440cb8ee6932f60a8fc7293a5")
        self.assertEqual(s.MAMMAL_README,"README.txt")
        self.assertEqual(s.MAMMAL_BYTES,3580)
        self.assertEqual(s.MAMMAL_MD5,"b03a51664b620a2cdd3cc38bb20b4215")

    def test_provider_metadata_unique_and_strict_bytes(self):
        x={"original_source_metadata":{"files":[{
           "original_filename":s.TURTLE_XML,
           "provider_bytes":s.TURTLE_BYTES,
           "provider_MD5_or_checksum":{"type":"MD5","value":s.TURTLE_MD5},
           "download_provider_uri":"https://www.sciencebase.gov/catalog/file/get/"+
                           s.source.TURTLE_ITEM+"?f=test"}]}}
        z=s.selected_source_item(x,s.TURTLE_XML,"USGS",
                                 s.TURTLE_BYTES,s.TURTLE_MD5)
        self.assertEqual(z["md5"],s.TURTLE_MD5)
        x["original_source_metadata"]["files"][0]["provider_bytes"]+=1
        with self.assertRaisesRegex(ValueError,"byte count"):
            s.selected_source_item(x,s.TURTLE_XML,"USGS",
                                   s.TURTLE_BYTES,s.TURTLE_MD5)

    def test_original_fgdc_attribute_definitions_no_turtle_measurements(self):
        with tempfile.TemporaryDirectory() as root:
            f=Path(root)/"source.xml"
            f.write_text("<metadata><eainfo><detailed><attr>"
              "<attrlabl>step_id</attrlabl><attrdef>Original step identifier</attrdef>"
              "</attr><attr><attrlabl>protected_status</attrlabl>"
              "<attrdef>Protected area at step endpoint</attrdef></attr>"
              "</detailed></eainfo></metadata>")
            d=s.original_fgdc_labels(f)
        self.assertEqual(d["attributes_documented"],2)
        self.assertFalse(d["original_PIT_or_habitat_values_read"])
        self.assertEqual(d["field_definitions"][0]["name"],"step_id")

    def test_original_mammal_README_only_is_not_iSSA_outcome(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"author.txt"
            p.write_text("Reproducible original data dictionary\nStep data\n")
            d=s.original_readme_structure(p)
        self.assertEqual(d["n_lines"],2)
        self.assertFalse(d["source_original_animal_step_rows_read"])

    def test_disallow_invented_external_source_file(self):
        with self.assertRaisesRegex(ValueError,"not official"):
            s.validate_url("https://attacker.example.com/animal.csv","USGS")
        with self.assertRaisesRegex(ValueError,"not original"):
            s.validate_url("https://attacker.example.com/animal.csv","Zenodo")

if __name__=="__main__":
    unittest.main()
