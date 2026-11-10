"""v119 FIRST SOURCE feasibility of historical 2019 and 2020 RWS Vaklodingen
soundings in authentic OpenEarth archive, NOT a filled Zeeland coastline
raster, true 2020 accessible bottom, or any bird use/foraging outcome.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import numpy as np
from netCDF4 import Dataset
from pyproj import Transformer,CRS

PREFIX="https://rwsprojectarchief.openearth.nl/downloads/kustgenese2/bathymetrie/Vaklodingen/"
NATIVE_ORIGINAL={
 '2019':('20190712_vaklodingen.nc',3594788),
 '2020':('20200717_vaklodingen.nc',3991532)}
MAX_ORIGINAL_BYTES=20_000_000
NO_ECOLOGICAL_USED_AVAILABLE_BEHAVIOR=True
FIXED_SITE_WGS84={
 "Roompotsluis Buiten gauge":(51.619722,3.681944),
 "Roggenplaat shoal":(51.66398,3.79130),
 "Neeltje Jans island":(51.631944,3.698889),
 "Roompot Marina":(51.59357,3.71752)}
SIGNATURES=(b'CDF\x01',b'CDF\x02',b'\x89HDF')
SOURCE_FROZEN_COORDINATE_VARIABLES=('x','y','lon','lat','longitude','latitude','easting','northing')
BATHY_ELEVATION_PRIORITY=('z','bed_level','bedlevel','height','elevation','bottom_depth','depth','waterdepth')

class SourceStop(Exception):pass

def download_original_snapshot(native,expected,dest):
    if native not in [v[0] for v in NATIVE_ORIGINAL.values()]:
        raise ValueError('STOP_V119_UNFROZEN_ORIGINAL_2019_2020_RWS_VAKLO_FILE')
    url=PREFIX+native
    request=Request(url,headers={'Accept':'application/x-netcdf,application/octet-stream,*/*',
        'User-Agent':'boids-v119-historical-RWS-original-Vaklodingen-Dutch-coast-source-only/1.0'})
    try:
        with urlopen(request,timeout=70) as r:
            b=r.read(MAX_ORIGINAL_BYTES+1)
            content_type=r.headers.get('Content-Type')
            last_modified=r.headers.get('Last-Modified')
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        raise SourceStop('ORIGINAL_OPENEARTH_RWS_VAKLO_SOURCE_HTTP_OR_TRANSPORT_'+str(e)[:170]) from e
    if len(b)!=expected or len(b)>MAX_ORIGINAL_BYTES:
        raise SourceStop('STOP_ORIGINAL_ARCHIVE_RWS_FILE_BYTES_CHANGED_OR_LIMIT_EXCEEDED')
    if not any(b.startswith(sig) for sig in SIGNATURES):
        raise SourceStop('STOP_ORIGINAL_VAKLO_ARCHIVE_RETURNED_NON_NETCDF_HTML_OR_ERROR')
    Path(dest).write_bytes(b)
    return {'original_native_URL':url,'original_source_Bytes':len(b),
        'original_source_SHA256':hashlib.sha256(b).hexdigest(),
        'original_header_content_type':content_type,
        'original_last_modified':last_modified,
        'source_netcdf_magic_verified':True,
        'source_publisher_checksum_not_available_locally_SHAs_computed_on_actual_bytes':True}

def safe_array_extent(var):
    try:
        a=np.ma.array(var[:],copy=False)
        if a.size>5_000_000:return {'status':'SOURCE_ARRAY_TOO_LARGE_COORDINATE_EXTENT_NOT_EXTRACTED'}
        data=a.compressed().astype(float)
        if not len(data):
            return {'status':'NO_FINITE_COORDINATE_SOURCE'}
        finite=data[np.isfinite(data)]
        if not len(finite):return {'status':'NO_FINITE_COORDINATE_SOURCE'}
        return {'status':'SOURCE_ARRAY_FINITE',
          'n_native_finite_values':int(len(finite)),
          'min_source_value':float(np.min(finite)),
          'max_source_value':float(np.max(finite))}
    except (ValueError,TypeError,IndexError,OSError,OverflowError) as e:
        return {'status':'SOURCE_ARRAY_UNREADABLE',
                'reason':str(e)[:100]}

def _attributes(v):
    out={}
    for name in v.ncattrs():
        value=v.getncattr(name)
        if isinstance(value,np.ndarray):value=value.tolist()
        if isinstance(value,(list,tuple)):
            value=str(value[:5])[:220]
        else:value=str(value)[:220]
        if name.lower() in ('units','standard_name','long_name','positive','grid_mapping',
                             'crs','epsg_code','spatial_ref','axis','calendar','coordinates',
                             'vertical_datum','source','date','time_coverage_start','time_coverage_end'):
            out[name]=value
    return out

def geo_source_first(path,original_year):
    with Dataset(path,'r') as ds:
        glob={k:str(ds.getncattr(k))[:300] for k in ds.ncattrs()
              if k.lower() in ('title','institution','history','source','institution',
                  'summary','projection','crs','epsg','epsg_code','spatial_ref',
                  'vertical_datum','time_coverage_start','time_coverage_end','date_created')}
        variables={}
        for name,v in ds.variables.items():
            variables[name]={'original_dim_names':list(v.dimensions),
                'native_shape':list(v.shape),'original_dtype':str(v.dtype),
                'original_source_CF_attrs':_attributes(v)}
            if name.lower() in SOURCE_FROZEN_COORDINATE_VARIABLES:
                variables[name]['native_source_coordinate_extent']=safe_array_extent(v)
        geodatum_text=json.dumps({'global':glob,'variables':variables}).lower()
        explicit_EPSG_RD=any(t in geodatum_text for t in (
                'epsg:28992','epsg 28992','epsg_code 28992',
                'amersfoort / rd new'))
        explicit_WGS84=any(t in geodatum_text for t in (
                'epsg:4326','epsg 4326',
                'geographic latitude longitude'))
        NAP_explicit='nap' in geodatum_text
        geo={
          'source_native_CRS_verified_EPSG28992':explicit_EPSG_RD,
          'source_native_CRS_verified_EPSG4326':explicit_WGS84,
          'source_vertical_NAP_string_present_in_native_metadata':NAP_explicit,
          'native_public_landmark_geographic_bbox_assessment':{},
          'original_native_coordinate_arrays_not_released':True}
        xname=next((n for n in ('x','easting') if n in ds.variables),None)
        yname=next((n for n in ('y','northing') if n in ds.variables),None)
        if not(xname and yname):
            xname=next((n for n in ('lon','longitude') if n in ds.variables),None)
            yname=next((n for n in ('lat','latitude') if n in ds.variables),None)
        if xname and yname:
            xv=ds.variables[xname];yv=ds.variables[yname]
            ex=safe_array_extent(xv);ey=safe_array_extent(yv)
            geo['original_xy_native_names']=[xname,yname]
            geo['source_x_and_y_extent']={'x':ex,'y':ey}
            if ex['status']=='SOURCE_ARRAY_FINITE' and ey['status']=='SOURCE_ARRAY_FINITE':
                if explicit_EPSG_RD and xname in ('x','easting'):
                    transformer=Transformer.from_crs('EPSG:4326','EPSG:28992',always_xy=True)
                    src='EPSG:28992_NATIVE_EXPLICIT'
                elif explicit_WGS84 and xname in ('lon','longitude'):
                    transformer=None
                    src='EPSG:4326_NATIVE_EXPLICIT'
                else:
                    transformer=None
                    src='NO_AUTHENTIC_MATCH_OF_CRS_TO_NATIVE_COORDINATE_PAIR'
                for place,(lat,lon) in FIXED_SITE_WGS84.items():
                    if src=='EPSG:28992_NATIVE_EXPLICIT':
                        XX,YY=transformer.transform(lon,lat)
                    elif src=='EPSG:4326_NATIVE_EXPLICIT':
                        XX,YY=lon,lat
                    else:
                        geo['native_public_landmark_geographic_bbox_assessment'][place]={
                            'source_status':'NO_CERTIFIED_NATIVE_GEOREFERENCE'}
                        continue
                    within=(ex['min_source_value']<=XX<=ex['max_source_value'] and
                            ey['min_source_value']<=YY<=ey['max_source_value'])
                    geo['native_public_landmark_geographic_bbox_assessment'][place]={
                        'source_native_CRS_used':src,
                        'source_fixed_locus_within_original_raw_NC_coordinate_BBOX_only':bool(within),
                        'BBOX_does_not_prove_native_valid_depth_or_soundings':True}
        possible=[]
        for name,v in ds.variables.items():
            title=(name+' '+str(getattr(v,'standard_name',''))+' '+str(getattr(v,'long_name',''))).lower()
            if (name.lower() in BATHY_ELEVATION_PRIORITY or
                ('bathymetr' in title or 'bed level' in title or 'seafloor' in title)) and v.ndim>=1:
                possible.append({'native_variable_name':name,
                    'original_var_CF':variables[name]['original_source_CF_attrs'],
                    'source_variable_dimensions':variables[name]['native_shape']})
        return {'analysis':'V119_ORIGINAL_'+original_year+'_RWS_VAKLO_NC_METADATA_ONLY',
          'original_source_year_from_fixed_filename':int(original_year),
          'original_global_attrs':glob,
          'native_variable_catalog':variables,
          'geographical_datum_source_QA':geo,
          'candidate_bed_elevation_or_depth_source_variables_PRIORITY_BEFORE_DATA_VALUES':possible,
          'source_data_quality_status':'TRUE_ORIGINAL_NETCDF_METADATA_ADMITTED',
          'NO_assumption_of_2020_ZEELAND_or_bird_foraging_or_real_habitat_access':True}

def run(output):
    results={'analysis':'V119_2019_2020_TRUE_ORIGINAL_RWS_VAKLO_BATHYMETRY_NETCDF_SOURCE_CENSUS',
      'source_locked_original_urls':[PREFIX+f for f,_ in NATIVE_ORIGINAL.values()],
      'source_only_NO_gull_movement_or_NAP_dryflat_Y_estimated':True,
      'original_year_source':{},'source_status':'SOURCE_PENDING'}
    with tempfile.TemporaryDirectory() as tmp:
        for year,(filename,expected_size) in NATIVE_ORIGINAL.items():
            try:
                local=Path(tmp)/filename
                receipt=download_original_snapshot(filename,expected_size,local)
                metadata=geo_source_first(local,year)
                results['original_year_source'][year]={
                     'source_status':'AUTHENTIC_HISTORICAL_ORIGINAL_NETCDF_METADATA_ADMITTED',
                     'original_source_file_SHA_and_bytes':receipt,
                     'original_source_geo_and_bathy_CRS_NAP_QA':metadata}
            except (SourceStop,ValueError,OSError,RuntimeError) as e:
                results['original_year_source'][year]={
                    'source_status':'SOURCE_STOP_HISTORICAL_BATHYMETRY_NOT_ADMITTED',
                    'source_failure':repr(e)[:260]}
            sample=results['original_year_source'][year]
            meta=sample.get('original_source_geo_and_bathy_CRS_NAP_QA') or {}
            geo=meta.get('geographical_datum_source_QA') or {}
            print('V119_TRUE_RWS_HISTORICAL_BATHY_YEAR_SOURCE '+json.dumps({
                'year':year,'status':sample['source_status'],
                'source_blocker':sample.get('source_failure'),
                'native_CRS':{'RD_28992':geo.get('source_native_CRS_verified_EPSG28992'),
                               'WGS84_4326':geo.get('source_native_CRS_verified_EPSG4326')},
                'source_vertical_NAP_metadata':geo.get('source_vertical_NAP_string_present_in_native_metadata'),
                'native_coordinate_2019_2020_Roompot_Roggenplaat_BBOX':geo.get('native_public_landmark_geographic_bbox_assessment'),
                'native_source_bathy_candidates':meta.get('candidate_bed_elevation_or_depth_source_variables_PRIORITY_BEFORE_DATA_VALUES'),
                'not_actual_local_raster_bathymetry_or_bird_time_niche':True},sort_keys=True),flush=True)
    results['source_status']='AUTHENTIC_SOURCE_METADATA_ADMITTED' if any(
        r['source_status']=='AUTHENTIC_HISTORICAL_ORIGINAL_NETCDF_METADATA_ADMITTED'
        for r in results['original_year_source'].values()) else 'SOURCE_UNAVAILABLE'
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(results,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('V119_TRUE_HISTORICAL_BATHYNETCDF_SOURCE_FINAL '+json.dumps({
        'source_status':results['source_status'],
        'actual_original_2019_2020_source_year_status':{
            k:v['source_status'] for k,v in results['original_year_source'].items()},
        'no_new_actual_bird_2020_tide_solar_or_foraging_effect':True},sort_keys=True),flush=True)
    return results
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
