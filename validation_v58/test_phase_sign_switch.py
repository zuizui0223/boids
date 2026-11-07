"""Pure known-truth tests: v58 fixed-B/h phase sign switch, NOT observed ecology."""
from __future__ import annotations

import math
import unittest
from datetime import datetime,timedelta,timezone
import numpy as np

from phase_sign_switch import (phase_versions,phase_rotation,analyse_switch,
                               _vectors,MIN_ROWS,MIN_BIRDS,MIN_WEEKS)

def synthetic_rows(year,n_birds=5,each=300):
    rows=[]
    for b in range(n_birds):
        for i in range(each):
            ph=1 if i%2 else -1
            t=datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=4*i)
            target=[1.,0.] if ph==1 else [0.,1.]
            rows.append(dict(id=f"bird{b}",t=t,phase=ph,ghost_phase=-ph,
                h=.5*math.sin(i*.071+b*.11),lat=53.4+.01*b,lon=5.7+.001*i,
                clocksin=math.sin(i),clockcos=math.cos(i),
                yearsin=math.sin(i*.01),yearcos=math.cos(i*.01),
                previous_e=.6,previous_n=.8,previous_speed_log=1.,
                target_e=target[0],target_n=target[1]))
    return rows

def known_forecast(train,test,level):
    if level!=1:raise AssertionError("v58 only uses one unchanged phase model")
    return np.asarray([[1.,0.] if r["phase"]==1 else [0.,1.] for r in test])

class PhaseSignSourceTests(unittest.TestCase):
    def setUp(self):
        self.train=synthetic_rows(2010)
        self.test=synthetic_rows(2011)

    def test_flip_changes_only_phase_not_original_B_or_future_target(self):
        plus,minus=phase_versions(self.test)
        self.assertEqual(len(plus),len(self.test))
        self.assertEqual(len(minus),len(self.test))
        for old,a,b in zip(self.test,plus,minus):
            self.assertEqual(a["phase"],1)
            self.assertEqual(b["phase"],-1)
            self.assertEqual({k:v for k,v in a.items() if k!="phase"},
                             {k:v for k,v in b.items() if k!="phase"})
            self.assertEqual({k:v for k,v in old.items() if k!="phase"},
                             {k:v for k,v in a.items() if k!="phase"})
        self.assertTrue(any(r["phase"]==-1 for r in self.test))
        with self.assertRaisesRegex(ValueError,"ACTUAL_PHASE"):
            phase_versions([{**self.test[0],"phase":0}])

    def test_sign_and_wrap_east_north_orientation(self):
        right=np.asarray([[1.,0.],[1.,0.]])
        up=np.asarray([[0.,1.],[0.,-1.]])
        angles=phase_rotation(right,up)
        self.assertTrue(np.allclose(angles,[90.,-90.]))
        self.assertTrue(np.allclose(phase_rotation(up,right),-angles))
        small=np.array([[math.cos(math.radians(179)),math.sin(math.radians(179))]])
        past=np.array([[math.cos(math.radians(-179)),math.sin(math.radians(-179))]])
        self.assertAlmostEqual(float(phase_rotation(past,small)[0]),-2.,places=8)
        with self.assertRaisesRegex(ValueError,"UNDEFINED"):
            phase_rotation(np.array([[0.,0.]]),np.array([[1.,0.]]))

    def test_real_phase_better_than_opposite_on_identical_original_rows(self):
        calls=[]
        def fit(train,test,level):
            calls.append((len(train),len(test),level))
            return known_forecast(train,test,level)
        result=analyse_switch(self.train,self.test,fit,bird_draws=180,week_draws=120)
        self.assertEqual(result["admission"],"MODEL_FIXED_PHASE_SWAP_ON_ORIGINAL_HELDOUT_GPS")
        self.assertEqual(calls,[(1500,4500,1)])
        self.assertEqual(result["test_original_rows"],1500)
        self.assertTrue(result["identical_actual_predictions_replayed"])
        m=result["main"]["metrics"]
        self.assertAlmostEqual(m["actual_minus_flipped_cosine_loss_gain"]["pooled_equal_bird_mean"],1.)
        self.assertAlmostEqual(m["actual_minus_flipped_angle_error_gain_degrees"]["pooled_equal_bird_mean"],90.)
        self.assertAlmostEqual(m["model_phase_switch_absolute_angle_degrees"]["pooled_equal_bird_mean"],90.)
        self.assertEqual(m["actual_minus_flipped_cosine_loss_gain"]["positive_birds"],5)
        self.assertAlmostEqual(m["model_implied_signed_switch"]["equal_bird_circular_mean_degrees"],-90.)
        self.assertTrue(all(r["admission"]=="MODEL_SWITCH_AND_OBSERVED_ORIGINAL_HEADING_SCORING"
                     for r in result["original_phase_subgroups"].values()))
        self.assertTrue(all(r["admission"]=="MODEL_SWITCH_AND_OBSERVED_ORIGINAL_HEADING_SCORING"
                     for r in result["source_height_quartile_subgroups"].values()))

    def test_model_switch_geometry_does_not_depend_on_future_target(self):
        def fit(train,test,level):return known_forecast(train,test,level)
        original=analyse_switch(self.train,self.test,fit,bird_draws=20,week_draws=20)
        altered=[{**r,"target_e":-r["target_e"],"target_n":-r["target_n"]}
                 for r in self.test]
        changed=analyse_switch(self.train,altered,fit,bird_draws=20,week_draws=20)
        a=original["main"]["metrics"]
        b=changed["main"]["metrics"]
        self.assertEqual(a["model_implied_signed_switch"],b["model_implied_signed_switch"])
        self.assertEqual(a["model_phase_switch_absolute_angle_degrees"],
                         b["model_phase_switch_absolute_angle_degrees"])
        self.assertNotEqual(a["actual_minus_flipped_cosine_loss_gain"],
                            b["actual_minus_flipped_cosine_loss_gain"])

    def test_missing_phase_group_is_not_falsely_admitted(self):
        train=[{**r,"phase":1} for r in self.train]
        result=analyse_switch(train,self.test,known_forecast,bird_draws=50,week_draws=50)
        self.assertTrue(all(group["admission"]=="NOT_ADMITTED_SOURCE_OR_BOTH_PHASES_IN_TRAIN"
                            for group in result["source_height_quartile_subgroups"].values()))

    def test_cohort_support_threshold_is_preserved(self):
        self.assertEqual((MIN_ROWS,MIN_BIRDS,MIN_WEEKS),(1000,3,4))
        result=analyse_switch(self.train,self.test[:999],known_forecast,bird_draws=20,week_draws=20)
        self.assertEqual(result["admission"],"NOT_ADMITTED_ORIGINAL_TRAIN_OR_TEST_SAMPLE")
        self.assertNotIn("main",result)

    def test_undefined_cosine_bearing_is_hard_stop_not_biological_null(self):
        with self.assertRaisesRegex(ValueError,"UNDEFINED"):
            analyse_switch(self.train,self.test,
                lambda a,b,c:np.zeros((len(b),2)),bird_draws=20,week_draws=20)
        with self.assertRaisesRegex(ValueError,"DIMENSIONS"):
            _vectors(self.test,np.zeros((2,2)))

    def test_original_test_predicted_value_must_equal_chosen_branch(self):
        def bad_forecast(train,test,level):
            vals=known_forecast(train,test,level)
            vals[0]*=-1
            return vals
        with self.assertRaisesRegex(ValueError,"ACTUAL_PHASE_REPLAY"):
            analyse_switch(self.train,self.test,bad_forecast,bird_draws=20,week_draws=20)

    def test_clustered_CI_targets_differ_from_per_episode_but_both_are_reported(self):
        result=analyse_switch(self.train,self.test,known_forecast,bird_draws=300,week_draws=200)
        m=result["main"]["metrics"]["actual_minus_flipped_angle_error_gain_degrees"]
        self.assertEqual(len(m["paired_whole_bird_bootstrap95"]),2)
        self.assertEqual(len(m["paired_whole_week_bootstrap95"]),2)
        self.assertEqual(m["positive_birds"],5)
        self.assertGreater(result["main"]["test_weeks"],4)

if __name__=="__main__":unittest.main()
