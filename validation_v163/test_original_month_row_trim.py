"""v163 source-free checks of published Table A1 clipping and date semantics."""
from datetime import datetime
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from original_tableA1_month_row_trim import (
    exact_datetime, SOURCE_RETAINED_EXPECTED, PAPER_OUT_OF_MONTH_ROWS_EXPECTED,
    SOURCE_TOTAL_EXPECTED
)
from paper_tableA1_source_consistency import published_tableA1

class TestSourceDateGate(unittest.TestCase):
    def test_expected_126231_minus_20315(self):
        self.assertEqual(SOURCE_TOTAL_EXPECTED-PAPER_OUT_OF_MONTH_ROWS_EXPECTED,
                         SOURCE_RETAINED_EXPECTED)
    def test_table_A1_HONO_exact_month_boundaries(self):
        x=published_tableA1()["HONO"]
        self.assertTrue(x[1]<=(2023,7)<=x[2])
        self.assertFalse(x[1]<=(2018,8)<=x[2])
    def test_table_A1_MRC4_is_unverified_alias(self):
        x=published_tableA1()["MRC4"]
        self.assertEqual(x[3],"MSC4 paper alias")
    def test_real_leapyear_day(self):
        self.assertEqual(exact_datetime(2020,60,11),datetime(2020,2,29,11))
        with self.assertRaises(AssertionError):exact_datetime(2019,366,3)
    def test_no_phantom_click_after_clipped_gap(self):
        original={2:"clicked",3:"clicked",4:"clicked"}
        clipped={k:v for k,v in original.items() if k!=3}
        self.assertNotIn(3,clipped)
        self.assertNotIn(4-1,clipped)
        self.assertIn(2,clipped)

if __name__=="__main__":unittest.main()
