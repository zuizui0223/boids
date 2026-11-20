import tempfile, unittest
from pathlib import Path
import numpy as np
from source_semantics import one_source,SourceStop
from ayu_source_gate import blobsha
class TestSourceSemantic(unittest.TestCase):
 def test_author_column_x_y_and_untouched_two(self):
    a=np.arange(6000*22,dtype=float).reshape(6000,22)
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"a.txt";np.savetxt(p,a)
        b=p.read_bytes()
        x=one_source(p,blobsha(b),len(b))
        self.assertEqual(x["columns"],22)
        self.assertEqual(x["x_range"][0],2.)
        self.assertEqual(x["y_range"][0],12.)
 def test_wrong_blob_fails(self):
    with tempfile.TemporaryDirectory() as d:
       p=Path(d)/"a.txt";p.write_text("2 3")
       with self.assertRaises(SourceStop):one_source(p,"0"*40,3)
 def test_missing_columns_fails(self):
    a=np.zeros((5001,20))
    with tempfile.TemporaryDirectory() as d:
       p=Path(d)/"a.txt";np.savetxt(p,a)
       with self.assertRaises(SourceStop):one_source(p,blobsha(p.read_bytes()),len(p.read_bytes()))
if __name__=="__main__":unittest.main()
