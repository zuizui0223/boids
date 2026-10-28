"""Post-result v20-C audit known truth, preserves primary and no-retune contract."""
import unittest
import postresult_audit as m


class AuditTests(unittest.TestCase):
    def sample(self):
        rows=[]
        for g in range(15):
            n=2 if g<9 else 1  # 9*2 + 6*1 = 24 source target rows
            for t in range(n):
                rows.append({"group":f"group{g:02d}",
                             "season":("D" if t==0 else "E"),
                             "error_M0":.1,
                             "error_M1":.09,
                             "error_M2":.1-m.ORIGINAL_FROZEN_MAIN_GAIN})
        return rows

    def test_full_group_season_reporting_and_exact_primary_reproduction(self):
        d=m.audit(self.sample(),m.ORIGINAL_FROZEN_MAIN_GAIN)
        self.assertEqual(d["source_groups"],15)
        self.assertEqual(d["source_future_group_season_targets"],24)
        self.assertEqual(d["positive_group_sign_count"],15)
        self.assertAlmostEqual(d["exact_one_sided_sign_probability_if_independent_group_signs"],
                               1/32768)
        self.assertTrue(d["all_leave_one_group_out_primary_means_positive"])
        self.assertFalse(d["no_target_or_hyperparameter_refitted"] is False)
        self.assertFalse(d["source_raw_GPS_or_original_ecological_rows_exported"])

    def test_changed_outcome_or_source_support_cannot_replace_original_endpoint(self):
        with self.assertRaisesRegex(ValueError,"Frozen original target support"):
            m.audit(self.sample()[:-1],m.ORIGINAL_FROZEN_MAIN_GAIN)
        with self.assertRaisesRegex(ValueError,"Original v20-B primary"):
            m.audit(self.sample(),m.ORIGINAL_FROZEN_MAIN_GAIN+0.2)
        wrong=self.sample()
        wrong[0]["group"]="new_group_16"
        with self.assertRaisesRegex(ValueError,"denominator"):
            m.audit(wrong,m.ORIGINAL_FROZEN_MAIN_GAIN)

    def test_group_equal_aggregation_not_fix_weighted(self):
        test=[
          {"group":"A","season":"D","error_M0":.09,"error_M2":.01},
          {"group":"A","season":"E","error_M0":.09,"error_M2":.01},
          {"group":"B","season":"E","error_M0":.01,"error_M2":.05},
        ]
        z,n,k=m.group_equal_gain(test)
        self.assertAlmostEqual(z,.02)
        self.assertEqual((n,k),(2,3))


if __name__=="__main__":
    unittest.main()
