"""Pure source-only provider and shapefile fixtures, never original animal data."""
import unittest
import io
import zipfile
from pathlib import Path
import source_only as s

class OriginalSourceKnownTruth(unittest.TestCase):
 def test_exact_zenodo_and_baptist_derived_file(self):
  self.assertEqual(s.RECORD,14535985)
  self.assertEqual(s.PUBLISHED_MD5,"eaa559c9b8401ed4db70b0ef70fe2d7c")
  self.assertEqual(s.DATAFILE,"TidalFlats_UTM32_Baptistetal2019_extended.zip")
 def test_original_source_checksum_strict(self):
  files=[{"key":s.DATAFILE,"size":194400,
         "checksum":"md5:"+s.PUBLISHED_MD5,
         "links":{"content":"https://zenodo.org/api/records/14535985/files/x/content"}}]
  self.assertEqual(s.select_original({"files":files})["size"],194400)
  bad=[dict(files[0],checksum="md5:"+"0"*32)]
  with self.assertRaisesRegex(ValueError,"MD5"):s.select_original({"files":bad})
 def test_reject_untrusted_original_file_domain(self):
  with self.assertRaisesRegex(ValueError,"Zenodo"):
   s.select_original({"files":[{"key":s.DATAFILE,"size":1000,
     "checksum":"md5:"+s.PUBLISHED_MD5,
     "links":{"content":"https://untrusted.example.org/z"}}]})
 def test_zip_bomb_and_traversal_rejected(self):
  with io.BytesIO() as b:
   with zipfile.ZipFile(b,"w") as z:
    z.writestr("../leak.shp",b"123")
   b.seek(0)
   with zipfile.ZipFile(b) as z:
    with self.assertRaisesRegex(ValueError,"ZIP path"):s.safe_members(z)
 def test_exact_polygon_components_required(self):
  with io.BytesIO() as b:
   with zipfile.ZipFile(b,"w") as z:
    z.writestr("one.shp",b"a")
   b.seek(0)
   with zipfile.ZipFile(b) as z:
    with self.assertRaisesRegex(ValueError,"components"):s.inspect_shapefile(z)
 def test_geo_source_gate_never_needs_gps_or_water_level(self):
  self.assertAlmostEqual(s.STATION[0],6.202908)
  self.assertAlmostEqual(s.STATION[1],53.468937)
  import inspect
  self.assertIn("no_animal_GPS_or_tide_values_or_GIS_join_scored", inspect.getsource(s.run))
  self.assertNotIn("forecast as v32", inspect.getsource(s))
if __name__=="__main__":unittest.main()
