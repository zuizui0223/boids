"""Invented source metadata and schema only. No bird GPS or map geometries."""
import unittest
import source_only as s

class SourceOnlyKnownTruth(unittest.TestCase):
 def test_fixed_corrected_dataset_and_no_old_version(self):
  self.assertEqual(s.MENDELEY_ID,"27mysx289g")
  self.assertEqual(s.VERSION,2)
  self.assertEqual(s.ZIP_NAME,"EctpWZ3L_gpkg.zip")
  self.assertEqual(len(s.LAYER_IDS),3)
  self.assertIn("WS3shp:ws3_ecotope_mp_litoral_zones_and_dynamics",s.LAYER_IDS)
 def test_wfs_uses_only_source_catalog_and_schema(self):
  with self.assertRaises(ValueError):s.url_for_wfs("GetFeature")
  with self.assertRaises(ValueError):s.url_for_wfs("DescribeFeatureType","WS3shp:untrusted")
 def test_no_signed_metadata_url_or_token_export(self):
  fake={"filename":s.ZIP_NAME,"id":"file-uuid","content_details":{
       "download_url":"https://private.example.com/SECRET",
       "sha256_hash":"a"*64,"size":34567,"content_type":"application/zip"}}
  d=s.file_entry(fake)
  self.assertEqual(d["published_sha256"],"a"*64)
  self.assertNotIn("SECRET",str(d))
 def test_wfs_only_frozen_layers_in_capabilities(self):
  xml=b'''<WFS_Capabilities><FeatureTypeList>
    <FeatureType><Name>WS3shp:ws3_ecotope_mp_basic</Name>
      <Title>Old Wadden ecotope</Title><DefaultCRS>EPSG:28992</DefaultCRS>
      <WGS84BoundingBox><LowerCorner>5.0 52.0</LowerCorner>
       <UpperCorner>7.0 54.0</UpperCorner></WGS84BoundingBox>
    </FeatureType>
    <FeatureType><Name>WS3shp:ws3_bivbeds_focc</Name></FeatureType>
    <FeatureType><Name>OTHER:random</Name></FeatureType>
    </FeatureTypeList></WFS_Capabilities>'''
  a=s.wfs_capabilities(xml)
  self.assertEqual(a["matched_layers"],2)
  self.assertFalse(a["all_required_present"])
  self.assertEqual(a["three_frozen_ecotope_layers"][s.LAYER_IDS[0]]
                   ["original_advertised_default_CRS"],"EPSG:28992")
 def test_describe_type_classification_field_recognition(self):
  data=b'''<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <xsd:element name="name" type="xsd:string"/>
      <xsd:element name="ecotope" type="xsd:string"/>
      <xsd:element name="the_geom" type="gml:MultiPolygonPropertyType"/>
      </xsd:schema>'''
  a=s.wfs_schema(data,s.LAYER_IDS[0])
  self.assertIn("ecotope",a["possible_classification_fields"])
  self.assertEqual(a["field_count"],3)
if __name__=="__main__": unittest.main()
