"""Synthetic known-truth for same-source one-hour persistence and B-day ghosts.

NEVER fetch original fish or NOAA data in these tests.
"""
from __future__ import annotations
import unittest
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v155_autopersistence_partner import (
    run_rows,score_pair,summarize,MODELS,PAIRS,MIN_TEST_HOURS
)

class TestOriginalNoLeakage(unittest.TestCase):
    def test_daily_complete_run_and_true_previous_source_hour(self):
        days=[tuple(range(24*i,24*(i+1))) for i in range(7)]
        positives={
            "Bocaccio":{23,24,25,26,3*24+10},
            "UF440":{3*24+10,6*24+10,10},
            "White Seabass":{10,5*24+10},
        }
        data=list(run_rows(days,positives))
        self.assertEqual(len(data),24*7-1)
        self.assertEqual(data[0][0],1)
        self.assertEqual(data[0][2],0)
        h24=next(r for r in data if r[0]==24)
        self.assertEqual(h24[2],1)  # yesterday hour 23 is a REAL observed target
        h10=next(r for r in data if r[0]==10)
        self.assertEqual(h10[3]["UF440"],1)
        self.assertEqual(h10[4]["UF440"][3],1) # day3, same original hour of day
        self.assertEqual(h10[4]["UF440"][5],0)
    def test_missing_day_is_not_filled_as_negatives(self):
        days=[tuple(range(24*i,24*(i+1))) for i in range(7)]
        broken=list(days)
        broken[3]=tuple(v+24 for v in broken[3]) # skip original day
        with self.assertRaises(AssertionError):
            list(run_rows(broken,{"Bocaccio":set()}))
    def test_holdout_source_lag_support_is_strict(self):
        n=2100
        yr=np.array([2019]*1500+[2020]*600)
        x={m:np.ones((n,2)) for m in MODELS if m!="constant"}
        y=np.zeros(n,dtype=np.int8)
        b=np.zeros(n,dtype=np.int8)
        r=score_pair(x,y,b,yr,2020)
        self.assertEqual(r["status"],"STOP_SOURCE_LAG_HOURS")
        self.assertEqual(r["heldout_hours"],600)
    def test_sites_not_independent_coasts(self):
        make=lambda site,x:{
            "site":site,
            "improvement_nats_per_original_hour":{
                "solar_over_constant":0.2,"tide_over_solar":0.0,
                "own_previous_1h_over_tide":0.1,
                "real_partner_over_own_previous":x,
                "wrong_partner_3d_over_own_previous":0.0,
                "wrong_partner_5d_over_own_previous":0.0,
                "real_partner_over_best_dayghost":x,
                "real_partner_over_constant":0.3+x,
            }
        }
        info=summarize([make("A",0.1),make("A",0.2),make("B",-0.3)])
        self.assertEqual(info["n_sites"],2)
        self.assertEqual(info["n_cohorts"],3)
        self.assertEqual(info["equal_siteyear"]["real_partner_over_own_previous"]["positive_cohorts"],2)
        self.assertEqual(info["equal_source_site"]["real_partner_over_own_previous"]["positive_sites"],1)
    def test_partner_is_necessarily_contemporaneous(self):
        self.assertIn("partner_real",MODELS)
        self.assertEqual(PAIRS,("UF440","White Seabass"))
        self.assertEqual(MIN_TEST_HOURS,720)

if __name__=="__main__":unittest.main()
