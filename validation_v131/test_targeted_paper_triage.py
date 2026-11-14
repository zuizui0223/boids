"""Additional v131 source triage audit; no empirical global effects computed."""
import json
import unittest
from collections import Counter
from pathlib import Path

PAPERS=Path(__file__).with_name('targeted_paper_triage.json')
class TargetedGlobalLiteratureSourceTruth(unittest.TestCase):
    def setUp(self):
        self.x=json.loads(PAPERS.read_text())
        self.papers=self.x['papers']
    def test_source_triage_contains_not_meta_results_and_unique_papers(self):
        self.assertEqual(self.x['eligible_global_meta_effects_extracted'],0)
        self.assertEqual(len(self.papers),10)
        self.assertEqual(len({x['doi'] for x in self.papers}),10)
        self.assertTrue(all(x.get('source_url') for x in self.papers))
        self.assertTrue(all(x['global_effect_extracted'] is False for x in self.papers))
    def test_field_vs_lab_and_same_field_cohort_kept_separate(self):
        theory=[x for x in self.papers if x['evidence_arm'].startswith('theoretical_')]
        lab=[x for x in self.papers if x['evidence_arm'].startswith('laboratory_')]
        self.assertEqual(len(theory),1)
        self.assertEqual(len(lab),1)
        fr=[x for x in self.papers if x['id'] in (
          'EKREM_2025_CLUNIO_TIMESPACE','JACOBSEN_2026_CLUNIO_THEORY')]
        self.assertEqual(fr[0]['independence_cluster'],fr[1]['independence_cluster'])
        self.assertTrue('field' in fr[0]['evidence_arm'])
    def test_no_florida_plover_morning_only_as_tide_solar_meta(self):
        study=next(x for x in self.papers if x['id']=='FLORIDA_PLOVERS_2023')
        self.assertIn('exclude from primary',study['tide_solar_status'])
        self.assertEqual(len(study['secondary_effects_published_only']),3)
        self.assertTrue(all(e['beta_tide_standardized']<0 and e['se']>0
                            for e in study['secondary_effects_published_only']))
        self.assertIn('38',study['source_n'])
    def test_cross_taxon_and_regions_not_mistaken_for_replicated_effects(self):
        groups={x['functional_group'] for x in self.papers}
        regions={x['region'] for x in self.papers}
        self.assertTrue({'shorebird','fish','crustacean','intertidal_insect',
                         'terrestrial_coastal_mammal'}<=groups)
        self.assertIn('Eastern Tropical Pacific',regions)
        self.assertIn('Northwest Pacific',regions)
        self.assertIn('Northeast Pacific',regions)
        self.assertEqual(sum(x['global_effect_extracted'] for x in self.papers),0)
        mammal=next(x for x in self.papers if x['id']=='GOLDSBOROUGH_2023_CAPUCHIN')
        self.assertEqual(mammal['meta_endpoint_family'],'camera_detection')

if __name__=='__main__':unittest.main()
