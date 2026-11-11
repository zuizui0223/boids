"""v123 source-grain known-truth. Synthetic tests never enter real paper results."""
import unittest
import numpy as np
from affine import Affine
import native_20m_RWS_dry_duration_vs_ground_change as q
class NativeOriginalTwentyMetreCells(unittest.TestCase):
    def test_source_frozen_2016_2021_native_20m_grid_alignment(self):
        a=Affine(20,0,35090,0,-20,413570)
        b=Affine(20,0,36870,0,-20,413410)
        r=q.verify_native_original_2016_2021_co_registration(a,b,np.array([3.82]))
        self.assertTrue(r['source_numeric_affine_origins_differ_by_integer_20m_cells'])
        self.assertFalse(r['native_2016_and_2021_20m_polygons_exactly_shared'])
        self.assertEqual(r['numeric_east_origin_shift_2021_minus_2016_in_20m_cells'],89)
        self.assertEqual(r['numeric_north_origin_shift_2021_minus_2016_in_20m_cells'],-8)
        nonmatching=q.verify_native_original_2016_2021_co_registration(
            a,Affine(20,0,36871,0,-20,413410),np.array([3.82]))
        self.assertFalse(nonmatching['source_numeric_affine_origins_differ_by_integer_20m_cells'])
    def test_true_source_20m_cell_collapse_four_repeated_5m_points_are_not_four_replicates(self):
        x=np.arange(441).astype(float);y=np.zeros(441)
        z19=np.full(441,-.2);z20=np.full(441,-.1)
        dry16=np.repeat(48.,441);dry21=np.repeat(52.,441)
        ids2016=[(50,50)]*220+[(50,51)]*221
        ids2021=[(58,139)]*220+[(58,140)]*221
        rows=q.native_20m_coarse_source_aggregation(x,y,z19,z20,dry16,dry21,ids2016,ids2021)
        self.assertEqual(len(rows),2)
        self.assertEqual([r['source_n_original_5m_centers_located_within_this_20m_cell'] for r in rows],[220,221])
        r=q.summarize_native_20m(rows,dry16,dry21,z19,z20)
        self.assertEqual(r['status'],'NOT_ESTIMATED_NATIVE_SOURCE_COARSE_CELLS_LT8')
        self.assertEqual(r['native_2021_20m_source_cells'],2)
    def test_native_same20m_cell_conflicting_original_source_values_stop(self):
        x=np.arange(441).astype(float);y=np.zeros(441)
        z19=np.full(441,-.2);z20=np.full(441,-.1)
        dry16=np.full(441,48.);dry21=np.full(441,50.)
        dry21[0]=51.
        with self.assertRaisesRegex(ValueError,'NOT_CONST_WITHIN_ITS_NATIVE_CELL'):
            q.native_20m_coarse_source_aggregation(x,y,z19,z20,dry16,dry21,
                [(1,1)]*441,[(1,1)]*441)

    def test_mixed_original_2016_source_cells_within_one_2021_are_not_forced_to_same_polygon(self):
        x=np.arange(441).astype(float);y=np.zeros(441)
        z19=np.full(441,-.2);z20=np.full(441,-.1)
        dry16=np.concatenate((np.full(100,47.),np.full(120,49.),np.full(221,48.)))
        dry21=np.concatenate((np.full(220,50.),np.full(221,54.)))
        ids2016=[(1,1)]*100+[(1,2)]*120+[(1,3)]*221
        ids2021=[(9,9)]*220+[(9,10)]*221
        cells=q.native_20m_coarse_source_aggregation(x,y,z19,z20,dry16,dry21,ids2016,ids2021)
        self.assertEqual(len(cells),2)
        self.assertEqual(cells[0]['source_distinct_2016_native_cells_overlapping_this_2021_cell'],2)
        self.assertAlmostEqual(cells[0]['original_2016_RWS_source_point_sampled_raw_mean_in_2021_cell'],
            (100*47+120*49)/220)
        self.assertEqual(cells[0]['original_2021_RWS_native_20m_raw_value'],50.)
    def test_source_spearman_ties_and_unknown_effect_boundaries(self):
        self.assertAlmostEqual(q.spearman([1,2,3,3],[1,2,3,3]),1.)
        self.assertAlmostEqual(q.spearman([1,2,3],[3,2,1]),-1.)
        self.assertIsNone(q.spearman([1,1,1],[1,2,3]))
        self.assertIn('No 2020 bird GPS activity',q.__doc__)
    def test_exact_prior_true_source_hashes_frozen(self):
        self.assertEqual(len(q.FROZEN_SHA),4)
        self.assertEqual(q.OLD_V121_PAIRED,439)
        self.assertAlmostEqual(q.OLD_V122_MEAN['2021'],50.746031746,places=6)
if __name__=='__main__':unittest.main()
