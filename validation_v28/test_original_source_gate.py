"""v28 original ungulate GPS and camera Zenodo source-only mock tests."""
from __future__ import annotations
import csv
import tempfile
import unittest
from pathlib import Path
import original_source_gate as s


class OriginalUngulateSource(unittest.TestCase):
    def test_expected_Zenodo_original_record_and_2_observation_sources(self):
        self.assertEqual(s.RECORD,7766936)
        self.assertEqual(s.DOI,"10.5281/zenodo.7766936")
        self.assertEqual(len(s.SOURCE_TARGETS),4)
        self.assertIn("RSFapproach_data.csv",s.SOURCE_TARGETS)
        self.assertIn("IDMapproach_data.csv",s.SOURCE_TARGETS)

    def test_provider_original_file_checksum_and_size_strict(self):
        fake={"original_published_files":[{
            "original_filename":"RSFapproach_data.csv","provider_bytes":2000000,
            "provider_MD5_or_checksum":"md5:"+"a"*32,
            "content_url":"https://zenodo.org/api/records/7766936/files/original.csv"
        }]}
        x=s.require_file(fake,"RSFapproach_data.csv")
        self.assertEqual(x["size"],2000000)
        self.assertEqual(x["md5"],"a"*32)
        fake["original_published_files"][0]["provider_bytes"]=60000000
        with self.assertRaisesRegex(ValueError,"unsupported"):
            s.require_file(fake,"RSFapproach_data.csv")

    def test_source_CSV_only_header_even_if_animal_values_are_present(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"test.csv"
            with p.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=["AnimalID","Case","Location","Forest"])
                w.writeheader()
                w.writerow({"AnimalID":"SENSITIVE-ANIMAL-A",
                            "Case":1,"Location":"40.234,-5.124","Forest":.80})
            result=s.only_csv_header(p)
        self.assertEqual(result["source_header_count"],4)
        self.assertEqual(result["physical_data_lines_after_header"],1)
        self.assertFalse(result["original_GPS_or_available_habitat_numerics_read"])
        self.assertFalse(result["original_individual_animal_IDs_read"])
        self.assertNotIn("SENSITIVE-ANIMAL-A",str(result))
        self.assertNotIn("40.234",str(result))

    def test_wrong_source_host_is_not_fetched(self):
        fake={"original_published_files":[{
            "original_filename":"RSFapproach_data.csv","provider_bytes":2000000,
            "provider_MD5_or_checksum":"md5:"+"a"*32,
            "content_url":"https://attacker.example.org/original.csv"
        }]}
        with self.assertRaisesRegex(ValueError,"not from"):
            s.require_file(fake,"RSFapproach_data.csv")

if __name__=="__main__":
    unittest.main()
