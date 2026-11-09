"""v86 known truth: binary GPS WMR mid/high class and true RWS tide×solar 4way.

All below are synthetic animals and habitat classifications, NEVER evidence
of real Wadden wild tidal ecology. Production source must first exactly
replay original v82 Schier 857/18/41734 and Ameland 381/10/19407.
"""
from __future__ import annotations

from collections import defaultdict
from unittest.mock import patch
import unittest

import numpy as np

import wild_tideflat_binary_fourway as b
from tide_solar_four_way_source_and_effect import ADMIT

TEST_MONTHS=(6,7,8)

def make_fake_original_shape_sites(schier_mode="positive",ameland_mode="none",
                                   animal_count=8):
    """Full true source form, synthetic GPS indices never real Wadden data."""
    sites={}
    geo={}
    class_source={}
    expected={}
    # WMR native source synthetic classes 0/3/4 only
    classes=np.zeros(50,dtype=np.uint8)
    classes[3]=3
    classes[4]=4
    for site,mode in (("Schier",schier_mode),("Ameland",ameland_mode)):
        source=defaultdict(list)
        four={}
        n=0
        counts={"ebb_DAY":0,"ebb_NIGHT":0,"flood_DAY":0,"flood_NIGHT":0}
        for month in TEST_MONTHS:
            closest=[]
            for animal in range(animal_count):
                for height in range(5):
                    phases={}
                    for phase in (-1,+1):
                        vals={}
                        for light in ("DAY","NIGHT"):
                            positions=[]
                            for j in range(5):
                                idx=len(closest)
                                positions.append((month,idx))
                                key=("flood" if phase==1 else "ebb")+"_"+light
                                counts[key]+=1
                                if mode=="positive":
                                    allow=(phase==+1 and light=="NIGHT")
                                elif mode=="negative":
                                    allow=(phase==-1 and light=="NIGHT")
                                elif mode=="both_night_equal":
                                    allow=(light=="NIGHT")
                                elif mode=="none":
                                    allow=False
                                elif mode=="mid_vs_high":
                                    allow=(light=="NIGHT")
                                else:
                                    raise AssertionError("unknown synthetic mode")
                                ix=3 if allow else 7
                                closest.append(ix)
                            vals[light]=positions
                        phases[phase]=vals
                    four[(f"SYNTHETIC_ANIMAL_{animal}",month,height)]=phases
            source[month]={"closest":np.asarray(closest,dtype=int)}
        metadata={
            "all_four_conditions_same_real_bird_month_height_source":{
                "admission":ADMIT,
                "original_birds_in_all_four_tide_and_light_conditions":animal_count,
                "original_four_way_source_fix_count":
                    len(four)*4*5}}
        sites[site]=(four,metadata)
        geo[site]=source
        class_source[site]={"class":classes.copy()}
        expected[site]=(len(four),animal_count,len(four)*4*5)
    return sites,geo,class_source,expected

class GPSBinaryTideflatFourwayKnownTruth(unittest.TestCase):
    def test_frozen_real_source_census_is_old_v82_not_failed_v85(self):
        self.assertEqual(b.FROZEN_SOURCE_REAL_2010["Schier"],(857,18,41734))
        self.assertEqual(b.FROZEN_SOURCE_REAL_2010["Ameland"],(381,10,19407))
        self.assertEqual(b.MIN_CLASS4_SOURCE_GPS_FIXES,100)
        self.assertEqual(b.ORIGINAL_NATIVE_SOURCE_CELLS,398520)
        self.assertEqual(b.BOOT,10000)

    def test_no_Y_read_when_old_bird_tide_sun_full_source_drifted(self):
        sites,geo,classes,expected=make_fake_original_shape_sites()
        with patch.dict(b.FROZEN_SOURCE_REAL_2010,expected,clear=True):
            q=b.hard_before_outcome_both_sites(sites)
        self.assertEqual(q["Schier"]["original_identified_real_birds_in_source"],8)
        self.assertNotIn("SYNTHETIC_ANIMAL_",str(q))
        sites["Ameland"][1]["all_four_conditions_same_real_bird_month_height_source"][
            "original_four_way_source_fix_count"]-=1
        with patch.dict(b.FROZEN_SOURCE_REAL_2010,expected,clear=True):
            with self.assertRaisesRegex(ValueError,"ORIGINAL_V82_2010_RWS_SOLAR_SOURCE_DRIFT"):
                b.score_binary_original_two_sites_if_source_gated(
                    sites,geo,classes)

    def test_true_original_bird_4way_source_positive_and_negative_site_by_site(self):
        sites,geo,classes,expected=make_fake_original_shape_sites(
            schier_mode="positive",ameland_mode="negative")
        with patch.dict(b.FROZEN_SOURCE_REAL_2010,expected,clear=True),\
             patch.object(b,"ORIGINAL_NATIVE_SOURCE_CELLS",50):
            q=b.score_binary_original_two_sites_if_source_gated(sites,geo,classes)
        s=q["binary_mid_high_2010_true_wild_RWS_tidal_solar_by_site"]["Schier"]
        a=q["binary_mid_high_2010_true_wild_RWS_tidal_solar_by_site"]["Ameland"]
        v=s["primary_binary_GPS_position_in_intertidal_probability_D"]
        self.assertAlmostEqual(
            v["site_original_true_bird_equal_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY"],1.0)
        self.assertTrue(all(abs(z-1.0)<1e-10 for z in v["true_bird_10000_bootstrap95"]))
        self.assertEqual(v["original_birds_positive_D"],8)
        self.assertIn("POSITIVE",v["fixed_exploratory_class_status"])
        w=a["primary_binary_GPS_position_in_intertidal_probability_D"]
        self.assertAlmostEqual(
            w["site_original_true_bird_equal_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY"],-1.0)
        self.assertIn("NEGATIVE",w["fixed_exploratory_class_status"])
        c=q["main_binary_mid_high_GPS_position_two_site_bird_cluster_CONTRAST"]
        self.assertAlmostEqual(c["Schier_bird_equal_minus_Ameland_bird_equal"],2.0)
        self.assertNotIn("SYNTHETIC_ANIMAL_",str(q))
        self.assertEqual(q["secondary_high_littoral4_only_if_source_100GPS_each"][
            "status"],"ORIGINAL_WMR_NATIVE_HIGH_ONLY_GPS_SOURCE_TOO_SPARSE")

    def test_positive_night_in_both_phases_does_NOT_imply_tidal_interaction(self):
        sites,geo,classes,expected=make_fake_original_shape_sites(
            schier_mode="both_night_equal",ameland_mode="both_night_equal")
        with patch.dict(b.FROZEN_SOURCE_REAL_2010,expected,clear=True),\
             patch.object(b,"ORIGINAL_NATIVE_SOURCE_CELLS",50):
            q=b.score_binary_original_two_sites_if_source_gated(sites,geo,classes)
        for site in ("Schier","Ameland"):
            z=q["binary_mid_high_2010_true_wild_RWS_tidal_solar_by_site"][site]
            main=z["primary_binary_GPS_position_in_intertidal_probability_D"]
            self.assertAlmostEqual(
                main["site_original_true_bird_equal_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY"],0)
            self.assertEqual(
                main["fixed_exploratory_class_status"],
                "WMR_MIDHIGH_TIDE_BY_SOLAR_POSITION_FOURWAY_NOT_ESTABLISHED")
            self.assertAlmostEqual(
                z["secondary_same_4way_sample_separate_ebb_night_minus_day"][
                    "original_bird_mean"],1)
            self.assertAlmostEqual(
                z["secondary_same_4way_sample_separate_flood_night_minus_day"][
                    "original_bird_mean"],1)

    def test_binary_source_class_and_bird_month_nesting_no_invalid_model_index(self):
        sites,geo,classes,expected=make_fake_original_shape_sites()
        with patch.object(b,"ORIGINAL_NATIVE_SOURCE_CELLS",50):
            with self.assertRaisesRegex(ValueError,"WRONG_PINNED"):
                b._score_original_site("Schier",sites["Schier"][0],
                    geo["Schier"],np.full(50,2,dtype=np.uint8))
            with self.assertRaisesRegex(ValueError,"UNREGISTERED"):
                b._score_original_site("Schier",sites["Schier"][0],
                    geo["Schier"],classes["Schier"]["class"],
                    positive_codes=(2,))
            old=int(geo["Schier"][6]["closest"][0])
            geo["Schier"][6]["closest"][0]=51
            with self.assertRaisesRegex(ValueError,"BAD_GPS_TO_NIOZ"):
                b._score_original_site("Schier",sites["Schier"][0],
                    geo["Schier"],classes["Schier"]["class"])
            geo["Schier"][6]["closest"][0]=old

    def test_bird_bootstrap_not_gps_pseudoreplication(self):
        sample=b._real_bird_aggregate({
            "animal_A":{6:[+.4]*300,7:[+.4]},
            "animal_B":{6:[-.4]*10},
            "animal_C":{6:[0]*10}})
        self.assertEqual(len(sample),3)
        self.assertAlmostEqual(sample.mean(),0.)
        assert all(abs(z-.5)<1e-10 for z in b._boot_site(np.array([.5]*8)))
        self.assertEqual(b._boot_site(np.array([0]*8)),[0.,0.])

if __name__=="__main__":
    unittest.main()
