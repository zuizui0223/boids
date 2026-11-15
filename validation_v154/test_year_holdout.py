"""v154 source-free fake heldout model/feature invariants."""
import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v154_year_holdout import loss,brier,score_models,MODELS

class TestV154(unittest.TestCase):
    def test_scoring_proper_binary_direction(self):
        y=np.array([0,1,0,1])
        good=np.array([.1,.9,.2,.8])
        poor=np.array([.9,.1,.8,.2])
        self.assertLess(loss(y,good),loss(y,poor))
        self.assertLess(brier(y,good),brier(y,poor))
        self.assertEqual(MODELS[-1],"real_gauge_plus_partner")
    def test_never_fit_without_source_target_support(self):
        n=1800
        years=np.array([2019]*1200+[2020]*600)
        mats={k:np.ones((n,2),dtype=float) for k in
              ["base","real","ghost3","ghost11","partner"]}
        y=np.zeros(n,dtype=int)
        b=np.zeros(n,dtype=int)
        x=score_models(mats,y,b,years,2020)
        self.assertEqual(x["status"],"STOP_HOURS")
    def test_qualifying_source_counts_must_be_strict(self):
        n=2600
        years=np.array([2019]*1600+[2020]*1000)
        mats={k:np.ones((n,2),dtype=float) for k in
              ["base","real","ghost3","ghost11","partner"]}
        y=np.array([1]*100+[0]*2500)
        b=np.array([1]*100+[0]*2500)
        r=score_models(mats,y,b,years,2020)
        self.assertEqual(r["status"],"STOP_SOURCE_RESPONSE_SUPPORT")
        self.assertEqual(r["train_target_positive"],100)
        self.assertEqual(r["test_target_positive"],0)

if __name__=="__main__":unittest.main()
