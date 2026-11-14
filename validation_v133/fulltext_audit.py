"""Original-source access audit; access is never study inclusion or an effect."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

FIELD_PRIORITIES = {'possible_field_tide_solar', 'possible_field_tide_only'}
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
TIDE = re.compile(r'\b(?:tidal|tide|tides|ebb|circatidal)\b', re.I)
DIEL = re.compile(r'\b(?:diel|circadian|diurnal|nocturnal|daylight|photoperiod|solar)\b|day.?night', re.I)
REPOSITORY = re.compile(r'zenodo|dryad|figshare|movebank|osf\.io|github\.com|pangaea|bco-dmo|imos|aed\.|data\.', re.I)


def normalize_doi(value):
    value = str(value or '').strip().lower()
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value)


def select_candidates(corpus):
    return [dict(r) for r in corpus['original_published_bibliography_machine_triage']
            if r['automated_relevance_priority'] in FIELD_PRIORITIES]


def node_text(node):
    return ' '.join(' '.join(node.itertext()).split()) if node is not None else ''


def summarize_xml(raw, expected_doi):
    root = ET.fromstring(raw)
    article_ids = {normalize_doi(x.text) for x in root.findall('./front/article-meta/article-id')
                   if x.get('pub-id-type') == 'doi'}
    if normalize_doi(expected_doi) not in article_ids:
        raise ValueError('ORIGINAL_XML_ARTICLE_DOI_MISMATCH')
    body = root.find('body')
    body_text = node_text(body)
    tables = []
    for table in root.findall('.//table-wrap'):
        table_text = node_text(table)
        if TIDE.search(table_text):
            tables.append({'id': table.get('id'), 'label': node_text(table.find('label')),
                           'mentions_uncertainty': bool(re.search(r'\b(?:SE|SD|CI)\b|confidence|standard error', table_text, re.I))})
    # Only the focal article's narrative/supplement links; cited papers are not
    # evidence that the focal study deposited original data.
    parents = {c: p for p in root.iter() for c in p}
    links = set()
    supplements = []
    for el in root.iter():
        p = el
        in_references = False
        while p in parents:
            p = parents[p]
            if p.tag in ('ref-list', 'ref'):
                in_references = True
        if in_references:
            continue
        href = el.get('{http://www.w3.org/1999/xlink}href')
        if href and href.startswith(('http://', 'https://')) and REPOSITORY.search(href):
            links.add(href)
        if el.tag == 'supplementary-material':
            hrefs = sorted({child.get('{http://www.w3.org/1999/xlink}href')
                            for child in el.iter()
                            if child.get('{http://www.w3.org/1999/xlink}href')})
            supplements.append({'id': el.get('id'), 'href': hrefs[0] if hrefs else None,
                                'all_hrefs': hrefs,
                                'hrefs_may_be_source_relative': True,
                                'label': node_text(el.find('label'))})
    return {
        'article_type': root.get('article-type', 'unknown'),
        'verified_article_dois': sorted(article_ids),
        'original_title': node_text(root.find('./front/article-meta/title-group/article-title')),
        'original_xml_sha256': hashlib.sha256(raw).hexdigest(),
        'original_xml_bytes': len(raw),
        'body_mentions_tide': bool(TIDE.search(body_text)),
        'body_mentions_diel': bool(DIEL.search(body_text) or
                                   (re.search(r'\bday\b', body_text, re.I) and re.search(r'\bnight\b', body_text, re.I))),
        'table_count': len(root.findall('.//table-wrap')),
        'tidal_table_locators': tables,
        'primary_repository_links': sorted(links),
        'supplement_locators': supplements,
        'fulltext_eligibility_decided': False,
        'effect_extracted_automatically': False,
    }


def retrieve(url, path):
    path = Path(path)
    if path.exists():
        return path.read_bytes()
    for attempt in range(2):
        try:
            req = Request(url, headers={'User-Agent': 'Boids-public-literature-source-audit/133'})
            with urlopen(req, timeout=35) as response:
                raw = response.read()
            path.write_bytes(raw)
            return raw
        except HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt:
                raise
            time.sleep(1)


def audit_row(row, cache):
    result = {k: row.get(k) for k in ('id', 'doi', 'pmid', 'title', 'year', 'automated_relevance_priority')}
    doi = normalize_doi(row.get('doi'))
    key = hashlib.sha256(row['id'].encode()).hexdigest()[:20]
    query = f'DOI:"{doi}"' if doi else f'EXT_ID:{row["pmid"]} AND SRC:MED'
    url = BASE + 'search?' + urlencode({'query': query, 'format': 'json', 'resultType': 'core', 'pageSize': 20})
    result['metadata_url'] = url
    try:
        raw = retrieve(url, cache / f'{key}_metadata.json')
        metadata = json.loads(raw)
        records = metadata.get('resultList', {}).get('result', [])
        exact = [r for r in records if normalize_doi(r.get('doi')) == doi] if doi else []
        result['metadata_sha256'] = hashlib.sha256(raw).hexdigest()
        if not exact:
            result['status'] = 'NO_EXACT_DOI_METADATA_MATCH'
            return result
        # Prefer a record with full text without erasing the other records.
        rec = sorted(exact, key=lambda r: bool(r.get('pmcid')), reverse=True)[0]
        result.update({'resolved_pmid': rec.get('pmid'), 'resolved_pmcid': rec.get('pmcid'),
                       'resolved_title': rec.get('title'), 'source_is_open_access': rec.get('isOpenAccess'),
                       'metadata_exact_match_records': len(exact)})
        if not rec.get('pmcid'):
            result['status'] = 'METADATA_VERIFIED_NO_PMC_XML_ID'
            return result
        xml_url = BASE + rec['pmcid'] + '/fullTextXML'
        result['fulltext_url'] = xml_url
        xml = retrieve(xml_url, cache / f'{rec["pmcid"]}.xml')
        result['original_xml_sha256'] = hashlib.sha256(xml).hexdigest()
        result['original_xml_bytes'] = len(xml)
        result.update(summarize_xml(xml, doi))
        result['status'] = 'ORIGINAL_XML_RETRIEVED_DOI_VERIFIED'
    except HTTPError as e:
        result['status'] = 'SOURCE_HTTP_ERROR'
        result['http_status'] = e.code
    except (ValueError, ET.ParseError) as e:
        result['status'] = 'SOURCE_PARSE_OR_DOI_VALIDATION_FAILURE'
        result['error_type'] = type(e).__name__
        result['error'] = str(e)[:160]
        if str(e) == 'ORIGINAL_XML_ARTICLE_DOI_MISMATCH':
            result['mismatch_expected_doi'] = doi
            result['mismatch_observed_xml_dois'] = [x.text for x in ET.fromstring(xml).findall('./front/article-meta/article-id')
                                                  if x.get('pub-id-type') == 'doi']
            result['mismatch_disposition'] = 'Retained as unavailable for exact-DOI evidence; publisher identifier discrepancy not silently corrected.'
    except Exception as e:
        result['status'] = 'SOURCE_TRANSPORT_FAILURE'
        result['error_type'] = type(e).__name__
        result['error'] = str(e)[:160]
    return result


def run(corpus_path, cache, output, workers=4):
    data = Path(corpus_path).read_bytes()
    corpus = json.loads(data)
    rows = select_candidates(corpus)
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending = [executor.submit(audit_row, row, cache) for row in rows]
        for f in as_completed(pending):
            results.append(f.result())
            if len(results) % 20 == 0 or len(results) == len(rows):
                print('FULLTEXT_SOURCE_AUDIT', len(results), '/', len(rows), dict(Counter(r['status'] for r in results)), flush=True)
    results.sort(key=lambda r: r['id'])
    success = [r for r in results if r['status'] == 'ORIGINAL_XML_RETRIEVED_DOI_VERIFIED']
    supplement_locators = [loc for r in success for loc in r['supplement_locators']]
    result = {
        'version': 'v133-fulltext-source-access-1',
        'retrieved_utc': datetime.now(timezone.utc).isoformat(),
        'parent_branch_sha': '0eeb9113764df4903f0cf1bf7153e7d40e8934c4',
        'parent_artifact_id': 14110556853,
        'parent_artifact_zip_sha256': 'f89d423ec0f242e7b9038794a1d430d4c8232fca415d136fd7f696b669507963',
        'input_corpus_sha256': hashlib.sha256(data).hexdigest(),
        'input_metadata_candidates': len(corpus['original_published_bibliography_machine_triage']),
        'selected_field_metadata_candidates': len(rows),
        'selected_by_old_priority': dict(Counter(r['automated_relevance_priority'] for r in rows)),
        'access_status_counts': dict(Counter(r['status'] for r in results)),
        'retrieved_article_types': dict(Counter(r['article_type'] for r in success)),
        'retrieved_with_tidal_table_locators': sum(bool(r['tidal_table_locators']) for r in success),
        'retrieved_with_repository_links': sum(bool(r['primary_repository_links']) for r in success),
        'supplement_locators_total': len(supplement_locators),
        'supplement_locators_with_original_file_href': sum(bool(loc['all_hrefs']) for loc in supplement_locators),
        'fulltext_access_is_not_fulltext_eligibility': True,
        'uncertain_and_other_candidates_not_screened': len(corpus['original_published_bibliography_machine_triage']) - len(rows),
        'global_meta_pooled_effect': 'NOT_ESTIMATED',
        'records': results,
    }
    p = Path(output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}, ensure_ascii=False), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', required=True)
    parser.add_argument('--cache', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    run(args.corpus, args.cache, args.output, args.workers)
