import unittest
from v145_onset_null import onset_day_masks,tolerant_rotated_scores

class OnsetKnownTruth(unittest.TestCase):
    def test_cross_midnight_transition(self):
        x=onset_day_masks([1<<23,1])
        self.assertEqual(x,[1<<23,0])
    def test_first_hour_not_inferred(self):
        self.assertEqual(onset_day_masks([1,0,1<<9]),[0,0,1<<9])
    def test_timing_tolerance(self):
        a=[1<<3,1<<9,1<<13,1<<17]
        self.assertEqual(tolerant_rotated_scores(a,a,0),[4,0,0,0])
        b=[1<<4,1<<10,1<<14,1<<18]
        z=tolerant_rotated_scores(a,b,1)
        self.assertEqual(z[0],4)
        self.assertEqual(z[1],0)
    def test_too_wide_tolerance(self):
        with self.assertRaises(ValueError):
            tolerant_rotated_scores([1],[1],4)
if __name__=="__main__":unittest.main()
