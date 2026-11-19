import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import numpy as np
from netCDF4 import Dataset,date2num

from validation_v222.true_bird_GPS_to_BAW_native_NC4_Nil_16_past_time_source import (
    YEAR_SOURCE_N,FROZEN_MONTHS,FROZEN_HOURS,FROZEN_DAY,FROZEN_HALF_DEGREES_LAT,
    FROZEN_HALF_DEGREES_LON,FROZEN_NATIVE_NEAREST_MAX_DELTA_DEG,
    FROZEN_WINDOW_MINUTES,BAW_WCS_NATIVE_NIL,
    public_WCS_centre,fixed_model_source_knot,fixed_source_WCS_GetCoverage,
    source_query_in_fixed_16,eligible_bird_source_bin,
    freeze_original_bird_source_pilot,interpret_native_WCS_NC4_at_bird_GPS
)

def synthetic_native_NC4(year,month,hour,maskedcentre=False,unit="m",time_offset=0):
    lat0,lon0=public_WCS_centre()
    with tempfile.TemporaryDirectory() as t:
        path=Path(t)/"synthetic_bounded_source.nc"
        with Dataset(str(path),"w",format="NETCDF4") as ds:
            ds.createDimension("time",1)
            ds.createDimension("lat",9)
            ds.createDimension("lon",9)
            tim=ds.createVariable("time","f8",("time",))
            tim.units="seconds since 1970-01-01 00:00:00 UTC"
            tim[:]=[date2num(fixed_model_source_knot(year,month,hour)+timedelta(seconds=time_offset),
                            tim.units)]
            y=ds.createVariable("lat","f8",("lat",))
            x=ds.createVariable("lon","f8",("lon",))
            y[:]=lat0+np.linspace(-0.02,0.02,9)
            x[:]=lon0+np.linspace(-0.02,0.02,9)
            height=ds.createVariable("sea_surface_height_2d","f4",("time","lat","lon"),
                                      fill_value=np.float32(BAW_WCS_NATIVE_NIL))
            height.units=unit
            a=np.full((1,9,9),.37,dtype=np.float32)
            if maskedcentre:a[0,4,4]=np.float32(BAW_WCS_NATIVE_NIL)
            height[:]=a
        return path.read_bytes()

class FrozenBirdPastWCSNC4NoOutcomePilot(unittest.TestCase):
    def test_original_year_month_day_UTC_source_scope_fixed(self):
        self.assertEqual(YEAR_SOURCE_N,{
            2018:{"original_common":193088,"previous15":157863},
            2019:{"original_common":155387,"previous15":125241}})
        self.assertEqual(FROZEN_MONTHS,(6,7,8,9))
        self.assertEqual(FROZEN_HOURS,(0,12))
        self.assertEqual(FROZEN_DAY,15)
        self.assertEqual(FROZEN_HALF_DEGREES_LAT,.15)
        self.assertEqual(FROZEN_HALF_DEGREES_LON,.25)
        self.assertEqual(FROZEN_NATIVE_NEAREST_MAX_DELTA_DEG,.003)
        self.assertEqual(FROZEN_WINDOW_MINUTES,20)
        self.assertEqual(2*4*2,16)
        for year in (2018,2019):
            for mon in FROZEN_MONTHS:
                for hour in FROZEN_HOURS:
                    url=fixed_source_WCS_GetCoverage(year,mon,hour)
                    self.assertTrue(source_query_in_fixed_16(url,year,mon,hour))
                    self.assertIn("netcdf4",url)
                    self.assertIn(f"{year}-{mon:02}-15",url)
        with self.assertRaises(ValueError):
            fixed_source_WCS_GetCoverage(2019,5,12)
        with self.assertRaises(ValueError):
            fixed_source_WCS_GetCoverage(2020,6,12)

    def test_original_event_selection_on_UTC_only_not_current_ACC_Y(self):
        knot=fixed_model_source_knot(2018,6,0)
        src={"source_utc_event":knot+timedelta(minutes=19,seconds=59),
             "source_month":6,"original_acc_forage_events":0}
        self.assertTrue(eligible_bird_source_bin(src,2018,6,0))
        src["original_acc_forage_events"]=100
        self.assertTrue(eligible_bird_source_bin(src,2018,6,0))
        src["source_utc_event"]=knot+timedelta(minutes=20)
        self.assertFalse(eligible_bird_source_bin(src,2018,6,0))
        src["source_utc_event"]=knot-timedelta(seconds=1)
        self.assertFalse(eligible_bird_source_bin(src,2018,6,0))

    def test_animal_pilot_membership_is_frozen_by_date_never_label(self):
        knot=fixed_model_source_knot(2018,6,12)
        common=[]
        for minute,Y in [(4,0),(18,100),(21,0)]:
            common.append(({"source_utc_event":knot+timedelta(minutes=minute),
                "source_month":6,"source_lat":53.33,"source_lon":5.08,
                "private_bird":"tag%d"%minute,
                "original_acc_forage_events":Y},
                "day",None,None))
        name="validation_v222.true_bird_GPS_to_BAW_native_NC4_Nil_16_past_time_source.YEAR_SOURCE_N"
        with patch.dict(name,{2018:{"original_common":3,"previous15":3}}):
            g=freeze_original_bird_source_pilot(2018,common,[0,1,2])
        self.assertEqual(len(g[(6,12)]),2)
        self.assertEqual(sum(len(v) for v in g.values()),2)
        self.assertEqual(len(g),8)

    def test_native_WCS_fill_at_true_GPS_and_nonselected_events_partition(self):
        lat0,lon0=public_WCS_centre()
        selected=[(lat0,lon0,"tagA"),(lat0+.01,lon0+.01,"tagB"),
                  (lat0+.151,lon0,"tagC")]
        raw=synthetic_native_NC4(2018,6,12,maskedcentre=True)
        result=interpret_native_WCS_NC4_at_bird_GPS(raw,6,12,2018,selected)
        cell=result["native_model_crop_counts"]
        gps=result["true_source_GPS_ACC_event_model_cell_status"]
        self.assertEqual(cell["original_native_model_Nil_cell_n"],1)
        self.assertEqual(gps["n_actual_original_GPS_ACC_prev15_events_in_fixed_time_window"],3)
        self.assertEqual(gps["n_bird_events_outside_fixed_native_ROI"],1)
        self.assertEqual(gps["n_actual_bird_events_nearest_model_grid_accepted"],2)
        self.assertEqual(gps["n_GPS_matched_native_model_Nil_events"],1)
        self.assertEqual(gps["n_GPS_matched_native_model_numeric_events"],1)
        self.assertEqual(gps["n_distinct_original_tagged_birds_in_time_window_only"],3)
        self.assertNotIn("source_lon",str(result))

    def test_wrong_model_time_and_units_stop_without_data_forgiveness(self):
        lat0,lon0=public_WCS_centre()
        with self.assertRaisesRegex(ValueError,"ACTUAL_TIME_KNOT"):
            interpret_native_WCS_NC4_at_bird_GPS(
                synthetic_native_NC4(2019,9,0,time_offset=1200),
                9,0,2019,[(lat0,lon0,"tag")])
        with self.assertRaisesRegex(ValueError,"MISSING_UNIT_OR_OFFICIAL_NIL"):
            interpret_native_WCS_NC4_at_bird_GPS(
                synthetic_native_NC4(2018,6,0,unit="cm"),
                6,0,2018,[(lat0,lon0,"tag")])

if __name__=="__main__":
    unittest.main()
