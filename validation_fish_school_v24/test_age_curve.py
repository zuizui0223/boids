"""v24 offline synthetic known-truth and source-support gates.

No original Puy or Niizato animal coordinates are accessed by these tests.
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v22"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v24"))
from forecast_transfer import SourceStop
from comparison import relative_other_mean
import age_curve as m


def make_pair():
    fps=50.
    ntime=1000
    nfish=3
    frame=np.arange(ntime,dtype=float)
    pos=np.empty((ntime,nfish,2))
    for fish in range(nfish):
        pos[:,fish,0]=.3*frame + (fish+1)*np.sin(frame/(20+fish*10)) + fish*5
        pos[:,fish,1]=.15*frame + (fish+1)*np.cos(frame/(30+fish*10)) -fish*5
    idx=np.arange(110,900)
    current=(pos[idx]-pos[idx-5])/(5/fps)
    old=(pos[idx-100]-pos[idx-105])/(5/fps)
    gg=np.arange(len(idx)*nfish*3,dtype=float).reshape(-1,3)/1000
    c=np.concatenate((gg,relative_other_mean(current,current).reshape(-1,2)),axis=1)
    z=np.concatenate((gg,relative_other_mean(old,current).reshape(-1,2)),axis=1)
    X={"geometry":gg,"current":c,"stale2s":z}
    base={
      "X":{"short":X,"delayed":X},
      "Y":{"short":np.zeros((len(gg),2)),"delayed":np.zeros((len(gg),2))},
      "source":{"sha":"CONSTRUCTED_ONLY"},
      "source_checks":{"no_future_trajectory_inputs":True}
    }
    return pos,idx,base


class OriginalCohortAndAgeTruth(unittest.TestCase):
    def test_no_change_to_own_or_current_geometry_across_six_ages(self):
        pos,idx,base=make_pair()
        out=m.source_age_panels(base,pos,idx,50.,5)
        self.assertEqual(list(out["X"]["short"]),list(m.MODELS))
        for model in m.MODELS:
            np.testing.assert_array_equal(out["X"]["short"][model][:,:3],
                                          base["X"]["short"]["geometry"])
        np.testing.assert_array_equal(out["X"]["short"]["age_0s"],
                                      base["X"]["short"]["current"])
        np.testing.assert_array_equal(out["X"]["short"]["age_2s"],
                                      base["X"]["short"]["stale2s"])
        self.assertEqual(out["past_source_frame_lags"],[0,5,10,25,50,100])

    def test_two_second_lag_is_not_fixed_focal_prior(self):
        pos,idx,base=make_pair()
        result=m.source_age_panels(base,pos,idx,50.,5)
        self.assertGreater(np.max(np.abs(result["X"]["short"]["age_1s"] -
                                         result["X"]["short"]["age_0s"])),.01)

    def test_future_source_rows_never_affect_past_feature_construction(self):
        pos,idx,base=make_pair()
        first=m.source_age_panels(base,pos,idx,50.,5)
        pos2=pos.copy()
        pos2[901:]+=10000.
        second=m.source_age_panels(base,pos2,idx,50.,5)
        for key in m.MODELS:
            np.testing.assert_array_equal(first["X"]["short"][key],second["X"]["short"][key])

    def test_intermediate_missing_source_position_is_fail_closed(self):
        pos,idx,base=make_pair()
        pos[120-25,0,0]=np.nan
        with self.assertRaises(SourceStop):
            m.source_age_panels(base,pos,idx,50.,5)

    def test_change_to_pinned_existing_source_feature_fails_replay(self):
        pos,idx,base=make_pair()
        base["X"]["short"]["current"]=base["X"]["short"]["current"].copy()
        base["X"]["short"]["current"][0,-1]+=3
        with self.assertRaises(SourceStop):
            m.source_age_panels(base,pos,idx,50.,5)

    def test_reject_wrong_clock_and_two_sec_history(self):
        pos,idx,base=make_pair()
        with self.assertRaises(SourceStop):
            m.source_age_panels(base,pos,idx,25.,5)
        with self.assertRaises(SourceStop):
            m.source_age_panels(base,pos,idx-10,50.,5)

    def test_delayed_subset_replayed_exactly(self):
        pos,idx,base=make_pair()
        nfish=3
        groups=np.arange(0,len(idx),2)
        rows=(groups[:,None]*nfish+np.arange(nfish)[None,:]).ravel()
        base["X"]["delayed"]={key:base["X"]["short"][key][rows].copy()
                              for key in base["X"]["short"]}
        base["Y"]["delayed"]=base["Y"]["short"][rows]
        z=m.source_age_panels(base,pos,idx,50.,5,rows)
        self.assertEqual(len(z["X"]["delayed"]["age_2s"]),len(rows))
        self.assertEqual(len(z["Y"]["delayed"]),len(rows))

    def test_model_names_and_prior_MSE_anchors_frozen(self):
        self.assertEqual(m.AGES,(0.,.1,.2,.5,1.,2.))
        self.assertEqual(m.MODELS[0],"geometry")
        self.assertEqual(m.ANCHORS["tetra"]["short"]["age_0s"],11.352981111900112)
        self.assertEqual(m.ANCHORS["ayu"]["delayed"]["age_2s"],30463.936132138184)

    def test_recording_wrong_count_is_source_stop(self):
        with self.assertRaises(SourceStop):
            m.assess({},"ayu")
        with self.assertRaises(SourceStop):
            m.assess({},"tetra")


if __name__=="__main__":unittest.main()
