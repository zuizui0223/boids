"""Known-truth pure tests of official historical AHN2 WCS source integrity.

Fake GeoTIFF is synthetic; no wild birds/tide cause ever enters unit tests.
"""
import io,unittest
from collections import namedtuple
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from pyproj import Transformer
from ahn2_original_dtm_source_gate import (
    OFFICIAL_DTM_WCS,SAMPLE_CENTRES,
    SourceStop,parse_wcs_caps,parse_coverage_description,inspect_patch,
    bounded_get,PATCH_METRES,PATCH_PIXELS)

CAPABILITIES=b"""<?xml version="1.0"?>
<wcs:WCS_Capabilities xmlns:wcs="http://www.opengis.net/wcs" version="1.0.0">
 <wcs:ContentMetadata><wcs:CoverageOfferingBrief>
 <wcs:name>AHN2_DTM</wcs:name>
 </wcs:CoverageOfferingBrief></wcs:ContentMetadata>
</wcs:WCS_Capabilities>"""
DESC=b"""<?xml version="1.0"?>
<wcs:CoverageDescription xmlns:wcs="http://www.opengis.net/wcs">
 <wcs:CoverageOffering>
 <wcs:name>AHN2_DTM</wcs:name>
 <wcs:supportedCRSs><wcs:requestResponseCRSs>EPSG:28992</wcs:requestResponseCRSs></wcs:supportedCRSs>
 <wcs:supportedFormats><wcs:formats>GeoTIFF</wcs:formats></wcs:supportedFormats>
 </wcs:CoverageOffering>
</wcs:CoverageDescription>"""

class Ahn2OriginalSourceTest(unittest.TestCase):
    def test_frozen_original_WCS_and_coverage_from_source_XML(self):
        self.assertTrue(OFFICIAL_DTM_WCS.startswith("https://api.ellipsis-drive.com"))
        c=parse_wcs_caps(CAPABILITIES)
        self.assertEqual(c["chosen_original_DTM_coverage"],"AHN2_DTM")
        d=parse_coverage_description(DESC,"AHN2_DTM")
        self.assertEqual(d["requested_format"],"GeoTIFF")
        self.assertEqual(d["horizontal_CRS_declared"],"EPSG:28992")
    def test_wrong_coverage_or_current_ahn6_disallowed(self):
        bad=CAPABILITIES.replace(b"AHN2_DTM",b"AHN6_DSM")
        # No silent switch to current AHN6 if the official AHN2 endpoint mutated.
        # Single layer named AHN6_DSM is not accepted: current code would
        # permit it because endpoint was specific; this guard is important.
        with self.assertRaises(SourceStop):
            parse_wcs_caps(bad)
    def test_synthetic_source_geotiff_pixel_nodata_and_crs(self):
        site="ameland";lat,lon=SAMPLE_CENTRES[site]
        east,north=Transformer.from_crs(4326,28992,always_xy=True).transform(lon,lat)
        data=np.full((128,128),-9999,dtype="float32")
        data[:60,:60]=.25
        data[60:80,60:80]=-1.5
        transform=from_origin(east-PATCH_METRES/2,north+PATCH_METRES/2,
                              PATCH_METRES/128,PATCH_METRES/128)
        with MemoryFile() as mem:
            with mem.open(driver="GTiff",height=128,width=128,count=1,
                          dtype="float32",crs="EPSG:28992",transform=transform,
                          nodata=-9999) as ds:
                ds.write(data,1)
            encoded=mem.read()
        result=inspect_patch(encoded,(east,north),site)
        self.assertEqual(result["source_finite_pixels"],4000)
        self.assertEqual(result["source_candidate_minus3_plus3_NAP_pixels"],4000)
        self.assertEqual(result["original_raster_crs_epsg"],28992)
        self.assertFalse(result["historical_GPS_or_tide_join"])
        with self.assertRaisesRegex(SourceStop,"NOT_GEOTIFF"):
            inspect_patch(b"not a TIFF",(east,north),site)
    def test_bounded_get_http_error_status_or_oversize(self):
        class Response:
            status=200
            headers={"Content-Type":"text/xml"}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return b"x"*(n+1)
        with self.assertRaisesRegex(SourceStop,"OVER_CAP"):
            bounded_get(OFFICIAL_DTM_WCS,{"request":"GetCapabilities"},10,
                        opener=lambda *args,**kw:Response())
        with self.assertRaisesRegex(SourceStop,"NOT_OFFICIAL"):
            bounded_get("https://not.official/",{"request":"GetCapabilities"},100)
    def test_AHN2_surface_not_evidence_of_direct_real_exposure(self):
        self.assertEqual(set(SAMPLE_CENTRES),
                         {"schiermonnikoog","ameland"})
        with self.assertRaisesRegex(SourceStop,"EPSG28992"):
            parse_coverage_description(DESC.replace(b"28992",b"3857"),"AHN2_DTM")
if __name__=="__main__":unittest.main()
