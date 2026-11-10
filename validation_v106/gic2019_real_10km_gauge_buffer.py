"""v106 first genuine GIC 2019 wetland-probability pixel values within 10km of
preselected 2019 original UHSLC gauge sites, one lowest-ID site per populated
15-degree hemisphere band. IMPORTANT: NOT tidal-flat dry area or animal niche.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime
from hashlib import sha256,md5
from math import cos,radians,floor,ceil
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
from urllib.error import HTTPError,URLError
import argparse,base64,json,tempfile
import numpy as np
import rasterio
from rasterio.windows import Window
from pyproj import Geod
from affine import Affine
from aggregate_all_2019_physical import macro_rows
from real_global_UHSLC_hourly_station_manifest import _latitude_band

PARENT_V105_RUN=42737124600
GLOBAL_V94_RUN=42616065580
SOURCE_BUCKET='gic-archive'
SOURCE_DIR='gic-2019-v1-0/v1-0-1'
GIC_SOURCE_PREFIX='murray-gic-v1.0.1-twprobabilityEnd-'
TILE_N=65536
SAMPLING_RADIUS_M=10_000.
PROVIDER_METADATA='https://storage.googleapis.com/storage/v1/b/gic-archive/o/'
PUBLISHER_DOWNLOAD='https://storage.googleapis.com/gic-archive/'
MAX_DOWNLOAD_SIZE=260_000_000
POLICY_BANDS=['N_00_15','N_15_30','N_30_45','N_45_60','N_60_75',
              'S_00_15','S_30_45','S_45_60']
GEOD=Geod(ellps='WGS84')

class SourceUnavailable(Exception):pass

def choose_station_by_original_UID(source_files,band):
    if band not in POLICY_BANDS:raise ValueError('SOURCE_STOP_UNKNOWN_OR_UNFROZEN_LATITUDE_BAND')
    sites,byband,counts,_=macro_rows(source_files)
    if counts['candidate']!=564 or counts['eligible']!=160:
        raise ValueError('SOURCE_STOP_NATIVE_UHSLC_STATION_COUNTS_DRIFTED')
    allowed=byband[band]['raw_station_outcomes']
    if len(allowed)==0:raise ValueError('SOURCE_STOP_NO_ORIGINAL_2019_SOURCE_QUALIFIED_GAUGE_IN_BAND')
    item=min(allowed,key=lambda r:int(r['uid']))
    if _latitude_band(item['latitude'])!=band:
        raise ValueError('SOURCE_STOP_GAUGE_GEO_CANNOT_IDENTIFY_OWN_BAND')
    return item,{'original_station_count_in_band':len(allowed),
       'selection':'the smallest native uhslc_id in source-only quality-eligible year 2019',
       'selection_ignores_tidal_F_and_sunlight_overlap_and_raster_outcomes':True}

def read_original_geotransform(v105_artifact):
    source=json.loads(Path(v105_artifact).read_text())
    if source.get('analysis')!='V105_TRUE_ORIGINAL_GIC2019_TIDAL_WETLAND_PROBABILITY_TILE_GEOREF_FIRST' or (
       source.get('status')!='ORIGINAL_GCS_2019_TWPROBABILITYEND_RASTER_GEOREF_AND_SAMPLED_PIXELS_ADMITTED'
    ) or (source.get('source_provenance') or {}).get('source_byte_identity')!='VERIFIED_PROVIDER_MD5':
        raise ValueError('SOURCE_STOP_NEED_GENUINE_ORIGINAL_FIRST_TILE_CRS_AND_PROVIDER_MD5')
    geom=source['real_original_raster_geospatial_metadata']
    if geom['crs_string']!='EPSG:4326' or geom['width_native_pixels']!=TILE_N or geom['height_native_pixels']!=TILE_N:
        raise ValueError('SOURCE_STOP_SOURCE_ORIGINAL_GLOBAL_WGS84_TILE_GRID_CHANGED')
    aff=Affine(*geom['native_affine_matrix'])
    if aff.b!=0 or aff.d!=0 or aff.a<=0 or aff.e>=0:
        raise ValueError('SOURCE_STOP_NON_ORIGINAL_GRID_ORIENTATION')
    return aff

def native_expected_tile(lat,lon,aff):
    if not (-90<=lat<=90 and -180<=lon<=180):
        raise ValueError('SOURCE_STOP_NATIVE_WGS84_STATION_INVALID')
    cc=(lon-aff.c)/aff.a;rr=(lat-aff.f)/aff.e
    if cc<0 or rr<0:
        raise SourceUnavailable('SOURCE_OUTSIDE_NATIVE_2019_TILE_GRID_ORIGIN_NOT_WETLAND_ABSENCE')
    colstart=int(floor(cc))//TILE_N*TILE_N
    rowstart=int(floor(rr))//TILE_N*TILE_N
    name=f'{GIC_SOURCE_PREFIX}{rowstart:010d}-{colstart:010d}.tif'
    return {'native_GCS_tile_name':SOURCE_DIR+'/'+name,
       'expected_colstart_original_pixels':colstart,
       'expected_rowstart_original_pixels':rowstart,
       'gauge_local_original_expected_pixel_col':int(floor(cc))-colstart,
       'gauge_local_original_expected_pixel_row':int(floor(rr))-rowstart}

def metadata_for_native_tile(item):
    path=item['native_GCS_tile_name']
    if not (path.startswith(SOURCE_DIR+'/'+GIC_SOURCE_PREFIX) and path.endswith('.tif')):
        raise ValueError('SOURCE_STOP_NOT_ORIGINAL_NATIVE_2019_T7_TILE')
    url=PROVIDER_METADATA+quote(path,safe='')
    req=Request(url,headers={'Accept':'application/json',
            'User-Agent':'boids-v106-GIC2019-native-tile-source-geodesic-pilot/1.0'})
    try:
        with urlopen(req,timeout=35) as r:
            data=json.loads(r.read(1_000_001))
    except HTTPError as e:
        if e.code==404:raise SourceUnavailable('ORIGINAL_GIC_2019_EXPECTED_TILE_HTTP404_MAP_COVERAGE_UNDETERMINED') from e
        raise SourceUnavailable('ORIGINAL_GIC_2019_GCS_METADATA_TRANSPORT_HTTP_'+str(e.code)) from e
    except (URLError,TimeoutError) as e:raise SourceUnavailable('ORIGINAL_GIC_2019_METADATA_TRANSPORT_FAILURE') from e
    if data.get('name')!=path or data.get('bucket')!=SOURCE_BUCKET:
        raise ValueError('SOURCE_STOP_GCS_ORIGINAL_OBJECT_IDENTITY_MISMATCH')
    expected=int(data.get('size',0))
    if not data.get('md5Hash') or expected<=0:
        raise ValueError('SOURCE_STOP_ORIGINAL_GCS_MD5_SIZE_ABSENT')
    if expected>MAX_DOWNLOAD_SIZE:
        raise SourceUnavailable('ORIGINAL_GCS_SOURCE_TILE_BYTES_EXCEED_PREDECLARED_260MB_LIMIT')
    return {'name':path,'size':expected,'md5Hash':data['md5Hash'],
       'generation':data.get('generation'),'crc32c':data.get('crc32c'),
       'contentType':data.get('contentType'),'object_metadata_original':url}

def download_and_verify_original_gcs_tile(original,path):
    url=PUBLISHER_DOWNLOAD+original['name']
    request=Request(url,headers={'Accept':'image/tiff, application/octet-stream',
        'User-Agent':'boids-v106-public-original-2019-GIC-native-tidal-wetland/1.0'})
    size=0;h=md5();sh=sha256()
    try:
        with urlopen(request,timeout=95) as response, open(path,'wb') as dst:
            while True:
                block=response.read(1_048_576)
                if not block:break
                size+=len(block)
                if size>MAX_DOWNLOAD_SIZE:
                    raise ValueError('SOURCE_STOP_TILE_TOO_LARGE_WHILE_STREAMING')
                h.update(block);sh.update(block);dst.write(block)
    except (HTTPError,URLError,TimeoutError) as e:
        raise SourceUnavailable('ORIGINAL_GIC_T7_PUBLIC_DOWNLOAD_NETWORK_FAILURE') from e
    if size!=original['size'] or base64.b64encode(h.digest()).decode()!=original['md5Hash']:
        raise ValueError('SOURCE_STOP_GENUINE_GCS_TILE_MD5_OR_SIZE_NOT_VERIFIED')
    return {'source_original_GCS_provider_MD5_verified':True,
       'full_native_tiff_provider_source_size_bytes':size,
       'original_GCS_tiff_sha256_local':sh.hexdigest(),
       'provider_generation':original['generation']}

def source_10km_wetland_probability(ds,lat,lon):
    if ds.crs.to_string()!='EPSG:4326' or ds.count!=1:
        raise ValueError('SOURCE_STOP_ACTUAL_TILE_NOT_SOURCE_EXPECTED_EPSG4326_ONE_BAND')
    a=ds.transform.a;e=ds.transform.e;c=ds.transform.c;f=ds.transform.f
    dlat=SAMPLING_RADIUS_M/110_900.
    dlon=SAMPLING_RADIUS_M/(111_000*max(cos(radians(lat)),.10))
    west,east=lon-dlon,lon+dlon
    south,north=lat-dlat,lat+dlat
    col0=max(0,int(floor((west-c)/a)))
    col1=min(ds.width,int(ceil((east-c)/a)))
    row0=max(0,int(floor((f-north)/abs(e))))
    row1=min(ds.height,int(ceil((f-south)/abs(e))))
    if col0>=col1 or row0>=row1:
        return {'source_window':'NO_OVERLAPPING_10KM_BUFFER_WITH_SELECTED_TILE',
                'complete_10km_circle_in_this_tile':False}
    complete=bool(west>=ds.bounds.left and east<=ds.bounds.right
                  and south>=ds.bounds.bottom and north<=ds.bounds.top)
    win=Window(col0,row0,col1-col0,row1-row0)
    img=ds.read(1,window=win,masked=True)
    xs=c+(np.arange(col0,col1)+.5)*a
    ys=f+(np.arange(row0,row1)+.5)*e
    xgrid,ygrid=np.meshgrid(xs,ys)
    _,_,dist=GEOD.inv(np.full(xgrid.size,lon),np.full(xgrid.size,lat),
                      xgrid.ravel(),ygrid.ravel())
    inside=dist.reshape(img.shape)<=SAMPLING_RADIUS_M
    native_mask=np.ma.getmaskarray(img)
    valid=inside & (~native_mask)
    src=np.asarray(img.data,dtype=np.float64)
    values=src[valid]
    if len(values) and (np.min(values)<0 or np.max(values)>100):
        raise ValueError('SOURCE_STOP_TIDAL_WETLAND_RF_NATIVE_PIXEL_OUT_OF_0_100_RANGE')
    return {'source_window':'NATIVE_GIC_10KM_GEODESIC_PIXEL_BUFFER',
        'buffer_radius_m':SAMPLING_RADIUS_M,
        'complete_10km_circle_in_this_tile':complete,
        'n_original_pixels_in_10km_circle_in_this_one_tile':int(np.sum(inside)),
        'n_valid_original_GIC_pixels_10km':int(np.sum(valid)),
        'n_masked_GIC_pixels_inside10km':int(np.sum(inside&native_mask)),
        'source_validity_fraction_among_this_tile_10km_pixels':
             float(len(values)/max(1,int(np.sum(inside)))),
        'RF_tidal_wetland_probability_mean_source_valid_pixels':
             float(values.mean()) if len(values) else None,
        'fraction_valid_source_pixels_RF_agreement_ge20':
             float(np.mean(values>=20)) if len(values) else None,
        'fraction_valid_source_pixels_RF_agreement_ge50':
             float(np.mean(values>=50)) if len(values) else None,
        'no_habitat_area_no_tidalflat_specificity_no_instantaneous_exposure':True}

def run(v94dir,v105artifact,band,output):
    files=list(Path(v94dir).rglob('v94-2019-original-source-*.json'))
    if len(files)!=12:raise ValueError('STOP_NO_GENUINE_V94_12_ORIGINAL_STATION_SOURCE_BANDS')
    s,select=choose_station_by_original_UID(files,band)
    aff=read_original_geotransform(v105artifact)
    out={'analysis':'V106_2019_UHSLC_TIDAL_WETLAND_2017_2019_GENUINE_NATIVE_GIC_10KM_GEODESIC_PROXIMITY_PILOT',
        '2019_original_UHSLC_station_id':s['uid'],
        '2019_original_UHSLC_band':band,
        'station_country_source':s['country'],
        'original_source_coords_public':[s['longitude_signed'],s['latitude']],
        '2019_measured_gauge_mean_abs_M':s['opportunity']['mean_daily_abs_M'],
        '2019_measured_gauge_form_factor_F':s['form_factor_F'],
        'selection':select,
        'source_v105_run':PARENT_V105_RUN,
        'source_v94_original_run':GLOBAL_V94_RUN,
        'source_status':'SOURCE_NOT_ADMITTED',
        'no_observed_bird_or_real_dry_tidalflat':True}
    try:
        tile=native_expected_tile(float(s['latitude']),float(s['longitude_signed']),aff)
        out['derived_tile_grid_source_only']=tile
        meta=metadata_for_native_tile(tile)
        out['native_GCS_original_object_provenance']=meta
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'original_valid_GIC2019_t7.tif'
            confirmed=download_and_verify_original_gcs_tile(meta,path)
            out['source_MD5_gate']=confirmed
            with rasterio.open(path) as ds:
                if ds.transform.is_degenerate or ds.crs is None:
                    raise ValueError('SOURCE_STOP_ORIGINAL_GCS_AFFINE_OR_CRS_INVALID')
                c_expected=aff.c+tile['expected_colstart_original_pixels']*aff.a
                f_expected=aff.f+tile['expected_rowstart_original_pixels']*aff.e
                if abs(ds.transform.a-aff.a)>1e-10 or abs(ds.transform.e-aff.e)>1e-10 or (
                    abs(ds.transform.c-c_expected)>abs(aff.a)*1.1 or
                    abs(ds.transform.f-f_expected)>abs(aff.e)*1.1):
                    raise ValueError('SOURCE_STOP_ORIGINAL_GCS_NATIVE_TILE_GRID_MISREGISTERED')
                row,col=ds.index(s['longitude_signed'],s['latitude'])
                if not (0<=row<ds.height and 0<=col<ds.width):
                    raise ValueError('SOURCE_STOP_REAL_GAUGE_LOCATION_NOT_INSIDE_EXPECTED_NATIVE_TILE')
                out['raster_original_geo']={'crs':ds.crs.to_string(),
                    'bounds':list(ds.bounds),'native_raster_width':ds.width,
                    'native_raster_height':ds.height,'native_nodata':ds.nodata,
                    'source_original_pixel_resolution_native':list(ds.res)}
                out['true_2019_gauge_10km_static_tidal_wetland_RF_agreement']=(
                    source_10km_wetland_probability(ds,float(s['latitude']),float(s['longitude_signed'])))
                r=out['true_2019_gauge_10km_static_tidal_wetland_RF_agreement']
                out['source_status']='ORIGINAL_2019_GIC_PROBABILITY_BUFFER_ADMITTED' if (
                    r.get('n_valid_original_GIC_pixels_10km',0)>0 and
                    r.get('complete_10km_circle_in_this_tile',False)
                    ) else 'ORIGINAL_2019_GIC_TILED_BUFFER_PARTIAL_OR_EMPTY'
    except SourceUnavailable as e:
        out['source_status']='SOURCE_UNAVAILABLE_OR_OUTSIDE_SINGLE_TILE_SOURCE_COVERAGE'
        out['source_failure_reason']=str(e)
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V106_ORIGINAL_TRUE_GIC_GAUGE_BUFFER '+json.dumps({
        'band':band,'UHSLC_id':s['uid'],'status':out['source_status'],
        'native_tile':(out.get('derived_tile_grid_source_only') or {}).get('native_GCS_tile_name'),
        'n_valid_RF_wetland_pixels':(out.get('true_2019_gauge_10km_static_tidal_wetland_RF_agreement') or {}).get('n_valid_original_GIC_pixels_10km'),
        'mean_RF_agreement':(out.get('true_2019_gauge_10km_static_tidal_wetland_RF_agreement') or {}).get('RF_tidal_wetland_probability_mean_source_valid_pixels'),
        'fraction_RF_ge50':(out.get('true_2019_gauge_10km_static_tidal_wetland_RF_agreement') or {}).get('fraction_valid_source_pixels_RF_agreement_ge50'),
        'original_failure':out.get('source_failure_reason'),
        'NO_REAL_DRY_FLAT_OR_BIRD_NICHE':True},sort_keys=True),flush=True)
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument('--v94-source-dir',required=True)
    p.add_argument('--v105-original-geo-audit',required=True)
    p.add_argument('--band',required=True,choices=POLICY_BANDS)
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.v94_source_dir,a.v105_original_geo_audit,a.band,a.output)
