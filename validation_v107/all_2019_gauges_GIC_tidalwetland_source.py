"""v107 all 160 original eligible 2019 UHSLC gauge sites × actual original
2017–2019 GIC tidal-WETLAND probability within 10km, exact native 2019
tile-source grouping. Public physical environment only; no species/foraging.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse,json
import rasterio
from aggregate_all_2019_physical import macro_rows
from real_global_UHSLC_hourly_station_manifest import _latitude_band
from gic2019_real_10km_gauge_buffer import (
    read_original_geotransform,native_expected_tile,metadata_for_native_tile,
    download_and_verify_original_gcs_tile,source_10km_wetland_probability,
    SourceUnavailable,GLOBAL_V94_RUN,PARENT_V105_RUN
)
SHARD_COUNT=16
ORIGINAL_SOURCE_STATIONS=160
ORIGINAL_CANDIDATE_STATIONS=564
EXPECTED_BANDS=12
def assigned_source_shard(native_tile_name_or_none,uid):
    """Source geometry alone; no dynamic tide effect/observed habitat used."""
    if native_tile_name_or_none is not None:
        return int.from_bytes(sha256(native_tile_name_or_none.encode('utf-8')).digest(),'big')%SHARD_COUNT
    return int(uid)%SHARD_COUNT

def cohort_by_source_location(v94source,geo_source):
    paths=list(Path(v94source).rglob('v94-2019-original-source-*.json'))
    sites,byband,counts,_=macro_rows(paths)
    if len(paths)!=EXPECTED_BANDS or counts['candidate']!=ORIGINAL_CANDIDATE_STATIONS or counts['eligible']!=ORIGINAL_SOURCE_STATIONS:
        raise ValueError('STOP_FULL_564_2019_ORIGINAL_SOURCE_CENSUS_NOT_PRESERVED')
    orig=read_original_geotransform(geo_source)
    allrow=[]
    for s in sorted(sites,key=lambda v:int(v['uid'])):
        info={'original_2019_UHSLC_station_ID':int(s['uid']),
          'original_2019_UHSLC_station_country':s['country'],
          'original_2019_station_latitude':float(s['latitude']),
          'original_2019_station_longitude_signed':float(s['longitude_signed']),
          'original_2019_station_band':_latitude_band(s['latitude']),
          'original_2019_observed_low_tide_x_sun_daily_absM':
              float(s['opportunity']['mean_daily_abs_M']),
          'original_2019_measured_tidal_form_F':float(s['form_factor_F']),
          'source_status':'NOT_STARTED'}
        try:
            tile=native_expected_tile(float(s['latitude']),float(s['longitude_signed']),orig)
            info['original_GIC_fixed_tile']=tile
            sh=assigned_source_shard(tile['native_GCS_tile_name'],s['uid'])
        except SourceUnavailable as e:
            info['source_status']='SOURCE_OUTSIDE_NATIVE_GIC_2019_TILE_GRID_NOT_NEGATIVE_HABITAT'
            info['source_failure_reason']=str(e)
            sh=assigned_source_shard(None,s['uid'])
        info['predeclared_tile_hash_shard']=sh
        allrow.append(info)
    ids=[x['original_2019_UHSLC_station_ID'] for x in allrow]
    if len(ids)!=160 or len(set(ids))!=160:
        raise ValueError('STOP_ORIGINAL_SOURCE_UID_DUPLICATE_OR_MISSING')
    return allrow,counts,orig

def run(v94dir,v105audit,shard,outpath):
    if not isinstance(shard,int) or not 0<=shard<SHARD_COUNT:
        raise ValueError('STOP_TILE_SOURCE_SHARD_OUTSIDE_16_PREDECLARED_SHARDS')
    original,census,orig_aff=cohort_by_source_location(v94dir,v105audit)
    selected=[x for x in original if x['predeclared_tile_hash_shard']==shard]
    grouped=defaultdict(list)
    report={'analysis':'V107_ALL160_GENUINE_2019_GIC_TIDAL_WETLAND_PROBABILITY_GAUGE_GEOSPATIAL',
       'source_original_v94_run':GLOBAL_V94_RUN,'source_original_v105_run':PARENT_V105_RUN,
       '2019_original_full_station_candidates':census['candidate'],
       '2019_original_quality_eligible_site_n_all_shards':census['eligible'],
       'tile_shard_n':SHARD_COUNT,'this_fixed_tile_shard':shard,
       'predeclared_source_only_UID_or_tile_hash_assignment':True,
       'selected_original_gauge_count_this_shard':len(selected),
       'cohort_original_source_station_UIDs_this_shard':sorted(x['original_2019_UHSLC_station_ID'] for x in selected),
       'source_results':[],'source_failure_details':[],
       'biological_endpoint':'NONE',
       'habitat_semantic_boundary':'GIC twprobabilityEnd 2017–2019 random forest tidal wetland agreement includes flat+mangrove+marsh. NOT site dry habitat, prey or animal niche.'}
    for x in selected:
        if x['source_status'].startswith('SOURCE_OUTSIDE_'):
            report['source_results'].append(x)
        else:grouped[x['original_GIC_fixed_tile']['native_GCS_tile_name']].append(x)
    with TemporaryDirectory() as temp:
        for k,(tile_name,originals) in enumerate(sorted(grouped.items()),1):
            try:
                provider=metadata_for_native_tile(originals[0]['original_GIC_fixed_tile'])
                dest=Path(temp)/'original_tile.tif'
                receipt=download_and_verify_original_gcs_tile(provider,dest)
                with rasterio.open(dest) as raster:
                    if raster.crs is None or raster.crs.to_string()!='EPSG:4326' or raster.count!=1:
                        raise ValueError('STOP_GIC_NATIVE_TIDAL_WETLAND_GEOMETRY_CRITICAL_DRIFT')
                    first=originals[0]['original_GIC_fixed_tile']
                    expected_c=orig_aff.c+first['expected_colstart_original_pixels']*orig_aff.a
                    expected_f=orig_aff.f+first['expected_rowstart_original_pixels']*orig_aff.e
                    if (abs(raster.transform.a-orig_aff.a)>1e-10 or
                        abs(raster.transform.e-orig_aff.e)>1e-10 or
                        abs(raster.transform.c-expected_c)>1.1*abs(orig_aff.a) or
                        abs(raster.transform.f-expected_f)>1.1*abs(orig_aff.e)):
                        raise ValueError('STOP_GIC_ORIGINAL_TILE_NATIVE_GEOREFERENCE_MISMATCH')
                    for s in originals:
                        out=dict(s)
                        out['native_GCS_source_original_metadata']={'object':tile_name,
                            'source_size_bytes':provider['size'],
                            'original_source_generation':provider['generation'],
                            'verified_provider_MD5':receipt['source_original_GCS_provider_MD5_verified']}
                        p=source_10km_wetland_probability(raster,
                                  s['original_2019_station_latitude'],
                                  s['original_2019_station_longitude_signed'])
                        out['actual_2019_GIC_tidal_wetland_10km_static_source']=p
                        out['source_status']=('ADMITTED_COMPLETE_10KM_TIDAL_WETLAND_RF_SOURCE' if
                            p.get('complete_10km_circle_in_this_tile',False) and
                            p.get('n_valid_original_GIC_pixels_10km',0)>0 else
                            'TRUNCATED_OR_MASKED_10KM_SINGLE_TILE_UNFIT_FOR_SITE_COMPARISON')
                        report['source_results'].append(out)
                dest.unlink(missing_ok=True)
            except SourceUnavailable as e:
                for s in originals:
                    out=dict(s)
                    out['source_status']='SOURCE_UNAVAILABLE_NOT_HABITAT_ABSENCE'
                    out['source_failure_reason']=str(e)
                    report['source_results'].append(out)
                report['source_failure_details'].append({'native_original_tile':tile_name,
                                                          'source_error':str(e),
                                                          'source_UIDs':[x['original_2019_UHSLC_station_ID'] for x in originals]})
            print('V107_ORIGINAL_SOURCE_TILE_BATCH '+json.dumps({'shard':shard,
              'n_tiles_processed':k,'original_tile_source':tile_name,
              'n_source_station_ids':len(originals),
              'source_station_admitted_complete_count':sum(x.get('source_status')==
                'ADMITTED_COMPLETE_10KM_TIDAL_WETLAND_RF_SOURCE' for x in report['source_results'])},
              sort_keys=True),flush=True)
    report['source_results'].sort(key=lambda x:x['original_2019_UHSLC_station_ID'])
    ids=[x['original_2019_UHSLC_station_ID'] for x in report['source_results']]
    if len(ids)!=len(selected) or len(set(ids))!=len(selected):
        raise ValueError('STOP_ORIGINAL_SOURCE_SHARD_GAUGE_EXHAUSTIVENESS_OR_DUPLICATION')
    status=dict(Counter(x['source_status'] for x in report['source_results']))
    report['source_status_summary']=status
    report['source_original_gauges_represented']=len(ids)
    report['source_original_distinct_GIC_tile_requests']=len(grouped)
    report['status']='SOURCE_EXHAUSTIVE_SHARD' if len(ids)==len(selected) else 'STOP'
    Path(outpath).parent.mkdir(parents=True,exist_ok=True)
    Path(outpath).write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V107_ALL160_WETLAND_PILOT_TILE_SHARD_FINAL '+json.dumps({
      'shard':shard,'status':report['status'],
      'original_station_IDs_in_this_shard':len(ids),
      'original_distinct_native_GCS_tiles_requested':len(grouped),
      'source_status_counts':status,
      'source_coverage_is_NOT_true_dry_or_biological_habitat':True},sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v94-source-dir',required=True)
    p.add_argument('--v105-original-geo-audit',required=True)
    p.add_argument('--shard',type=int,required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.v94_source_dir,a.v105_original_geo_audit,a.shard,a.output)
