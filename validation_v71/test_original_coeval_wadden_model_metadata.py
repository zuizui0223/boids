"""v71 synthetic tests of original provider MD5, dataset fidelity and tide cadence."""
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

from original_coeval_wadden_model_metadata import (
    CKAN,DATAVERSE,PACKAGE,DOI,FILE_NAMES,original_metadata,
    authenticated_provider_file,netcdf_source_structure)

def simulated_original_netcdf(n=96):
    """Known-truth *synthetic* hydro array, NOT field NIOZ source."""
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"synthetic.nc"
        with Dataset(path,"w") as d:
            d.createDimension("time",n)
            d.createDimension("latitude",2)
            d.createDimension("longitude",3)
            t=d.createVariable("time","f8",("time",))
            t.standard_name="time"
            t.units="hours since 2010-01-01 00:00:00"
            t[:]=np.arange(n,dtype=float)
            lat=d.createVariable("latitude","f4",("latitude",))
            lat.units="degrees_north"
            lat.standard_name="latitude"
            lat[:]=[53.2,53.7]
            lon=d.createVariable("longitude","f4",("longitude",))
            lon.units="degrees_east"
            lon.standard_name="longitude"
            lon[:]=[5.5,6.,6.5]
            surface=d.createVariable("water_level","f4",
                ("time","latitude","longitude"))
            surface.units="m"
            surface.long_name="sea surface water level synthetic"
            surface[:]=0.
        return path.read_bytes()

def simulated_provider():
    a=simulated_original_netcdf()
    b=b"Public original source readme synthetic known truth.\n"
    blobs={"README.txt":b,"eco_av.201001.nc":a,
           "eco_av.201101.nc":a}
    resources=[]
    for year in (2009,2010,2011):
        for month in range(1,13):
            name=f"eco_av.{year}{month:02d}.nc"
            raw=blobs.get(name,a)
            resources.append({"name":name,
                "size":len(raw),
                "hash":hashlib.md5(raw).hexdigest(),
                "url":"https://doi.nioz.nl/not-real/"+name})
    resources.append({"name":"README.txt","size":len(b),
        "hash":hashlib.md5(b).hexdigest(),
        "url":"https://doi.nioz.nl/not-real/README.txt"})
    reply={"success":True,"result":{"id":PACKAGE,"resources":resources}}
    def getter(url,cap):
        if url==CKAN:
            return json.dumps(reply).encode()
        if url==DATAVERSE:
            raise ValueError("this synthetic test authenticates CKAN only")
        for filename,value in blobs.items():
            if url.endswith(filename):return value
        raise RuntimeError("Unexpected provider source URL")
    return getter,blobs

class AuthenticNIOZSourceAuditTests(unittest.TestCase):
    def test_provider_manifest_36_frozen_months_and_MD5(self):
        getter,blobs=simulated_provider()
        metadata=original_metadata(fetch=getter)
        self.assertEqual(metadata["method"],"CKAN_ORIGINAL_PROVIDER")
        self.assertEqual(metadata["total_original_netcdf_monthly_resources"],36)
        for name in FILE_NAMES:
            _,receipt=authenticated_provider_file(
                metadata["source_original_resources"][name],fetch=getter)
            self.assertTrue(receipt["original_provider_MD5_verified"])
            self.assertEqual(receipt["original_bytes"],len(blobs[name]))
        self.assertEqual(metadata["package_identifier"],PACKAGE)

    def test_falsified_MD5_stops_and_wrong_remote_host_stops(self):
        getter,_=simulated_provider()
        manifest=original_metadata(fetch=getter)
        record=manifest["source_original_resources"]["README.txt"]
        with self.assertRaisesRegex(ValueError,"MD5_MISMATCH"):
            authenticated_provider_file({**record,
                "md5":"0"*32},fetch=getter)
        badreply=json.loads(getter(CKAN,cap=5_000_000))
        badreply["result"]["resources"][-1]["url"]="https://malicious.invalid/fake"
        def bad_getter(url,cap):
            if url==CKAN:return json.dumps(badreply).encode()
            raise ValueError("no alternative provider")
        with self.assertRaisesRegex(RuntimeError,"SOURCE_STOP"):
            original_metadata(fetch=bad_getter)

    def test_original_structural_field_time_and_geographic_admission_only(self):
        buf=simulated_original_netcdf()
        report=netcdf_source_structure(buf,source_month="201001")
        self.assertTrue(report["source_temporal_within_tide_resolution_supported"])
        self.assertTrue(report["both_wadden_site_reference_points_inside_native_lat_lon_bounding_box"])
        self.assertIn("water_level",report["original_marine_hydrodynamic_variable_names_candidates"])
        self.assertNotIn("synthetic_bird",str(report))
        self.assertTrue(report["no_wave_model_OR_bathy_cells_or_2010_bird_GPS_read_or_exported"])

    def test_temporal_monthly_mean_is_not_misclassified_as_tidal_hydrodynamics(self):
        raw=simulated_original_netcdf(n=1)
        result=netcdf_source_structure(raw,source_month="201101")
        self.assertFalse(result["source_temporal_within_tide_resolution_supported"])
        self.assertTrue(result["both_wadden_site_reference_points_inside_native_lat_lon_bounding_box"])
        with self.assertRaisesRegex(ValueError,"MONTH_NOT_LOCKED"):
            netcdf_source_structure(raw,source_month="201612")

if __name__=="__main__":
    unittest.main()
