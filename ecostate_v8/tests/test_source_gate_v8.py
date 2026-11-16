import sys, pathlib, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import source_gate_v8 as g

class TestSourceOnly(unittest.TestCase):
    def test_identify_archive(self):
        f=g.file_summaries([{'filename':'Field_Margins_Bulbul.zip','size':214000000,'digest':'sha256:abc','id':1}])
        self.assertEqual(f[0]['name'],g.BULBUL_ARCHIVE)
        self.assertEqual(f[0]['size'],214000000)
    def test_reject_non_object_response(self):
        self.assertEqual(g.file_summaries(['not-object',{},1]),[{'name':'','size':None,'checksum':None,'file_id':None,'has_download_link':False}])
    def test_no_response_data_in_functions(self):
        for name in ('dryad_gate','usgs_gate'):
            import inspect
            code=inspect.getsource(getattr(g,name))
            self.assertNotIn('openpyxl',code)
            self.assertNotIn('read_csv',code)
    def test_route_identifiers(self):
        self.assertTrue(g.BULBUL_DOI.endswith('wwpzgmsxg'))
        self.assertEqual(g.USGS_ITEM,'62ffeecfd34ed6dc55925915')

if __name__=='__main__':unittest.main()
