"""Known mathematical and schedule invariants; no claimed animal results."""
import math
import unittest
from phase_design import (phase_beat_days, information_balance, step_indices,
                          SCHEMES, DAYLIGHT, M2_H, S2_H)

class HarmonicDesignTests(unittest.TestCase):
    def test_rayleigh_phase_wrap(self):
        self.assertAlmostEqual(phase_beat_days(),14.76529453553628,places=8)
        self.assertAlmostEqual(phase_beat_days(M2_H,S2_H), phase_beat_days(S2_H,M2_H))
        with self.assertRaises(ValueError):
            phase_beat_days(12,12)

    def test_balance_known_truth(self):
        self.assertAlmostEqual(information_balance([10,10,10,10]),1.0)
        self.assertEqual(information_balance([0,10,10,10]),0)
        self.assertAlmostEqual(information_balance([20,10,5,5]),
                               16/(40*(1/20+1/10+1/5+1/5)))
        for row in ([1,-1,1,1],[1,2,3],[1,2,3,1.5]):
            with self.assertRaises(ValueError):
                information_balance(row)

    def test_same_effort_different_schedule(self):
        clock,idx=step_indices()
        self.assertEqual(len(idx["daylight_only_8h"]),48)
        self.assertEqual(len(idx["one_day_one_night_8h"]),48)
        self.assertEqual(len(idx["four_2h_blocks_8h"]),48)
        self.assertEqual(len(idx["continuous_24h_reference"]),144)
        self.assertTrue(all(DAYLIGHT[0] <= clock[j] < DAYLIGHT[1]
                            for j in idx["daylight_only_8h"]))
        for scheme in ("one_day_one_night_8h","four_2h_blocks_8h"):
            self.assertEqual(sum(DAYLIGHT[0]<=clock[j]<DAYLIGHT[1] for j in idx[scheme]),24)

if __name__=="__main__":
    unittest.main()
