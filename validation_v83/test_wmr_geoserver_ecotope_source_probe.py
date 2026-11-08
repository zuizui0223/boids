"""v83B synthetic WMR original-GeoServer source and V2 version guard tests."""
import json
import unittest
from unittest.mock import patch

import wmr_geoserver_ecotope_source_probe as p

def mock_cap(*,corrected=False):
    version=("Corrected 2021, 4% mean exposure revision. "
             "doi 10.17632/27mysx289g.2" if corrected
             else "2008-2012 Wadden trilateral ecotopes, publication 2019")
    s=f'''<?xml version="1.0"?>
    <wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs/2.0"
        xmlns:ows="http://www.opengis.net/ows/1.1">
       <wfs:FeatureTypeList><wfs:FeatureType>
          <wfs:Name>{p.MAIN}</wfs:Name><wfs:Title>WS3 ECOTOPE original</wfs:Title>
          <wfs:Abstract>{version}</wfs:Abstract>
          <ows:WGS84BoundingBox><ows:LowerCorner>5.1 53.1</ows:LowerCorner>
          <ows:UpperCorner>6.9 54.0</ows:UpperCorner></ows:WGS84BoundingBox>
       </wfs:FeatureType></wfs:FeatureTypeList>
    </wfs:WFS_Capabilities>'''
    return s.encode()

def mock_schema():
    return ('''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
       <xs:complexType name="eco"><xs:sequence>
       <xs:element name="LitoralCod" type="xs:int"/>
       <xs:element name="DynamicCod" type="xs:int"/>
       <xs:element name="the_geom" type="xs:string"/>
       </xs:sequence></xs:complexType></xs:schema>''').encode()

def mock_features():
    return json.dumps({"type":"FeatureCollection","features":[{
       "type":"Feature","geometry":{"type":"MultiPolygon",
         "coordinates":[[[[6.0,53.40],[6.02,53.41],[6.0,53.40]]]]},
       "properties":{"LitoralCod":2,"DynamicCod":0,"secret_tag":"not_animal_data"}
    }]}).encode()

class OriginalWMRWebServiceKnownTruth(unittest.TestCase):
    def test_layer_id_pinned_and_genuine_original_capabilities_source(self):
        a=p.native_capabilities(mock_cap())
        self.assertTrue(a["original_main_ecotope_layer_present"])
        self.assertIn(p.MAIN,a["source_original_relevant_layers"])
        b=p.native_schema(mock_schema())
        self.assertIn("LitoralCod",b["original_native_litoral_or_depth_fields"])
        self.assertFalse(p.version_strict_from_publisher_meta(a,b)[
            "corrected_2021_v2_SOURCE_status"]==
            "CORRECTED_2021_V2_PROVENANCE_VERIFIED")

    def test_corrected_provenance_requires_metadata_not_wfs_layer_title(self):
        cap=p.native_capabilities(mock_cap(corrected=True))
        schema=p.native_schema(mock_schema())
        v=p.version_strict_from_publisher_meta(cap,schema)
        self.assertTrue(v["source_version_2021_v2_DOI_in_WMR_original_native_metadata"])
        self.assertEqual(v["corrected_2021_v2_SOURCE_status"],
                         "CORRECTED_2021_V2_PROVENANCE_VERIFIED")
        self.assertEqual(p.EXPECTED_CORRECTED_DOI,
                         "10.17632/27mysx289g.2")

    def test_no_animal_or_polygon_coordinates_exported_from_original_feature_sample(self):
        q=p.native_sample(mock_features(),"Schiermonnikoog")
        self.assertEqual(q["original_WFS_polygon_geojson_samples"],1)
        self.assertEqual(q["original_native_relevant_class_code_sample_counts"],
                         {"LitoralCod:2":1,"DynamicCod:0":1})
        self.assertNotIn("[6.0",json.dumps(q))
        self.assertEqual(q["original_geometries_only_type_counts_not_original_coordinates"],
                         {"MultiPolygon":1})

    def test_invalid_geojson_or_schema_or_service_exception_stops(self):
        with self.assertRaisesRegex(p.SourceUnavailable,"GEOJSON"):
            p.native_sample(b"not json","Ameland_Nes")
        with self.assertRaisesRegex(p.SourceUnavailable,"FIELDS_NOT_RETURNED"):
            p.native_schema(b"<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'/>")
        with self.assertRaisesRegex(p.SourceUnavailable,"WFS_EXCEPTION"):
            p.native_capabilities(b"<ExceptionReport/>")
        with self.assertRaisesRegex(p.SourceUnavailable,"GEOJSON"):
            p.native_sample(b'{"error":"no data"}',"Ameland_Nes")

    def test_trilateral_wfs_bbox_and_feature_count_locked(self):
        self.assertEqual(p.MAX_GEO_FEATURES,10)
        self.assertEqual(len(p.STATION_BBOX),2)
        self.assertEqual(p.STATION_BBOX["Schiermonnikoog"],(6,53.35,6.32,53.53))
        self.assertTrue(all(name.startswith("WS3shp:ws3_")
                            for name in p.EXPECTED_LAYERS))

if __name__=="__main__":
    unittest.main()
