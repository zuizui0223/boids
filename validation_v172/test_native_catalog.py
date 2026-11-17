"""Source-independent fixture for a genuine small THREDDS catalog NetCDF."""
import tempfile,unittest
from pathlib import Path
from netCDF4 import Dataset
from native_catalog_nc_geoindex import schema,VLIE_RD_SEARCH

class TestV172(unittest.TestCase):
    def test_original_netcdf_catalog_variable_parsing(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"synthetic_catalog.nc"
            with Dataset(str(path),"w",format="NETCDF4_CLASSIC") as nc:
                nc.createDimension("tile",3)
                nc.createDimension("char",12)
                x=nc.createVariable("tile_west_rd","f8",("tile",))
                x[:]=[125000.,135000.,145000.]
                nc.title="SYNTHETIC DO NOT CONSIDER VERIFIED HISTORIC"
            value=schema(path.read_bytes(),{"original_binary_SHA256":"synthetic"})
        self.assertEqual(value["original_netcdf_dims"]["tile"],3)
        self.assertEqual(value["original_netcdf_variables"]["tile_west_rd"]["numeric_max"],145000.)
        self.assertEqual(value["tile_2016_actual_xy_isource_and_NAP_coverage"],"NOT_YET_VERIFIED")
    def test_untrusted_catalog_cannot_claim_animal_exposure(self):
        self.assertEqual(VLIE_RD_SEARCH,[120000,575000,150000,615000])
if __name__=="__main__":unittest.main()
