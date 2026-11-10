"""v121 TRUE original Dutch ground terrain (not DSM, map, seabed or bird GPS):
2019 Rijkswaterstaat AHN3-derived Oosterschelde DTM5 versus ORIGINAL 2020
Roggenplaat AHN4 DTM2 source, at exactly 441 fixed 2019 5m cell centers.
2020 product starts 31 Oct, AFTER 2020 May–July gull source. No bird inference.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import json,math,argparse,os,time
import numpy as np
import rasterio
from rasterio.windows import Window
from astral import Observer
from astral.sun import elevation
from original_2019_Oosterschelde_DTM_ground_source import (
    ROOT,LAYER,PROBE_QA,_download_original_raster)
from real_RWS_2020_gauge_stage_vs_2019_ground_DTM import (
    EXPECTED_DTM_SOURCE_SHA256,EXPECTED_SOURCE_BYTES,
    _read_original_5m_ground_v116_replay,_real_hourly_RWS_source,
    same_original_transport_retry)
from original_2020_gull_RWS_source import (
    original_2020_gauge_may_aug,NATIVE_SECONDARY,OriginalSourceStop)

SOURCE_2020_URL='https://downloads.rijkswaterstaatdata.nl/hoogte_2020/hoogte_roggenplaat_2020_dtm_2m.tif'
SOURCE_2020_CATALOG='https://data.overheid.nl/dataset/15344-hoogtebestand-roggenplaat-2m-dtm-2020'
SOURCE_2020_PRODUCT_START='2020-10-31'
SOURCE_YEAR_2019=2019;SOURCE_YEAR_2020=2020
MAX_2020_SOURCE_BYTES=180_000_000
SHA_2019=EXPECTED_DTM_SOURCE_SHA256
TARGET='Roggenplaat shoal'
AXIS_HALF=10
FIXED_NATIVE_5M_CENTERS=21*21
MIN_PAIRED_VALID_FRACTION=.90
DELTA_STAGE=(-.20,0.,+.20)
SOURCE_AHN_NAP_PARENT_ONLY=True

class SourceStop(Exception):pass

def native_2020_original_DTM_fetch(dst):
    """Only first-party original raw TIFF, never WMS screenshot or DSM."""
    try:
        req=Request(SOURCE_2020_URL,headers={'User-Agent':'boids-v121-real-2020-Roggenplaat-DTM2-terrain-source/1.0'})
        size=0; digest=sha256()
        with urlopen(req,timeout=120) as r,open(dst,'wb') as f:
            if r.status!=200:raise SourceStop('SOURCE_STOP_2020_DTM_PUBLISHER_HTTP_NOT_200')
            for block in iter(lambda:r.read(1_048_576),b''):
                size+=len(block)
                if size>MAX_2020_SOURCE_BYTES:
                    raise SourceStop('SOURCE_STOP_2020_PUBLISHED_DTM_OVER_FIXED_180MB_SIZE_LIMIT')
                digest.update(block);f.write(block)
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        raise SourceStop('SOURCE_TRANSPORT_UNAVAILABLE_2020_RWS_DTM_'+str(e)[:140]) from e
    with open(dst,'rb') as f:header=f.read(4)
    if header not in (bytes([73,73,42,0]),bytes([77,77,0,42]),bytes([73,73,43,0]),bytes([77,77,0,43])):
        raise SourceStop('SOURCE_STOP_ORIGINAL_2020_FILE_NOT_NATIVE_TIFF')
    return {'official_first_party_file':SOURCE_2020_URL,
      'original_file_bytes':size,'original_file_SHA256_local':digest.hexdigest(),
      'metadata_catalogue':SOURCE_2020_CATALOG,
      'catalogue_temporal_start_post_2020_bird_observation':SOURCE_2020_PRODUCT_START,
      'source_original_raster_content_bytes_verified_not_publisher_MD5':True}

def exact_original_2019_raster_centers(ds):
    """Exactly same 21×21 2019 5m source cells in earlier v116 fixed public plot."""
    fixed=PROBE_QA[TARGET]
    from pyproj import Transformer
    RD=Transformer.from_crs('EPSG:4326',ds.crs,always_xy=True)
    x,y=RD.transform(fixed['lon'],fixed['lat'])
    row,col=ds.index(x,y)
    if not (0<=row<ds.height and 0<=col<ds.width):
        raise ValueError('STOP_2019_ORIGINAL_DTM_FIXED_ROGGENPLAAT_OUTSIDE_SOURCE')
    r=np.arange(row-AXIS_HALF,row+AXIS_HALF+1)
    c=np.arange(col-AXIS_HALF,col+AXIS_HALF+1)
    if r.min()<0 or c.min()<0 or r.max()>=ds.height or c.max()>=ds.width:
        raise ValueError('STOP_FIXED_SOURCE_PLOT_CROSSES_2019_DTM_NATIVE_TILE')
    arr=ds.read(1,window=Window(int(c.min()),int(r.min()),len(c),len(r)),masked=True)
    if arr.size!=FIXED_NATIVE_5M_CENTERS:
        raise ValueError('STOP_ORIGINAL_FIXED_2019_441_CELL_SAMPLE_CHANGED')
    rr,cc=np.meshgrid(r,c,indexing='ij')
    # GDAL affine maps centers using native 0.5 offsets, no interpolation.
    xv,yv=ds.transform*(cc.ravel()+.5,rr.ravel()+.5)
    z=np.asarray(arr.data).ravel().astype(float)
    valid=~np.ma.getmaskarray(arr).ravel()
    z[~valid]=np.nan
    return np.asarray(xv),np.asarray(yv),z,{'native_fixed_original_2019_public_plot':TARGET,
       'native_2019_DTM_grid_px':len(z),
       'native_2019_valid_z_count':int(valid.sum()),
       '2019_original_native_raster_plot_rowcol':[int(row),int(col)],
       'source_original_2019_native_ground_median_if_valid':float(np.median(z[valid])) if valid.any() else None}

def nearest_original_2020_DTM_at_fixed_2019_centers(ds,x,y):
    """One actual original native 2020 DTM2 cell per 2019 SOURCE grid center.
    No bilinear smoothing, no nodata-to-zero conversion, no favorable regridding.
    """
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if not(len(x)==len(y)==FIXED_NATIVE_5M_CENTERS):
        raise ValueError('STOP_2020_SOURCE_ORIGINAL_2019_GRID_FRAME_NOT_441')
    if ds.crs is None or ds.crs.to_string()!='EPSG:28992':
        raise ValueError('STOP_2020_RWS_DTM_NATIVE_RD28992_CRS_MISMATCH')
    if ds.count!=1 or not (1.5<abs(ds.res[0])<2.5 and 1.5<abs(ds.res[1])<2.5):
        raise ValueError('STOP_2020_ORIGINAL_DTM_NOT_NATIVE_2M_GRID')
    c=np.floor((x-ds.transform.c)/ds.transform.a).astype(int)
    r=np.floor((y-ds.transform.f)/ds.transform.e).astype(int)
    inr=(r>=0)&(c>=0)&(r<ds.height)&(c<ds.width)
    values=np.full(len(x),np.nan,dtype=float)
    if inr.any():
        r0=int(r[inr].min());r1=int(r[inr].max())+1
        c0=int(c[inr].min());c1=int(c[inr].max())+1
        if (r1-r0)*(c1-c0)>50000:
            raise ValueError('STOP_2020_DTM_FIXED_100M_NATIVE_WINDOW_TOO_LARGE')
        arr=ds.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
        rv=r[inr]-r0;cv=c[inr]-c0
        v=arr.data[rv,cv].astype(float)
        mask=np.ma.getmaskarray(arr)[rv,cv]
        values[np.where(inr)[0][~mask]]=v[~mask]
    good=np.isfinite(values)
    return values,{'original_2020_DTM_valid_at_exact_2019_fixed_cell_centres':int(good.sum()),
        'original_2020_DTM_native_masked_or_outside_2019_centres':int((~good).sum()),
        'original_2020_DTM_elevation_source_minmax':[float(np.nanmin(values)),float(np.nanmax(values))] if good.any() else None,
        'original_2020_DTM_source_native_raster_res':list(ds.res),
        'original_source_masked_pixels_not_assumed_water_or_zero':True}

def true_ground_change_and_gauge_screen(z19,z20,stages,lat,lon):
    z19=np.asarray(z19,dtype=float);z20=np.asarray(z20,dtype=float)
    paired=np.isfinite(z19)&np.isfinite(z20)
    n=int(paired.sum());N=len(z19)
    if N!=FIXED_NATIVE_5M_CENTERS or n/N<MIN_PAIRED_VALID_FRACTION:
        return {'status':'NOT_ESTIMATED_PAIRED_SOURCE_GEOGRAPHY_LT90PCT',
            'n_original_fixed_grid_cells':N,'n_both_native_years_valid':n,
            'paired_DTM_source_fraction':n/N}
    dif=z20[paired]-z19[paired]
    out={'status':'2020_ORIGINAL_RWS_DTM_GROUND_CHANGE_AT_FIXED_2019_CELL_CENTRES',
       'n_paired_native_source_ground_cells':n,'n_original_fixed_2019_frame':N,
       'paired_fraction':n/N,
       'original_year_2019_source_height_median_m':float(np.median(z19[paired])),
       'original_year_2020_post_bird_DTM_height_median_m':float(np.median(z20[paired])),
       '2020_minus_2019_native_ground_z_diff_mean_m':float(dif.mean()),
       '2020_minus_2019_native_ground_z_diff_median_m':float(np.median(dif)),
       '2020_minus_2019_native_ground_z_diff_q05_q25_q75_q95_m':np.quantile(dif,[.05,.25,.75,.95]).tolist(),
       'n_true_paired_5m_centres_with_native_ground_diff_over_20cm':int((dif>.2).sum()),
       'n_true_paired_5m_centres_with_native_ground_diff_below_minus20cm':int((dif<-.2).sum()),
       'native_pixel_correlation_and_shared_survey_footprints_not_independent_replicates':True,
       '2020_october_terrain_follows_2020_may_aug_animal_and_RWS_tide_period':True}
    h=np.array([float(stages[t]) for t in sorted(stages)],dtype=float)
    times=sorted(stages)
    sday=np.array([elevation(Observer(latitude=lat,longitude=lon),t)>3 for t in times])
    snight=np.array([elevation(Observer(latitude=lat,longitude=lon),t)<-3 for t in times])
    screen={}
    for delta in DELTA_STAGE:
        a=(z19[paired][None,:]>h[:,None]+delta).mean(axis=1)
        b=(z20[paired][None,:]>h[:,None]+delta).mean(axis=1)
        screen[str(delta)]={'fixed_2020_original_RWS_Binnen_hourly_gauge_stage_m_NAP_shift':delta,
           '2019_ground_fraction_above_same_2020_gauge_stage_mean':float(a.mean()),
           '2020_october_ground_fraction_above_same_earlier_2020_gauge_stage_mean':float(b.mean()),
           '2020_minus_2019_ground_source_screen_difference':float((b-a).mean()),
           '2019_ground_astro_DAY_above_gauge_source_fraction':float(a[sday].mean()),
           '2020_october_ground_astro_DAY_above_gauge_source_fraction':float(b[sday].mean()),
           '2019_ground_astro_NIGHT_above_gauge_source_fraction':float(a[snight].mean()),
           '2020_october_ground_astro_NIGHT_above_gauge_source_fraction':float(b[snight].mean()),
           'not_true_MayAug2020_local_tidalflat_exposure':True}
    out['same_fixed_real_2020_RWS_measured_gauge_stage_counterfactual_across_two_DTM_survey_eras']=screen
    out['native_RWS_stage_hourly_n']=len(stages)
    out['NO_actual_2020_bird_forage_activity_true_local_h_x_t']=True
    return out

def run(v116meta,output):
    report={'analysis':'V121_TRUE_2019_AHN3_VS_2020_AHN4_POST_BIRD_ROGGENPLAAT_DTM_GROUND_PAIR',
     'original_2019_raster_SHA256_frozen':SHA_2019,
     '2019_parent_run':42833186694,'source_2020_RWS_DTM':'Roggenplaat 2020 AHN4 DTM2m NOT DSM',
     'official_2020_source_url':SOURCE_2020_URL,
     'source_2020_coverage_start':SOURCE_2020_PRODUCT_START,
     'native_original_source_vertical_reference':'AHN parent NAP but individual raster vertical tags may be absent',
     'source_status':'SOURCE_PENDING','no_bird_GPS_Y_or_2020_may_july_actual_exposure_measured':True}
    with TemporaryDirectory() as td:
        r19=Path(td)/'real2019_ground.tif';r20=Path(td)/'real2020_roggenplaat_ground.tif'
        try:
            old=_download_original_raster(r19,ROOT+LAYER['dtm_5']['filename'],LAYER['dtm_5']['id'])
            old_meta=_read_original_5m_ground_v116_replay(r19,v116meta)
            report['real2019_source_receipt']=old
            with rasterio.open(r19) as ds19:
                if ds19.crs.to_string()!='EPSG:28992' or ds19.width!=8000 or ds19.height!=7500:
                    raise SourceStop('SOURCE_STOP_ORIGINAL_2019_AHN_NATIVE_GRID_CHANGED')
                x,y,z19,ground19=exact_original_2019_raster_centers(ds19)
            if ground19['native_2019_valid_z_count']!=441:
                raise SourceStop('SOURCE_STOP_OLD_ROGGENPLAAT_2019_441_SOURCE_NOT_REPRODUCED')
            if abs(ground19['source_original_2019_native_ground_median_if_valid']-(-.10779999941587448))>1e-5:
                raise SourceStop('SOURCE_STOP_OLD_ROGGENPLAAT_REAL_2019_ELEVATION_NOT_REPLAYED')
            report['original_fixed_public_2019_DTM_source_replay']=ground19
        except (SourceStop,ValueError,RuntimeError,OSError) as e:
            report['source_status']='SOURCE_STOP_ORIGINAL_2019_DTM5_NO_TRUE_REPLAY'
            report['source_error']=str(e)[:250]
            return emit(report,output)
        try:
            report['original_2020_publisher_raster_source']=native_2020_original_DTM_fetch(r20)
            with rasterio.open(r20) as ds20:
                report['original_2020_native_GeoTIFF_geometry']={
                    'source_CRS':ds20.crs.to_string() if ds20.crs else None,
                    'source_width':ds20.width,'source_height':ds20.height,
                    'source_resolution':list(ds20.res),
                    'native_band_unit':ds20.units[0] if ds20.units else None,
                    'native_nodata':ds20.nodata,
                    'source_metadata_tags_subset':{k:str(v)[:100] for k,v in ds20.tags().items()},
                    'source_original_native_bounds':list(ds20.bounds)}
                z20,info=nearest_original_2020_DTM_at_fixed_2019_centers(ds20,x,y)
            report['real2020_source_sample_at_exact_original_fixed_2019_grid_centres']=info
        except (SourceStop,ValueError,rasterio.errors.RasterioError,OSError) as e:
            report['source_status']='SOURCE_STOP_ORIGINAL_2020_RWS_Roggenplaat_2M_DTM_GEOGRAPHY'
            report['source_error']=str(e)[:250]
            return emit(report,output)
        paired=np.isfinite(z19)&np.isfinite(z20)
        if paired.sum()/len(z19)<MIN_PAIRED_VALID_FRACTION:
            report['source_status']='NO_PAIRED_2019_2020_RWS_DTM_GROUND_SOURCE_LT90PCT'
            report['paired_2019_2020_DTM_valid_pixel_fraction']=float(paired.mean())
            return emit(report,output)
        try:
            (stage,proof),retry=existing_tide_provider()
            from real_RWS_2020_gauge_stage_vs_2019_ground_DTM import _real_hourly_RWS_source
            hours=_real_hourly_RWS_source(stage)
            report['original_2020_Roompotsluis_Binnen_10min_RWS_source_proof']={**proof,**retry}
        except (OriginalSourceStop,ValueError,TimeoutError,OSError) as e:
            report['source_status']='SOURCE_ADMITTED_BOTH_DTM_YEARS_BUT_2020_MEASURED_RWS_STAGE_NOT_AVAILABLE'
            report['source_RWS_failure']=str(e)[:200]
            # Genuine 2-year terrain delta can still be calculated without gauge stage.
            result=true_ground_change_and_gauge_screen_only(z19,z20)
            report['source_2019_2020_ground_change_without_tide']=result
            return emit(report,output)
        coords=PROBE_QA[TARGET]
        report['fixed_true_RWS_stage_and_both_native_ground_products']=(
            true_ground_change_and_gauge_screen(z19,z20,hours,coords['lat'],coords['lon']))
        report['source_status']='REAL_2019_2020_ORIGINAL_ROGGENPLAAT_TERRAIN_PAIRED_AND_2020_RWS_COUNTERFACTUAL_SCREEN'
    return emit(report,output)

def true_ground_change_and_gauge_screen_only(z19,z20):
    paired=np.isfinite(z19)&np.isfinite(z20)
    dif=z20[paired]-z19[paired]
    return {'status':'REAL_2019_2020_PAIRED_GROUND_CHANGE_WITHOUT_NATIVE_RWS',
        'native_paired_n':int(paired.sum()),
        'ground_difference_median':float(np.median(dif)),
        'ground_difference_q05_q95':np.quantile(dif,[.05,.95]).tolist(),
        'not_animal_or_true_MayJuly_2020_exposure':True}

def existing_tide_provider():
    from real_RWS_2020_gauge_stage_vs_2019_ground_DTM import same_original_transport_retry
    from original_2020_gull_RWS_source import original_2020_gauge_may_aug,NATIVE_SECONDARY
    return same_original_transport_retry(
        lambda:original_2020_gauge_may_aug(NATIVE_SECONDARY),NATIVE_SECONDARY)

def emit(report,output):
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    p=report.get('fixed_true_RWS_stage_and_both_native_ground_products') or report.get(
        'source_2019_2020_ground_change_without_tide') or {}
    print('V121_TRUE_2019_VS_2020_ROGGENPLAAT_ORIGINAL_DTM_NAP_SOURCE '+json.dumps({
       'source_status':report['source_status'],
       'source_2019_DTM_ground':report.get('original_fixed_public_2019_DTM_source_replay'),
       'source_2020_DTM_native':report.get('original_2020_native_GeoTIFF_geometry'),
       'original_2020_DTM_plot_source_valid':report.get('real2020_source_sample_at_exact_original_fixed_2019_grid_centres'),
       'ground_height_change':{k:v for k,v in p.items() if 'difference' in k or 'diff_' in k or 'median' in k or 'paired' in k},
       'two_year_same_RWS_gauge_stage_physical_screen':p.get('same_fixed_real_2020_RWS_measured_gauge_stage_counterfactual_across_two_DTM_survey_eras'),
       'source_error':report.get('source_error') or report.get('source_RWS_failure'),
       'NO_2020_GULL_ACTIVITY_OR_TRUE_MayJuly_EXPOSURE':True},
       sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--v116-real-2019-source-artifact',required=True)
    ap.add_argument('--output',required=True)
    a=ap.parse_args();run(a.v116_real_2019_source_artifact,a.output)
