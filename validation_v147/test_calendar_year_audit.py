"""Source-free known-truth checks for v147 temporal partition mathematics."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from year_stability import score_year, each_year_complete_run_masks, TYPES

class TestYearStability(unittest.TestCase):
    def test_whole_day_circular_matching_expected(self):
        masks = {typ: [0, 0] for typ in TYPES}
        masks["Bocaccio"] = [1, 2]
        masks["UF440"] = [1, 2]
        _, rows = score_year("T", 2018, [masks])
        rr = next(r for r in rows if r["chorus_A"]=="Bocaccio" and r["chorus_B"]=="UF440")
        self.assertEqual(rr["observed"], 2)
        self.assertEqual(rr["exact_shift_expected"], 1)
        self.assertFalse(rr["admitted_exploratory_year"])
    def test_local_year_boundary_wont_mix_runs(self):
        # original source hour index constructed from calendar date, no observed data
        from datetime import datetime, timezone, timedelta
        epoch=datetime(1899,12,30,tzinfo=timezone.utc)
        start=datetime(2020,12,22,tzinfo=timezone.utc)
        end=datetime(2021,1,12,tzinfo=timezone.utc)
        base=int((start-epoch).total_seconds()//3600)
        last=int((end-epoch).total_seconds()//3600)
        item={"nominal":set(range(base,last)),"off":set(),"noise":set(),"fish":{}}
        groups, runs=each_year_complete_run_masks(item)
        for year, mats in groups.items():
            self.assertGreaterEqual(len(mats),1)
            for m in mats:
                self.assertEqual(set(m),set(TYPES))
                self.assertGreaterEqual(len(m[TYPES[0]]),7)

if __name__=="__main__":
    unittest.main()
