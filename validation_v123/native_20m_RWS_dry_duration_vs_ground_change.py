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

def original_native_cell_ids(ds,x,y):
    if ds.crs is None or ds.crs.to_string()!='EPSG:28992':
        raise ValueError('STOP_V123_ORIGINAL_DRY20_SOURCE_NOT_RD_NEW')
    a=ds.transform
    if abs(ds.res[0]-20.)>1e-6 or abs(ds.res[1]-20.)>1e-6:
        raise ValueError('STOP_V123_SOURCE_MODELLED_DRYING_NATIVE_GRID_NOT20M')
    rows=np.floor((y-a.f)/a.e).astype(np.int64)
    cols=np.floor((x-a.c)/a.a).astype(np.int64)
    if not (np.isfinite(rows).all() and np.isfinite(cols).all()):
        raise ValueError('STOP_V123_NONFINITE_SOURCE_RD_COORDINATES')
    return list(zip(rows.tolist(),cols.tolist()))

def verify_native_original_2016_2021_co_registration(aff16,aff21):
    if (abs(aff16.a-aff21.a)>1e-6 or abs(aff16.e-aff21.e)>1e-6
        or abs(aff16.a-20.)>1e-6 or abs(aff16.e+20.)>1e-6):
        raise ValueError('STOP_V123_TRUE_2016_2021_GRID_CELLS_HAVE_DIFFERENT_SCALE')
    dx=(aff21.c-aff16.c)/20.;dy=(aff21.f-aff16.f)/20.
    if abs(dx-round(dx))>1e-6 or abs(dy-round(dy))>1e-6:
        raise ValueError('STOP_V123_ORIGINAL_20M_RWS_DRYING_MAPS_ARE_NOT_CO_REGISTERED')
    return {'native_20m_map_origin_shift_is_exact_integer_grid_cells':True,
       'east_shift_2021_minus_2016_in_native_20m_cells':int(round(dx)),
       'north_shift_2021_minus_2016_in_native_20m_cells':int(round(dy))}

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

def native_20m_coarse_source_aggregation(coords_x,coords_y, z19,z20,
                                         dry16,dry21,ids2016,ids2021):
    n=FIXED_NATIVE_5M_CENTERS
    if not all(len(q)==n for q in (coords_x,coords_y,z19,z20,dry16,dry21,ids2016,ids2021)):
        raise ValueError('STOP_V123_ORIGINAL_GEO_5M_2019_FRAME_NOT_441')
    grouped=defaultdict(list)
    for i,(a,b) in enumerate(zip(ids2016,ids2021)):
        if (not np.isfinite(dry16[i])) or (not np.isfinite(dry21[i])):
            continue
        grouped[b].append(i)
    cells=[]
    for key,idx in sorted(grouped.items()):
        origin_2016={ids2016[i] for i in idx}
        if len(origin_2016)!=1:
            raise ValueError('STOP_V123_NATIVE_20M_RWS_SAME_PHYSICAL_CELL_DIFFERS_BETWEEN_YEARS')
        d16={float(dry16[i]) for i in idx};d21={float(dry21[i]) for i in idx}
        if len(d16)!=1 or len(d21)!=1:
            raise ValueError('STOP_V123_ORIGINAL_MODELLED_DRY20_SOURCE_NOT_CONST_WITHIN_ITS_NATIVE_CELL')
        k=[i for i in idx if np.isfinite(z19[i]) and np.isfinite(z20[i])]
        row={'source_native_20m_2021_grid_cell_rowcol':[int(key[0]),int(key[1])],
           'source_n_original_5m_centers_located_within_this_20m_cell':len(idx),
           'source_n_paired_real_2019_2020_5m_centers':len(k),
           'original_2016_RWS_native_dry_duration_numeric':next(iter(d16)),
           'original_2021_RWS_native_dry_duration_numeric':next(iter(d21))}
        if k:
            d=(np.asarray(z20)[k]-np.asarray(z19)[k])
            row.update({'source_paired_2019_DTM5_ground_mean_m':float(np.mean(np.asarray(z19)[k])),
               'source_paired_2020_DTM2_ground_mean_m':float(np.mean(np.asarray(z20)[k])),
               'source_2020_minus_2019_ground_change_mean_m':float(np.mean(d)),
               'source_2020_minus_2019_ground_change_median_m':float(np.median(d))})
        cells.append(row)
    return cells

def summarize_native_20m(cells,dry16,dry21,z19,z20):
    if not len(cells):
        return {'status':'NOT_ESTIMATED_NO_NATIVE_20M_SOURCE_CELLS'}
    valid=[c for c in cells if 'source_2020_minus_2019_ground_change_mean_m' in c]
    if len(valid)<8:
        return {'status':'NOT_ESTIMATED_NATIVE_SOURCE_COARSE_CELLS_LT8',
           'native_20m_source_cells':len(cells),'native_z_paired_source_cells':len(valid)}
    a=np.array([c['original_2016_RWS_native_dry_duration_numeric'] for c in cells])
    b=np.array([c['original_2021_RWS_native_dry_duration_numeric'] for c in cells])
    dz=np.array([c['source_2020_minus_2019_ground_change_mean_m'] for c in valid])
    dmodel=np.array([c['original_2021_RWS_native_dry_duration_numeric']-
                     c['original_2016_RWS_native_dry_duration_numeric'] for c in valid])
    h20=np.array([c['source_paired_2020_DTM2_ground_mean_m'] for c in valid])
    model20=np.array([c['original_2021_RWS_native_dry_duration_numeric'] for c in valid])
    return {'status':'NATIVE_20M_ORIGINAL_2016_2021_ECOTOPE_DRY_INDEX_VS_2019_2020_DTM_SOURCE_DESCRIPTIVE',
       'n_original_unique_20m_source_grid_cells':len(cells),
       'n_original_20m_cells_with_both_terrain_eras':len(valid),
       'source_original_5m_centers_per_true_20m_cell_min_max':[
           min(c['source_n_original_5m_centers_located_within_this_20m_cell'] for c in cells),
           max(c['source_n_original_5m_centers_located_within_this_20m_cell'] for c in cells)],
       'source_original_5m_centers_total_represented':sum(
            c['source_n_original_5m_centers_located_within_this_20m_cell'] for c in cells),
       'source_equal_NATIVE_20m_cell_weight_2016_model_numeric_mean':float(a.mean()),
       'source_equal_NATIVE_20m_cell_weight_2021_model_numeric_mean':float(b.mean()),
       'source_equal_NATIVE_20m_cell_weight_2021_minus_2016_native_model_numeric_mean':float(np.mean(b-a)),
       'source_equal_NATIVE_20m_cell_weight_2021_minus_2016_native_model_numeric_median':float(np.median(b-a)),
       'source_2019_5m_pointweighted_model_native_mean_2016_old':float(np.mean(dry16[np.isfinite(dry16)])),
       'source_2019_5m_pointweighted_model_native_mean_2021_old':float(np.mean(dry21[np.isfinite(dry21)])),
       'spearman_20m_cell_2020_minus_2019_ground_mean_vs_2021_minus_2016_model_dry_index':spearman(dz,dmodel),
       'spearman_20m_cell_2020_ground_mean_vs_2021_modelled_dry_index':spearman(h20,model20),
       'source_20m_cells_spatially_dependent_not_independent_animals':True,
       'native_tiff_band_unit_tag_absent_official_RWS_handbook_uses_dry_time_percent':True,
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
                    if year=='2016':aff16=ds.transform
                    else:aff21=ds.transform
                if np.isfinite(values).sum()!=FIXED_NATIVE_5M_CENTERS or abs(np.mean(values)-OLD_V122_MEAN[year])>TOL:
                    raise ValueError('STOP_V123_RWS_OLD_2016_2021_NATIVE_DRY_MAP_PIXEL_SOURCE_NOT_REPLAYED_'+year)
                maps[year]=values
                report.setdefault('source_2016_2021_public_original_metadata',{})[year]=proof
            report['native_source_20m_2016_2021_RWS_DRY_duration_co_registration']=(
                verify_native_original_2016_2021_co_registration(aff16,aff21))
            cells=native_20m_coarse_source_aggregation(
                x,y,z19,z20,maps['2016'],maps['2021'],groups['2016'],groups['2021'])
            audit=summarize_native_20m(cells,maps['2016'],maps['2021'],z19,z20)
            report['source_native_20m_geographic_plot_audit']=audit
            # Source coarse geometry is public, but retain only aggregate not raw site original coordinates
            report['source_native_20m_original_cell_count']=len(cells)
            report['source_status']='GENUINE_ORIGINAL_2016_2021_RWS_DRY20_AND_2019_2020_DTM_NATIVE20M_GRAIN_VALIDATED'
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
       'OLD_2020_2019_ground_source_replayed':report.get('original_v121_2019_2020_true_ground_source_replay'),
       'NOT_REAL_2020_GULL_DRY_SUBSTRATE_OR_ACTIVITY':True},sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--v116-2019-original-source',required=True)
    a.add_argument('--output',required=True)
    b=a.parse_args();run(b.v116_2019_original_source,b.output)
