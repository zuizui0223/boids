"""Protect source identity and the outcome-independent sensitivity screen."""
import unittest

from validation_v134.source_screen import select_rescue, verify_article


def article(ids='<article-id pub-id-type="doi">10.1/right</article-id>', body='<body><sec><p>Observed activity.</p></sec></body>', refs=''):
    return f'<article><front><article-meta>{ids}</article-meta></front>{body}<back>{refs}</back></article>'.encode()


class SourceScreenTests(unittest.TestCase):
    def test_rescue_selection_ignores_result_and_access(self):
        rows = [
            {'id': 'a', 'automated_relevance_priority': 'uncertain_relevance', 'title': 'Fish movement', 'source_screen_evidence_flags': {'tide': True, 'behavior': True}, 'p': 0.9},
            {'id': 'b', 'automated_relevance_priority': 'uncertain_relevance', 'title': 'Intertidal community', 'source_screen_evidence_flags': {}, 'p': 0.001},
            {'id': 'c', 'automated_relevance_priority': 'possible_field_tide_only', 'title': 'Tidal fish', 'source_screen_evidence_flags': {'tide': True, 'behavior': True}},
            {'id': 'd', 'automated_relevance_priority': 'uncertain_relevance', 'title': 'Fish movement', 'source_screen_evidence_flags': {'tide': True, 'behavior': False}},
        ]
        self.assertEqual([x['id'] for x in select_rescue({'original_published_bibliography_machine_triage': rows})], ['a', 'b'])
        rows[0]['p'] = 0.000001
        self.assertEqual(len(select_rescue({'original_published_bibliography_machine_triage': rows})), 2)

    def test_front_doi_match_and_body(self):
        r = verify_article(article(), doi='https://doi.org/10.1/RIGHT')
        self.assertEqual(r['identity_basis'], 'DOI')
        self.assertTrue(r['substantive_body_available'])

    def test_reference_doi_cannot_verify_focal_article(self):
        raw = article(refs='<ref-list><ref><pub-id pub-id-type="doi">10.1/wrong</pub-id></ref></ref-list>')
        with self.assertRaisesRegex(ValueError, 'DOI_MISMATCH'):
            verify_article(raw, doi='10.1/wrong')

    def test_pmid_fallback_requires_focal_pmid(self):
        raw = article(ids='<article-id pub-id-type="pmid">12345</article-id>')
        self.assertEqual(verify_article(raw, pmid='12345')['identity_basis'], 'PMID')
        with self.assertRaisesRegex(ValueError, 'PMID_MISMATCH'):
            verify_article(raw, pmid='999')

    def test_doi_mismatch_cannot_be_rescued_with_pmid(self):
        raw = article(ids='<article-id pub-id-type="pmid">12345</article-id><article-id pub-id-type="doi">10.1/right</article-id>')
        with self.assertRaisesRegex(ValueError, 'DOI_MISMATCH'):
            verify_article(raw, doi='10.1/wrong', pmid='12345')

    def test_absent_or_empty_body_remains_unavailable(self):
        for body in ('', '<body/>', '<body><sec><p> </p></sec></body>'):
            self.assertFalse(verify_article(article(body=body), doi='10.1/right')['substantive_body_available'])

    def test_no_identity_is_not_verification(self):
        with self.assertRaisesRegex(ValueError, 'MISSING_EXPECTED_IDENTITY'):
            verify_article(article())


if __name__ == '__main__':
    unittest.main()
