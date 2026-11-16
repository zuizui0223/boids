"""Original-independent known-truth tests: true previous 15m source and score."""
import unittest
from datetime import datetime,timedelta,timezone
import numpy as np
from bird_tide_after_prev15 import (
    source_actual_previous,source_gate,score_grouped,NAMES,GHOSTS,RIDGE_LAMBDA,
    MIN_HISTORY_PAIRS
)

def make_record(bird,minute,week=23,day="day"):
    t=datetime(2018,6,4,tzinfo=timezone.utc)+timedelta(minutes=minute)
    return ({"private_bird":bird,"source_utc_event":t,"source_month":6},day,None,week)

class TestV165(unittest.TestCase):
    def test_actual_previous_quarterhour_no_gap_imputation(self):
        cases=[make_record("bird1",0),make_record("bird1",15),
               make_record("bird1",45),make_record("bird2",15)]
        idx,prev,qa=source_actual_previous(cases)
        self.assertEqual(idx.tolist(),[1])
        self.assertEqual(prev.tolist(),[0])
        self.assertEqual(qa["MATCHED_15MIN_SAME_BIRD_WITHIN_WEEK"],1)
        self.assertEqual(qa["NO_GENUINE_PREVIOUS_15MIN_BIN"],3)
    def test_week_boundary_rejects_prior_label(self):
        cases=[make_record("bird1",0,week=23),
               make_record("bird1",15,week=24)]
        idx,prev,qa=source_actual_previous(cases)
        self.assertEqual(idx.size,0)
        self.assertEqual(qa["CROSS_ISO_WEEK_BOUNDARY_REJECTED"],1)
    def test_source_gate_hard_stop_for_tiny_original(self):
        cases=[make_record("x",0),make_record("x",15)]
        idx,prev,qa=source_actual_previous(cases)
        gate=source_gate(cases,idx,prev)
        self.assertFalse(gate["all_predeclared_source_gates_pass"])
    def test_bird_and_week_equal_scoring(self):
        y=np.asarray([0,0,0,1],dtype=float)
        pred={"A":np.asarray([0,0,0,0],dtype=float),
              "B":np.asarray([0,0,0,1],dtype=float)}
        weeks=np.asarray([21,21,22,22])
        bird=np.asarray([1,1,1,2])
        wk,n,sc,src=score_grouped(y,pred,weeks,bird)
        self.assertEqual(wk.tolist(),[21,22])
        self.assertEqual(n,["A","B"])
        self.assertAlmostEqual(sc[0,0],0)
        self.assertAlmostEqual(sc[1,0],0.5)
        self.assertAlmostEqual(sc[1,1],0)
    def test_fixed_model_families(self):
        self.assertEqual(RIDGE_LAMBDA,20.)
        self.assertEqual(MIN_HISTORY_PAIRS,25000)
        self.assertEqual(GHOSTS,(3,7,11))
        self.assertIn("HISTORY_TIDE0",NAMES)
        self.assertIn("HISTORY_TIDE11",NAMES)

if __name__=="__main__":unittest.main()
