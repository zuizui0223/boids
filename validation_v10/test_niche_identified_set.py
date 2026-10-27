"""Finite candidate-set 3D use and information-metric test contracts."""
import unittest
import numpy as np

from niche_identified_set import (
    ALPHAS, SOURCE_DISTANCE_M, KAPPA0_PER_S2, N_AGENTS, GRAINS, WORLDS,
    gamma, effective_coefficient, targets_and_initial_positions, simulate,
    categorical_uses, mutual_information_equal_groups, ecological_metrics,
    conditional_z_thickness, metric_envelopes, joint_species_state,
    total_variation, experiment,
)


class TestKnownTruthNiche(unittest.TestCase):
    def test_all_source_social_steering_values_equal(self):
        vals=[effective_coefficient(a,SOURCE_DISTANCE_M) for a in ALPHAS]
        for v in vals: self.assertAlmostEqual(v,KAPPA0_PER_S2,places=14)
        self.assertEqual(len(set(gamma(a) for a in ALPHAS)),len(ALPHAS))

    def test_source_spacing_3d_geometry(self):
        for world in WORLDS.values():
            targets,pos=targets_and_initial_positions(world)
            self.assertEqual(pos.shape,(N_AGENTS,3))
            self.assertEqual(targets.shape,(N_AGENTS,3))
            for j in range(0,N_AGENTS,2):
                self.assertAlmostEqual(np.linalg.norm(pos[j+1]-pos[j]),world['initial_pair_distance_m'])

    def test_no_social_force_is_invariant_to_alpha_with_common_random_numbers(self):
        a=simulate(WORLDS['novel_spacing_shared_resources'],ALPHAS[0],123,
                   social_on=False,steps=320,burn_in=90)
        b=simulate(WORLDS['novel_spacing_shared_resources'],ALPHAS[-1],123,
                   social_on=False,steps=320,burn_in=90)
        np.testing.assert_array_equal(a,b)

    def test_synthetic_replay_is_exact(self):
        a=simulate(WORLDS['novel_spacing_reassembled_resources'],ALPHAS[2],5,
                   steps=320,burn_in=90)
        b=simulate(WORLDS['novel_spacing_reassembled_resources'],ALPHAS[2],5,
                   steps=320,burn_in=90)
        np.testing.assert_array_equal(a,b)

    def test_same_noise_different_social_force_changes_trajectory(self):
        a=simulate(WORLDS['novel_spacing_shared_resources'],ALPHAS[0],5,steps=320,burn_in=90)
        b=simulate(WORLDS['novel_spacing_shared_resources'],ALPHAS[-1],5,steps=320,burn_in=90)
        self.assertGreater(np.max(np.abs(a-b)),1e-3)

    def test_every_observation_including_tails_is_counted_once(self):
        obs=np.ones((8,N_AGENTS,3))*5000
        p=categorical_uses(obs,GRAINS['coarse'])
        self.assertEqual(p.shape,(N_AGENTS,4,4,4))
        np.testing.assert_array_equal(p[:,-1,-1,-1],np.ones(N_AGENTS))
        np.testing.assert_allclose(p.sum(axis=(1,2,3)),np.ones(N_AGENTS))

    def test_shared_support_metric_is_zero_under_identical_species(self):
        same=np.ones((N_AGENTS,2,2,2),float)/8
        m=ecological_metrics(same)
        self.assertAlmostEqual(m['species_horizontal_information_nats'],0)
        self.assertAlmostEqual(m['species_vertical_information_given_xy_nats'],0)
        self.assertAlmostEqual(m['within_species_individual_vertical_information_given_xy_nats'],0)
        self.assertAlmostEqual(m['species_horizontal_bhattacharyya_overlap'],1)
        self.assertAlmostEqual(m['effective_vertical_states_given_xy'],2)

    def test_vertical_partition_is_conditional_not_horizontal(self):
        p=np.zeros((N_AGENTS,2,2,2),float)
        p[:6,:,:,0]=.25
        p[6:,:,:,1]=.25
        m=ecological_metrics(p)
        self.assertAlmostEqual(m['species_horizontal_information_nats'],0,places=11)
        self.assertAlmostEqual(m['species_vertical_information_given_xy_nats'],np.log(2),places=11)

    def test_horizontal_partition_is_not_vertical_partition(self):
        p=np.zeros((N_AGENTS,2,2,2),float)
        p[:6,0,:,0]=.25;p[:6,0,:,1]=.25
        p[6:,1,:,0]=.25;p[6:,1,:,1]=.25
        m=ecological_metrics(p)
        self.assertAlmostEqual(m['species_horizontal_information_nats'],np.log(2),places=11)
        self.assertAlmostEqual(m['species_vertical_information_given_xy_nats'],0,places=11)

    def test_grain_changes_information_not_sign_by_definition(self):
        obs=simulate(WORLDS['source_spacing_shared_resources'],ALPHAS[1],7,steps=350,burn_in=90)
        cs=categorical_uses(obs,GRAINS['coarse'])
        fs=categorical_uses(obs,GRAINS['fine'])
        self.assertEqual(cs.shape[1:],(4,4,4))
        self.assertEqual(fs.shape[1:],(7,7,7))
        for p in (cs,fs):
            m=ecological_metrics(p)
            self.assertGreaterEqual(m['species_vertical_information_given_xy_nats'],0)
            self.assertGreaterEqual(m['species_horizontal_information_nats'],0)
            self.assertLessEqual(m['species_horizontal_information_nats'],np.log(2)+1e-9)
            self.assertLessEqual(m['species_vertical_information_given_xy_nats'],np.log(2)+1e-9)

    def test_total_variation_bounds_and_zero(self):
        x=np.array([.4,.6]);y=np.array([.7,.3])
        self.assertAlmostEqual(total_variation(x,x),0)
        self.assertAlmostEqual(total_variation(x,y),.3)
        with self.assertRaises(ValueError):total_variation(x,np.array([.8,.8]))

    def test_envelope_is_zero_for_identical_candidate_distributions(self):
        p=np.ones((N_AGENTS,2,2,2),float)/8
        summary=metric_envelopes({0.:p,1.:p})
        self.assertAlmostEqual(summary['maximum_joint_species_xyz_total_variation'],0)
        self.assertTrue(all(abs(v['width'])<1e-11 for v in summary['metric_ranges'].values()))

    def test_summary_reports_finite_set_only(self):
        out=experiment(seeds=2,alphas=(0.,2.),steps=310,burn_in=90,
                       worlds={'pilot':WORLDS['novel_spacing_shared_resources']})
        self.assertEqual(out['status'],'SYNTHETIC_CANDIDATE_SET_PROPAGATION_NOT_OBSERVED_ECOLOGICAL_FORECAST')
        self.assertEqual(out['simulation']['seeds'],[20261028,20261029])
        self.assertEqual(len(out['worlds']['pilot']['grains']),2)
        self.assertLessEqual(out['worlds']['pilot']['grains']['coarse']['maximum_joint_species_xyz_total_variation'],1.)
        self.assertNotIn('observed_gps',out)


if __name__=='__main__':unittest.main()
