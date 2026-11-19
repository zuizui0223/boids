import unittest

from validation_v209.original_BAW_WMS_NODATA_vs_measured_RWS_tidelevel import (
    YEARS,MONTHS,STATION_SOURCE_CODES,UTC_HOURS,EXPECTED_EXTREME_SENTINEL_N,
    SENTINEL,PLAUSIBLE,paired_date_api,
    describe_original_observed_height_by_model_class,
    classify_frozen_12_group_criterion
)

def artificial_fixed_source_groups(invert=()):
    cohorts={}
    for key,n_sentinel in EXPECTED_EXTREME_SENTINEL_N.items():
        lvals=[-1.0]*n_sentinel
        pvals=[+1.0]*(6-n_sentinel)
        if key in invert:
            lvals=[+1.0]*n_sentinel
            pvals=[-1.0]*(6-n_sentinel)
        source=describe_original_observed_height_by_model_class({
            SENTINEL:lvals, PLAUSIBLE:pvals})
        cohorts[key]={"source_status":
            "RWS_MODEL_AVAILABILITY_AND_NATIVE_WATERLEVEL_SOURCE_AUDITED",
            "source_RWS_levels_by_original_model_validity_class":source}
    return cohorts

class OriginalTidalLevelSelectiveModelNoData(unittest.TestCase):
    def test_preexisting_72_original_WMS_site_times_and_known_sentinel_counts(self):
        self.assertEqual(len(YEARS)*len(MONTHS)*len(STATION_SOURCE_CODES)*len(UTC_HOURS),72)
        self.assertEqual(len(EXPECTED_EXTREME_SENTINEL_N),12)
        self.assertEqual(sum(EXPECTED_EXTREME_SENTINEL_N.values()),22)
        self.assertEqual(sum(v==0 for v in EXPECTED_EXTREME_SENTINEL_N.values()),4)
        self.assertEqual(UTC_HOURS,(0,4,8,12,16,20))
        j,*_=paired_date_api("June")
        s,*_=paired_date_api("September")
        self.assertEqual(j("2018",4).isoformat(),"2018-06-01T04:00:00+00:00")
        self.assertEqual(s("2019",20).isoformat(),"2019-09-01T20:00:00+00:00")
        with self.assertRaises(ValueError):
            paired_date_api("November")

    def test_measured_rws_mNAP_lower_at_native_model_nodata(self):
        src={SENTINEL:[-1.0,-1.5],PLAUSIBLE:[1,1.5,2.0,2.5]}
        v=describe_original_observed_height_by_model_class(src)
        self.assertEqual(v["status"],"MEASURED_RWS_LEVEL_VS_MODEL_NODATA_CLASS_CONTRAST_EVALUABLE")
        self.assertEqual(v["n_original_measured_RWS_exact_UTC_paired"],6)
        self.assertTrue(v["low_observed_tide_direction_supported"])
        self.assertLess(v["observed_RWS_sentinel_minus_plausible_mean_NAP_m"],0)

    def test_always_available_offshore_source_is_negative_control_not_missing_data_zero(self):
        v=describe_original_observed_height_by_model_class({
           SENTINEL:[],PLAUSIBLE:[0,1,2,3,4,5]})
        self.assertEqual(v["status"],"NOT_EVALUABLE_SPARSE_ONE_OR_BOTH_MODEL_CLASSES")
        self.assertIsNone(v["low_observed_tide_direction_supported"])

    def test_frozen_at_least7of8_criterion_and_negative_result_preserved(self):
        a=classify_frozen_12_group_criterion(artificial_fixed_source_groups())
        self.assertEqual(a["n_eligible_frozen_mixed_NODATA_and_plausible_groups"],8)
        self.assertEqual(a["n_original_always_plausible_Wierumergronden_control_groups"],4)
        self.assertTrue(a["frozen_directional_criterion_at_least7of8_and_median_negative"])
        mixed=[k for k,v in EXPECTED_EXTREME_SENTINEL_N.items() if v>=2]
        b=classify_frozen_12_group_criterion(artificial_fixed_source_groups([mixed[0]]))
        self.assertEqual(b["n_groups_extreme_NoData_at_lower_original_RWS_height"],7)
        self.assertTrue(b["frozen_directional_criterion_at_least7of8_and_median_negative"])
        c=classify_frozen_12_group_criterion(artificial_fixed_source_groups(mixed[:2]))
        self.assertEqual(c["n_groups_extreme_NoData_at_lower_original_RWS_height"],6)
        self.assertFalse(c["frozen_directional_criterion_at_least7of8_and_median_negative"])

    def test_unbalanced_or_nonfinite_rws_must_stop(self):
        with self.assertRaises(ValueError):
            describe_original_observed_height_by_model_class({
                SENTINEL:[float("nan")],PLAUSIBLE:[1,2,3]})
        with self.assertRaises(ValueError):
            classify_frozen_12_group_criterion({})

if __name__=="__main__":
    unittest.main()
