import unittest
from datetime import datetime,timedelta,timezone
from unittest.mock import patch

from validation_v221.original_real_birdGPS_ACC_to_BAW20min_WCS_source_clock_gate import (
    YEAR_COHORT,FOUR_MONTHS,BAW_NATIVE_GRID_INTERVAL_SEC,
    FROZEN_NATIVE_SPACE_LAT,FROZEN_NATIVE_SPACE_LONG,FROZEN_NIL,
    chronological_WCS20min_UTC_join_clock,
    native_space_from_WCS_description,native_WCS_potential_GPS_geography,
    source_counter_add,source_counter_final,make_source_counter,
    authentic_year_source_cohort
)

class OriginalBirdGPSQuarterHourToPhysicalSource20minClock(unittest.TestCase):
    def test_frozen_original_cohorts_and_2025_hindcast_clock(self):
        self.assertEqual(YEAR_COHORT,{
             2018:{"raw_common":193088,"prior15":157863},
             2019:{"raw_common":155387,"prior15":125241}})
        self.assertEqual(FOUR_MONTHS,(6,7,8,9))
        self.assertEqual(BAW_NATIVE_GRID_INTERVAL_SEC,1200)

    def test_native_20min_prior_vs_nearest_tie_and_future_value_leak(self):
        start=datetime(2018,6,1,0,0,0,tzinfo=timezone.utc)
        x=chronological_WCS20min_UTC_join_clock(start,2018)
        self.assertEqual(x["past_lag_sec"],0)
        self.assertEqual(x["nearest_abs_offset_sec"],0)
        self.assertFalse(x["nearest_requires_future_model_clock"])
        self.assertEqual(x["nearest_bin"],"nearest_le_60sec")
        nine=chronological_WCS20min_UTC_join_clock(start+timedelta(minutes=9),2018)
        self.assertEqual(nine["past_lag_sec"],540)
        self.assertFalse(nine["nearest_requires_future_model_clock"])
        ten=chronological_WCS20min_UTC_join_clock(start+timedelta(minutes=10),2018)
        self.assertEqual(ten["nearest_abs_offset_sec"],600)
        self.assertFalse(ten["nearest_requires_future_model_clock"])
        eleven=chronological_WCS20min_UTC_join_clock(start+timedelta(minutes=11),2018)
        self.assertEqual(eleven["past_lag_sec"],660)
        self.assertEqual(eleven["nearest_abs_offset_sec"],540)
        self.assertTrue(eleven["nearest_requires_future_model_clock"])
        self.assertEqual(eleven["selected_nearest_model_timestamp"],
            start+timedelta(minutes=20))
        with self.assertRaisesRegex(ValueError,"NOT_UTC_AWARE"):
            chronological_WCS20min_UTC_join_clock(start.replace(tzinfo=None),2018)
        with self.assertRaisesRegex(ValueError,"YEAR_DIFFERENT"):
            chronological_WCS20min_UTC_join_clock(start,2019)

    def test_original_BAW_WCS_source_envelope_cannot_be_inferred_from_year_label(self):
        source={
          "source_native_envelopes":[{"native_axisLabels":"Lat Long time",
             "source_lowerCorner":"52.863260107482425 4.176920490043966",
             "source_upperCorner":"53.94115222955482 7.3396245354662515"}],
          "source_time_positions_if_any":[{"source_time":"2018-01-01T00:00:00.000Z"},
             {"source_time":"2019-01-01T00:00:00.000Z"}],
          "source_nil_values":[{"native_literal":FROZEN_NIL}],
          "source_UOM_tags":[{"native_uom_code":"m"}]
        }
        lo,hi=native_space_from_WCS_description(source,2018)
        self.assertEqual(lo,(FROZEN_NATIVE_SPACE_LAT[0],FROZEN_NATIVE_SPACE_LONG[0]))
        self.assertEqual(hi,(FROZEN_NATIVE_SPACE_LAT[1],FROZEN_NATIVE_SPACE_LONG[1]))
        self.assertTrue(native_WCS_potential_GPS_geography(
            53.3,5.09,lo,hi))
        self.assertFalse(native_WCS_potential_GPS_geography(
            57,5.09,lo,hi))
        source["source_nil_values"]=[{"native_literal":"unexpected"}]
        with self.assertRaisesRegex(ValueError,"NIL"):
            native_space_from_WCS_description(source,2018)

    def test_all_original_bird_source_events_counted_without_Y_response_filtering(self):
        dt=datetime(2018,6,1,0,0,tzinfo=timezone.utc)
        common=[
         ({"source_utc_event":dt,"source_month":6,"source_lat":53.3,
           "source_lon":5.09,"private_bird":"private1","original_acc_forage_events":0},
          "night",None,None),
         ({"source_utc_event":dt+timedelta(minutes=11),"source_month":6,
           "source_lat":52.1,"source_lon":5.09,"private_bird":"private2",
           "original_acc_forage_events":100},"day",None,None),
         ({"source_utc_event":dt+timedelta(minutes=20),"source_month":6,
           "source_lat":53.4,"source_lon":5.5,"private_bird":"private1",
           "original_acc_forage_events":0},"day",None,None)
        ]
        mod="validation_v221.original_real_birdGPS_ACC_to_BAW20min_WCS_source_clock_gate.YEAR_COHORT"
        with patch.dict(mod,{2018:{"raw_common":3,"prior15":3}}):
            r=authentic_year_source_cohort(common,[0,1,2],2018,
                 (FROZEN_NATIVE_SPACE_LAT[0],FROZEN_NATIVE_SPACE_LONG[0]),
                 (FROZEN_NATIVE_SPACE_LAT[1],FROZEN_NATIVE_SPACE_LONG[1]))
        self.assertEqual(r["n_original_tagged_GPS_ACC_bins"],3)
        self.assertEqual(r["n_inside_published_BAW_WCS2_NL_geographical_envelope"],2)
        self.assertEqual(r["source_distinct_tagged_birds_count_only"],2)
        self.assertEqual(r["n_nearest_model20min_clock_requires_future_value"],1)
        self.assertEqual(r["n_exact_native_20min_clock_events"],2)
        self.assertEqual(r["by_original_solar_day_night"]["day"]["n_original_tagged_GPS_ACC_bins"],2)
        self.assertTrue(r["original_source_within_GPS_20min_join_does_NOT_check_Nil"])

    def test_nonfinite_GPS_source_is_not_fabricated_as_model_geographical_coverage(self):
        with self.assertRaises(ValueError):
            native_WCS_potential_GPS_geography(float("nan"),5.0,
                (52,4),(54,8))

if __name__=="__main__":
    unittest.main()
