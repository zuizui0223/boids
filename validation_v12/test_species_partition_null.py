import unittest
import numpy as np
import emergent_preferences as m
import species_partition_null as sp

class TestSpeciesRelabelling(unittest.TestCase):
    def test_pair_preserving_partition_count(self):
        self.assertEqual(len(sp.ALL_SPLITS),20)
        self.assertEqual(sp.ACTUAL_SPLIT,(0,1,2))
    def test_neutral_exact_relabel_null_has_expected_exchangeability(self):
        c=next(c for c in m.CONDITIONS if c.name=='neutral')
        a=m.simulate(c,m.SEED_START)
        r=sp.exact_label_audit(a['xyz'])
        self.assertGreaterEqual(r['exact_horizontal_tail_p'],.1-1e-9)
        self.assertEqual(r['n_pair_preserving_assignments'],20)
    def test_relabel_result_deterministic(self):
        c=next(c for c in m.CONDITIONS if c.name=='learning_plus_social')
        a=m.simulate(c,m.SEED_START)
        self.assertEqual(sp.exact_label_audit(a['xyz']),sp.exact_label_audit(a['xyz']))
    def test_identical_agents_zero_mutual_info(self):
        arr=np.ones((2,3))/3.
        self.assertAlmostEqual(sp.mi(arr),0.,places=12)

if __name__=='__main__':unittest.main()
