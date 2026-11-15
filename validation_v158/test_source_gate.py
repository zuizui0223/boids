"""v158 fake CSV source-only tests, no original porpoise outcomes loaded."""
import unittest,csv,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from porpoise_source_gate import MAX_CSV_BYTES,MAX_COLUMNS,DOI,BASENAME

class TestPorpoiseSource(unittest.TestCase):
    def test_original_source_name_and_schema_bounds(self):
        self.assertEqual(DOI,"10.1002/ece3.72566")
        self.assertEqual(BASENAME,"ece372566-sup-0002-DataS2.csv")
        self.assertGreaterEqual(MAX_CSV_BYTES,25*1024*1024)
        self.assertGreaterEqual(MAX_COLUMNS,25)
    def test_missing_hour_must_not_be_equated_to_no_click(self):
        # A source-only absence of row does NOT imply C-POD was operating.
        rows=[{"hour":"1","buzz":"1"},{"hour":"3","buzz":"0"}]
        self.assertNotIn("2",{r["hour"] for r in rows})
        self.assertNotEqual(sum(int(r["buzz"]) for r in rows),3)

if __name__=="__main__":
    unittest.main()
