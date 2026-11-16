"""Source-free known-truth tests for the time-bin correction."""
import unittest
from datetime import datetime,timedelta,timezone
from native_quarterhour_lag_tide import floor15,corrected_previous_bin,MIN_HISTORY_PAIRS
from bird_tide_after_prev15 import source_actual_previous

def row(bird,h,m,s,week=23):
    utc=datetime(2018,6,4,h,m,s,tzinfo=timezone.utc)
    return ({"private_bird":bird,"source_utc_event":utc,"source_month":6},
            "day",None,week)

class TestNativeQuarterhour(unittest.TestCase):
    def test_earliest_event_not_native_grid_start(self):
        x=datetime(2018,6,4,10,16,31,tzinfo=timezone.utc)
        self.assertEqual(floor15(x),datetime(2018,6,4,10,15,tzinfo=timezone.utc))
    def test_source_earliest_events_separated_15m_nonexact_are_real_adjacent_bins(self):
        src=[row("b",10,1,22),row("b",10,16,31),row("b",10,50,4)]
        i,p,q=corrected_previous_bin(src)
        self.assertEqual(i.tolist(),[1])
        self.assertEqual(p.tolist(),[0])
        exact_i,exact_p,qa=source_actual_previous(src)
        self.assertEqual(exact_i.size,0)
    def test_bird_identity_and_iso_week_are_necessary(self):
        src=[row("bird_A",10,2,0,week=23),row("bird_B",10,17,1,week=23)]
        i,p,q=corrected_previous_bin(src)
        self.assertEqual(i.size,0)
        cross=[row("bird_A",10,2,0,week=23),row("bird_A",10,17,1,week=24)]
        i,p,q=corrected_previous_bin(cross)
        self.assertEqual(i.size,0)
        self.assertEqual(q["ORIGINAL_QUARTERHOUR_SOURCE_WEEK_BOUNDARY"],1)
    def test_same_bird_duplicate_native_quarterhour_must_STOP(self):
        src=[row("b",10,0,14),row("b",10,14,59)]
        with self.assertRaises(AssertionError):corrected_previous_bin(src)
    def test_nonUTC_timestamps_not_source_corrected(self):
        bad=datetime(2018,6,4,10,0)
        with self.assertRaises(ValueError):floor15(bad)
    def test_precommitted_source_gate_not_revised(self):
        self.assertEqual(MIN_HISTORY_PAIRS,25000)

if __name__=="__main__":unittest.main()
