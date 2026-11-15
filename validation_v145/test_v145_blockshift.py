"""Known mathematical invariants, no invented animal source result."""
import unittest
from datetime import date,timedelta
from v145_blockshift import (score_by_all_rotations,randomization,
                            eligible_complete_days,contiguous_runs,
                            MIN_RUN_DAYS)
class BlockNullKnownTruth(unittest.TestCase):
    def test_shift_preserves_equal_clock_hour_means(self):
        a=[1,2,4,8]
        b=[1,2,4,8]
        self.assertEqual(score_by_all_rotations(a,b),[4,0,0,0])
        r=randomization(4,[score_by_all_rotations(a,b)],"S","A","B",n=49)
        self.assertAlmostEqual(r["exact_uniform_shift_expectation_hours"],1.)
        self.assertGreater(r["two_sided_monte_carlo_compatibility_p"],0.)
    def test_shift_matched_multiple_day_bouts(self):
        a=[3,3,0,0,0,0,0]
        b=[3,3,0,0,0,0,0]
        y=score_by_all_rotations(a,b)
        self.assertEqual(y[0],4)
        self.assertEqual(sum(y)/len(y),16/7)
    def test_cross_month_block_separation(self):
        start=date(2023,1,25)
        days={start+timedelta(days=i):tuple(range(24)) for i in range(14)}
        runs=contiguous_runs(days,min_days=3)
        self.assertEqual([len(r) for r in runs],[7,7])
        self.assertEqual(MIN_RUN_DAYS,7)
    def test_half_day_not_full_effort(self):
        from v145_blockshift import local_time
        # Original Excel UTC serial hours, summer day, show <24 hours excluded
        day=int((date(2019,7,15)-date(1899,12,30)).days)*24
        sample={day+i for i in range(12)}
        self.assertEqual(len(eligible_complete_days(sample)),0)
if __name__=="__main__":unittest.main()
