"""v169 known-truth fixtures — no original bird outcomes loaded."""
import unittest
from datetime import datetime,timezone
import numpy as np
from original_tide_component_ablation import (
    TIDE_PANELS,SHIFTS,PANEL_ORDER,ablation_feature_matrices,
    model_gains,MIN_SOURCE_STRATUM_HOURS
)

def row(year=2018,bird="b",clock=10,night=False):
    t=datetime(year,7,10,clock,1,0,tzinfo=timezone.utc)
    e={
       "source_utc_event":t,"source_month":7,"private_bird":bird,
       "original_acc_forage_events":3,"original_acc_inactive_events":7
    }
    heights=(.4,.6,.8,.5)
    phases=(1,-1,1,-1)
    return (e,"night" if night else "day",
            tuple((h,p) for h,p in zip(heights,phases)),28)

class TestTideComponentDecomposition(unittest.TestCase):
    def test_frozen_component_panels_have_same_native_physical_terms(self):
        self.assertEqual(SHIFTS,(0,3,7,11))
        self.assertEqual(TIDE_PANELS["FULL"],(0,1,2,3,4))
        self.assertEqual(TIDE_PANELS["HEIGHT"],(0,))
        self.assertEqual(TIDE_PANELS["PHASE"],(1,))
        self.assertEqual(TIDE_PANELS["HEIGHT_PHASE_CROSS"],(0,1,2))
        self.assertEqual(TIDE_PANELS["HEIGHT_PHASE_NIGHT"],(0,1,3,4))
        self.assertEqual(MIN_SOURCE_STRATUM_HOURS,1500)
    def test_source_true_history_nested_in_solar(self):
        src=[row(),row(clock=11,night=True)]
        cols=ablation_feature_matrices(src,np.array([0,1]),
                                       np.array([0,1]),2018,["b"])
        self.assertEqual(len(cols),25)
        self.assertEqual(cols["HISTORY"].shape[1],13)
        self.assertEqual(cols["HEIGHT_0"].shape[1],14)
        self.assertEqual(cols["FULL_0"].shape[1],18)
        self.assertEqual(cols["FULL_11"].shape,cols["FULL_0"].shape)
        self.assertAlmostEqual(cols["FULL_0"][0,-1],0.3)
        self.assertAlmostEqual(cols["FULL_0"][0,-6],0.4)
        self.assertAlmostEqual(cols["FULL_0"][0,-5],1.0)
        self.assertAlmostEqual(cols["FULL_0"][1,-3],1.0) # true night x rising tide phase
    def test_weekly_model_estimator_selects_global_wrong_after_week_mean(self):
        names=["HISTORY"]+[p+"_"+str(off) for off in SHIFTS for p in PANEL_ORDER]
        # Construct source scores: correct-time beats each wrong on average,
        # but not every individual week.
        a=np.array([.5,.5])
        data=np.zeros((2,len(names)))
        data[:,0]=a
        for j,name in enumerate(names[1:],1):
            data[:,j]=np.array([.30,.50]) if name.endswith("_0") else np.array([.45,.45])
        out=model_gains(data,names,np.array([22,23]),nboot=50,seed=42)
        q=out["by_component_panel"]["HEIGHT"]["correct_vs_best_wrong"]
        self.assertAlmostEqual(q["mean_MSE_improvement_positive_is_better"],.05)
        self.assertEqual(q["original_2019_week_positive_n"],1)
        self.assertEqual(q["total_2019_original_weeks"],2)
        self.assertEqual(len(q["matched_estimand_2019_week_bootstrap_descriptive_95_interval"]),2)
    def test_wrong_source_model_ablation_rejects_nonfinite_tide(self):
        src=[row()]
        e,s,matches,w=src[0]
        source=[(e,s,((float("nan"),1),)+matches[1:],w)]
        with self.assertRaises(AssertionError):
            ablation_feature_matrices(source,np.array([0]),
                                      np.array([0]),2018,["b"])

if __name__=="__main__":
    unittest.main()
