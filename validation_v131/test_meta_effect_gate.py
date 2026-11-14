"""v131 synthetic meta arithmetic and strict non-independence gates.
All effects here are fabricated KNOWN TRUTHS; no wild animal meta claim.
"""
from __future__ import annotations
from copy import deepcopy
import unittest
import meta_effect_gate as g

def row(i,taxon,group,region='Atlantic',site=None,effect=.2,se=.05):
    return {'effect_id':f'test-{i}','study_id':f'study-{i}',
      'source_url':f'https://example.org/nonreal/{i}',
      'independent_coast_cluster':site or f'site-{i}',
      'taxon':taxon,'functional_group':group,
      'ocean_region':region,'endpoint_family':'movement',
      'metric':'cv_relative_skill',
      'effect':effect,'sampling_se':se,
      'original_effect_source_verified':True,
      'effect_estimate_status':'SOURCE_EXTRACTED'}

class GlobalIndependentSiteMetaKnownTruth(unittest.TestCase):
    def setUp(self):
        self.ex=[row(1,'A','bird','Atlantic',effect=.2),
                 row(2,'B','fish','Pacific',effect=.1),
                 row(3,'C','crab','Indian',effect=.3)]

    def test_empty_ledger_is_not_pooled(self):
        out=g.exploratory_dl_pool([])
        self.assertIsNone(out['pooled_effect'])
        self.assertEqual(out['scientific_status'],'NOT_ESTIMATED_EMPTY_EFFECT_LEDGER')

    def test_requires_real_effect_with_original_source_and_se(self):
        bad=deepcopy(self.ex[0]);bad['original_effect_source_verified']=False
        with self.assertRaisesRegex(g.EffectGateStop,'NOT_VERIFIED'):
            g.validate_effect_entry(bad)
        bad=deepcopy(self.ex[0]);bad['sampling_se']=0
        with self.assertRaisesRegex(g.EffectGateStop,'POSITIVE_SAMPLING_SE'):
            g.validate_effect_entry(bad)
        bad=deepcopy(self.ex[0]);bad['metric']='pooled_mse_and_oddsratio'
        with self.assertRaisesRegex(g.EffectGateStop,'NOT_COMPARABLE'):
            g.validate_effect_entry(bad)

    def test_repeated_birds_and_studies_on_same_coast_not_three_independent_units(self):
        repeated=[row(1,'A','bird',site='same-site'),
                  row(2,'B','fish',site='same-site'),
                  row(3,'C','crab',site='same-site')]
        out=g.exploratory_dl_pool(repeated)
        self.assertIsNone(out['pooled_effect'])
        self.assertIn('DUPLICATED_COAST',out['scientific_status'])
        self.assertEqual(out['gate']['unique_sites'],1)

    def test_three_coasts_two_functional_groups_three_taxa_admitted_only_synthetic(self):
        z=g.exploratory_dl_pool(self.ex,strict_three_oceans=True)
        self.assertAlmostEqual(z['pooled_effect'],.2)
        self.assertEqual(z['gate']['unique_coasts'],3)
        self.assertEqual(z['gate']['unique_taxa'],3)
        self.assertEqual(z['gate']['unique_ocean_regions'],3)
        self.assertTrue(z['gate']['admitted'])
        self.assertGreaterEqual(z['tau2_DL'],0.)
        self.assertIn('NOT_full_multilevel_phylogenetic_or_site_dependence_model',z)

    def test_mixed_behaviour_and_movement_not_pooled(self):
        rows=deepcopy(self.ex)
        rows[0]['endpoint_family']='classified_behavior'
        x=g.exploratory_dl_pool(rows)
        self.assertIsNone(x['pooled_effect'])
        self.assertIn('MIXED_NONCOMPARABLE_ENDPOINTS',x['scientific_status'])

    def test_three_sites_but_same_taxon_or_functional_group_not_global_claim(self):
        rows=deepcopy(self.ex)
        for x in rows:x['functional_group']='shorebird'
        x=g.exploratory_dl_pool(rows)
        self.assertIsNone(x['pooled_effect'])
        self.assertEqual(x['gate']['gates']['functional_groups_ge2'],False)

    def test_three_regions_required_only_when_stated_for_global_ocean_claim(self):
        rows=deepcopy(self.ex)
        for x in rows:x['ocean_region']='Atlantic'
        a=g.exploratory_dl_pool(rows,strict_three_oceans=True)
        self.assertIsNone(a['pooled_effect'])
        self.assertFalse(a['gate']['gates']['ocean_regions_ge3'])

    def test_dl_nonidentical_effects_yield_wider_heterogeneity(self):
        rows=deepcopy(self.ex)
        for x,effect in zip(rows,(-.6,.1,.8)):x['effect']=effect
        z=g.exploratory_dl_pool(rows)
        self.assertGreater(z['tau2_DL'],0.)
        lo,hi=z['approx_CI95_normal_not_final']
        self.assertLess(lo,z['pooled_effect'])
        self.assertGreater(hi,z['pooled_effect'])
        self.assertTrue(z['NOT_a_final_globally_generalizable_claim'])

if __name__=='__main__':unittest.main()
