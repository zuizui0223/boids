"""Source-independent tests for the v160 prospective site splitter."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from porpoise_site_holdout import fixed_features,gate,loss,MODELS,GHOST_MODELS
import numpy as np

class TestForagingSourceConditional(unittest.TestCase):
    def test_season_clock_and_detected_click_opportunity(self):
        a,prev=fixed_features(2018,156,12,100,10)
        self.assertEqual(len(a),10)
        self.assertEqual(len(prev),11)
        self.assertAlmostEqual(prev[-1],np.log1p(10))
        self.assertAlmostEqual(a[-1],np.log1p(100))
    def test_never_rescue_ineligible_site(self):
        training=[{"Y":1} for _ in range(1200)]
        test=[{"Y":1} for _ in range(400)]
        allowed,support=gate(training,test)
        self.assertFalse(allowed)
        self.assertEqual(support["test_buzz_negative"],0)
    def test_ghost_has_different_hour_support(self):
        self.assertEqual(GHOST_MODELS,("C2_common","C3_previous_1h_buzz","G24_previous_day_buzz"))
        self.assertNotIn("C0_constant",GHOST_MODELS)
    def test_proper_binary_loss(self):
        y=np.array([1,0,1,0])
        good=np.array([.9,.1,.8,.2])
        bad=np.array([.1,.9,.2,.8])
        self.assertLess(loss(y,good),loss(y,bad))
        self.assertIn("C2_previous_click_density",MODELS)
    def test_negative_hours_must_be_source_obs(self):
        real={10:{"clicks":2,"buzz":0},12:{"clicks":30,"buzz":10}}
        self.assertNotIn(11,real)
        self.assertNotEqual(sum(x["buzz"]==0 for x in real.values()),3)

if __name__=="__main__":unittest.main()
