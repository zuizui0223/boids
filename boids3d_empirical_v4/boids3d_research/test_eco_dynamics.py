"""Fast known-truth and scientific-boundary regression checks."""
import unittest
from dataclasses import replace
import numpy as np
from eco_dynamics import (EcologicalRules,fields,run,state_information,
                          heldout_individual_species_gain)
from validate_ecological_bridge import binned_overlap

class EcologicalDynamicsTests(unittest.TestCase):
    def setUp(self):
        self.base=EcologicalRules(steps=190,burn=70,nights=2,seed=13)

    def test_fields_have_two_resource_types_and_state(self):
        R,E=fields(self.base.shape)
        self.assertEqual(R.shape,(2,*self.base.shape))
        self.assertEqual(E.shape,self.base.shape)
        self.assertTrue(np.all(R>=0))
        self.assertGreater(float(np.std(E)),0)

    def test_no_reachable_state_variation_cannot_buffer(self):
        metrics,*_=run(replace(self.base,state_heterogeneity=0,state_tracking=.85),return_trajectories=True)
        self.assertAlmostEqual(metrics['state_buffering_advantage'],0,places=10)

    def test_private_shared_resources_agree_when_no_depletion(self):
        a,tr1,*_=run(replace(self.base,resource_pool='shared',consumption=0),return_trajectories=True)
        b,tr2,*_=run(replace(self.base,resource_pool='private',consumption=0),return_trajectories=True)
        np.testing.assert_allclose(tr1,tr2,atol=1e-8)

    def test_resource_depletion_modifies_dynamics(self):
        a,tr1,*_=run(replace(self.base,consumption=0),return_trajectories=True)
        b,tr2,*_=run(replace(self.base,consumption=.20),return_trajectories=True)
        self.assertGreater(float(np.linalg.norm(tr1-tr2)),1)
        self.assertLess(b['mean_uptake'],a['mean_uptake'])

    def test_state_transfer_metrics_finite_and_bounded(self):
        m,tr,a,av,g=run(self.base,return_trajectories=True)
        info=state_information(tr,g)
        self.assertGreaterEqual(info['effective_vertical_states'],1)
        self.assertLessEqual(info['effective_vertical_states'],8.001)
        self.assertGreaterEqual(info['species_vertical_partition_information_nats'],-1e-10)
        self.assertEqual(len(info['species_heldout_individual_gain']),14)
        self.assertTrue(all(np.isfinite(info['species_heldout_individual_gain'])))
        for grid in [(4,4,4),(8,8,4),(16,16,8)]:
            res=binned_overlap(tr,g,grid)
            self.assertTrue(0<=res['within']<=1.001)
            self.assertTrue(0<=res['between']<=1.001)

    def test_invalid_pool_fails(self):
        with self.assertRaises(ValueError):run(replace(self.base,resource_pool='neither'))

if __name__=='__main__':unittest.main()
