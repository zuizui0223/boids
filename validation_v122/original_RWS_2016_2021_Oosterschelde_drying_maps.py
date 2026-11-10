"""v122 original first-party Rijkswaterstaat 2016/2021 Oosterschelde
ecotope modelled tidal-flat DRYING-DURATION rasters native source-only.
NOT the actual May–July 2020 tidal water above actual ground at 2020
gull GPS, and native numeric codes are NOT certified percent or hours.
"""
from __future__ import annotations
import argparse,hashlib,io,json,xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from collections import Counter
import numpy as np
import rasterio
from rasterio.windows import Window
from pyproj import Transformer
from real_2019_2020_Roggenplaat_paired_ground_source import (
    exact_original_2019_raster_centers,SHA_2019,EXPECTED_SOURCE_BYTES,FIXED_NATIVE_5M_CENTERS,
    ROOT,LAYER,_download_original_raster,
    _read_original_5m_ground_v116_replay)

SOURCE_BASE="https://downloads.rijkswaterstaatdata.nl/ecotopen_zout_raster/"
SOURCE_FILES={'2016':'edvd_os_2016.tif','2021':'edvd_os_2021.tif'}
EXPECTED_SOURCE_CONCEPT="official Oosterschelde ecological model DRYING DURATION maps"
MAX_TIF_BYTES=12_000_000
MAX_META_BYTES=150_000
MIN_YEAR_PAIRED_FRACTION=.9
SIGNATURES=(bytes([73,73,42,0]),bytes([77,77,0,42]),bytes([73,73,43,0]),bytes([77,77,0,43]))
SOURCE_YEAR_TEMPORAL_CAVEAT="2016 and 2021 ecotope models, not 2020 bird observation"
APPROVED_OFFICIAL_CATALOGUE="https://data.overheid.nl/dataset/46902-droogvalduurkaart--basiskaart-voor-de-zoute-ecotopen-oosterschelde-2021"

class SourceStop(Exception): pass

def authentic_source_file(name,output,limit):
    if name not in [*SOURCE_FILES.values(),*(f+'.xml' for f in SOURCE_FILES.values())]:
        raise ValueError("STOP_NOT_FROZEN_ORIGINAL_RWS_DRYING_DURATION_FILE")
    request=Request(SOURCE_BASE+name,headers={
       'User-Agent':'boids-v122-original-RWS-Oosterschelde-2016-2021-drying-duration-source/1.0',
       'Accept':'image/tiff,application/octet-stream,application/xml,*/*'})
    h=hashlib.sha256();n=0
    try:
        with urlopen(request,timeout=65) as src,open(output,'wb') as dst:
            if src.status!=200:raise SourceStop('SOURCE_RWS_UNEXPECTED_HTTP_STATUS')
            for block in iter(lambda:src.read(524288),b''):
                n+=len(block)
                if n>limit:raise SourceStop('SOURCE_NATIVE_RWS_FILE_ABOVE_FROZEN_LIMIT')
                h.update(block);dst.write(block)
    except (HTTPError,URLError,TimeoutError,OSError) as e:
        raise SourceStop('SOURCE_ORIGINAL_RWS_DRYING_MAP_UNAVAILABLE_'+str(e)[:160]) from e
    if name.endswith('.tif') and Path(output).read_bytes()[:4] not in SIGNATURES:
        raise SourceStop('SOURCE_NATIVE_2016_2021_DRYING_MAP_NOT_TIFF')
    return {'provider_original_name':name,'official_native_url':SOURCE_BASE+name,
        'original_source_bytes':n,'original_source_SHA256':h.hexdigest()}

def source_metadata_XML(path):
    raw=Path(path).read_bytes()
    try:root=ET.fromstring(raw)
    except ET.ParseError:
        return {'source_original_XML_valid':False,'source_unit_legend_unverified':True}
    snippets=[]
    for node in root.iter():
        if node.text and any(k in node.text.lower() for k in (
            'droogvalduur','percentage','percent','procent','uur','hour','tijdsduur','fractie','klasse','eenheid')):
            val=' '.join(node.text.split())
            if len(val)>7 and val not in snippets:snippets.append(val[:250])
    return {'source_original_XML_valid':True,
       'source_element_root':root.tag,'original_RWS_drying_duration_unit_metadata_snippets':snippets[:25],
       'unit_percent_hours_or_class_not_automatically_certified':True}

def original_native_raster_at_2019_fixed_centers(ds,x,y):
    """Nearest exact native RWS grid cell at each *original* fixed 2019 source
    cell center; no interpolation, zero is valid unless native nodata mask.
    """
    if ds.crs is None or ds.transform.is_degenerate or ds.count!=1:
        raise SourceStop('SOURCE_NATIVE_RWS_DRYING_MAP_HAS_NO_REAL_GEOREFERENCING')
    x=np.asarray(x,dtype=float).reshape(-1);y=np.asarray(y,dtype=float).reshape(-1)
    if len(x)!=FIXED_NATIVE_5M_CENTERS or len(y)!=len(x):
        raise ValueError('SOURCE_STOP_RWS_2019_ORIGINAL_FIXED441_GEO_FRAME_MISMATCH')
    if ds.crs.to_string()!='EPSG:28992':
        transform=Transformer.from_crs('EPSG:28992',ds.crs,always_xy=True)
        x,y=transform.transform(x,y)
    a=ds.transform
    c=np.floor((x-a.c)/a.a).astype(int)
    r=np.floor((y-a.f)/a.e).astype(int)
    inside=(r>=0)&(c>=0)&(r<ds.height)&(c<ds.width)
    values=np.full(len(x),np.nan,dtype=float)
    if inside.any():
        r0=int(r[inside].min());r1=int(r[inside].max())+1
        c0=int(c[inside].min());c1=int(c[inside].max())+1
        if (r1-r0)*(c1-c0)>50_000:
            raise SourceStop('SOURCE_NATIVE_DRYING_MAP_FIXED_PLOT_EXCESSIVE_NATIVE_PIXELS')
        z=ds.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
        vv=z.data[r[inside]-r0,c[inside]-c0]
        mask=np.ma.getmaskarray(z)[r[inside]-r0,c[inside]-c0]
        p=np.where(inside)[0][~mask & np.isfinite(vv)]
        values[p]=vv[~mask & np.isfinite(vv)]
    good=np.isfinite(values)
    return values,{'source_fixed_Roggenplaat_2019_gridcentres_n':len(values),
       'source_valid_native_drying_map_pixels':int(good.sum()),
       'source_outside_native_footprint_n':int((~inside).sum()),
       'source_masked_or_nan_inside_n':int((inside & ~good).sum()),
       'source_original_valid_numeric_values_including_0':True}

def public_source_native_value_profile(values):
    arr=np.asarray(values,dtype=float)
    v=arr[np.isfinite(arr)]
    if len(v)==0:return {'source_numeric_unit':'UNKNOWN','n_original_valid_source_pixels':0}
    count=Counter(str(int(q)) if float(q).is_integer() else str(round(float(q),6)) for q in v)
    return {'source_numeric_unit':'UNVERIFIED_NOT_A_CALIBRATED_PERCENT_OR_HOURS',
        'n_original_valid_source_pixels':len(v),
        'original_raw_source_numeric_minmax':[float(v.min()),float(v.max())],
        'original_raw_source_numeric_mean':float(np.mean(v)),
        'original_raw_source_numeric_q05_q25_med_q75_q95':
          np.quantile(v,[.05,.25,.5,.75,.95]).tolist(),
        'native_source_unique_numeric_codes':len(count),
        'original_raw_native_first_25_numeric_code_counts':dict(sorted(count.items())[:25])}

def run(v116meta,outpath):
    report={'analysis':'V122_ORIGINAL_RWS_2016_VS_2021_OOSTERSCHELDE_DRYING_DURATION_ECOTOPE_RASTER_SOURCE_QA',
      'original_RWS_2021_dataset':APPROVED_OFFICIAL_CATALOGUE,
      'fixed_publisher_native_drying_duration_geotiffs':SOURCE_FILES,
      'source_raster_semantics':'modelled 2016/2021 RWS East Scheldt dry duration, not measured 2020 animals or time-level stage',
      'source_2021_occurs_AFTER_original_2020_gull_spring_summer':True,
      'source_status':'SOURCE_PENDING','no_bird_temporal_niche_or_actual_2020_dryflat_h':True}
    with TemporaryDirectory() as temp:
        old=Path(temp)/'original2019DTM5.tif'
        try:
            p=_download_original_raster(old,ROOT+LAYER['dtm_5']['filename'],LAYER['dtm_5']['id'])
            check=_read_original_5m_ground_v116_replay(old,v116meta)
            with rasterio.open(old) as ds:
                x,y,z19,frame=exact_original_2019_raster_centers(ds)
            if frame['native_2019_valid_z_count']!=441 or abs(
                frame['source_original_2019_native_ground_median_if_valid']+.1078)>1e-4:
                raise SourceStop('SOURCE_STOP_ORIGINAL_FIXED_2019_ROGGENPLAAT_441_REPLAY_CHANGED')
            report['original_2019_DTM5_geographic_replay']={
                '2019_source_SHA256':p['original_locally_downloaded_SHA256'],**frame}
        except (SourceStop,ValueError,rasterio.errors.RasterioError,OSError) as e:
            report['source_status']='SOURCE_STOP_OLD_2019_ROGGENPLAAT_GEOMETRY'
            report['source_error']=str(e)[:240]
            return emit(report,outpath)
        values={}
        report['original_publisher_native_drying_raster_years']={}
        for year,filename in SOURCE_FILES.items():
            item={'year':year,'official_filename':filename,'status':'SOURCE_PENDING'}
            raw=Path(temp)/filename
            try:
                receipt=authentic_source_file(filename,raw,MAX_TIF_BYTES)
                item['original_public_RWS_TIFF_source']=receipt
                with rasterio.open(raw) as ds:
                    item['native_RWS_drying_raster_GeoTIFF_properties']={
                       'native_CRS':ds.crs.to_string() if ds.crs else None,
                       'native_dims':[ds.width,ds.height],'source_native_res_m_or_CRS_units':list(ds.res),
                       'native_nodata':ds.nodata,'native_band_units':ds.units[0] if ds.units else None,
                       'native_band_dtype':ds.dtypes[0],
                       'native_source_affine':list(ds.transform)[:6],
                       'native_source_band_description':ds.descriptions[0],
                       'native_tags_subset':{k:str(v)[:160] for k,v in ds.tags().items() if k.lower() in (
                           'description','units','scale','offset','category_names','legend','source','statistic')},
                       'native_source_WGS84_bbox_not_inferred':True}
                    data,source=original_native_raster_at_2019_fixed_centers(ds,x,y)
                values[year]=data
                item['original_fixed_441_location_source_coverage']=source
                item['original_native_RWS_drying_map_numeric_profile']=public_source_native_value_profile(data)
                item['status']='NATIVE_ORIGINAL_RWS_DRYING_MAP_TRUE_GEOTIFF_SOURCE_ADMITTED'
            except (SourceStop,ValueError,RuntimeError,rasterio.errors.RasterioError,OSError) as e:
                item['status']='SOURCE_RWS_ORIGINAL_DRYING_MAP_GEOTIFF_NOT_ADMITTED'
                item['native_source_error']=str(e)[:180]
            for xmlname in (filename+'.xml',):
                try:
                    xmlpath=Path(temp)/xmlname
                    metadata_receipt=authentic_source_file(xmlname,xmlpath,MAX_META_BYTES)
                    item['official_original_publisher_sidecar_xml']={
                       **metadata_receipt,**source_metadata_XML(xmlpath)}
                except (SourceStop,ValueError,OSError) as e:
                    item['official_original_sidecar_xml_not_admitted']={
                        'reason':str(e)[:180],'native_unit_not_established':True}
            report['original_publisher_native_drying_raster_years'][year]=item
            print('V122_TRUE_RWS_ECOTOPE_DRY_DURATION_SOURCE_YEAR '+json.dumps({
                'year':year,'source_status':item['status'],
                'raw_native_raster_profile':item.get('original_native_RWS_drying_map_numeric_profile'),
                'fixed_Roggenplaat_source_coverage':item.get('original_fixed_441_location_source_coverage'),
                'native_units':(item.get('native_RWS_drying_raster_GeoTIFF_properties') or {}).get('native_band_units'),
                'original_metadata_XML_snippets':(item.get('official_original_publisher_sidecar_xml') or {}).get(
                    'original_RWS_drying_duration_unit_metadata_snippets')},
                sort_keys=True),flush=True)
        if len(values)==2:
            supported=np.isfinite(values['2016'])&np.isfinite(values['2021'])
            out={'native_paired_same_fixed_2019_Roggenplaat_DTM_centres':int(supported.sum()),
                 'original_2016_2021_RWS_drying_raster_shared_valid_fraction':float(supported.mean()),
                 'site_source_units_PHYSICAL_INTERVAL_NOT_CERTIFIED':True}
            if supported.mean()>=.9:
                a=values['2016'][supported];b=values['2021'][supported]
                out.update({'source_status':'PAIRED_NATIVE_NUMERIC_DRY_DURATION_CODES_AVAILABLE_UNITS_UNVERIFIED',
                    'RWS_native_source_year_2021_minus_2016_numeric_diff_median_UNITS_UNVERIFIED':
                         float(np.median(b-a)),
                    'RWS_native_source_year_2021_minus_2016_numeric_diff_q05_q95_UNITS_UNVERIFIED':
                         np.quantile(b-a,[.05,.95]).tolist(),
                    'NO_2020_2021_REAL_DRY_HOURS_COMPARISON':True})
            else:out['source_status']='NOT_ESTIMATED_NATIVE_2016_2021_SOURCE_BOTH_COVER_LT90PCT'
            report['source_year_paired_original_native_RWS_model_semantic_guard']=out
        if len(values)==2 and all(v['status']=='NATIVE_ORIGINAL_RWS_DRYING_MAP_TRUE_GEOTIFF_SOURCE_ADMITTED'
                for v in report['original_publisher_native_drying_raster_years'].values()):
            report['source_status']='RWS_ORIGINAL_2016_2021_MODELLED_DRY_DURATION_TIFF_SOURCE_ADMITTED'
        else:
            report['source_status']='SOURCE_ONLY_PARTIAL_RWS_MODELLED_DRY_DURATION'
    return emit(report,outpath)

def emit(report,outpath):
    Path(outpath).parent.mkdir(parents=True,exist_ok=True)
    Path(outpath).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V122_ORIGINAL_2016_2021_ECOTOPE_DRYING_MAP_FINAL '+json.dumps({
      'status':report['source_status'],
      'native_source_years':{k:{'status':v['status'],
             'source_441_valid':(v.get('original_fixed_441_location_source_coverage') or {}).get(
               'source_valid_native_drying_map_pixels'),
             'numeric_source_profile':v.get('original_native_RWS_drying_map_numeric_profile'),
             'XML_snippets':(v.get('official_original_publisher_sidecar_xml') or {}).get(
               'original_RWS_drying_duration_unit_metadata_snippets')}
             for k,v in report.get('original_publisher_native_drying_raster_years',{}).items()},
      'paired_native_source':report.get('source_year_paired_original_native_RWS_model_semantic_guard'),
      'no_2020_gull_Y_or_2020_actual_stage_drying_inferred':True},sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    args=argparse.ArgumentParser()
    args.add_argument('--v116-real-2019-source-artifact',required=True)
    args.add_argument('--output',required=True)
    x=args.parse_args();run(x.v116_real_2019_source_artifact,x.output)
