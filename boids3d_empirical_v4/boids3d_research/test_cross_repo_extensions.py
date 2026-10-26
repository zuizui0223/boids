"""Regression checks for the cross-repository research bridge."""
import unittest
from dataclasses import replace
import numpy as np
from eco_dynamics import EcologicalRules,run,state_information
from density_breeding_patch_bridge import BreedingRules,run as run_breeding,effective_components
from synchronous_local_test import sample_local
from overlap_smoothing_audit import spatial_overlap

class CrossRepoExtensions(unittest.TestCase):
    def setUp(self):
        self.base=EcologicalRules(steps=130,burn=50,thin=4,nights=2,seed=17)

    def test_three_pools_are_exactly_equivalent_without_consumption(self):
        tracks=[]
        for pool in ('shared','species','private'):
            _,tr,_,_,_=run(replace(self.base,resource_pool=pool,consumption=0),return_trajectories=True)
            tracks.append(tr)
        np.testing.assert_array_equal(tracks[0],tracks[1])
        np.testing.assert_array_equal(tracks[1],tracks[2])

    def test_three_pools_diverge_with_consumption(self):
        tracks=[]
        for pool in ('shared','species','private'):
            _,tr,_,_,_=run(replace(self.base,resource_pool=pool,consumption=.30),return_trajectories=True)
            tracks.append(tr)
        self.assertGreater(float(np.linalg.norm(tracks[0]-tracks[1])),.01)
        self.assertGreater(float(np.linalg.norm(tracks[1]-tracks[2])),.01)

    def test_horizontal_and_vertical_information_are_distinct(self):
        groups=np.repeat(np.arange(2),7)
        tr=np.zeros((3,14,24,3));tr[:,:,:,2]=2
        tr[:,groups==0,:,0]=2
        tr[:,groups==1,:,0]=10
        data=state_information(tr,groups)
        self.assertGreater(data['species_horizontal_partition_information_nats'],.65)
        self.assertAlmostEqual(data['species_vertical_partition_information_nats'],0,places=9)
        tr[:,:,:,0]=2
        tr[:,groups==1,:,2]=5
        data=state_information(tr,groups)
        self.assertAlmostEqual(data['species_horizontal_partition_information_nats'],0,places=9)
        self.assertGreater(data['species_vertical_partition_information_nats'],.65)

    def test_absent_synchronous_neighbours_returns_missing_not_zero(self):
        group=np.repeat(np.arange(2),7)
        track=np.zeros((2,14,20,3))
        track[:,group==0,:,0]=2
        track[:,group==1,:,0]=10
        results=sample_local(track,group,dxy_max=2)
        self.assertIsNone(results['heterospecific']['mean_nearby_absolute_height_difference'])
        self.assertEqual(results['heterospecific']['eligible_pairs'],0)

    def test_no_smoothing_and_large_prior_yield_different_sparse_overlap(self):
        group=np.repeat(np.arange(2),7)
        track=np.zeros((2,14,20,3))
        track[:,group==0,:,0]=2
        track[:,group==1,:,0]=10
        sparse=spatial_overlap(track,group,(16,16,8),0)
        smoothed=spatial_overlap(track,group,(16,16,8),.06)
        self.assertAlmostEqual(sparse['between'],0,places=10)
        self.assertGreater(smoothed['between'],.1)

    def test_demography_observation_and_fixed_total_null(self):
        out=run_breeding(BreedingRules(n_patches=6,n_years=4,initial_n=90,
               final_n=20,seed=7,n_null=49,crowding_strength=2))
        self.assertEqual(len(out['annual_expected_totals']),4)
        self.assertEqual(sum(out['annual_simulated_latent_counts'][0]),90)
        self.assertEqual(sum(out['annual_simulated_latent_counts'][-1]),20)
        self.assertTrue(0<out['lower_tail_p']<=1)
        self.assertTrue(all(1<=v<=6 for v in out['annual_observed_effective_components']))
        self.assertAlmostEqual(effective_components([5,5,0,0]),2)

if __name__=='__main__': unittest.main()
