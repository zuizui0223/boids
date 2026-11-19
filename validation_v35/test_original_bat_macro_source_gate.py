"""Offline synthetic source/MD5 discipline for v35; no animal records."""
import unittest
from original_bat_macro_source_gate import structural_columns,download_original,FILES,run

class MacroSourceTests(unittest.TestCase):
    def test_structural_metadata_only(self):
        s="Study,Country,Species,HomeRange,Forest\n"+\
          "s1,France,Myotis,10,0.5\ns1,France,Myotis,15,0.4\ns2,Spain,Eptesicus,12,0.3\n"
        r=structural_columns(s)
        self.assertEqual(r["rows"],3)
        self.assertEqual(r["structure_only_candidate_category_support"]["Study"]["distinct_labels_at_most_10000"],2)
        self.assertEqual(r["structure_only_candidate_category_support"]["Country"]["distinct_labels_at_most_10000"],2)
        self.assertFalse(r["numeric_home_range_movement_or_habitat_values_opened"])
    def test_delimiter_and_missing_id(self):
        r=structural_columns("Study;Species;Distance\ns1;Pipistrellus;25\n;Myotis;30\n")
        self.assertEqual(r["rows"],2)
        self.assertEqual(r["structure_only_candidate_category_support"]["Study"]["nonempty_rows"],1)
    def test_html_200_refused(self):
        f=download_original(FILES["published_meta"],lambda u:(200,"text/html",b"<html>Validating...</html>"))
        self.assertEqual(f["status"],"ORIGINAL_CSV_NOT_RECEIVED")
    def test_hash_mismatch_never_substituted(self):
        f=download_original(FILES["published_meta"],lambda u:(200,"text/csv",b"Study,Species\ns1,Myotis\n"))
        self.assertEqual(f["status"],"ORIGINAL_MD5_MISMATCH_STOP")
    def test_access_stop_not_negative_ecology(self):
        r=run(lambda u:(401,"text/plain",b"not authorized"))
        self.assertEqual(r["status"],"ORIGINAL_MACRO_CSV_SOURCE_ACCESS_OR_INTEGRITY_STOP")
        self.assertFalse(r["source_outcomes_opened"])
        self.assertFalse(r["ecological_model_fitted"])

if __name__=="__main__":unittest.main()
