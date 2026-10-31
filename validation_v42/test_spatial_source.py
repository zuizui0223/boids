"""Source-only spatial and timestamp logic with invented WGS84 animals."""
import datetime as dt
import unittest
import spatial_source as m

BASE=dt.datetime(2010,5,1,8)
LAT=m.STATION_LAT
LON=m.STATION_LON
def make(name,offlat=0.,offtime=0.,n=10):
    return [(name,BASE+dt.timedelta(minutes=10*i+offtime),
             LAT+offlat,LON) for i in range(n)]
class SyntheticGeoTimes(unittest.TestCase):
 def test_source_protocol_immutability(self):
    self.assertEqual(m.RADII_KM,(.1,.2,1.))
    self.assertEqual(m.PRIMARY_RADIUS_KM,.2)
    self.assertEqual(m.TARGET_YEARS,(2010,2011,2012))
    self.assertEqual(m.MIN_FOCAL_BIRDS,20)
 def test_close_other_bird_with_past_heading_but_no_social_claim(self):
    pts=make("private-A",0.)+make("private-B",0.0005)
    x=m.coordinate_source_support_fixture(pts) if hasattr(m,"coordinate_source_support_fixture") else None
    # Structural gate expects 39 birds; override only the artificial constant
    old_n,old_rows=m.EXPECTED_SOURCE_BIRDS,m.EXPECTED_SOURCE_VALID_FIXES
    try:
        m.EXPECTED_SOURCE_BIRDS=2;m.EXPECTED_SOURCE_VALID_FIXES=len(pts)
        o=m.coordinate_source_support(pts)
    finally:m.EXPECTED_SOURCE_BIRDS,m.EXPECTED_SOURCE_VALID_FIXES=old_n,old_rows
    a=o["2010_2012_support_all_fixed_radii"]["0.2_km"]
    self.assertGreater(a["potential_spatially_cotimed_focal_starts"],0)
    self.assertEqual(a["source_focal_birds_with_neighbor_candidate"],2)
    self.assertEqual(o["status"],m.STOP)
 def test_far_co_timed_birds_do_not_count_as_spatial_neighbors(self):
    pts=make("private-A",0.)+make("private-B",0.03)
    old_n,old_rows=m.EXPECTED_SOURCE_BIRDS,m.EXPECTED_SOURCE_VALID_FIXES
    try:
        m.EXPECTED_SOURCE_BIRDS=2;m.EXPECTED_SOURCE_VALID_FIXES=len(pts)
        o=m.coordinate_source_support(pts)
    finally:m.EXPECTED_SOURCE_BIRDS,m.EXPECTED_SOURCE_VALID_FIXES=old_n,old_rows
    a=o["2010_2012_support_all_fixed_radii"]["1_km"]
    self.assertEqual(a["potential_spatially_cotimed_focal_starts"],0)
 def test_only_other_past_heading_at_or_before_target_start(self):
    # B has two original fixes 11 min after A timestamps; at the focal
    # original t the latest usable B endpoint must be within earlier 5 min.
    pts=make("private-A",0.,0.)+make("private-B",0.0005,7.)
    old_n,old_rows=m.EXPECTED_SOURCE_BIRDS,m.EXPECTED_SOURCE_VALID_FIXES
    try:
        m.EXPECTED_SOURCE_BIRDS=2;m.EXPECTED_SOURCE_VALID_FIXES=len(pts)
        o=m.coordinate_source_support(pts)
    finally:m.EXPECTED_SOURCE_BIRDS,m.EXPECTED_SOURCE_VALID_FIXES=old_n,old_rows
    self.assertLess(o["2010_2012_support_all_fixed_radii"]["0.2_km"]["potential_spatially_cotimed_focal_starts"],
                    o["original_frozen_25km_local_source_support"]["original_focal_four_fix_starts_all_local_25km"])
 def test_two_other_birds_distinct(self):
    pts=make("private-A",0.)+make("private-B",.0005)+make("private-C",.0007)
    old_n,old_rows=m.EXPECTED_SOURCE_BIRDS,m.EXPECTED_SOURCE_VALID_FIXES
    try:
        m.EXPECTED_SOURCE_BIRDS=3;m.EXPECTED_SOURCE_VALID_FIXES=len(pts)
        o=m.coordinate_source_support(pts)
    finally:m.EXPECTED_SOURCE_BIRDS,m.EXPECTED_SOURCE_VALID_FIXES=old_n,old_rows
    self.assertGreater(o["all_2008_2014_yearly_spatial_time_opportunity_counts"]["2010"]
                  ["focal_with_two_or_more_other_PAST_heading_within_0.2_km"],0)
 def test_public_gauge_radius_not_optimized_to_observed_source(self):
    self.assertAlmostEqual(m.STUDY_GAUGE_RADIUS_KM,25.)
    self.assertAlmostEqual(m.NEIGHBOR_MAX_PREVIOUS_FIX_AGE_MIN,5.)
 def test_no_raw_original_GPS_location_export(self):
    import inspect
    s=inspect.getsource(m.run)
    self.assertIn("no_animal_GPS_coordinates_ID_or_real_UTC_timestamps_exported",s)
    self.assertNotIn("GPS_binary_output",s)
if __name__=="__main__":unittest.main()
