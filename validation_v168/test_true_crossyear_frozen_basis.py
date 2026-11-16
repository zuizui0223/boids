"""Synthetic, source-free known truth for v168 real 2018->2019 transfer."""
import unittest
from datetime import datetime,timezone
import numpy as np
from v168_true_year_transfer import (
    original_features,true_window_y,MODELS,WRONG_DAYS,
    RIDGE_LAMBDA,MIN_TRAIN,MIN_ALL_TEST,PANELS
)
from run_original_2018_matched_week_holdout import ridge_fit_predict

def original_source(year,bird,hour,night=False):
    time=datetime(year,6,20,hour,11,30,tzinfo=timezone.utc)
    e={"source_utc_event":time,"source_month":6,
       "private_bird":bird,"original_acc_forage_events":3,
       "original_acc_inactive_events":7}
    same=(e,"night" if night else "day",
          ((0.4,1),(0.6,-1),(0.8,1),(0.3,-1)),25)
    return same

class TestYearTransfer(unittest.TestCase):
    def test_fixed_month_sun_clock_with_unseen_2019_bird(self):
        train=[original_source(2018,"a",9),original_source(2018,"b",10)]
        test=[original_source(2019,"new",9),original_source(2019,"a",10)]
        idx=np.asarray([0,1]);lag=np.asarray([0,1])
        train_neutral=original_features(train,idx,lag,2018,["a","b"],False)
        test_neutral=original_features(test,idx,lag,2019,["a","b"],False)
        self.assertEqual(set(train_neutral),set(MODELS))
        self.assertEqual(train_neutral["SOLAR"].shape,(2,12))
        self.assertEqual(test_neutral["SOLAR"].shape,(2,12))
        self.assertEqual(train_neutral["HISTORY_TIDE0"].shape,(2,18))
        self.assertEqual(test_neutral["HISTORY_TIDE11"].shape,(2,18))
        self.assertTrue(np.isfinite(test_neutral["HISTORY_TIDE7"]).all())
    def test_known_bird_original_onehot_frozen_from_2018(self):
        train=[original_source(2018,"a",9),original_source(2018,"b",10)]
        test=[original_source(2019,"b",9),original_source(2019,"a",10)]
        idx=np.asarray([0,1])
        x=original_features(train,idx,idx,2018,["a","b"],True)
        y=original_features(test,idx,idx,2019,["a","b"],True)
        self.assertEqual(x["SOLAR"].shape,(2,13))
        self.assertEqual(y["HISTORY_TIDE0"].shape,(2,19))
        self.assertEqual(x["SOLAR"][:,1].tolist(),[0.,1.])
        self.assertEqual(y["SOLAR"][:,1].tolist(),[1.,0.])
    def test_unseen_bird_cannot_get_misleading_fixed_effect(self):
        test=[original_source(2019,"brand_new",9)]
        with self.assertRaises(AssertionError):
            original_features(test,np.array([0]),np.array([0]),2019,["a","b"],True)
    def test_wrong_year_source_stops(self):
        test=[original_source(2019,"a",9)]
        with self.assertRaises(AssertionError):
            original_features(test,np.array([0]),np.array([0]),2018,["a"],False)
    def test_real_response_is_acc_events_not_feeding_minutes(self):
        test=[original_source(2019,"a",9)]
        self.assertAlmostEqual(true_window_y(test,np.array([0]))[0],.3)
    def test_original_ridge_and_fixed_wrong_dates_not_tuned(self):
        self.assertEqual(RIDGE_LAMBDA,20.)
        self.assertEqual(WRONG_DAYS,(3,7,11))
        self.assertEqual(PANELS,("NEUTRAL_ALL","KNOWN_BIRDS"))
        self.assertEqual(MIN_TRAIN,100000)
        self.assertEqual(MIN_ALL_TEST,50000)
        a=np.array([[1.,0.],[1.,1.],[1.,0.]])
        y=np.array([0.,1.,0.])
        p=ridge_fit_predict(a,y,a,lam=RIDGE_LAMBDA)
        self.assertTrue(np.isfinite(p).all())
        self.assertTrue(((p>=0)&(p<=1)).all())
    def test_best_wrong_global_score_must_be_selected_after_week_mean(self):
        # Crossing wrong model within weeks: choosing per-week best is different
        # from choosing best model after the full heldout-year week mean.
        models=np.array([[.02,.05,.11],[.11,.03,.04]])
        true=np.array([.02,.02])
        glob=float(models.mean(axis=0).min()-true.mean())
        week=float((models.min(axis=1)-true).mean())
        self.assertNotAlmostEqual(glob,week)

if __name__=="__main__":unittest.main()
