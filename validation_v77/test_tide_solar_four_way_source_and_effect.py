"""v77 synthetic four-condition flood/ebb×day/night original-shape known truth.

Known-truth means no wild GPS, no real tide or claimed ecology.
"""
from __future__ import annotations
from collections import defaultdict
import unittest
import numpy as np

from tide_solar_four_way_source_and_effect import (
    ADMIT,MIN_FOUR_WAY_STRATA,fourway_source_only,
    score_fourway_difference_in_differences)

def make_source(mode="positive",*,bird_count=8,months=(8,9,10),bands=5):
    paired={}
    position={}
    modeled=np.linspace(0,1,101)
    allcells=list(range(len(modeled)))
    for month in months:
        position[month]={"closest":[],"circles":[],
                         "model_expo":modeled}
        for bird in range(bird_count):
            for b in range(bands):
                for phase in (-1,1):
                    vals={}
                    for light in ("DAY","NIGHT"):
                        refs=[]
                        for repeat in range(5):
                            ix=len(position[month]["closest"])
                            refs.append((month,ix))
                            if light=="DAY":
                                rank=.20
                            elif mode=="positive":
                                rank=.85 if phase==1 else .40
                            elif mode=="negative":
                                rank=.30 if phase==1 else .90
                            elif mode=="both_positive_equal":
                                rank=.80
                            else:
                                raise ValueError("Bad synthetic mode")
                            position[month]["closest"].append(round(rank*100))
                            position[month]["circles"].append(allcells)
                        vals[light]=refs
                    paired[(f"SYNTHETIC_BIRD_{bird}",month,phase,b)]=vals
        position[month]["closest"]=np.asarray(position[month]["closest"],dtype=int)
    qa={"admission":"SOURCE_ADMITTED_V76_ORIGINAL_REAL_SAME_BIRD_MONTH_TIDE_STATE",
        "true_RWS_height_bin_metres":.2}
    return paired,qa,position

class FourCellTideXLightTests(unittest.TestCase):
    def test_source_complete_foursomes_with_real_bird_month_height_grain(self):
        pairs,qa,positions=make_source()
        selected,source=fourway_source_only(pairs,qa,verify_original_replay=False)
        self.assertEqual(source["admission"],ADMIT)
        self.assertEqual(len(selected),120)
        self.assertEqual(source["original_birds_in_all_four_tide_and_light_conditions"],8)
        self.assertEqual(source["original_2010_months_with_complete_four_way_conditions"],3)
        self.assertEqual(source["original_four_way_source_fix_count"],2400)
        self.assertEqual(source["original_source_GPS_fix_counts_by_true_ebb_flood_and_astronomical_light"],
             {"ebb_day":600,"ebb_night":600,"flood_day":600,"flood_night":600})
        self.assertTrue(source["fixed_no_future_heading_or_monthly_used_model_index_for_source"])
        self.assertNotIn("SYNTHETIC_BIRD_",str(source))

    def test_positive_four_way_interaction_genuinely_tested_not_assumed(self):
        pairs,qa,positions=make_source("positive")
        selected,source=fourway_source_only(pairs,qa,verify_original_replay=False)
        result=score_fourway_difference_in_differences(selected,source,positions)
        main=result["original_2010_Schier_RWS_tide_phase_by_astro_light_interaction"][
            "frozen_primary_genuine_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY"]
        self.assertEqual(main["original_independent_birds"],8)
        self.assertEqual(main["original_bird_months_with_true_tide_day_night_match"],24)
        self.assertGreater(main["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"],.40)
        self.assertGreater(main["whole_original_bird_10000_bootstrap95"][0],.40)
        self.assertEqual(main["original_birds_with_night_higher"],8)
        self.assertTrue(result["original_2010_Schier_RWS_tide_phase_by_astro_light_interaction"][
            "frozen_exploratory_primary_status"].startswith("EXPLORATORY_POSITIVE"))
        self.assertNotIn("SYNTHETIC_BIRD_",str(result))

    def test_negative_four_way_interaction_not_rescued_by_positive_night_effect(self):
        pairs,qa,positions=make_source("negative")
        selected,source=fourway_source_only(pairs,qa,verify_original_replay=False)
        result=score_fourway_difference_in_differences(selected,source,positions)
        main=result["original_2010_Schier_RWS_tide_phase_by_astro_light_interaction"][
            "frozen_primary_genuine_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY"]
        self.assertLess(main["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"],-.4)
        self.assertLess(main["whole_original_bird_10000_bootstrap95"][1],-.4)
        self.assertIn("NEGATIVE",result["original_2010_Schier_RWS_tide_phase_by_astro_light_interaction"][
            "frozen_exploratory_primary_status"])

    def test_no_interaction_despite_positive_night_main_in_both_phases(self):
        pairs,qa,positions=make_source("both_positive_equal")
        selected,source=fourway_source_only(pairs,qa,verify_original_replay=False)
        result=score_fourway_difference_in_differences(selected,source,positions)
        main=result["original_2010_Schier_RWS_tide_phase_by_astro_light_interaction"][
            "frozen_primary_genuine_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY"]
        self.assertAlmostEqual(main["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"],0.)
        self.assertEqual(result["original_2010_Schier_RWS_tide_phase_by_astro_light_interaction"][
            "frozen_exploratory_primary_status"],
            "FOUR_WAY_TIDE_LIGHT_INTERACTION_NOT_ESTABLISHED")
        self.assertGreater(result["secondary_same_four_way_sample_separate_night_day_effect"][
            "measured_RWS_ebb"]["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"],.5)

    def test_underpowered_and_incomplete_original_tide_class_must_not_score(self):
        pairs,qa,positions=make_source()
        few={k:v for k,v in pairs.items() if k[0] in
            (f"SYNTHETIC_BIRD_{i}" for i in range(4))}
        selected,source=fourway_source_only(few,qa,verify_original_replay=False)
        self.assertIn("NOT_ADMITTED",source["admission"])
        result=score_fourway_difference_in_differences(selected,source,positions)
        self.assertEqual(result["flood_minus_ebb_of_NIGHT_minus_DAY"],
                         "NOT_ESTIMATED_SOURCE_GATE")
        onephase={k:v for k,v in pairs.items() if k[2]==1}
        selected,source=fourway_source_only(onephase,qa,verify_original_replay=False)
        self.assertEqual(len(selected),0)
        self.assertIn("NOT_ADMITTED",source["admission"])

    def test_unmodified_2010_v76_source_counts_must_replay_before_real_effect(self):
        pairs,qa,positions=make_source()
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP_V77"):
            fourway_source_only(pairs,qa,verify_original_replay=True)
        self.assertGreaterEqual(MIN_FOUR_WAY_STRATA,100)

if __name__=="__main__":
    unittest.main()
