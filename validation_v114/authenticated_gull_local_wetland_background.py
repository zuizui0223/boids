"""v114 genuine 2017–19 GIC tidal-WETLAND local map context at 2020 gull GPS.

For every genuine original USED 2020 gull GPS site, read 8 point observations
at 8 fixed geodesic compass bearings around that site (r=500/1000/2000m).
These 8 spatially correlated background *pixels* are not 8 independent birds,
not actual accessible alternative habitats, and not 2020 dry-flat access.
No original bird IDs/GPS positions/source pixel arrays are released.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from math import floor
import numpy as np
import rasterio
from rasterio.windows import Window
from pyproj import Geod
from gic2019_real_10km_gauge_buffer import (
    read_original_geotransform,native_expected_tile,metadata_for_native_tile,
    download_and_verify_original_gcs_tile,SourceUnavailable)
from real_2020_gull_GIC_native_pixels import (
    source_2020_original_gull_GIC_pixels)
AZIMUTHS=np.arange(0.,360.,45.,dtype=float)
RADII_M=(500,1000,2000)
PRIMARY_RADIUS_M=1000
EXPECTED_N_RAYS=8
MAX_REAL_TILES=4
MAX_SOURCE_CROP_PIXELS=8_000_000
GEOD=Geod(ellps='WGS84')

def fixed_geodesic_neighbors(latitude,longitude,radius_m):
    """Exact source WGS84 geodesic cardinal/diagonal points, no outcome selection."""
    if radius_m not in RADII_M:
        raise ValueError('STOP_V114_UNREGISTERED_LOCAL_CONTEXT_RADIUS')
    lat=np.asarray(latitude,dtype=float).reshape(-1)
    lon=np.asarray(longitude,dtype=float).reshape(-1)
    if len(lat)!=len(lon) or len(lat)==0 or not np.isfinite(lat).all() or not np.isfinite(lon).all():
        raise ValueError('STOP_V114_INVALID_ORIGINAL_GULL_GPS_WGS84')
    rays=np.tile(AZIMUTHS,len(lat))
    south=np.repeat(lat,EXPECTED_N_RAYS);east=np.repeat(lon,EXPECTED_N_RAYS)
    distance=np.full(len(rays),float(radius_m))
    x,y,_=GEOD.fwd(east,south,rays,distance)
    return np.asarray(y).reshape(len(lat),EXPECTED_N_RAYS),np.asarray(x).reshape(len(lon),EXPECTED_N_RAYS)

def native_pixel_values_vector(raster,latitude,longitude,original_validated_affine):
    """One raster source band, array input at source-native EPSG:4326 WGS84 positions.
    On native pixel mask/outside-tile => NaN, NEVER zero or wetland absence.
    """
    a=raster.transform
    expected=original_validated_affine
    if raster.crs is None or raster.crs.to_string()!='EPSG:4326' or raster.count!=1 or (
        a.b!=0 or a.d!=0 or a.a<=0 or a.e>=0 or
        abs(a.a-expected.a)>1e-10 or abs(a.e-expected.e)>1e-10):
        raise ValueError('STOP_V114_ORIGINAL_GIC_NATIVE_TILE_SOURCE_CRS_AFFINE')
    lat=np.asarray(latitude,dtype=float).reshape(-1)
    lon=np.asarray(longitude,dtype=float).reshape(-1)
    if len(lat)!=len(lon):raise ValueError('STOP_V114_COORDINATE_SHAPES')
    col=np.floor((lon-a.c)/a.a).astype(np.int64)
    row=np.floor((lat-a.f)/a.e).astype(np.int64)
    inside=(row>=0)&(col>=0)&(row<raster.height)&(col<raster.width)
    result=np.full(len(lat),np.nan)
    if not inside.any():return result,{'source_points_inside_selected_original_tile':0,'source_points_native_valid_pixels':0}
    col0=int(col[inside].min());col1=int(col[inside].max())+1
    row0=int(row[inside].min());row1=int(row[inside].max())+1
    if (col1-col0)*(row1-row0)>MAX_SOURCE_CROP_PIXELS:
        raise ValueError('SOURCE_STOP_V114_ORIGINAL_NATIVE_GIC_TIFF_WINDOW_TOO_LARGE')
    img=raster.read(1,window=Window(col0,row0,col1-col0,row1-row0),masked=True)
    rr=row[inside]-row0;cc=col[inside]-col0
    vals=np.asarray(img.data)[rr,cc].astype(float)
    mask=np.ma.getmaskarray(img)[rr,cc]
    valid=(~mask)&np.isfinite(vals)&(vals>=0)&(vals<=100)
    if ((~mask)&(~np.isfinite(vals)|(vals<0)|(vals>100))).any():
        raise ValueError('STOP_V114_ORIGINAL_GIC_RF_SCORE_OUTSIDE_VALID_0_100')
    dest=np.where(inside)[0]
    result[dest[valid]]=vals[valid]
    return result,{'source_points_inside_selected_original_tile':int(inside.sum()),
       'source_points_native_valid_pixels':int(valid.sum()),
       'source_points_native_masked_or_outside':int(len(lat)-valid.sum())}

def attach_true_GIC_local_neighbors(bird_hour,source_v105_audit,
                                      previously_admitted_v112_events=None,
                                      previously_admitted_v112_source_proof=None):
    """Source verify original used raster first with UNCHANGED v112 helper;
    append raw 8-ray source coordinates' RF scores without calculating new Z.

    Optional previously admitted events may ONLY be reused after frozen v112
    and v113 exact source/old-effect replay. Per-pixel original true GIC TIFF
    MD5 and exact 2020 used RF value are verified AGAIN in this function.
    """
    if previously_admitted_v112_events is None:
        events,v112_source_proof=source_2020_original_gull_GIC_pixels(bird_hour,source_v105_audit)
    else:
        events=previously_admitted_v112_events
        v112_source_proof=previously_admitted_v112_source_proof
        if not isinstance(v112_source_proof,dict) or (
              v112_source_proof.get('source_original_GIC_2017_2019_layer')!='twprobabilityEnd'
        ) or len(events)!=sum(
             x.get('original_2020_GPS_fix_source_at_most30km',0) for x in
             v112_source_proof.get('source_GIC_pixel_gull_species_QA',{}).values()):
            raise ValueError('STOP_V114_PREVIOUS_V112_SOURCE_AUTHENTICATION_NOT_REPLAYED')
    source_aff=read_original_geotransform(source_v105_audit)
    grouped=defaultdict(list)
    for i,e in enumerate(events):
        for r in RADII_M:
            e[f'v114_r{r}_original_GIC_8ray_native_RF']=None
        if e.get('source_original_GIC_valid_RF') is None:
            continue
        native=native_expected_tile(e['latitude'],e['longitude'],source_aff)
        grouped[native['native_GCS_tile_name']].append(i)
    if len(grouped)>MAX_REAL_TILES:
        raise ValueError('STOP_V114_ORIGINAL_GIC_GULL_LOCATION_NATIVE_TILES_OVER_FROZEN4')
    source_tally=Counter()
    original_proofs=[]
    with TemporaryDirectory(prefix='boids-v114-authenticated-local-GIC_') as tmp:
        for k,(filename,ind) in enumerate(sorted(grouped.items())):
            tile=native_expected_tile(events[ind[0]]['latitude'],events[ind[0]]['longitude'],source_aff)
            meta=metadata_for_native_tile(tile)
            dest=Path(tmp)/f'original_native_GIC_{k}.tif'
            receipt=download_and_verify_original_gcs_tile(meta,dest)
            with rasterio.open(dest) as ds:
                expected_c=source_aff.c+tile['expected_colstart_original_pixels']*source_aff.a
                expected_f=source_aff.f+tile['expected_rowstart_original_pixels']*source_aff.e
                if (abs(ds.transform.c-expected_c)>1.1*abs(source_aff.a) or
                    abs(ds.transform.f-expected_f)>1.1*abs(source_aff.e)):
                    raise ValueError('STOP_V114_GIC_ORIGINAL_TILE_GRID_NOT_IDENTICAL_TO_V112')
                latitude=np.array([events[i]['latitude'] for i in ind],dtype=float)
                longitude=np.array([events[i]['longitude'] for i in ind],dtype=float)
                # For multi-source areas, a neighbor crossing the tile boundary is
                # treated as MISSING source; never zero. Source coverage gate
                # is computed on the actual ORIGINAL tide×solar eligible GPS fixes.
                # For the frozen Zeeland source all offsets remain inside one tile.
                used,pointqa=native_pixel_values_vector(ds,latitude,longitude,source_aff)
                for n,idx in enumerate(ind):
                    v=events[idx]['source_original_GIC_valid_RF']
                    if np.isfinite(used[n]) and abs(float(v)-used[n])>1e-10:
                        raise ValueError('STOP_V114_PREVIOUS_REAL_GIC_GPS_PIXEL_REPLAY_DIFFERENT')
                    if np.isfinite(used[n]) != (v is not None):
                        raise ValueError('STOP_V114_PREVIOUS_REAL_GIC_GPS_PIXEL_MASK_REPLAY_DRIFT')
                for radius in RADII_M:
                    lat8,lon8=fixed_geodesic_neighbors(latitude,longitude,radius)
                    values,qa=native_pixel_values_vector(ds,lat8.ravel(),lon8.ravel(),source_aff)
                    values=values.reshape(len(ind),EXPECTED_N_RAYS)
                    full=np.isfinite(values).all(axis=1)
                    for n,idx in enumerate(ind):
                        if full[n]: events[idx][f'v114_r{radius}_original_GIC_8ray_native_RF']=tuple(float(q) for q in values[n])
                    source_tally[f'r{radius}_original_GPS_fix_all8_neighborhood_pixels_valid']+=int(full.sum())
                    source_tally[f'r{radius}_native_8ray_map_source_points_outside_or_masked']+=int(np.sum(~np.isfinite(values)))
                source_tally['genuine_used_GPS_points_revalidated_against_original_GIC_provider_TIFF']+=len(ind)
            original_proofs.append({'original_native_GIC_filename':filename,
                'source_publisher_MD5_verified':receipt['source_original_GCS_provider_MD5_verified'],
                'original_tile_bytes':meta['size'],
                'source_original_GCS_generation':meta['generation'],
                'original_gull_GPS_used_sites_in_tile':len(ind)})
            dest.unlink(missing_ok=True)
    return events,{
        'source_2020_original_gull_native_used_GIC_replay_QA':v112_source_proof,
        'source_all_radii_fixed_compass_bearings':AZIMUTHS.tolist(),
        'source_radii_predeclared_m':list(RADII_M),
        'source_real_GIC_authenticated_tile_count':len(grouped),
        'source_original_GIC_tile_provenance':original_proofs,
        'source_authenticated_raw_neighbor_pixel_counts':dict(source_tally),
        'source_original_gull_GPS_hour_rows_total':len(events),
        'source_original_true_bird_ID_exact_site_and_time_not_exported':True,
        'no_local_time_varying_available_tidalflat_or_prey':True}
