import unittest
import numpy as np
from assignment_and_delay import rotate_other_velocities,local_vectors,build,SourceStop,ROTATIONS

class AssignmentFixtures(unittest.TestCase):
 def setUp(self):
    self.vel=np.zeros((3,8,2),float)
    self.vel[:,:,0]=np.arange(8)[None,:]
    self.mask=np.zeros((3,8,8),bool)
    self.mask[:,:,1]=True
    self.mask[:,1,1]=False
 def test_true_sum_of_other_velocities_preserved(self):
    v=self.vel
    for i in range(8):
       other=[j for j in range(8) if j!=i]
       for shift in ROTATIONS:
          s=np.roll(v[:,other,:],shift,axis=1)
          np.testing.assert_allclose(s.sum(axis=1),v[:,other,:].sum(axis=1))
 def test_fixed_member_assignment_changes_local(self):
    m=self.mask
    a=rotate_other_velocities(self.vel,m,1)
    b=rotate_other_velocities(self.vel,m,3)
    self.assertEqual(a.shape,self.vel.shape)
    self.assertFalse(np.allclose(a,b))
 def test_all_seven_neighbors_is_assignment_invariant(self):
    mask=np.ones((3,8,8),dtype=bool)
    mask[:,np.arange(8),np.arange(8)]=False
    a=rotate_other_velocities(self.vel,mask,1)
    b=rotate_other_velocities(self.vel,mask,3)
    np.testing.assert_allclose(a,b,rtol=0,atol=1e-12)
 def test_isolated_fish_yield_zero(self):
    z=rotate_other_velocities(self.vel,np.zeros_like(self.mask),1)
    self.assertTrue(np.allclose(z,0.))
 def test_unknown_rotation_fails(self):
    with self.assertRaises(ValueError):rotate_other_velocities(self.vel,self.mask,5)
 def test_mask_shape_stop(self):
    with self.assertRaises(SourceStop):rotate_other_velocities(self.vel,np.ones((3,7,8)),1)
 def test_native_alignment_known_truth(self):
    n=500;frame=np.arange(n,dtype=float)
    p=np.zeros((n,8,2),float)
    for i in range(8):
       p[:,i,0]=i*.8 + .1*frame
       p[:,i,1]=i*.4 + .02*(i+1)*frame
    idx=np.arange(120,n-40,10)
    v,m,al,c=local_vectors(p,frame,idx)
    self.assertEqual(al.shape,(len(idx),8,2))
    self.assertEqual(m.shape,(len(idx),8,8))
    self.assertTrue(np.isfinite(al).all())
if __name__=="__main__":unittest.main()
