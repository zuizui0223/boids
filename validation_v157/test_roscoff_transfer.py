"""All v157 pre-outcome tests are synthetic, never actual acoustic source."""
import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from roscoff_transfer import (
    make_ghost_periods,is_supported,losses,MODELS,GHOST_MODELS,
    MIN_PRIMARY_TEST,MIN_GHOST_TEST
)

class TestRoscoffSourceMethods(unittest.TestCase):
    def test_one_and_two_wrong_source_periods_never_target(self):
        groups={k:[str(5*j+i+1) for i in range(5)] for j,k in
                enumerate(("Low","Medium","High","Very High"))}
        ghosts=make_ghost_periods(groups)
        self.assertEqual(len(ghosts),20)
        self.assertEqual(ghosts["1"],("2","3"))
        self.assertEqual(ghosts["5"],("1","2"))
        self.assertTrue(all(pid not in ref for pid,ref in ghosts.items()))
    def test_missing_period_category_not_invented(self):
        groups={k:[str(5*j+i+1) for i in range(5)] for j,k in
                enumerate(("Low","Medium","High","Very High"))}
        groups["High"]=groups["High"][:4]
        with self.assertRaises(AssertionError):
            make_ghost_periods(groups)
    def test_test_source_40h_and_25h_precommitted(self):
        self.assertEqual(MIN_PRIMARY_TEST,40)
        self.assertEqual(MIN_GHOST_TEST,25)
    def test_source_response_support_requires_negative_state(self):
        train=[{"A":1,"B":1} for _ in range(250)]
        test=[{"A":1,"B":1} for _ in range(70)]
        ok,q=is_supported(train,test)
        self.assertFalse(ok)
        self.assertEqual(q["heldout_A_positive"],70)
    def test_brier_and_logloss_are_proper(self):
        good,b=losses(np.array([0,1]),np.array([.1,.9]))
        bad,c=losses(np.array([0,1]),np.array([.9,.1]))
        self.assertLess(np.mean(good),np.mean(bad))
        self.assertLess(np.mean(b),np.mean(c))
    def test_other_source_day_ghosts_are_separate_from_real_hour(self):
        self.assertEqual(MODELS,("constant","environment","own_previous_1h","real_partner"))
        self.assertIn("wrong_source_day_plus1",GHOST_MODELS)
        self.assertIn("wrong_source_day_plus2",GHOST_MODELS)

if __name__=="__main__":
    unittest.main()
