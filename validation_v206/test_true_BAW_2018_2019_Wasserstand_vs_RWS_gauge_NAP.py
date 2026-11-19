import unittest
import urllib.parse
from validation_v206.true_BAW_2018_2019_Wasserstand_vs_RWS_gauge_NAP import (
 STATION_SOURCE_CODES, UTC_HOURS, YEARS, frozen_UTC,
 frozen_WMS_model_request, verified_frozen_WMS_request,
 validate_three_pinned_native_stations,
 descriptive_matched_model_vs_RWS,
)

class FixedOriginalWMSNativeGaugeSource(unittest.TestCase):
    def test_exactly_thirtysix_fixed_source_queries_and_clock(self):
        self.assertEqual(len(STATION_SOURCE_CODES)*len(UTC_HOURS)*len(YEARS),36)
        self.assertEqual(UTC_HOURS,(0,4,8,12,16,20))
        self.assertEqual(frozen_UTC("2018",12).isoformat(),"2018-06-01T12:00:00+00:00")
        for year in YEARS:
            for site in STATION_SOURCE_CODES:
                for hour in UTC_HOURS:
                    url=frozen_WMS_model_request(year,site,hour)
                    self.assertTrue(verified_frozen_WMS_request(url))
                    q=dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
                    self.assertEqual(q["TIME"],f"{year}-06-01T{hour:02}:00:00.000Z")
                    self.assertEqual(q["CRS"],"EPSG:4326")
                    self.assertIn("GetFeatureInfo",url)
        with self.assertRaisesRegex(ValueError,"NONFROZEN"):
            frozen_UTC("2019",1)

    def test_original_RWS_catalogue_exact_codes_not_effect_selected(self):
        rows=[{"Code":f"other{i}","Naam":f"Other {i}"} for i in range(60)]
        rows.extend([
          {"Code":"vlieland.haven","Naam":"Vlieland, haven"},
          {"Code":"terschelling.west","Naam":"Terschelling, west"},
          {"Code":"wierumergronden","Naam":"Wierumergronden"}])
        x=validate_three_pinned_native_stations({"LocatieLijst":rows})
        self.assertEqual(len(x),3)
        self.assertTrue(all(r["2011_RD_reference_not_RWS_2018_instrument_position"] for r in x.values()))
        rows.append({"Code":"vlieland.haven","Naam":"duplicated native"})
        with self.assertRaisesRegex(Exception,"MISSING_OR_AMBIGUOUS"):
            validate_three_pinned_native_stations({"LocatieLijst":rows})

    def test_descriptive_exact_pairs_no_false_numerical_admission(self):
        no=descriptive_matched_model_vs_RWS([(1,1),(2,2)])
        self.assertEqual(no["status"],"NOT_EVALUABLE_LESS_THAN_3_PAIRED_NUMERIC")
        yes=descriptive_matched_model_vs_RWS([(0,0),(1,1),(2,2),(3,3)])
        self.assertEqual(yes["numeric_model_RWS_NAP_RMSE_under_meter_assumption"],0.0)
        self.assertEqual(yes["native_pairs_Pearson_r_no_significance_claim"],1.0)
        self.assertTrue(yes["native_WMS_model_unit_and_exact_gauge_position_UNVERIFIED"])

if __name__=="__main__":
    unittest.main()
