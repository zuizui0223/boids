import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
from ablate_schooling import layer_matrices,validate_frozen,FROZEN_M0,FROZEN_FULL,FROZEN_FAST
from forecast_transfer import SourceStop

class LayerTests(unittest.TestCase):
    def setUp(self):
        a=np.arange(3*13,dtype=float).reshape(3,13)
        b=np.arange(3*7,dtype=float).reshape(3,7)
        fast=np.arange(3*10,dtype=float).reshape(3,10)
        self.a,self.b=a,b
        self.mock={"X":{"self":a,"boids":np.concatenate((a,b),axis=1),
                        "speed_selective":np.concatenate((a,fast),axis=1)}}
    def test_layers_have_fixed_dimensions(self):
        x=layer_matrices(self.mock)
        self.assertEqual({k:v.shape[1] for k,v in x.items()},
           {"own":13,"separation_only":15,"cohesion_only":16,
            "alignment_only":15,"spatial_only":18,
            "meanfield_no_repulsion":18,"no_cohesion":18,
            "full_boids":20,"faster_neighbor":23})
    def test_geometry_does_not_leak_neighbor_alignment(self):
        x=layer_matrices(self.mock)
        np.testing.assert_array_equal(x["spatial_only"][:,13:],self.b[:,[0,1,4,5,6]])
        np.testing.assert_array_equal(x["alignment_only"][:,13:],self.b[:,[2,3]])
    def test_full_original_is_bitwise_equal(self):
        x=layer_matrices(self.mock)
        np.testing.assert_array_equal(x["full_boids"],self.mock["X"]["boids"])
    def test_frozen_score_requires_replay(self):
        exact={"own":FROZEN_M0[0],"full_boids":FROZEN_FULL[0],
               "faster_neighbor":FROZEN_FAST[0]}
        validate_frozen(exact,0)
        exact["full_boids"]+=.002
        with self.assertRaises(SourceStop):validate_frozen(exact,0)
    def test_different_feature_schema_stops(self):
        mock={"X":{"self":self.a,"boids":np.zeros((3,19)),
                    "speed_selective":np.zeros((3,23))}}
        with self.assertRaises(SourceStop):layer_matrices(mock)
if __name__=="__main__":unittest.main()
