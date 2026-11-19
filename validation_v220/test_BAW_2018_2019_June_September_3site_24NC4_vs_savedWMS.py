import tempfile
import unittest
import urllib.parse
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from validation_v220.BAW_2018_2019_June_September_3site_24NC4_vs_savedWMS import (
    FROZEN_PUBLIC_SITES,FROZEN_YEARS,FROZEN_MONTHS,FROZEN_UTC_HOURS,
    strict_public_coordinate,fixed_timestamp,fixed_WCS_GetCoverage_URL,
    source_bounded_24_query_admitted,archived_model_class_for_case,
    native_WCS_nearest_grid_class,source_same_time_class_agreement,
    BAW_WCS_NATIVE_NIL,PLAUSIBLE,SENTINEL
)

def native_source_test_NC4(site,value=None):
    if value is None:value=BAW_WCS_NATIVE_NIL
    lon0,lat0=strict_public_coordinate(site)
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"from_source.nc"
        with Dataset(str(path),mode="w",format="NETCDF4") as ds:
            ds.createDimension("time",1)
            ds.createDimension("lat",7)
            ds.createDimension("lon",7)
            time=ds.createVariable("time","f8",("time",))
            time[:]=[1527811200]
            lat=ds.createVariable("lat","f8",("lat",))
            lon=ds.createVariable("lon","f8",("lon",))
            lat[:]=lat0+np.linspace(-.009,.009,7)
            lon[:]=lon0+np.linspace(-.009,.009,7)
            h=ds.createVariable("sea_surface_height_2d","f4",("time","lat","lon"),
                fill_value=np.float32(BAW_WCS_NATIVE_NIL))
            h.units="m"
            a=np.full((1,7,7),.2,dtype="float32")
            a[0,3,3]=np.float32(value)
            h[:]=a
        return path.read_bytes()

class OriginalBAWThreeSiteTwoMonthNilReplication(unittest.TestCase):
    def test_exact_twentyfour_cases_predeclared(self):
        self.assertEqual(len(FROZEN_PUBLIC_SITES),3)
        self.assertEqual(FROZEN_YEARS,("2018","2019"))
        self.assertEqual(FROZEN_MONTHS,{"June":"06","September":"09"})
        self.assertEqual(FROZEN_UTC_HOURS,(0,12))
        self.assertEqual(len(FROZEN_PUBLIC_SITES)*len(FROZEN_YEARS)*
                         len(FROZEN_MONTHS)*len(FROZEN_UTC_HOURS),24)
        for year in FROZEN_YEARS:
            for month in FROZEN_MONTHS:
                for site in FROZEN_PUBLIC_SITES:
                    for hour in FROZEN_UTC_HOURS:
                        u=fixed_WCS_GetCoverage_URL(year,month,site,hour)
                        self.assertTrue(source_bounded_24_query_admitted(
                             u,year,month,site,hour))
                        q=urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query)
                        self.assertIn(("format","application/x-netcdf4"),q)
                        self.assertEqual(len([v for k,v in q if k=="subset"]),3)
                        self.assertIn(fixed_timestamp(year,month,hour),u.replace("%3A",":").replace("%22",'"'))
        with self.assertRaises(ValueError):
            fixed_WCS_GetCoverage_URL("2019","June","nonpublished",0)
        with self.assertRaises(ValueError):
            fixed_WCS_GetCoverage_URL("2019","February","VlielandHaven",0)
        with self.assertRaises(ValueError):
            fixed_WCS_GetCoverage_URL("2019","September","WestTerschelling",6)

    def test_native_nearest_coordinates_for_all_three_source_sites(self):
        for site in FROZEN_PUBLIC_SITES:
            original=native_WCS_nearest_grid_class(native_source_test_NC4(site),site)
            self.assertEqual(original["nearest_native_WCS_class"],"NC4_OFFICIAL_NIL")
            self.assertEqual(original["native_grid_official_Nil_cells"],1)
            self.assertEqual(original["native_grid_total_cells"],49)
            self.assertTrue(source_same_time_class_agreement("NC4_OFFICIAL_NIL",SENTINEL))
            self.assertFalse(source_same_time_class_agreement("NC4_OFFICIAL_NIL",PLAUSIBLE))
            v=native_WCS_nearest_grid_class(native_source_test_NC4(site,.6),site)
            self.assertEqual(v["nearest_native_WCS_class"],"NC4_NUMERIC_SOURCE")
            self.assertTrue(source_same_time_class_agreement("NC4_NUMERIC_SOURCE",PLAUSIBLE))
            self.assertFalse(source_same_time_class_agreement("NC4_NUMERIC_SOURCE",SENTINEL))

    def test_original_v209_model_class_selected_by_exact_UTC_not_provider_order(self):
        case={"all_12_official_model_validity_vs_measured_tide_level_cohorts":{
             "September_2019_WestTerschelling":{
              "original_SIX_WMS_source_replies_SHA_only":[
                 {"original_fixed_UTC":"2019-09-01T00:00:00+00:00",
                  "source_model_value_class":SENTINEL,
                  "source_original_WMS_reply_SHA256":"f"*64},
                 {"original_fixed_UTC":"2019-09-01T12:00:00+00:00",
                  "source_model_value_class":PLAUSIBLE,
                  "source_original_WMS_reply_SHA256":"e"*64},
              ]}
             }}
        a=archived_model_class_for_case(case,"September","2019","WestTerschelling",0)
        b=archived_model_class_for_case(case,"September","2019","WestTerschelling",12)
        self.assertEqual(a["archived_original_WMS_class"],SENTINEL)
        self.assertEqual(b["archived_original_WMS_class"],PLAUSIBLE)
        self.assertTrue(a["native_original_WMS_raw_time_series_NOT_requeried"])
        case["all_12_official_model_validity_vs_measured_tide_level_cohorts"]["September_2019_WestTerschelling"][
          "original_SIX_WMS_source_replies_SHA_only"].append(
           {"original_fixed_UTC":"2019-09-01T12:00:00+00:00",
            "source_model_value_class":SENTINEL})
        with self.assertRaisesRegex(ValueError,"TIME_MATCH_NOT_UNIQUE"):
            archived_model_class_for_case(case,"September","2019","WestTerschelling",12)

    def test_never_explain_model_nil_as_observed_dryflat(self):
        self.assertFalse(source_same_time_class_agreement("NC4_OTHER_VALUE_UNRESOLVED",SENTINEL))
        self.assertFalse(source_same_time_class_agreement("NC4_OTHER_VALUE_UNRESOLVED",PLAUSIBLE))
        with self.assertRaises(ValueError):
            native_WCS_nearest_grid_class(b"<xml>not NetCDF4</xml>","VlielandHaven")
        with self.assertRaises(ValueError):
            strict_public_coordinate("WaddenRandom")

if __name__=="__main__":
    unittest.main()
