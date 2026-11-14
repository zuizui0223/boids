"""Replay v134 published effects from seven original article XML files.

Uses only the standard library. By default the supplied caches are read-only.
``--download`` requires empty (or absent) cache directories and retrieves only
the seven official Europe PMC fullTextXML URLs. No raw animal data are fetched.

The adjacent published_effect_verification.json is the immutable reference for
saved source hashes. A changed hash is disclosed, not explained speculatively:
the fixed identity, table-value and animal-unit assertions must still pass.
This is a source-extraction replay, not a model refit or pooling authorization.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
import xml.etree.ElementTree as ET


REFERENCE = Path(__file__).with_name('published_effect_verification.json')
BASE_URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
MAX_XML_BYTES = 10 * 1024 * 1024
SOURCES = {
    'gull': ('fulltext', 'PMC6106178', '10.1002/ece3.4167'),
    'lemon': ('fulltext', 'PMC5842499', '10.1007/s00227-018-3318-y'),
    'sevengill': ('fulltext', 'PMC10565395', '10.1098/rsos.230667'),
    'helgoland_oyster': ('fulltext', 'PMC13408198', '10.1038/s41598-026-63105-x'),
    'plovers': ('fulltext', 'PMC10668691', '10.3390/ani13223548'),
    'bream': ('rescue', 'PMC3832432', '10.1371/journal.pone.0080962'),
    'arcachon_oyster': ('fulltext', 'PMC5636115', '10.1371/journal.pone.0185918'),
}


class VerificationError(ValueError):
    """Source evidence does not support a required replay assertion."""


def require(condition: bool, message: str) -> None:
    # Explicit checks also run under python -O, unlike bare assert statements.
    if not condition:
        raise VerificationError(message)


def plain(element: ET.Element) -> str:
    return ' '.join(' '.join(element.itertext()).split())


def article_identity(raw: bytes, pmcid: str, doi: str) -> tuple[ET.Element, dict]:
    root = ET.fromstring(raw)
    require(root.tag == 'article', 'NOT_A_FOCAL_ARTICLE_XML')
    ids = root.findall('./front/article-meta/article-id')
    dois = sorted({(x.text or '').strip().lower() for x in ids
                   if x.get('pub-id-type') == 'doi'})
    require(doi.lower() in dois, f'FOCAL_DOI_MISMATCH: expected {doi}; found {dois}')
    pmcids = sorted({(x.text or '').strip().upper() for x in ids
                     if x.get('pub-id-type') in ('pmc', 'pmcid')})
    pmcids = [x if x.startswith('PMC') else 'PMC' + x for x in pmcids]
    require(pmcid in pmcids, f'FOCAL_PMCID_MISMATCH: expected {pmcid}; found {pmcids}')
    body = root.find('body')
    body_text = plain(body) if body is not None else ''
    require(bool(body_text), 'EMPTY_OR_MISSING_BODY')
    return root, {'focal_doi_verified': True, 'focal_pmcid_verified': True,
                  'focal_article_dois': dois, 'body_text_characters': len(body_text)}


class OfficialRedirectOnly(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        destination = urlparse(newurl)
        require(destination.scheme == 'https' and
                destination.hostname in ('www.ebi.ac.uk', 'ebi.ac.uk'),
                'NON_OFFICIAL_REDIRECT_REJECTED')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_xml(url: str) -> bytes:
    request = Request(url, headers={
        'Accept': 'application/xml',
        'User-Agent': 'Boids-v134-published-source-verification/1.0',
    })
    with build_opener(OfficialRedirectOnly()).open(request, timeout=45) as response:
        raw = response.read(MAX_XML_BYTES + 1)
    require(len(raw) <= MAX_XML_BYTES, 'ARTICLE_XML_EXCEEDS_10_MIB_LIMIT')
    return raw


def table_rows(root: ET.Element, table_id: str) -> list[list[str]]:
    body = root.find('body')
    tables = [t for t in body.iter('table-wrap') if t.get('id') == table_id]
    require(len(tables) == 1, f'TABLE_MISSING_OR_DUPLICATED: {table_id}')
    return [[plain(cell) for cell in row] for row in tables[0].iter('tr')]


def unique_row(root: ET.Element, table_id: str, label: str) -> list[str]:
    matches = [r for r in table_rows(root, table_id) if r and r[0] == label]
    require(len(matches) == 1, f'ROW_MISSING_OR_DUPLICATED: {table_id}: {label}')
    return matches[0]


def verify_numbers(trees: dict[str, ET.Element], receipt: dict) -> None:
    def check(key, table_id, label, expected, positions=(1, 2), row=None):
        cells = row if row is not None else unique_row(trees[key], table_id, label)
        require(len(cells) > max(positions), f'INCOMPLETE_ROW: {key}: {label}')
        actual = [float(cells[p].replace('−', '-').replace(' ', '')) for p in positions]
        require(all(math.isfinite(x) for x in actual) and actual == list(expected),
                f'COEFFICIENT_SE_MISMATCH: {key}: {label}: {actual} != {list(expected)}')
        receipt['coefficient_checks'].append({
            'source': key, 'table_id': table_id, 'label': label,
            'estimate': actual[0], 'reported_se': actual[1],
            'original_row_cells': cells, 'passed': True,
        })

    check('gull', 'ece34167-tbl-0003', 'Water level', (-0.40, 0.04))
    check('gull', 'ece34167-tbl-0003', 'Night', (0.59, 0.08))
    for label, pair in [('Flood', (0.012, 0.132)), ('High', (-0.600, 0.149)),
                        ('Low', (0.028, 0.144))]:
        check('lemon', 'Tab8', label, pair)
    for label, pair in [('Tide_height intermediate', (-0.074, 0.034)),
                        ('Tide_height low', (-0.149, 0.041)),
                        ('Sexmale:Tide_height intermediate', (-0.523, 0.051)),
                        ('Sexmale:Tide_height low', (-1.042, 0.062))]:
        check('sevengill', 'RSOS230667TB2', label, pair)
    oyster_row = unique_row(trees['helgoland_oyster'], 'Tab1', 'Water level')
    check('helgoland_oyster', 'Tab1', 'VOA Water level', (3.26, 0.72), row=oyster_row)
    check('helgoland_oyster', 'Tab1', 'VOD Water level', (-4.47, 1.10),
          positions=(6, 7), row=oyster_row)

    # Associate species/habitat with the following tide row. Never zip an
    # unchecked partial row set to expected effects or silently swap species.
    plover_expected = {
        'animals-13-03548-t001': {
            'Piping Plover, mudflat': (-0.40, 0.15),
            'Piping Plover, beach': (0.89, 0.06),
            'Snowy Plover, mudflat': (-0.45, 0.07),
            'Snowy Plover, beach': (0.17, 0.07),
            'Wilson’s Plover, mudflat': (-0.11, 0.03),
            'Wilson’s Plover, beach': (0.71, 0.05),
        },
        'animals-13-03548-t002': {
            'Piping Plover, mudflat': (-0.01, 0.08),
            'Snowy Plover, mudflat': (-0.17, 0.10),
        },
    }
    for table_id, expected in plover_expected.items():
        current_species, found = '', set()
        for cells in table_rows(trees['plovers'], table_id):
            if len(cells) > 1 and cells[1] == 'Intercept':
                current_species = cells[0]
            if cells and cells[0] == 'Tide':
                require(current_species in expected and current_species not in found,
                        f'UNEXPECTED_PLOVER_TIDE_ROW: {table_id}: {current_species}')
                check('plovers', table_id, current_species + ' Tide',
                      expected[current_species], row=cells)
                found.add(current_species)
        require(found == set(expected), f'MISSING_PLOVER_TIDE_ROWS: {table_id}')
    for label, pair in [('Diel period', (0.1651113, 0.019)),
                        ('Tidal period', (0.1785145, 0.035)),
                        ('Depth', (-0.0972872, 0.029)),
                        ('Diel·Tide', (0.1120134, 0.039))]:
        check('bream', 'pone-0080962-t004', label, pair)
    require(len(receipt['coefficient_checks']) == 23, 'EXPECTED_23_COEFFICIENT_SE_PAIRS')

    lemon_tags = [r[0].split()[0] for r in table_rows(trees['lemon'], 'Tab2')
                  if len(r) == 6 and r[1] in ('Wet', 'Dry')]
    tag_counts = Counter(lemon_tags)
    repeated = sorted(k for k, n in tag_counts.items() if n > 1)
    require(len(lemon_tags) == 20 and len(tag_counts) == 18 and
            repeated == ['4A0A043D40', '4A63380105'] and
            all(n in (1, 2) for n in tag_counts.values()), 'LEMON_ANIMAL_UNIT_MISMATCH')
    receipt['unit_checks']['lemon'] = {
        'deployments': len(lemon_tags), 'distinct_pit_tag_ids': len(tag_counts),
        'repeated_ids': repeated,
    }
    bream_rows = [r for r in table_rows(trees['bream'], 'pone-0080962-t001')
                  if len(r) == 7 and r[0].isdigit()]
    require([r[0] for r in bream_rows] == ['1', '2', '3', '4', '5', '6'],
            'BREAM_ANIMAL_UNIT_MISMATCH')
    activity_n, depth_n = [int(r[5]) for r in bream_rows], [int(r[6]) for r in bream_rows]
    require(activity_n == [11669, 7074, 17247, 196, 408, 476] and
            depth_n == [11785, 6981, 17202, 203, 423, 472], 'BREAM_RECORD_COUNTS_MISMATCH')
    receipt['unit_checks']['bream'] = {
        'fish': len(bream_rows), 'activity_records': sum(activity_n),
        'depth_records': sum(depth_n),
        'first_three_fish_share_activity_records': sum(activity_n[:3]) / sum(activity_n),
    }
    receipt['arithmetic_only_not_fitted_effects'] = {
        'lemon_high_minus_low_point': -0.600 - 0.028, 'lemon_high_minus_low_se': None,
        'sevengill_male_low_minus_high_point': -0.149 - 1.042,
        'sevengill_male_low_minus_high_se': None,
        'reason_se_null': 'No within-fit covariance matrices reported in focal XML.',
    }


def run(fulltext_cache: str, rescue_cache: str, output: str, download: bool = False) -> dict:
    caches = {'fulltext': Path(fulltext_cache).resolve(), 'rescue': Path(rescue_cache).resolve()}
    target = Path(output).resolve()
    source_paths = {key: caches[which] / (pmcid + '.xml')
                    for key, (which, pmcid, _) in SOURCES.items()}
    require(target != REFERENCE.resolve() and
            target not in {path.resolve() for path in source_paths.values()},
            'OUTPUT_MUST_NOT_OVERWRITE_REFERENCE_OR_SOURCE')
    receipt = {
        'version': 'v134-original-published-source-replay-1',
        'verified_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'six effect papers plus Arcachon classification',
        'no_new_fit': True, 'no_downloads': not download, 'raw_animal_data_downloaded': False,
        'sources': {}, 'coefficient_checks': [], 'unit_checks': {},
        'all_numeric_checks_passed': False, 'source_hash_drift': [],
        'source_hash_policy': (
            'Every actual XML SHA256 is compared with the saved source receipt. '
            'A mismatch is reported as byte drift; its cause is not inferred. '
            'Success with drift verifies only the fixed focal identities, body '
            'availability, table values and animal-unit checks, not all article bytes.'),
    }
    try:
        reference_raw = REFERENCE.read_bytes()
        reference = json.loads(reference_raw)
        receipt['saved_reference_path'] = str(REFERENCE.resolve())
        receipt['saved_reference_sha256'] = hashlib.sha256(reference_raw).hexdigest()
        require(set(reference['sources']) == set(SOURCES), 'SAVED_SOURCE_SET_MISMATCH')
        if download:
            for cache in set(caches.values()):
                require(not cache.exists() or (cache.is_dir() and not any(cache.iterdir())),
                        f'DOWNLOAD_REQUIRES_EMPTY_CACHE: {cache}')
            for cache in set(caches.values()):
                cache.mkdir(parents=True, exist_ok=True)
        trees = {}
        for key, (_, pmcid, doi) in SOURCES.items():
            saved = reference['sources'][key]
            require(saved['doi'] == doi and saved['pmcid'] == pmcid,
                    f'SAVED_RECEIPT_IDENTITY_MISMATCH: {key}')
            url = BASE_URL + pmcid + '/fullTextXML'
            path = source_paths[key]
            raw = download_xml(url) if download else path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            source = {'doi': doi, 'pmcid': pmcid, 'path': str(path), 'url': url,
                      'bytes': len(raw), 'sha256': digest, 'saved_sha256': saved['sha256'],
                      'sha256_matches_saved': digest == saved['sha256'],
                      'downloaded_this_run': download, 'focal_doi_verified': False}
            receipt['sources'][key] = source
            if not source['sha256_matches_saved']:
                receipt['source_hash_drift'].append(key)
                source['byte_drift_note'] = (
                    'XML bytes differ from the frozen snapshot. Cause not determined; '
                    'this run separately checks focal identity and prespecified evidence.')
            trees[key], identity = article_identity(raw, pmcid, doi)
            source.update(identity)
            if download:
                # Save only verified focal full text, and never overwrite a file.
                with path.open('xb') as handle:
                    handle.write(raw)
        verify_numbers(trees, receipt)
        receipt['all_numeric_checks_passed'] = True
        receipt['status'] = ('VERIFIED_WITH_SOURCE_BYTE_DRIFT' if receipt['source_hash_drift']
                             else 'VERIFIED_AGAINST_ORIGINAL_XML')
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        receipt['status'] = 'FAILED_ORIGINAL_SOURCE_REPLAY'
        receipt['error_type'] = type(error).__name__
        receipt['error'] = str(error)
    receipt['n_coefficient_se_pairs_checked'] = len(receipt['coefficient_checks'])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    return receipt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fulltext-cache', required=True,
                        help='Directory holding the six v133 PMC*.xml sources.')
    parser.add_argument('--rescue-cache', required=True,
                        help='Directory holding the yellowfin-bream rescue XML.')
    parser.add_argument('--output', required=True, help='Write a new replay receipt JSON here.')
    parser.add_argument('--download', action='store_true',
                        help='Fetch the seven official XMLs into empty/absent supplied caches.')
    args = parser.parse_args(argv)
    try:
        receipt = run(args.fulltext_cache, args.rescue_cache, args.output, args.download)
    except (OSError, VerificationError) as error:
        print(str(error), file=sys.stderr)
        return 1
    summary = {key: receipt[key] for key in
               ('status', 'n_coefficient_se_pairs_checked', 'source_hash_drift')}
    summary.update(source_articles=len(receipt['sources']), output=str(Path(args.output).resolve()))
    print(json.dumps(summary), flush=True)
    if not receipt['all_numeric_checks_passed']:
        print(receipt.get('error', 'Source replay failed.'), file=sys.stderr)
        return 1
    if receipt['source_hash_drift']:
        print('Source bytes changed; inspect source_hash_drift and per-source hashes in the receipt.',
              file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
