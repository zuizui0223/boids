import unittest
import urllib.parse
from validation_v201.true_BAW_WFS_Vlieland_2018_2019_highlow_boundary_HITS import (
 WFS_TYPES,DISTANCE_M,SOURCE_WFS_NATIVE_CRS,fixed_roi,
 make_hits_request,only_native_WFS_hits_request,parse_original_native_hits
)
class OriginalWFS2BoundaryHITS(unittest.TestCase):
    def test_frozen_half_width_exactly_5km(self):
        r=fixed_roi()
        self.assertAlmostEqual(r[2]-r[0],10000)
        self.assertAlmostEqual(r[3]-r[1],10000)
        self.assertEqual(DISTANCE_M,5000)
        self.assertEqual(len(WFS_TYPES),4)
    def test_native_only_hits_no_geometry_get(self):
        r=fixed_roi()
        q=make_hits_request(WFS_TYPES[0],r)
        self.assertTrue(only_native_WFS_hits_request(q))
        self.assertEqual(dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(q).query))["resultType"],"hits")
        self.assertIn(SOURCE_WFS_NATIVE_CRS,urllib.parse.unquote(q))
        bad=(r[0]-5000,r[1],r[2],r[3])
        with self.assertRaises(ValueError):
            make_hits_request(WFS_TYPES[0],bad)
        with self.assertRaises(ValueError):
            make_hits_request("unexpected_2017_ger",r)
    def test_true_count_from_native_wfs2_featurecollection_only(self):
        x=b'<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" numberMatched="2" numberReturned="0"/>'
        self.assertEqual(parse_original_native_hits(x),2)
        z=b'<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" numberMatched="0" numberReturned="0"/>'
        self.assertEqual(parse_original_native_hits(z),0)
    def test_reject_noninteger_unknown_and_true_geometry(self):
        for x in (
          b'<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" numberMatched="unknown" numberReturned="0"/>',
          b'<ExceptionReport><Exception>Bad BBOX</Exception></ExceptionReport>',
          b'<FeatureCollection numberMatched="1" numberReturned="1"><member/></FeatureCollection>'
        ):
            with self.assertRaises(ValueError):
                parse_original_native_hits(x)
if __name__=="__main__":
    unittest.main()
