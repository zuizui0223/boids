import unittest
import numpy as np
from affine import Affine
from rasterio.io import MemoryFile
from buffalo_field_v11c import circular_options,sample_raster,condloss,make_design

class TestIndependentSameMethod(unittest.TestCase):
    def test_exact_same_start_and_length(self):
        x,y=circular_options(100,100,130,140)
        self.assertEqual(len(x),21)
        self.assertAlmostEqual(x[0],130)
        self.assertAlmostEqual(y[0],140)
        self.assertTrue(np.allclose(np.hypot(x-100,y-100),50))
    def test_no_same_bearing_duplicate(self):
        x,y=circular_options(100,100,140,100)
        self.assertTrue(np.all(np.hypot(x[1:]-140,y[1:]-100)>0.1))
    def test_same_gis_sampling_no_case_leak(self):
        with MemoryFile() as mem:
          with mem.open(driver='GTiff',height=20,width=20,count=1,dtype='float32',crs='EPSG:3112',
                        transform=Affine.translation(0,200)*Affine.scale(10,-10),nodata=-999) as ds:
            ds.write(np.arange(400,dtype='float32').reshape(20,20),1)
            a=sample_raster(ds,np.array([35,35,35]),np.array([165,165,165]))
            self.assertTrue(np.allclose(a,[63,63,63]))
    def test_outside_original_source_is_nan(self):
        with MemoryFile() as mem:
          with mem.open(driver='GTiff',height=10,width=10,count=1,dtype='float32',crs='EPSG:3112',
                        transform=Affine.translation(0,100)*Affine.scale(10,-10),nodata=-999) as ds:
            ds.write(np.ones((10,10),dtype='float32'),1)
            a=sample_raster(ds,np.array([-1,5,120]),np.array([95,95,95]))
            self.assertTrue(np.isnan(a[0]))
            self.assertAlmostEqual(a[1],1)
            self.assertTrue(np.isnan(a[2]))
    def test_conditional_no_effect_reality(self):
        n=3;sizes=np.repeat(21,n);starts=np.arange(n)*21;used=starts
        z=np.zeros((63,3));w=np.full(n,1/n)
        value,grad=condloss(np.zeros(3),z,sizes,starts,used,w)
        self.assertAlmostEqual(value,np.log(21),places=9)
        self.assertTrue(np.allclose(grad,0))
    def test_positive_choice_feature_has_gradient(self):
        sizes=np.array([3,3]);starts=np.array([0,3]);used=starts.copy()
        x=np.array([[1.0],[0.0],[0.0],[1.0],[0.0],[0.0]])
        val,grad=condloss(np.zeros(1),x,sizes,starts,used,np.array([.5,.5]))
        self.assertLess(grad[0],0)
    def test_null_values_not_imputed(self):
        with MemoryFile() as mem:
          with mem.open(driver='GTiff',height=4,width=4,count=1,dtype='float32',crs='EPSG:3112',
                        transform=Affine.translation(0,40)*Affine.scale(10,-10),nodata=-999) as ds:
            a=np.ones((4,4),dtype='float32');a[0,0]=-999;ds.write(a,1)
            val=sample_raster(ds,[5,15],[35,35])
            self.assertTrue(np.isnan(val[0]));self.assertEqual(val[1],1.)
if __name__=='__main__':unittest.main()
