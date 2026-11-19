import hashlib
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from validation_v200.original_BAW_year_NL_WFS_WCS_schema_envelope import (
 CAP_SHA, WFS_TYPES, WCS_IDS, native_metadata_gate,
 parsed_corner_pair, only_native_query, source_xml, PUBLISHED_VLIE_RD
)
class OriginalYearNLSourceContracts(unittest.TestCase):
    def test_names_locked_exactly_four_and_six(self):
        self.assertEqual(len(WFS_TYPES),4)
        self.assertEqual(len(WCS_IDS),6)
        self.assertEqual(len(set(WFS_TYPES)),4)
        self.assertEqual(len(set(WCS_IDS)),6)
        self.assertEqual(PUBLISHED_VLIE_RD,(135280,590000))
    def test_frozen_only_describe_no_original_data(self):
        u=only_native_query("WFS","DescribeFeatureType",WFS_TYPES[0])
        self.assertIn("DescribeFeatureType",u)
        self.assertNotIn("GetFeature",u)
        v=only_native_query("WCS","DescribeCoverage",WCS_IDS[0])
        self.assertIn("DescribeCoverage",v)
        self.assertNotIn("GetCoverage",v)
        with self.assertRaises(ValueError):
            only_native_query("WFS","GetFeature",WFS_TYPES[0])
        with self.assertRaises(ValueError):
            only_native_query("WCS","GetCoverage",WCS_IDS[0])
    def test_native_wfs_source_and_bbox(self):
        children=''.join(
          '<FeatureType><Name>'+nm+'</Name><DefaultCRS>EPSG:4326</DefaultCRS>'
          '<WGS84BoundingBox><LowerCorner>4.0 52.8</LowerCorner>'
          '<UpperCorner>7.5 54.2</UpperCorner></WGS84BoundingBox>'
          '</FeatureType>' for nm in WFS_TYPES)
        xml=('<WFS_Capabilities version="2.0.0"><OperationsMetadata>'
          '<Operation name="DescribeFeatureType"/></OperationsMetadata>'
          '<FeatureTypeList>'+children+'</FeatureTypeList></WFS_Capabilities>').encode()
        with patch.dict("validation_v200.original_BAW_year_NL_WFS_WCS_schema_envelope.CAP_SHA",{"WFS":hashlib.sha256(xml).hexdigest()}):
            root,entries,ops=native_metadata_gate(xml,"WFS")
            self.assertEqual(len(entries),4)
            self.assertIn("DescribeFeatureType",ops)
            self.assertEqual(parsed_corner_pair(entries[WFS_TYPES[0]]),[4,52.8,7.5,54.2])
            with self.assertRaisesRegex(ValueError,"SHA_CHANGED"):
                native_metadata_gate(xml+b" ", "WFS")
    def test_wcs_native_coverage_names(self):
        xml=('<Capabilities version="2.0.1">'
         '<Contents>'+''.join('<CoverageSummary><CoverageId>'+x+
         '</CoverageId></CoverageSummary>' for x in WCS_IDS)+'</Contents></Capabilities>').encode()
        with patch.dict("validation_v200.original_BAW_year_NL_WFS_WCS_schema_envelope.CAP_SHA",{"WCS":hashlib.sha256(xml).hexdigest()}):
            root,entries,ops=native_metadata_gate(xml,"WCS")
            self.assertEqual(len(entries),6)
    def test_reject_xxe(self):
        with self.assertRaisesRegex(ValueError,"DTD"):
            source_xml(b'<!DOCTYPE x [<!ENTITY p SYSTEM "file:///etc/passwd">]><WFS_Capabilities>&p;</WFS_Capabilities>')
if __name__=="__main__":
    unittest.main()
