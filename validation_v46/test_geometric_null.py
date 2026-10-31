"""Invented heading geometry only; no raw original wild GPS or tides."""
import unittest
import numpy as np
import geometric_null as m

class KnownTruth(unittest.TestCase):
 def test_frozen_support_and_permutation_counts(self):
    self.assertEqual((m.N_BIRDS,m.N_STEPS,m.SHAMS,m.BOOTS),(17,4660,1000,10000))
 def test_geometric_mean_regression_of_symmetric_left_right_turn(self):
    before=np.tile([1.,0.],(2,1))
    after=np.array([[0.,1.],[0.,-1.]])
    near=np.tile([1.,0.],(2,1))
    far=np.tile([0.,1.],(2,1))
    x,B,c=m.geometry(before,after,near,far)
    self.assertAlmostEqual(x[:,4].mean(),-1.)
    self.assertAlmostEqual(x[:,3].mean(),-1.)
    self.assertAlmostEqual(x[:,0].mean(),0.)
 def test_exact_single_turn_source_decomposition(self):
    b=np.array([[1.,0.]])
    a=np.array([[0.,1.]])
    n=np.array([[1.,0.]])
    f=np.array([[0.,1.]])
    mtx,B,c=m.geometry(b,a,n,f)
    self.assertAlmostEqual(mtx[0,4],-2.)
    self.assertAlmostEqual(mtx[0,3],-1.)
    self.assertAlmostEqual(mtx[0,0],-1.)
    self.assertAlmostEqual(mtx[0,1]-mtx[0,2],-1.)
 def test_zero_turn_no_excess(self):
    b=np.array([[0.,1.]])
    mtx,_,_=m.geometry(b,b,b,np.array([[1.,0.]]))
    self.assertTrue(np.allclose(mtx,0.))
 def test_all_perbird_real_source_geometric_identities(self):
    b=np.array([[1.,0.],[0.,1.]])
    a=np.array([[.6,.8],[-.8,.6]])
    n=np.array([[0.,1.],[1.,0.]])
    f=np.array([[1.,0.],[0.,1.]])
    mtx,_,_=m.geometry(b,a,n,f)
    self.assertTrue(np.allclose(mtx[:,0],mtx[:,1]-mtx[:,2]))
    self.assertTrue(np.allclose(mtx[:,4],mtx[:,3]+mtx[:,0]))
 def test_nonfinite_or_wrongshape_fails(self):
    with self.assertRaises(ValueError):m.geometry(np.array([[np.nan,0.]]),np.array([[1.,0.]]),np.array([[0.,1.]]),np.array([[1.,0.]]))
    with self.assertRaises(ValueError):m.geometry(np.ones((1,3)),np.ones((1,3)),np.ones((1,3)),np.ones((1,3)))
 def test_bird_equalweight_bootstrap(self):
    d=np.array([[0,1],[0,0],[1,1]])
    result=m.bootstrap([2.,-1.],d)
    self.assertAlmostEqual(result["equal_whole_bird_mean"],.5)
    self.assertEqual(result["positive_birds"],1)
 def test_1000_symmetric_hand_shams_average_near_zero(self):
    N=200
    b=np.tile([1.,0.],(N,1))
    n=np.tile([0.,1.],(N,1))
    f=np.tile([1.,0.],(N,1))
    q=m.symmetric_handedness_sham(b,np.zeros(N),n,f,{0:np.arange(100),1:np.arange(100,200)})
    self.assertEqual(q["sham_repetitions"],1000)
    self.assertLess(abs(q["mean_sham_C_NF_GEOMETRIC_EXCESS"]),.1)
 def test_original_v45_complete_source_receipt_mandatory(self):
    import inspect
    x=inspect.getsource(m.original_replay)
    self.assertIn("oldv.evaluate",x)
    self.assertIn("OLD.read_text",x)
    self.assertIn("1e-12",x)
 def test_stop_when_original_birds_missing_no_effect(self):
    res=m.score({},np.array([],dtype=int),np.empty((0,2)),np.empty((0,2)),np.empty((0,2)),np.empty((0,2)),{},np.array([],dtype=int),{})
    self.assertEqual(res["status"],"NOT_ADMITTED_GPS_GEOMETRIC_SYMMETRIC_TURN_NULL")
    self.assertFalse(res["any_new_effect_reported"])
if __name__=="__main__":unittest.main()
