"""Source-preserving known-truth tests; no observed species data are used."""
import unittest
import numpy as np
import resource_ablation as m


class TestGenerativeContract(unittest.TestCase):
    def test_source_equivalent_steering(self):
        for alpha in m.ALPHAS:
            self.assertAlmostEqual(float(m.force_coefficient(alpha,m.SOURCE_D)),m.KAPPA0,places=13)

    def test_new_distance_separates_candidate_coefficients(self):
        x=[float(m.force_coefficient(a,25.0)) for a in m.ALPHAS]
        self.assertGreater(max(x)-min(x),0.001)

    def test_initial_positions_are_species_blind(self):
        for contrast in m.SCENARIOS.values():
            target,start=m.targets_and_starts(*contrast)
            np.testing.assert_array_equal(start[:6],start[6:])
            self.assertEqual(target.shape,(m.N_AGENTS,3))

    def test_resource_intervention_changes_only_targets(self):
        x0,s0=m.targets_and_starts(0.,0.)
        xv,sv=m.targets_and_starts(0.,8.)
        xh,sh=m.targets_and_starts(9.,0.)
        np.testing.assert_allclose(s0,sv)
        np.testing.assert_allclose(s0,sh)
        np.testing.assert_allclose(x0[:,:2],xv[:,:2])
        np.testing.assert_allclose(x0[:,2],xh[:,2])

    def test_no_social_alpha_is_irrelevant(self):
        first=m.simulate(9.,8.,m.ALPHAS[0],123,False,steps=70,burn_in=10)
        last=m.simulate(9.,8.,m.ALPHAS[-1],123,False,steps=70,burn_in=10)
        np.testing.assert_array_equal(first,last)

    def test_social_alpha_can_change_trajectory_in_novel_spacing(self):
        first=m.simulate(0.,0.,m.ALPHAS[0],321,True,steps=60,burn_in=10)
        last=m.simulate(0.,0.,m.ALPHAS[-1],321,True,steps=60,burn_in=10)
        self.assertGreater(float(np.max(np.abs(first-last))),1.e-5)

    def test_common_random_numbers_deterministic(self):
        a=m.simulate(0.,8.,1.,420,True,steps=80,burn_in=10)
        b=m.simulate(0.,8.,1.,420,True,steps=80,burn_in=10)
        np.testing.assert_array_equal(a,b)

    def test_invalid_alpha_and_frame_fail(self):
        with self.assertRaisesRegex(ValueError,'STOP_INVALID_EXPERIMENT'):
            m.simulate(0.,0.,3.,123,True,steps=40,burn_in=10)
        with self.assertRaises(ValueError):
            m.simulate(0.,0.,0.,123,True,steps=10,burn_in=20)


class TestEcologicalSummaries(unittest.TestCase):
    def test_3d_probability_mass_conserved(self):
        points=m.simulate(0.,0.,0.,101,False,steps=90,burn_in=10)
        p=m.categorical_probabilities(points,m.GRAINS['coarse'])
        self.assertEqual(p.shape,(12,4,4,4))
        np.testing.assert_allclose(p.sum(axis=(1,2,3)),np.ones(12))

    def test_species_identical_mi_is_zero(self):
        p=np.ones((2,3,2,5))/30
        self.assertAlmostEqual(m.mi_equal_groups(p),0.,places=12)

    def test_split_vertical_observable_mi_ln2(self):
        a=np.zeros((12,4,4,4))
        a[:6,1,1,0]=1.;a[6:,1,1,3]=1.
        out=m.niche_metrics(a)
        self.assertAlmostEqual(out['I_species_XY'],0.,places=12)
        self.assertAlmostEqual(out['I_species_Z_given_XY'],np.log(2),places=12)

    def test_split_horizontal_observable_mi_ln2(self):
        a=np.zeros((12,4,4,4))
        a[:6,0,1,1]=1.;a[6:,3,1,1]=1.
        out=m.niche_metrics(a)
        self.assertAlmostEqual(out['I_species_XY'],np.log(2),places=12)
        self.assertAlmostEqual(out['I_species_Z_given_XY'],0.,places=12)

    def test_total_variation_mass_and_identity(self):
        a=np.zeros((2,3));a[0,0]=1.
        b=np.zeros((2,3));b[1,2]=1.
        self.assertEqual(m.total_variation(a,b),1.)
        self.assertEqual(m.total_variation(a,a),0.)
        with self.assertRaisesRegex(ValueError,'STOP_TV_NORMALIZATION'):
            m.total_variation(a,b*2)

    def test_predictor_scores_true_distribution_higher(self):
        a=np.zeros((2,4,4,4));a[:,1,1,1]=1.
        b=np.zeros_like(a);b[:,3,3,3]=1.
        self.assertGreater(m.overlap_oracle(a,a),m.overlap_oracle(b,a))

    def test_false_label_or_pair_assignment_fails(self):
        a=np.full((12,4,4,4),1./64)
        with self.assertRaisesRegex(ValueError,'STOP_BAD_PAIR_PERMUTATION'):
            m.niche_metrics(a,pair_perm=(1,1,2,3,4,5))

    def test_small_end_to_end_receipt_has_no_wild_claims(self):
        o=m.experiment(seed_ids=m.SEEDS[:10],steps=75,burn_in=15,
            alpha_values=(0.,1.),
            scenario_names=('no_species_resource_contrast','vertical_resource_contrast'),
            grain_names=('coarse',))
        self.assertIn('SYNTHETIC',o['status'])
        self.assertEqual(len(o['niche_by_world']),2)
        self.assertIn('known_environment_vs_blind_forward_scores',o)
        z=o['niche_by_world']['no_species_resource_contrast']['coarse']
        a=z['by_candidate']['social_off']['0.0']
        b=z['by_candidate']['social_off']['1.0']
        self.assertEqual(a,b)

    def test_wrong_seed_count_fails(self):
        with self.assertRaisesRegex(ValueError,'STOP_INVALID_REPLICATION_DESIGN'):
            m.experiment(seed_ids=m.SEEDS[:8])

class TestIndividualMechanismBoundary(unittest.TestCase):
    def test_zero_role_offset_retains_identical_initial_geometry(self):
        t0,x0=m.targets_and_starts(0.,0.,0.)
        t1,x1=m.targets_and_starts(0.,0.,2.5)
        np.testing.assert_array_equal(x0,x1)
        self.assertGreater(np.max(np.abs(t1[:,2]-t0[:,2])),2.)

    def test_no_species_vertical_label_even_with_role_offsets(self):
        t,x=m.targets_and_starts(0.,0.,2.5)
        np.testing.assert_array_equal(t[:6],t[6:])

    def test_simulation_bootstrap_signature(self):
        r=m.experiment(seed_ids=m.SEEDS[:10],steps=70,burn_in=15,
          alpha_values=(0.,1.),
          scenario_names=('no_species_resource_contrast','horizontal_resource_contrast'),
          grain_names=('coarse',))
        self.assertIn('social_on:coarse',r['role_specific_vertical_target_control'])
        self.assertIn('horizontal_resource_contrast:coarse',r['matched_simulation_seed_bootstrap95_alpha1'])
        n=r['role_specific_vertical_target_control']['social_on:coarse']
        self.assertGreater(n['imposed_target_role_offset_individual_information'],0.)
        self.assertGreaterEqual(n['zero_role_target_offset_individual_information'],0.)

if __name__=='__main__': unittest.main()
