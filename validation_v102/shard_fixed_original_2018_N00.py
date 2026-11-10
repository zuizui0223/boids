"""v102 transport-only reshard 2018 N_00_15 original UHSLC by fixed station_ID modulo 3.
Does not touch original 2018 scoring or response thresholds; v97 run reused.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
import argparse,json
from original_UHSLC_2018_holdout import run as old_native_2018_run
BAND="N_00_15";N_SHARDS=3;ORIGINAL_2019_SOURCE_N=22
def subset_by_source_only_uid(frame,shard):
    if shard not in range(N_SHARDS):raise ValueError('STOP_ILLEGAL_SOURCE_SHARD')
    ids=[int(s['uid']) for s in frame]
    if len(frame)!=ORIGINAL_2019_SOURCE_N or len(set(ids))!=len(ids):
        raise ValueError('STOP_ORIGINAL_2019_SOURCE_N00_UID_FRAME_CHANGED')
    return [r for r in frame if int(r['uid'])%N_SHARDS==shard]
def run(original_v94_band,shard,outpath):
    doc=json.loads(Path(original_v94_band).read_text())
    if doc.get('analysis')!='V94_ALL_STATIONS_2019_ORIGINAL_UHSLC_HOURLY_TIDE_SOLAR_PHYSICAL' or doc.get('band')!=BAND:
        raise ValueError('STOP_SOURCE_METADATA_MISMATCH')
    rows=doc['raw_station_outcomes']
    selected=subset_by_source_only_uid(rows,shard)
    ids=[r['uid'] for r in selected]
    doc['raw_station_outcomes']=selected
    with TemporaryDirectory() as p:
        file=Path(p)/'fixed_original_source_shard_2019.json'
        file.write_text(json.dumps(doc))
        parent=old_native_2018_run(file,BAND,str(Path(p)/'original_2018_shard.json'))
    parent['source_shard_2019_fixed_UID_MOD_3']={
        'shard':shard,'n_shards':N_SHARDS,'fixed_2019_full_original_band_n':len(rows),
        'fixed_2019_shard_original_source_station_ids':ids,
        'native_v94_original_2019_artifact_sha256':sha256(Path(original_v94_band).read_bytes()).hexdigest(),
        'original_2018_policy_identical_to_v97':True}
    Path(outpath).parent.mkdir(parents=True,exist_ok=True)
    Path(outpath).write_text(json.dumps(parent,sort_keys=True,indent=2)+'\n')
    print('V102_SHARD_2018_COMPLETE '+json.dumps({'shard':shard,'source_ids':ids,
        'source_2018_valid':parent['summary']['2018_original_hourly_qualified_site_n'],
        'source_2018_qc_not_admitted':parent['summary']['2018_qc_failed_count'],
        'source_transport_failed':parent['summary']['2018_transport_or_provider_failed_count']},sort_keys=True),flush=True)
    return parent
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--original-v94-N00-json',required=True)
    p.add_argument('--shard',type=int,required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.original_v94_N00_json,a.shard,a.output)
