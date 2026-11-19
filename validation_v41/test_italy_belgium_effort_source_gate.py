"""v41 synthetic origin-safe source, no behavior numbers."""
import unittest
from italy_belgium_effort_source_gate import source_units,audit,aggregate,get,FILES

class V41Test(unittest.TestCase):
    def test_event_file_duplication_not_assumed_effort(self):
        rows=[
            {"SITE":"S1","DATE":"2025-06-01","TIME-12":"22:00","FILES":"r1","TREATMENT":"wood"},
            {"SITE":"S1","DATE":"2025-06-01","TIME-12":"22:00","FILES":"r1","TREATMENT":"wood"},
            {"SITE":"S1","DATE":"2025-06-01","TIME-12":"22:20","FILES":"r2","TREATMENT":"wood"},
        ]
        r=source_units(rows,"italy")
        self.assertEqual(r["site_date"]["distinct_keys"],1)
        self.assertEqual(r["site_date_file"]["distinct_keys"],2)
        self.assertFalse(r["full_scheduled_zero_detection_windows_independently_verified"])
        self.assertFalse(r["numeric_bat_acoustic_or_prey_values_accessed"])
    def test_belgium_original_loc_metadata_schema(self):
        rows=[{"Loc":"L1","Date":"2026-08-01","Time":"23:00",
               "Filename":"capture.wav","Filepath":"path","Group":"Bat"}]
        x=source_units(rows,"belgium")
        self.assertEqual(x["distinct_site_tokens"],1)
        self.assertEqual(x["site_date_time"]["distinct_keys"],1)
    def test_bad_hash_fails_before_behavior(self):
        original=FILES["italy"]
        d,rows=get("italy",lambda u:(200,"text/csv",b"SITE,DATE\nS1,2025-01-01"))
        self.assertEqual(d["status"],"SOURCE_MD5_MISMATCH_STOP")
        self.assertIsNone(rows)
    def test_all_original_files_unavailable_not_animal_null(self):
        r=audit(lambda u:(200,"text/html",b"<!doctype html>Validating..."))
        self.assertEqual(r["status"],"SOURCE_ACCESS_OR_SCHEMA_STOP")
        self.assertFalse(r["zero_detection_windows_inferred"])
        self.assertFalse(r["cross_country_model_fitted"])
if __name__=="__main__":unittest.main()
