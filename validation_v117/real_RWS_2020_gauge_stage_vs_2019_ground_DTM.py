"""v117 independent REAL 2020 official Roompot gauge stage × 2019 RWS DTM terrain.
Strictly a conditional above-GAUGE-stage screen on four fixed ~100m plots,
NOT local calibrated dry tidalflat, food, bird foraging or temporal niche.
Original DTM vertical NAP is supported by official parent AHN documentation
but NOT independently certified in the 2019 TIFF source band unit tag.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
from math import ceil,pi
from pathlib import Path
import argparse,json,time
import numpy as np
import rasterio
from rasterio.windows import Window
from astral import Observer
from astral.sun import elevation
from original_2019_Oosterschelde_DTM_ground_source import (
    ROOT,LAYER,PROBE_QA,PRIMARY,PROBE_RADIUS_METRES,
    _download_original_raster,_raster_geo_QA,RD)
from original_2020_gull_RWS_source import (
    original_2020_gauge_may_aug,NATIVE_PRIMARY,NATIVE_SECONDARY,
    OriginalSourceStop)

EXPECTED_DTM_SOURCE_SHA256="605db8a6a58cbfb922cfabf11b072664b91c0236b471dcf2081683d17dcfd7ef"
EXPECTED_SOURCE_BYTES=34799884
ORIGINAL_V116_RUN=42833186694
ORIGINAL_V111_ACTUAL_2020_RWS_SOURCE_RUN=42748780612
SCIENTIFIC_WGS84="EPSG:4326"
TARGET_UTC_START=datetime(2020,5,1,tzinfo=timezone.utc)
TARGET_UTC_END=datetime(2020,9,1,tzinfo=timezone.utc)
OFFSET_SCENARIOS_NAP_M=(-.20,0.,+.20)
SUN_ALTITUDE_DAY=3.
SUN_ALTITUDE_NIGHT=-3.
MIN_ORIGINAL_HOURLY_RWS_STAGES=2000
ORIGINAL_SQUARE_PIXELS_PER_AXIS=21
SOURCE_GAUGE_FIXED_ASSIGNMENT={
 "Roompotsluis Buiten gauge":NATIVE_PRIMARY,
 "Roggenplaat shoal":NATIVE_SECONDARY,
 "Neeltje Jans island":NATIVE_PRIMARY,
 "Roompot Marina":NATIVE_SECONDARY}

def _read_original_5m_ground_v116_replay(p,v116artifact):
    origin=json.loads(Path(v116artifact).read_text())
    if (origin.get('analysis')!='V116_2019_OOSTERSCHELDE_ORIGINAL_GROUND_DTM_5M_2M_REAL_RWS_SOURCE_QA'
       or origin.get('source_status')!='ORIGINAL_2019_OOSTERSCHELDE_DTM_RASTER_SOURCE_ADMITTED'):
        raise ValueError('SOURCE_STOP_NATIVE_RWS_2019_DTM_V116_AUTHENTIC_SOURCE_MISSING')
    old=origin['native_raster_admission']['dtm_5']
    if old['source_status']!='DIRECT_ORIGINAL_RWS_2019_DTM_RASTER_READ':
        raise ValueError('SOURCE_STOP_NATIVE_ORIGINAL_DTM_5M_NOT_ADMITTED')
    provenance=old['authentic_original_raster_source']
    if (provenance['original_locally_downloaded_SHA256']!=EXPECTED_DTM_SOURCE_SHA256 or
        provenance['source_native_file_bytes']!=EXPECTED_SOURCE_BYTES):
        raise ValueError('SOURCE_STOP_V116_ORIGINAL_2019_DTM_SHA_DRIFT')
    if sha256(Path(p).read_bytes()).hexdigest()!=EXPECTED_DTM_SOURCE_SHA256:
        raise ValueError('SOURCE_STOP_CURRENT_RWS_2019_GROUND_DTM_SHA_DRIFT')
    return old

def _extract_fixed_original_square(ds,place):
    """Same actual 2019 original pixels as v116; no selecting favorable z or GPS."""
    x,y=RD.transform(place['lon'],place['lat'])
    row,col=ds.index(x,y)
    if not (0<=row<ds.height and 0<=col<ds.width):
        return np.array([],dtype=float),{'status':'OUTSIDE_ORIGINAL_DTM_COVERAGE_NOT_ZERO'}
    pixels=int(ceil(PROBE_RADIUS_METRES/min(abs(ds.res[0]),abs(ds.res[1]))))
    r0=max(0,row-pixels);r1=min(ds.height,row+pixels+1)
    c0=max(0,col-pixels);c1=min(ds.width,col+pixels+1)
    values=ds.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
    z=values.compressed().astype(float)
    return z,{'source_status':'ORIGINAL_RWS_2019_FIXED_100M_DTM_PIXELS',
        'n_source_valid_original_ground_pixels':int(len(z)),
        'n_source_masked':int(values.size-len(z)),
        'n_source_total_native_square_pixels':int(values.size),
        'native_horizontal_cell_area_square_metres':float(abs(ds.transform.a*ds.transform.e))}

def _check_original_v116_plot_replay(plot,old,name):
    previous=[x for x in old['original_fixed_probe_results'] if x['original_source_fixed_probe']==name]
    if len(previous)!=1:
        raise ValueError('SOURCE_STOP_ORIGINAL_2019_FIXED_PLOT_NOT_REPRODUCED')
    before=previous[0]
    if (plot['n_source_valid_original_ground_pixels']!=before['original_valid_ground_height_native_pixels']
       or plot['n_source_total_native_square_pixels']!=before['original_total_native_raster_pixels_in_sample']):
        raise ValueError('SOURCE_STOP_HISTORIC_2019_REAL_GROUND_DTM_PIXEL_COUNT_DRIFT')
    return {'replayed_original_v116_real_2019_ground_mask_count':True,
            'same_exact_fixed_public_plot_as_v116':name}

def _real_hourly_RWS_source(records):
    """Observed 10min TRUE RWS, only clock 00 of each native UTC hour, no interpolation."""
    stages={t:float(v) for t,v in records.items()
        if TARGET_UTC_START<=t<TARGET_UTC_END and t.minute==0 and t.second==0}
    if len(stages)<MIN_ORIGINAL_HOURLY_RWS_STAGES:
        raise OriginalSourceStop('SOURCE_STOP_REAL_2020_RWS_TOO_FEW_TRUE_HOURLY_MEASUREMENTS')
    return stages

def _astral_source_solar_days(utc_times,lat,lon):
    observer=Observer(latitude=float(lat),longitude=float(lon),elevation=0)
    angles=np.array([float(elevation(observer,ts)) for ts in utc_times])
    return angles>SUN_ALTITUDE_DAY, angles<SUN_ALTITUDE_NIGHT

def physical_native_2019_ground_above_2020_real_gauge_source(z,stages_utc,
                                                           lat,lon):
    """Measured RWS GAUGE stage is proxy, NOT local tide at surveyed ground.
    delta scenario adds +0.2m to water => no more above-stage pixels possible.
    """
    heights=np.asarray(z,dtype=float)
    if not len(heights) or not np.isfinite(heights).all():
        return {'source_status':'NOT_ESTIMATED_NO_NATIVE_2019_GROUND_Z'}
    if not len(stages_utc):
        return {'source_status':'NOT_ESTIMATED_NO_2020_NATIVE_RWS_STAGE'}
    stamps=sorted(stages_utc)
    h=np.asarray([stages_utc[t] for t in stamps])
    day,night=_astral_source_solar_days(stamps,lat,lon)
    if not day.any() or not night.any():
        return {'source_status':'NOT_ESTIMATED_NO_TRUE_ASTRONOMICAL_DAY_AND_NIGHT'}
    scenarios={}
    for delta in OFFSET_SCENARIOS_NAP_M:
        frac=(heights[None,:] > (h[:,None]+delta)).mean(axis=1)
        scenarios[str(delta)]={
         'gauge_stage_shift_metres_FIXED_UNCERTAINTY_NOT_CI':delta,
         'native_ground_pixels_mean_above_GAUGE_stage_proportion_all_hours':float(frac.mean()),
         'fraction_original_gauge_hours_at_least_half_plot_above_STAGE':float(np.mean(frac>=.5)),
         'native_ground_pixels_mean_above_GAUGE_stage_proportion_astro_DAY':float(frac[day].mean()),
         'native_ground_pixels_mean_above_GAUGE_stage_proportion_astro_NIGHT':float(frac[night].mean()),
         'astral_DAY_minus_NIGHT_source_fraction_difference':float(frac[day].mean()-frac[night].mean()),
         'mean_absolute_hour_to_hour_change_in_above_stage_fraction':float(np.mean(np.abs(np.diff(frac)))),
         'native_source_gaussian_or_simulated_waterlevels_used':False}
    return {'source_status':'CONDITIONAL_RWS_GAUGE_STAGE_ABOVE_ORIGINAL_2019_GROUND_PROPORTION',
       'original_hour_count_from_genuine_2020_RWS_10min_clock_hour':len(stamps),
       'observed_original_2020_RWS_gauge_level_min_max_mNAP':[float(h.min()),float(h.max())],
       'observed_original_2020_RWS_gauge_level_q05_q50_q95_mNAP':
           np.quantile(h,[.05,.5,.95]).tolist(),
       'original_astronomical_DAY_native_gauge_hours':int(day.sum()),
       'original_astronomical_NIGHT_native_gauge_hours':int(night.sum()),
       'original_solar_twilight_or_neither_hours':int((~day&~night).sum()),
       'original_2019_ground_valid_source_pixels':int(len(heights)),
       'original_2019_ground_native_height_range_min_max':[float(heights.min()),float(heights.max())],
       'original_2019_ground_native_height_median':float(np.median(heights)),
       'genuine_RWS_stage_uncertainty_scenarios':scenarios,
       'vertical_datum_status':'NATIONAL_AHN_PARENT_DOC_SAYS_NAP_BUT_INDIVIDUAL_2019_RWS_DTM_TIFF_VERTICAL_UNIT_TAG_MISSING',
       'hydraulic_h_at_actual_sampled_ground':'NOT_MEASURED_OFFICIAL_GAUGE_STAGE_PROXY',
       'actual_tide_flat_exposure_or_bird_activity':'NOT_ESTIMATED'}

def same_original_transport_retry(call,name,max_attempts=3):
    """Only identical original RWS provider HTTP429, HTTP504, timeout; never source QC."""
    failures=[]
    for i in range(max_attempts):
        try:
            return call(),{'real_original_RWS_source_retrieval_attempts':i+1,
                           'transport_only_retries':failures}
        except OriginalSourceStop as e:
            message=str(e)
            if not any(k in message for k in ('HTTP Error 429','HTTP Error 504',
                                             'timed out','TimeoutError','SOURCE_UNAVAILABLE_RWS')):
                raise
            failures.append({'original_station':name,'attempt':i+1,'network':message[:160]})
            if i==max_attempts-1:raise
            time.sleep(2**i)
    raise AssertionError('unreachable')

def run(v116_original_source_artifact,output):
    report={'analysis':'V117_GENUINE_2020_RWS_ROOMPO_STAGE_X_AUTHENTIC_2019_RWS_OOSTERSCHELDE_DTM5_GAUGE_PROXY_ONLY',
       'actual_source_v116_action':ORIGINAL_V116_RUN,
       'actual_original_RWS_2020_gauge_source_v111':ORIGINAL_V111_ACTUAL_2020_RWS_SOURCE_RUN,
       'original_RWS_2019_DTM_source_SHA256_pre_frozen':EXPECTED_DTM_SOURCE_SHA256,
       'native_geographical_probe_gauge_assignment_FIXED_BEFORE_WETDRY':SOURCE_GAUGE_FIXED_ASSIGNMENT,
       'source_original_RWS_MayAug_2020_tides':{},'source_public_original_DTM_fixed_probe_physical_screening':{},
       'source_vertical_reference':'AHN parent states NAP in meters, native RWS 2019 DTM GeoTIFF band unit does not assert NAP',
       'NO_OBSERVED_GULL_OR_ACTUAL_LOCAL_DRY_WET_HABITAT':True,
       'source_status':'SOURCE_PENDING'}
    for station in (NATIVE_PRIMARY,NATIVE_SECONDARY):
        try:
            (native,proof),retry=same_original_transport_retry(
                lambda:original_2020_gauge_may_aug(station),station)
            globals()[('_NOT_SAVED') if False else '_NOT_DEFINED'] if False else None
            report['source_original_RWS_MayAug_2020_tides'][station]={
                **proof,**retry,
                'real_hourly_native_source_n':len(_real_hourly_RWS_source(native)),
                'source_status':'REAL_2020_MEASURED_RWS_GAUGE_SOURCE'}
            # Hold real measured 10min values only in ephemeral memory, not GitHub artifact.
            if 'original_tides' not in locals(): original_tides={}
            original_tides[station]=_real_hourly_RWS_source(native)
        except (OriginalSourceStop,ValueError,TimeoutError,OSError) as e:
            report['source_original_RWS_MayAug_2020_tides'][station]={
                'source_status':'SOURCE_NOT_ADMITTED_2020_NATIVE_RWS_TIDE',
                'failure':str(e)[:220]}
    if not ('original_tides' in locals() and set(original_tides)=={NATIVE_PRIMARY,NATIVE_SECONDARY}):
        report['source_status']='SOURCE_STOP_ORIGINAL_2020_TWO_RWS_WATERBODIES'
        return save(report,output)
    with __import__('tempfile').TemporaryDirectory() as temp:
        original=Path(temp)/'official_RWS_2019_ground_DTM_5m.tif'
        try:
            receipt=_download_original_raster(original,ROOT+LAYER['dtm_5']['filename'],
                        LAYER['dtm_5']['id'])
            old=_read_original_5m_ground_v116_replay(original,v116_original_source_artifact)
            report['source_original_2019_DTM_provider_verified_download']=receipt
            with rasterio.open(original) as ds:
                if (ds.crs is None or ds.crs.to_string()!='EPSG:28992' or
                    ds.width!=8000 or ds.height!=7500 or
                    abs(ds.res[0]-5)>1e-8 or abs(ds.res[1]-5)>1e-8):
                    raise ValueError('SOURCE_STOP_REAL_2019_DTM_NATIVE_AFFINE_SOURCE_DRIFT')
                for name,loc in PROBE_QA.items():
                    z,q=_extract_fixed_original_square(ds,loc)
                    replay=_check_original_v116_plot_replay(q,old,name)
                    source={'source_probe':name,'native_DTM_source_support':q,
                            'source_original_2019_DTM_replay':replay,
                            'assigned_original_RWS_2020_waterlevel_gauge':SOURCE_GAUGE_FIXED_ASSIGNMENT[name],
                            'same_NAP_vertical_source_from_RWS_AHN_documented_but_raster_tag_not_verified':True}
                    if len(z):
                        physical=physical_native_2019_ground_above_2020_real_gauge_source(
                            z,original_tides[SOURCE_GAUGE_FIXED_ASSIGNMENT[name]],
                            loc['lat'],loc['lon'])
                        source['conditional_original_real_2020_GAUGE_stage_source_screen']=physical
                    else:
                        source['conditional_original_real_2020_GAUGE_stage_source_screen']={
                            'source_status':'NOT_ESTIMATED_NO_ORIGINAL_2019_GROUND_Z'}
                    report['source_public_original_DTM_fixed_probe_physical_screening'][name]=source
        except (ValueError,OriginalSourceStop,TimeoutError,OSError) as e:
            report['source_status']='SOURCE_STOP_ORIGINAL_2019_DTM_OR_REAL_TIDE_REPLAY'
            report['source_failure']=repr(e)[:220]
            return save(report,output)
    report['source_status']='REAL_RWS_2019_GROUND_DTM_AND_2020_GAUGE_STAGE_CONDITIONAL_PHYSICAL_SCREENING_ADMITTED'
    return save(report,output)

def save(obj,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('V117_TRUE_2019_DTM_X_2020_ROOMPO_GAUGE_STAGE_SOURCE_FINAL '+json.dumps({
       'source_status':obj['source_status'],
       'real_2020_measured_RWS_source':{k:v.get('real_hourly_native_source_n') for k,v in obj.get('source_original_RWS_MayAug_2020_tides',{}).items()},
       'original_FIXED_plot_conditional_source_gauge_stage_above_ground':{
          k:{'native_DTM_valid_source':v['native_DTM_source_support']['n_source_valid_original_ground_pixels'],
             'RWS_2020_site_gauge_proxy':v['assigned_original_RWS_2020_waterlevel_gauge'],
             'conditional_physical':v['conditional_original_real_2020_GAUGE_stage_source_screen']}
          for k,v in obj.get('source_public_original_DTM_fixed_probe_physical_screening',{}).items()},
       'NO_actual_local_h_t_bird_foraging_or_intertidal_area':True},sort_keys=True),flush=True)
    return obj
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v116-original-source-artifact',required=True)
    p.add_argument('--output',required=True)
    x=p.parse_args()
    run(x.v116_original_source_artifact,x.output)
