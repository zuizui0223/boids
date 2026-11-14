"""Source-exact supplemental contrasts and explicitly bounded uncertainty.

No pooling estimator is implemented. This is not a replacement for frozen v131.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import io
import json
from math import exp, isclose, isfinite, sqrt
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

DOI = '10.1007/s12237-025-01598-x'
SOURCE_URL = 'https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs12237-025-01598-x/MediaObjects/12237_2025_1598_MOESM1_ESM.docx'
SOURCE_SHA256 = '51929d7a7eac9b5c4c6ab54ac8bab9321df8add192edc98e1c4ca8a09c08783a'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
METRICS = {'hedges_g', 'fisher_z_partial_r', 'cv_relative_skill', 'log_rate_ratio', 'log_odds_ratio'}
ENDPOINTS = {'classified_behavior', 'movement', 'field_density', 'acoustic_detection'}


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def contrast_difference(a, b, covariance=None):
    for estimate, se in (a, b):
        if not numeric(estimate) or not numeric(se) or se <= 0:
            raise ValueError('Finite estimates and strictly positive marginal SEs required')
    estimate = a[0] - b[0]
    lower, upper = abs(a[1] - b[1]), a[1] + b[1]
    result = {'estimate': estimate, 'se_lower_bound': lower, 'se_upper_bound': upper,
              'sampling_se': None, 'uncertainty_type': 'unknown_covariance_upper_bound',
              'normal_covariance_envelope_95': [estimate - 1.96 * upper, estimate + 1.96 * upper],
              'eligible_for_inverse_variance_weight': False}
    if covariance is not None:
        bound = a[1] * b[1]
        if not numeric(covariance) or (abs(covariance) > bound and
                                       not isclose(abs(covariance), bound, rel_tol=1e-12, abs_tol=0.0)):
            raise ValueError('Covariance violates the Cauchy-Schwarz bound')
        se = sqrt(max(0.0, a[1] ** 2 + b[1] ** 2 - 2 * covariance))
        result.update({'sampling_se': se, 'uncertainty_type': 'supplied_covariance',
                       'normal_interval_95': [estimate - 1.96 * se, estimate + 1.96 * se],
                       'eligible_for_inverse_variance_weight': se > 0})
    return result


def rounding_envelope(a_est, a_se, b_est, b_se):
    def half_unit(s):
        return float(Decimal(10) ** Decimal(str(s)).as_tuple().exponent / 2)
    a, b, sa, sb = float(a_est), float(b_est), float(a_se), float(b_se)
    contrast_difference((a, sa), (b, sb))
    half_est = half_unit(a_est) + half_unit(b_est)
    largest_se = sa + sb + half_unit(a_se) + half_unit(b_se)
    est_lo, est_hi = a - b - half_est, a - b + half_est
    return {'rounding_assumption': 'Each printed number is rounded to its displayed decimal precision.',
            'estimate_range': [est_lo, est_hi], 'maximum_se': largest_se,
            'normal_envelope_95': [est_lo - 1.96 * largest_se, est_hi + 1.96 * largest_se]}


def poolability_audit(rows, strict_three_oceans=False):
    """An additional prospective contract, never a pooled-effect estimator."""
    signature = ('endpoint_family', 'outcome_id', 'metric', 'estimand_id', 'contrast_id', 'exposure_units', 'exposure_definition_id',
                 'conditioning', 'adjustment_signature')
    required = ('effect_id', 'study_id', 'coast_id', 'taxon', 'functional_group', 'ocean_region',
                'source_url', 'source_locator', 'doi', 'effect_estimate_status') + signature
    reasons = []
    if not rows:
        return {'admitted': False, 'reasons': ['EMPTY_EFFECT_LEDGER'], 'pooled_effect': None}
    if any(any(r.get(k) in (None, '') for k in required) for r in rows):
        reasons.append('MISSING_SOURCE_OR_ESTIMAND_METADATA')
    if len({tuple(r.get(k) for k in signature) for r in rows}) != 1:
        reasons.append('INCOMPATIBLE_ESTIMAND_OR_SCALE')
    if any(r.get('metric') not in METRICS or r.get('endpoint_family') not in ENDPOINTS for r in rows):
        reasons.append('UNSUPPORTED_METRIC_OR_ENDPOINT')
    if any(r.get('effect_estimate_status') != 'SOURCE_EXTRACTED' for r in rows):
        reasons.append('EFFECT_NOT_SOURCE_EXTRACTED')
    if any(r.get('source_verified') is not True or r.get('label_ambiguous') is not False for r in rows):
        reasons.append('SOURCE_OR_LABEL_NOT_VERIFIED')
    if any(r.get('model_provenance_resolved') is not True for r in rows):
        reasons.append('MODEL_PROVENANCE_UNRESOLVED')
    if any(r.get('uncertainty_type') != 'reported_sampling_se' or
           not numeric(r.get('sampling_se')) or r['sampling_se'] <= 0 for r in rows):
        reasons.append('INEXACT_OR_MISSING_SAMPLING_UNCERTAINTY')
    if any(not numeric(r.get('effect')) for r in rows):
        reasons.append('NONFINITE_EFFECT')
    if any(r.get('metric') == 'cv_relative_skill' and numeric(r.get('effect')) and r['effect'] > 1 for r in rows):
        reasons.append('RELATIVE_SKILL_EXCEEDS_NONNEGATIVE_LOSS_UPPER_BOUND')
    skill_rows = [r for r in rows if r.get('metric') == 'cv_relative_skill']
    if skill_rows and (any(not r.get('loss_id') or r.get('loss_is_nonnegative') is not True or
                          r.get('baseline_loss_positive') is not True or
                          r.get('normalizer_definition') != '(baseline_loss-model_loss)/baseline_loss'
                          for r in skill_rows) or
                       len({r.get('loss_id') for r in skill_rows}) != 1):
        reasons.append('RELATIVE_SKILL_LOSS_OR_NORMALIZER_NOT_COMPARABLE')
    studies, coasts = [r.get('study_id') for r in rows], [r.get('coast_id') for r in rows]
    if len(set(studies)) != len(studies) or len(set(coasts)) != len(coasts):
        reasons.append('DEPENDENCE_WITHOUT_COVARIANCE')
    if len(set(studies)) < 3 or len(set(coasts)) < 3:
        reasons.append('FEWER_THAN_THREE_INDEPENDENT_STUDY_COASTS')
    if len({r.get('taxon') for r in rows}) < 3 or len({r.get('functional_group') for r in rows}) < 2:
        reasons.append('GLOBAL_TAXON_FUNCTIONAL_GROUP_REQUIREMENT_NOT_MET')
    regions = {r.get('ocean_region') for r in rows}
    if strict_three_oceans and len(regions) < 3:
        reasons.append('GLOBAL_OCEAN_CLAIM_REQUIRES_THREE_REGIONS')
    return {'admitted': not reasons, 'reasons': reasons, 'pooled_effect': None,
            'independent_study_labels': len(set(studies)), 'coast_labels': len(set(coasts)),
            'ocean_region_labels': len(regions), 'strict_three_oceans': strict_three_oceans,
            'n_rows_is_not_independent_k': len(rows)}


def extract_docx(raw):
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('Original supplemental DOCX SHA256 mismatch')
    z = zipfile.ZipFile(io.BytesIO(raw))
    root = ET.fromstring(z.read('word/document.xml'))
    tables = []
    for table in root.findall('.//w:tbl', NS):
        tables.append([[''.join(c.itertext()).strip() for c in row.findall('w:tc', NS)]
                       for row in table.findall('w:tr', NS)])
    if len(tables) != 8 or tables[6][0][:4] != ['Behaviour', 'Comparisons', 'Estimate', 'SE']:
        raise ValueError('Original supplemental table schema changed')
    effects = []

    def add(behavior, site, table, panel, row_number, conditioning, values):
        label, est, se, zvalue, pvalue = values
        estimate, stderr = float(est), float(se)
        if not numeric(estimate) or stderr <= 0:
            raise ValueError('Invalid source numeric effect')
        if panel == 'A':
            estimand = 'diel_contrast_at_tidal_stage'
        elif panel == 'B':
            estimand = 'tidal_contrast_at_diel_period'
        else:
            estimand = 'additive_diel_contrast' if 'tide' not in label else 'additive_tidal_contrast'
        model = 'diel_plus_tide' if table == 'S7' else 'diel_times_tide'
        model_resolved = True
        model_note = 'Original selected feeding model or reported conditional S8 comparisons.'
        if table == 'S7' and behavior == 'preening':
            model, conditioning = 'diel_only', 'no_tidal_adjustment'
            estimand = 'diel_contrast_no_tidal_adjustment'
            model_note = 'Original main article Table 2 and Results retain only diel for Tagus preening.'
        elif table == 'S7' and behavior == 'roosting':
            model, model_resolved = 'model_provenance_unresolved', False
            conditioning = 'marginal_over_other_cycle_weighting_and_model_averaging_unresolved'
            estimand = 'marginal_tidal_contrast_unresolved_model' if 'tide' in label else 'marginal_diel_contrast_unresolved_model'
            model_note = ('Table 2 ranks interaction first and additive second within delta AICc 2; '
                          'methods mention both model averaging and best-model emmeans. S7 marginal '
                          'contrasts do not resolve the model/averaging provenance; no harmonization.')
        effects.append({
            'effect_id': f'{table}_{panel or "main"}_{row_number}_{behavior}',
            'study_id': 'RODRIGUES_2025_SPOONBILL', 'coast_id': 'PT_' + site.upper().replace(' ', '_'),
            'doi': DOI, 'source_url': SOURCE_URL, 'source_sha256': SOURCE_SHA256,
            'source_table': table, 'source_panel': panel, 'source_data_row_1based': row_number,
            'source_locator': f'Table {table}, panel {panel or "main"}, data row {row_number}',
            'effect_estimate_status': 'SOURCE_EXTRACTED', 'ocean_region': 'Atlantic',
            'site': site, 'taxon': 'Platalea leucorodia', 'functional_group': 'shorebird',
            'behavior': behavior, 'independent_animals_in_site': 10 if site == 'Tagus estuary' else 25,
            'endpoint_family': 'classified_behavior',
            'outcome_id': 'ACC_classified_' + behavior + '_event_probability',
            'metric': 'log_odds_ratio', 'estimand_id': estimand, 'contrast_id': label,
            'exposure_units': 'published_four_diel_and_four_tidal_categories',
            'exposure_definition_id': 'sunrise_sunset_pm1p5h_tide_extrema_pm2h',
            'exposure_definition': ('Sunrise/sunset each span 1.5h before to 1.5h after the event; '
                                    'day/night exclude these transition periods. Low/high tide each '
                                    'span 2h before to 2h after the corresponding extremum; '
                                    'rising/ebbing occupy the intervening periods.'),
            'conditioning': conditioning,
            'adjustment_signature': 'binomial_GLMM_individual_random_intercept_' + model,
            'model_provenance_resolved': model_resolved, 'model_provenance_note': model_note,
            'contrast_as_printed': label, 'estimate_as_printed': est, 'se_as_printed': se,
            'z_as_printed': zvalue, 'p_as_printed': pvalue, 'p_adjustment': 'Tukey',
            'effect': estimate, 'sampling_se': stderr, 'uncertainty_type': 'reported_sampling_se',
            'source_verified': True, 'label_ambiguous': False, 'independent_row': False,
            'reported_ci': None, 'sampling_covariance_with_other_contrasts': None,
            'derived_odds_ratio': exp(estimate),
            'derived_unadjusted_normal_95_log_interval': [estimate - 1.96 * stderr, estimate + 1.96 * stderr],
            'derived_interval_is_not_tukey_adjusted_or_rounding_robust': True,
        })

    behavior = ''
    for i, row in enumerate(tables[6][1:], start=1):
        if row[0]:
            behavior = row[0].lower()
        add(behavior, 'Tagus estuary', 'S7', None, i, 'additive_other_cycle_adjustment', row[1:6])
    behavior, stage, period = '', '', ''
    for i, row in enumerate(tables[7][2:], start=1):
        if len(row) != 13:
            raise ValueError('Unexpected merged supplemental row schema')
        if row[0]:
            behavior = row[0].lower()
        if row[1]:
            stage = row[1].lower()
        if row[7]:
            period = row[7].lower()
        add(behavior, 'Ria Formosa', 'S8', 'A', i, 'tidal_stage=' + stage, row[2:7])
        add(behavior, 'Ria Formosa', 'S8', 'B', i, 'diel_period=' + period, row[8:13])
    keys = Counter((r['behavior'], r['site'], r['source_table'], r['source_panel'], r['conditioning'], r['contrast_id']) for r in effects)
    for r in effects:
        key = (r['behavior'], r['site'], r['source_table'], r['source_panel'], r['conditioning'], r['contrast_id'])
        if keys[key] > 1:
            r['label_ambiguous'] = True
            r['label_issue'] = 'Repeated source label with different values; not silently relabeled.'
    return effects


def run(docx_path, output_dir):
    raw = Path(docx_path).read_bytes()
    effects = extract_docx(raw)
    feeding = [r for r in effects if r['behavior'] == 'feeding']
    daynight = [r for r in feeding if r['contrast_id'] == 'day vs night']
    low = next(r for r in daynight if r['conditioning'] == 'tidal_stage=low tide')
    high = next(r for r in daynight if r['conditioning'] == 'tidal_stage=high tide')
    result = contrast_difference((low['effect'], low['sampling_se']), (high['effect'], high['sampling_se']))
    result.update({'estimand': '(day-night log odds of feeding at low tide) - (day-night at high tide)',
                   'source_effect_ids': [low['effect_id'], high['effect_id']],
                   'ratio_of_day_night_odds_ratios': exp(result['estimate']),
                   'normal_covariance_envelope_ratio_scale': [exp(x) for x in result['normal_covariance_envelope_95']],
                   'rounding_sensitivity': rounding_envelope(low['estimate_as_printed'], low['se_as_printed'], high['estimate_as_printed'], high['se_as_printed']),
                   'one_study_one_site_interaction': True,
                   'exploratory_reanalysis_of_published_rounded_contrasts': True,
                   'not_a_reported_exact_CI_or_causal_effect': True})
    roundenv = result['rounding_sensitivity']['normal_envelope_95']
    result['rounding_sensitivity']['ratio_envelope'] = [exp(x) for x in roundenv]
    source = {'version': 'v133-spoonbill-source-extracted-effects-1',
              'doi': DOI, 'source_url': SOURCE_URL, 'source_sha256': SOURCE_SHA256,
              'source_bytes': len(raw), 'effects': effects,
              'scope': 'All S7/S8 behavior contrast rows; one study, two wetlands, correlated outcomes.'}
    summary = {'version': 'v133-published-effect-calculation-1',
               'source_effect_rows': len(effects), 'feeding_effect_rows': len(feeding),
               'source_studies': 1, 'source_wetlands': 2, 'distinct_species': 1,
               'ambiguous_all_behavior_rows': sum(r['label_ambiguous'] for r in effects),
               'ambiguous_feeding_rows': sum(r['label_ambiguous'] for r in feeding),
               'day_night_feeding_effects': daynight, 'ria_low_vs_high_diel_interaction': result,
               'tagus_interaction': {'estimate': None, 'status': 'NOT_ESTIMATED_ADDITIVE_MODEL_IMPOSES_ABSENCE'},
               'feeding_row_poolability': poolability_audit(feeding),
               'global_meta_pooled_effect': 'NOT_ESTIMATED',
               'no_raw_behavioral_fit_performed': True}
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, obj in [('published_spoonbill_effect_ledger.json', source),
                      ('results/spoonbill_tide_diel_contrasts.json', summary)]:
        p = out / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'day_night_feeding_effects'}, ensure_ascii=False, allow_nan=False))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--docx', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    run(args.docx, args.output_dir)
