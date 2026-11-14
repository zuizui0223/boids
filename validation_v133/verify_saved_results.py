"""Validate saved source accounting and optionally replay the pinned original DOCX.

This verifies the extraction artifact, not the underlying studies' model validity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import contextlib
import io
import json
from math import isclose
from pathlib import Path
import tempfile

from effect_extraction import run as extract

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def read(path):
    return json.loads(Path(path).read_text())


def compare(saved, replayed, location='root'):
    """Compare all provenance fields; tolerate only floating-point roundoff."""
    if isinstance(saved, dict):
        assert isinstance(replayed, dict) and saved.keys() == replayed.keys(), location
        for key in saved:
            compare(saved[key], replayed[key], location + '.' + key)
    elif isinstance(saved, list):
        assert isinstance(replayed, list) and len(saved) == len(replayed), location
        for index, (a, b) in enumerate(zip(saved, replayed)):
            compare(a, b, location + f'[{index}]')
    elif isinstance(saved, (int, float)) and not isinstance(saved, bool):
        assert isinstance(replayed, (int, float)) and not isinstance(replayed, bool), location
        assert isclose(saved, replayed, rel_tol=1e-12, abs_tol=1e-14), location
    else:
        assert type(saved) is type(replayed) and saved == replayed, location


def verify(source_docx=None):
    audit = read(ROOT / 'results/fulltext_access_audit.json')
    records = audit['records']
    assert len(records) == len({r['id'] for r in records}) == 150
    assert audit['selected_field_metadata_candidates'] == len(records)
    assert Counter(r['status'] for r in records) == audit['access_status_counts']
    assert Counter(r['automated_relevance_priority'] for r in records) == {
        'possible_field_tide_solar': 93, 'possible_field_tide_only': 57}
    assert audit['input_metadata_candidates'] == 1061
    assert audit['uncertain_and_other_candidates_not_screened'] == 911
    successful = [r for r in records if r['status'] == 'ORIGINAL_XML_RETRIEVED_DOI_VERIFIED']
    assert len(successful) == 86
    assert Counter(r['article_type'] for r in successful) == audit['retrieved_article_types']
    for row in successful:
        assert row['doi'].lower() in row['verified_article_dois']
        assert len(row['original_xml_sha256']) == 64
        assert row['original_xml_bytes'] > 0
        assert row['fulltext_eligibility_decided'] is False
        assert row['effect_extracted_automatically'] is False
    locators = [loc for row in successful for loc in row['supplement_locators']]
    assert len(locators) == audit['supplement_locators_total'] == 228
    assert sum(bool(loc['all_hrefs']) for loc in locators) == audit['supplement_locators_with_original_file_href'] == 228
    assert all('caption' not in loc for row in successful
               for loc in row['tidal_table_locators'] + row['supplement_locators'])

    ledger = read(ROOT / 'published_spoonbill_effect_ledger.json')
    effects = ledger['effects']
    assert len(effects) == len({r['effect_id'] for r in effects}) == 174
    assert {r['study_id'] for r in effects} == {'RODRIGUES_2025_SPOONBILL'}
    assert sum(r['behavior'] == 'feeding' for r in effects) == 60
    assert sum(r['label_ambiguous'] for r in effects) == 28
    result = read(ROOT / 'results/spoonbill_tide_diel_contrasts.json')
    interaction = result['ria_low_vs_high_diel_interaction']
    assert isclose(interaction['estimate'], -1.12)
    assert interaction['sampling_se'] is None
    assert interaction['eligible_for_inverse_variance_weight'] is False
    assert result['tagus_interaction']['estimate'] is None
    assert result['feeding_row_poolability']['admitted'] is False
    assert result['no_raw_behavioral_fit_performed'] is True

    capuchin = read(ROOT / 'results/capuchin_original_source_audit.json')
    assert capuchin['original_sequence_rows'] == 22185 and capuchin['zero_count_rows'] == 0
    assert capuchin['all_rows_conditioned_on_detection'] is True
    assert capuchin['can_estimate_unconditional_activity_rate_from_this_csv'] is False
    assert capuchin['raw_behavioral_effect_fit_performed'] is False

    index = read(ROOT / 'source_evidence_index.json')
    studies = index['studies']
    assert len(studies) == len({s['doi'].lower() for s in studies}) == 17
    assert Counter(s['quantitative_evidence']['category'] for s in studies) == index['summary']['category_counts']
    assert sum(s['quantitative_evidence']['common_tide_by_diel_pool_ready'] for s in studies) == 0
    pointer_count = 0
    for study in studies:
        for loc in study['ledger_locations']:
            value = read(REPO / loc['path'])
            for key in loc['json_pointer'].split('/')[1:]:
                key = key.replace('~1', '/').replace('~0', '~')
                value = value[int(key)] if isinstance(value, list) else value[key]
            assert value is not None
            pointer_count += 1
    assert all(x['global_meta_pooled_effect'] == 'NOT_ESTIMATED' for x in (audit, result, index))

    if source_docx:
        with tempfile.TemporaryDirectory(prefix='v133-original-replay-') as output:
            with contextlib.redirect_stdout(io.StringIO()):
                extract(source_docx, output)
            for name in ('published_spoonbill_effect_ledger.json', 'results/spoonbill_tide_diel_contrasts.json'):
                compare(read(ROOT / name), read(Path(output) / name), name)

    return {'status': 'VERIFIED', 'original_docx_replayed': bool(source_docx),
            'selected_access_records': len(records), 'doi_verified_xml': len(successful),
            'original_supplement_locators': len(locators), 'source_studies_indexed': len(studies),
            'resolved_ledger_pointers': pointer_count, 'dependent_spoonbill_contrasts': len(effects),
            'global_meta_pooled_effect': 'NOT_ESTIMATED', 'new_raw_behavioral_model': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-docx')
    args = parser.parse_args()
    print(json.dumps(verify(args.source_docx), sort_keys=True))
