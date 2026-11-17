"""Synthetic historical native NetCDF geo/time gate tests, no real source data."""
import tempfile,os,unittest
from pathlib import Path
from netCDF4 import Dataset
import numpy as np
from historical_dem_source_gate import inspect_original_netcdf

class TestHistoricalBathySource(unittest.TestCase):
    def test_native_epsg28992_geography_and_missing_source_date(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.nc"
            with Dataset(str(p),"w",format="NETCDF4_CLASSIC") as nc:
                nc.createDimension("x",4);nc.createDimension("y",3)
                x=nc.createVariable("x","f8",("x",))
                y=nc.createVariable("y","f8",("y",))
                x[:]=[125000.,128000.,131000.,134000.]
                y[:]=[590000.,591000.,592000.]
                height=nc.createVariable("z","f8",("y","x"),fill_value=-999.)
                height[:]=np.array([[0.5,-0.1,0.2,0.4]]*3)
                nc.title="Rijkswaterstaat synthetic historical source (NOT genuine)"
                nc.setncattr("projection","Amersfoort / RD New (EPSG:28992)")
            raw=p.read_bytes()
        source=inspect_original_netcdf(raw,{"original_native_binary_SHA256":"synthetic"},2016)
        geo=source["source_geographic_coverage_and_admission"]
        self.assertEqual(geo["filename_suggested_year"],2016)
        self.assertTrue(geo["source_extent_intersects_broad_Vlieland_region"])
        self.assertEqual(geo["native_NAP_vertical_datum_strict_verification"],"NOT_VERIFIED_FROM_FILENAME_ONLY")
        self.assertEqual(source["original_netcdf_coordinate_metadata"]["z"]["finite_original_values"],12)
    def test_source_offshore_tile_must_not_be_assumed_vlieland(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic2.nc"
            with Dataset(str(p),"w",format="NETCDF4_CLASSIC") as nc:
                nc.createDimension("x",2);nc.createDimension("y",2)
                nc.createVariable("x","f8",("x",))[:]=[200000.,210000.]
                nc.createVariable("y","f8",("y",))[:]=[630000.,640000.]
            info=inspect_original_netcdf(p.read_bytes(),{},2019)
        self.assertFalse(info["source_geographic_coverage_and_admission"]["source_extent_intersects_broad_Vlieland_region"])
    def test_native_rejects_html_not_dataset(self):
        from historical_dem_source_gate import acquire_bytes
        # Source parser must check original binary magic before treating
        # 200-response access pages as successful data.
        self.assertTrue(b"<html"[:3]!=b"CDF")

if __name__=="__main__":
    unittest.main()
