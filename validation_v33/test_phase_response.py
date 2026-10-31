"""Pure known-truth for local tide movement; no original bird GPS."""
import datetime as dt
import math
import unittest
import phase_response as m
class Tests(unittest.TestCase):
 def test_haversine_and_offshore_geofence(self):
  self.assertAlmostEqual(m.haversine_km(53.,6.,53.,6.),0.)
  self.assertGreater(m.haversine_km(53.46,6.2,52.,6.2),25.)
 def test_nearest_tide_exact_UTC_with_halfstep_ties_earlier(self):
  self.assertEqual(m.nearest_tide_key(dt.datetime(2010,1,1,0,14)),dt.datetime(2010,1,1,0,10))
  self.assertEqual(m.nearest_tide_key(dt.datetime(2010,1,1,0,15)),dt.datetime(2010,1,1,0,10))
  self.assertEqual(m.nearest_tide_key(dt.datetime(2010,1,1,0,16)),dt.datetime(2010,1,1,0,20))
 def test_clock_month_matching_high_minus_low_with_invented_steps(self):
  bird="invented"
  base=dt.datetime(2010,5,1,9,0)
  # Four independent identical-hour successive steps in two tide classes.
  points=[]
  tide_values={}
  for day in (0,1,2,3,4,5,6,7,8,9,10,11):
   t=base+dt.timedelta(days=day)
   lat=53.468937;lon=6.202908
   points.append((bird,t,lat,lon))
   points.append((bird,t+dt.timedelta(minutes=60),lat,lon+(.01 if day>=6 else .001)))
   middle=t+dt.timedelta(minutes=30)
   tide_values[m.nearest_tide_key(middle)]=(-1. if day<6 else 1.)
  strata,qa=m.original_step_strata(points,tide_values,-.5,.5)
  self.assertGreater(qa["pairs_with_valid_RWS_tide_and_local_GPS"],10)
  self.assertIn(bird,strata)
  self.assertEqual(len(strata[bird]),1)
  self.assertGreater(strata[bird][0]["difference"],0.)
 def test_strict_source_only_quartile_support(self):
  with self.assertRaises(ValueError):m.source_level_quartiles({dt.datetime(2010,1,1):0.})
 def test_stop_if_too_few_matched_bird_hour_strata(self):
  out=m.evaluate({"private":[{"difference":0.2,"n_high":3,"n_low":4}]})
  self.assertEqual(out["status"],"NOT_ADMITTED_WITHIN_BIRD_TIDE_HOUR_MATCHING")
  self.assertFalse(out["any_ecological_tide_effect_exported"])
 def test_all_birds_equal_weight_after_gate(self):
  a={}
  for i in range(20):
   a[f"secret-{i:02d}"]=[{"difference":1. if i==0 else -.1,"n_high":2,"n_low":2}
                       for j in range(12+(i==0)*100)]
  out=m.evaluate(a)
  self.assertEqual(out["status"],"EXPLORATORY_ORIGINAL_HIGH_VS_LOW_TIDE_LOCAL_SPEED_ASSOCIATION")
  self.assertAlmostEqual(out["mean_high_minus_low_log_speed"],(1.-1.9)/20.)
  self.assertEqual(out["support"]["paired_original_bird_month_hour_strata"],340)
  self.assertNotIn("secret-",str(out))
  self.assertEqual(out,m.evaluate(a))
if __name__=="__main__":unittest.main()
