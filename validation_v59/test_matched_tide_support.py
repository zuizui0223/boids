"""v59 source-only synthetic tests; never evidence of wildlife tidal effects."""
import unittest
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from matched_tide_support import (
    audit_source_only,_cyclic_clock,_cyclic_doy,STAGES,
    MIN_PAIRS,MIN_BIRDS,MIN_WEEKS,MIN_MONTHS)

def row(bird,day,phase,*,lon=5.5,water=.1,hour=12,pe=1.,pn=0.,speed=1.):
    return {"id":bird,"t":datetime(2011,5,1,tzinfo=timezone.utc)+timedelta(days=day,hours=hour),
            "lat":53.4,"lon":lon,"h":water,"phase":phase,
            "previous_e":pe,"previous_n":pn,"previous_speed_log":speed,
            "target_e":1.,"target_n":0.}

class ActualSourceMatchingTests(unittest.TestCase):
    def test_clock_and_day_wrapping(self):
        self.assertEqual(_cyclic_clock(23,1),2)
        self.assertEqual(_cyclic_doy(360,5),10)

    def test_same_bird_real_opposite_phase_not_reused(self):
        a=[row("a",0,1),row("a",2,-1),row("a",4,1)]
        r=audit_source_only(a)
        self.assertEqual(r["unique_disjoint_actual_opposite_tide_pairs"],1)
        self.assertEqual(r["actual_next_heading_effect"],"NOT_ESTIMATED")
        self.assertEqual(r["admission"],"NOT_ADMITTED_INSUFFICIENT_REAL_MATCHED_SOURCE_SUPPORT")
        other=deepcopy(a)
        for x in other:x.update(target_e=1e6,target_n=-1e6)
        self.assertEqual(r,audit_source_only(other))
        self.assertNotIn("a",repr(r["anonymous_pairs_per_bird_min_median_max"]))

    def test_each_frozen_source_gate_excludes_invalid_pair(self):
        p=row("x",0,1)
        bad=[{"id":"other"},{"lon":6.1},{"h":.35},
             {"t":p["t"]+timedelta(hours=2)},
             {"t":p["t"]+timedelta(days=100)},
             {"t":p["t"]+timedelta(days=2,hours=6)},
             {"previous_e":-1.},{"previous_speed_log":1.6}]
        for mutation in bad:
            with self.subTest(mutation=mutation):
                q={**row("x",2,-1),**mutation}
                self.assertEqual(audit_source_only([p,q])["unique_disjoint_actual_opposite_tide_pairs"],0)

    def test_same_B_cell_but_not_another_bird(self):
        rows=[row("a",0,1),row("a",2,-1),row("b",2,-1),
              row("a",4,1,lon=5.6),row("a",6,1)]
        r=audit_source_only(rows)
        self.assertEqual(r["unique_disjoint_actual_opposite_tide_pairs"],1)
        self.assertEqual(r["rising_rows_with_candidate_after_sequential_gates"][STAGES[0]],2)

    def test_duplicate_bad_phase_and_bad_time_hard_stop(self):
        base=[row("a",0,1),row("a",2,-1)]
        for invalid in [base+[deepcopy(base[0])],
                        [{**base[0],"phase":0},base[1]],
                        [{**base[0],"h":float("nan")},base[1]],
                        [{**base[0],"t":base[0]["t"].replace(tzinfo=None)},base[1]],
                        [{**base[0],"t":base[0]["t"].replace(year=2010)},base[1]]]:
            with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
                audit_source_only(invalid)

    def test_positive_admission_is_feasibility_not_heading(self):
        self.assertEqual((MIN_PAIRS,MIN_BIRDS,MIN_WEEKS,MIN_MONTHS),(60,3,8,3))
        data=[]
        for bird in range(3):
            for i in range(35):
                data.extend([row(f"bird{bird}",2*i,1),row(f"bird{bird}",2*i+1,-1)])
        report=audit_source_only(data)
        self.assertEqual(report["unique_disjoint_actual_opposite_tide_pairs"],105)
        self.assertEqual(report["birds_with_at_least_ten_pairs"],3)
        self.assertEqual(report["admission"],"SOURCE_SUPPORT_ADMITTED_FOR_LATER_PREREGISTERED_OUTCOME")
        self.assertEqual(report["actual_next_heading_effect"],"NOT_ESTIMATED")
        self.assertEqual(report,audit_source_only(list(reversed(data))))

if __name__=="__main__":
    unittest.main()
