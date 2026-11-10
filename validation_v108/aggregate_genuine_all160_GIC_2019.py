"""v108 source-complete 2019 UHSLC 160 gauges × original GIC 2017–19 static
tidal-WETLAND probability source, with source-level pilot identity replay and
100-km source-geometry clusters. NOT actual exposed tidal flat or animal time niche.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict
from math import isfinite
from statistics import mean,median
import argparse,json
import numpy as np
from aggregate_all_2019_physical import coastal_clusters,spearman
from all_2019_gauges_GIC_tidalwetland_source import (
    SHARD_COUNT,ORIGINAL_SOURCE_STATIONS,ORIGINAL_CANDIDATE_STATIONS,
    assigned_source_shard)
from real_global_UHSLC_hourly_station_manifest import _latitude_band
SOURCE_RUN_V107=42738720185
SOURCE_RUN_V106=42737938244
COMPLETE='ADMITTED_COMPLETE_10KM_TIDAL_WETLAND_RF_SOURCE'
GIC_VALUE_KEY='actual_2019_GIC_tidal_wetland_10km_static_source'
PILOT_VALUE_KEY='true_2019_gauge_10km_static_tidal_wetland_RF_agreement'
MEASURES=['n_valid_original_GIC_pixels_10km',
          'RF_tidal_wetland_probability_mean_source_valid_pixels',
          'fraction_valid_source_pixels_RF_agreement_ge20',
          'fraction_valid_source_pixels_RF_agreement_ge50']
def source_census(v107files):
    if len(v107files)!=SHARD_COUNT:
        raise ValueError('STOP_REQUIRE_ALL_16_ORIGINAL_GIC_2019_SOURCE_TILE_SHARDS')
    results=[]; seen_shard=set(); statuses=Counter()
    for file in v107files:
        x=json.loads(Path(file).read_text())
        shard=x.get('this_fixed_tile_shard')
        if x.get('analysis')!='V107_ALL160_GENUINE_2019_GIC_TIDAL_WETLAND_PROBABILITY_GAUGE_GEOSPATIAL' or x.get('status')!='SOURCE_EXHAUSTIVE_SHARD' or shard in seen_shard or shard not in range(SHARD_COUNT):
            raise ValueError('STOP_ORIGINAL_GIC_SOURCE_SHARD_IDENTITY_OR_STATUS_CHANGED')
        seen_shard.add(shard)
        row=x['source_results']
        if len(row)!=x['selected_original_gauge_count_this_shard'] or len(row)!=x['source_original_gauges_represented']:
            raise ValueError('STOP_ORIGINAL_GIC_SHARD_SOURCE_COUNTS_NOT_EXHAUSTIVE')
        ids=sorted(s['original_2019_UHSLC_station_ID'] for s in row)
        if ids!=x['cohort_original_source_station_UIDs_this_shard']:
            raise ValueError('STOP_ORIGINAL_GIC_NATIVE_SOURCE_SHARD_STATION_IDENTITY_DIFFERENT')
        for r in row:
            uid=r['original_2019_UHSLC_station_ID']
            tile=(r.get('original_GIC_fixed_tile') or {}).get('native_GCS_tile_name')
            if r['predeclared_tile_hash_shard']!=shard or assigned_source_shard(tile,uid)!=shard:
                raise ValueError('STOP_SOURCE_ADAPTIVE_POST_OUTCOME_SHARD_SELECTION')
            statuses[r['source_status']]+=1
            results.append(r)
    ids=[r['original_2019_UHSLC_station_ID'] for r in results]
    if seen_shard!=set(range(SHARD_COUNT)) or len(ids)!=ORIGINAL_SOURCE_STATIONS or len(set(ids))!=ORIGINAL_SOURCE_STATIONS or len({r['original_2019_station_band'] for r in results})!=8:
        raise ValueError('STOP_MISSING_ORIGINAL_160_PUBLIC_2019_GAUGES_SOURCE')
    results.sort(key=lambda r:r['original_2019_UHSLC_station_ID'])
    return results,dict(statuses)

def pilot_exact_replay(original,pilotfiles):
    if len(pilotfiles)!=8:raise ValueError('STOP_ORIGINAL_EIGHT_SITES_PILOT_SOURCE_MISSING')
    indexed={s['original_2019_UHSLC_station_ID']:s for s in original}
    out=[]
    seen=set()
    for path in pilotfiles:
        pilot=json.loads(Path(path).read_text())
        uid=pilot['2019_original_UHSLC_station_id']
        if uid in seen or uid not in indexed:raise ValueError('STOP_ORIGINAL_PILOT_GAUGE_REPLAY_ID_CHANGED')
        seen.add(uid);p=indexed[uid]
        if abs(p['original_2019_observed_low_tide_x_sun_daily_absM']-pilot['2019_measured_gauge_mean_abs_M'])>1.e-12 or abs(p['original_2019_measured_tidal_form_F']-pilot['2019_measured_gauge_form_factor_F'])>1e-12:
            raise ValueError('STOP_ORIGINAL_PILOT_GAUGE_TIDE_SOURCE_DRIFT')
        r=p.get(GIC_VALUE_KEY) or {};q=pilot.get(PILOT_VALUE_KEY) or {}
        compared=0
        if q:
            if not r:raise ValueError('STOP_ORIGINAL_PILOT_GIC_RASTER_REPLAY_UNAVAILABLE')
            for measure in MEASURES:
                a=r.get(measure);b=q.get(measure)
                if a is None or b is None:
                    if a!=b:raise ValueError('STOP_PILOT_GIC_SOURCE_MASK_DIFFERENT')
                elif abs(float(a)-float(b))>1.e-10:
                    raise ValueError('STOP_PILOT_GIC_SOURCE_RASTER_PIXELS_CHANGED_'+measure)
                compared+=1
        elif r:
            raise ValueError('STOP_PILOT_SOURCE_ABSENCE_BUT_NEW_UNIDENTIFIED_GIC_VALUES')
        out.append({'original_UHSLC_id':uid,'native_GIC_tile_repeated_source_fields':compared,
                    'pilot_gic_status':pilot['source_status'],'global_gic_status':p['source_status']})
    if len(out)!=8:raise ValueError('STOP_ORIGINAL_PILOT_UNIQUE_SITE_N_NOT8')
    return sorted(out,key=lambda x:x['original_UHSLC_id'])

def region_source_coverage(original):
    geo=[{'uid':r['original_2019_UHSLC_station_ID'],
          'latitude':r['original_2019_station_latitude'],
          'longitude_signed':r['original_2019_station_longitude_signed'],
          'data':r} for r in original]
    groups=coastal_clusters(geo)
    if len(groups)!=130:raise ValueError('STOP_ORIGINAL_2019_100KM_COASTAL_REGIONS_GEOMETRY_DRIFT')
    out=[]
    for g in groups:
        ok=[x['data'] for x in g if x['data']['source_status']==COMPLETE]
        item={'original_station_UIDs':[x['uid'] for x in g],
            'original_station_n':len(g),
            'n_gauges_full_10km_original_GIC_pixel_support':len(ok),
            'n_gauges_not_full_10km_source':len(g)-len(ok),
            'region_source_status':'FULL_SOURCE_COVERAGE' if len(ok)==len(g) else
                ('PARTIAL_SOURCE_COVERAGE' if ok else 'NO_SOURCE_COVERAGE')}
        if ok:
            item.update({
               'mean_static_GIC_tidalwetland_RF_agreement_0_100':float(mean(
                    r[GIC_VALUE_KEY]['RF_tidal_wetland_probability_mean_source_valid_pixels'] for r in ok)),
               'mean_fraction_valid_10km_pixels_RF_agreement_ge50':float(mean(
                    r[GIC_VALUE_KEY]['fraction_valid_source_pixels_RF_agreement_ge50'] for r in ok)),
               'mean_source_year_2019_F':float(mean(
                    r['original_2019_measured_tidal_form_F'] for r in ok)),
               'mean_2019_source_daily_abs_M':float(mean(
                    r['original_2019_observed_low_tide_x_sun_daily_absM'] for r in ok))})
        out.append(item)
    return out

def _summarize_associations(regions):
    vals=[r for r in regions if r['region_source_status']=='FULL_SOURCE_COVERAGE']
    any_valid=[r for r in regions if r['region_source_status']!='NO_SOURCE_COVERAGE']
    def calc(rows):
        if len(rows)<8:return {'n':len(rows),'status':'SOURCE_TOO_FEW_VALID_INDEPENDENT_COASTS'}
        return {'n':len(rows),
          'mean_source_static_tidal_wetland_RF_agreement_0_100':float(mean(
            r['mean_static_GIC_tidalwetland_RF_agreement_0_100'] for r in rows)),
          'mean_fraction_source_RF_ge50':float(mean(
            r['mean_fraction_valid_10km_pixels_RF_agreement_ge50'] for r in rows)),
          'Spearman_2019_physical_tide_form_F_vs_source_static_wetland_RF50_descriptive':float(spearman(
             [r['mean_source_year_2019_F'] for r in rows],
             [r['mean_fraction_valid_10km_pixels_RF_agreement_ge50'] for r in rows])),
          'Spearman_2019_physical_solar_gauge_absM_vs_static_wetland_RF50_descriptive':float(spearman(
             [r['mean_2019_source_daily_abs_M'] for r in rows],
             [r['mean_fraction_valid_10km_pixels_RF_agreement_ge50'] for r in rows])),
          'Spearman_2019_tidal_form_F_vs_gauge_absM_same_source_ref':float(spearman(
             [r['mean_source_year_2019_F'] for r in rows],
             [r['mean_2019_source_daily_abs_M'] for r in rows])),
          'geographical_inference_for_biological_time_niche':'NONE_NOT_MEASURED'}
    return {'fully_original_10km_area_covered_100km_coasts_only':calc(vals),
        'any_complete_site_in_100km_coast_with_partial_coverage_flagged':calc(any_valid)}

def run(v107dir,v106dir,output):
    files=list(Path(v107dir).rglob('v107-native-original-2019-wetland-160cohort-shard-*.json'))
    pilot=list(Path(v106dir).rglob('v106-genuine-2019-GIC-gauge-*.json'))
    original,status=source_census(files)
    replay=pilot_exact_replay(original,pilot)
    groups=region_source_coverage(original)
    groupstat=Counter(g['region_source_status'] for g in groups)
    by_band=defaultdict(Counter)
    for x in original:by_band[x['original_2019_station_band']][x['source_status']]+=1
    report={'analysis':'V108_2019_160_UHSLC_GENUINE_ORIGINAL_GIC_TIDAL_WETLAND_RF_GLOBAL_100KM_SPATIAL_QA',
      '2026_original_raster_shard_run':SOURCE_RUN_V107,
      'original_pilot_8_raster_source_run':SOURCE_RUN_V106,
      'source_frozen_gauge_station_n':ORIGINAL_SOURCE_STATIONS,
      'original_source_station_shards_n':SHARD_COUNT,
      'source_status_all_160_original':status,
      'source_region_100km_total':len(groups),
      'source_region_100km_genuine_map_coverage':dict(groupstat),
      'status_by_preexisting_2019_15deg_band':{k:dict(v) for k,v in sorted(by_band.items())},
      'source_true_eight_pilot_exact_replay_all':replay,
      'descriptive_physical_vs_static_wetland_source_proximity':_summarize_associations(groups),
      'region_level_2019_source_genuine_static_geospatial_probabilities':groups,
      'NO_BIOLOGICAL_NICHE_OR_TIDAL_FLAT_DRY_HOURS':True,
      'science_claim_boundary':'GIC 2017–2019 random forest tidal wetland probability includes marsh, mangrove, flats; tidal form F→|M| already physically expected by four-harmonic null; no species niches measured.'}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V108_REAL_ALL160_UHSLC_GIC_GLOBAL_WETLAND_SOURCE_AUDIT '+json.dumps({
        'original_2019_public_gauge_n':len(original),
        'original_100km_geo_regions':len(groups),
        'original_gauge_source_quality':status,
        'geo_region_source_coverage':dict(groupstat),
        'eight_original_pilot_site_replay_count':len(replay),
        'descriptive_static_wetland_source_correlations':
            report['descriptive_physical_vs_static_wetland_source_proximity'],
        'not_actual_exposed_habitat_or_organism_niche':True},sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument('--v107-source-dir',required=True)
    p.add_argument('--v106-pilot-dir',required=True)
    p.add_argument('--output',required=True)
    x=p.parse_args();run(x.v107_source_dir,x.v106_pilot_dir,x.output)
