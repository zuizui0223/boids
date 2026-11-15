"""Only fake hourly masks, never real acoustic outcomes."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v152_solar_day_shift import exact_rotations,STRATA,ALL24,summary_panel,empty_agg,add_to

def selectors():
    return [
        {"dawn_transition":1,"dusk_transition":2,"stable_night":4,
         "stable_day":8,"midnight_legacy":ALL24^15},
        {"dawn_transition":2,"dusk_transition":4,"stable_night":8,
         "stable_day":16,"midnight_legacy":ALL24^30},
    ]

class TestV152(unittest.TestCase):
    def test_day_shift_exact_but_diel_clock_fixed(self):
        a=[3,3]
        b=[1,2]
        s=exact_rotations(a,b,selectors())
        actual=sum(s[k][0] for k in STRATA)
        swapped=sum(s[k][1] for k in STRATA)
        self.assertEqual(actual,2)
        self.assertEqual(swapped,2)
        agg=empty_agg();add_to(agg,s)
        self.assertEqual(sum(agg[k]["O"] for k in STRATA),actual)
        self.assertEqual(sum(agg[k]["E"] for k in STRATA),2)
    def test_can_have_dawn_excess_but_no_stable_excess(self):
        sel=[{"dawn_transition":1,"dusk_transition":2,"stable_night":4,"stable_day":8,
              "midnight_legacy":ALL24^15}]*2
        a=[1,0];b=[1,0]
        score=exact_rotations(a,b,sel)
        v=empty_agg();add_to(v,score)
        result=summary_panel(v)
        self.assertEqual(result["dawn_transition"]["O"],1)
        self.assertAlmostEqual(result["dawn_transition"]["E"],.5)
        self.assertEqual(result["stable_day"]["O"],0)
        self.assertEqual(result["dusk_transition"]["O"],0)
    def test_refuse_nonpartition(self):
        selectors=[{"dawn_transition":1,"dusk_transition":2,"stable_night":4,"stable_day":8,
                    "midnight_legacy":ALL24^15}]
        with self.assertRaises(ValueError):exact_rotations([0,0],[0,0],selectors)
        with self.assertRaises(AssertionError):exact_rotations([3],[3],
                [{"dawn_transition":0,"dusk_transition":0,"stable_night":0,
                 "stable_day":0,"midnight_legacy":0}])

if __name__=="__main__":unittest.main()
