"""Source-only original BAW WCS and directory HTML pure fixture tests."""
import unittest
import source_only as m
class BAWKnownTruth(unittest.TestCase):
 def test_fixed_years_original_and_no_vertical_datum_guess(self):
  self.assertEqual(m.YEAR_WINDOW,(2008,2009,2010,2011,2012))
  self.assertEqual(m.EXPECTED_DEM_HORIZONTAL,"EPSG:25832")
  self.assertNotEqual(m.EXPECTED_VERTICAL_SOURCE,m.ORIGINAL_RWS_TIDE_VERTICAL)
 def test_source_urls_only_official_wcs_or_official_directory(self):
  self.assertTrue(m.BAW_DATA.startswith("https://dl.datenrepository.baw.de/"))
  self.assertTrue(m.BAW_WCS.startswith("https://mdi-dienste.baw.de/"))
  with self.assertRaisesRegex(ValueError,"not registered"):m._request_metadata("https://untrusted.example.org/file")
 def test_html_actual_file_per_year_does_not_infer_from_folder_range(self):
  s=b'''<html><a href="2010_topography_netherlands.tif">2010</a>
      <a href="2008_topography_netherlands.tif">2008</a>
      <a href="1996-2014_metadata.html">1996-2014</a></html>'''
  x=m.parse_index(s)
  self.assertEqual(x["source_linked_year_specific_files"]["2010"],["2010_topography_netherlands.tif"])
  self.assertFalse(x["all_five_historical_year_names_advertised"])
 def test_wcs_coverage_ids_parse_actual_annual_names_only(self):
  raw=b'''<Capabilities version="2.0.1" xmlns:wcs="http://www.opengis.net/wcs/2.0">
      <Contents><wcs:CoverageSummary><wcs:CoverageId>topography_NL_2008</wcs:CoverageId>
      <wcs:Title>NL 2008 10m</wcs:Title></wcs:CoverageSummary>
      <wcs:CoverageSummary><wcs:CoverageId>topography_NL_2010</wcs:CoverageId>
      <wcs:Title>NL 2010 10m</wcs:Title></wcs:CoverageSummary>
      </Contents></Capabilities>'''
  x=m.parse_wcs(raw)
  self.assertEqual(x["original_WCS_version"],"2.0.1")
  self.assertEqual(x["original_coverage_ids_for_2008_2012"]["2010"],["topography_NL_2010"])
  self.assertFalse(x["all_five_years_WCS_discoverable"])
 def test_year_code_without_false_partial_matches(self):
  self.assertEqual(m.years_in_text("NL_2008_2012_Geotiff"),[2008,2012])
  self.assertEqual(m.years_in_text("bogus_12010.tif"),[])
if __name__=="__main__":unittest.main()
