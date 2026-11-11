"""v124 synthetic tests verify independent SciPy and all 35 map shifts.
Synthetic test samples NEVER replace original RWS source 36 cells."""
from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import independent_SciPy_2021_native20m_spatial_shift as q

def synthetic_grid():
    rows={}
    for r in range(6):
        for c in range(6):
            z=float(r*6+c)
            rows[(r,c)]={
               '2020_october_minus_2019_ground_mean_m':z,
               '2020_october_original_ground_mean_m':z+.1,
               '2021_original_raw_dry_index':50+z,
               '2016_raw_dry_index_primary_literal_WKT_point_overlay':50,
               '2016_raw_dry_index_sensitivity_EPSG_authority':50,
               'n_paired_original_2019_2020_ground_centers':1}
    return rows

class OriginalStaticModelMapSourceTruth(unittest.TestCase):
    def test_complete_6x6_source_grid_required_not_441_independent_sites(self):
        self.assertEqual(q.N_COARSE,36)
        self.assertEqual(q.UNIQUE_SPATIAL_SHIFTS,35)
        self.assertEqual((q.N_ROWS,q.N_COLS),(6,6))
    def test_separate_scipy_no_same_rank_helper_and_all_cyclic_shifts(self):
        with patch.object(q,'REPORTED_PRIMARY',1.),patch.object(q,'REPORTED_AUTHORITY_SENSITIVITY',1.):
            result=q.independent_scipy_spatial_validation(synthetic_grid())
        for value in result['two_original_projection_interpretations'].values():
            self.assertAlmostEqual(value['independent_scipy_2020_2019_ground_change_vs_2021_2016_model_raw_diff_spearman'],1.)
            self.assertEqual(value['toroidal_35_geographically_WRONG_20m_map_alignment_source_diagnostic'][
               'n_geographic_CYCLIC_shifted_map_variants'],35)
            self.assertEqual(len(value['spatial_leave_one_ROW_out_spearman_min_max']),2)
            self.assertTrue(value['all_STATISTICS_DESCRIPTIVE_SOURCE_STRUCTURE_ONLY_NO_P_VALUES'])
    def test_original_true_v123_source_status_and_wkt_crs_uncertainty_required(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'wrong_source.json'
            p.write_text(json.dumps({'analysis':q.SOURCE_ANALYSIS,'source_status':'SOURCE_STOP',
                'source_original_public_FIXED_36_native20m_cell_aggregate_for_INDEPENDENT_RECALC':{}}))
            with self.assertRaisesRegex(ValueError,'NOT_IDENTICAL_AUTHENTIC'):
                q.load_fixed_original_v123_source(p)
    def test_malformed_or_repeated_geographic_cell_fails_before_ranks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json'
            record={'relative_original_2021_20m_grid_row':0,
                    'relative_original_2021_20m_grid_column':0,
                    'n_paired_original_2019_2020_ground_centers':1}
            record.update({f:2. for f in q.FIELDS.values()})
            p.write_text(json.dumps({'analysis':q.SOURCE_ANALYSIS,'source_status':q.SOURCE_STATUS,
                'source_original_public_FIXED_36_native20m_cell_aggregate_for_INDEPENDENT_RECALC':{
                    'n_public_rows':36,'public_coarse_cell_rows':[record]*36}}))
            with self.assertRaisesRegex(ValueError,'GEO_KEYS_CHANGED'):
                q.load_fixed_original_v123_source(p)
if __name__=="__main__":unittest.main()
