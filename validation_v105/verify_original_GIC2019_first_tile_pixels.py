"""v105 authenticate and inspect ONE actual original 2017–2019 GIC tidal wetland GeoTIFF.

This is neither bare tidalflat habitat nor instantaneous true dry tidal exposure,
and it is NOT animal time-niche evidence. Fixed FIRST original GCS tile only.
"""
from __future__ import annotations
import base64,csv,hashlib,io,json,os,tempfile
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
import argparse
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform,transform_bounds
from aggregate_all_2019_physical import macro_rows

BUCKET='gic-archive'
NATIVE_PATH='gic-2019-v1-0/v1-0-1/murray-gic-v1.0.1-twprobabilityEnd-0000000000-0000000000.tif'
URL='https://storage.googleapis.com/'+BUCKET+'/'+NATIVE_PATH
SOURCE_SIZE_BYTES=53506115
SOURCE_MD5_PROVIDER_BASE64='Xeb2lnUWEK2EWWKvE41W3w=='
SOURCE_GENERATION='1659524265600797'
WGS84='EPSG:4326'
BLOCK_SAMPLE_PIXELS=256
MAX_SOURCE_BYTES=60_000_000

def _fetch_original_geotiff(out_path,request_fn=None):
    # Request original file bytes ONLY, with a fixed expected provider original checksum.
    if request_fn is None:
        req=Request(URL,headers={
            'Accept':'image/tiff, application/octet-stream',
            'User-Agent':'boids-v105-original-GIC2019-twprobabilityEnd-source-CRS-QA/1.0'})
        stream=urlopen(req,timeout=90)
    else:
        stream=request_fn(URL)
    counter=0
    h=hashlib.md5()
    sh=hashlib.sha256()
    with stream as resp,open(out_path,'wb') as out:
        while True:
            block=resp.read(524288)
            if not block:break
            counter+=len(block)
            if counter>MAX_SOURCE_BYTES:raise ValueError('STOP_GCS_SOURCE_BYTES_EXCEED_PROVIDER_BOUND')
            h.update(block);sh.update(block);out.write(block)
    if counter!=SOURCE_SIZE_BYTES or base64.b64encode(h.digest()).decode()!=SOURCE_MD5_PROVIDER_BASE64:
        raise ValueError('STOP_ORIGINAL_GCS_PROVIDER_SIZE_OR_MD5_MISMATCH')
    return {'original_GCS_public_url':URL,'native_GCS_object_generation':SOURCE_GENERATION,
        'original_provider_size_bytes':SOURCE_SIZE_BYTES,
        'actual_download_size_bytes':counter,
        'original_provider_md5_base64':SOURCE_MD5_PROVIDER_BASE64,
        'verified_local_sha256':sh.hexdigest(),'source_byte_identity':'VERIFIED_PROVIDER_MD5'}

def _qa_windows(src):
    width,height=src.width,src.height
    if min(width,height)<1 or src.count!=1:
        raise ValueError('STOP_NOT_SINGLEBAND_GIC_TWPROBABILITY_END_OR_INVALID_DIMENSIONS')
    n=BLOCK_SAMPLE_PIXELS
    specs=[('upper_left',0,0),('center',max(0,(width-n)//2),max(0,(height-n)//2)),
           ('lower_right',max(0,width-n),max(0,height-n))]
    result=[]
    for name,col,row in specs:
        region=Window(col,row,min(n,width-col),min(n,height-row))
        # Native nodata & masks must be respected, 0 is not automatically missing.
        vals=src.read(1,window=region,masked=True)
        arr=vals.compressed()
        p={'window':name,'column':col,'row':row,'total_pixels':int(vals.size),
           'source_masked_pixels':int(np.ma.getmaskarray(vals).sum()),
           'unmasked_pixels':len(arr)}
        if len(arr):
            p.update({'source_valid_min':float(arr.min()),'source_valid_max':float(arr.max()),
                      'source_valid_mean':float(np.mean(arr)),
                      'n_source_valid_above_50':int(np.sum(arr>=50)),
                      'n_source_valid_above_20':int(np.sum(arr>=20))})
        result.append(p)
    return result

def _gauge_points_in_this_one_tile(src,original):
    if src.crs is None:raise ValueError('STOP_ORIGINAL_TILE_GEOREFERENCING_CRS_MISSING')
    map_bounds=src.bounds
    selected=[]
    for s in original:
        try:
            x,y=transform(WGS84,src.crs,[float(s['longitude_signed'])],[float(s['latitude'])])
            row,col=src.index(x[0],y[0])
        except (ValueError,OverflowError) as e:
            raise ValueError('STOP_SOURCE_GEOREFERENCING_WGS84_FAILED') from e
        if 0<=row<src.height and 0<=col<src.width:
            z=src.read(1,window=Window(col,row,1,1),masked=True)
            masked=bool(np.ma.getmaskarray(z)[0,0])
            selected.append({'original_UHSLC_station_id':s['uid'],
               'native_GIC_tile_row':int(row),'native_GIC_tile_column':int(col),
               'original_2019_station_exact_point_in_THIS_tile':True,
               'valid_source_pixel':not masked,
               'pixel_tidal_wetland_RF_agreement_0_to_100':None if masked else float(z[0,0]),
               'NOT_BARE_FLAT_OR_INSTANTANEOUS_EXPOSURE':True})
    return selected

def run(source_dir,output):
    source=list(Path(source_dir).rglob('v94-2019-original-source-*.json'))
    sites,band_data,counts,_=macro_rows(source)
    if counts['candidate']!=564 or counts['eligible']!=160:
        raise ValueError('STOP_ORIGINAL_2019_UHSLC_SOURCE_FRAME_NOT_564_160')
    result={'analysis':'V105_TRUE_ORIGINAL_GIC2019_TIDAL_WETLAND_PROBABILITY_TILE_GEOREF_FIRST',
      'layer_semantic':'twprobabilityEnd 2017–2019 tidal wetland RF agreement encompassing flat/mangrove/marsh',
      'NO_BARE_TIDAL_FLAT_OR_ACTUAL_EXPOSURE_OR_BIOLOGY':True,
      'original_station_frame':counts,'tile_selection':'lexically_first_original_publisher_GCS_t7_source',
      'status':'UNVERIFIED_PROVIDER_SOURCE'}
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'original_GIC2019_twprobabilityEnd_first.tif'
        report=_fetch_original_geotiff(p)
        result['source_provenance']=report
        with rasterio.open(p) as ds:
            if ds.crs is None or ds.transform.is_degenerate:
                raise ValueError('STOP_GCS_ORIGINAL_GEOTIFF_MISSING_CRS_OR_AFFINE')
            bounds=transform_bounds(ds.crs,WGS84,*ds.bounds,densify_pts=21)
            bands=ds.block_shapes
            result['real_original_raster_geospatial_metadata']={
              'driver':ds.driver,'crs_string':ds.crs.to_string(),
              'width_native_pixels':ds.width,'height_native_pixels':ds.height,
              'band_count':ds.count,'dtype':list(ds.dtypes),'nodata':ds.nodata,
              'raster_block_shapes':list(bands),'native_affine_matrix':list(ds.transform)[:6],
              'original_raster_bounds_native':list(ds.bounds),
              'original_raster_bounds_wgs84':list(bounds),
              'resolution_in_original_CRS':list(ds.res),
              'mask_flag_enums':[[str(y) for y in x] for x in ds.mask_flag_enums],
              'source_is_tiled':ds.is_tiled}
            result['native_source_window_sample_QA']=_qa_windows(ds)
            included=_gauge_points_in_this_one_tile(ds,sites)
            result['2019_UHSLC_gauge_exact_points_inside_selected_TILE_only']=included
            result['n_2019_gauge_points_inside_THIS_tile']=len(included)
            result['n_2019_gauge_points_outside_THIS_tile_NOT_global_no_habitat']=len(sites)-len(included)
            result['status']='ORIGINAL_GCS_2019_TWPROBABILITYEND_RASTER_GEOREF_AND_SAMPLED_PIXELS_ADMITTED'
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V105_ORIGINAL_INTERTIDAL_RASTER_SOURCE_FINAL '+json.dumps({
      'status':result['status'],'provider_MD5':result['source_provenance']['source_byte_identity'],
      'original_tile_native_dims':[result['real_original_raster_geospatial_metadata']['width_native_pixels'],
              result['real_original_raster_geospatial_metadata']['height_native_pixels']],
      'crs':result['real_original_raster_geospatial_metadata']['crs_string'],
      'wgs84_tile_bounds':result['real_original_raster_geospatial_metadata']['original_raster_bounds_wgs84'],
      'native_sample_windows':result['native_source_window_sample_QA'],
      'n_2019_real_gauge_sites_geographically_inside_THIS_tile_only':
             result['n_2019_gauge_points_inside_THIS_tile'],
      'n_outside_is_NOT_a_wetland_absence':True,'no_biological_or_tidal_exposure_result':True},
      sort_keys=True),flush=True)
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--v94-original-source-dir',required=True)
    a.add_argument('--output',required=True)
    o=a.parse_args();run(o.v94_original_source_dir,o.output)
