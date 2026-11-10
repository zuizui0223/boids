"""v118 original 2020 two Larus GPS genuine used destination +7 same-real-step
rotations sampled against RWS historical 2019 5m DTM actual ground source mask.

This is coverage accounting ONLY, not actual 2020 dry-flat time, feeding,
gull choice/selection, internal clock or a causal ecological effect. Real
original DTM source lacks native vertical NAP tag and local hydraulic h(x,t).
"""
from __future__ import annotations
import argparse,hashlib,json,math,time
from collections import Counter,defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import rasterio
from rasterio.windows import Window
from pyproj import Transformer
from original_2019_Oosterschelde_DTM_ground_source import ROOT,LAYER,_download_original_raster
from original_2020_gull_RWS_source import (
    fetch_original_gulls,original_2020_gauge_may_aug,NATIVE_PRIMARY,
    OriginalSourceStop,SourceNotAdmitted)
from original_delta_2020_gull_source import FOCAL
from two_gull_tide_solar_fourway import original_movement_opportunities
from original_GIC_equal_step_rotated_destinations import (
    original_geodesic_same_step_length_alternatives,N_ALTERNATIVE_ENDPOINTS)
from true_original_gull_equal_step_BSTI import (
    hard_replay_original_v111_genuine_movement_effects,COMMON_SOURCE_MONTHS)

KNOWN_GENUINE_2019_RWS_DTM5_SHA='605db8a6a58cbfb922cfabf11b072664b91c0236b471dcf2081683d17dcfd7ef'
KNOWN_SOURCE_DTM5_BYTES=34799884
EXPECTED_GULL_STEPS_COMMON_MAY_JULY=45133
ORIGINAL_GULL_TRACK_V115=42789950512
ORIGINAL_REAL_DTM_V116=42833186694
REAL_GAUGE_V117=42834074592
MIN_SOURCE_COMPLETE_EIGHT_DTM_HEIGHT_RATIO=.90
N_SOURCE_NATIVE_GEO_CHUNK_PIXELS=128
ORIGINAL_GROUND_DTM_RWS_CRS='EPSG:28992'
WGS84_NATIVE='EPSG:4326'
TRANSFORM_WGS84_RD=Transformer.from_crs(WGS84_NATIVE,ORIGINAL_GROUND_DTM_RWS_CRS,always_xy=True)

def sample_original_DTM_native_pixels(ds,latitudes,longitudes):
    """No interpolation and exact original lidar native nodata.
    Deterministic 128x128 pixel windows are for bounded source IO only.
    """
    lat=np.asarray(latitudes,dtype=float).reshape(-1)
    lon=np.asarray(longitudes,dtype=float).reshape(-1)
    if len(lat)!=len(lon) or not len(lat) or not (np.isfinite(lat).all() and np.isfinite(lon).all()):
        raise ValueError('SOURCE_STOP_ORIGINAL_2020_GULL_GEO_COORDINATE_INVALID')
    if ds.crs is None or ds.crs.to_string()!=ORIGINAL_GROUND_DTM_RWS_CRS or ds.count!=1:
        raise ValueError('SOURCE_STOP_NOT_THE_ORIGINAL_RWS_EPSG28992_GROUND_DTM')
    X,Y=TRANSFORM_WGS84_RD.transform(lon,lat)
    col=np.floor((X-ds.transform.c)/ds.transform.a).astype(np.int64)
    row=np.floor((Y-ds.transform.f)/ds.transform.e).astype(np.int64)
    inside=(row>=0)&(row<ds.height)&(col>=0)&(col<ds.width)
    values=np.full(len(lat),np.nan,dtype=float)
    groups=defaultdict(list)
    for i in np.flatnonzero(inside):
        groups[(int(row[i]//N_SOURCE_NATIVE_GEO_CHUNK_PIXELS),
                int(col[i]//N_SOURCE_NATIVE_GEO_CHUNK_PIXELS))].append(i)
    for (rblock,cblock),idx in sorted(groups.items()):
        rr=rblock*N_SOURCE_NATIVE_GEO_CHUNK_PIXELS
        cc=cblock*N_SOURCE_NATIVE_GEO_CHUNK_PIXELS
        width=min(N_SOURCE_NATIVE_GEO_CHUNK_PIXELS,ds.width-cc)
        height=min(N_SOURCE_NATIVE_GEO_CHUNK_PIXELS,ds.height-rr)
        src=ds.read(1,window=Window(cc,rr,width,height),masked=True)
        rs=row[idx]-rr
        cs=col[idx]-cc
        masked=np.ma.getmaskarray(src)[rs,cs]
        zs=np.asarray(src.data)[rs,cs].astype(float)
        valid=(~masked)&np.isfinite(zs)
        if (valid & ((zs<-100.)|(zs>250.))).any():
            raise ValueError('SOURCE_STOP_ORIGINAL_DTM_Z_NATIVE_BOUNDS_IMPLAUSIBLE')
        indices=np.asarray(idx,dtype=int)
        values[indices[valid]]=zs[valid]
    q={'n_exact_original_WGS84_coordinates_processed':len(lat),
      'n_original_pixel_centers_inside_published_2019_DTM_tile':int(np.sum(inside)),
      'n_native_source_pixel_ground_z_present':int(np.sum(np.isfinite(values))),
      'n_original_coordinates_outside_2019_DTM_tile':int(np.sum(~inside)),
      'n_original_DTM_inside_source_tile_but_lidar_masked':int(np.sum(inside&~np.isfinite(values))),
      'n_deterministic_128pixel_source_geo_chunks':len(groups),
      'source_no_interpolated_DTM_values':True}
    return values,q

def _v115_same_original_move_source_checks(events):
    if len(events)!=EXPECTED_GULL_STEPS_COMMON_MAY_JULY:
        raise ValueError('STOP_V118_GENUINE_2020_45133_ORIGINAL_MAYJUL_MOVEMENTS_NOT_REPLAYED')
    return dict(Counter(e['taxon'] for e in events))

def native_2019_DTM_source_coverage_two_species(events,ds):
    """Native 2020 GPS destination vs seven exact same real source step rotations;
    masks only, no tide/dry habitat Y or wetland-class threshold selection.
    """
    _v115_same_original_move_source_checks(events)
    beginlat=[e['GPS_departure_lat'] for e in events]
    beginlon=[e['GPS_departure_lon'] for e in events]
    endlat=[e['GPS_arrival_lat'] for e in events]
    endlon=[e['GPS_arrival_lon'] for e in events]
    lats,lons,distances,_=original_geodesic_same_step_length_alternatives(
       beginlat,beginlon,endlat,endlon)
    used,uq=sample_original_DTM_native_pixels(ds,endlat,endlon)
    alts,aq=sample_original_DTM_native_pixels(ds,lats.ravel(),lons.ravel())
    alts=alts.reshape(len(events),N_ALTERNATIVE_ENDPOINTS)
    valid_used=np.isfinite(used)
    full=np.isfinite(alts).all(axis=1)&valid_used
    species={}
    for s in sorted(FOCAL):
        ids=np.array([i for i,e in enumerate(events) if e['taxon']==s],dtype=int)
        sub=full[ids]
        source_used=valid_used[ids]
        n=len(ids)
        if n==0:raise ValueError('STOP_V118_ONE_PREDECLARED_GULL_SPECIES_SOURCE_MISSING')
        unique_birds={events[i]['bird'] for i in ids}
        species[s]={
          'original_genuine_2020_MayJuly_source_independent_gull_birds_with_any_step':len(unique_birds),
          'original_real_GPS_2020_source_movement_steps':n,
          'real_destination_original_2019_DTM_native_z_valid_count':int(np.sum(source_used)),
          'real_destination_DTM_original_source_valid_fraction':float(np.mean(source_used)),
          'actual_and_all_seven_equal_step_alternatives_native_DTM_valid_count':int(np.sum(sub)),
          'actual_and_all_seven_equal_step_alternatives_native_DTM_valid_fraction':float(np.mean(sub)),
          'original_source_survey_DTM_8point_geographic_completeness_ge90pct':bool(np.mean(sub)>=MIN_SOURCE_COMPLETE_EIGHT_DTM_HEIGHT_RATIO),
          'true_original_2020_steps_lt100m_source_only':int(np.sum(distances[ids]<100.)),
          'true_source_dryness_behavior_time_niche_NOT_ESTIMATED':True}
    return {
      'real_2020_gull_movement_source_geometry_and_mask_only':species,
      'source_actual_destination_pixel_support':uq,
      'source_seven_rotated_equal_distance_pixel_support':aq,
      'total_2020_two_species_native_original_steps':len(events),
      'number_total_native_actual_plus_all7_valid_source_steps':int(np.sum(full)),
      'source_pass_predeclared_both_taxa_ge90percent_full_8point_DTM_coverage':bool(
          all(species[s]['original_source_survey_DTM_8point_geographic_completeness_ge90pct'] for s in FOCAL)),
      'source_fail_implies_no_time_varying_biological_availability_effect_estimated':True,
      '2019_native_ground_z_NOT_same_as_2020_tidalflat_accessibility':True}

def _source_transport_retry(call,source,max_attempts=3):
    errors=[]
    for attempt in range(max_attempts):
        try:return call(),{'attempts':attempt+1,'same_source_transport_failures':errors}
        except (OriginalSourceStop,SourceNotAdmitted,TimeoutError,OSError) as e:
            message=str(e)
            if not any(k in message for k in ('SOURCE_UNAVAILABLE','HTTP Error 429','HTTP Error 504',
                                             'timed out','TimeoutError')):
                raise
            errors.append({'original_source':source,'attempt':attempt+1,'transport':message[:160]})
            if attempt==max_attempts-1:raise
            time.sleep(2**attempt)
    raise AssertionError('unreachable')

def run(output):
    out={'analysis':'V118_2020_TWO_GULL_TRUE_GPS_7ROTATED_STEPLENGTH_HISTORIC_RWS_DTM_2019_COVERAGE_SOURCE_ONLY',
         'original_RWS_2019_DTM_sha':KNOWN_GENUINE_2019_RWS_DTM5_SHA,
         'original_source_years':{'gps':2020,'DTM':2019},
         'previous_true_v115_GIC_2020_gull_result':ORIGINAL_GULL_TRACK_V115,
         'previous_RWS_2019_DTM_source':ORIGINAL_REAL_DTM_V116,
         'previous_RWS_true_2020_gauge_source':REAL_GAUGE_V117,
         'source_native_GIC_or_tidalflat_used_suitability_Y':'NOT_ESTIMATED',
         'source_original_bird_IDs_native_GPS_positions_alternative_positions_AND_RWS_height_arrays_NOT_EXPORTED':True,
         'source_status':'SOURCE_PENDING'}
    try:
        (birds,gpsproof),r1=_source_transport_retry(fetch_original_gulls,'corrected Zenodo 2020 original gull')
        (tides,rwsproof),r2=_source_transport_retry(
             lambda:original_2020_gauge_may_aug(NATIVE_PRIMARY),'RWS Roompotsluis Buiten 2020')
        out['original_2020_GPS_source_retrieval_QA']={'source':gpsproof,'transport_retries':r1}
        out['original_2020_RWS_source_retrieval_QA']={'source':rwsproof,'transport_retries':r2}
    except (OriginalSourceStop,SourceNotAdmitted,ValueError,TimeoutError,OSError) as e:
        out['source_status']='SOURCE_STOP_ORIGINAL_2020_GPS_OR_GAUGE'
        out['source_failure']=str(e)[:220]
        return _save(out,output)
    allmoves,original_gps_qa=original_movement_opportunities(birds,radius=20.)
    try:
        # NO SOURCE BATHYMETRY GIC opening before verifying original v111
        # 2020 bird source/endpoints/real tide/sun exact previous effects.
        replay=hard_replay_original_v111_genuine_movement_effects(allmoves,tides)
        out['strict_original_v111_true_GPS_RWS_Y_replay_BEFORE_DTM']=replay
        print('V118_OLD_TRUE_GULL_2020_RWS_SPEED_SOURCE_REPLAY_BEFORE_NEW_DTM '+json.dumps(replay,sort_keys=True),flush=True)
    except ValueError as e:
        out['source_status']='SOURCE_STOP_PREVIOUS_GULL_2020_MOVEMENT_NOT_EXACTLY_REPRODUCED'
        out['prior_replay_failure']=str(e)[:180]
        return _save(out,output)
    common=[e for e in allmoves if e['month'] in COMMON_SOURCE_MONTHS]
    out['original_2020_native_public_gull_step_source_n_before_DTM']=len(common)
    with TemporaryDirectory() as tmp:
        file=Path(tmp)/'true_publisher_RWS_DTM5_original_2019.tif'
        try:
            from original_2019_Oosterschelde_DTM_ground_source import _download_original_raster
            _receipt=_download_original_raster(file,ROOT+LAYER['dtm_5']['filename'],LAYER['dtm_5']['id'])
            if _receipt['original_locally_downloaded_SHA256']!=KNOWN_GENUINE_2019_RWS_DTM5_SHA or _receipt['source_native_file_bytes']!=KNOWN_SOURCE_DTM5_BYTES:
                raise ValueError('SOURCE_STOP_ORIGINAL_2019_RWS_DTM_SHA_OR_FILE_SIZE_DRIFT')
            out['original_2019_ground_DTM5_source_receipt']={**_receipt,
                'native_vertical_georef_limit':'NATIONAL_AHN_HEIGHTS_NAP_BUT_RWS_2019_TIFF_NATIVE_VERTICAL_UNIT_TAG_ABSENT'}
            with rasterio.open(file) as raster:
                if (raster.crs is None or raster.crs.to_string()!=ORIGINAL_GROUND_DTM_RWS_CRS or
                    raster.width!=8000 or raster.height!=7500 or raster.count!=1 or
                    abs(raster.res[0]-5)>1e-10 or abs(raster.res[1]-5)>1e-10):
                    raise ValueError('SOURCE_STOP_ORIGINAL_RWS_NATIVE_2019_DTM_CRS_AFFINE_IDENTITY')
                source=native_2019_DTM_source_coverage_two_species(common,raster)
            out['native_original_2019_DTM_source_vs_original_2020_gull_7step_GPS_COVERAGE']=source
            out['source_status']='SOURCE_VALID_NATIVE_2019_DTM_COVERAGE_ADMITTED_BUT_ANIMAL_DRYNESS_NOT_ESTIMATED'
        except (ValueError,OriginalSourceStop,SourceNotAdmitted,TimeoutError,OSError) as e:
            out['source_status']='SOURCE_STOP_REAL_2019_DTM_NATIVE_SAMPLING'
            out['DTM_original_native_source_failure']=str(e)[:240]
    return _save(out,output)

def _save(report,output):
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    stats=report.get('native_original_2019_DTM_source_vs_original_2020_gull_7step_GPS_COVERAGE') or {}
    print('V118_2020_TRUE_GULL_2019_REAL_DTM_EIGHT_SOURCE_GATE_RESULT '+json.dumps({
       'source_status':report['source_status'],
       'previous_original_v111_birds_source_replayed':(report.get('strict_original_v111_true_GPS_RWS_Y_replay_BEFORE_DTM') or {}).get('source_status'),
       'original_2020_movement_source_n':report.get('original_2020_native_public_gull_step_source_n_before_DTM'),
       'native_DTM_2020_source_species_coverage':stats.get('real_2020_gull_movement_source_geometry_and_mask_only'),
       'all_real_alt_8point_DTM_covered_n':stats.get('number_total_native_actual_plus_all7_valid_source_steps'),
       'both_taxa_90pct_source_gate_for_future_real_animal_local_dry_habitat':stats.get('source_pass_predeclared_both_taxa_ge90percent_full_8point_DTM_coverage'),
       'no_true_local_h_t_or_bird_time_niche_Y_estimated':True},sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
