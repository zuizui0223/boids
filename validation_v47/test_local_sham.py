"""Invented fixed-source environmental grid/phase and sham tests; no wild GPS."""
import unittest
import datetime as dt
import inspect
import numpy as np
import local_sham as v

class KnownTruth(unittest.TestCase):
 def test_fixed_crs_and_grids_and_cohort(self):
    self.assertEqual(v.GRID_M,2000.)
    self.assertEqual(v.PERM,500)
    self.assertEqual(v.MIN_EPISODES,1000)
    self.assertEqual(v.MIN_BIRDS,10)
    self.assertEqual(v.PROTOCOL.split("/")[-1],"V47_LOCATION_MATCHED_TIDAL_HEADING_SHAM_PROTOCOL.md")
 def test_meter_grid_boundary_and_negative_floor(self):
    self.assertEqual(v.spatial_cell(0.,0.),(0,0))
    self.assertEqual(v.spatial_cell(1999.9,-.1),(0,-1))
    self.assertEqual(v.spatial_cell(2000.,-2000.),(1,-1))
    self.assertEqual(v.spatial_cell(-2000.0001,4000.),(-2,2))
 def test_key_protects_same_bird_UTC_year_quarter_clock_tide_and_location(self):
    t=dt.datetime(2010,4,1,8,0)
    a=v.fixed_group_key(3,t,.1,1000.,-1000.)
    self.assertEqual(a,(3,2010,1,1,"rising",0,-1))
    self.assertNotEqual(v.fixed_group_key(4,t,.1,1000.,-1000.),a)
    self.assertNotEqual(v.fixed_group_key(3,t,-.1,1000.,-1000.),a)
    self.assertNotEqual(v.fixed_group_key(3,dt.datetime(2011,4,1,8),.1,1000.,-1000.),a)
    self.assertIsNone(v.fixed_group_key(3,t,0.,1000.,-1000.))
 def test_timezone_aware_original_timestamp_rejected(self):
    with self.assertRaisesRegex(ValueError,"UTC"):
        v.fixed_group_key(1,dt.datetime(2010,1,1,tzinfo=dt.timezone.utc),1,0,0)
 def test_no_favorable_threshold_search(self):
    self.assertEqual((v.MIN_EPISODES_PER_BIRD,v.MIN_MONTHS,v.MIN_YEARS),(10,4,2))
    self.assertEqual(v.SEED,20261031)
    self.assertEqual(v.BIRD_BOOT,10000)
 def test_zero_source_support_emits_no_sham_scores(self):
    before=np.array([[1.,0.],[1.,0.]])
    after=np.array([[0.,1.],[1.,0.]])
    near=np.array([[0.,1.],[0.,1.]])
    far=np.array([[1.,0.],[1.,0.]])
    pinned={"bird":np.array([0,0]),
            "start":np.array([np.datetime64("2010-01-01","us")]*2)}
    result=v.local_sham_score(pinned,np.array([0,1]),before,after,near,far,
                              [np.array([0,1])],{"source":"fixture"})
    self.assertEqual(result["status"],"NOT_ADMITTED_LOCAL_MATCHED_SHAM_SUPPORT")
    self.assertFalse(result["any_new_time_specific_heading_effect_exported"])
    self.assertNotIn("observed_minus_sham",str(result))
 def test_mirror_turn_geometry_exactly_reused(self):
    old=v.v46.geometry
    prev=np.array([[1.,0.],[1.,0.]])
    future=np.array([[0.,1.],[-1.,0.]])
    n=np.array([[0.,1.],[0.,1.]])
    f=np.array([[1.,0.],[1.,0.]])
    score,_,c=old(prev,future,n,f)
    turning=future-c[:,None]*prev
    self.assertTrue(np.allclose(np.sum(turning*(n-f),axis=1),score[:,0]))
 def test_previous_num_replay_mandatory_and_original_frozen(self):
    code=inspect.getsource(v.frozen_wild_replay)
    self.assertIn("v46.original_replay",code)
    self.assertIn("v46.score",code)
    self.assertIn("nested_close",code)
    self.assertIn("len(positions)!=4660",code)
 def test_origin_is_public_RWS_gauge_not_original_bird_position(self):
    self.assertAlmostEqual(v.GAUGE_LON,6.202908)
    self.assertAlmostEqual(v.GAUGE_LAT,53.468937)
 def test_sham_only_swaps_neighbor_pairs_not_focal_response(self):
    code=inspect.getsource(v.local_sham_score)
    self.assertIn("near[assignment]-far[assignment]",code)
    self.assertNotIn("turn_residual[assignment]",code)
 def test_no_raw_telemetry_output(self):
    code=inspect.getsource(v.run)
    self.assertIn("no_original_GPS_coordinates_bird_ID_times_or_tide_height_series_saved",code)

if __name__=="__main__":unittest.main()
