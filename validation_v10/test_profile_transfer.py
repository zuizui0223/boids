"""Out-of-seed equal-individual conditional state-prediction tests."""
import unittest
import numpy as np
from niche_identified_set import N_AGENTS
from profile_transfer import heldout_seed_vertical_gain


class TestHeldoutProfile(unittest.TestCase):
    def test_identical_individuals_have_no_gain(self):
        a=np.full((4,N_AGENTS,2,2,2),1./8.)
        r=heldout_seed_vertical_gain(a,50)
        self.assertAlmostEqual(r['mean_heldout_self_minus_pooled_nats_per_fix'],0)
        self.assertAlmostEqual(r['mean_xy_supported_fraction'],1)

    def test_stable_individual_profiles_predict_new_synthetic_seed(self):
        cube=np.zeros((4,N_AGENTS,2,2,2),float)
        for i in range(N_AGENTS):
            # Opposite z preferences within each simulated species, and same xy.
            cube[:,i,:,:,i%2]=.25
        r=heldout_seed_vertical_gain(cube,80)
        self.assertGreater(r['mean_heldout_self_minus_pooled_nats_per_fix'],.1)
        self.assertEqual(r['positive_heldout_seeds'],4)

    def test_missing_training_xy_support_fails_closed(self):
        cube=np.zeros((3,N_AGENTS,2,2,2),float)
        cube[0,:,:,0,0]=.5
        cube[1,:,:,1,0]=.5
        cube[2,:,:,0,0]=.5
        with self.assertRaisesRegex(ValueError,'STOP_NO_SHARED_HORIZONTAL_SUPPORT'):
            heldout_seed_vertical_gain(cube,10)

    def test_zero_pseudocount_refused(self):
        arr=np.full((3,N_AGENTS,2,2,2),.125)
        with self.assertRaises(ValueError):heldout_seed_vertical_gain(arr,50,pseudo=0)


if __name__=='__main__':unittest.main()
