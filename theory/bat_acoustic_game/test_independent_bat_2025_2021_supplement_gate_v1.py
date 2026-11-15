"""Independent source-bundle admission tests; invented names only."""
import unittest
from independent_bat_2025_2021_supplement_gate_v1 import member_extension,SOURCE,PUBLIC_EXTS,MAX_BYTES
class TestOriginalSourceAdmission(unittest.TestCase):
    def test_pdf_is_not_data(self):
        self.assertNotIn(member_extension("PMC2025/pnas.2407810122.sapp.pdf"),PUBLIC_EXTS)
    def test_movies_are_not_measured_track_table(self):
        self.assertNotIn(member_extension("supplement/movieS1.mp4"),PUBLIC_EXTS)
    def test_xlsx_is_only_potential_source(self):
        self.assertIn(member_extension("dataset/results.xlsx"),PUBLIC_EXTS)
    def test_uncompressed_zip_needs_separate_gate(self):
        self.assertIn(member_extension("archive/Data.zip"),PUBLIC_EXTS)
    def test_two_independent_original_studies(self):
        self.assertEqual(len(SOURCE),2)
        self.assertEqual({x["pmcid"] for x in SOURCE.values()},{"PMC12002023","PMC8601711"})
        self.assertNotEqual(*[x["original_paper_doi"] for x in SOURCE.values()])
    def test_public_source_bounded(self):
        self.assertEqual(MAX_BYTES,80*1024*1024)
if __name__=="__main__":unittest.main()
