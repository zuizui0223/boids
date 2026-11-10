"""v120 source-only THREDDS original XML/HTML/NetCDF index known truths.

Synthetic fixtures in this test NEVER become alleged 2019/2020 coastal z or animals.
"""
import tempfile,unittest
from pathlib import Path
from netCDF4 import Dataset
import numpy as np
import original_delta_THREDDS_vaklodingen_catalog_source as q

class AuthenticDeltaSourceFrame(unittest.TestCase):
    def test_original_2020_and_old_source_endpoints_locked(self):
        self.assertEqual(len(q.SOURCES),2)
        self.assertIn('vaklodingen_new',q.SOURCES['2020_release_documented'])
        self.assertIn('vaklodingen/catalog.xml',q.SOURCES['older_tile_collection'])
        self.assertEqual(len(q.FIXED_ZEELAND_RD_POINT_CLOUD),4)
        with self.assertRaisesRegex(ValueError,'UNFROZEN'):
            q.get_original_source('https://fake.example/tiles.xml',1)
    def test_native_THREDDS_XML_catalog_distinct_files_no_pseudoreplication(self):
        raw=b'''<?xml version="1.0"?><catalog xmlns="http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0">
          <dataset name="top" ID="source"><dataset name="vaklodingenKB109_5150.nc"
          urlPath="opendap/rijkswaterstaat/vaklodingen/vaklodingenKB109_5150.nc"/>
          <dataset name="vaklodingenKB109_5150.nc"
          urlPath="opendap/rijkswaterstaat/vaklodingen/vaklodingenKB109_5150.nc"/>
          <dataset name="vaklodingenKB110_4948.nc" urlPath="a/b.nc"/>
          <dataset name="catalog.nc" urlPath="c/catalog.nc"/></dataset></catalog>'''
        out=q.parse_true_catalog_xml(raw)
        self.assertEqual(out['n_distinct_original_tile_NC'],2)
        self.assertEqual(out['n_auxiliary_NC'],1)
        self.assertEqual(out['original_all_tile_source_names_sorted'],
              ['vaklodingenKB109_5150.nc','vaklodingenKB110_4948.nc'])
        self.assertEqual(out['native_2020_true_survey_year'],'NOT_ESTABLISHED_FROM_SERVER_RELEASE_OR_FILE_MODIFIED')
    def test_HTTP_page_lacks_CRS_survey_year_and_NAP_cannot_be_treated_as_seabed(self):
        raw=b'<html><body>Catalog <a>vaklodingenKB123_3332.nc</a><a>vaklodingenKB123_3332.nc</a></body></html>'
        out=q.parse_original_catalog_html(raw)
        self.assertEqual(out['n_distinct_original_tile_NC'],1)
        self.assertTrue(out['original_source_HTML_has_no_valid_actual_seabed_pixels'])
        with self.assertRaisesRegex(RuntimeError,'NOT_CATALOG'):
            q.parse_true_catalog_xml(raw)
    def test_original_small_NC_index_is_not_2020_surveys(self):
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/'real-format.nc'
            with Dataset(file,'w',format='NETCDF4') as ds:
                ds.createDimension('x',3)
                x=ds.createVariable('x','f8',('x',))
                x[:]=[34000.,44000.,54000.]
                x.units='m';ds.title='Catalog of tile grids, not original 2020 seabed'
            raw=file.read_bytes()
            info=q.source_native_small_index(raw,temp)
            self.assertEqual(info['original_source_index_native_variables']['x']['numeric_1d_native_extent'],
                             [34000.,54000.])
            self.assertTrue(info['index_is_not_measurement_of_2020_bird_seabed_or_tidalflat'])
    def test_no_2019_height_hypothesis_from_server_catalog_timestamp(self):
        self.assertIn('NO animal results',q.__doc__)
        self.assertTrue(q.EXTENT_NEEDS_NATIVE_CRS_AND_PIXEL_MASK)
if __name__=='__main__':unittest.main()
