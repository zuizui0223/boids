"""Roscoff source-audit constants and synthetic missing-hour handling."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from roscoff_source_gate import MIN_POS_PER_ALL_FOLDS,MIN_NEG_PER_ALL_FOLDS,MIN_SOURCE_PERIODS_POSITIVE
from hourly_diagnostic import SOURCE_SHA

class TestV156(unittest.TestCase):
    def test_source_is_exact_republished_fingerprint(self):
        self.assertEqual(SOURCE_SHA,"2df8fac5749d804b8d16d98db065ba19dc3796a4a01ce1cfa87c56f5d622d0d0")
    def test_no_tuned_target_selection(self):
        self.assertEqual(MIN_POS_PER_ALL_FOLDS,3)
        self.assertEqual(MIN_NEG_PER_ALL_FOLDS,3)
        self.assertEqual(MIN_SOURCE_PERIODS_POSITIVE,6)

if __name__=="__main__":unittest.main()
