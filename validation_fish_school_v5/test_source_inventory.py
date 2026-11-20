import unittest
from source_inventory import zenodo_metadata,osf_metadata,safe_get
class InventoryTests(unittest.TestCase):
 def test_zenodo_real_file_fields_known_truth(self):
  fake=lambda url:{"id":10890112,"metadata":{"title":"Tracks"},"files":[
   {"key":"tracks.zip","size":3000,"checksum":"md5:aaa","links":{"self":"https://zenodo.org/api/files/ok"}}]}
  a=zenodo_metadata(fake)
  self.assertEqual(a["original_file_count"],1)
  self.assertFalse(a["movement_data_opened"])
 def test_no_files_not_admitted(self):
  self.assertEqual(safe_get(lambda:zenodo_metadata(lambda u:{"files":[]}))["status"],"SOURCE_METADATA_STOP")
 def test_invalid_traversal(self):
  self.assertEqual(safe_get(lambda:zenodo_metadata(lambda u:{"files":[{"key":"../bad","size":1}]}))["status"],"SOURCE_METADATA_STOP")
 def test_osf_storage_manifest(self):
  x=osf_metadata(lambda u:{"data":[{"attributes":{"name":"osfstorage"},
            "relationships":{"files":{"links":{"related":{"href":"https://api.osf.io/v2/files/xxx/"}}}}}]})
  self.assertEqual(x["storage_provider_count"],1)
  self.assertFalse(x["file_outcomes_opened"])
if __name__=="__main__":unittest.main()
