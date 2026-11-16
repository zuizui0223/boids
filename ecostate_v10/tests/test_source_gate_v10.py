import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import source_gate_v10 as x
class Tests(unittest.TestCase):
    def test_doi_exact(self):self.assertEqual(x.DOI,'10.5061/dryad.b8gtht7tf')
    def test_https_only(self):
        for url in ('http://datadryad.org/api/v2','https://evil.test/file','https://datadryad.org.evil.test/'):
            with self.assertRaises(ValueError):x.trusted(url)
    def test_nested_hal_matching(self):
        a={'_embedded':{'stash:files':[{'filename':'data_for_model.rds','id':45}, {'filename':'README.md','id':46}]}}
        self.assertEqual(x.walk_embedded(a),[{'filename':'data_for_model.rds','id':45}])
    def test_version_link(self):self.assertEqual(x.hrefs({'_links':{'stash:version':{'href':'/api/v2/versions/9'}}}),['/api/v2/versions/9'])
    def test_not_reading_csv_rds(self):
        import inspect
        s=inspect.getsource(x)
        for forbidden in ('pyreadr','pandas.read_csv','pickle.load','rdata.load','read_rds('):self.assertNotIn(forbidden,s)
if __name__=='__main__':unittest.main()
