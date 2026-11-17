"""THREDDS catalog source-only fixtures. No original elevation or animal records."""
import unittest
from thredds_tile_catalog_source import inspect_xml
XML=b'''<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns="http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"
         xmlns:xlink="http://www.w3.org/1999/xlink">
 <dataset name="Root">
  <dataset name="vaklodingenKB125_1110.nc" urlPath="opendap/rijkswaterstaat/vaklodingen/vaklodingenKB125_1110.nc"/>
  <dataset name="vaklodingenKB125_1008.nc" urlPath="opendap/rijkswaterstaat/vaklodingen/vaklodingenKB125_1008.nc"/>
  <catalogRef xlink:title="Branch" xlink:href="another/catalog.xml"/>
 </dataset>
</catalog>'''
class TestRealTileSourceCatalog(unittest.TestCase):
    def test_only_dataset_name_not_spatial_coverage(self):
        o=inspect_xml(XML,{"original_catalog_binary_SHA256":"fixture"})
        self.assertEqual(o["n_XML_dataset_or_catalogRef_entries"],4)
        self.assertEqual(o["n_original_native_NetCDF_file_paths"],2)
        self.assertEqual(o["real_native_NetCDF_tile_crs_and_2016_altitude_DATE"],
                         "NOT_TESTED_FROM_CATALOG_NAMES")
        self.assertEqual(o["actual_bird_GPS_inside_valid_2016_survey_height"],"NOT_TESTED")
    def test_incorrect_non_THREDDS_root_rejected(self):
        with self.assertRaises(AssertionError):
            inspect_xml(b"<html><body>not catalog</body></html>",{})
    def test_vlieland_candidates_arent_proven_by_filename(self):
        o=inspect_xml(XML,{"original_catalog_binary_SHA256":"fixture"})
        self.assertEqual(o["n_tile_or_Vlieland_source_name_candidates"],2)
        self.assertTrue(all(x["source_name"].startswith("vaklodingenKB")
                            for x in o["source_dataset_name_samples_NOT_verified_GPS_coverage"]))
if __name__=="__main__":unittest.main()
