"""v132 known-truth human-curated primary evidence matrix source/independence QA."""
import json
import unittest
from pathlib import Path
P=Path(__file__).with_name('curated_primary_ecological_evidence.json')

class PrimaryComparativeEvidenceTruth(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(P.read_text());self.studies=self.data['source_rows']
        self.by={z['id']:z for z in self.studies}

    def test_fifteen_primary_source_studies_have_provenance_not_pooled(self):
        self.assertEqual(self.data['global_meta_pooled_effect'],'NOT_ESTIMATED')
        self.assertEqual(self.data['version'],'v132-original-primary-evidence-matrix-1')
        self.assertEqual(len(self.studies),15)
        self.assertEqual(len({x['id'] for x in self.studies}),15)
        self.assertEqual(len({x['doi'] for x in self.studies if x['doi']}),14)
        self.assertTrue(all(x['published_source'].startswith('https://') and x['reason_no_pool'] for x in self.studies))
        self.assertTrue(all(x['coast_cluster'] and x['study_cluster'] and x['taxa'] and x['group'] for x in self.studies))

    def test_same_wadden_coast_two_knot_sources_and_vlieland_not_independent(self):
        for k in ('VLIE_OYST_2018','NL_RED_KNOT_2017','NL_RED_KNOT_2026'):
            self.assertEqual(self.by[k]['coast_cluster'],'WADDEN_NL')
        self.assertEqual(len({self.by[k]['coast_cluster'] for k in (
            'VLIE_OYST_2018','NL_RED_KNOT_2017','NL_RED_KNOT_2026')}),1)

    def test_second_study_has_two_portugal_wetlands_not_two_experiments(self):
        p=self.by['PORT_SPOON_2025']
        self.assertEqual(p['numeric']['tagus_feeding_interaction_deltaAICc'],10.28)
        self.assertEqual(p['numeric']['ria_feeding_additive_deltaAICc'],373.92)
        self.assertIn('same species',p['sample'] if 'same species' in p['sample'] else p['taxa']+' same species')
        self.assertIn('one original paper',p['sample'])

    def test_original_negative_controls_and_mixed_individual_results_not_discarded(self):
        a=self.by['FL_HORSESHOE_2024']
        self.assertAlmostEqual(a['numeric']['tide_beta']/a['numeric']['tide_se'],1.978/1.776)
        self.assertIn('not strongly',a['core_finding'])
        b=self.by['AK_SABLEFISH_2017']
        self.assertEqual(b['numeric']['individuals_tide_in_best'],3)
        self.assertEqual(b['numeric']['individuals_scored'],6)
        self.assertEqual(b['numeric']['group_tide_deltaAIC'],2.2)
        self.assertEqual(b['numeric']['group_tide_interaction_deltaAIC'],4.2)

    def test_opportunity_channels_diverse_and_comparability_guard(self):
        groups={x['group'] for x in self.studies}
        regions={x['region'] for x in self.studies}
        self.assertTrue({'shorebird','fish','crustacean','insect','mammal',
                         'multi_trophic','seabird','chelicerate'}<=groups)
        self.assertIn('Southern Ocean',regions)
        self.assertIn('Eastern Tropical Pacific',regions)
        self.assertIn('Northeast Atlantic',regions)
        self.assertIn('Southwest Pacific',regions)
        a=self.by['AUS_MUDCRAB_2023']
        self.assertEqual(a['numeric']['inactive_class_time_percent'],79)
        self.assertIn('low/incoming',a['core_finding'])
        self.assertIn('hour of day removed',a['core_finding'])

    def test_tide_only_and_theory_separate_from_tide_solar_field(self):
        self.assertIn('night impossible',self.by['USA_PLOVERS_2023']['solar'])
        self.assertIn('not factorially',self.by['USA_MARSH_2012']['solar'])
        self.assertIn('model-supported',self.by['FR_MIDGE_2025']['core_finding'])
        self.assertIn('not established',self.by['PAN_GHOSTCRAB_2022']['tide'])

if __name__=='__main__':unittest.main()
