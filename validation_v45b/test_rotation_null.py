"""Original-source-free fixed 2D rotation and exact mirror geometry tests."""
import unittest
import json
import inspect
import math
import numpy as np
import rotation_null as m

class KnownTruth(unittest.TestCase):
 def test_fixed_geometric_mirror_protocol_and_inference(self):
    self.assertEqual(m.BOOT,10000)
    self.assertEqual(m.SEED,20261031)
    self.assertEqual(m.MIN_HEIGHT_STRATUM_BIRDS,10)
    self.assertEqual(m.MIN_STRATUM_EPISODES,1000)
    self.assertEqual(m.MEASURES[0],"PRIMARY_NEAR_MINUS_FAR_EXCESS_AFTER_SYMMETRIC_TURN")
 def test_exact_algebra_perpendicular_and_mirror(self):
    prev=np.array([[1.,0.],[1.,0.]])
    after=np.array([[math.cos(.3),math.sin(.3)],
                    [math.cos(.3),-math.sin(.3)]])
    near=np.array([[1.,0.],[1.,0.]])
    far=np.array([[0.,1.],[0.,1.]])
    values,qa=m.rotate_decompose(prev,after,near,far)
    self.assertLess(qa["max_per_episode_mirror_mean_vs_geometric_expectation"],1e-12)
    self.assertTrue(np.allclose(values[:,1],values[:,2]+values[:,0]))
    self.assertAlmostEqual(values[:,0].mean(),0.,places=12)
    self.assertLess(values[:,1].mean(),0.)
 def test_initial_alignment_geometric_negative_with_zero_excess(self):
    theta=.2
    prev=np.array([[1.,0.],[1.,0.]])
    after=np.array([[math.cos(theta),math.sin(theta)],
                    [math.cos(theta),-math.sin(theta)]])
    near=np.array([[1.,0.],[1.,0.]])
    far=np.array([[0.,1.],[0.,1.]])
    val,qa=m.rotate_decompose(prev,after,near,far)
    self.assertGreater(float(np.mean(val[:,3])),0.)
    self.assertLess(float(np.mean(val[:,1])),0.)
    self.assertAlmostEqual(float(np.mean(val[:,0])),0.,places=12)
 def test_heading_inference_not_relabelled_social_force(self):
    s=inspect.getsource(m.run)
    self.assertIn("no_original_bird_ID_position_UTC_GPS_bearing",s)
    self.assertIn("No altitude",s)
 def test_all_input_vector_shapes_checked(self):
    x=np.array([[1.,0.]])
    with self.assertRaisesRegex(ValueError,"shape"):
       m.rotate_decompose(x,np.array([[1.,0.,0.]]),x,x)
 def test_nonunit_previous_direction_rejected(self):
    x=np.array([[.5,0.]])
    y=np.array([[1.,0.]])
    with self.assertRaisesRegex(ValueError,"not unit"):
       m.rotate_decompose(x,y,y,y)
 def test_source_free_bird_bootstrap_controls_sign(self):
    samp=np.array([[0,1],[0,0],[1,1]])
    out=m.bird_boot([.2,-.1],samp)
    self.assertAlmostEqual(out["equal_original_bird_mean"],.05)
    self.assertEqual(out["positive_source_birds"],1)
 def test_correct_previous_sources_mandatory(self):
    self.assertEqual(m.OLD_SOURCE.name,"original_near_far_turning_convergence_v45.json")
    source=inspect.getsource(m.replay_exact_prior_v45_then_keep_vectors)
    self.assertIn("v45.evaluate",source)
    self.assertIn("old.nested_close",source)
    self.assertIn("old_saved",source)
 def test_sham_and_raw_effect_not_replaced_as_primary(self):
    self.assertEqual(m.MEASURES[0],"PRIMARY_NEAR_MINUS_FAR_EXCESS_AFTER_SYMMETRIC_TURN")
    self.assertIn("GEOMETRIC_MIRROR_EXPECTATION",m.MEASURES[2])
 def test_frozen_previous_v45_original_target_stats(self):
    self.assertEqual(m.v45.MIN_MOVEMENT_KM,.05)
    self.assertEqual(m.v45.MIN_OTHER_RESULTANT,.25)
    self.assertEqual(m.v45.MIN_BIRDS,12)
    self.assertEqual(m.MIN_PER_STRATUM_BIRD,10)
 def test_empty_input_does_not_create_animal_effect(self):
    empty=np.empty((0,2))
    x,qa=m.rotate_decompose(empty,empty,empty,empty)
    self.assertEqual(x.shape,(0,7))
    self.assertEqual(qa["max_algebra_error"],0.)
if __name__=="__main__":
    unittest.main()
