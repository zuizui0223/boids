"""v72 synthetic original-shape monthly model footprint; not animal ecology."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from native_monthly_exposure_source import (
    EXPECTED_SHAPE,FIXED_SHA,native_readme_meaning,
    original_native_month,check_monthly_native_source)

def fake_month(*,late=False,geoshift=0):
    shape=EXPECTED_SHAPE
    ys=np.linspace(53.05,53.85,shape[0],dtype=np.float32)
    xs=np.linspace(5.35,6.65,shape[1],dtype=np.float32)
    lat=np.broadcast_to(ys[:,None],shape).copy()+geoshift
    lon=np.broadcast_to(xs[None,:],shape).copy()
    expo=np.broadcast_to(np.linspace(0,100,shape[1]),shape).copy()
    if late:expo+=2
    return lat,lon,expo

class OriginalMonthlyExposureSourceKnownTruth(unittest.TestCase):
    def test_readme_original_units_must_be_explicit_and_not_guessed(self):
        good=native_readme_meaning(b""
            b"README for 2010 NIOZ model monthly hydro\n"
            b"Time table\n"
            b"time_expo: percentage of time exposed to air (percent)\n")
        self.assertEqual(good["semantics_admission"],
                         "ORIGINAL_README_EXPLICIT_MODELED_EXPOSURE_PROPORTION")
        self.assertTrue(good["native_exposure_variable_literal_mentioned"])
        bad=native_readme_meaning(b"time_expo modelled exposure uncertainty\n")
        self.assertTrue(bad["semantics_admission"].startswith("NOT_ADMITTED"))
        unclear=native_readme_meaning(b"No mention of original exposure variable\n")
        self.assertTrue(unclear["semantics_admission"].startswith("NOT_ADMITTED"))
        self.assertEqual(len(FIXED_SHA),3)

    def test_2010_2011_native_grid_and_original_exposure_summary_admitted(self):
        a=fake_month()
        b=fake_month(late=True)
        qa=check_monthly_native_source(
            {"eco_av.201001.nc":a,"eco_av.201101.nc":b},
            native_readme_meaning(b"time_expo: percent proportion of exposure\n"))
        self.assertEqual(qa["modelled_monthly_exposure_source_admission"],
                         "SOURCE_ONLY_MODELED_MONTHLY_EXPOSURE_MAP_FOR_FUTURE_GPS_JOIN")
        self.assertEqual(qa["source_geographic_cells_with_latlon_in_degrees"],486*820)
        for s,datum in qa["source_site_neighborhoods"].items():
            self.assertLess(datum["nearest_original_native_model_cell_center_m"],2000.)
            self.assertGreater(datum["original_both_years_monthly_model_numeric_nonnegative_cells_5km"],50)
            self.assertAlmostEqual(datum["2011_minus_2010_model_pixel_value_UNITS_UNVERIFIED"]["median"],2)
        self.assertNotIn("53.46894",str(qa))

    def test_assume_no_semantics_no_admission_even_if_numeric_looks_like_fraction(self):
        a=fake_month()
        qa=check_monthly_native_source(
            {"eco_av.201001.nc":a,"eco_av.201101.nc":a},
            native_readme_meaning(b"temporal data, time_expo ambiguous\n"))
        self.assertTrue(qa["modelled_monthly_exposure_source_admission"].startswith("NOT_ADMITTED"))

    def test_grid_coordinate_drift_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"DIFFERENT_SOURCE_NATIVE_GRIDS"):
            check_monthly_native_source(
                {"eco_av.201001.nc":fake_month(),
                 "eco_av.201101.nc":fake_month(geoshift=.1)},
                native_readme_meaning(b"time_expo: percent exposed\n"))

    def test_no_source_outcome_or_unselected_year_in_native_arrays(self):
        # Build original-shaped synthetic known-truth netCDF with native fields
        # plus extra irrelevant "future_heading" to prove no such variable used.
        a=fake_month()
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"temp.nc"
            with Dataset(path,"w") as ds:
                ds.createDimension("y",486)
                ds.createDimension("x",820)
                for name,field in zip(("lat","lon","time_expo"),a):
                    v=ds.createVariable(name,"f4",("y","x"))
                    v[:]=field
                h=ds.createVariable("future_heading","f4",("y","x"))
                h[:]=999.
            raw=path.read_bytes()
            result=original_native_month(raw,"eco_av.201001.nc")
            np.testing.assert_allclose(result[0],a[0],rtol=1e-5)
            np.testing.assert_allclose(result[2],a[2],rtol=1e-5)
            with self.assertRaisesRegex(ValueError,"UNFROZEN"):
                original_native_month(raw,"eco_av.201208.nc")

if __name__=="__main__":
    unittest.main()
