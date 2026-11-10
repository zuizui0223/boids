"""v120 Deltares original THREDDS source-only multi-tile historical Vaklodingen audit.

Find authentic SOURCE catalog listing and small NetCDF tile index. Do NOT
equate server modified date, interpolated tide/terrain, or tile name with
2019/2020 actual original Zeeland seabed measurements. NO animal results.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import xml.etree.ElementTree as ET
from tempfile import TemporaryDirectory
import numpy as np
from netCDF4 import Dataset

SERVER='https://opendap.deltares.nl/thredds/'
SOURCES={
 '2020_release_documented':SERVER+'catalog/opendap/rijkswaterstaat/vaklodingen_new/catalog.xml',
 'older_tile_collection':SERVER+'catalog/opendap/rijkswaterstaat/vaklodingen/catalog.xml'}
FALLBACK_HTML={
 '2020_release_documented':SERVER+'catalog/opendap/rijkswaterstaat/vaklodingen_new/catalog.html',
 'older_tile_collection':SERVER+'catalog/opendap/rijkswaterstaat/vaklodingen/catalog.html'}
OLD_NATIVE_CATALOG=SERVER+'fileServer/opendap/rijkswaterstaat/vaklodingen/catalog.nc'
MAX_XML=3_000_000;MAX_HTML=2_000_000;MAX_CATALOG_NC=2_000_000
FIXED_ZEELAND_RD_POINT_CLOUD={
  'Roompotsluis Buiten gauge':(36911.979,404810.4),
  'Roggenplaat shoal':(44591.863,409561.762),
  'Neeltje Jans island':(38116.787,406142.536),
  'Roompot Marina':(39308.592,401844.365)}
EXTENT_NEEDS_NATIVE_CRS_AND_PIXEL_MASK=True
ALLOWED_URLS=set(SOURCES.values())|set(FALLBACK_HTML.values())|{OLD_NATIVE_CATALOG}
MAGIC=(b'CDF\x01',b'CDF\x02',b'\x89HDF')

def get_original_source(url,limit):
    if url not in ALLOWED_URLS:
        raise ValueError('STOP_NONDELTA_FIRSTPARTY_OR_UNFROZEN_VAKLO_SOURCE')
    req=Request(url,headers={
       'Accept':'application/xml,text/html,application/x-netcdf,application/octet-stream,*/*',
       'User-Agent':'boids-v120-source-only-2020-era-vaklodingen-THREDDS-catalog/1.0'})
    try:
        with urlopen(req,timeout=48) as resp:
            raw=resp.read(limit+1)
            content_type=resp.headers.get('Content-Type')
            effective=resp.geturl()
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        raise RuntimeError('SOURCE_UNAVAILABLE_DELTA_THREDDS_'+str(e)[:180]) from e
    if len(raw)>limit:raise RuntimeError('STOP_SOURCE_CATALOG_OVER_FROZEN_TRANSFER_LIMIT')
    if not effective.startswith('https://opendap.deltares.nl/thredds/'):
        raise RuntimeError('STOP_UNVERIFIED_THREDDS_PROVIDER_REDIRECT')
    return raw,{'genuine_original_publisher_URL':url,
         'downloaded_native_metadata_bytes':len(raw),
         'native_source_response_SHA256':hashlib.sha256(raw).hexdigest(),
         'original_ContentType':content_type,
         'source_HTTPS_provider_verified':True}

def parse_true_catalog_xml(raw):
    try:root=ET.fromstring(raw)
    except ET.ParseError as e:raise RuntimeError('STOP_ORIGINAL_THREDDS_NOT_XML') from e
    if not root.tag.rsplit('}',1)[-1]=='catalog':
        raise RuntimeError('STOP_ORIGINAL_THREDDS_XML_NOT_CATALOG')
    files=[];sizes={}
    for el in root.iter():
        name=el.tag.rsplit('}',1)[-1]
        if name=='dataset':
            filename=el.get('name') or ''
            urlpath=el.get('urlPath') or ''
            if filename.endswith('.nc') or urlpath.endswith('.nc'):
                files.append({'source_dataset_name':filename,'source_urlPath':urlpath,
                             'original_dataset_ID':el.get('ID')})
        if name=='dataSize':
            pass
    unique={x['source_urlPath'] or x['source_dataset_name']:x for x in files}
    tiles=sorted([v for v in unique.values() if re.fullmatch(
            r'vaklodingenKB\d+_\d+\.nc',v['source_dataset_name'])])
    references=sorted([v for v in unique.values() if v not in tiles],key=lambda z:z['source_dataset_name'])
    return {'source_native_catalog_parse_status':'ORIGINAL_XML_THREDDS_CATALOG_PARSE_AUTHENTICATED',
       'original_root_XML_tag':root.tag,
       'n_distinct_original_tile_NC':len(tiles),
       'n_auxiliary_NC':len(references),
       'original_all_tile_source_names_sorted':[v['source_dataset_name'] for v in tiles],
       'original_auxiliary_source_file_names':[v['source_dataset_name'] for v in references],
       'original_full_tile_catalog_SHA256_names':hashlib.sha256((
           '\n'.join(v['source_dataset_name'] for v in tiles)).encode()).hexdigest(),
       'native_catalog_geographical_relevance':'NOT_ESTABLISHED_FROM_TILE_NAMES',
       'native_2020_true_survey_year':'NOT_ESTABLISHED_FROM_SERVER_RELEASE_OR_FILE_MODIFIED'}

def parse_original_catalog_html(raw):
    html=raw.decode('utf-8-sig',errors='strict')
    if 'thredds' not in html.lower() and 'Catalog' not in html:
        raise RuntimeError('STOP_NOT_THREDDS_NATIVE_HTML_CATALOG')
    # HTML is a Fallback publisher listing, NOT an original XML+CF survey claim.
    names=sorted(set(re.findall(r'vaklodingenKB[0-9]+_[0-9]+\.nc',html)))
    return {'source_native_catalog_parse_status':'FIRSTPARTY_HTML_LISTING_ONLY_NOT_NATIVE_XML',
      'n_distinct_original_tile_NC':len(names),
      'original_all_tile_source_names_sorted':names,
      'original_full_tile_catalog_SHA256_names':hashlib.sha256(
           '\n'.join(names).encode()).hexdigest(),
      'native_catalog_geographical_relevance':'NOT_ESTABLISHED',
      'native_2020_true_survey_year':'NOT_ESTABLISHED',
      'original_source_HTML_has_no_valid_actual_seabed_pixels':True}

def source_native_small_index(raw,folder):
    if not any(raw.startswith(sig) for sig in MAGIC):
        raise RuntimeError('STOP_SMALL_ORIGINAL_THREDDS_INDEX_NOT_NETCDF_MAGIC')
    path=Path(folder)/'publisher_catalog.nc'
    path.write_bytes(raw)
    with Dataset(path,'r') as ds:
        meta={k:str(ds.getncattr(k))[:220] for k in ds.ncattrs()
              if k.lower() in ('title','source','summary','conventions','history',
                              'spatial_ref','crs','epsg','vertical_datum',
                              'time_coverage_start','time_coverage_end')}
        variables={}
        for name,v in ds.variables.items():
            attrs={k:str(v.getncattr(k))[:150] for k in v.ncattrs()
                   if k.lower() in ('units','long_name','standard_name','grid_mapping',
                                     'spatial_ref','calendar','time_coverage_start','time_coverage_end')}
            result={'dims':list(v.dimensions),'shape':list(v.shape),
                    'source_native_attrs':attrs}
            # Only small 1D numeric coordinate vectors; no full seabed array.
            if v.ndim==1 and v.size<=50000 and v.dtype.kind in ('i','f','u'):
                rawvalues=np.ma.array(v[:],copy=False).compressed()
                values=np.asarray(rawvalues,dtype=float)
                values=values[np.isfinite(values)]
                if len(values):
                    result['numeric_1d_native_extent']=[float(values.min()),float(values.max())]
            variables[name]=result
        return {'original_small_catalog_nc_SHA256':hashlib.sha256(raw).hexdigest(),
           'native_index_bytes':len(raw),'original_source_global_attrs':meta,
           'original_source_index_native_variables':variables,
           'index_is_not_measurement_of_2020_bird_seabed_or_tidalflat':True}

def run(output):
    out={'analysis':'V120_FIRSTPARTY_DELTA_OLD_AND_2020_THREDDS_VAKLO_NETCDF_TILES_SOURCE_CATALOG',
      'fixed_4_Zeeland_native_RD_point_reference':FIXED_ZEELAND_RD_POINT_CLOUD,
      'native_2019_2020_survey_year_and_NAP_requirements_not_assumed':True,
      'source_data_is_NOT_2020_gull_time_niche_or_full_dryflat':True,
      'catalogs':{},'native_small_index':{},'source_status':'SOURCE_PENDING'}
    for key,url in SOURCES.items():
        try:
            raw,receipt=get_original_source(url,MAX_XML)
            data=parse_true_catalog_xml(raw)
            out['catalogs'][key]={**receipt,**data}
        except (RuntimeError,ValueError) as e:
            out['catalogs'][key]={'native_firstparty_original_XML_source_status':'SOURCE_NOT_AVAILABLE_OR_MALFORMED',
                                  'original_failure':str(e)[:180]}
            # A documented HTML source is a weaker catalog listing fallback,
            # never a NetCDF measured value or a verified 2020 survey year.
            try:
                html,receipt=get_original_source(FALLBACK_HTML[key],MAX_HTML)
                data=parse_original_catalog_html(html)
                out['catalogs'][key]['original_public_HTML_catalog_fallback']={**receipt,**data}
            except (RuntimeError,UnicodeDecodeError,ValueError) as e2:
                out['catalogs'][key]['html_fallback_source_stop']=str(e2)[:180]
        c=out['catalogs'][key]
        valid=(c.get('n_distinct_original_tile_NC') or (
            c.get('original_public_HTML_catalog_fallback') or {}).get('n_distinct_original_tile_NC'))
        print('V120_DELTA_VAKLO_PUBLISHER_CATALOG_SOURCE '+json.dumps({
           'catalog':key,'native_XML_status':c.get('source_native_catalog_parse_status'),
           'native_source_tile_count':valid,'source_original_error':c.get('original_failure'),
           'original_tile_index_not_2020_survey':True},sort_keys=True),flush=True)
    try:
        raw,receipt=get_original_source(OLD_NATIVE_CATALOG,MAX_CATALOG_NC)
        with TemporaryDirectory() as temp:
            info=source_native_small_index(raw,temp)
        out['native_small_index']={**receipt,**info,'source_status':'ORIGINAL_SMALL_INDEX_METADATA_ADMITTED'}
    except (RuntimeError,ValueError,OSError) as e:
        out['native_small_index']={'source_status':'SMALL_ORIGINAL_INDEX_NOT_ADMITTED',
                                 'original_failure':str(e)[:180]}
    print('V120_REAL_DELTA_BATHY_ORIGINAL_NATIVE_INDEX '+json.dumps({
        'source_status':out['native_small_index']['source_status'],
        'original_source_native_dims':{k:v['shape'] for k,v in
         out['native_small_index'].get('original_source_index_native_variables',{}).items()},
        'original_index_metadata_original_time_range_only_not_real_2020_source':True},sort_keys=True),flush=True)
    if any(c.get('n_distinct_original_tile_NC',0)>0 or
           (c.get('original_public_HTML_catalog_fallback') or {}).get('n_distinct_original_tile_NC',0)>0
           for c in out['catalogs'].values()):
        out['source_status']='ORIGINAL_DELTA_MULTI_TILE_INDEX_ADMITTED_NOT_LOCAL_HISTORICAL_SURVEYS'
    else:out['source_status']='NATIVE_CATALOG_ACCESS_BLOCKED'
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V120_REAL_DELTA_THREDDS_VAKLO_SOURCE_FINAL '+json.dumps({
       'source_status':out['source_status'],
       'catalog_summaries':{k:{'n_true_XML_tiles':v.get('n_distinct_original_tile_NC'),
              'n_fallback_HTML_tiles':(v.get('original_public_HTML_catalog_fallback') or {}).get('n_distinct_original_tile_NC'),
              'native_error':v.get('original_failure')}
              for k,v in out['catalogs'].items()},
       'small_native_index_status':out['native_small_index']['source_status'],
       'no_Local_Zeeland_bathymetry_or_2020_survey_Y_identified':True},sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
