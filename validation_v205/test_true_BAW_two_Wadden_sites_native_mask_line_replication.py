import unittest
import urllib.parse
from validation_v205.true_BAW_two_Wadden_sites_native_mask_line_replication import (
    PUBLIC_ROI_RD, FROZEN_YEARS, FOUR_WFS_NAMES, TWO_WCS_IDS,
    FIXED_RADIUS_M, fixed_site_roi, original_fixed_URL,
    approved_exact_source_query, fixed_replication_decision,
)

class IndependentPublicCoastalSiteSourceReplication(unittest.TestCase):
    def test_two_unchanged_independent_predeclared_WEBTICS_sites(self):
        self.assertEqual(PUBLIC_ROI_RD,{
            "WestTerschelling":(143870,597420),
            "Wierumergronden":(192882,614562)})
        self.assertEqual(FROZEN_YEARS,("2018","2019"))
        self.assertEqual(FIXED_RADIUS_M,5000)
        self.assertEqual(len(FOUR_WFS_NAMES),4)
        self.assertEqual(len(TWO_WCS_IDS),2)
        for s in PUBLIC_ROI_RD:
            xmin,ymin,xmax,ymax=fixed_site_roi(s)
            self.assertAlmostEqual(xmax-xmin,10000)
            self.assertAlmostEqual(ymax-ymin,10000)

    def test_exact_source_urls_one_of_2_sites_only_year_2018_2019(self):
        for s in PUBLIC_ROI_RD:
            for y in FROZEN_YEARS:
                for kind in ("WCS","WFS_HITS","WFS_GEOJSON"):
                    for lev in ((None,) if kind=="WCS" else ("high","low")):
                        q=original_fixed_URL(s,y,kind,lev)
                        self.assertTrue(approved_exact_source_query(q,kind))
                        params=urllib.parse.parse_qsl(urllib.parse.urlsplit(q).query)
                        if kind=="WCS":
                            self.assertEqual(sum(a=="subset" for a,b in params),2)
                            self.assertTrue(any(a=="coverageId" for a,b in params))
                        elif kind=="WFS_HITS":
                            self.assertEqual(dict(params)["resultType"],"hits")
                        else:
                            self.assertEqual(dict(params)["count"],"500")
                            self.assertEqual(dict(params)["outputFormat"],"application/json")
        with self.assertRaises(ValueError):
            original_fixed_URL("VlielandHaven","2018","WCS")
        with self.assertRaises(ValueError):
            original_fixed_URL("WestTerschelling","2020","WCS")

    def test_frozen_replication_requires_both_lost_and_gained_each_ge100(self):
        valid=fixed_replication_decision(100,100,90,90)
        self.assertTrue(valid["minimum_source_loss_and_gain_each_100_met"])
        self.assertTrue(valid["exploratory_source_mask_turnover_pattern_replicated"])
        fail=fixed_replication_decision(100,100,89,95)
        self.assertFalse(fail["exploratory_source_mask_turnover_pattern_replicated"])
        sparse=fixed_replication_decision(100,99,100,99)
        self.assertFalse(sparse["minimum_source_loss_and_gain_each_100_met"])
        self.assertFalse(sparse["exploratory_source_mask_turnover_pattern_replicated"])
        with self.assertRaises(ValueError):
            fixed_replication_decision(10,100,11,90)

if __name__=="__main__":
    unittest.main()
