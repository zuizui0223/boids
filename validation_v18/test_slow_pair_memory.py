"""v18 TR-to-CM future route memory known-truth tests, no real GPS read."""
import datetime as dt
import math
import unittest

import numpy as np
import slow_pair_memory as v


class SourceContract(unittest.TestCase):
    def test_original_author_hashes_and_independent_pairs(self):
        self.assertEqual(v.ORIGINAL_ZIP_SHA256,
            "8e3f588ae927ab196f8c9dc9eebc9146bf656b344e68db8ba5f3c20d49edc3dc")
        self.assertEqual(v.ORIGINAL_PAIRS,14)
        self.assertEqual(v.ORIGINAL_GPS_FILES,426)
        self.assertEqual(v.SHELLS,(250,500,750,1000,1250,1500,1750,2000))
        self.assertEqual(v.BOOTSTRAP_RESAMPLES,10000)

    def test_original_filename_predeclared_stage_and_site(self):
        a=v.file_identity("CM_trimmed/15-X40_Site_LH_pair_Nocheck_CM_2024-08-16 09:36:05.csv")
        self.assertEqual(a,("15-X40","LH","pair","CM","2024-08-16 09:36:05"))
        b=v.file_identity("CM_trimmed/19-C41_Site_SH_solo_Nocheck_TR_2024-06-16 13:41:11.csv")
        self.assertEqual(b,("19-C41","SH","solo","TR","2024-06-16 13:41:11"))
        self.assertIsNone(v.file_identity("subject_unknown.csv"))

    def test_strict_original_gps_utc_timestamp(self):
        self.assertEqual(v.original_time_utc("2024-08-16 09:36:05.2"),
                         dt.datetime(2024,8,16,9,36,5,200000))
        self.assertEqual(v.original_time_utc("2024-08-16T09:36:05"),
                         dt.datetime(2024,8,16,9,36,5))
        with self.assertRaises(ValueError):
            v.original_time_utc("NA")

    def test_site_projection_cannot_substitute_different_site(self):
        lon=v.LAT_LON_ORIGIN["LH"][1]
        lat=v.LAT_LON_ORIGIN["LH"][0]
        x,y=v.projected("LH",lat,lon)
        self.assertAlmostEqual(x,0.,places=9)
        self.assertAlmostEqual(y,0.,places=9)
        a=v.projected("SH",lat,lon)
        self.assertGreater(math.hypot(*a),1000.)

    def test_circular_angle_wrapping_and_empty_training(self):
        self.assertAlmostEqual(v.wrapped(2*math.pi-.10),-.10)
        self.assertAlmostEqual(v.mean_angle([math.pi-.1,-math.pi+.1]),math.pi)
        self.assertIsNone(v.mean_angle([]))


class PredictivePreRegistration(unittest.TestCase):
    def _known_truth(self):
        tracks={}
        pairs=[f"O{i}" for i in range(1,15)]
        for index,p in enumerate(pairs):
            for site in ("LH","SH"):
                offset=(index-6.5)*0.09+(0.6 if site=="LH" else -0.6)
                for birdindex in (0,1):
                    bird=f"B{index:02d}{birdindex}"
                    for t in range(3):
                        hist={s:offset+birdindex*.001 for s in v.SHELLS}
                        tracks[(p,bird,site,"solo","TR",f"{p}-{site}-{bird}-{t}-TR")]=hist
                    for t in range(2):
                        later={s:offset+birdindex*.001+(.003 if t else -.003) for s in v.SHELLS}
                        mode="pair" if t else "solo"
                        tracks[(p,bird,site,mode,"CM",f"{p}-{site}-{bird}-{t}-CM")]=later
        return tracks,pairs

    def test_historical_templates_dont_include_future_cm(self):
        world,pairs=self._known_truth()
        prior=v.build_historic_templates(world)
        altered={}
        for key,angles in world.items():
            altered[key]={s:(2.5 if key[4]=="CM" else a) for s,a in angles.items()}
        nextprior=v.build_historic_templates(altered)
        self.assertEqual(prior,nextprior)

    def test_fully_heldout_fourteen_pair_truth_generates_expected_gain(self):
        world,pairs=self._known_truth()
        result=v.score(world,pairs)
        self.assertEqual(result["status"],"EXPLORATORY_14_PAIR_FUTURE_CM_ROUTE_MEMORY_FORECAST")
        self.assertEqual(result["primary_pair_history"]["positive_independent_pairs"],14)
        self.assertGreater(result["primary_pair_history"]["equal_pair_mean_gain_rad2"],.015)
        self.assertEqual(result["secondary_individual_history"]["n_independent_pairs"],14)
        self.assertEqual(len(result["per_pair"]),14)
        self.assertEqual(result["total_matched_CM_tracks"],14*2*2*2)

    def test_failed_pair_is_not_selectively_dropped(self):
        world,pairs=self._known_truth()
        world={k:x for k,x in world.items() if not (k[0]=="O14" and k[4]=="CM")}
        result=v.score(world,pairs)
        self.assertEqual(result["status"],"NOT_ADMITTED_FROZEN_CM_ROUTE_SUPPORT")
        self.assertFalse(result["any_prediction_score_exported"])
        self.assertTrue(any(x["pair"]=="O14" for x in result["pair_support"]))

    def test_external_population_baseline_never_uses_test_pair(self):
        world,pairs=self._known_truth()
        person,group=v.build_historic_templates(world)
        prior=v.population_without_pair(group,"O01","LH",250)
        altered={}
        for k,angles in world.items():
            if k[0]=="O01" and k[4]=="TR":
                altered[k]={s:2.0 for s in angles}
            else:altered[k]=angles
        nextgroup=v.build_historic_templates(altered)[1]
        afterward=v.population_without_pair(nextgroup,"O01","LH",250)
        self.assertEqual(prior,afterward)

    def test_missing_personal_training_uses_pair_in_every_target(self):
        world,pairs=self._known_truth()
        world={k:x for k,x in world.items()
               if not(k[0]=="O3" and k[1].endswith("1") and k[4]=="TR")}
        result=v.score(world,pairs)
        self.assertEqual(result["status"],"EXPLORATORY_14_PAIR_FUTURE_CM_ROUTE_MEMORY_FORECAST")
        self.assertGreater(result["per_pair"]["O3"]["historical_no_self_template_fallback_shells"],0)


if __name__=="__main__":
    unittest.main()
