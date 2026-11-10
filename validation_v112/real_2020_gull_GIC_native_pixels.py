"""v112 original public GIC wetland raster source: extract native 2020
two-gull GPS position-at-fix RF pixels from independently measured 2017–19 map.
Output anonymous source counts only; source bytes ephemeral. No raw trajectories.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from rasterio.windows import Window
import json
import numpy as np
import rasterio
from gic2019_real_10km_gauge_buffer import (
    read_original_geotransform,native_expected_tile,metadata_for_native_tile,
    download_and_verify_original_gcs_tile,SourceUnavailable)
from gull_GIC_native_tidesolar_occupancy import (
    original_gull_position_opportunity,descriptive_real_RF_location_use)

MAX_NATIVE_SOURCE_TILES=4
MAX_BBOX_PIXELS_PER_TILE=8_000_000
SOURCE_RUN_GIC_V105=42737124600
SOURCE_GIC_MAX_RADIUS_KM=30.
PREDECLARED_PRIMARY_RADIUS_KM=20.

def source_2020_original_gull_GIC_pixels(bird_hour,authenticated_v105_raster_georef):
    """Uses ORIGINAL WGS84 bird position + original native GCS source TIFF tile.
    Native GIC RF mask is respected (0 is genuine score).
    """
    aff=read_original_geotransform(authenticated_v105_raster_georef)
    events,sourceqa=original_gull_position_opportunity(
        bird_hour,radius=SOURCE_GIC_MAX_RADIUS_KM)
    grouped=defaultdict(list)
    sourcecounts=Counter()
    for idx,e in enumerate(events):
        e['source_original_GIC_valid_RF']=None
        try:
            candidate=native_expected_tile(float(e['latitude']),float(e['longitude']),aff)
            grouped[candidate['native_GCS_tile_name']].append((idx,candidate))
        except SourceUnavailable:
            sourcecounts['outside_native_GIC_grid_not_negative_habitat']+=1
    if len(grouped)>MAX_NATIVE_SOURCE_TILES:
        raise ValueError('STOP_V112_ORIGINAL_GIC_SOURCE_TILES_MORE_THAN_4_PREDECLARED')
    tile_receipts=[]
    with TemporaryDirectory(prefix='boids_v112_original_gull_tidalwetland_') as tmp:
        for k,(filename,locations) in enumerate(sorted(grouped.items())):
            try:
                provenance=metadata_for_native_tile(locations[0][1])
                path=Path(tmp)/f'tile{k}.tif'
                digest=download_and_verify_original_gcs_tile(provenance,path)
                with rasterio.open(path) as ds:
                    if ds.crs is None or ds.crs.to_string()!='EPSG:4326' or ds.count!=1:
                        raise ValueError('STOP_V112_GIC_NATIVE_TIFF_CRS_BAND_INVALID')
                    ref=locations[0][1]
                    expected_c=aff.c+ref['expected_colstart_original_pixels']*aff.a
                    expected_f=aff.f+ref['expected_rowstart_original_pixels']*aff.e
                    if (abs(ds.transform.a-aff.a)>1e-10 or
                        abs(ds.transform.e-aff.e)>1e-10 or
                        abs(ds.transform.c-expected_c)>abs(aff.a)*1.1 or
                        abs(ds.transform.f-expected_f)>abs(aff.e)*1.1):
                        raise ValueError('STOP_V112_PUBLISHER_GIC_NATIVE_TILE_GEOREF_NOT_VERIFIED')
                    rc=[]
                    for idx,candidate in locations:
                        e=events[idx]
                        row,col=ds.index(e['longitude'],e['latitude'])
                        if row<0 or row>=ds.height or col<0 or col>=ds.width:
                            sourcecounts['original_GPS_near_native_tile_edge_not_supported']+=1
                            continue
                        rc.append((idx,row,col))
                    if rc:
                        minrow=min(a[1] for a in rc);maxrow=max(a[1] for a in rc)
                        mincol=min(a[2] for a in rc);maxcol=max(a[2] for a in rc)
                        width=maxcol-mincol+1;height=maxrow-minrow+1
                        if width*height>MAX_BBOX_PIXELS_PER_TILE:
                            raise ValueError('STOP_V112_NATIVE_TILED_PIXEL_WINDOW_TOO_LARGE')
                        img=ds.read(1,window=Window(mincol,minrow,width,height),masked=True)
                        mask=np.ma.getmaskarray(img)
                        vals=np.asarray(img.data)
                        for idx,row,col in rc:
                            r=row-minrow;c=col-mincol
                            if mask[r,c]:
                                sourcecounts['original_native_masked_GIC_tidalwetland_pixel']+=1
                                continue
                            value=float(vals[r,c])
                            if not np.isfinite(value) or value<0 or value>100:
                                raise ValueError('STOP_V112_ORIGINAL_GIC_RF_TIDALWETLAND_VALUE_OUTSIDE_0_100')
                            events[idx]['source_original_GIC_valid_RF']=value
                            sourcecounts['original_native_GIC_RF_pixel_authenticated']+=1
                tile_receipts.append({'genuine_GCS_tidalwetland_tile_name':filename,
                    'original_publisher_file_MD5_verified':digest['source_original_GCS_provider_MD5_verified'],
                    'original_provider_generation':provenance['generation'],
                    'source_original_file_bytes':provenance['size'],
                    'number_original_gull_GPS_fix_source_locations_in_tile':len(locations),
                    'native_2020_GPS_source_pixel_window_source_success':True})
                path.unlink(missing_ok=True)
            except SourceUnavailable as e:
                sourcecounts['unavailable_original_GIC_source_pixels']+=len(locations)
                tile_receipts.append({'genuine_GCS_tidalwetland_tile_name':filename,
                   'source_status':'NATIVE_SOURCE_UNAVAILABLE_NOT_HABITAT_ABSENCE',
                   'source_error':str(e)[:150],
                   'n_native_GPS_FIX_with_original_map_unavailable':len(locations)})
    sitecount=Counter(e['species'] for e in events)
    coverage={s:{
        'original_2020_GPS_fix_source_at_most30km':int(sitecount[s]),
        'original_GIC_RF_valid_source_GPS_pixels':sum(
            e['species']==s and e['source_original_GIC_valid_RF'] is not None for e in events)}
        for s in sitecount}
    return events,{'source_original_GIC_2017_2019_layer':'twprobabilityEnd',
        'source_tidal_wetland_not_bare_flat_or_true_tidal_stage':True,
        'source_original_2020_gull_GPS_source_radius_max_km':SOURCE_GIC_MAX_RADIUS_KM,
        'source_original_2020_native_GPS_fix_QA':sourceqa,
        'source_original_GIC_tile_count':len(grouped),
        'source_original_GIC_TIFF_receipts_anonymized':tile_receipts,
        'source_original_GIC_pixel_coverage_counts':dict(sourcecounts),
        'source_GIC_pixel_gull_species_QA':coverage,
        'no_original_animal_ID_GPS_location_timestamp_GIC_pixel_images_exported':True}

def radius_subset(original_GIC_events,radius):
    if radius not in (10.,20.,30.):
        raise ValueError('STOP_V112_RADIUS_NOT_FROZEN_BEFORE_GIC_SOURCE')
    from two_gull_tide_solar_fourway import great_circle_km
    from original_2020_gull_RWS_source import GEO_PRIMARY
    return [e for e in original_GIC_events
            if great_circle_km(e['latitude'],e['longitude'],*GEO_PRIMARY)<=radius]
