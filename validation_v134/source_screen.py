"""Sensitivity expansion of v132 triage, with focal-article identity checks.

This module decides access/identity, not biological eligibility. It deliberately
does not modify the frozen v133 audit or use outcome significance for selection.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from validation_v133.fulltext_audit import BASE, node_text, normalize_doi, retrieve

TITLE_TIDE = re.compile(r'\b(?:tidal|tides?|intertidal|circatidal)\b', re.I)


def select_rescue(corpus: dict) -> list[dict]:
    result = []
    for row in corpus['original_published_bibliography_machine_triage']:
        flags = row.get('source_screen_evidence_flags', {})
        if row.get('automated_relevance_priority') != 'uncertain_relevance':
            continue
        if (flags.get('tide') and flags.get('behavior')) or TITLE_TIDE.search(row.get('title', '')):
            result.append(dict(row))
    return result


def verify_article(raw: bytes, doi=None, pmid=None) -> dict:
    root = ET.fromstring(raw)
    ids = root.findall('./front/article-meta/article-id')
    dois = sorted({normalize_doi(x.text) for x in ids if x.get('pub-id-type') == 'doi'})
    pmids = sorted({str(x.text or '').strip() for x in ids if x.get('pub-id-type') == 'pmid'})
    if doi:
        if normalize_doi(doi) not in dois:
            raise ValueError('FOCAL_ARTICLE_DOI_MISMATCH')
        identity = 'DOI'
    elif pmid:
        if str(pmid).strip() not in pmids:
            raise ValueError('FOCAL_ARTICLE_PMID_MISMATCH')
        identity = 'PMID'
    else:
        raise ValueError('MISSING_EXPECTED_IDENTITY')
    body = root.find('body')
    body_text = node_text(body)
    return {
        'identity_basis': identity,
        'article_dois': dois, 'article_pmids': pmids,
        'article_type': root.get('article-type', 'unknown'),
        'body_element_present': body is not None,
        'body_text_characters': len(body_text),
        'substantive_body_available': bool(body_text),
        'table_count': len(root.findall('.//table-wrap')),
        'original_xml_sha256': hashlib.sha256(raw).hexdigest(),
        'original_xml_bytes': len(raw),
        'fulltext_eligibility_decided': False,
    }


def audit_record(row: dict, cache: Path) -> dict:
    result = {k: row.get(k) for k in ('id', 'doi', 'pmid', 'title', 'year')}
    doi = normalize_doi(row.get('doi'))
    pmid = str(row.get('pmid') or '').strip()
    key = hashlib.sha256(row['id'].encode()).hexdigest()[:20]
    query = f'DOI:"{doi}"' if doi else f'EXT_ID:{pmid} AND SRC:MED'
    url = BASE + 'search?' + urlencode({'query': query, 'format': 'json', 'resultType': 'core', 'pageSize': 20})
    result['metadata_url'] = url
    try:
        raw = retrieve(url, cache / f'{key}_metadata.json')
        metadata = json.loads(raw)
        records = metadata.get('resultList', {}).get('result', [])
        if doi:
            exact = [r for r in records if normalize_doi(r.get('doi')) == doi]
        else:
            exact = [r for r in records if str(r.get('pmid', r.get('id', ''))) == pmid and r.get('source') == 'MED']
        result['metadata_sha256'] = hashlib.sha256(raw).hexdigest()
        if not exact:
            result['status'] = 'NO_EXACT_ARTICLE_METADATA_MATCH'
            return result
        rec = sorted(exact, key=lambda r: bool(r.get('pmcid')), reverse=True)[0]
        result.update({'resolved_pmid': rec.get('pmid'), 'resolved_pmcid': rec.get('pmcid'),
                       'resolved_title': rec.get('title'), 'metadata_exact_match_records': len(exact)})
        if not rec.get('pmcid'):
            result['status'] = 'METADATA_VERIFIED_NO_PMC_XML_ID'
            return result
        xml_url = BASE + rec['pmcid'] + '/fullTextXML'
        result['fulltext_url'] = xml_url
        xml = retrieve(xml_url, cache / f'{rec["pmcid"]}.xml')
        result.update(verify_article(xml, doi=doi, pmid=pmid))
        result['status'] = ('ORIGINAL_XML_IDENTITY_AND_BODY_VERIFIED' if result['substantive_body_available']
                            else 'ORIGINAL_XML_VERIFIED_BODY_UNAVAILABLE')
    except HTTPError as error:
        result.update(status='SOURCE_HTTP_ERROR', http_status=error.code)
    except (ValueError, ET.ParseError) as error:
        result.update(status='SOURCE_PARSE_OR_IDENTITY_FAILURE', error=str(error)[:200])
    except Exception as error:
        result.update(status='SOURCE_TRANSPORT_FAILURE', error_type=type(error).__name__, error=str(error)[:200])
    return result


def run(corpus_path: str, cache_path: str, output: str, workers=4) -> dict:
    raw = Path(corpus_path).read_bytes()
    corpus = json.loads(raw)
    selected = select_rescue(corpus)
    cache = Path(cache_path)
    cache.mkdir(parents=True, exist_ok=True)
    records = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(audit_record, row, cache) for row in selected]
        for future in as_completed(futures):
            records.append(future.result())
            if len(records) % 10 == 0 or len(records) == len(selected):
                print('RESCUE_SOURCE_AUDIT', len(records), '/', len(selected), flush=True)
    records.sort(key=lambda r: r['id'])
    result = {
        'version': 'v134-uncertain-rescue-access-1',
        'retrieved_utc': datetime.now(timezone.utc).isoformat(),
        'input_corpus_sha256': hashlib.sha256(raw).hexdigest(),
        'selection_rule': 'uncertain_relevance AND ((original tide flag AND original behavior flag) OR tidal/tide/tides/intertidal/circatidal title word)',
        'selection_uses_results_or_access': False,
        'selected_candidates': len(selected),
        'selected_years': dict(sorted(Counter(str(r['year']) for r in selected).items())),
        'access_status_counts': dict(Counter(r['status'] for r in records)),
        'access_is_not_eligibility': True,
        'records': records,
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
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
