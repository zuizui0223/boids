import json
import unittest
from pathlib import Path
import numpy as np
import emergent_preferences as m
import social_influence_scan as sc
import crossover_audit_v12 as cr
import grain_audit_v12 as ga

ROOT=Path(__file__).resolve().parent/'results'

class TestStrengthAndGrain(unittest.TestCase):
    def test_zero_social_strength_matches_no_social_input(self):
        a=next(c for c in m.CONDITIONS if c.name=='learning_plus_social')
        b=next(c for c in m.CONDITIONS if c.name=='private_learning_plus_boids')
        out0=m.simulate(a,17,social_strength=0.)
        out1=m.simulate(b,17)
        np.testing.assert_array_equal(out0['xyz'],out1['xyz'])
    def test_different_strength_invalid(self):
        a=next(c for c in m.CONDITIONS if c.name=='learning_plus_social')
        with self.assertRaisesRegex(ValueError,'Invalid social'):
            m.simulate(a,17,social_strength=-1.)
    def test_crossing_is_interpolated(self):
        self.assertAlmostEqual(cr.crossing([0,.5,1],[-1,1,1]),.25)
        self.assertIsNone(cr.crossing([0,.5,1],[-1,-.5,-.2]))
    def test_frozen_receipt_strength_crossing_in_range(self):
        rec=json.loads((ROOT/'social_influence_scan_v12.json').read_text())
        c=cr.audit(rec,draws=100)
        self.assertGreater(c['estimated_gain_crossover'],.25)
        self.assertLess(c['estimated_gain_crossover'],.75)
    def test_strength_scan_preserves_seed_paired_replicates(self):
        x=sc.scan(seeds=3,strengths=(0.,.5,1.))
        self.assertEqual(len(x['seeds']),3)
        self.assertEqual(len(x['worlds']),3)
    def test_fine_grain_contains_more_categories(self):
        self.assertGreater(np.prod([len(m.FINE_GRAIN[d])+1 for d in ('x','y','z')]),
                           np.prod([len(m.PRIMARY_GRAIN[d])+1 for d in ('x','y','z')]))
    def test_group_z_forecast_stable_across_two_grains_in_receipt(self):
        x=json.loads((ROOT/'grain_audit_v12.json').read_text())
        for k in ('coarse','fine'):
            self.assertGreater(x['results']['learning_plus_social'][k]['guild_z_heldout'],.08)
            self.assertLess(x['results']['learning_mixed_species_social'][k]['guild_z_heldout'],.03)

if __name__=='__main__':unittest.main()
