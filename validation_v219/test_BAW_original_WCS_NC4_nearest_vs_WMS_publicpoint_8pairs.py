import tempfile
import unittest
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from validation_v219.BAW_original_WCS_NC4_nearest_vs_WMS_publicpoint_8pairs import (
    FROZEN_SOURCE_RD,FROZEN_HOURS,FROZEN_YEARS,
    FROZEN_NUMERIC_APPROX_TOLERANCE_M,
    fixed_public_wgs84,frozen_year_UTC,
    exact_bounded_WCS_query,fixed_native_WCS_url_is_approved,
    nearest_original_WCS_grid_point,compare_WCS_nearest_vs_WMS,
    BAW_WCS_NATIVE_NIL
)

VALID="PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED"
SENTINEL="EXTREME_NODATA_SENTINEL_CANDIDATE"

def small_native_NC4(site,nearest=float(BAW_WCS_NATIVE_NIL),unit="m",missing=False):
    lon_ref,lat_ref=fixed_public_wgs84(site)
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"generated.nc"
        with Dataset(str(path),mode="w",format="NETCDF4") as ds:
            ds.createDimension("time",1)
            ds.createDimension("lat",7)
            ds.createDimension("lon",7)
            time=ds.createVariable("time","f8",("time",))
            time.units="seconds since 1970-01-01 00:00:00 UTC"
            time[:]=[1527854400]
            lat=ds.createVariable("lat","f8",("lat",))
            lon=ds.createVariable("lon","f8",("lon",))
            lat[:]=lat_ref+np.linspace(-.009,.009,7)
            lon[:]=lon_ref+np.linspace(-.009,.009,7)
            if missing:
                var=ds.createVariable("sea_surface_height_2d","f4",("time","lat","lon"))
            else:
                var=ds.createVariable("sea_surface_height_2d","f4",("time","lat","lon"),
                       fill_value=np.float32(BAW_WCS_NATIVE_NIL))
            var.units=unit
            data=np.full((1,7,7),np.float32(0.1),dtype=np.float32)
            data[0,3,3]=np.float32(nearest)
            var[:]=data
        return path.read_bytes()

class FrozenOriginalHydroTwoInterfaceSourceContract(unittest.TestCase):
    def test_eight_cases_frozen_2018_2019_june1_00_and_12(self):
        self.assertEqual(set(FROZEN_SOURCE_RD),{"VlielandHaven","Wierumergronden"})
        self.assertEqual(FROZEN_HOURS,(0,12))
        self.assertEqual(len(FROZEN_SOURCE_RD)*len(FROZEN_YEARS)*len(FROZEN_HOURS),8)
        self.assertEqual(FROZEN_NUMERIC_APPROX_TOLERANCE_M,.05)
        for yr in FROZEN_YEARS:
            for site in FROZEN_SOURCE_RD:
                for hour in FROZEN_HOURS:
                    url=exact_bounded_WCS_query(yr,site,hour)
                    self.assertTrue(fixed_native_WCS_url_is_approved(url,yr,site,hour))
                    self.assertIn("GetCoverage",url)
                    self.assertIn("x-netcdf4",url)
                    self.assertIn("time%28%22",url)
                    self.assertEqual(frozen_year_UTC(yr,hour),f"{yr}-06-01T{hour:02d}:00:00.000Z")
        with self.assertRaises(ValueError):
            exact_bounded_WCS_query("2020","VlielandHaven",12)
        with self.assertRaises(ValueError):
            exact_bounded_WCS_query("2019","otherSite",0)
        with self.assertRaises(ValueError):
            exact_bounded_WCS_query("2019","VlielandHaven",6)

    def test_native_nearest_fill_matches_exact_WCS_declared_FillValue(self):
        data=nearest_original_WCS_grid_point(
           small_native_NC4("VlielandHaven"),"VlielandHaven")
        self.assertEqual(data["source_nearest_gridpoint_class"],"SOURCE_NC4_OFFICIAL_FILLVALUE")
        self.assertIsNone(data["source_nearest_gridpoint_model_value_m_if_numeric"])
        self.assertEqual(data["source_nearest_native_gridrow_col"],[3,3])
        self.assertEqual(data["source_native_nc4_official_fillvalue_cell_n"],1)
        self.assertEqual(data["source_native_nc4_total_cells"],49)
        result=compare_WCS_nearest_vs_WMS(
            data,None,{"native_GeoJSON_Wasserstand_classification":SENTINEL})
        self.assertTrue(result["categorical_agreement"])
        self.assertEqual(result["status"],"BOTH_NATIVE_WCS_WMS_FILL_NO_DATA")

    def test_source_numeric_matches_or_disagrees_without_favoring_one(self):
        v=nearest_original_WCS_grid_point(small_native_NC4(
            "Wierumergronden",.54),"Wierumergronden")
        self.assertEqual(v["source_nearest_gridpoint_class"],"SOURCE_NC4_NUMERIC_MODEL_HEIGHT_M")
        near=compare_WCS_nearest_vs_WMS(v,.56,{
            "native_GeoJSON_Wasserstand_classification":VALID})
        self.assertTrue(near["categorical_agreement"])
        self.assertTrue(near["source_numeric_abs_delta_lte_0p05m"])
        bad=compare_WCS_nearest_vs_WMS(v,None,{
            "native_GeoJSON_Wasserstand_classification":SENTINEL})
        self.assertFalse(bad["categorical_agreement"])
        self.assertEqual(bad["status"],"SOURCE_INTERFACE_WMS_VS_WCS_NEAREST_CLASS_DIFFERENCE")

    def test_bad_native_unit_or_missing_OGC_FillValue_stops_before_comparison(self):
        with self.assertRaisesRegex(ValueError,"UNIT_CHANGED"):
            nearest_original_WCS_grid_point(
                small_native_NC4("VlielandHaven",unit="cm"),"VlielandHaven")
        with self.assertRaisesRegex(ValueError,"MISSING_FILLVALUE"):
            nearest_original_WCS_grid_point(
                small_native_NC4("VlielandHaven",missing=True),"VlielandHaven")
        with self.assertRaisesRegex(ValueError,"NOT_BOUNDED_HDF5_BINARY"):
            nearest_original_WCS_grid_point(b"<ServiceExceptionReport/>","VlielandHaven")

if __name__=="__main__":
    unittest.main()
