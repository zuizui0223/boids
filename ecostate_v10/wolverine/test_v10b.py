import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import source_v10b as x
class Tests(unittest.TestCase):
 def test_expected_original_md5(self):self.assertEqual(x.SOURCE_MD5,'6d694faeadde68fbce1c0b45632aa21c')
 def test_version_lock(self):self.assertEqual(x.REC,'5011732')
 def test_size_guard(self):self.assertTrue(x.MAXBYTES<100_000_000)
 def test_no_animal_effect(self):
  import inspect
  t=inspect.getsource(x)
  self.assertNotIn('predict_proba',t)
  self.assertNotIn('logistic_regression',t)
if __name__=='__main__':unittest.main()
