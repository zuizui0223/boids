"""v16 fast 1-second turning: synthetic controls and pure anti-leakage tests only."""
from __future__ import annotations

import math
import random
import tempfile
import unittest
import zipfile
from pathlib import Path

import fast_turn_forecast as m


def artificial(flock,bird,release,now,stale,target):
    own=(0.,1.,0.,.5,.3)
    return m.Event(flock,release,bird,own,(now,0.,0.,1.),
                   (stale,0.,0.,1.),target)


class FastSourceAndTime(unittest.TestCase):
    def test_source_and_performance_are_frozen(self):
        self.assertEqual(m.ORIGINAL_SHA256,
           "7380feccd8c2e4e1675679411d1ee8075cd29ccbd2dada98e317ca88053ffbfa")
        self.assertEqual(m.HISTORIC_TRAIN,(5,6,7,8))
        self.assertEqual(m.FUTURE_RELEASE_MIN,9)
        self.assertEqual(m.FUTURE_RELEASE_MAX,15)
        self.assertEqual(m.RIDGE_ALPHA,30.)
        self.assertEqual(m.RAW_FIX_MAX_OFFSET_MS,200)
        self.assertEqual(len(m.SOURCE_FLOCKS),8)

    def test_nearest_past_does_not_read_future_partner(self):
        earlier=m.Fix(900,0,0,1.,1.)
        later=m.Fix(1050,0,0,1.,1.)
        track=m.BirdTrack("B",[earlier,later],[900,1050])
        self.assertIs(m.near(track,1000),later)
        self.assertIs(m.past(track,1000),earlier)
        self.assertIsNone(m.past(track,800))

    def test_relative_geometry_with_equal_age_translation(self):
        x=m.Fix(10000,100.,50.,math.pi/2,900.)
        y=m.Fix(10000,120.,50.,math.pi/2,900.)
        xold=m.Fix(0,-100.,-50.,math.pi/2,800.)
        yold=m.Fix(0,-80.,-50.,math.pi/2,800.)
        self.assertEqual(m.social_features(x,y),m.social_features(xold,yold))

    def test_directions_and_angular_wrap(self):
        x=m.Fix(1000,20.,30.,math.pi/2,100.)
        p=m.Fix(0,19.,30.,0.,99.)
        v=m.direction_features(x,p)
        self.assertEqual(len(v),5)
        self.assertAlmostEqual(v[0],1.)
        self.assertAlmostEqual(m.wrapped(2*math.pi+.12),.12)


class FastFlockPrediction(unittest.TestCase):
    def _world(self):
        rng=random.Random(19)
        events=[]
        for flock in m.SOURCE_FLOCKS:
            for release in (5,6,7,8,9,10,11,12,13,14,15):
                for j in range(90):
                    cur=rng.uniform(-1,1)
                    sta=rng.uniform(-1,1)
                    target=.36*cur+rng.gauss(0,.06)
                    events.append(artificial(flock,f"bird{j%5}",release,cur,sta,target))
        return events

    def test_synthetic_known_truth_present_partner_positive(self):
        world=self._world()
        r=m.evaluate(world,{})
        self.assertEqual(r["status"],"EXPLORATORY_INDEPENDENT_EIGHT_FLOCK_FAST_TURN_FORECAST")
        self.assertEqual(r["current_vs_stale"]["positive_flocks"],8)
        self.assertGreater(r["current_vs_stale"]["equal_flock_mean"],.01)
        self.assertEqual(len(r["per_flock"]),8)

    def test_no_future_target_leakage_into_design(self):
        e=artificial("01","B",5,.4,.1,.8)
        f=artificial("01","B",5,.4,.1,-.4)
        import numpy as np
        np.testing.assert_array_equal(m.design([e],"current"),
                                      m.design([f],"current"))

    def test_missing_flock_yields_no_primary_scores(self):
        events=[e for e in self._world() if e.flock!="08"]
        r=m.evaluate(events,{})
        self.assertEqual(r["status"],"FAST_NOT_ADMITTED_FROZEN_GATE")
        self.assertNotIn("per_flock",r)
        self.assertTrue(any("08" in reason for reason in r["failures"]))

    def test_clock_matched_targets_have_equal_support(self):
        e=[artificial("01","B",5,.1,-.2,.3)]
        self.assertEqual(m.design(e,"own").shape,(1,5))
        self.assertEqual(m.design(e,"current").shape,(1,9))
        self.assertEqual(m.design(e,"stale").shape,(1,9))
        with self.assertRaises(ValueError):
            m.design(e,"ghost")


if __name__=="__main__":
    unittest.main()
