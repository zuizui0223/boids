"""Original ID+UTC structural eligibility tests, never GPS positions."""
import datetime as dt
import unittest
import source_support as m

class TimeOnlySupport(unittest.TestCase):
    def test_sufficient_birds_all_days(self):
        start=dt.datetime(2020,1,1)
        birds={}
        for b in range(12):
            birds[str(b)]={start+dt.timedelta(days=d,hours=h) for d in range(12)
                          for h in (0,2,4,8,12,18)}
        q=m.upper_bound_from_id_stamps(birds)
        self.assertEqual(q["original_source_distinct_birds"],12)
        self.assertEqual(q["original_complete_UTC_days_upper_bound"],144)
        self.assertEqual(q["original_consecutive_complete_day_events_upper_bound"],132)
        self.assertEqual(q["birds_potentially_eligible_before_GPS_quality"],12)
        self.assertGreater(q["individual_future_days_potentially_eligible_before_GPS_quality"],80)
    def test_fewer_than_six_fixes_does_not_claim_support(self):
        start=dt.datetime(2020,1,1)
        x={"x": {start+dt.timedelta(days=d,hours=h) for d in range(10)
                  for h in (0,4,8,12,16)}}
        q=m.upper_bound_from_id_stamps(x)
        self.assertEqual(q["original_complete_UTC_days_upper_bound"],0)
        self.assertEqual(q["individual_future_days_potentially_eligible_before_GPS_quality"],0)
    def test_missing_previous_calendar_day_excluded(self):
        start=dt.datetime(2020,1,1)
        x={"x":{start+dt.timedelta(days=d,hours=h) for d in (0,1,3,4,5,6,7)
                for h in (0,2,4,8,12,18)}}
        q=m.upper_bound_from_id_stamps(x)
        self.assertEqual(q["original_consecutive_complete_day_events_upper_bound"],5)
    def test_low_number_individuals_cannot_be_eligible(self):
        start=dt.datetime(2020,1,1)
        x={str(b):{start+dt.timedelta(days=d,hours=h) for d in range(15)
                   for h in (0,2,4,8,12,18)} for b in range(4)}
        q=m.upper_bound_from_id_stamps(x)
        self.assertEqual(q["birds_potentially_eligible_before_GPS_quality"],0)

if __name__=="__main__":unittest.main()
