import unittest

from validation_v134.compile_evidence import summarize_records


def record(doi, decision='FIELD_TIDE_ONLY', body=True):
    return {'doi': doi, 'decision': decision, 'body_available': body,
            'fulltext_substantively_read': body, 'numeric_records': 0,
            'origin': 'v133_acquired', 'previously_audited_v133': False}


class EvidenceSummaryTests(unittest.TestCase):
    def test_duplicate_doi_is_not_another_study(self):
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_DOI'):
            summarize_records([record('10.1/a'), record('10.1/a')])

    def test_missing_body_cannot_be_core_eligible(self):
        with self.assertRaisesRegex(ValueError, 'BODY_UNAVAILABLE'):
            summarize_records([record('10.1/a', body=False)])

    def test_unresolved_body_remains_in_accounting(self):
        result = summarize_records([record('10.1/a', 'UNRESOLVED', body=False), record('10.1/b')])
        self.assertEqual(result['decision_records'], 2)
        self.assertEqual(result['substantive_bodies_available'], 1)
        self.assertEqual(result['decision_counts']['UNRESOLVED'], 1)
        self.assertEqual(result['global_meta_pooled_effect'], 'NOT_ESTIMATED')


if __name__ == '__main__':
    unittest.main()
