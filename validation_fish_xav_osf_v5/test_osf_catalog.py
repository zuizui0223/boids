import unittest
from osf_catalog import crawl,START
class CatalogTests(unittest.TestCase):
 def test_recursive_directory(self):
  f=START+"sub/"
  pages={START:{"data":[{"attributes":{"name":"sub","kind":"folder"},
     "relationships":{"files":{"links":{"related":{"href":f}}}}}],"links":{"next":None}},
     f:{"data":[{"attributes":{"name":"x.wav","kind":"file","size":1234},"id":"A"},
                 {"attributes":{"name":"y.mp4","kind":"file","size":500},"id":"B"}],"links":{"next":None}}}
  r=crawl(lambda url:pages[url]);self.assertEqual(r["n_files"],2)
  self.assertEqual(r["n_api_pages"],2)
  self.assertEqual(r["extension_counts"][".wav"],1)
 def test_no_animal_effect(self):
  r=crawl(lambda url:{"data":[],"links":{}})
  self.assertFalse(r["biological_correlation_estimated"])
if __name__=="__main__":unittest.main()
