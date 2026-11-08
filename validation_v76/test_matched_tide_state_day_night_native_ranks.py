"""v76 synthetic 2010 source label and matched tide day/night ordinal rank tests."""
import unittest
from datetime import datetime,timedelta

import numpy as np

from matched_tide_state_day_night_native_ranks import (
    tide_light_source_groups,score_matched_tide_day_night,
    _aggregate_original_bird_months,PRIMARY_BIN_METRES,TWILIGHT_DEGREES)

def mock_real_shape(*,high_night=True):
    """Fictional original-shaped bird/month/phase, NO actual bird records."""
    out={}
    expo=np.linspace(0,1,500)
    birds=[f"SYNTHETIC_TEST_BIRD_{i}" for i in range(5)]
    for m in (8,9,10,11,12):
        fixes=[]
        closest=[]
        allcells=list(range(500))
        circles=[]
        for bird in birds:
            for i in range(48):
                # Each tidal state 12 original-shaped fixes: six before
                # solar daylight and six after, for both ebb and flood.
                is_night=i%12>=6
                fixes.append((bird,
                    datetime(2010,m,10)+timedelta(hours=i),
                    53.45,6.0))
                good=450 if high_night else 50
                bad=50 if high_night else 450
                closest.append(good if is_night else bad)
                circles.append(allcells)
        n=len(fixes)
        out[m]={
            "source_receipt":{"fixed_source_admission":
                "SOURCE_ADMITTED_V75_ORIGINAL_GPS_2010_MONTH_NATIVE_MODEL_1KM"},
            "fixes":fixes,
            "valid":np.ones(n,dtype=bool),
            "valid_birds":set(birds),
            "closest":np.asarray(closest,dtype=int),
            "circles":circles,
            "model_expo":expo}
    def tide_sun_label(bird,month,index):
        case=(index%48)//12
        is_night=index%12>=6
        phase=1 if case%2 else -1
        height=.1 if case//2==0 else .3
        return height,phase,"NIGHT" if is_night else "DAY"
    return out,tide_sun_label

class SameBirdSameTideNativeSolarKnownTruth(unittest.TestCase):
    def test_original_tide_phase_and_height_source_gate_synthetic(self):
        src,lab=mock_real_shape()
        paired,qa=tide_light_source_groups(src,None,
            height_bin=.2,synthetic_labels=lab)
        self.assertTrue(qa["admission"].startswith("SOURCE_ADMITTED"))
        self.assertEqual(qa["original_distinct_birds_in_tide_matched_groups"],5)
        self.assertEqual(qa["original_distinct_months_in_paired_conditions"],5)
        self.assertEqual(qa["original_paired_condition_groups_ge5_day_and_night"],100)
        self.assertEqual(qa["original_genuine_night_GPS_positions_in_matched_tide_conditions"],600)
        self.assertEqual(qa["original_genuine_day_GPS_positions_in_matched_tide_conditions"],600)
        self.assertEqual(qa["original_physical_RWS_ebb_strata"],50)
        self.assertEqual(qa["original_physical_RWS_flood_strata"],50)
        self.assertTrue(qa["no_model_index_or_next_heading_used_in_pair_matching"])
        self.assertNotIn("SYNTHETIC_TEST_BIRD_",str(qa))

    def test_known_truth_positive_night_high_index_after_exact_tide_matching(self):
        src,lab=mock_real_shape(high_night=True)
        groups,qa=tide_light_source_groups(src,None,synthetic_labels=lab)
        r=score_matched_tide_day_night(groups,qa,src)
        main=r["primary_original_wild_same_bird_month_rws_tide_matched_ordinal_rank"]
        self.assertEqual(main["original_independent_birds"],5)
        self.assertEqual(main["original_bird_months_with_true_tide_day_night_match"],25)
        self.assertGreater(main["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"],.7)
        self.assertGreater(main["whole_original_bird_10000_bootstrap95"][0],.7)
        self.assertEqual(main["original_birds_with_night_higher"],5)
        self.assertTrue(main["frozen_exploratory_main_status"].startswith("EXPLORATORY_MATCHED_RWS_TIDE_NIGHT_HIGHER"))
        self.assertNotIn("SYNTHETIC_TEST_BIRD_",str(r))

    def test_known_truth_negative_synthetic_not_rescued(self):
        src,lab=mock_real_shape(high_night=False)
        groups,qa=tide_light_source_groups(src,None,synthetic_labels=lab)
        r=score_matched_tide_day_night(groups,qa,src)
        main=r["primary_original_wild_same_bird_month_rws_tide_matched_ordinal_rank"]
        self.assertLess(main["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"],-.7)
        self.assertLess(main["whole_original_bird_10000_bootstrap95"][1],-.7)
        self.assertIn("NIGHT_LOWER",main["frozen_exploratory_main_status"])

    def test_unmatched_day_night_source_stops_without_reading_model_ranks(self):
        src,_=mock_real_shape()
        def nightonly(bird,month,index):
            return (.1,1,"NIGHT")
        groups,qa=tide_light_source_groups(src,None,synthetic_labels=nightonly)
        self.assertEqual(qa["admission"],"NOT_ADMITTED_V76_TIDE_MATCHED_DAY_NIGHT_SOURCE")
        out=score_matched_tide_day_night(groups,qa,src)
        self.assertEqual(out["original_wild_day_night_exposure_rank_effect"],
                         "NOT_ESTIMATED_SOURCE_GATE")
        with self.assertRaisesRegex(ValueError,"UNFROZEN_MONTH"):
            tide_light_source_groups({8:src[8]},None,synthetic_labels=nightonly)

    def test_frozen_bins_clock_and_bird_clustering(self):
        self.assertEqual(PRIMARY_BIN_METRES,.2)
        self.assertEqual(TWILIGHT_DEGREES,3.)
        src,lab=mock_real_shape()
        with self.assertRaisesRegex(ValueError,"UNFROZEN_HEIGHT"):
            tide_light_source_groups(src,None,height_bin=.12,synthetic_labels=lab)
        with self.assertRaisesRegex(ValueError,"UNFROZEN_GPS"):
            tide_light_source_groups(src,None,shift_seconds=3600,synthetic_labels=lab)
        q=_aggregate_original_bird_months({
            "a":{8:[.1]*30,9:[.1]*30},"b":{8:[-.1]*20}},seed=100)
        self.assertEqual(q["original_independent_birds"],2)
        self.assertEqual(q["original_bird_months_with_true_tide_day_night_match"],3)
        self.assertAlmostEqual(q["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"],0)

if __name__=="__main__":
    unittest.main()
