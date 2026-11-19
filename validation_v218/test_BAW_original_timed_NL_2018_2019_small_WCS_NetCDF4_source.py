import tempfile
import unittest
import urllib.parse
from pathlib import Path
import numpy as np
from netCDF4 import Dataset
from validation_v218.BAW_original_timed_NL_2018_2019_small_WCS_NetCDF4_source import (
 FROZEN_SOURCE_RD,FROZEN_YEARS,FROZEN_UTC,FROZEN_FORMAT,FROZEN_COVERAGE_IDS,
 SPATIAL_HALF_WIDTH_DEG,only_four_frozen_WCS_getcoverage_urls,
 source_bounded_authorized_query,inspect_WCS_generated_NC4,BAW_WCS_NATIVE_NIL
)

class GenuineSmallBAWWCSNC4SourceContract(unittest.TestCase):
    def test_fixed_two_sites_years_and_Lat_Long_time_subsets(self):
        self.assertEqual(FROZEN_SOURCE_RD,{
            "VlielandHaven":(135280,590000),"Wierumergronden":(192882,614562)})
        self.assertEqual(FROZEN_YEARS,("2018","2019"))
        self.assertEqual(FROZEN_FORMAT,"application/x-netcdf4")
        self.assertEqual(SPATIAL_HALF_WIDTH_DEG,0.015)
        for year in FROZEN_YEARS:
            for site in FROZEN_SOURCE_RD:
                url=only_four_frozen_WCS_getcoverage_urls(year,site)
                self.assertTrue(source_bounded_authorized_query(url,year,site))
                params=urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query)
                self.assertEqual(dict(params)["coverageId"],FROZEN_COVERAGE_IDS[year])
                self.assertEqual(dict(params)["format"],"application/x-netcdf4")
                subsets=[v for k,v in params if k=="subset"]
                self.assertEqual(len(subsets),3)
                self.assertTrue(subsets[0].startswith("Lat("))
                self.assertTrue(subsets[1].startswith("Long("))
                self.assertEqual(subsets[2],'time("'+FROZEN_UTC[year]+'")')
        with self.assertRaises(ValueError):
            only_four_frozen_WCS_getcoverage_urls("2020","VlielandHaven")
        with self.assertRaises(ValueError):
            only_four_frozen_WCS_getcoverage_urls("2018","unknown")

    def test_authentic_generated_NetCDF4_attributes_are_not_original_annual_file(self):
        with tempfile.TemporaryDirectory() as t:
            filename=str(Path(t)/"synthetic.nc")
            with Dataset(filename,"w",format="NETCDF4") as ds:
                ds.createDimension("Lat",3)
                ds.createDimension("Long",4)
                var=ds.createVariable("Wasserstand","f4",("Lat","Long"),
                    fill_value=np.float32(BAW_WCS_NATIVE_NIL))
                var.units="m"
                values=np.full((3,4),-0.94,dtype=np.float32)
                values[0,0]=np.float32(BAW_WCS_NATIVE_NIL)
                var[:]=values
            binary=Path(filename).read_bytes()
            result=inspect_WCS_generated_NC4(binary)
            self.assertEqual(result["native_surface_height_variable"],"Wasserstand")
            self.assertEqual(result["native_surface_height_original_WCS_subset_attributes"]["units"],"m")
            self.assertTrue(result["original_WCS_nil_m_matches_NetCDF4_output__FillValue_if_present"])
            self.assertEqual(result["n_subset_total_source_pixels"],12)
            self.assertEqual(result["n_finite_and_plausible_model_height_numeric"],11)
            self.assertEqual(result["n_finite_extreme_sentinel_candidates"],1)
            self.assertTrue(result["ORIGINAL_FULL_YEAR_BAW_DOWNLOAD_NETCDF_ATTRIBUTES_NOT_DIRECTLY_READ"])

    def test_non_NetCDF_and_wrong_variable_must_stop(self):
        with self.assertRaisesRegex(ValueError,"NOT_SMALL_NATIVE_NETCDF4"):
            inspect_WCS_generated_NC4(b"<ServiceException>No native NetCDF</ServiceException>")
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"wrong.nc"
            with Dataset(str(path),"w",format="NETCDF4") as ds:
                ds.createDimension("time",1)
                ds.createVariable("temperature","f4",("time",))[:]=[20]
            with self.assertRaisesRegex(ValueError,"NO_UNIQUE_NATIVE"):
                inspect_WCS_generated_NC4(path.read_bytes())

    def test_source_numeric_extreme_is_not_assumed_field_wetdry(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"masks.nc"
            with Dataset(str(path),"w",format="NETCDF4") as ds:
                ds.createDimension("Lat",2)
                ds.createDimension("Long",2)
                var=ds.createVariable("sea_surface_height_2d","f4",("Lat","Long"))
                var[:]=np.array([[0.2,-0.4],[1e31,0.1]],dtype=np.float32)
            data=inspect_WCS_generated_NC4(path.read_bytes())
            self.assertFalse(data["original_WCS_nil_m_matches_NetCDF4_output__FillValue_if_present"])
            self.assertEqual(data["n_finite_extreme_sentinel_candidates"],1)
            self.assertEqual(data["n_finite_and_plausible_model_height_numeric"],3)

if __name__=="__main__":
    unittest.main()
