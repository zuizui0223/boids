"""v91 synthetic original-group mixture identities and hard replay tests.

SYNTHETIC ecological responses below are mathematical source-known truths,
not new wild Wadden results or independent taxa/signed replication.
"""
from __future__ import annotations

from collections import defaultdict
from unittest.mock import patch
import unittest

import numpy as np

import two_stage_gps_tide_solar_mixture as v
from wild_tideflat_binary_fourway import _score_original_site
from two_island_common_month_bird_contrast import _private_original_bird_means

def fake_four_cell(*,all_outside=False):
    # A strong synthetic sign inversion: F-N p=.2, F-D p=.7,
    # E-N p=.5, E-D p=.4 -> D(p)=-.6. Extra +.3 in F-N
    # makes mean original NIOZ rank D(R)=+.12 although D(p)<0.
    proportions=(2,7,5,4)
    cells={}
    for (phase,light),n in zip(v.CELLS,proportions):
        y=np.array(([1]*n+[0]*(10-n)),int)
        if all_outside:y[:]=0
        base=np.where(y==1,.15,-.15)
        if phase==1 and light=="NIGHT":base=base+.3
        cells[(phase,light)]=(base,y)
    return cells

class EcologicalTwoStageObservedDataIdentityKnownTruth(unittest.TestCase):
    def test_frozen_original_RWS_source_and_old_effects(self):
        self.assertEqual(v.BOOTS,10000)
        self.assertEqual(v.SEED_NEW,20261109)
        self.assertEqual(v.SITES,("Schier","Ameland"))
        self.assertEqual(v.PRIOR_TRUE_2010["Schier"]["birds"],18)
        self.assertEqual(v.PRIOR_TRUE_2010["Ameland"]["groups"],381)
        self.assertEqual(v.PRIOR_TRUE_2010["Schier"]["D_flatP"] if
                         "D_flatP" in v.PRIOR_TRUE_2010["Schier"]
                         else v.PRIOR_TRUE_2010["Schier"]["D_binary"],
                         -0.0561556674)

    def test_known_truth_opposite_signs_exact_two_channel_identity(self):
        x=v.four_cell_original_identity(fake_four_cell())
        self.assertAlmostEqual(x["D_flatP"],-.6)
        self.assertAlmostEqual(x["D_rank"],.12)
        self.assertLess(x["D_entry"],0)
        self.assertGreater(x["D_resid"],0)
        self.assertAlmostEqual(x["D_entry"]+x["D_resid"],x["D_rank"])
        self.assertTrue(x["has_both_original_WMR_habitat_classes"])
        self.assertLess(x["max_exact_mixture_identity_residual"],1e-12)

    def test_only_one_habitat_category_cannot_create_fake_entry_contribution(self):
        x=v.four_cell_original_identity(fake_four_cell(all_outside=True))
        self.assertFalse(x["has_both_original_WMR_habitat_classes"])
        self.assertEqual(x["D_entry"],0)
        self.assertAlmostEqual(x["D_rank"],x["D_resid"])
        self.assertEqual(x["D_flatP"],0)

    def test_invalid_four_source_no_GPS_pseudoreplication_or_illegal_Y(self):
        d=fake_four_cell()
        del d[(1,"DAY")]
        with self.assertRaisesRegex(ValueError,"NOT_EXACT"):
            v.four_cell_original_identity(d)
        d=fake_four_cell()
        r,y=d[(1,"DAY")]
        d[(1,"DAY")]=(r,np.ones(len(y),dtype=int)*2)
        with self.assertRaisesRegex(ValueError,"INVALID_ORIGINAL"):
            v.four_cell_original_identity(d)

    def test_hierarchical_original_bird_months_equal_weight_not_GPS_count(self):
        a={
            "Original_Bird_A":{6:[{"D_rank":.2,"D_flatP":-.5,"D_entry":-.1,"D_resid":.3}]*100,
                               7:[{"D_rank":0,"D_flatP":0,"D_entry":0,"D_resid":0}]},
            "Original_Bird_B":{6:[{"D_rank":-.1,"D_flatP":.1,"D_entry":-.2,"D_resid":.1}]}}
        q=v._bird_hierarchy(a)
        self.assertEqual(len(q["D_rank"]),2)
        self.assertAlmostEqual(q["D_rank"][0],.1)
        self.assertAlmostEqual(q["D_rank"][1],-.1)
        self.assertAlmostEqual(q["D_rank"].mean(),0.)
        self.assertTrue(np.allclose(q["D_rank"],q["D_entry"]+q["D_resid"]))

    def test_strict_known_original_2010_old_rank_and_binary_replay_before_new_mixture(self):
        x=v.PRIOR_TRUE_2010["Schier"]
        mock_binary={
            "primary_binary_GPS_position_in_intertidal_probability_D":{
                "true_bird_10000_bootstrap95":list(x["D_binary_95"])}}
        with patch.object(v,"_private_original_bird_means",
                     return_value=np.ones(18)*x["D_rank"]),\
             patch.object(v,"_score_original_site",
                     return_value=(np.ones(18)*x["D_binary"],mock_binary)),\
             patch.object(v,"_site_bird_boot",
                     return_value=list(x["D_rank_95"])):
            four={("some_private_tag",6,i):{} for i in range(857)}
            q,ra,bi=v.original_site_old_outcome_replays(
                "Schier",four,{},np.zeros(398520,dtype=np.uint8))
            self.assertTrue(abs(q["D_rank"]-x["D_rank"])<1e-12)
        with patch.object(v,"_private_original_bird_means",
                     return_value=np.ones(18)*.20):
            with self.assertRaisesRegex(ValueError,"PRIOR_ORIGINAL"):
                v.original_site_old_outcome_replays(
                    "Schier",four,{},np.zeros(398520,dtype=np.uint8))

    def test_genuine_original_site_per_bird_decomposition_match_old_estimates(self):
        # A known toy version of the original 4-cell source (same fixed
        # identity but model index values and source WMR classes synthetic).
        expo=np.linspace(0,1,12)
        cls=np.zeros(398520,dtype=np.uint8)
        cls[[1,2,3,4]]=3
        closest=np.array([1,3,7,8,2,3,8,9],dtype=int)
        pre={6:{"closest":closest,"model_expo":expo,
                "circles":[list(range(12)) for _ in closest]}}
        four={
            ("synthetic_animal_one",6,0):{
                (1 if phase==1 else -1):{
                    "NIGHT":[(6,0 if phase==1 else 4),(6,1 if phase==1 else 5)],
                    "DAY":[(6,2 if phase==1 else 6),(6,3 if phase==1 else 7)]}
                for phase in (1,-1)}}
        source_r=_private_original_bird_means(four,pre)
        source_y,_=_score_original_site(
            "Schier",four,pre,cls,positive_codes=(3,4))
        values,summary=v.decompose_real_original_site(
            "Schier",four,pre,cls,source_r,source_y)
        self.assertEqual(len(values["D_rank"]),1)
        self.assertTrue(np.allclose(
            values["D_rank"],values["D_entry"]+values["D_resid"],
            atol=1e-12,rtol=0))
        self.assertLess(summary["source_max_per_fourcell_algebra_identity_error"],1e-12)
        self.assertNotIn("synthetic_animal_one",str(summary))

    def test_site_bird_component_bootstraps_independently(self):
        q=v._site_independent_bird_component_diff([+.2]*18,[-.1]*10)
        self.assertAlmostEqual(q["Schier_minus_Ameland_bird_conditional_difference"],.3)
        self.assertTrue(all(abs(t-.3)<1e-12 for t in
            q["whole_original_bird_separate_site_bootstrap95"]))
        z=v._site_independent_bird_component_diff(
            [+.1,-.1]*9,[+.1,-.1]*5)
        self.assertEqual(z["direction_status"],
                         "CONDITIONAL_SITE_DIFFERENCE_NOT_ESTABLISHED")

if __name__=="__main__":
    unittest.main()
