"""Source-only invented bird ID & UTC original telemetry support fixtures."""
import datetime as dt
import unittest
import source_timestamps as m

BASE=dt.datetime(2010,1,1,10)
class SourceOnlyKnownTruth(unittest.TestCase):
 def test_single_bird_has_no_other_heading(self):
    times={ "private-a":[BASE+dt.timedelta(minutes=10*i) for i in range(20)]}
    q=m.co_observation_opportunities(times)
    a=q["registered_2010_2012_test_source_support"]
    self.assertEqual(a["test_years_potential_focal_with_one_other_past_heading"],0)
    self.assertEqual(q["status"],m.STATUS_STOP)
 def test_two_synchronous_birds_have_observed_other_past_heading(self):
    times={f"private-{k}":[BASE+dt.timedelta(minutes=10*i) for i in range(40)]
           for k in range(3)}
    q=m.co_observation_opportunities(times)
    a=q["registered_2010_2012_test_source_support"]
    self.assertEqual(a["test_years_potential_focal_four_fix_starts"],3*(40-3))
    self.assertEqual(a["test_years_potential_focal_with_one_other_past_heading"],3*(40-3))
    self.assertEqual(q["yearly_source_time_only_opportunities"]["2010"]
        ["focal_starts_with_two_or_more_distinct_prior_other_headings"],3*(40-3))
    self.assertNotIn("private-",str(q))
 def test_other_future_timestamp_not_available_at_focal_time(self):
    # Focal candidate t=09:50, other latest two-fix heading ends 09:51
    # (and its previous endpoint 09:41 is 9 min stale).
    a=BASE-dt.timedelta(minutes=10)
    t1=[a+dt.timedelta(minutes=10*i) for i in range(4)]
    t2=[a+dt.timedelta(minutes=1)+dt.timedelta(minutes=10*i) for i in range(2)]
    bybird={"private-A":t1,"private-B":t2}
    q=m.co_observation_opportunities(bybird)
    a=q["registered_2010_2012_test_source_support"]
    self.assertEqual(a["test_years_potential_focal_four_fix_starts"],1)
    self.assertEqual(a["test_years_potential_focal_with_one_other_past_heading"],0)
 def test_original_duplicates_all_rejected_not_first_wins(self):
    rows=[("private-a",BASE),("private-a",BASE),
          ("private-a",BASE+dt.timedelta(minutes=10)),
          ("private-b",BASE)]
    birds,a=m.discard_all_duplicate_source_bird_UTC_events(rows)
    self.assertEqual(a["original_duplicate_source_bird_UTC_keys"],1)
    self.assertEqual(a["original_duplicate_rows_all_discarded"],2)
    self.assertEqual(len(birds["private-a"]),1)
 def test_original_source_period_and_phase_past_only(self):
    self.assertEqual(m.original.RECORD,10053970)
    self.assertEqual(len(m.original.PINS),7)
    self.assertEqual(m.TARGET_START_YEARS,(2010,2011,2012))
    self.assertEqual(m.MAX_OTHER_HEADING_AGE_MIN,5)
    self.assertEqual(m.MIN_BIRDS_WITH_TIME_SUPPORTED_FOCAL_STARTS,20)
 def test_no_original_coordinates_in_source_only_code(self):
    import inspect
    s=inspect.getsource(m.source_timestamps_only)
    self.assertNotIn('row.get("location-lat")',s)
    self.assertNotIn('row.get("location-long")',s)
    self.assertNotIn('row.get("heading")',s)
    self.assertNotIn('read_original_valid_gps',s)
 def test_original_source_quality_flags_as_documented(self):
    self.assertTrue(m.original.flag_true("true"))
    self.assertFalse(m.original.flag_true("",blank_false=True))
if __name__=="__main__":unittest.main()
