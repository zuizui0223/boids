"""Source-free year reexpression and temporal non-leakage fixtures."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from porpoise_temporal_holdout import source_year,evaluate
from porpoise_site_holdout import fixed_features,MIN_TRAIN,MIN_TEST

class TestYearHoldout(unittest.TestCase):
    def test_original_year_from_frozen_site_feature(self):
        for y in (2009,2012,2016,2020,2023):
            base,_=fixed_features(y,151,14,10,8)
            self.assertEqual(source_year({"C1":base}),y)
    def test_refuses_non_original_year(self):
        with self.assertRaises(AssertionError):
            source_year({"C1":[0]*8+[99.0,0]})
    def test_strict_earlier_year_split(self):
        records=[{"C1":fixed_features(2019,20,12,5,5)[0]}]*20
        records += [{"C1":fixed_features(2020,20,12,5,5)[0]}]*10
        tr=[r for r in records if source_year(r)<2020]
        te=[r for r in records if source_year(r)==2020]
        self.assertEqual(len(tr),20)
        self.assertEqual(len(te),10)
        self.assertEqual(MIN_TRAIN,1000)
        self.assertEqual(MIN_TEST,250)

if __name__=="__main__":unittest.main()
