"""v115 source-original 2020 movement-step candidates and authenticated GIC RF pixels.

For every original movement start, rotate the REAL observed geodesic step
bearing by +45,...,+315 degrees at the SAME REAL observed step length, and
sample exact published 2017–2019 native GIC TIDAL WETLAND RF TIFF pixels.
These seven points are kinematically matched STATIC MAP controls, NOT
seven independent animals, true accessible feeding patches or dry sediment.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import rasterio
from pyproj import Geod
from gic2019_real_10km_gauge_buffer import (
    read_original_geotransform,native_expected_tile,metadata_for_native_tile,
    download_and_verify_original_gcs_tile,SourceUnavailable)
from authenticated_gull_local_wetland_background import native_pixel_values_vector

GEOD=Geod(ellps='WGS84')
ROTATIONS_DEGREES=np.arange(45.,360.,45.,dtype=float)
N_ALTERNATIVE_ENDPOINTS=7
MAX_NATIVE_TILES=4
# Geometry-only engineering: split source coordinates into native 512-pixel
# grid windows rather than reading one bounding box >8m source pixels.
# No source GPS or GIC RF score is filtered, interpolated or resampled.
ORIGINAL_NATIVE_WINDOW_CHUNK_PIXELS=512
MIN_TOTAL_GPS_SOURCE_STEPS=2000
PUBLIC_GIC_IS_TIDAL_WETLAND_NOT_TRUE_DRY_TIDAL_FLAT=True

def original_geodesic_same_step_length_alternatives(departure_lat,departure_lon,
                                                     arrival_lat,arrival_lon):
    """Return (7, lat)/(7, lon) for each real original bird GPS step.
    No random site choice or outgoing numeric habitat score inspection.
    """
    la0=np.atleast_1d(np.array(departure_lat,dtype=float))
    lo0=np.atleast_1d(np.array(departure_lon,dtype=float))
    la1=np.atleast_1d(np.array(arrival_lat,dtype=float))
    lo1=np.atleast_1d(np.array(arrival_lon,dtype=float))
    if not(len(la0)==len(lo0)==len(la1)==len(lo1)) or not len(la0):
        raise ValueError('STOP_V115_ORIGINAL_MOVE_SOURCE_COORDINATES_INVALID')
    bearing,back,distance=GEOD.inv(lo0,la0,lo1,la1)
    if not np.isfinite(distance).all() or (distance<0).any():
        raise ValueError('STOP_V115_NATIVE_MOVE_DISTANCES_INVALID')
    n=len(la0)
    headings=(np.repeat(bearing,N_ALTERNATIVE_ENDPOINTS)+
              np.tile(ROTATIONS_DEGREES,n))%360.
    lengths=np.repeat(distance,N_ALTERNATIVE_ENDPOINTS)
    x,y,_=GEOD.fwd(np.repeat(lo0,N_ALTERNATIVE_ENDPOINTS),
                   np.repeat(la0,N_ALTERNATIVE_ENDPOINTS),headings,lengths)
    return np.asarray(y).reshape(n,N_ALTERNATIVE_ENDPOINTS),(
        np.asarray(x).reshape(n,N_ALTERNATIVE_ENDPOINTS)),(
        np.asarray(distance)),np.asarray(bearing)

def native_source_pixels_geometry_chunked(raster,latitude,longitude,aff):
    """Exact native source cell values for ALL provided points; deterministic 512
    source-pixel chunk grouping prevents giant bounding box, with identical
    native pixel masks to direct original single-window extraction.
    """
    la=np.asarray(latitude,dtype=float).ravel()
    lo=np.asarray(longitude,dtype=float).ravel()
    if la.size!=lo.size:raise ValueError('STOP_V115_GEO_CHUNK_COORDINATE_SHAPE')
    if not la.size:return np.array([],dtype=float),{'n_geometric_windows':0}
    t=raster.transform
    if not np.isfinite(la).all() or not np.isfinite(lo).all():
        raise ValueError('STOP_V115_NATIVE_GPS_OR_7ROTATED_COORDINATES_NOT_FINITE')
    rr=np.floor((la-t.f)/t.e).astype(np.int64)
    cc=np.floor((lo-t.c)/t.a).astype(np.int64)
    geo=defaultdict(list)
    for i,(r,c) in enumerate(zip(rr,cc)):
        geo[(int(r//ORIGINAL_NATIVE_WINDOW_CHUNK_PIXELS),
             int(c//ORIGINAL_NATIVE_WINDOW_CHUNK_PIXELS))].append(i)
    native=np.full(len(la),np.nan,dtype=float)
    n_sample=0
    for _,indices in sorted(geo.items()):
        result,proof=native_pixel_values_vector(
            raster,la[indices],lo[indices],aff)
        native[indices]=result
        n_sample+=len(indices)
    if n_sample!=len(native):
        raise ValueError('STOP_V115_GEO_CHUNK_HAS_DROPPED_ORIGINAL_SOURCE_GPS_PIXELS')
    return native,{'n_geometric_windows':len(geo),
      'n_original_native_coordinates_processed':n_sample,
      'source_one_original_GIC_pixel_per_exact_WGS84_coordinate':True}


def native_GIC_same_step_endpoint_pixels(original_GPS_step_events,original_GIC_v105_source):
    """Auth original GIC tile by source MD5 and original WGS84 native affine.
    Never export actual GPS origin/destination/alternative points or tags.
    """
    events=original_GPS_step_events
    if len(events)<MIN_TOTAL_GPS_SOURCE_STEPS:
        raise ValueError('STOP_V115_NO_SUFFICIENT_2020_ORIGINAL_GPS_MOVE_SOURCE')
    aff=read_original_geotransform(original_GIC_v105_source)
    grouped=defaultdict(list)
    stopped=Counter()
    for i,e in enumerate(events):
        e['v115_real_2020_GPS_destination_native_GIC_RF']=None
        e['v115_7_original_same_step_rotated_GIC_RF']=None
        try:
            t=native_expected_tile(e['GPS_arrival_lat'],e['GPS_arrival_lon'],aff)
            grouped[t['native_GCS_tile_name']].append(i)
        except SourceUnavailable:
            stopped['original_destination_outside_native_GIC_grid']+=1
    if len(grouped)>MAX_NATIVE_TILES:
        raise ValueError('STOP_V115_MORE_THAN4_NATIVE_GIC_SOURCE_TILES_FROZEN')
    receipts=[]
    with TemporaryDirectory(prefix='boids-original-v115-GIC-step-alternatives_') as tmp:
        for k,(name,ids) in enumerate(sorted(grouped.items())):
            tile=native_expected_tile(
                events[ids[0]]['GPS_arrival_lat'],
                events[ids[0]]['GPS_arrival_lon'],aff)
            meta=metadata_for_native_tile(tile)
            dest=Path(tmp)/f'actual_publisher_native_GIC_tile_{k}.tif'
            source=download_and_verify_original_gcs_tile(meta,dest)
            with rasterio.open(dest) as ds:
                expect_c=aff.c+tile['expected_colstart_original_pixels']*aff.a
                expect_f=aff.f+tile['expected_rowstart_original_pixels']*aff.e
                if ds.crs is None or ds.crs.to_string()!='EPSG:4326' or ds.count!=1 or (
                    abs(ds.transform.c-expect_c)>abs(aff.a)*1.1 or
                    abs(ds.transform.f-expect_f)>abs(aff.e)*1.1):
                    raise ValueError('STOP_V115_ORIGINAL_GIC_PROVIDER_WGS84_TILE_GEO_CHANGED')
                start_lat=np.array([events[i]['GPS_departure_lat'] for i in ids])
                start_lon=np.array([events[i]['GPS_departure_lon'] for i in ids])
                end_lat=np.array([events[i]['GPS_arrival_lat'] for i in ids])
                end_lon=np.array([events[i]['GPS_arrival_lon'] for i in ids])
                al_lat,al_lon,original_distance,original_bearing=(
                    original_geodesic_same_step_length_alternatives(start_lat,start_lon,end_lat,end_lon))
                used,qa=native_source_pixels_geometry_chunked(ds,end_lat,end_lon,aff)
                rotated,control_qa=native_source_pixels_geometry_chunked(ds,al_lat.ravel(),al_lon.ravel(),aff)
                rotated=rotated.reshape(len(ids),N_ALTERNATIVE_ENDPOINTS)
                valid=np.isfinite(used)&np.isfinite(rotated).all(axis=1)
                for i,idx in enumerate(ids):
                    if valid[i]:
                        events[idx]['v115_real_2020_GPS_destination_native_GIC_RF']=float(used[i])
                        events[idx]['v115_7_original_same_step_rotated_GIC_RF']=tuple(float(v) for v in rotated[i])
                stopped['original_native_GIC_source_geometry_windows_for_used_endpoints']+=qa['n_geometric_windows']
                stopped['original_native_GIC_source_geometry_windows_for_7rotated_alternatives']+=control_qa['n_geometric_windows']
                stopped['original_true_GPS_step_endpoints_with_valid_source_RF']+=int(np.isfinite(used).sum())
                stopped['original_true_GPS_steps_with_seven_same_length_GIC_RF']+=int(valid.sum())
                stopped['original_GIC_destination_or_seven_control_invalid_or_masked']+=int((~valid).sum())
                stopped['original_true_GPS_steps_shorter_than100m_ONLY_DESCRIPTIVE_QA']+=int((original_distance<100.).sum())
                stopped['original_true_GPS_steps_zero_length_NOT_DROPPED']+=int((original_distance==0).sum())
            receipts.append({'original_GCS_TIFF':name,
               'source_publisher_MD5_verified':source['source_original_GCS_provider_MD5_verified'],
               'native_original_GIC_tile_bytes':meta['size'],
               'original_source_generation':meta['generation'],
               'n_original_true_2020_movement_steps_in_native_tile':len(ids)})
            dest.unlink(missing_ok=True)
    return events,{'analysis':'v115_original_2020_two_species_GIC_seven_same_step_rotations_source_only',
       'genuine_original_2020_GPS_movement_source_n':len(events),
       'fixed_counterfactual_bearings_relative_to_REAL_step':ROTATIONS_DEGREES.tolist(),
       'same_real_observed_WGS84_step_length_preserved':True,
       'original_gull_static_GIC_2017_2019_tidal_WETLAND_not_true_dry_available':True,
       'original_GIC_provider_MD5_receipts':receipts,
       'original_GIC_native_source_coverage':dict(stopped),
       'real_GIC_total_original_distinct_native_tile_sources':len(grouped),
       'original_bird_IDs_and_actual_or_alt_GPS_positions_NOT_EXPORTED':True}
