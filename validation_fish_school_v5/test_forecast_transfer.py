import unittest
import numpy as np
from forecast_transfer import group_vectors,make_trial,SourceStop,assess
class ForecastFixtures(unittest.TestCase):
 def test_group_vector_dimensions(self):
  rng=np.random.default_rng(20);p=rng.uniform(0,100,size=(5,8,2))
  v=rng.normal(size=(5,8,2))
  a=group_vectors(p,v)
  self.assertEqual(a.shape,(5,8,10))
  self.assertTrue(np.isfinite(a).all())
 def test_isolated_school_social_zero(self):
  p=np.array([[[float(i*100),0.] for i in range(8)]])
  v=np.zeros_like(p)
  x=group_vectors(p,v)
  self.assertTrue(np.allclose(x,0))
 def test_exact_time_target_support(self):
  n=4000
  frame=np.arange(n,dtype=float)
  base=np.linspace(10,80,8)[None,:,None]
  t=np.arange(n)[:,None,None]
  p=np.zeros((n,8,2))
  p[:,:,0]=base[:,:,0]+.01*t[:,:,0]
  p[:,:,1]=np.linspace(10,80,8)[None,:]
  x=make_trial(frame,p,0)
  self.assertGreater(x["observations"],3000)
  self.assertEqual(x["X"]["boids"].shape[1]-x["X"]["self"].shape[1],7)
  self.assertEqual(x["X"]["speed_selective"].shape[1]-x["X"]["self"].shape[1],10)
 def test_missing_frame_gates(self):
  n=4000;frame=np.arange(n,dtype=float);frame[1000:]+=1
  p=np.zeros((n,8,2))
  p[:,:,0]=np.arange(n)[:,None]*.01+np.arange(8)[None,:]
  x=make_trial(frame,p,0)
  self.assertGreater(x["observations"],3000)
 def test_independent_trial_requirement(self):
  with self.assertRaises(SourceStop):assess({})
if __name__=="__main__":unittest.main()
