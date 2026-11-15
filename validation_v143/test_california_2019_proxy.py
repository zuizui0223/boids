"""Synthetic integrity tests, not fake fish or tide measurements."""
from __future__ import annotations
import unittest
from california_2019_proxy import contrast, hour_range, overlap_range, START_H,END_H
class TestFixedPredeclaredAnalysis(unittest.TestCase):
    def test_all_2x2_four_positive_cells(self):
        tab={k:{"exposure_hours":200,"positive_hours":25} for k in ("00","01","10","11")}
        self.assertAlmostEqual(contrast(tab)["night_vs_day_tide_log_odds_diffdiff"],0.)
        tab["11"]["positive_hours"]=50
        self.assertGreater(contrast(tab)["night_vs_day_tide_log_odds_diffdiff"],0)
    def test_insufficient_cell_refused(self):
        tab={k:{"exposure_hours":200,"positive_hours":25} for k in ("00","01","10","11")}
        tab["10"]["positive_hours"]=0
        self.assertEqual(contrast(tab)["status"],"STOP_INSUFFICIENT_2X2_SUPPORT")
    def test_no_observation_outside_original_time(self):
        self.assertEqual(len(hour_range(START_H/24, (START_H+5)/24)),5)
        self.assertFalse(hour_range((END_H+20)/24,(END_H+30)/24))
if __name__=="__main__":unittest.main()
