import unittest
import source_page_audit as p
class Pages(unittest.TestCase):
 def test_next_page_and_dedupe(self):
  a=p.base.BASE+"versions/44/files"
  pages={a:{"_embedded":{"stash:files":[{"id":1,"path":"first.csv"}]},
             "_links":{"next":{"href":"versions/44/files?page=2"}}},
        p.base.BASE+"versions/44/files?page=2":{"_embedded":{"stash:files":[{"id":1,"path":"first.csv"},{"id":2,"path":"q25_autoChorusDetect4.zip"}]}}}
  result,n=p.get_files_with_pages(a,lambda url:pages[url])
  self.assertEqual(n,2)
  self.assertEqual(len(result),2)
 def test_repeated_next_stops(self):
  a=p.base.BASE+"versions/44/files"
  pages={a:{"_embedded":{"stash:files":[]},"_links":{"next":{"href":"versions/44/files"}}}}
  with self.assertRaises(p.base.SourceStop):
   p.get_files_with_pages(a,lambda url:pages[url])
if __name__=="__main__":unittest.main()
