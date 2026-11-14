import importlib.util
from pathlib import Path
import unittest


class OriginalFulltextAuditTests(unittest.TestCase):
    def module(self):
        p = Path(__file__).with_name('fulltext_audit.py')
        self.assertTrue(p.exists(), 'source audit is not implemented')
        spec = importlib.util.spec_from_file_location('fulltext_audit', p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_field_selection_does_not_promote_uncertain_or_review_to_included(self):
        m = self.module()
        rows = [{'id': 'a', 'automated_relevance_priority': 'possible_field_tide_solar'},
                {'id': 'b', 'automated_relevance_priority': 'possible_field_tide_only'},
                {'id': 'c', 'automated_relevance_priority': 'uncertain_relevance'},
                {'id': 'd', 'automated_relevance_priority': 'possible_review_theory'}]
        self.assertEqual([r['id'] for r in m.select_candidates({'original_published_bibliography_machine_triage': rows})], ['a', 'b'])

    def test_mismatched_doi_cannot_supply_primary_evidence(self):
        m = self.module()
        xml = b'<article><front><article-meta><article-id pub-id-type="doi">10.1/wrong</article-id></article-meta></front><body><p>Tide and night.</p></body></article>'
        with self.assertRaises(ValueError):
            m.summarize_xml(xml, '10.1/right')

    def test_reference_only_tide_is_not_body_evidence(self):
        m = self.module()
        xml = b'<article article-type="research-article"><front><article-meta><article-id pub-id-type="doi">10.1/example</article-id></article-meta></front><body><p>A forest example.</p></body><back><ref-list><ref>tidal night effect SE</ref></ref-list></back></article>'
        x = m.summarize_xml(xml, 'https://doi.org/10.1/example')
        self.assertFalse(x['body_mentions_tide'])
        self.assertFalse(x['body_mentions_diel'])
        self.assertFalse(x['fulltext_eligibility_decided'])

    def test_table_and_primary_data_link_retain_locators(self):
        m = self.module()
        xml = b'<article xmlns:xlink="http://www.w3.org/1999/xlink" article-type="research-article"><front><article-meta><article-id pub-id-type="doi">10.1/example</article-id><title-group><article-title>Example</article-title></title-group></article-meta></front><body><sec><p>Tidal stage and day night.</p><table-wrap id="t1"><label>Table 1</label><caption><p>Tide estimates</p></caption><table><tr><td>SE</td><td>0.04</td></tr></table></table-wrap><p><ext-link xlink:href="https://zenodo.org/records/123">Data</ext-link></p></sec></body><back><ref-list><ref><ext-link xlink:href="https://zenodo.org/records/999">Other paper data</ext-link></ref></ref-list></back></article>'
        x = m.summarize_xml(xml, '10.1/example')
        self.assertEqual(x['table_count'], 1)
        self.assertEqual(x['tidal_table_locators'][0]['id'], 't1')
        self.assertEqual(x['primary_repository_links'], ['https://zenodo.org/records/123'])

    def test_correction_is_preserved_as_article_type_not_new_experiment(self):
        m = self.module()
        xml = b'<article article-type="correction"><front><article-meta><article-id pub-id-type="doi">10.1/example</article-id></article-meta></front><body><p>Tidal and diel correction.</p></body></article>'
        self.assertEqual(m.summarize_xml(xml, '10.1/example')['article_type'], 'correction')

    def test_supplement_locator_in_child_media_is_retained(self):
        m = self.module()
        xml = b'<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><article-meta><article-id pub-id-type="doi">10.1/example</article-id></article-meta></front><body><supplementary-material id="s1"><label>Supplement 1</label><media xlink:href="original-supplement.xlsx"/></supplementary-material></body></article>'
        loc = m.summarize_xml(xml, '10.1/example')['supplement_locators'][0]
        self.assertEqual(loc['href'], 'original-supplement.xlsx')
        self.assertEqual(loc['all_hrefs'], ['original-supplement.xlsx'])


if __name__ == '__main__':
    unittest.main()
