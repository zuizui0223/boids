"""v132 source and machine-screen logic known truths. Fixtures are synthetic only."""
from __future__ import annotations
import copy
import unittest
import period_stratified_literature_screen as m

def old_197():
    return {'analysis':'V131_GLOBAL_TIDAL_SOLAR_TEMPORAL_NICHE_RAW_SOURCE_AND_METADATA_DISCOVERY',
      'literature_search_metadata_candidates_only':{
       'metadata_only_candidate_citations':[
       {'doi':f'10.1200/example{i}','title':f'Old paper {i}','year':1990+i%30,
        'publication_pmid':str(5000+i),'journal':'test'} for i in range(197)]}}

class TrueV132SearchSafety(unittest.TestCase):
    def test_stratified_search_fixed_and_36_queries(self):
        self.assertEqual(len(m.ERAS),6)
        self.assertEqual(len(m.TAXON),6)
        self.assertEqual(len(m.ERAS)*len(m.TAXON),36)
        self.assertEqual(m.MAX_PER_QUERY,40)
        a=m.query_string('shorebirds','1970_1999')
        b=m.query_string('coastal_other','2025_2026')
        self.assertIn('FIRST_PDATE:[1970-01-01 TO 1999-12-31]',a)
        self.assertIn('FIRST_PDATE:[2025-01-01 TO 2026-12-31]',b)
        self.assertIn('oystercatcher',a)
        self.assertIn('intertidal reptile',b)

    def test_field_tide_solar_diagnostic_and_weak_abstract_not_verified_study(self):
        x=m.triage_title_abstract('Shorebird movement in tidal marsh',
              'GPS field measurements showed diel and tidal behaviour of birds')
        self.assertEqual(x[0],'possible_field_tide_solar')
        self.assertTrue(x[1]['tide'])
        self.assertTrue(x[1]['solar'])
        self.assertEqual(m.triage_title_abstract('Fish tidal estuary movement',
                 'GPS fish field study of migration and tidal phase')[0],
                 'possible_field_tide_only')
        self.assertEqual(m.triage_title_abstract('Molecular circatidal rhythms in marine crustaceans',
               'laboratory knockout of circatidal clock genes in amphipod')[0],
               'possible_clock_lab')
        self.assertEqual(m.triage_title_abstract('CRAB bacteremia',
                'carbapenem resistant acinetobacter clinical antibiotic resistance')[0],
                'unrelated')

    def test_study_literature_queries_with_original_abstract_source_then_clean_export(self):
        r={'title':'GPS tidal and diel bird activity',
             'doi':'https://doi.org/10.1000/XYZ',
             'pmid':'1223344','pubYear':'2018',
             'journalTitle':'Ecology',
             'abstractText':'<p>Field sampling of shorebird foraging and habitat use across day and night tidal phases</p>'}
        z=m.sanitize_source_record(r,'2015_2019','shorebirds')
        self.assertEqual(z['doi'],'10.1000/xyz')
        self.assertEqual(z['id'],'doi:10.1000/xyz')
        self.assertEqual(z['year'],2018)
        self.assertIn('Field sampling',z['abstract_excerpt'])
        self.assertIn('tidal phases',z['_screen_text'])

    def test_197_source_provenance_and_correct_DOI_dedup_and_preprint_caution(self):
        prev=old_197()
        new=[{'id':'doi:10.1200/example42','doi':'10.1200/example42',
               'pmid':'5042','title':'Old paper 42','year':2002,
               'journal':'test','abstract_excerpt':'one','_screen_text':'New field tide day shorebird movement',
               'discovery_queries':['1970_1999:shorebirds']},
             {'id':'doi:10.1000/independent','doi':'10.1000/independent',
               'pmid':'333','title':'Different field tide paper','year':2023,
               'journal':'test','abstract_excerpt':'two','_screen_text':'Tide and diel fish study',
               'discovery_queries':['2020_2024:fish']}]
        out,proof=m.merge_with_old(prev,new)
        self.assertEqual(len(out),198)
        self.assertEqual(proof['v131_seed_count'],197)
        self.assertEqual(proof['v132_records_matching_existing_or_new_query_entries'],1)
        original=next(x for x in out if x['id']=='doi:10.1200/example42')
        self.assertEqual(original['discovery_queries'],['1970_1999:shorebirds','v131_seed_197'])
        self.assertIn('one',original['abstract_excerpt'])

    def test_no_197_proof_misreported_as_independent_effects(self):
        p=old_197()
        p['analysis']='FAKE_SOURCE'
        with self.assertRaisesRegex(ValueError,'PREVIOUS_V131'):
            m.merge_with_old(p,[])
        p=old_197()
        p['literature_search_metadata_candidates_only']['metadata_only_candidate_citations'].pop()
        with self.assertRaisesRegex(ValueError,'OLD_197'):
            m.merge_with_old(p,[])

    def test_review_theory_distinct_from_field(self):
        a=m.triage_title_abstract('Review of circatidal clocks in crabs',
                 'A review of circatidal and lunar rhythms in crustaceans')
        self.assertEqual(a[0],'possible_review_theory')
        b=m.triage_title_abstract('Ocean oyster reef biodiversity',
                'Metadata about intertidal restoration')
        self.assertIn(b[0],('uncertain_relevance','unrelated'))

if __name__=='__main__': unittest.main()
