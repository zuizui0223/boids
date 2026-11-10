"""v116: real 2019 Oosterschelde ground-elevation source (DTM, not DSM).
Use only original published RWS 2019 DTM 5m/2m GeoTIFF or official WCS raster,
not colorized WMS image, current 2025 bathymetry, synthetic elevations or GPS.
Fixed four landmark probe regions WITHOUT selecting bird/habitat outcomes.
NO observed foraging, local 2020 dry tideflat, or species temporal niche.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.io import MemoryFile
from pyproj import Transformer

ROOT="https://downloads.rijkswaterstaatdata.nl/hoogte_2019/"
WCS="https://geo.rijkswaterstaat.nl/services/ogc/gdr/hoogte_2019/ows"
LAYER={
  "dtm_5":{"id":"hoogte_2019:oosterschelde_2019_dtm_5",
            "filename":"oosterschelde_2019_dtm_5.tif","source_nominal_resolution_m":5.},
  "dtm_2":{"id":"hoogte_2019:oosterschelde_2019_dtm_2",
            "filename":"oosterschelde_2019_dtm_2.tif","source_nominal_resolution_m":2.}}
PRIMARY="dtm_5"
SECONDARY="dtm_2"
SOURCE_YEAR=2019
MAX_ORIGINAL_SOURCE_MEGABYTES=150
MAX_GETCOVERAGE_MEGABYTES=8
MAX_XML_BYTES=5_000_000
PROBE_RADIUS_METRES=50.
PROBE_QA={
 "Roompotsluis Buiten gauge":{"lat":51.619722,"lon":3.681944,
      "physical_waterbody_source":"North Sea side fixed original 2020 RWS external tide gauge"},
 "Roggenplaat shoal":{"lat":51.66398,"lon":3.79130,
      "physical_waterbody_source":"Oosterschelde shoal from GeoNames, NOT an original bird GPS position"},
 "Neeltje Jans island":{"lat":51.631944,"lon":3.698889,
      "physical_waterbody_source":"barrier island; actual wet/dry marsh interpretation NOT automatic"},
 "Roompot Marina":{"lat":51.59357,"lon":3.71752,
      "physical_waterbody_source":"marine harbor, inside/outside hydrodynamic link NOT validated"}}
TIF_SIGNATURES=(b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+')
RD=Transformer.from_crs("EPSG:4326","EPSG:28992",always_xy=True)
WGS=Transformer.from_crs("EPSG:28992","EPSG:4326",always_xy=True)

class SourceNotAvailable(Exception):pass

def _request(url,timeout=45,method='GET'):
    if not (url.startswith(ROOT) or url.startswith(WCS)):
        raise ValueError('STOP_NOT_ORIGINAL_RWS_2019_GROUND_DTM_PUBLISHER')
    return Request(url,method=method,headers={
      'Accept':'application/xml,application/octet-stream,image/tiff,*/*',
      'User-Agent':'boids-v116-2019-RWS-Oosterschelde-original-DTM-ground-elevation-source-only/1.0'})

def _try_publisher_metadata(url,method='HEAD'):
    try:
        with urlopen(_request(url,method=method),timeout=35) as r:
            return {'source_http_code':r.status,'content_type':r.headers.get('Content-Type'),
               'native_content_length':r.headers.get('Content-Length'),
               'source_last_modified':r.headers.get('Last-Modified'),
               'source_etag':r.headers.get('ETag'),
               'source_accept_ranges':r.headers.get('Accept-Ranges'),
               'official_original_filename_url':url,'status':'ORIGINAL_SOURCE_METADATA_ACCESSIBLE'}
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        return {'status':'SOURCE_METADATA_UNAVAILABLE','error_type':type(e).__name__,
                'error_str':str(e)[:180], 'official_original_filename_url':url}

def original_catalog_XML(service,params):
    url=WCS+'?'+urlencode(params,doseq=True)
    try:
        with urlopen(_request(url),timeout=35) as r:raw=r.read(MAX_XML_BYTES+1)
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        return {'original_source_status':'SOURCE_UNAVAILABLE_OFFICIAL_WCS','source_error':str(e)[:180]}
    if len(raw)>MAX_XML_BYTES: return {'original_source_status':'SOURCE_XML_SIZE_EXCEEDED'}
    try:root=ET.fromstring(raw)
    except ET.ParseError as e:
        return {'original_source_status':'SOURCE_RETURNED_NON_XML', 'raw_content_SHA256':hashlib.sha256(raw).hexdigest()}
    coverage=[]
    for elem in root.iter():
        if elem.tag.rsplit('}',1)[-1] in ('CoverageId','Identifier'):
            if elem.text and 'oosterschelde_2019_dtm' in elem.text.lower():
                coverage.append(elem.text.strip())
    return {'original_source_status':'OFFICIAL_RWS_WCS_METADATA_RECEIVED',
       'url_public_provider':url,'source_raw_SHA256':hashlib.sha256(raw).hexdigest(),
       'native_root_element':root.tag,'returned_2019_Oosterschelde_DTM_ids':sorted(set(coverage)),
       'raw_bytes':len(raw),
       'XML_contains_vertical_datum_NAP':b'NAP' in raw or b'nap' in raw}

def _download_original_raster(fixed,url,source_id):
    """Single original published raw TIFF, never a map render; capped safety."""
    lim=MAX_ORIGINAL_SOURCE_MEGABYTES*1_000_000
    hh=hashlib.sha256()
    n=0
    try:
        with urlopen(_request(url),timeout=110) as src, open(fixed,'wb') as out:
            while True:
                chunk=src.read(1_048_576)
                if not chunk:break
                n+=len(chunk)
                if n>lim:raise SourceNotAvailable('ORIGINAL_RWS_GEOTIFF_OVER_FROZEN_150MB_LIMIT')
                hh.update(chunk);out.write(chunk)
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        raise SourceNotAvailable('ORIGINAL_RWS_DTM_TIFF_DOWNLOAD_FAILURE_'+str(e)[:120]) from e
    with open(fixed,'rb') as stream:sig=stream.read(4)
    if sig not in TIF_SIGNATURES:
        raise SourceNotAvailable('ORIGINAL_RWS_DTM_NATIVE_FILE_NOT_TIFF_NO_WMS_OR_HTML_ALLOWED')
    return {'original_file_url':url,'source_native_file_bytes':n,
       'original_locally_downloaded_SHA256':hh.hexdigest(),
       'source_file_content':'ORIGINAL_UNRENDERED_TIFF_NOT_HTML_OR_WMS',
       'source_checksum_note':'SHA256 computed on original downloaded bytes, publisher checksum not supplied',
       'source_original_requested_layer':source_id}

def _wcs_native_raster_window(layer,lon,lat):
    """Fallback GetCoverage raw source TIFF with fixed native RD x/y 100m
    window; no WMS snapshots or arbitrary favorable coastal pixel picks.
    """
    x,y=RD.transform(lon,lat)
    r=PROBE_RADIUS_METRES
    params=[
      ('service','WCS'),('request','GetCoverage'),('version','2.0.1'),
      ('CoverageID',LAYER[layer]['id']),('format','image/tiff'),
      ('subset',f'x({x-r:.2f},{x+r:.2f})'),
      ('subset',f'y({y-r:.2f},{y+r:.2f})')]
    url=WCS+'?'+urlencode(params,doseq=True)
    try:
        with urlopen(_request(url),timeout=65) as stream:
            b=stream.read(MAX_GETCOVERAGE_MEGABYTES*1_000_000+1)
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        raise SourceNotAvailable('OFFICIAL_DTM_WCS_GEOTIFF_SUBSET_REQUEST_FAILURE_'+str(e)[:120]) from e
    if len(b)>MAX_GETCOVERAGE_MEGABYTES*1_000_000 or b[:4] not in TIF_SIGNATURES:
        raise SourceNotAvailable('OFFICIAL_WCS_NOT_SOURCE_TIFF_OR_SOURCE_TOO_LARGE')
    return b,{'original_source_provider_URL':url,'source_WCS_CoverageID':LAYER[layer]['id'],
       'original_source_response_SHA256':hashlib.sha256(b).hexdigest(),
       'source_original_TIFF_bytes':len(b),
       'source_no_WMS_pixel_rendering':True}

def _raster_geo_QA(ds):
    if ds.crs is None or ds.transform.is_degenerate or ds.count!=1:
        raise SourceNotAvailable('ORIGINAL_RWS_DTM_SOURCE_MISSING_VALID_CRS_OR_SINGLE_ELEVATION_BAND')
    unit=ds.units[0] if ds.units else None
    tags={**ds.tags(),**ds.tags(1)}
    return {'original_raster_source_CRS':ds.crs.to_string(),
        'original_raster_native_width':ds.width,'original_raster_native_height':ds.height,
        'original_raster_source_pixel_size':list(ds.res),
        'original_raster_native_nodata':ds.nodata,
        'original_raster_source_band_unit_tag':unit,
        'original_raster_source_tags_subset':{k:str(v)[:160] for k,v in tags.items() if k.lower() in (
            'units','vertical_datum','vert_datum','datum','description','area_or_point','source','date','unit_type')},
        'original_mask_flags':[[str(v) for v in x] for x in ds.mask_flag_enums],
        'original_source_horizontal_bounds':list(ds.bounds),
        'original_source_NAP_vertical_tag_present':any('NAP' in str(v).upper() for v in tags.values())}

def _single_original_lidar_probe(ds,name,place):
    if ds.crs is None:raise SourceNotAvailable('SOURCE_DTM_CRS_UNAVAILABLE')
    xf=Transformer.from_crs('EPSG:4326',ds.crs,always_xy=True)
    x,y=xf.transform(place['lon'],place['lat'])
    radius=PROBE_RADIUS_METRES
    try:
        row,col=ds.index(x,y)
        pix=max(1,int(math.ceil(radius/min(abs(ds.res[0]),abs(ds.res[1])))))
        row0=max(0,row-pix);row1=min(ds.height,row+pix+1)
        col0=max(0,col-pix);col1=min(ds.width,col+pix+1)
        if row0>=row1 or col0>=col1:
            return {'original_source_fixed_probe':name,
               'source_status':'OUTSIDE_THIS_ORIGINAL_DTM_RASTER_NOT_ZERO_HEIGHT'}
        v=ds.read(1,window=Window(col0,row0,col1-col0,row1-row0),masked=True)
        valid=v.compressed()
        center=ds.read(1,window=Window(col,col,1,1),masked=True) if False else None
        # No assumption that a 100 m tile is fully flat; keep native nodata.
        return {'original_source_fixed_probe':name,
           'source_status':'VALID_ORIGINAL_DTM_PLOT' if len(valid)>0 else 'ORIGINAL_DTM_SOURCE_NO_VALID_Z_AT_PLOT',
           'original_probe_public_lonlat':[place['lon'],place['lat']],
           'original_native_source_RD_XY_m':[round(x,3),round(y,3)],
           'source_raster_center_row_col':[int(row),int(col)],
           'source_probe_bbox_approx_100m':True,
           'original_total_native_raster_pixels_in_sample':int(v.size),
           'original_valid_ground_height_native_pixels':int(len(valid)),
           'original_masked_ground_height_native_pixels':int(v.size-len(valid)),
           'source_native_ground_height_min':float(valid.min()) if len(valid) else None,
           'source_native_ground_height_max':float(valid.max()) if len(valid) else None,
           'source_native_ground_height_median':float(np.median(valid)) if len(valid) else None,
           'source_native_ground_height_q25_q75':[float(np.quantile(valid,q)) for q in (.25,.75)] if len(valid) else None,
           'site_waterbody_source_uncertainty':place['physical_waterbody_source']}
    except (ValueError,rasterio.errors.RasterioError) as e:
        return {'original_source_fixed_probe':name,
           'source_status':'NATIVE_RASTER_GEO_OR_MASK_STOP',
           'source_error':str(e)[:180]}
def run(output):
    report={'analysis':'V116_2019_OOSTERSCHELDE_ORIGINAL_GROUND_DTM_5M_2M_REAL_RWS_SOURCE_QA',
      'source_catalogue_2019_RWS_DTM_not_DSM':True,
      'source_original_2019_collected_year_note':'catalogue says 2019 and refers to AHN3 2018 source; not exact 2020 seabed',
      'source_original_2020_RWS_gauge_data_not_automatically_local_DTM_tide':True,
      'NOT_ACTUAL_EXPOSED_TIDALFLAT_OR_ANY_NEW_GULL_TIME_NICHE':True,
      'fixed_original_geo_probes':PROBE_QA,
      'source_status':'SOURCE_PENDING','primary':PRIMARY,'secondary':SECONDARY,
      'publisher_files':{},'source_WCS_catalogue':{},'native_raster_admission':{}}
    cap=original_catalog_XML('WCS',{'service':'WCS','request':'GetCapabilities','version':'2.0.1'})
    report['source_WCS_catalogue']['capabilities']=cap
    for name in (PRIMARY,SECONDARY):
        origin=LAYER[name]
        direct=ROOT+origin['filename']
        report['publisher_files'][name]=_try_publisher_metadata(direct,'HEAD')
        desc=original_catalog_XML('WCS',{'service':'WCS','request':'DescribeCoverage',
          'version':'2.0.1','CoverageID':origin['id']})
        report['source_WCS_catalogue'][name+'_description']=desc
        source_result={'original_RWS_DTM_layer':origin,'source_status':'SOURCE_UNAVAILABLE',
                        'original_fixed_probe_results':[]}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'authentic_source_DTM.tif'
            try:
                receipt=_download_original_raster(path,direct,origin['id'])
                with rasterio.open(path) as ds:
                    source_result['authentic_original_raster_source']=receipt
                    source_result['original_raster_metadata']=_raster_geo_QA(ds)
                    source_result['original_fixed_probe_results']=[
                        _single_original_lidar_probe(ds,k,v) for k,v in PROBE_QA.items()]
                    source_result['source_status']='DIRECT_ORIGINAL_RWS_2019_DTM_RASTER_READ'
            except (SourceNotAvailable,rasterio.errors.RasterioError) as e:
                source_result['direct_original_source_blocker']=str(e)[:190]
                # Source 100m WCS GetCoverage fallback, never interpret error XML as raster.
                for k,v in PROBE_QA.items():
                    try:
                        b,receipt=_wcs_native_raster_window(name,v['lon'],v['lat'])
                        with MemoryFile(b) as m:
                            with m.open() as ds:
                                x=_raster_geo_QA(ds)
                                q=_single_original_lidar_probe(ds,k,v)
                        source_result['original_fixed_probe_results'].append({
                             **q,'native_WCS_original_response':receipt,
                             'source_original_CRS':x['original_raster_source_CRS'],
                             'source_original_pixel_unit_tag':x['original_raster_source_band_unit_tag'],
                             'source_NAP_native_raster_tag_present':x['original_source_NAP_vertical_tag_present']})
                    except (SourceNotAvailable,rasterio.errors.RasterioError) as e2:
                        source_result['original_fixed_probe_results'].append({
                            'original_source_fixed_probe':k,'source_status':'SOURCE_UNAVAILABLE_NOT_ZERO_GROUND_HEIGHT',
                            'source_stop_reason':str(e2)[:160]})
                if any(x['source_status']=='VALID_ORIGINAL_DTM_PLOT' for x in source_result['original_fixed_probe_results']):
                    source_result['source_status']='SOURCE_ADMITTED_OFFICIAL_2019_WCS_SUBSET_RASTER'
            report['native_raster_admission'][name]=source_result
        print('V116_TRUE_OOSTERSCHELDE_DTM_YEAR2019_LAYER '+json.dumps({
            'name':name,'source_status':source_result['source_status'],
            'original_DTM_CRS':(source_result.get('original_raster_metadata') or {}).get('original_raster_source_CRS'),
            'real_fixed_original_lidar_probes':source_result['original_fixed_probe_results'],
            'source_direct_blocker':source_result.get('direct_original_source_blocker')},
            sort_keys=True),flush=True)
    if any(v['source_status'] in ('DIRECT_ORIGINAL_RWS_2019_DTM_RASTER_READ',
        'SOURCE_ADMITTED_OFFICIAL_2019_WCS_SUBSET_RASTER') for v in report['native_raster_admission'].values()):
        report['source_status']='ORIGINAL_2019_OOSTERSCHELDE_DTM_RASTER_SOURCE_ADMITTED'
    else:report['source_status']='SOURCE_NOT_ADMITTED_NO_GROUND_HEIGHT_OR_DRYNESS_ESTIMATED'
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('V116_TRUE_2019_RWS_GROUND_DTM_GEO_SOURCE_FINAL '+json.dumps({
        'status':report['source_status'],
        'original_layer_status':{k:v['source_status'] for k,v in report['native_raster_admission'].items()},
        'n_original_fixed_probes_valid_ground_height':{
            k:sum(x['source_status']=='VALID_ORIGINAL_DTM_PLOT' for x in v['original_fixed_probe_results'])
             for k,v in report['native_raster_admission'].items()},
        'source_NAP_vertical_metadata_MUST_be_verified_before_2020_gauge_tide_comparison':True,
        'NO_gull_behavior_or_true_2020_exposed_flat_hours':True},sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
