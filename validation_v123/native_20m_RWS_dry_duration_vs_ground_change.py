"""v123 genuine RWS independent source-grain audit: original 20m 2016/2021
Oosterschelde M2 modelled drying-duration raster cells vs 2019/October 2020
historical DTM heights at fixed 441 original 5m center sample locations.
CRITICAL: 441 points contain repeat observations of a MUCH smaller number of
native 20m drying cells. No 2020 bird GPS activity or true local dryness Y.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse,json
import numpy as np
from pyproj import Transformer
from rasterio.windows import Window
import rasterio

from original_2019_Oosterschelde_DTM_ground_source import (
    ROOT,LAYER,_download_original_raster)
from real_RWS_2020_gauge_stage_vs_2019_ground_DTM import (
    _read_original_5m_ground_v116_replay)
from real_2019_2020_Roggenplaat_paired_ground_source import (
    SOURCE_2020_URL,SHA_2019,EXPECTED_SOURCE_BYTES,
    native_2020_original_DTM_fetch,exact_original_2019_raster_centers,
    nearest_original_2020_DTM_at_fixed_2019_centers,
    FIXED_NATIVE_5M_CENTERS)
from original_RWS_2016_2021_Oosterschelde_drying_maps import (
    SOURCE_FILES,SOURCE_BASE,MAX_TIF_BYTES,authentic_source_file,
    original_native_raster_at_2019_fixed_centers)

FROZEN_SHA={
 '2019_DTM5':'605db8a6a58cbfb922cfabf11b072664b91c0236b471dcf2081683d17dcfd7ef',
 '2020_DTM2':'e876987b188a87fa2933a08c88f69285ff5600c6ed8459118c4cd355e18498b2',
 '2016_dry20':'c57801e4820833dfad22d43d5eaa388a65ffae18c070436f1b4c1723c93fdf16',
 '2021_dry20':'f8032ce2148a363f15d8ff6c7a3059a9478993f9a0289be25a67aa19b0c8a940'}
OLD_V121_PAIRED=439
OLD_V121_DIFF_MEAN=0.1251977220875612
OLD_V122_MEAN={'2016':48.662131519274375,'2021':50.74603174603175}
TOL=1e-7
SOURCE_NATIVE_COARSE_RES_M=20.
ORIGINAL_PIXEL_SCOPE_2019=441

def _validate_native_drying_crs(ds):
    """Source publisher 2016 WKT names EPSG28992 but contains PROJ stere
    rather than EPSG official sterea. Do NOT silently override publisher CRS.
    Exact native TIFF SHA is also checked by the caller before sampling.
    """
    if ds.crs is None:
        raise ValueError('STOP_V123_ORIGINAL_DRY20_SOURCE_NO_NATIVE_CRS')
    wkt=ds.crs.to_wkt()
    if ds.crs.to_epsg()==28992:
        return 'RWS_NATIVE_CANONICAL_EPSG28992_STEREA'
    if ('AUTHORITY["EPSG","28992"]' in wkt and
        'PROJECTION["Stereographic"]' in wkt and ds.crs.is_projected):
        return 'RWS_2016_LITERAL_STERE_WKT_WITH_INCONSISTENT_EPSG28992_AUTHORITY'
    raise ValueError('STOP_V123_ORIGINAL_DRY20_CRS_NOT_VALIDATED_FROM_AUTHENTIC_SOURCE')

def _source_native_xy(ds,x,y,mode='LITERAL_ORIGINAL_WKT'):
    mode_allowed=('LITERAL_ORIGINAL_WKT','AUTHORITY_EPSG28992_SENSITIVITY')
    if mode not in mode_allowed:
        raise ValueError('STOP_V123_UNREGISTERED_ORIGINAL_2016_MAP_CRS_ASSUMPTION')
    status=_validate_native_drying_crs(ds)
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if x.shape!=y.shape or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('STOP_V123_NONFINITE_ORIGINAL_2019_RD_COORDINATES')
    if (mode=='LITERAL_ORIGINAL_WKT' and
        status=='RWS_2016_LITERAL_STERE_WKT_WITH_INCONSISTENT_EPSG28992_AUTHORITY'):
        X,Y=Transformer.from_crs('EPSG:28992',ds.crs,always_xy=True).transform(x,y)
        return np.asarray(X),np.asarray(Y)
    return x.copy(),y.copy()

def original_native_cell_ids(ds,x,y,mode='LITERAL_ORIGINAL_WKT'):
    X,Y=_source_native_xy(ds,x,y,mode)
    a=ds.transform
    if abs(abs(a.a)-20.)>1e-6 or abs(abs(a.e)-20.)>1e-6 or a.b!=0 or a.d!=0:
        raise ValueError('STOP_V123_SOURCE_MODELLED_DRYING_NATIVE_GRID_NOT20M')
    rows=np.floor((Y-a.f)/a.e).astype(np.int64)
    cols=np.floor((X-a.c)/a.a).astype(np.int64)
    if not (np.isfinite(rows).all() and np.isfinite(cols).all()):
        raise ValueError('STOP_V123_NONFINITE_SOURCE_RD_COORDINATES')
    return list(zip(rows.tolist(),cols.tolist()))

def sample_native_2016_authority_sensitivity(ds,x,y):
    """Prespecified alternative: ASSUME the false 2016 EPSG28992 authority
    is physically canonical RD New. Read EXACT native TIFF source pixels;
    never use alternative as a data-driven replacement for literal-WKT Y.
    """
    if _validate_native_drying_crs(ds)!=(
         'RWS_2016_LITERAL_STERE_WKT_WITH_INCONSISTENT_EPSG28992_AUTHORITY'):
        raise ValueError('STOP_V123_ALTERNATIVE_REQUIRES_ORIGINAL_2016_STERE_AUTHORITY_MISMATCH')
    X,Y=_source_native_xy(ds,x,y,'AUTHORITY_EPSG28992_SENSITIVITY')
    a=ds.transform
    cols=np.floor((X-a.c)/a.a).astype(np.int64)
    rows=np.floor((Y-a.f)/a.e).astype(np.int64)
    inside=(rows>=0)&(cols>=0)&(rows<ds.height)&(cols<ds.width)
    out=np.full(len(X),np.nan,dtype=float)
    if inside.any():
        c0=int(cols[inside].min());c1=int(cols[inside].max())+1
        r0=int(rows[inside].min());r1=int(rows[inside].max())+1
        if (c1-c0)*(r1-r0)>50_000:
            raise ValueError('STOP_V123_NATIVE_2016_ALTERNATE_SAMPLE_TOO_LARGE')
        arr=ds.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
        vals=np.asarray(arr.data)[rows[inside]-r0,cols[inside]-c0].astype(float)
        mask=np.ma.getmaskarray(arr)[rows[inside]-r0,cols[inside]-c0]
        good=(~mask)&np.isfinite(vals)
        out[np.where(inside)[0][good]]=vals[good]
    return out

def verify_native_original_2016_2021_co_registration(aff16,aff21,
                                                     primary_projection_displacement_m):
    """Record NUMERIC grid-origin differences without falsely assuming true
    physical 20m polygon co-registration of two different native projections.
    """
    if (abs(aff16.a-aff21.a)>1e-6 or abs(aff16.e-aff21.e)>1e-6
        or abs(aff16.a-20.)>1e-6 or abs(aff16.e+20.)>1e-6):
        raise ValueError('STOP_V123_TRUE_2016_2021_GRID_CELLS_HAVE_DIFFERENT_SCALE')
    dx=(aff21.c-aff16.c)/20.;dy=(aff21.f-aff16.f)/20.
    numeric_origin_align=(abs(dx-round(dx))<=1e-6 and
                          abs(dy-round(dy))<=1e-6)
    displacement=float(np.median(primary_projection_displacement_m))
    return {
       'source_numeric_affine_origins_differ_by_integer_20m_cells':bool(numeric_origin_align),
       'numeric_east_origin_shift_2021_minus_2016_in_20m_cells':float(dx),
       'numeric_north_origin_shift_2021_minus_2016_in_20m_cells':float(dy),
       'original_2016_source_WKT_differs_from_official_RWS_EPSG28992':True,
       'median_coordinate_shift_native_2016_literal_WKT_vs_canonical_EPSG_m':displacement,
       'native_2016_and_2021_20m_polygons_exactly_shared':False,
       'source_action':'POINT_SAMPLED_APPROXIMATE_OVERLAY_NOT_EXACT_CELL_MATCH'}

def ranks(a):
    x=np.asarray(a,dtype=float)
    order=np.argsort(x);out=np.empty(len(x))
    i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[order[j]]==x[order[i]]:j+=1
        out[order[i:j]]=(i+j+1)/2
        i=j
    return out

def spearman(a,b):
    x=ranks(a);y=ranks(b)
    x=x-x.mean();y=y-y.mean()
    denom=np.linalg.norm(x)*np.linalg.norm(y)
    return float(np.dot(x,y)/denom) if denom>0 else None

def native_20m_coarse_source_aggregation(coords_x,coords_y,z19,z20,
                                         dry16,dry21,ids2016,ids2021):
    """Choose independent 2021 NATIVE 20m cells as reporting grain. The 2016
    source map is NOT polygon-identical: its values are averaged over fixed
    original 2019 5m sample points within each 2021 source cell. This is
    an equal-2021-cell *point-sampled overlay*, not exact area intersection.
    """
    n=FIXED_NATIVE_5M_CENTERS
    if not all(len(q)==n for q in (
        coords_x,coords_y,z19,z20,dry16,dry21,ids2016,ids2021)):
        raise ValueError('STOP_V123_ORIGINAL_GEO_5M_2019_FRAME_NOT_441')
    grouped=defaultdict(list)
    original16=defaultdict(set)
    for i,(a,b) in enumerate(zip(ids2016,ids2021)):
        if not (np.isfinite(dry16[i]) and np.isfinite(dry21[i])):
            continue
        original16[a].add(float(dry16[i]))
        grouped[b].append(i)
    for key,vals in original16.items():
        if len(vals)!=1:
            raise ValueError('STOP_V123_ORIGINAL_MODELLED_DRY20_SOURCE_NOT_CONST_WITHIN_ITS_NATIVE_CELL')
    cells=[]
    for key,idx in sorted(grouped.items()):
        present16={ids2016[i] for i in idx}
        source_d21={float(dry21[i]) for i in idx}
        if len(source_d21)!=1:
            raise ValueError('STOP_V123_ORIGINAL_2021_MODELLED_DRY20_NOT_CONST_WITHIN_ITS_NATIVE_CELL')
        k=[i for i in idx if np.isfinite(z19[i]) and np.isfinite(z20[i])]
        row={'source_native_20m_2021_grid_cell_rowcol':[int(key[0]),int(key[1])],
           'source_n_original_5m_centers_located_within_this_20m_cell':len(idx),
           'source_n_paired_real_2019_2020_5m_centers':len(k),
           'source_distinct_2016_native_cells_overlapping_this_2021_cell':len(present16),
           'original_2016_RWS_source_point_sampled_raw_mean_in_2021_cell':float(np.mean(np.asarray(dry16)[idx])),
           'original_2021_RWS_native_20m_raw_value':next(iter(source_d21)),
           'native_2016_wetland_20m_cell_not_same_polygon_as_2021':True}
        if k:
            d=np.asarray(z20)[k]-np.asarray(z19)[k]
            row.update({
             'source_paired_2019_DTM5_ground_mean_m':float(np.mean(np.asarray(z19)[k])),
             'source_paired_2020_DTM2_ground_mean_m':float(np.mean(np.asarray(z20)[k])),
             'source_2020_minus_2019_ground_change_mean_m':float(np.mean(d)),
             'source_2020_minus_2019_ground_change_median_m':float(np.median(d))})
        cells.append(row)
    return cells

def summarize_native_20m(cells,dry16,dry21,z19,z20,
                         distinct_native_2016,distinct_source_pairs):
    if not len(cells):
        return {'status':'NOT_ESTIMATED_NO_NATIVE_20M_SOURCE_CELLS'}
    valid=[c for c in cells if 'source_2020_minus_2019_ground_change_mean_m' in c]
    if len(valid)<8:
        return {'status':'NOT_ESTIMATED_NATIVE_SOURCE_COARSE_CELLS_LT8',
           'native_2021_20m_source_cells':len(cells),'native_z_paired_source_cells':len(valid)}
    a=np.array([c['original_2016_RWS_source_point_sampled_raw_mean_in_2021_cell']
                for c in cells])
    b=np.array([c['original_2021_RWS_native_20m_raw_value'] for c in cells])
    dz=np.array([c['source_2020_minus_2019_ground_change_mean_m'] for c in valid])
    dmodel=np.array([c['original_2021_RWS_native_20m_raw_value']-
              c['original_2016_RWS_source_point_sampled_raw_mean_in_2021_cell'] for c in valid])
    h20=np.array([c['source_paired_2020_DTM2_ground_mean_m'] for c in valid])
    model20=np.array([c['original_2021_RWS_native_20m_raw_value'] for c in valid])
    return {'status':'RWS_SOURCE_YEAR_2016_STERE_WKT_2021_STEREA_APPROXIMATE_20M_OVERLAY_NOT_IDENTICAL_NATIVE_CELLS',
       'n_2021_original_unique_20m_source_grid_cells':len(cells),
       'n_2016_original_unique_20m_source_grid_cells':int(distinct_native_2016),
       'n_unique_2016_2021_cell_intersection_pairs_at_FIXED_2019_5m_sample_centers':int(distinct_source_pairs),
       'n_original_2021_cells_OVERLAPPING_multiple_2016_native_cells':int(sum(
         c['source_distinct_2016_native_cells_overlapping_this_2021_cell']>1 for c in cells)),
       'n_2021_20m_cells_with_both_original_ground_eras':len(valid),
       'n_fixed_5m_centers_per_2021_20m_cell_min_max':[
           min(c['source_n_original_5m_centers_located_within_this_20m_cell'] for c in cells),
           max(c['source_n_original_5m_centers_located_within_this_20m_cell'] for c in cells)],
       'source_fixed_original_5m_centers_TOTAL_represented':int(sum(
         c['source_n_original_5m_centers_located_within_this_20m_cell'] for c in cells)),
       'original_equal_2021_native_20m_cell_weight_2016_model_raw_mean_POINT_SAMPLED_OVERLAY':float(a.mean()),
       'original_equal_2021_native_20m_cell_weight_2021_model_raw_mean':float(b.mean()),
       'original_equal_2021_native_20m_cell_weight_2021_minus_2016_model_raw_mean':float(np.mean(b-a)),
       'original_equal_2021_native_20m_cell_weight_2021_minus_2016_model_raw_median':float(np.median(b-a)),
       'OLD_v122_441_pointweighted_model_native_mean_2016_replayed':float(np.mean(
           dry16[np.isfinite(dry16)])),
       'OLD_v122_441_pointweighted_model_native_mean_2021_replayed':float(np.mean(
           dry21[np.isfinite(dry21)])),
       'spearman_NATIVE_2021_20m_cell_2020_minus_2019_ground_mean_vs_2021_minus_2016_dry_INDEX':spearman(dz,dmodel),
       'spearman_NATIVE_2021_20m_cell_2020_ground_mean_vs_2021_modelled_dry_INDEX':spearman(h20,model20),
       'source_spatially_dependent_20m_cells_no_naive_p_values':True,
       'native_TIFF_band_unit_tag_absent_handbook_context_not_unambiguous_percent':True,
       '2016_to_2021_model_difference_NOT_actual_2020_year_dynamic_dryflat':True,
       'site_individual_bird_food_or_actual_2020_dryflat_Y':'NOT_ESTIMATED'}

def run(v116_source,out):
    report={'analysis':'V123_ORIGINAL_RWS_20M_DRYING_MAP_NATIVE_CELL_INDEPENDENCE_AUDIT',
       'source_status':'SOURCE_PENDING','native_RWS_real_source_2016_2021_tiff_SHA256':FROZEN_SHA,
       'source_2020_october_ground_is_POST_2020_MayJuly_gull_tracking':True,
       'source_RWS_modelled_percent_hydromorphology_from_handbook_but_native_band_unit_tags_absent':True,
       'NO_GULL_TIME_NICHE_OR_LOCAL_2020_DRY_SUBSTRATE_INFERRED':True}
    with TemporaryDirectory() as td:
        r19=Path(td)/'real2019dtm5.tif';r20=Path(td)/'real2020dtm2.tif'
        try:
            _download_original_raster(r19,ROOT+LAYER['dtm_5']['filename'],LAYER['dtm_5']['id'])
            _read_original_5m_ground_v116_replay(r19,v116_source)
            with rasterio.open(r19) as ds:
                x,y,z19,geo=exact_original_2019_raster_centers(ds)
            receipt=native_2020_original_DTM_fetch(r20)
            if receipt['original_file_SHA256_local']!=FROZEN_SHA['2020_DTM2']:
                raise ValueError('STOP_V123_ORIGINAL_2020_RWS_AHN4_SHA_DIFFERENT')
            with rasterio.open(r20) as ds:
                z20,meta=nearest_original_2020_DTM_at_fixed_2019_centers(ds,x,y)
            paired=np.isfinite(z19)&np.isfinite(z20)
            if paired.sum()!=OLD_V121_PAIRED or abs(float(np.mean(z20[paired]-z19[paired]))-OLD_V121_DIFF_MEAN)>TOL:
                raise ValueError('STOP_V123_ORIGINAL_2019_2020_DTM_OBSERVED_CHANGE_NOT_REPRODUCED')
            report['original_v121_2019_2020_true_ground_source_replay']={
               'original_paired_fixed_native_5m_cell_centers':int(paired.sum()),
               'original_2020_minus_2019_ground_mean_m':float(np.mean(z20[paired]-z19[paired])),
               'same_real_original_genuine_DTM_SHA256_as_prior':True}
            maps={};groups={}
            for year in ('2016','2021'):
                p=Path(td)/(SOURCE_FILES[year])
                proof=authentic_source_file(SOURCE_FILES[year],p,12_000_000)
                if proof['original_source_SHA256']!=FROZEN_SHA[year+'_dry20']:
                    raise ValueError('STOP_V123_RWS_NATIVE_MODELLED_DRY20_ORIGINAL_SHA_DRIFT_'+year)
                with rasterio.open(p) as ds:
                    values,meta=original_native_raster_at_2019_fixed_centers(ds,x,y)
                    groups[year]=original_native_cell_ids(ds,x,y)
                    if year=='2016':
                        aff16=ds.transform
                        crs16=_validate_native_drying_crs(ds)
                        # Original TIFF literal WKT is the PRIMARY, not the false
                        # EPSG authority in its final WKT token.
                        native_x,native_y=_source_native_xy(ds,x,y)
                        difference=np.hypot(native_x-x,native_y-y)
                        if float(np.max(difference))>10.:
                            raise ValueError('STOP_V123_TRUE_2016_RWS_NATIVE_CRS_DISPLACEMENT_OVER10M')
                        alt2016=sample_native_2016_authority_sensitivity(ds,x,y)
                        altgroups=original_native_cell_ids(
                             ds,x,y,mode='AUTHORITY_EPSG28992_SENSITIVITY')
                        report['original_2016_literal_CRS_metadata_2019_fixed_geography']={
                           'original_RWS_CRS_status':crs16,
                           'native_rasterio_EPSG_does_NOT_resolve_despite_authority_in_WKT':True,
                           'median_native_2016_stere_vs_EPSG28992_2019_CRS_shift_m':float(np.median(difference)),
                           'min_max_native_2016_stere_vs_EPSG28992_shift_m':[
                               float(np.min(difference)),float(np.max(difference))],
                           'original_2016_native_WKT_to_official_2021_EPSG28992_not_identical':True}
                    else:
                        aff21=ds.transform
                        if _validate_native_drying_crs(ds)!='RWS_NATIVE_CANONICAL_EPSG28992_STEREA':
                            raise ValueError('STOP_V123_TRUE_2021_SOURCE_NOT_CANONICAL_RD_NEW')
                if np.isfinite(values).sum()!=FIXED_NATIVE_5M_CENTERS or abs(np.mean(values)-OLD_V122_MEAN[year])>TOL:
                    raise ValueError('STOP_V123_RWS_OLD_2016_2021_NATIVE_DRY_MAP_PIXEL_SOURCE_NOT_REPLAYED_'+year)
                maps[year]=values
                report.setdefault('source_2016_2021_public_original_metadata',{})[year]=proof
            report['native_source_20m_2016_2021_RWS_DRY_duration_co_registration']=(
                verify_native_original_2016_2021_co_registration(
                    aff16,aff21,difference))
            if (alt2016 is None or altgroups is None or
                np.isfinite(alt2016).sum()!=FIXED_NATIVE_5M_CENTERS):
                raise ValueError('STOP_V123_2016_EPSG_AUTHORITY_SENSITIVITY_SOURCE_INCOMPLETE')
            report['source_two_CRS_interpretations_2016_pixel_switch_QA']={
                'original_same_441_public_Roggenplaat_source_points':FIXED_NATIVE_5M_CENTERS,
                'n_true_original_5m_centres_switching_native_2016_cell_ID_under_alternative_EPSG':int(sum(
                    a!=b for a,b in zip(groups['2016'],altgroups))),
                'n_original_5m_centres_switching_native_2016_PIXEL_VALUE_under_alternative_EPSG':int(sum(
                    not np.isclose(a,b,rtol=0,atol=1e-10) for a,b in zip(maps['2016'],alt2016))),
                'source_literal_2016_WKT_is_PRIMARY_and_EPSG28992_override_is_ONLY_sensitivity':True}
            stats={}
            for label,source_2016_values,source_2016_cells in [
                 ('PRIMARY_2016_LITERAL_PUBLISHER_WKT',maps['2016'],groups['2016']),
                 ('SENSITIVITY_2016_SOURCE_STATED_EPSG28992_AUTHORITY_OVERRIDE',
                         alt2016,altgroups)]:
                cells=native_20m_coarse_source_aggregation(
                    x,y,z19,z20,source_2016_values,maps['2021'],
                    source_2016_cells,groups['2021'])
                valid_pairs={(source_2016_cells[i],groups['2021'][i])
                    for i in range(FIXED_NATIVE_5M_CENTERS)
                    if np.isfinite(source_2016_values[i]) and np.isfinite(maps['2021'][i])}
                stats[label]=summarize_native_20m(cells,source_2016_values,maps['2021'],
                      z19,z20,len({k[0] for k in valid_pairs}),len(valid_pairs))
            report['source_native_20m_geographic_plot_audit']=stats['PRIMARY_2016_LITERAL_PUBLISHER_WKT']
            report['source_native_20m_geographic_plot_projection_SENSITIVITY_NOT_NEW_DATA']=stats[
                  'SENSITIVITY_2016_SOURCE_STATED_EPSG28992_AUTHORITY_OVERRIDE']
            # Transparent public-source audit table at the ACTUAL 2021 20m grain,
            # not 441 GPS fixes or 441 independent drying cells. These 36 coarse
            # georeferenced summary values are public environmental data, and
            # relative row/column only: no original bird/tide information.
            public_min_row=min(r['source_native_20m_2021_grid_cell_rowcol'][0] for r in cells)
            public_min_col=min(r['source_native_20m_2021_grid_cell_rowcol'][1] for r in cells)
            # Recompute the two projection interpretations in the same fixed
            # 2021 source cell order without selecting by the correlation.
            primary_cells=native_20m_coarse_source_aggregation(
                x,y,z19,z20,maps['2016'],maps['2021'],
                groups['2016'],groups['2021'])
            sensitivity_by_cell={
                tuple(r['source_native_20m_2021_grid_cell_rowcol']):r
                for r in cells}
            public_records=[]
            for r in primary_cells:
                key=tuple(r['source_native_20m_2021_grid_cell_rowcol'])
                srow=sensitivity_by_cell[key]
                public_records.append({
                    'relative_original_2021_20m_grid_row':int(key[0]-public_min_row),
                    'relative_original_2021_20m_grid_column':int(key[1]-public_min_col),
                    'n_public_2019_5m_centers':r['source_n_original_5m_centers_located_within_this_20m_cell'],
                    'n_paired_original_2019_2020_ground_centers':r['source_n_paired_real_2019_2020_5m_centers'],
                    '2016_raw_dry_index_primary_literal_WKT_point_overlay':
                         r['original_2016_RWS_source_point_sampled_raw_mean_in_2021_cell'],
                    '2016_raw_dry_index_sensitivity_EPSG_authority':
                         srow['original_2016_RWS_source_point_sampled_raw_mean_in_2021_cell'],
                    '2021_original_raw_dry_index':r['original_2021_RWS_native_20m_raw_value'],
                    '2020_october_minus_2019_ground_mean_m':
                         r.get('source_2020_minus_2019_ground_change_mean_m'),
                    '2020_october_original_ground_mean_m':
                         r.get('source_paired_2020_DTM2_ground_mean_m'),
                    'source_2016_primary_WKT_native_cells_within_original_2021_cell':
                         r['source_distinct_2016_native_cells_overlapping_this_2021_cell']
                })
            report['source_original_public_FIXED_36_native20m_cell_aggregate_for_INDEPENDENT_RECALC']={
                'source_grain':'one native published 2021 20m cell, paired 2016 point-sampled native values',
                'n_public_rows':len(public_records),
                'source_original_modelled_dry_duration_unit_not_verified':True,
                'source_spatial_independence_not_claimed':True,
                'source_2020_survey_after_2020_MayJuly_gull_time':True,
                'public_coarse_cell_rows':public_records}
            report['source_native_2021_20m_original_cell_count']=len(
               {x for x in groups['2021']})
            report['source_status']='GENUINE_2016_LITERAL_STERE_WKT_AND_2021_EPSG28992_COARSE_20M_POINT_OVERLAY_WITH_CRS_SENSITIVITY'
        except (ValueError,RuntimeError,OSError,rasterio.errors.RasterioError) as e:
            report['source_status']='SOURCE_STOP_NATIVE_2016_2021_DRY20_OR_2019_2020_DTM_REPLAY'
            report['source_stop_reason']=str(e)[:260]
    return emit(report,out)

def emit(report,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V123_REAL_ORIGINAL_RWS_20M_DRY_DURATION_NATIVE_GRAIN_RESULT '+json.dumps({
       'source_status':report['source_status'],
       'co_registration':report.get('native_source_20m_2016_2021_RWS_DRY_duration_co_registration'),
       'native_geographic_analysis':report.get('source_native_20m_geographic_plot_audit'),
       'source_2016_native_CRS_discrepancy':report.get('original_2016_literal_CRS_metadata_2019_fixed_geography'),
       'source_native_authority_override_sensitivity':report.get('source_native_20m_geographic_plot_projection_SENSITIVITY_NOT_NEW_DATA'),
       'source_genuine_2016_pixel_switch_counts':report.get('source_two_CRS_interpretations_2016_pixel_switch_QA'),
       'OLD_2020_2019_ground_source_replayed':report.get('original_v121_2019_2020_true_ground_source_replay'),
       'NOT_REAL_2020_GULL_DRY_SUBSTRATE_OR_ACTIVITY':True,
       'source_stop_reason':report.get('source_stop_reason')},sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--v116-2019-original-source',required=True)
    a.add_argument('--output',required=True)
    b=a.parse_args();run(b.v116_2019_original_source,b.output)
