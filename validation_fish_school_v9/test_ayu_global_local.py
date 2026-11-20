import tempfile,unittest
import numpy as np
from ayu_global_local import source_data,features,SourceStop
from ayu_source_gate import blobsha
class TestAyuOutOfSource(unittest.TestCase):
 def synthetic(self,n=1800):
    a=np.zeros((n,22))
    a[:,0]=np.arange(n)+1
    a[:,1]=np.round(np.arange(n)/30,2)
    for k in range(10):
       a[:,2+k]=20+2*k+.8*np.arange(n)+.7*np.sin(np.arange(n)/30+k)
       a[:,12+k]=50+3*k+.6*np.arange(n)+.5*np.cos(np.arange(n)/40+k)
    return a
 def test_fixed_feature_dimensions_and_targets(self):
    d=self.synthetic()
    pos=np.stack((d[:,2:12],d[:,12:22]),axis=-1)
    x=features(pos)
    self.assertEqual(x["X"]["G_global"].shape[1]-x["X"]["G_geometry"].shape[1],2)
    self.assertEqual(x["X"]["G_both"].shape[1]-x["X"]["G_geometry"].shape[1],4)
    self.assertEqual(x["X"]["G_global_ghost3"].shape,x["X"]["G_both"].shape)
    self.assertEqual(x["Y"]["short"].shape,x["Y"]["delayed"].shape)
 def test_global_preserved_under_ghost_feature_design(self):
    d=self.synthetic()
    pos=np.stack((d[:,2:12],d[:,12:22]),axis=-1)
    x=features(pos)
    np.testing.assert_array_equal(x["X"]["G_global"],
                                   x["X"]["G_global_ghost3"][:,:-2])
 def test_source_time30fps_not20(self):
    d=self.synthetic(6100)
    with tempfile.TemporaryDirectory() as tmp:
       from pathlib import Path
       p=Path(tmp)/"a.txt";np.savetxt(p,d,fmt="%.8f")
       raw=p.read_bytes()
       frame,sec,pos=source_data(p,blobsha(raw),len(raw))
       self.assertEqual(pos.shape,(6100,10,2))
       self.assertAlmostEqual((frame[-1]-frame[0])/(sec[-1]-sec[0]),30.,delta=.01)
 def test_wrong_20fps_time_rejected(self):
    d=self.synthetic(6100)
    d[:,1]=np.round(np.arange(6100)/20,2)
    with tempfile.TemporaryDirectory() as tmp:
       from pathlib import Path
       p=Path(tmp)/"a.txt";np.savetxt(p,d,fmt="%.8f")
       raw=p.read_bytes()
       with self.assertRaises(SourceStop):source_data(p,blobsha(raw),len(raw))
if __name__=="__main__":unittest.main()
