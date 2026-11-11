"""v124 independent source-backed SciPy checks of ORIGINAL 36 RWS 2021 20m
coarse cells against 2016 drying-index point overlay and 2019/2020 terrain.
Strict POST-v123 exploratory spatial shift diagnostic, NOT randomization p,
not independent 36 organisms/coasts, not true May–July 2020 bird dry habitat.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr,pearsonr

ORIGINAL_V123_RUN=42968384405
SOURCE_ANALYSIS='V123_ORIGINAL_RWS_20M_DRYING_MAP_NATIVE_CELL_INDEPENDENCE_AUDIT'
SOURCE_STATUS='GENUINE_2016_LITERAL_STERE_WKT_AND_2021_EPSG28992_COARSE_20M_POINT_OVERLAY_WITH_CRS_SENSITIVITY'
REPORTED_PRIMARY=0.9604240395245733
REPORTED_AUTHORITY_SENSITIVITY=0.9618771869015008
TOL=1e-12
N_ROWS=N_COLS=6
N_COARSE=36
UNIQUE_SPATIAL_SHIFTS=35

FIELDS={
 'primary':'2016_raw_dry_index_primary_literal_WKT_point_overlay',
 'authority':'2016_raw_dry_index_sensitivity_EPSG_authority',
 'year2021':'2021_original_raw_dry_index',
 'ground_diff':'2020_october_minus_2019_ground_mean_m',
 'ground2020':'2020_october_original_ground_mean_m'}

def load_fixed_original_v123_source(path):
    data=json.loads(Path(path).read_text())
    if (data.get('analysis')!=SOURCE_ANALYSIS or
        data.get('source_status')!=SOURCE_STATUS):
        raise ValueError('SOURCE_STOP_V124_NOT_IDENTICAL_AUTHENTIC_V123_ORIGINAL_36_CELL_RESULT')
    ref=data.get('source_original_public_FIXED_36_native20m_cell_aggregate_for_INDEPENDENT_RECALC') or {}
    rows=ref.get('public_coarse_cell_rows') or []
    if ref.get('n_public_rows')!=N_COARSE or len(rows)!=N_COARSE:
        raise ValueError('SOURCE_STOP_V124_NOT_EXACT_36_ORIGINAL_2021_NATIVE_CELLS')
    grid={}
    for row in rows:
        key=(row.get('relative_original_2021_20m_grid_row'),
             row.get('relative_original_2021_20m_grid_column'))
        if (len(key)!=2 or not all(isinstance(v,int) for v in key) or
            not (0<=key[0]<N_ROWS and 0<=key[1]<N_COLS) or key in grid):
            raise ValueError('SOURCE_STOP_V124_ORIGINAL_2021_NATIVE_20M_GEO_KEYS_CHANGED')
        if (any(row.get(field) is None or not np.isfinite(row[field])
                for field in FIELDS.values()) or
            row['n_paired_original_2019_2020_ground_centers']<1):
            raise ValueError('SOURCE_STOP_V124_ORIGINAL_36_CELL_NUMERIC_MISSING_OR_NOT_FINITE')
        grid[key]=row
    if set(grid)!={(r,c) for r in range(N_ROWS) for c in range(N_COLS)}:
        raise ValueError('SOURCE_STOP_V124_6_BY_6_NATIVE_SOURCE_GRID_INCOMPLETE')
    old=data['source_native_20m_geographic_plot_audit']
    alt=data['source_native_20m_geographic_plot_projection_SENSITIVITY_NOT_NEW_DATA']
    if (abs(old['spearman_NATIVE_2021_20m_cell_2020_minus_2019_ground_mean_vs_2021_minus_2016_dry_INDEX']-
            REPORTED_PRIMARY)>TOL or
        abs(alt['spearman_NATIVE_2021_20m_cell_2020_minus_2019_ground_mean_vs_2021_minus_2016_dry_INDEX']-
            REPORTED_AUTHORITY_SENSITIVITY)>TOL):
        raise ValueError('SOURCE_STOP_V124_PREVIOUS_VALIDATED_ORIGINAL_RESULT_DRIFT')
    # Validate not 36 independent subjects, and the 2016 original projection
    # metadata issue that materially changes true native pixel values.
    if (data.get('source_two_CRS_interpretations_2016_pixel_switch_QA',{}).get(
          'n_original_5m_centres_switching_native_2016_PIXEL_VALUE_under_alternative_EPSG')!=58 or
        data.get('source_native_20m_2016_2021_RWS_DRY_duration_co_registration',{}).get(
           'native_2016_and_2021_20m_polygons_exactly_shared') is not False):
        raise ValueError('SOURCE_STOP_V124_LOST_ORIGINAL_2016_PROJECTION_UNCERTAINTY')
    return grid,data

def independent_scipy_spatial_validation(grid):
    field=lambda f:np.array([[grid[r,c][FIELDS[f]] for c in range(N_COLS)]
                             for r in range(N_ROWS)],dtype=float)
    terrain_diff=field('ground_diff')
    terrain_2020=field('ground2020')
    model_2021=field('year2021')
    result={'analysis':'V124_SciPy_ORIGINAL_36CELL_SPATIAL_GEOGRAPHY_POST_OUTCOME_DIAGNOSTIC',
      'source_original_v123_run':ORIGINAL_V123_RUN,
      'true_original_2021_native20m_source_cells':N_COARSE,
      'source_all_36_cells_one_contiguous_Roggenplaat_plot':True,
      'NO_GENUINE_NULL_TEST_OR_P_VALUES':True,
      'NOT_INDEPENDENT_BIOLOGICAL_REPLICATION':True,
      'not_true_2020_gull_time_niche_feeding_or_tideflat_access':True,
      'two_original_projection_interpretations':{}}
    for label,source16 in (('LITERAL_2016_NATIVE_STERE_WKT',field('primary')),
                           ('2016_AUTHORITY_EPSG28992_ASSUMPTION_ONLY',field('authority'))):
        delta=model_2021-source16
        rho=float(spearmanr(terrain_diff.ravel(),delta.ravel()).statistic)
        target=REPORTED_PRIMARY if label.startswith('LITERAL') else REPORTED_AUTHORITY_SENSITIVITY
        if abs(rho-target)>TOL:
            raise ValueError('SOURCE_STOP_V124_INDEPENDENT_SciPy_SPEARMAN_DIFFERS_FROM_ORIGINAL_TRUE_SOURCE')
        # Preserves 6x6 drying source internal spatial texture but wraps map
        # at boundaries; physically implausible and only exploratory.
        shifted=[]
        for dr in range(N_ROWS):
            for dc in range(N_COLS):
                if dr==0 and dc==0:continue
                moved=np.roll(delta,shift=(dr,dc),axis=(0,1))
                shifted.append({'cyclic_row_shift_20m_cells':dr,
                  'cyclic_col_shift_20m_cells':dc,
                  'source_drying_map_shift_spearman_vs_UNSHIFTED_terrain':
                        float(spearmanr(terrain_diff.ravel(),moved.ravel()).statistic)})
        if len(shifted)!=UNIQUE_SPATIAL_SHIFTS:
            raise ValueError('SOURCE_STOP_V124_NOT_ALL_35_GEOGRAPHIC_SHIFT_DIAGNOSTICS')
        leave_rows=[float(spearmanr(terrain_diff[np.arange(6)!=r].ravel(),
             delta[np.arange(6)!=r].ravel()).statistic) for r in range(N_ROWS)]
        leave_cols=[float(spearmanr(terrain_diff[:,np.arange(6)!=c].ravel(),
             delta[:,np.arange(6)!=c].ravel()).statistic) for c in range(N_COLS)]
        coords=np.array([(r,c) for r in range(N_ROWS) for c in range(N_COLS)],dtype=float)
        X=np.column_stack([np.ones(N_COARSE),coords])
        z=terrain_diff.ravel()
        d=delta.ravel()
        zr=z-X@np.linalg.lstsq(X,z,rcond=None)[0]
        dr=d-X@np.linalg.lstsq(X,d,rcond=None)[0]
        shifted_value=np.array([x['source_drying_map_shift_spearman_vs_UNSHIFTED_terrain'] for x in shifted])
        result['two_original_projection_interpretations'][label]={
            'source_year_2021_minus_2016_raw_native_index_average':float(delta.mean()),
            'source_year_2021_minus_2016_raw_native_index_median':float(np.median(delta)),
            'source_20m_cells_with_positive_change':int((delta>0).sum()),
            'source_20m_cells_with_zero_change':int((delta==0).sum()),
            'source_20m_cells_with_negative_change':int((delta<0).sum()),
            'independent_scipy_2020_2019_ground_change_vs_2021_2016_model_raw_diff_spearman':rho,
            'independent_scipy_2020_ground_level_vs_2021_dry_model_index_spearman':float(
                 spearmanr(terrain_2020.ravel(),model_2021.ravel()).statistic),
            'toroidal_35_geographically_WRONG_20m_map_alignment_source_diagnostic':{
                'n_geographic_CYCLIC_shifted_map_variants':len(shifted),
                'min_shifted_map_rho':float(shifted_value.min()),
                'median_shifted_map_rho':float(np.median(shifted_value)),
                'max_shifted_map_rho':float(shifted_value.max()),
                'n_CYCLIC_shift_alignments_at_least_as_correlated_as_TRUE_point_overlay':int(
                    np.sum(shifted_value>=rho)),
                'max_correlated_wrong_map_shift':max(shifted,key=lambda x:x[
                    'source_drying_map_shift_spearman_vs_UNSHIFTED_terrain']),
                'CANNOT_USE_AS_RANDOMIZATION_P_OR_CAUSAL_NULL':True},
            'spatial_leave_one_ROW_out_spearman_min_max':[float(min(leave_rows)),
                                                       float(max(leave_rows))],
            'spatial_leave_one_COLUMN_out_spearman_min_max':[float(min(leave_cols)),
                                                          float(max(leave_cols))],
            'post_hoc_linear_row_col_DETRENDED_residual_spearman':float(
                     spearmanr(zr,dr).statistic),
            'post_hoc_linear_row_col_DETRENDED_residual_Pearson':float(
                     pearsonr(zr,dr).statistic),
            'all_STATISTICS_DESCRIPTIVE_SOURCE_STRUCTURE_ONLY_NO_P_VALUES':True}
    return result

def run(source_path,output):
    grid,source=load_fixed_original_v123_source(source_path)
    report=independent_scipy_spatial_validation(grid)
    report['original_2016_native_WKT_geolocation_issue']=source.get(
         'original_2016_literal_CRS_metadata_2019_fixed_geography')
    report['source_original_native_2016_2021_TIFF_SHA_frozen']=source.get(
         'native_RWS_real_source_2016_2021_tiff_SHA256')
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('V124_PUBLIC_TRUE_36CELL_INDEPENDENT_SCIPY_SPATIAL_SOURCE_VALIDATION '+json.dumps({
       'source_result':'INDEPENDENT_SCIPY_RANK_REPLAY_AND_35_SPATIAL_SHIFT_DIAGNOSTIC',
       'n_true_20m_coarse_cells':N_COARSE,
       'primary':report['two_original_projection_interpretations']['LITERAL_2016_NATIVE_STERE_WKT'],
       'secondary_CRSA':report['two_original_projection_interpretations'][
         '2016_AUTHORITY_EPSG28992_ASSUMPTION_ONLY'],
       'no_inference_on_real_2020_gulls_or_independent_36coasts':True
    },sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--original-v123-public-36cells',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.original_v123_public_36cells,a.output)
