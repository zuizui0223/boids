"""v22 pre-outcome known-truth temporal, wet/dry and no-outcome-selection tests."""
from __future__ import annotations

import math
import unittest
import numpy as np
import pandas as pd
import regime_group_forecast as m


def invented_source():
    rows=[]
    for g in range(26):
        seasons=list(range(5))+([5+g%6] if g<13 else [])
        for s in seasons:
            regime=m.CONTEXTS[s%4]
            raw=.2+g*.008+(.03 if regime=="wet" else 0)
            if g<4 and s==0:raw=float("nan")
            rows.append({"groupss_":float(g),
                "season":m.SEASONS[s],"season_type":regime,
                "days_tracked":15,"fidelity":raw})
    assert len(rows)==143
    return pd.DataFrame(rows)


class TestPreOutcomeWildRegime(unittest.TestCase):
    def test_original_source_and_model_parameters_frozen(self):
        self.assertEqual(m.SOURCE_SHA256,"d08864e91a543403cb1e8abf1bf9ea84247543181b8d4f4464ceb03929c0fa83")
        self.assertEqual(m.SOURCE_ROWS,143)
        self.assertEqual(m.SOURCE_GROUPS,26)
        self.assertEqual(m.SOURCE_MISSING_FIDELITY,4)
        self.assertEqual(m.SHRINK_KAPPA,2.)
        self.assertEqual(m.SEASONS[0],"year_one_1")
        self.assertEqual(m.SEASONS[-1],"year_two_5")

    def test_exact_original_group_and_regime_label_integrity(self):
        original=m.source_frame(invented_source())
        self.assertEqual(original["_group"].nunique(),26)
        self.assertEqual(original["_season"].nunique(),11)
        self.assertEqual(original["_regime"].nunique(),4)
        self.assertEqual(len(original),143)

    def test_fixed_future_targets_know_previous_group_and_other_source_not_outcomes(self):
        d=m.source_frame(invented_source())
        eligible=m.eligibility(d)
        self.assertGreater(len(eligible),30)
        self.assertGreater(len(set(x for x,_ in eligible)),8)
        rows=m.predict(d,eligible)
        self.assertEqual(len(rows),len(eligible))
        self.assertTrue(all(x["n_own_previous_seasons"]>=1 for x in rows))
        self.assertTrue(all(x["n_other_prior_groups"]>=3 for x in rows))

    def test_known_truth_group_history_is_sometimes_useful_beyond_environment(self):
        d=m.source_frame(invented_source())
        result=m.summarize(m.predict(d,m.eligibility(d)))
        self.assertEqual(result["status"],
            "EXPLORATORY_SAME_MOVEbank_POPULATION_REGIME_CONDITIONAL_FUTURE_FIDELITY")
        self.assertEqual(result["source_group_ids"],26)
        self.assertGreater(result["source_future_group_season_targets"],30)
        self.assertGreater(result["registered_contrasts"][
            "primary_history_beyond_environment_ME_minus_MEG"]["equal_group_mean_gain"],0)

    def test_target_outcome_change_cannot_change_any_earlier_predictions(self):
        d=m.source_frame(invented_source())
        targets=m.eligibility(d)
        before=m.predict(d,targets)
        altered=d.copy()
        # Target only in 11th season in a single original group.
        ix=altered.index[(altered["_group"]=="5") &
                         (altered["_season"]=="year_two_5")]
        self.assertEqual(len(ix),1)
        altered.loc[ix,"fidelity"]=0.99
        after=m.predict(altered,targets)
        def earlier(out):
            return {(r["group"],r["season"]):(
                r["mse_M0"],r["mse_ME"],r["mse_MG"],r["mse_MEG"])
                for r in out if m.SEASONS.index(r["season"])<10}
        self.assertEqual(earlier(before),earlier(after))

    def test_environment_classification_source_inconsistent_stops_before_model(self):
        data=invented_source()
        data.loc[data.index[0],"season_type"]="not_original"
        with self.assertRaisesRegex(ValueError,"environmental labels"):
            m.source_frame(data)
        data=invented_source()
        data.loc[data.index[0],"season_type"]="wet"
        with self.assertRaisesRegex(ValueError,"season assignment inconsistent"):
            m.source_frame(data)

    def test_duplicate_group_season_and_source_missingness_fail_closed(self):
        data=invented_source()
        data.loc[1,"groupss_"]=data.loc[0,"groupss_"]
        data.loc[1,"season"]=data.loc[0,"season"]
        with self.assertRaisesRegex(ValueError,"Group-season repeated"):
            m.source_frame(data)
        data=invented_source()
        data.loc[5,"fidelity"]=np.nan
        with self.assertRaisesRegex(ValueError,"missingness changed"):
            m.source_frame(data)

    def test_response_domain_check_no_outcome_tuning(self):
        d=m.source_frame(invented_source())
        t=m.eligibility(d)
        changed=d.copy()
        changed.loc[changed.index[7],"fidelity"]=8.0
        with self.assertRaisesRegex(ValueError,"not in 0..1"):
            m.predict(changed,t)

    def test_group_equal_aggregation_and_all_seasons_retain(self):
        samples=[
            {"group":"a","season":"year_one_3","mse_ME":.03,"mse_MEG":.01},
            {"group":"a","season":"year_one_4","mse_ME":.03,"mse_MEG":.01},
            {"group":"b","season":"year_one_4","mse_ME":.01,"mse_MEG":.05}
        ]
        value,ng,nt=m.group_mean_gain(samples,"mse_ME","mse_MEG")
        self.assertAlmostEqual(value,-.01)
        self.assertEqual((ng,nt),(2,3))


if __name__=="__main__":
    unittest.main()
