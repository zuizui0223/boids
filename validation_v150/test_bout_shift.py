"""Original-independent bit-mask fixtures for v150; no fish observations."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v150_bout_shift import beginnings, safe_central_hours, shifts_for_day

class TestV150(unittest.TestCase):
    def test_isolated_exact_simultaneous_onset(self):
        a=(1<<10);b=(1<<10)
        s=shifts_for_day(a,b,tuple(range(8,13)))
        self.assertEqual(s,[1,0,0,0,0])
        self.assertEqual(shifts_for_day(beginnings(a),beginnings(b),tuple(range(8,13))),s)
    def test_bout_order_and_non_wrap_shift_preserved(self):
        a=sum(1<<i for i in range(9,13))
        b=sum(1<<i for i in range(9,13))
        s=shifts_for_day(a,b,tuple(range(8,14)))
        self.assertEqual(s,[4,2,3,3,2])
        self.assertEqual(beginnings(a),1<<9)
        self.assertEqual(beginnings(b),1<<9)
    def test_solar_class_stable_window(self):
        flags=[False]*24
        for i in range(8,16):flags[i]=True
        valid=safe_central_hours(flags)
        self.assertIn(10,valid)
        self.assertIn(13,valid)
        self.assertNotIn(7,valid)
        self.assertNotIn(8,valid)
        self.assertNotIn(9,valid)
        self.assertNotIn(14,valid)
        self.assertNotIn(15,valid)
    def test_boundary_rejection(self):
        with self.assertRaises(ValueError):
            shifts_for_day(1,1,[0])
        with self.assertRaises(ValueError):
            safe_central_hours([True]*23)

if __name__=="__main__":unittest.main()
