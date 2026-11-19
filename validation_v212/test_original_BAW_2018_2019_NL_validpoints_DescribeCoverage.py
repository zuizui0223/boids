import hashlib
import unittest
import xml.etree.ElementTree as ET
from validation_v212.original_BAW_2018_2019_NL_validpoints_DescribeCoverage import (
 FROZEN_NATIVE_WCS_CAP_SHA,FROZEN_VALID_COUNTS,
 native_coverage_describe_URL,only_frozen_describe_URL,
 native_doc,inspect_native_coverage_description
)

class ExactBAWYearlyValidCountMetadata(unittest.TestCase):
    def test_two_native_annual_not_raw_20min_year_ids(self):
        self.assertEqual(set(FROZEN_VALID_COUNTS),{"2018","2019"})
        self.assertEqual(len(FROZEN_NATIVE_WCS_CAP_SHA),2)
        self.assertEqual(len(set(FROZEN_VALID_COUNTS.values())),2)
        self.assertTrue(all("nof_valid_data_points" in x and x.endswith("_nl")
                            for x in FROZEN_VALID_COUNTS.values()))
        self.assertTrue(all(len(h)==64 for h in FROZEN_NATIVE_WCS_CAP_SHA.values()))

    def test_do_not_guess_destination_route_other_than_source_verified_same_year(self):
        cap="https://coast.baw.de/geoserver/TrilaWatt_Hydrodynamik_2018/ows?service=WCS&version=2.0.1&request=GetCapabilities"
        url=native_coverage_describe_URL("2018",cap)
        self.assertTrue(only_frozen_describe_URL(url,"2018",cap))
        self.assertIn("DescribeCoverage",url)
        self.assertIn("nof_valid_data_points_2018_nl",url)
        self.assertNotIn("GetCoverage",url)
        with self.assertRaises(ValueError):
            native_coverage_describe_URL("2019",cap)
        with self.assertRaises(ValueError):
            native_coverage_describe_URL("2018",cap.replace("coast.baw.de","example.invalid"))

    def test_true_native_annual_coverage_envelope_not_synthetic_water_depth(self):
        xml=f'''<wcs:CoverageDescriptions xmlns:wcs="http://www.opengis.net/wcs/2.0"
             xmlns:gml="http://www.opengis.net/gml/3.2"
             xmlns:swe="http://www.opengis.net/swe/2.0">
          <wcs:CoverageDescription>
            <wcs:CoverageId>{FROZEN_VALID_COUNTS["2018"]}</wcs:CoverageId>
            <gml:boundedBy>
              <gml:Envelope srsName="http://www.opengis.net/def/crs/EPSG/0/25832" axisLabels="E N">
                <gml:lowerCorner>180000 5820000</gml:lowerCorner>
                <gml:upperCorner>450000 6120000</gml:upperCorner>
              </gml:Envelope>
            </gml:boundedBy>
            <gml:domainSet><gml:RectifiedGrid dimension="2">
              <gml:origin><gml:Point><gml:pos>180010 5820010</gml:pos></gml:Point></gml:origin>
              <gml:offsetVector>20 0</gml:offsetVector>
              <gml:offsetVector>0 20</gml:offsetVector>
            </gml:RectifiedGrid></gml:domainSet>
            <gml:rangeType><swe:DataRecord>
              <swe:field name="nof_valid_data_points"><swe:Quantity><swe:uom code="1"/></swe:Quantity></swe:field>
            </swe:DataRecord></gml:rangeType>
          </wcs:CoverageDescription>
        </wcs:CoverageDescriptions>'''.encode()
        doc=native_doc(xml,"CoverageDescriptions")
        meta=inspect_native_coverage_description(doc,"2018")
        self.assertEqual(meta["original_envelopes"][0]["native_axisLabels"],"E N")
        self.assertEqual(meta["native_rangeType_fields"][0]["name"],"nof_valid_data_points")
        self.assertTrue(meta["raw_WMS_1e31_FillValue_NOT_derived_from_annual_data"])

    def test_wrong_coverage_identity_and_XML_entity_rejected(self):
        x=(b'<CoverageDescriptions><CoverageDescription><CoverageId>unknown</CoverageId>'
           b'<Envelope srsName="EPSG:25832"><lowerCorner>1 1</lowerCorner>'
           b'<upperCorner>2 2</upperCorner></Envelope></CoverageDescription></CoverageDescriptions>')
        with self.assertRaises(ValueError):
            inspect_native_coverage_description(native_doc(x),"2018")
        with self.assertRaises(ValueError):
            native_doc(b'<!DOCTYPE z [<!ENTITY x SYSTEM "file:///etc/passwd">]><CoverageDescriptions>&x;</CoverageDescriptions>')
if __name__=="__main__":
    unittest.main()
