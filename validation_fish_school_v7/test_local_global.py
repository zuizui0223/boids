import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
from local_global import panels,SourceStop
class TestLocalGlobal(unittest.TestCase):
    def setUp(self):
        n=12*8
        own=np.zeros((n,13))
        block=np.zeros((n,7))
        ghost=np.zeros((n,7))
        self.d={"X":{"self":own,"boids":np.concatenate((own,block),axis=1),
                     "stale_school":np.concatenate((own,ghost),axis=1)}}
    def test_correct_dimensions(self):
        p=panels(self.d)
        self.assertEqual({k:v.shape[1] for k,v in p.items()},
             {"own":13,"geometry":18,"geometry_global":20,
              "geometry_local":20,"geometry_global_local":22,"geometry_stale_local":20})
    def test_same_speed_all_fish_has_zero_global_relative(self):
        self.d["X"]["self"][:,2:4]=[4.,3.]
        x=panels(self.d)
        self.assertTrue(np.allclose(x["geometry_global"][:,-2:],0))
    def test_known_one_fast_fish_global_other(self):
        self.d["X"]["self"][:,2]=np.tile(np.array([7.,0.,0.,0.,0.,0.,0.,0.]),12)
        x=panels(self.d)
        arr=x["geometry_global"][:,-2:].reshape(-1,8,2)
        self.assertAlmostEqual(arr[0,0,0],-7.)
        self.assertAlmostEqual(arr[0,1,0],1.)
    def test_stale_speed_is_distinct_feature_slot(self):
        self.d["X"]["stale_school"][:,15:17]=[2.,3.]
        x=panels(self.d)
        np.testing.assert_array_equal(x["geometry_stale_local"][:,-2:],
                                      self.d["X"]["stale_school"][:,15:17])
    def test_bad_schema_stop(self):
        self.d["X"]["self"]=np.zeros((12,13))
        with self.assertRaises(SourceStop):panels(self.d)
if __name__=="__main__":unittest.main()
