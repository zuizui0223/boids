import unittest
from validation_v216.original_BAW_ncHydro_yearly_WCS_candidate_metadata import (
  CANDIDATE, fixed_wcs_authorized, parse_native_WCS_capabilities,
  describe_URL,parse_native_WCS_desc,safe_xml
)

class BAWTimedNCOriginalWCSProbe(unittest.TestCase):
    def test_only_two_carefully_frozen_candidate_WCS_not_unverified_original(self):
        self.assertEqual(set(CANDIDATE),{"2018","2019"})
        for year,url in CANDIDATE.items():
            self.assertTrue(fixed_wcs_authorized(url,year,"GetCapabilities"))
            self.assertFalse(fixed_wcs_authorized(url.replace("https://","http://"),
                                                   year,"GetCapabilities"))
            self.assertFalse(fixed_wcs_authorized(url.replace(
                "coast.baw.de","fake.example"),year,"GetCapabilities"))
        self.assertFalse(fixed_wcs_authorized(CANDIDATE["2018"],"2019","GetCapabilities"))

    def test_original_WCS2_native_height_layer_must_be_nl_and_year(self):
        xml=b'''<wcs:Capabilities xmlns:wcs="http://www.opengis.net/wcs/2.0"
            xmlns:ows="http://www.opengis.net/ows/2.0" version="2.0.1">
          <ows:OperationsMetadata><ows:Operation name="DescribeCoverage"/></ows:OperationsMetadata>
          <wcs:Contents>
            <wcs:CoverageSummary><wcs:CoverageId>Hydro:sea_surface_height_2d_2018_NL</wcs:CoverageId></wcs:CoverageSummary>
            <wcs:CoverageSummary><wcs:CoverageId>Hydro:sea_surface_height_2d_2018_DE</wcs:CoverageId></wcs:CoverageSummary>
            <wcs:CoverageSummary><wcs:CoverageId>Hydro:salinity_2018_NL</wcs:CoverageId></wcs:CoverageSummary>
          </wcs:Contents>
        </wcs:Capabilities>'''
        x=parse_native_WCS_capabilities(xml,"2018")
        self.assertEqual(x["native_number_of_CoverageIds"],3)
        self.assertEqual(x["candidate_count"],1)
        self.assertIn("DescribeCoverage",x["native_advertised_operations"])
        cover=x["native_2018_2019_NL_SSH_CoverageId_candidates"][0]["native_CoverageId"]
        self.assertEqual(cover,"Hydro:sea_surface_height_2d_2018_NL")
        url=describe_URL("2018",cover)
        self.assertTrue(fixed_wcs_authorized(url,"2018","DescribeCoverage",cover))
        self.assertIn("coverageId=",url)
        self.assertFalse(fixed_wcs_authorized(url,"2019","DescribeCoverage",cover))

    def test_OGC_nil_from_WCS_is_not_original_NetCDF_fillvalue(self):
        source=b'''<wcs:CoverageDescriptions xmlns:wcs="http://www.opengis.net/wcs/2.0"
          xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:swe="http://www.opengis.net/swe/2.0">
          <wcs:CoverageDescription><wcs:CoverageId>Hydro:sea_surface_height_2d_2018_NL</wcs:CoverageId>
            <gml:boundedBy><gml:Envelope srsName="EPSG:4326" axisLabels="Lat Lon">
            <gml:lowerCorner>50 4</gml:lowerCorner>
            <gml:upperCorner>56 10</gml:upperCorner></gml:Envelope></gml:boundedBy>
            <gml:rangeType><swe:DataRecord>
              <swe:field name="sea_surface_height_2d"><swe:Quantity>
                <swe:uom code="m"/><swe:nilValues><swe:NilValues>
                <swe:nilValue reason="missing">9.999999848e30</swe:nilValue>
                </swe:NilValues></swe:nilValues>
              </swe:Quantity></swe:field>
            </swe:DataRecord></gml:rangeType>
          </wcs:CoverageDescription></wcs:CoverageDescriptions>'''
        x=parse_native_WCS_desc(source,"Hydro:sea_surface_height_2d_2018_NL")
        self.assertEqual(x["native_WCS_range_fields"][0]["native_WCS_uom"],["m"])
        self.assertEqual(x["native_WCS_nil_values"][0]["value"],"9.999999848e30")
        self.assertFalse(x["original_NetCDF_units_FillValue_datum_verified"])
        self.assertTrue(x["OGC_service_nil_is_not_original_NetCDF__FillValue"])

    def test_no_false_source_pass_for_html_serviceexception_XXE(self):
        for xml in (b"<html><body>not a WCS</body></html>",
                    b'<ServiceExceptionReport><ServiceException>Unknown coverage</ServiceException></ServiceExceptionReport>'):
            with self.assertRaises(ValueError):
                parse_native_WCS_capabilities(xml,"2018")
        with self.assertRaises(ValueError):
            safe_xml(b'<!DOCTYPE html [<!ENTITY ext SYSTEM "file:///etc/passwd">]><Capabilities>&ext;</Capabilities>',"Capabilities")
        with self.assertRaises(ValueError):
            parse_native_WCS_capabilities(b'<Capabilities version="1.0.0"/>',"2018")

if __name__=="__main__":
    unittest.main()
