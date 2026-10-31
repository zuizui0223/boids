"""Known truth, no actual bird tracks, original tide height or GPS accessed."""
import datetime as dt
import math
import unittest
import duty_phase_audit as a

class KnownTruth(unittest.TestCase):
 def test_immutable_tide_shifts_and_duration_bins(self):
  self.assertEqual(a.OFFSETS,(0,3,6))
  self.assertEqual(a.duration_bin(5),"SHORT_5_TO_30")
  self.assertEqual(a.duration_bin(29.99),"SHORT_5_TO_30")
  self.assertEqual(a.duration_bin(30),"MEDIUM_30_TO_90")
  self.assertEqual(a.duration_bin(89.99),"MEDIUM_30_TO_90")
  self.assertEqual(a.duration_bin(90),"LONG_90_TO_180")
  self.assertEqual(a.duration_bin(180),"LONG_90_TO_180")
  with self.assertRaises(ValueError):a.duration_bin(181)
 def test_source_day_and_phase_shift_same_actual_GPS_clock_stratum(self):
  # Original GPS candidate endpoints are invented. The tide reference alone is shifted.
  bird="private"
  astro={}
  pts=[]
  for d in range(40):
   t=dt.datetime(2010,5,1,9)+dt.timedelta(days=d)
   pts.append((bird,t,53.468937,6.202908))
   pts.append((bird,t+dt.timedelta(minutes=60),53.468937,6.206 if d%2 else 6.203))
   for lag in (0,3,6):
    m=t+dt.timedelta(minutes=30,hours=lag)
    astro[a.phase.nearest_tide_key(m)]=(-1. if d%2 else 1.) if lag==0 else 0.
  groups,qa=a.accumulate_step_strata(pts,astro,-.5,.5)
  pairs,support=a.paired_strata(groups,"OFFSET_0H_ALL")
  self.assertEqual(support["possible_paired_strata_before_bird_gate"],1)
  self.assertEqual(support["accepted_whole_birds"],0)
  _,phase3=a.paired_strata(groups,"OFFSET_PLUS_3H_ALL")
  self.assertEqual(phase3["possible_paired_strata_before_bird_gate"],0)
 def test_two_means_not_pool_bird_days(self):
  dataset={}
  for i in range(20):
   count=80 if i==0 else 10
   dataset[f"private-{i}"]=[{"log_speed_difference":1. if i==0 else -.1,
                           "elapsed_minutes_difference":10. if i==0 else -1.,
                           "year":2010,"n_high":2,"n_low":2}
                          for _ in range(count)]
  support={"accepted_whole_birds":20,"accepted_paired_strata":270,
           "possible_paired_strata_before_bird_gate":270,
           "original_steps_low_in_accepted_strata":540,
           "original_steps_high_in_accepted_strata":540}
  result=a.comparison(dataset,support)
  self.assertEqual(result["status"],"EXPLORATORY_POSTOUTCOME_DURATION_OR_PHASE_DIAGNOSTIC")
  self.assertAlmostEqual(result["response_high_minus_low_log1p_speed"]["equal_bird_mean"],(1.-1.9)/20.)
  self.assertAlmostEqual(result["elapsed_minutes_high_minus_low"]["equal_bird_mean"],(10.-19.)/20.)
  self.assertEqual(result,a.comparison(dataset,support))
  self.assertNotIn("private-",str(result))
 def test_support_stop_without_effect(self):
  output=a.comparison({},{"accepted_whole_birds":0,"accepted_paired_strata":0})
  self.assertEqual(output["status"],"NOT_ADMITTED_POSTOUTCOME_DIAGNOSTIC_SUPPORT")
  self.assertNotIn("mean_high_minus_low_log_speed",str(output))
 def test_silent_modified_previous_D_receipt_not_permitted(self):
  self.assertFalse(a._equal({"a":0.001},{"a":0.002}))
  self.assertTrue(a._equal({"a":[.25,2]},{"a":[.25,2]}))
 def test_all_seven_years_not_cherry_picked(self):
  data={"private":[{"year":2009,"log_speed_difference":-.1,"n_low":2,"n_high":2}]}
  years=a.yearly_descriptive(data)
  self.assertEqual(len(years),7)
  self.assertIsNone(years["2008"]["equal_bird_mean_high_minus_low_log_speed"])
  self.assertEqual(years["2009"]["birds_high_minus_low_negative"],1)
if __name__=="__main__":unittest.main()
