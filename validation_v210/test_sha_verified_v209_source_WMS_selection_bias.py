import tempfile
import unittest
from pathlib import Path

from validation_v210.sha_verified_v209_source_WMS_selection_bias import (
    FROZEN_ORIGINALS,EXPECTED_SOURCE_GROUP_NODATA,
    OriginalSourceIntegrityStop,exact_original_source,
    exactly_identifiable_group_selection_delta,
    ensure_independent_replays_same_source_statistical_content,
    report_selection_bias,SENTINEL,PLAUSIBLE,
)

def mock_original_replayed(raw_response_last="a"):
    all_groups={}
    for i,(key,n_s) in enumerate(EXPECTED_SOURCE_GROUP_NODATA.items()):
        n_v=6-n_s
        stat={
            "n_original_WMS_extreme_NoData_candidates":n_s,
            "n_original_WMS_plausible_source_candidates":n_v,
            "n_original_measured_RWS_exact_UTC_paired":6,
            "observed_RWS_sentinel_minus_plausible_mean_NAP_m":-1.2 if n_s else None,
            "status":"MEASURED_RWS_LEVEL_VS_MODEL_NODATA_CLASS_CONTRAST_EVALUABLE"
                if n_s else "NOT_EVALUABLE_SPARSE_ONE_OR_BOTH_MODEL_CLASSES"
        }
        reports=[{"original_fixed_UTC":f"2026-06-01T{j:02}:00:00Z",
            "source_original_WMS_reply_SHA256":raw_response_last*64,
            "source_model_value_class":SENTINEL if j<n_s else PLAUSIBLE,
            "RWS_cmNAP_observed_raw_height_NOT_republished":True
        } for j in range(6)]
        all_groups[key]={
          "source_status":"RWS_MODEL_AVAILABILITY_AND_NATIVE_WATERLEVEL_SOURCE_AUDITED",
          "source_RWS_levels_by_original_model_validity_class":stat,
          "original_RWS_native_source_receipt":{"original_RWS_publisher_JSON_SHA256":"b"*64},
          "original_SIX_WMS_source_replies_SHA_only":reports}
    return {"all_12_official_model_validity_vs_measured_tide_level_cohorts":all_groups}

class ExactSourceOnlySelectivityAudit(unittest.TestCase):
    def test_frozen_twelve_source_scope_and_original_72_wms_reply_count(self):
        self.assertEqual(len(EXPECTED_SOURCE_GROUP_NODATA),12)
        self.assertEqual(sum(EXPECTED_SOURCE_GROUP_NODATA.values()),22)
        self.assertEqual(sum(x==0 for x in EXPECTED_SOURCE_GROUP_NODATA.values()),4)
        self.assertEqual(len(FROZEN_ORIGINALS),2)
        self.assertTrue(all(len(h)==64 for h in FROZEN_ORIGINALS.values()))

    def test_exact_group_bias_shift_algebra(self):
        stat={"n_original_WMS_extreme_NoData_candidates":3,
              "n_original_WMS_plausible_numeric_candidate_n":3,
              "n_original_WMS_plausible_source_candidates":3,
              "status":"MEASURED_RWS_LEVEL_VS_MODEL_NODATA_CLASS_CONTRAST_EVALUABLE",
              "observed_RWS_sentinel_minus_plausible_mean_NAP_m":-1.2}
        self.assertAlmostEqual(exactly_identifiable_group_selection_delta(stat),+.6)
        stat["n_original_WMS_extreme_NoData_candidates"]=0
        stat["n_original_WMS_plausible_source_candidates"]=6
        stat["observed_RWS_sentinel_minus_plausible_mean_NAP_m"]=None
        self.assertEqual(exactly_identifiable_group_selection_delta(stat),0.0)

    def test_offline_replay_raw_WMS_sha_variability_does_not_erase_statistic(self):
        a=mock_original_replayed("a")
        b=mock_original_replayed("c")
        replay=ensure_independent_replays_same_source_statistical_content(a,b)
        self.assertEqual(replay["reproduced_native_RWS_provider_SHAs_equal_of_12"],12)
        self.assertEqual(replay["WMS_original_fixed_UTC_and_source_classes_identical_of_72"],72)
        self.assertEqual(replay["WMS_raw_HTTP_SHA_equal_of_72"],0)
        report=report_selection_bias(a,"source-a","source-b",replay)
        sums=report["source_selection_summary"]
        self.assertEqual(sums["n_coastal_mixed_source_groups"],8)
        self.assertEqual(sums["n_always_numeric_Wierumergronden_controls"],4)
        self.assertEqual(sums["n_source_coastal_groups_valid_only_RWS_mean_shift_positive"],8)
        self.assertTrue(sums["NOT_equivalent_to_global_original_72_vs_selected_50_RWS_overall_mean_difference"])

    def test_changed_actual_model_class_has_to_stop(self):
        a=mock_original_replayed("a")
        b=mock_original_replayed("c")
        b["all_12_official_model_validity_vs_measured_tide_level_cohorts"][
         "June_2018_VlielandHaven"]["original_SIX_WMS_source_replies_SHA_only"][0][
         "source_model_value_class"]=PLAUSIBLE
        with self.assertRaisesRegex(OriginalSourceIntegrityStop,"WMS_HAS_DIFFERENT_CLASS"):
            ensure_independent_replays_same_source_statistical_content(a,b)

    def test_fake_raw_source_cannot_masquerade_as_original_sha(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"fake.json"
            path.write_text('{"status":"FAKE"}')
            with self.assertRaisesRegex(OriginalSourceIntegrityStop,"WRONG_ORIGINAL"):
                exact_original_source(path,"44452986729")

if __name__=="__main__":
    unittest.main()
