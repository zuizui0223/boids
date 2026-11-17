"""v173 source-only geometry, index, and true-survey-year caution fixtures."""
import unittest
from historical_vlieland_tile_shortlist import (
    xy_intersect, GEO_BBOX_WIDE, EXPECTED_SHA, NATIVE_TILES, ALL_POSSIBLE_YEARS
)

class TestOriginalIndexGeography(unittest.TestCase):
    def test_real_borndiep_outside_vlieland(self):
        # v170 genuine Borndiep original 2016 bbox.
        exists,area=xy_intersect((155390.,604810.,175030.,620230.),GEO_BBOX_WIDE)
        self.assertFalse(exists)
        self.assertEqual(area,0.)
    def test_actual_candidate_bbox_and_partial_overlap(self):
        yes,area=xy_intersect((130000.,590000.,160000.,620000.),GEO_BBOX_WIDE)
        self.assertTrue(yes)
        self.assertAlmostEqual(area,20*25.)
    def test_edge_touch_without_area_is_not_valid_overlap(self):
        yes,area=xy_intersect((150000.,590000.,165000.,610000.),GEO_BBOX_WIDE)
        self.assertFalse(yes)
        self.assertEqual(area,0.)
    def test_original_index_identity_and_year_are_frozen(self):
        self.assertEqual(NATIVE_TILES,165)
        self.assertEqual(len(EXPECTED_SHA),64)
        self.assertIn(2016,ALL_POSSIBLE_YEARS)
        self.assertEqual(GEO_BBOX_WIDE,(120000,575000,150000,615000))
if __name__=="__main__":
    unittest.main()
