"""Algorithmic unit tests: all outcomes are artificial known-truth worlds."""
import unittest
from dataclasses import replace
import numpy as np
import emergent_preferences as m

class TestSymmetricAgentDynamics(unittest.TestCase):
    def test_candidate_source_equivalence(self):
        self.assertTrue(m.source_equivalence())
        self.assertEqual(len(m.ALPHAS),3)
    def test_identical_innate_preferences(self):
        a=m.simulate(m.CONDITIONS[0],m.SEED_START)
        self.assertTrue(np.array_equal(a['daily_q'],np.zeros_like(a['daily_q'])))
    def test_symmetrical_patch_layout(self):
        self.assertEqual(set(m.PATCHES[:,0]),{-12.,12.})
        self.assertEqual(set(m.PATCHES[:,2]),{-13.,13.})
    def test_sample_choices_replay_exactly(self):
        a=m.sample_categorical(np.random.default_rng(1),np.zeros((12,4)))
        b=m.sample_categorical(np.random.default_rng(1),np.zeros((12,4)))
        np.testing.assert_array_equal(a,b)
    def test_simulated_paths_reproducible(self):
        c=next(c for c in m.CONDITIONS if c.name=='learning_plus_social')
        a=m.simulate(c,13);b=m.simulate(c,13)
        np.testing.assert_array_equal(a['xyz'],b['xyz'])
        np.testing.assert_array_equal(a['choices'],b['choices'])
    def test_no_fixed_personal_target_but_heterogeneous_history(self):
        c=next(c for c in m.CONDITIONS if c.name=='private_learning_only')
        a=m.simulate(c,17)
        self.assertGreater(np.std(a['daily_q'][-1].max(axis=1)),.01)
    def test_all_four_resource_choices_possible(self):
        a=m.simulate(m.CONDITIONS[0],11)
        self.assertEqual(set(np.unique(a['choices'])),set(range(4)))
    def test_invalid_candidate_not_accepted(self):
        with self.assertRaisesRegex(ValueError,'Unknown Boids'):
            m.move(np.zeros((m.N,3)),np.zeros((m.N,3)),np.zeros(m.N,int),np.random.default_rng(1),5.,True)
    def test_history_shuffle_and_reset_not_both(self):
        c=replace(m.CONDITIONS[0],history_shuffle=True,history_reset=True)
        with self.assertRaisesRegex(ValueError,'Incompatible'):
            m.simulate(c,1)

class TestEcologicalMetrics(unittest.TestCase):
    def test_binning_shape(self):
        a=m.simulate(m.CONDITIONS[0],8)
        x=m.categorical_xyz(a['xyz'])
        self.assertEqual(x.shape,a['choices'].shape)
        self.assertGreaterEqual(int(x.min()),0)
        self.assertLess(int(x.max()),m.N*100)
    def test_patch_guild_forecast_uses_future_only_for_score(self):
        train=np.ones((m.TRAIN_DAYS,m.N_BLOCKS-m.BURN_BLOCKS,m.N),int)
        test=np.zeros_like(train)
        a=np.concatenate((train,test))
        g=m.guild_patch_gain(a)
        # All individuals choose the same category within each half; two guilds
        # cannot improve vs a pooled model at any training time.
        self.assertAlmostEqual(g,0.,places=12)
    def test_personal_patch_gain_from_informative_training(self):
        c=np.zeros((m.N_DAYS,m.N_BLOCKS-m.BURN_BLOCKS,m.N),int)
        for i in range(m.N):c[:,:,i]=i%3
        self.assertGreater(m.patch_predictive_gain(c),.15)
        self.assertAlmostEqual(m.guild_patch_gain(c),0.,places=11)
    def test_guild_patch_gain_from_different_learned_habits(self):
        c=np.zeros((m.N_DAYS,m.N_BLOCKS-m.BURN_BLOCKS,m.N),int)
        c[:,:,m.N_PER_SPECIES:]=1
        self.assertGreater(m.guild_patch_gain(c),.50)
    def test_conditional_vertical_info_zero_for_identical_profiles(self):
        p=np.zeros((m.N_DAYS,m.N_BLOCKS-m.BURN_BLOCKS,m.N,3))
        r=m.species_niche_information(p)
        self.assertLess(abs(r['horizontal_information_nats']),1e-12)
        self.assertLess(abs(r['vertical_information_given_xy_nats']),1e-12)
    def test_all_heldout_XY_are_scored(self):
        c=np.zeros((m.N_DAYS,m.N_BLOCKS-m.BURN_BLOCKS,m.N,3))
        c[m.TRAIN_DAYS:,:,:,0]=30.
        # The baseline implementation originally filtered unsupported XY cells.
        # The final algorithm scores them with the declared pseudo count and
        # reports support separately, eliminating selection on test locations.
        gain,support=m.vertical_gain(c)
        self.assertTrue(np.isfinite(gain))
        self.assertEqual(support,0.)
    def test_result_contains_no_measured_animals(self):
        d=m.experiment(seeds=3,conditions=(m.CONDITIONS[0],),alphas=(0.,),n_blocks=12)
        self.assertIn('NOT_WILD_EVIDENCE',d['status'])
        self.assertEqual(len(d['per_seed']),3)

class TestHierarchyShift(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        keys=('neutral','private_learning_only','learning_plus_social','learning_mixed_species_social','learning_social_depletion')
        cls.data={name:[] for name in keys}
        for name in keys:
            c=next(c for c in m.CONDITIONS if c.name==name)
            for seed in range(20261130,20261136):
                cls.data[name].append(m.inspect_single(c,1.,seed))
    def _mean(self,name,key):
        return float(np.mean([z[key] for z in self.data[name]]))
    def test_history_can_generate_personal_habits(self):
        self.assertGreater(self._mean('private_learning_only','patch_identity_gain_nats'),.12)
    def test_social_imitation_generates_group_forecast(self):
        self.assertGreater(self._mean('learning_plus_social','guild_patch_gain_nats'),.12)
    def test_switching_social_partner_mix_abolishes_group_forecast(self):
        self.assertGreater(self._mean('learning_plus_social','guild_patch_gain_nats')-
                           self._mean('learning_mixed_species_social','guild_patch_gain_nats'),.2)
    def test_resource_consumption_hinders_group_lock_in(self):
        self.assertGreater(self._mean('learning_plus_social','guild_patch_gain_nats')-
                           self._mean('learning_social_depletion','guild_patch_gain_nats'),.20)

if __name__=='__main__':unittest.main()
