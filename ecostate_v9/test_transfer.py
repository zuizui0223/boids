import unittest,sys
import numpy as np
from bear_transfer_v9 import conditional_nll,FEATURES,MD5,SHA256,MIN_CAND,MIN_BEAR
class Test(unittest.TestCase):
 def test_types(self):
  self.assertEqual(len(SHA256),64);self.assertEqual(len(MD5),32)
 def test_explicit_start_missing(self):
  self.assertNotIn('origin_state',sum(FEATURES.values(),[]))
 def test_same_used_event(self):
  x=np.array([[0.0],[1.0],[2.0],[1.0],[0.0],[2.0]])
  ns=np.array([3,3]);st=np.array([0,3]);used=np.array([2,3]);w=np.array([0.5,0.5])
  a=conditional_nll(np.array([0.3]),x,ns,st,used,w,deriv=True)
  self.assertAlmostEqual(a[0],conditional_nll(np.array([0.3]),x,ns,st,used,w),places=9)
 def test_finite_gradient(self):
  x=np.array([[0.],[1.],[2.],[1.],[0.],[2.]])
  ns=np.array([3,3]);st=np.array([0,3]);used=np.array([2,3]);w=np.array([.5,.5]);beta=np.array([.5]);eps=1e-5
  loss,gradient=conditional_nll(beta,x,ns,st,used,w,deriv=True)
  diff=(conditional_nll(beta+eps,x,ns,st,used,w)-conditional_nll(beta-eps,x,ns,st,used,w))/(2*eps)
  self.assertAlmostEqual(gradient[0],diff,places=5)
 def test_no_protected_habitat_assumption(self):
  self.assertNotIn('Protected',str(FEATURES))
 def test_bear_independence_gate(self):self.assertGreaterEqual(MIN_BEAR,15)
if __name__=='__main__':unittest.main()
