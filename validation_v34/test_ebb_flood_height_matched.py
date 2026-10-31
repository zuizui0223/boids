"""v34 invented known-truth: no original animal movement or tide outcomes."""
import datetime as dt
import json
import math
import unittest
import ebb_flood_height_matched as m

class KnownTruth(unittest.TestCase):
    def test_fixed_source_physics_and_half_meter_negative_bin(self):
        self.assertEqual(m.tide.STATION,"schiermonnikoog.waddenzee")
        self.assertEqual(m.HALF_HEIGHT_BIN_M,.5)
        self.assertEqual(m.SLOPE_HALF_WINDOW_MINUTES,30)
        self.assertEqual(m.height_bin(.5),1)
        self.assertEqual(m.height_bin(-.01),-1)
        self.assertEqual(m.height_bin(-.5),-1)
        self.assertEqual(m.height_bin(-.51),-2)
    def test_flood_rising_ebb_falling_at_same_original_level(self):
        center=dt.datetime(2010,5,1,11,40)
        series={center:.1,center-dt.timedelta(minutes=30):-.2,
                center+dt.timedelta(minutes=30):.4}
        self.assertEqual(m.astronomical_phase(center,series)[0],"flood")
        series[center-dt.timedelta(minutes=30)]=.4
        series[center+dt.timedelta(minutes=30)]=-.2
        self.assertEqual(m.astronomical_phase(center,series)[0],"ebb")
        series[center+dt.timedelta(minutes=30)]=.4
        self.assertEqual(m.astronomical_phase(center,series)[0],"turning")
        del series[center+dt.timedelta(minutes=30)]
        self.assertIsNone(m.astronomical_phase(center,series))
    def test_duration_bins_and_frozen_thresholds(self):
        self.assertEqual(m.fixed_duration_bin(5),"short_5_30")
        self.assertEqual(m.fixed_duration_bin(29.99),"short_5_30")
        self.assertEqual(m.fixed_duration_bin(30),"medium_30_90")
        self.assertEqual(m.fixed_duration_bin(89.99),"medium_30_90")
        self.assertEqual(m.fixed_duration_bin(90),"long_90_180")
        self.assertEqual(m.fixed_duration_bin(180),"long_90_180")
        with self.assertRaises(ValueError):m.fixed_duration_bin(181)
    def test_original_pairs_source_level_strict_UTC_and_geo(self):
        t=dt.datetime(2010,5,1,11)
        bird="private-animal"
        loc=(53.468937,6.202908)
        points=[(bird,t,*loc),(bird,t+dt.timedelta(minutes=10),53.469,6.205)]
        mid=t+dt.timedelta(minutes=5)
        key=m.phase.nearest_tide_key(mid)
        astro={key:.1,key-dt.timedelta(minutes=30):-.4,
               key+dt.timedelta(minutes=30):.4}
        g,qa=m.new_strata(points,astro)
        self.assertEqual(qa["valid_original_flood_pairs"],1)
        self.assertEqual(qa.get("valid_original_ebb_pairs",0),0)
        self.assertEqual(list(g.keys())[0][-2:],(0,"short_5_30"))
    def test_ebb_and_flood_matched_with_same_hour_height_and_duration(self):
        bird="secret-source"
        pts=[]
        astro={}
        # Every hour/minute category is fixed. Variations are across dates.
        for day in range(20):
            start=dt.datetime(2010,5,1,11)+dt.timedelta(days=day)
            pts.extend([(bird,start,53.468937,6.202908),
                        (bird,start+dt.timedelta(minutes=10),53.469,6.205 if day%2 else 6.204)])
            mid=start+dt.timedelta(minutes=5)
            t=m.phase.nearest_tide_key(mid)
            astro[t]=.1
            astro[t-dt.timedelta(minutes=30)]=(.4 if day%2 else -.4)
            astro[t+dt.timedelta(minutes=30)]=(-.4 if day%2 else .4)
        g,qa=m.new_strata(pts,astro)
        paired,support=m.matched_strata(g)
        self.assertEqual(support["paired_strata_admitted"],0) # only one matched stratum; bird gate is 8
        self.assertEqual(support["paired_strata_from_ineligible_birds"],1)
        self.assertEqual(qa["valid_original_flood_pairs"],10)
        self.assertEqual(qa["valid_original_ebb_pairs"],10)
    def test_bird_weighting_and_no_pseudoreplication(self):
        d={}
        for i in range(20):
            n=90 if i==0 else 10
            d[f"private-{i:02d}"]=[{
             "year":2010,"height_band":-1,"duration":"short_5_30",
             "n_ebb":2,"n_flood":2,
             "ebb_minus_flood_speed":1. if i==0 else -.1,
             "ebb_minus_flood_elapsed_minutes":2. if i==0 else -1.,
             "ebb_minus_flood_water_height_m":.01 if i==0 else -.005
             } for _ in range(n)]
        qa={"whole_birds_admitted":20,"paired_strata_admitted":280}
        result=m.summarize(d,qa)
        self.assertEqual(result["status"],"EXPLORATORY_MATCHED_EBB_FLOOD_MOVEMENT_HYSTERESIS")
        self.assertAlmostEqual(result["matched_estimands"]["PRIMARY_EBB_minus_FLOOD_log1p_speed"]["equal_bird_mean"],(1-1.9)/20)
        self.assertEqual(result["matched_estimands"]["PRIMARY_EBB_minus_FLOOD_log1p_speed"]["positive_birds"],1)
        self.assertEqual(result,m.summarize(d,qa))
        encoded=json.dumps(result)
        self.assertNotIn("private-",encoded)
        self.assertNotIn('"year":2010',encoded)
    def test_admission_stop_no_score(self):
        x=m.summarize({},{"whole_birds_admitted":0,"paired_strata_admitted":0})
        self.assertEqual(x["status"],"NOT_ADMITTED_EBB_FLOOD_HEIGHT_DUTY_MATCHED_SUPPORT")
        self.assertFalse(x["any_ebb_flood_effect_reported"])
        self.assertNotIn("matched_estimands",x)
    def test_immutable_original_D_replay_comparator(self):
        self.assertTrue(m.nested_close({"a":[.25,2]},{"a":[.25,2]}))
        self.assertFalse(m.nested_close({"a":[.25]},{"a":[.26]}))
if __name__=="__main__":
    unittest.main()
