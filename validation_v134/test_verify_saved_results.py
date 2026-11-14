"""Tampering tests: reject internally inconsistent saved science artifacts."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from validation_v134.verify_saved_results import verify

REPOSITORY = Path(__file__).resolve().parents[1]


class SavedResultsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(REPOSITORY / 'validation_v134', self.root / 'validation_v134',
                        ignore=shutil.ignore_patterns('__pycache__', 'figures'))
        for name in ('validation_v133/results/fulltext_access_audit.json',
                     'validation_v133/source_evidence_index.json',
                     'docs/V134_PENGUIN_PREFIT_ANALYSIS.md'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPOSITORY / name, target)

    def change(self, name, mutate):
        path = self.root / 'validation_v134' / name
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value))

    def test_saved_artifacts_pass_without_writes(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = verify(self.root)
        self.assertEqual(result['decision_records'], 118)
        self.assertEqual(result['scenarios'], 10)
        self.assertGreater(result['checks_passed'], 500)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_duplicate_doi_is_rejected(self):
        self.change('results/normalized_study_decisions.json', lambda a: a.append(a[0]))
        with self.assertRaisesRegex(ValueError, 'DECISION'):
            verify(self.root)

    def test_numeric_csv_disagrees_with_ledger(self):
        p = self.root / 'validation_v134/results/reported_numeric_records.csv'
        p.write_text(p.read_text().replace('-238,', '-237,', 1))
        with self.assertRaisesRegex(ValueError, 'NUMERIC'):
            verify(self.root)

    def test_original_source_hash_link_is_checked(self):
        self.change('fulltext_screen_a.json', lambda a: a[0]['source'].update(sha256='0'*64))
        with self.assertRaisesRegex(ValueError, 'SOURCE|LEDGER'):
            verify(self.root)

    def test_normalized_read_claim_cannot_be_changed_with_summary(self):
        self.change('results/normalized_study_decisions.json',
                    lambda a: a[0].update(fulltext_substantively_read=False))
        self.change('results/evidence_summary.json',
                    lambda a: a.update(substantive_fulltext_read_records=a['substantive_fulltext_read_records']-1))
        with self.assertRaisesRegex(ValueError, 'LEDGER_READ'):
            verify(self.root)

    def test_prefit_spec_tampering_is_rejected(self):
        p = self.root / 'docs/V134_PENGUIN_PREFIT_ANALYSIS.md'
        p.write_text(p.read_text()+'\nchanged\n')
        with self.assertRaisesRegex(ValueError, 'SPEC_HASH'):
            verify(self.root)

    def test_model_delta_is_reconstructed(self):
        self.change('results/penguin_analysis_results.json', lambda a: a['scenarios'][0].update(delta_current=99))
        with self.assertRaisesRegex(ValueError, 'DELTA'):
            verify(self.root)

    def test_constant_baseline_is_recomputed_from_inputs(self):
        def alter(a):
            a['scenarios'][1]['scores']['diagnostic_training_prevalence']['cross_entropy'] += .01
        self.change('results/penguin_analysis_results.json', alter)
        with self.assertRaisesRegex(ValueError, 'BASELINE'):
            verify(self.root)

    def test_missing_replay_scenario_is_rejected(self):
        replay = self.root / 'replay'
        replay.mkdir()
        result = json.loads((self.root/'validation_v134/results/penguin_analysis_results.json').read_text())
        result['scenarios'].pop()
        (replay/'penguin_analysis_results.json').write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError, 'REPLAY'):
            verify(self.root, replay_directory=replay)

    def test_optional_cache_requires_original_xml(self):
        with self.assertRaisesRegex(ValueError, 'XML'):
            verify(self.root, fulltext_cache=self.root/'missing_cache')


if __name__ == '__main__':
    unittest.main()
