import importlib.util
import json
from pathlib import Path
import unittest


class SourceEffectTests(unittest.TestCase):
    def module(self):
        p = Path(__file__).with_name('effect_extraction.py')
        self.assertTrue(p.exists(), 'effect extraction is not implemented')
        spec = importlib.util.spec_from_file_location('effect_extraction', p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_unknown_covariance_is_a_bound_not_an_independence_se(self):
        m = self.module()
        result = m.contrast_difference((-1.17, 0.04), (-0.05, 0.05))
        self.assertAlmostEqual(result['estimate'], -1.12)
        self.assertAlmostEqual(result['se_lower_bound'], 0.01)
        self.assertAlmostEqual(result['se_upper_bound'], 0.09)
        self.assertIsNone(result['sampling_se'])
        self.assertAlmostEqual(result['normal_covariance_envelope_95'][0], -1.2964)
        self.assertFalse(result['eligible_for_inverse_variance_weight'])

    def test_supplied_covariance_gets_correct_difference_variance(self):
        m = self.module()
        result = m.contrast_difference((3.0, 2.0), (1.0, 1.0), covariance=1.0)
        self.assertEqual(result['estimate'], 2.0)
        self.assertAlmostEqual(result['sampling_se'], 3 ** 0.5)
        with self.assertRaises(ValueError):
            m.contrast_difference((3.0, 2.0), (1.0, 1.0), covariance=2.01)

    def test_rounded_source_uncertainty_is_propagated(self):
        m = self.module()
        result = m.rounding_envelope('-1.17', '0.04', '-0.05', '0.05')
        self.assertAlmostEqual(result['estimate_range'][0], -1.13)
        self.assertAlmostEqual(result['estimate_range'][1], -1.11)
        self.assertAlmostEqual(result['maximum_se'], 0.1)
        self.assertAlmostEqual(result['normal_envelope_95'][0], -1.326)
        self.assertAlmostEqual(result['normal_envelope_95'][1], -0.914)

    def test_invalid_or_zero_marginal_uncertainty_is_not_admitted(self):
        m = self.module()
        for a in [(0, 0), (0, -1), (float('nan'), 1), (1, float('inf'))]:
            with self.assertRaises(ValueError):
                m.contrast_difference(a, (0, 1))

    def test_impossible_covariance_is_rejected_at_small_se_scale(self):
        with self.assertRaises(ValueError):
            self.module().contrast_difference((0.2, 1e-10), (0.1, 1e-10), covariance=1e-15)

    def test_same_metric_with_different_estimand_is_not_poolable(self):
        m = self.module()
        rows = self.fixtures()
        rows[1]['estimand_id'] = 'tide_only_main_effect'
        result = m.poolability_audit(rows)
        self.assertFalse(result['admitted'])
        self.assertIn('INCOMPATIBLE_ESTIMAND_OR_SCALE', result['reasons'])

    def test_bound_and_shared_study_do_not_become_independent_meta_rows(self):
        m = self.module()
        rows = self.fixtures()
        rows[1]['study_id'] = rows[0]['study_id']
        rows[2]['uncertainty_type'] = 'unknown_covariance_upper_bound'
        result = m.poolability_audit(rows)
        self.assertFalse(result['admitted'])
        self.assertIn('DEPENDENCE_WITHOUT_COVARIANCE', result['reasons'])
        self.assertIn('INEXACT_OR_MISSING_SAMPLING_UNCERTAINTY', result['reasons'])

    def test_large_negative_relative_skill_is_not_selectively_excluded(self):
        m = self.module()
        rows = self.fixtures()
        for row in rows:
            row['metric'] = 'cv_relative_skill'
            row['effect'] = -2.0
            row.update(loss_id='heldout_mean_squared_error', loss_is_nonnegative=True,
                       baseline_loss_positive=True,
                       normalizer_definition='(baseline_loss-model_loss)/baseline_loss')
        self.assertTrue(m.poolability_audit(rows)['admitted'])

    def test_relative_skill_requires_explicit_loss_and_normalizer(self):
        m = self.module()
        rows = self.fixtures()
        for row in rows:
            row['metric'] = 'cv_relative_skill'
        self.assertFalse(m.poolability_audit(rows)['admitted'])

    def test_source_locators_and_extraction_status_are_required(self):
        m = self.module()
        for field in ('source_url', 'source_locator', 'effect_estimate_status'):
            rows = self.fixtures()
            for row in rows:
                del row[field]
            with self.subTest(field=field):
                self.assertFalse(m.poolability_audit(rows)['admitted'])
        rows = self.fixtures()
        rows[0]['effect_estimate_status'] = 'SYNTHETIC_EXAMPLE'
        self.assertFalse(m.poolability_audit(rows)['admitted'])

    def test_unsupported_metrics_and_endpoints_are_not_admitted(self):
        m = self.module()
        for field, value in (('metric', 'pooled_mse_and_oddsratio'),
                             ('endpoint_family', 'laboratory_free_running_clock')):
            rows = self.fixtures()
            for row in rows:
                row[field] = value
            with self.subTest(field=field):
                self.assertFalse(m.poolability_audit(rows)['admitted'])

    def test_global_ocean_claim_keeps_the_three_region_requirement(self):
        m = self.module()
        rows = self.fixtures()
        for row in rows:
            row['ocean_region'] = 'Atlantic'
        self.assertTrue(m.poolability_audit(rows)['admitted'])
        self.assertFalse(m.poolability_audit(rows, strict_three_oceans=True)['admitted'])

    def test_original_tagus_preening_model_has_no_tide_adjustment(self):
        ledger = json.loads(Path(__file__).with_name('published_spoonbill_effect_ledger.json').read_text())
        rows = [r for r in ledger['effects'] if r['source_table'] == 'S7' and r['behavior'] == 'preening']
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertEqual(row['adjustment_signature'], 'binomial_GLMM_individual_random_intercept_diel_only')
            self.assertEqual(row['conditioning'], 'no_tidal_adjustment')

    def test_unresolved_roosting_model_is_not_recorded_as_additive(self):
        ledger = json.loads(Path(__file__).with_name('published_spoonbill_effect_ledger.json').read_text())
        rows = [r for r in ledger['effects'] if r['source_table'] == 'S7' and r['behavior'] == 'roosting']
        self.assertEqual(len(rows), 12)
        for row in rows:
            self.assertFalse(row.get('model_provenance_resolved', True))
            self.assertIn('unresolved', row['adjustment_signature'])
        fixtures = self.fixtures()
        fixtures[0]['model_provenance_resolved'] = False
        self.assertFalse(self.module().poolability_audit(fixtures)['admitted'])

    def test_missing_contrast_definition_cannot_pass_as_comparable(self):
        m = self.module()
        rows = self.fixtures()
        for row in rows:
            del row['contrast_id']
        result = m.poolability_audit(rows)
        self.assertFalse(result['admitted'])
        self.assertIn('MISSING_SOURCE_OR_ESTIMAND_METADATA', result['reasons'])

    def test_four_bins_with_different_physical_windows_are_incompatible(self):
        m = self.module()
        rows = self.fixtures()
        rows[1]['exposure_definition_id'] = 'solar_twilight_and_tide_extrema_plusminus_one_hour'
        self.assertFalse(m.poolability_audit(rows)['admitted'])

    @staticmethod
    def fixtures():
        return [dict(effect_id=str(i), study_id='study'+str(i), coast_id='coast'+str(i),
                     source_url='https://example.org/original'+str(i), source_locator='Table 1, row 3',
                     doi='10.1/example'+str(i), effect_estimate_status='SOURCE_EXTRACTED',
                     ocean_region='ocean'+str(i),
                     taxon='taxon'+str(i), functional_group='bird' if i == 0 else 'crustacean',
                     endpoint_family='classified_behavior', outcome_id='foraging_probability', metric='log_odds_ratio',
                     estimand_id='low_high_difference_in_day_night_log_odds',
                     contrast_id='(day-night)low-(day-night)high',
                     exposure_units='source_four_phase', conditioning='same_day_night_definition',
                     exposure_definition_id='sunrise_sunset_pm1p5h_tide_extrema_pm2h',
                     adjustment_signature='source_model', uncertainty_type='reported_sampling_se',
                     source_verified=True, label_ambiguous=False,
                     model_provenance_resolved=True,
                     effect=-0.3, sampling_se=0.1) for i in range(3)]


if __name__ == '__main__':
    unittest.main()
