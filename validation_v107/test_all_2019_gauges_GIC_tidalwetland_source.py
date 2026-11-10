"""v107 fixed original publisher GIC tile-hash shard selection, no wetland value selection."""
import unittest
import all_2019_gauges_GIC_tidalwetland_source as m
from gic2019_real_10km_gauge_buffer import native_expected_tile
from affine import Affine

class NativeAllSourceShardingTruth(unittest.TestCase):
    def test_stable_tile_hash_is_independent_of_gauge_outcome(self):
        t='gic-2019-v1-0/v1-0-1/murray-gic-v1.0.1-twprobabilityEnd-0000000000-0000000000.tif'
        self.assertEqual(m.assigned_source_shard(t,1),m.assigned_source_shard(t,200))
        self.assertIn(m.assigned_source_shard(t,1),range(16))
        self.assertEqual(m.assigned_source_shard(None,39),39%16)
    def test_global_native_grid_selection_fixed_without_tide_score(self):
        aff=Affine(.0002695,0,-180.000015,0,-.0002695,60.000005)
        same1=native_expected_tile(53.,6.,aff)
        same2=native_expected_tile(52.5,6.5,aff)
        self.assertEqual(same1['native_GCS_tile_name'],same2['native_GCS_tile_name'])
        self.assertEqual(m.assigned_source_shard(same1['native_GCS_tile_name'],12),
                         m.assigned_source_shard(same2['native_GCS_tile_name'],77))
    def test_predeclared_full_original_source_expected(self):
        self.assertEqual(m.SHARD_COUNT,16)
        self.assertEqual(m.ORIGINAL_SOURCE_STATIONS,160)
        self.assertEqual(m.ORIGINAL_CANDIDATE_STATIONS,564)
        self.assertEqual(m.EXPECTED_BANDS,12)
    def test_all_registered_shards_nonidentical_and_exhaustive_modulo(self):
        self.assertEqual({m.assigned_source_shard(None,u) for u in range(160)},set(range(16)))
    def test_study_declares_probabilities_not_true_tidal_exposure(self):
        self.assertIn('NOT tidal-flat dry area or animal niche',m.__doc__ if m.__doc__ else '')
if __name__=="__main__":unittest.main()
