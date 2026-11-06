"""Source-authenticated v51 continuation: same-bird/cell/month/clock matching.

No old models or source files are changed. Tests of the matching estimator can
run offline; all provider downloads happen only inside run(). No raw animal
identifiers, destination coordinates, or stratum keys are exported.
"""
from __future__ import annotations
import argparse
import json
import os
import tempfile
from pathlib import Path
import numpy as np
from matched_strata import matched_analysis

BASE_COMMIT = 'f4915fdd083762639ff626368ff43033a83498b9'
TILE_SHA = {
 'schiermonnikoog': [
  'b46913b06d888aa4ffb4336c1cf0ef4654a23863ec8b33c403d63c96e5408184',
  '876c6b81a5a9cc40ab5d8e106e80ac5b5a0b8110bdbf01764fae39ab90af20ac',
  'e6071871081b40657e970d0cd45d74b70f0d09903e99969aaa3ee12901da27e3',
  'c02982d9278f3aabe6756fd6dcbe28b140ad6f6573c1ad3f775429156c6ebe93',
  '67d820a92dad0e49fbf336d74dbb9baca1066c6a6bf900ee5dbda0277aeeebfe',
  'e67496100a4d42e1c55798eda8473fb62f61cd9aa50f03f399a460bd00f4dd1a',
  '11ea2aa58ad8a8a359b3ffb456d415e092ca2fc818e97f8eb0150a734ad3601d',
  '5c88dca2bf88dbddb0f726154243033c8d7b0ecbb0a4237620b3788a67ebe67c'],
 'ameland': [
  'b8e9a96f593247ec8325987559b20b5337733cebb53dee13a8dbce37e61d3088',
  '820f8aeea625f73dc833872cc7ebd06741171e9d65b2018d6e423e24121acb21',
  'ba84e68ecef4c82461fa6141cbec1fa40d316fa6783b5d24354ed5a59cce0c62',
  'e49769e82811fcb1430dfa3ca3b5fca563c8ca4f6781345e5f053a4b341c0c0d',
  '1f95ec25dc5858a51fd7843082ee06d91f13e56e115ddd99791f786ce5ff17c5',
  '30b794514538e75abf931976a6f3b84dd6a0f31d9f0af0cbeff01452eddac469',
  '8f81b8611e458744f288ce9fb715b95b2e246eafe8e272d4fcb13703694dad52',
  '93ca069384bd4a9e7762a034b4cc818d757a41f4db8d37d8eca2654afb007b7f']}
PARTITION = {'schiermonnikoog': [1009,3071,868], 'ameland': [1238,2016,1424]}
PREVIOUS_GAP = {'schiermonnikoog': .0013089744599297376, 'ameland': .16155644228204377}


def verify_source_replay(site, patch_hashes, partition, previous_gap):
    """A missing download is not a source-mask observation."""
    if site not in TILE_SHA:
        raise ValueError('Unfrozen study site')
    if list(patch_hashes) != TILE_SHA[site]:
        raise ValueError('SOURCE_STOP_AHN2_TILE_BYTES_DRIFT_OR_MISSING')
    if list(partition) != PARTITION[site]:
        raise ValueError('SOURCE_STOP_V50_ORIGINAL_PARTITION_DRIFT')
    if not np.isfinite(previous_gap) or abs(previous_gap-PREVIOUS_GAP[site]) > 1e-9:
        raise ValueError('SOURCE_STOP_V50_SAME_BIRD_CONTRAST_NOT_REPLAYED')


def run(site, output):
    # Existing modules are imported, not modified or silently reimplemented.
    import original_heading_skill_by_ahn2_mask as v50
    from source_original_gps_ahn2_overlap import rd_tile_at
    if site not in TILE_SHA:
        raise ValueError('Unfrozen study site')
    station = {'schiermonnikoog':'schiermonnikoog.waddenzee','ameland':'ameland.nes'}[site]
    data, hourly, receipts = {}, {}, {}
    with tempfile.TemporaryDirectory(prefix='v51_original_') as root:
        for year in (2010,2011):
            source = Path(root)/f'{site}_{year}.csv.gz'
            manifest = (v50.download_and_pin(year,source) if site=='schiermonnikoog'
                        else v50.original_gps(year,source))
            md5 = manifest.get('provider_md5_match',manifest.get('provider_original_md5_matched'))
            if md5 is not True:
                raise ValueError('SOURCE_STOP_ORIGINAL_GPS_MD5_NOT_VERIFIED')
            tide, gauge = v50.observed_rws_year(station,year)
            if gauge['gauge_rows'] != 52561:
                raise ValueError('SOURCE_STOP_MEASURED_RWS_SOURCE_COUNT_DRIFT')
            data[year], audit = v50.original_three_fix_heading_episodes(source,tide,site,clock_shift_s=0)
            hourly[year], position_audit = v50.source_hourly(source,site,year)
            receipts[str(year)] = {
                'GPS_provider_MD5_verified':md5,
                'GPS_compressed_SHA256':manifest['original_sha256'],
                'RWS_measured_NAP_count':gauge['gauge_rows'],
                'direction_source_audit':audit,
                'independent_original_GPS_audit':position_audit}
            source.unlink(missing_ok=True)
    e0, e1, full_replay = v50.same_fit_errors(data[2010],data[2011],site)
    selected, ranking = v50.freeze_training_cells(hourly[2010])
    coverage, fmt = v50.original_ahn2_layer()
    if len(selected) != 8:
        raise ValueError('SOURCE_STOP_EIGHT_TRAINING_TILES_NOT_PRESENT')
    tiles, hashes = {}, []
    for i,cell in enumerate(selected):
        print(f'v51 {site}: authentic AHN2 tile {i+1}/8',flush=True)
        # Propagate source failure rather than label it as terrain missingness.
        patch = v50.source_tile(cell,coverage,fmt)
        digest = patch['original_source_patch_SHA256']
        if digest != TILE_SHA[site][i]:
            raise ValueError('SOURCE_STOP_AHN2_TILE_BYTES_DRIFT_OR_MISSING')
        tiles[cell] = patch; hashes.append(digest)
    destinations, original_match = v50.exact_original_C_for_v41_rows(hourly[2011],data[2011])
    labels = [v50.classify_original_C_source(c,selected,tiles) for c in destinations]
    cells = [rd_tile_at(c['lat_C'],c['lon_C'])[0] for c in destinations]
    partition = [labels.count(g) for g in v50.GROUPS]
    prior = v50.within_bird_masked_minus_valid(data[2011],e0,e1,labels)
    gap = prior.get('masked_minus_valid_relative_phase_gain',float('nan'))
    verify_source_replay(site,hashes,partition,gap)
    errors = np.column_stack([e0,e1])
    report = {
        'analysis':'V51_FIXED_MODEL_MATCHED_BIRD_CELL_MONTH_CLOCK',
        'site':site,
        'base_commit':BASE_COMMIT,
        'executed_commit':os.getenv('GITHUB_SHA'),
        'evidence_status':'POST_V50_EXPLORATORY_SAME_HISTORICAL_COHORT',
        'source_original_receipts':receipts,
        'AHN2_all_eight_original_tile_SHA256_replayed':hashes,
        'full_v43_forecast_replay':full_replay,
        'original_C_matching':original_match,
        'source_partition_replay':dict(zip(v50.GROUPS,partition)),
        'prior_v50_same_bird_contrast_replayed':prior,
        'primary_bird_cell_month_clock':matched_analysis(data[2011],errors,labels,cells),
        'secondary_plus_true_phase':matched_analysis(data[2011],errors,labels,cells,phase_conditioned=True),
        'source_GPS_clock':'NATIVE_PROVISIONALLY_UTC_UNVERIFIED',
        'causal_boundary':'AHN2 missingness is not observed water, front, habitat or prey; no social force identified'}
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--site',required=True,choices=tuple(TILE_SHA))
    p.add_argument('--output',required=True)
    args=p.parse_args()
    print(json.dumps(run(args.site,args.output),sort_keys=True))
