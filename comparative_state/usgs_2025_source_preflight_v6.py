"""Source-only original USGS repeated-wetland survey preflight (2026-11-15).

Fetches provider ScienceBase JSON. Does NOT download or open bird or habitat responses.
Never reinterprets a metadata failure as a biological null.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

SOURCE_DOI = "10.5066/P13UJQP5"
ITEM_ID = "67c8bbcdd34ea599a3b9ae77"
EXPECTED_TITLE_KEYS = ("Habitat Features", "Waterbird", "California Waterfowl Habitat Program")
ITEM_URL = f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
MAX_META_BYTES = 3_000_000


def validate_provider_manifest(record: dict) -> dict:
    if str(record.get('id', '')) != ITEM_ID:
        return {'status': 'SOURCE_STOP_BAD_ITEM_ID', 'item_id': record.get('id')}
    title = str(record.get('title',''))
    if not all(k.lower() in title.lower() for k in EXPECTED_TITLE_KEYS):
        return {'status': 'SOURCE_STOP_UNEXPECTED_TITLE', 'title': title}
    files = record.get('files')
    if not isinstance(files, list) or not files:
        return {'status': 'SOURCE_STOP_NO_ORIGINAL_FILE_LIST', 'title': title}
    inventory = []
    for f in files:
        if not isinstance(f, dict):
            continue
        name = str(f.get('name', ''))
        url = f.get('downloadUri') or f.get('url')
        if url and (not str(url).startswith('https://') or not any(k in str(url).lower() for k in ('sciencebase.gov','usgs.gov'))):
            url = None
        inventory.append({
            'name': name,
            'size': f.get('size'),
            'downloadUri': url,
            'checksum': f.get('md5') or f.get('checksum'),
            'contentType': f.get('contentType'),
            'metadata_only': True,
        })
    is_data = lambda x: x['name'].lower().endswith(('.csv', '.xlsx', '.xls', '.zip', '.txt', '.tsv'))
    qualified = [f for f in inventory if is_data(f)]
    return {
        'status': 'SOURCE_FILE_INVENTORY_ADMITTED' if qualified else 'SOURCE_STOP_NO_TABULAR_SOURCE',
        'title': title,
        'total_provider_files': len(files),
        'plausible_original_data_files': qualified,
        'other_file_names': [f['name'] for f in inventory if f not in qualified],
        'original_numeric_outcomes_opened': False,
        'original_file_bytes_downloaded': False,
    }


def read_source():
    req = urllib.request.Request(ITEM_URL, headers={
        'User-Agent': 'ecostate-research/6.0 (original-source-only; no scraping)',
        'Accept': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=45) as r:
        if r.headers.get('Content-Length') and int(r.headers['Content-Length']) > MAX_META_BYTES:
            raise ValueError('provider item metadata too large')
        body = r.read(MAX_META_BYTES + 1)
    if len(body) > MAX_META_BYTES:
        raise ValueError('provider item metadata exceeds cap')
    return json.loads(body.decode('utf-8-sig'))


def run(out: Path):
    receipt = {
        'schema': 'ecostate.usgs_california_waterbird_source_v6',
        'source_doi': SOURCE_DOI,
        'item_id': ITEM_ID,
        'metadata_url': ITEM_URL,
        'status': 'SOURCE_STOP',
        'original_numeric_outcomes_opened': False,
        'original_file_bytes_downloaded': False,
        'purpose': 'Assess independent waterbird assemblage states at contemporaneously measured wetland surveys; not animal movement',
        'biological_replication_unit_unverified': 'wetland unit before source file headers are audited',
    }
    try:
        receipt.update(validate_provider_manifest(read_source()))
    except Exception as e:
        receipt['status'] = 'SOURCE_STOP_PROVIDER_METADATA_UNAVAILABLE'
        receipt['provider_error_type'] = type(e).__name__
        receipt['provider_error_message'] = str(e)[:300]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print('USGS_WETLAND_ORIGINAL_SOURCE_V6', receipt['status'], 'files', len(receipt.get('plausible_original_data_files',[])))
    return receipt


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=Path('comparative_state/results/usgs_waterbird_source_v6.json'))
    args=ap.parse_args()
    run(args.out)
