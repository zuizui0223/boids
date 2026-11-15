"""Known-truth tests for clock-bin nulls (no real acoustic outcomes)."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v149_clockbin import compare_pair,subgroups
from collections import defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"validation_v148"))
from same_day_diel import fresh,add_group

def group_records():
    return {w:defaultdict(fresh) for w in (24,6,4,2,1)}

class TestV149(unittest.TestCase):
    def test_exact_width1_and_other_widths(self):
        from datetime import date
        d=date(2020,2,1)
        g=group_records()
        for hour,typ in [(0,("Bocaccio","UF440")),(1,()),(2,()),(3,())]:
            for w in g:add_group(g[w],(d,hour//w),typ)
        result=compare_pair(g,"Bocaccio","UF440",1)
        self.assertEqual(result["1"],1.0)
        self.assertEqual(result["2"],0.5)
        self.assertEqual(result["4"],0.25)
        self.assertEqual(result["6"],0.25)
        self.assertEqual(result["24"],0.25)
    def test_single_hour_bin_expected_identically_O(self):
        from datetime import date
        d=date(2020,2,1)
        g=group_records()
        for hour,typ in [(0,("Bocaccio",)),(1,("UF440",)),(2,())]:
            for w in g:add_group(g[w],(d,hour//w),typ)
        values=compare_pair(g,"Bocaccio","UF440",0)
        self.assertEqual(values["1"],0.0)
        self.assertEqual(values["2"],0.5)
    def test_mismatch_O_refuses(self):
        from datetime import date
        d=date(2020,2,1)
        g=group_records()
        for w in g:add_group(g[w],(d,0),("Bocaccio","UF440"))
        with self.assertRaises(AssertionError):compare_pair(g,"Bocaccio","UF440",0)

if __name__=="__main__":unittest.main()
