#!/usr/bin/env python3
"""v11b strict source-only independent GPS x raster QC (NO animal-choice effects).

Source Forrest et al. 2025 Ecography, Zenodo 13749246. All raw GPS
coordinates remain ephemeral on the runner; report only counts, dates, CRS,
raster coverage and checksum. Only prospective bio model if quality admitted.
"""
from __future__ import annotations
import collections, csv, hashlib, json, math, os, sys, tempfile, urllib.request
from pathlib import Path
from urllib.parse import urlsplit
import numpy as np

RECORD=13749246
API=f'https://zenodo.org/api/records/{RECORD}'
FILES=['buffalo.csv','canopy_cover.tif','veg_herby.tif','slope_raster.tif']
BOUNDS={'buffalo.csv':30_000_000,'canopy_cover.tif':5_000_000,
        'veg_herby.tif':5_000_000,'slope_raster.tif':40_000_000}

def get_json(url):
    request=urllib.request.Request(url,headers={'User-Agent':'ecostate-v11b/1.0','Accept':'application/json'})
    with urllib.request.urlopen(request,timeout=45) as r:return json.loads(r.read())

def original_file(meta,key,out):
    m=[x for x in meta.get('files',[]) if x.get('key')==key]
    if len(m)!=1:raise ValueError('SOURCE_STOP_WRONG_FILE_COUNT_'+key)
    f=m[0]
    if not str(f.get('checksum','')).startswith('md5:'):raise ValueError('SOURCE_STOP_NO_PROVIDER_MD5_'+key)
    url=f.get('links',{}).get('content') or f.get('links',{}).get('self')
    u=urlsplit(url or '')
    if u.scheme!='https' or u.netloc not in ('zenodo.org','www.zenodo.org'):raise ValueError('SOURCE_STOP_UNTRUSTED_URL')
    if int(f.get('size',0))>BOUNDS[key]:raise ValueError('SOURCE_STOP_SOURCE_TOO_LARGE')
    req=urllib.request.Request(url,headers={'User-Agent':'ecostate-v11b/1.0'})
    h=hashlib.md5();s=hashlib.sha256();n=0
    with urllib.request.urlopen(req,timeout=120) as r,out.open('wb') as w:
        while True:
            b=r.read(1<<20)
            if not b:break
            n+=len(b)
            if n>BOUNDS[key]:raise ValueError('SOURCE_STOP_STREAM_TOO_LARGE')
            h.update(b);s.update(b);w.write(b)
    if n!=int(f['size']) or 'md5:'+h.hexdigest()!=f['checksum']:raise ValueError('SOURCE_STOP_PROVIDER_DIGEST_'+key)
    return {'name':key,'bytes':n,'provider_md5':h.hexdigest(),'actual_sha256':s.hexdigest()}

def source_qc(paths):
    import pandas as pd
    import rasterio
    from rasterio.warp import transform
    p=pd.read_csv(paths['buffalo.csv'],low_memory=False)
    cols=list(p.columns)
    required=['timestamp','lat','lon','node']
    if any(x not in cols for x in required):raise ValueError('SOURCE_SCHEMA_STOP_REQUIRED_GPS_COLS')
    lat=pd.to_numeric(p['lat'],errors='coerce').to_numpy(float)
    lon=pd.to_numeric(p['lon'],errors='coerce').to_numpy(float)
    good=np.isfinite(lat)&np.isfinite(lon)&(np.abs(lat)<=90)&(np.abs(lon)<=180)
    if good.sum()<5000:raise ValueError('SOURCE_SCHEMA_STOP_TOO_FEW_GPS_COORDS')
    nodes=p['node'].astype(str).str.strip()
    ntok=[x for x in nodes[good].unique().tolist() if x and x!='nan']
    # Only count non-identifying timestamp grammar and location success, no animal behavior.
    t1=pd.to_datetime(p['timestamp'],errors='coerce',utc=True)
    t2=pd.to_datetime(p['DateTime'],errors='coerce',utc=True) if 'DateTime' in cols else pd.Series([pd.NaT]*len(p))
    base={'source_rows':len(p),'source_columns':cols,'valid_gps_coordinates':int(good.sum()),
          'unique_node_tokens':len(ntok),'timestamp_parse_success':int(t1.notna().sum()),
          'datetime_parse_success':int(t2.notna().sum())}
    rasters={}
    for key in ('canopy_cover.tif','veg_herby.tif','slope_raster.tif'):
        with rasterio.open(paths[key]) as ds:
            if ds.crs is None:raise ValueError('SOURCE_SCHEMA_STOP_RASTER_MISSING_CRS_'+key)
            # Subsample first 50k valid original GPS fixes for source coverage and NoData QC.
            idx=np.flatnonzero(good)[::max(1,int(good.sum()/25000))][:25000]
            xs,ys=transform('EPSG:4326',ds.crs.to_string(),lon[idx].tolist(),lat[idx].tolist())
            samples=np.array([float(v[0]) for v in ds.sample(zip(xs,ys),masked=False)],dtype=float)
            bbox=(np.array(xs)>=ds.bounds.left)&(np.array(xs)<=ds.bounds.right)&(np.array(ys)>=ds.bounds.bottom)&(np.array(ys)<=ds.bounds.top)
            finite=np.isfinite(samples)
            notnodata=(samples!=ds.nodata) if ds.nodata is not None else np.ones(len(samples),bool)
            valid=finite&notnodata&bbox
            rasters[key]={'crs':ds.crs.to_string(),'shape':[ds.height,ds.width],
               'bands':ds.count,'nodata_declared':ds.nodata is not None,
               'geography_sampled':len(idx),'within_original_raster_extent':int(bbox.sum()),
               'valid_raster_value_samples':int(valid.sum()),
               'value_valid_fraction':float(valid.mean())}
    base['rasters']=rasters
    base['minimum_gate']={'counted_valid_coordinates':int(good.sum())>15000,
       'at_least_10_node_tokens':len(ntok)>=10,
       'timestamp_parseable':int(t1.notna().sum())>10000,
       'canopy_valid_samples':rasters['canopy_cover.tif']['value_valid_fraction']>.6,
       'vegetation_valid_samples':rasters['veg_herby.tif']['value_valid_fraction']>.6}
    base['status']='SOURCE_GEO_SCHEMA_ADMITTED' if all(base['minimum_gate'].values()) else 'SOURCE_SCHEMA_STOP_GEO_COVERAGE'
    return base

def run(out):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    result={'schema':'ecostate.v11b.independent_buffalo_same_method_GPS_raster_QC',
       'status':'SOURCE_OR_SCHEMA_STOP','publication_doi':'10.1111/ecog.07421',
       'source_record_id':RECORD,'original_gps_coordinates_exported':False,
       'biological_choice_effect_computed':False,'data_exports_only':'aggregate source QC / provider checksums'}
    try:
        m=get_json(API)
        with tempfile.TemporaryDirectory() as t:
            paths={key:Path(t)/key for key in FILES}
            rec=[]
            for key in FILES:rec.append(original_file(m,key,paths[key]))
            result['original_checksum_receipts']=rec
            result.update(source_qc(paths))
    except Exception as e:result.update({'status':'SOURCE_OR_SCHEMA_STOP','reason':str(e)[:1200]})
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('V11B_ORIGINAL_GEO_QC',result['status'],json.dumps({
       'source_rows':result.get('source_rows'), 'unique_nodes':result.get('unique_node_tokens'),
       'valid_coordinates':result.get('valid_gps_coordinates'),
       'time_parse':result.get('timestamp_parse_success'),'rasters':result.get('rasters'),
       'reason':result.get('reason')},separators=(',',':')))
    assert result['original_gps_coordinates_exported'] is False
    assert result['biological_choice_effect_computed'] is False
    return result
if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v11/results/buffalo_geo_qc_v11b.json')
