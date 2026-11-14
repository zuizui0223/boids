"""Reconcile source-screen ledgers without converting records into studies."""
from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path


def normalize_record(row, ledger, index, origin, old_dois):
    is_a = 'decision' in row
    source = row.get('source', row.get('original_source', {}))
    doi = str(row.get('doi') or '').lower()
    if not doi:
        raise ValueError('MISSING_FOCAL_DOI_IN_RETRIEVED_LEDGER')
    decision = row.get('decision', row.get('screening_decision'))
    if not decision:
        raise ValueError('MISSING_SUBSTANTIVE_SCREEN_DECISION')
    pointer = f'/{index}' if is_a else f'/records/{index}'
    basis = row.get('screen_method', row.get('screening_basis', ''))
    read_body = row.get('focal_fulltext_read', 'Scope excluded from focal title/abstract' not in basis)
    effects = row.get('effects', row.get('numeric_effects', []))
    record = {
        'doi': doi, 'title': row.get('title'), 'year': row.get('year'), 'pmcid': row.get('pmcid'),
        'origin': origin, 'decision': decision,
        'body_available': source.get('has_body', source.get('substantive_body_available', True)),
        'fulltext_substantively_read': bool(read_body),
        'screening_basis': basis,
        'endpoint_family': row.get('endpoint_family', row.get('response_family')),
        'region': row.get('region'), 'taxon_description': row.get('taxon', row.get('taxa')),
        'design': row.get('design'), 'response': row.get('outcome', row.get('actual_response')),
        'tidal_exposure': row.get('tide', row.get('tidal_exposure')),
        'solar_exposure': row.get('solar', row.get('solar_diel_predictor')),
        'joint_model_status': row.get('joint', row.get('joint_model_status')),
        'study_unit_description': row.get('unit', row.get('biological_sampling_units')),
        'original_url': source.get('url'), 'original_xml_sha256': source.get('sha256'),
        'ledger': ledger, 'json_pointer': pointer,
        'numeric_records': len(effects),
        'previously_audited_v133': doi in old_dois,
        'harmonized_meta_effect_admitted': False,
    }
    flattened = []
    key = 'effects' if is_a else 'numeric_effects'
    for j, effect in enumerate(effects):
        flattened.append({
            'doi': doi, 'origin': origin, 'screen_decision': decision,
            'endpoint_family': record['endpoint_family'], 'label': effect.get('label'),
            'estimate': effect.get('estimate'), 'reported_se': effect.get('se'),
            'reported_sd': effect.get('sd'),
            'reported_interval_json': json.dumps(effect.get('ci', effect.get('interval')), ensure_ascii=False),
            'scale_or_units': effect.get('scale', effect.get('units')),
            'role_as_extracted': effect.get('role', 'REPORTED_STATISTIC_SEE_SOURCE_LEDGER'),
            'source_locator': effect.get('locator', effect.get('source_locator')),
            'ledger': ledger, 'json_pointer': pointer + f'/{key}/{j}',
            'meta_included': False,
        })
    return record, flattened


def summarize_records(records):
    dois = [r['doi'] for r in records]
    if len(dois) != len(set(dois)):
        raise ValueError('DUPLICATE_DOI_WOULD_INFLATE_EVIDENCE')
    for row in records:
        if not row['body_available'] and row['decision'] != 'UNRESOLVED':
            raise ValueError('BODY_UNAVAILABLE_REQUIRES_UNRESOLVED_STATUS')
    return {
        'decision_records': len(records), 'distinct_article_dois': len(dois),
        'substantive_bodies_available': sum(r['body_available'] for r in records),
        'substantive_fulltext_read_records': sum(r['fulltext_substantively_read'] for r in records),
        'decision_counts': dict(sorted(Counter(r['decision'] for r in records).items())),
        'by_origin': dict(sorted(Counter(r['origin'] for r in records).items())),
        'numeric_extraction_records': sum(r['numeric_records'] for r in records),
        'articles_with_numeric_records': sum(r['numeric_records'] > 0 for r in records),
        'overlap_with_v133_17_article_source_audit': sum(r['previously_audited_v133'] for r in records),
        'new_to_v133_17_article_source_audit': sum(not r['previously_audited_v133'] for r in records),
        'article_and_record_counts_are_not_independent_coast_study_counts': True,
        'human_two_rater_prisma_adjudication_completed': False,
        'global_meta_pooled_effect': 'NOT_ESTIMATED',
    }


def run():
    directory = Path(__file__).resolve().parent
    old = json.loads((directory.parent / 'validation_v133/source_evidence_index.json').read_text())
    old_dois = {r['doi'].lower() for r in old['studies']}
    records, effects = [], []
    for name, origin in [('fulltext_screen_a.json', 'v133_acquired'),
                         ('fulltext_screen_b.json', 'v133_acquired'),
                         ('rescue_fulltext_screen.json', 'uncertain_rescue')]:
        value = json.loads((directory / name).read_text())
        rows = value if isinstance(value, list) else value['records']
        for i, row in enumerate(rows):
            record, rows_effects = normalize_record(row, 'validation_v134/' + name, i, origin, old_dois)
            records.append(record); effects.extend(rows_effects)
    summary = summarize_records(records)
    access = json.loads((directory / 'results/rescue_access_audit.json').read_text())
    summary.update({
        'frozen_metadata_corpus': 1061,
        'prior_field_triage_candidates': 150,
        'fixed_rule_uncertain_rescue_candidates': access['selected_candidates'],
        'total_targeted_article_access_checks': 150 + access['selected_candidates'],
        'remaining_metadata_records_outside_these_targeted_checks': 1061 - 150 - access['selected_candidates'],
        'rescue_access_status_counts': access['access_status_counts'],
        'scope': 'Bounded full-text/source expansion; not an exhaustive completed global systematic review.',
    })
    output = directory / 'results'
    output.mkdir(exist_ok=True)
    (output / 'evidence_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    (output / 'normalized_study_decisions.json').write_text(json.dumps(records, indent=2, ensure_ascii=False) + '\n')
    with (output / 'reported_numeric_records.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(effects[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(effects)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == '__main__':
    run()
