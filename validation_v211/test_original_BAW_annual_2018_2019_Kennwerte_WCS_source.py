import unittest
import hashlib
from validation_v211.original_BAW_annual_2018_2019_Kennwerte_WCS_source import (
 OFFICIAL_SOURCE_URLS,is_approved_original_year_url,
 parse_native_original_annual_WCS,is_native_count_coverage,
 RefuseUnverifiedRedirect
)
class StrictBAWAnnualOriginalSource(unittest.TestCase):
    def test_only_two_independently_official_year_WCS_urls(self):
        self.assertEqual(set(OFFICIAL_SOURCE_URLS),{"2018","2019"})
        for year,url in OFFICIAL_SOURCE_URLS.items():
            self.assertTrue(is_approved_original_year_url(url,year,"mdi-dienste.baw.de"))
            self.assertFalse(is_approved_original_year_url(url,year,"coast.baw.de"))
            self.assertFalse(is_approved_original_year_url(url.replace("https://","http://"),year,"mdi-dienste.baw.de"))
            self.assertFalse(is_approved_original_year_url(url.replace(year,"2020"),year,"mdi-dienste.baw.de"))
            allowed=url.replace("mdi-dienste.baw.de","coast.baw.de")
            self.assertTrue(is_approved_original_year_url(allowed,year,"coast.baw.de"))
        self.assertIsNone(RefuseUnverifiedRedirect().redirect_request(None,None,308,"",{},"https://evil.com/"))

    def test_native_coverage_id_names_from_real_xml_only(self):
        xml=b"""<?xml version="1.0"?>
         <Capabilities version="2.0.1" xmlns:wcs="http://www.opengis.net/wcs/2.0"
          xmlns:ows="http://www.opengis.net/ows/2.0">
           <wcs:Contents>
             <wcs:CoverageSummary><wcs:CoverageId>Wasserstand_2018_NL_no_filter</wcs:CoverageId></wcs:CoverageSummary>
             <wcs:CoverageSummary><wcs:CoverageId>count_valid_data_points_2018_NL</wcs:CoverageId></wcs:CoverageSummary>
             <wcs:CoverageSummary><wcs:CoverageId>tide_high_2018_nl</wcs:CoverageId></wcs:CoverageSummary>
           </wcs:Contents>
         </Capabilities>"""
        out=parse_native_original_annual_WCS(xml)
        self.assertEqual(out["n_original_CoverageSummary"],3)
        self.assertEqual(out["n_native_valid_count_candidates"],1)
        self.assertEqual(out["n_native_no_filter_candidates"],1)
        self.assertTrue(out["raw_time_resolved_20min_WMS_FillValue_NOT_derived_from_annual_Coverages"])

    def test_strict_separate_annual_name_not_time_series_WMS(self):
        self.assertFalse(is_native_count_coverage("sea_surface_height_2d_2019_NL"))
        self.assertTrue(is_native_count_coverage("Anzahl_gueltiger_Datenpunkte_2019_NL"))
        self.assertTrue(is_native_count_coverage("count_valid_data_points_2018_NL"))

    def test_untrusted_jats_or_malformed_XML_stops(self):
        with self.assertRaises(ValueError):
            parse_native_original_annual_WCS(b'<!DOCTYPE x [<!ENTITY ex SYSTEM "file:///etc/passwd">]><Capabilities>&ex;</Capabilities>')
        with self.assertRaises(ValueError):
            parse_native_original_annual_WCS(b'<html><body>wrong type</body></html>')
        with self.assertRaises(ValueError):
            parse_native_original_annual_WCS(b'<Capabilities version="2.0.1"><Contents></Contents></Capabilities>')
if __name__=="__main__":
    unittest.main()
