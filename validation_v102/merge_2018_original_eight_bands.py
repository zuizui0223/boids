"""v102 merge original v97 independently observed 2018 7 source bands and three
fixed source-only UID-mod-3 N_00_15 2018 original data fragments.
No effect estimation and no post-source removal of failed station IDs.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json,shutil,argparse
from shard_fixed_original_2018_N00 import BAND,N_SHARDS,ORIGINAL_2019_SOURCE_N
from original_UHSLC_2018_holdout import TEST_YEAR
EXPECTED_OTHER={'N_15_30','N_30_45','N_45_60','N_60_75','S_00_15','S_30_45','S_45_60'}
V97_ANALYSIS='V97_INDEPENDENT_2018_UHSLC_TIDE_SOLAR_ORIGINAL_HOURLY_HOLDOUT'
def counted_ids(d):
    # Exactly one fixed identity from each of three mutually exclusive original-source statuses.
    accepted=[int(x['uid']) for x in d['site_outputs']]
    failed=[int(x['id']) for x in d['source_failures']]
    qc=[int(x['id']) for x in d['source_quality_not_admitted']]
    ids=accepted+failed+qc
    if len(set(ids))!=len(ids):raise ValueError('STOP_DUPLICATE_ORIGINAL_STATION_IN_DIFFERENT_2018_SOURCE_STATUSES')
    return ids
def merge(shard_files,old_band_files,original_v94N00,output_dir):
    if len(shard_files)!=N_SHARDS or len(old_band_files)!=7:
        raise ValueError('STOP_ORIGINAL_SOURCE_ARTIFACT_COUNT_NOT_3_PLUS_7')
    original=json.loads(Path(original_v94N00).read_text())
    if original['band']!=BAND or original['analysis']!='V94_ALL_STATIONS_2019_ORIGINAL_UHSLC_HOURLY_TIDE_SOLAR_PHYSICAL':
        raise ValueError('STOP_ORIGINAL_2019_NATIVE_SOURCE_CHANGED')
    source_id={int(s['uid']) for s in original['raw_station_outcomes']}
    if len(source_id)!=ORIGINAL_2019_SOURCE_N:
        raise ValueError('STOP_2019_FIXED_22_N00_STATION_SOURCE_CHANGED')
    sourcehash=sha256(Path(original_v94N00).read_bytes()).hexdigest()
    seen_shards={};allids=set()
    output={'analysis':V97_ANALYSIS,'original_2019_selection_artifact_run':42616065580,
       'year':TEST_YEAR,'band':BAND,
       'original_preselected_2019_source_eligible_site_n':ORIGINAL_2019_SOURCE_N,
       'site_outputs':[],'source_failures':[],'source_quality_not_admitted':[],
       '2018_results_MUST_NOT_BE_USED_FOR_2019_MODEL_FIT':True}
    for path in shard_files:
        d=json.loads(Path(path).read_text())
        if d.get('analysis')!=V97_ANALYSIS or d.get('year')!=2018 or d.get('band')!=BAND:
            raise ValueError('STOP_2018_ORIGINAL_SHARD_SCIENTIFIC_DEF_CHANGED')
        meta=d.get('source_shard_2019_fixed_UID_MOD_3') or {}
        shard=meta.get('shard')
        if shard in seen_shards or shard not in range(N_SHARDS) or meta.get('n_shards')!=N_SHARDS:
            raise ValueError('STOP_SOURCE_SHARDS_MISSING_OR_REPEAT')
        if meta.get('native_v94_original_2019_artifact_sha256')!=sourcehash:
            raise ValueError('STOP_DIFFERENT_ORIGINAL_2019_TRAINING_FRAME_SOURCE')
        expectation={uid for uid in source_id if uid%N_SHARDS==shard}
        actual=set(meta.get('fixed_2019_shard_original_source_station_ids') or [])
        if actual!=expectation:
            raise ValueError('STOP_SOURCE_ONLY_SHARD_ORIGINAL_ID_SELECTION_CHANGED')
        ids=counted_ids(d)
        if set(ids)!=actual or set(ids)&allids or len(ids)!=d['original_preselected_2019_source_eligible_site_n']:
            raise ValueError('STOP_ORIGINAL_2018_SOURCE_FRAGMENT_MISSING_OR_REPEAT')
        allids.update(ids)
        seen_shards[shard]={'source_ids':len(ids),
            'original_source_2018_valid':len(d['site_outputs']),
            'original_source_2018_qc_not_admitted':len(d['source_quality_not_admitted']),
            'original_source_2018_download_failures':len(d['source_failures'])}
        for k in ('site_outputs','source_failures','source_quality_not_admitted'):
            output[k].extend(d[k])
    if set(seen_shards)!=set(range(N_SHARDS)) or allids!=source_id:
        raise ValueError('STOP_SOURCE_SHARD_UNION_ORIGINAL_2019_22_IDS_NOT_EXHAUSTIVE')
    for k,idfield in [('site_outputs','uid'),('source_failures','id'),('source_quality_not_admitted','id')]:
        output[k].sort(key=lambda x:int(x[idfield]))
    output['summary']={
        '2019_original_source_site_n':ORIGINAL_2019_SOURCE_N,
        '2018_original_hourly_qualified_site_n':len(output['site_outputs']),
        '2018_qc_failed_count':len(output['source_quality_not_admitted']),
        '2018_transport_or_provider_failed_count':len(output['source_failures'])}
    output['v102_source_transport_only_recovery']={
        'original_cancelled_run':42729101678,
        'source_N00_shards_UID_mod_3':seen_shards,
        'full_original_v94_2019_22_UID_SHA256':sourcehash,
        'no_biological_outcomes':True}
    Path(output_dir).mkdir(parents=True,exist_ok=True)
    target=Path(output_dir)/'v97-original-UHSLC-2018-N_00_15.json'
    target.write_text(json.dumps(output,sort_keys=True,indent=2)+'\n')
    passed={BAND}
    for path in old_band_files:
        obj=json.loads(Path(path).read_text())
        b=obj.get('band')
        if b not in EXPECTED_OTHER or b in passed or obj.get('analysis')!=V97_ANALYSIS or obj.get('year')!=2018:
            raise ValueError('STOP_ORIGINAL_2018_OTHER_BAND_IDENTITY_SOURCE')
        expected_n=obj['original_preselected_2019_source_eligible_site_n']
        if len(counted_ids(obj))!=expected_n:
            raise ValueError('STOP_ORIGINAL_PREVIOUS_2018_BAND_SOURCE_NOT_EXHAUSTIVE')
        passed.add(b)
        shutil.copyfile(path,Path(output_dir)/f'v97-original-UHSLC-2018-{b}.json')
    if passed!={BAND}|EXPECTED_OTHER or len(list(Path(output_dir).glob('v97-original-UHSLC-2018-*.json')))!=8:
        raise ValueError('STOP_8_BAND_ORIGINAL_SOURCE_REASSEMBLY_INCOMPLETE')
    print('V102_ORIGINAL_2018_RECOVERED_FULL_8BAND_SOURCE '+json.dumps({
        'bands':sorted(passed),'N00_original_source_ids':len(allids),
        'N00_original_2018_admitted':len(output['site_outputs']),
        'N00_original_2018_QC_failure':len(output['source_quality_not_admitted']),
        'N00_original_2018_transport_failure':len(output['source_failures']),
        'source_original_biological_outcome_estimated':False},sort_keys=True),flush=True)
    return output
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument('--source-shards-dir',required=True)
    p.add_argument('--original-seven-v97-dir',required=True)
    p.add_argument('--original-v94-N00-json',required=True)
    p.add_argument('--output-dir',required=True)
    a=p.parse_args()
    shards=list(Path(a.source_shards_dir).rglob('v102-shard-N_00_15-*.json'))
    original7=list(Path(a.original_seven_v97_dir).rglob('v97-original-UHSLC-2018-*.json'))
    merge(shards,original7,a.original_v94_N00_json,a.output_dir)
