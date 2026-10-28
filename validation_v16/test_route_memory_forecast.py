"""v16 slow independent future-release navigation test (synthetic fixtures only)."""
from __future__ import annotations
import datetime
import json
import math
import unittest
import numpy as np
import route_memory_forecast as v


class OriginalSourceContract(unittest.TestCase):
    def test_frozen_primary_parameters_and_source_identity(self):
        self.assertEqual(v.ORIGINAL_SHA256,"7380feccd8c2e4e1675679411d1ee8075cd29ccbd2dada98e317ca88053ffbfa")
        self.assertEqual(v.HISTORIC_RELEASES,(5,6,7,8))
        self.assertEqual(v.SHELLS,tuple(range(500,4501,500)))
        self.assertEqual(v.MAX_CROSSING_OVERSHOOT_M,50.)
        self.assertEqual(v.MIN_TEST_RELEASES_PER_FLOCK,3)
        self.assertEqual(len(v.REQUIRED_FLOCKS),8)

    def test_original_qstarz_utc_date_time_ms(self):
        t=v.parse_date_clock_ms({"UTC DATE":"2016/7/1","UTC TIME":"9:2:3","MS":"200"})
        expected=datetime.date(2016,7,1).toordinal()*86_400_000+(9*3600+2*60+3)*1000+200
        self.assertEqual(t,expected)
        with self.assertRaises(ValueError):
            v.parse_date_clock_ms({"UTC DATE":"2016/7/1","UTC TIME":"9:2:3","MS":"1000"})

    def test_coordinate_hemisphere_and_invalid_row(self):
        row={"VALID":"FIXED","UTC DATE":"2016/7/1","UTC TIME":"9:2:3",
             "MS":"200","LATITUDE":str(v.LAT0),"N/S":"N",
             "LONGITUDE":str(abs(v.LON0)),"E/W":"W"}
        t,x,y=v.original_row_xy_t(row)
        self.assertAlmostEqual(x,0.,places=6)
        self.assertAlmostEqual(y,0.,places=6)
        self.assertIsNone(v.original_row_xy_t({**row,"VALID":"INVALID"}))
        self.assertIsNone(v.original_row_xy_t({**row,"MS":"NaN"}))

    def test_first_outward_crossing_only_no_interpolation(self):
        records=[(1000,0.,0.),(1200,0.,496.),(1400,0.,503.),
                 (1600,0.,520.),(1800,0.,499.),(2000,0.,505.)]
        ans=v.first_shell_crossings(records)
        self.assertIn(500,ans)
        self.assertAlmostEqual(ans[500],0.)
        self.assertEqual(len(ans),1)

    def test_unrealistic_teleport_cannot_be_crossing(self):
        records=[(1000,0.,0.),(1200,0.,504.)]
        self.assertEqual(v.first_shell_crossings(records),{})

    def test_discontinuous_missing_fix_prevents_fabricated_crossing(self):
        records=[(1000,0.,499.),None,(1400,0.,502.)]
        self.assertEqual(v.first_shell_crossings(records),{})


class PredictiveStructure(unittest.TestCase):
    def _world(self):
        t={}
        for f,flock in enumerate(v.REQUIRED_FLOCKS):
            offset=(f-3.5)*.12
            for bird_idx in range(5):
                bird=f"B{bird_idx}"
                for release in range(5,16):
                    for_shell={}
                    for shell in v.SHELLS:
                        # Entirely artificial, no wild data: group memory should win.
                        for_shell[shell]=offset + bird_idx*.004 + math.sin(release)*.002
                    t[(flock,bird,release)]=for_shell
        return t

    def test_group_template_does_not_read_future_release(self):
        world=self._world()
        individual,flock=v.training_templates(world)
        changed=dict(world)
        for key in world:
            if key[2]>=9:
                changed[key]={s:math.pi for s in v.SHELLS}
        individual2,flock2=v.training_templates(changed)
        self.assertEqual(individual,individual2)
        self.assertEqual(flock,flock2)

    def test_group_history_beats_other_flocks_in_known_truth(self):
        result=v.evaluate_routes(self._world())
        self.assertTrue(result["all_8_flocks_admitted"])
        self.assertEqual(result["status"],"EXPLORATORY_INDEPENDENT_8_FLOCKS_REPEATED_ROUTE_FORECAST")
        self.assertEqual(result["flock_primary"]["positive_flocks"],8)
        self.assertGreater(result["flock_primary"]["equal_flock_mean"],.03)
        self.assertEqual(result["flock_primary"]["n_flc"],8)

    def test_all_eight_flocks_must_be_admitted(self):
        world={k:v for k,v in self._world().items() if k[0]!="08"}
        r=v.evaluate_routes(world)
        self.assertEqual(r["status"],"NOT_ADMITTED_8_FLOCKS_INCOMPLETE")
        self.assertNotIn("per_flock",r)
        self.assertEqual(r["per_flock_structural_result"]["08"]["matched_future_bird_release_shells"],0)

    def test_individual_fallback_on_unsupported_historic_only(self):
        world=self._world()
        # Add an individual after training only, with no historical self data.
        for release in range(9,16):
            world[("01","X99",release)]={shell:.5 for shell in v.SHELLS}
        r=v.evaluate_routes(world)
        self.assertTrue(r["all_8_flocks_admitted"])
        self.assertGreater(r["per_flock"]["01"]["individual_template_backoff_target_count"],0)

    def test_circular_wrap_at_zero_and_two_pi(self):
        self.assertAlmostEqual(v.wrap(2*math.pi+.05),.05)
        self.assertAlmostEqual(v.wrap(-2*math.pi-.05),-.05)
        self.assertAlmostEqual(v.mean_direction([math.pi-.1,-math.pi+.1]),math.pi)


if __name__=="__main__":
    unittest.main()
