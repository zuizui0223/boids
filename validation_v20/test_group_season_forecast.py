"""v20 pre-outcome future group-season known truth / temporal anti-leakage tests."""
import unittest
import numpy as np
import pandas as pd
import group_season_forecast as m


def fixture():
    rows=[]
    for g in range(21):
        n=4 if g==0 else 3 if g<8 else 2 if g<15 else 1
        for s in range(n):
            # Final singleton source group contributes actual G season for
            # five-category source integrity, not as a repeated group.
            season_idx=4 if g==20 else s
            y=.1+.023*g + .002*season_idx
            rows.append({"ID":float(g),"SEASON":m.SEASON_ORDER[season_idx],
                         "fidelity":y,
                         "AREA_SQM":1000000*(1+.07*g)*np.exp(.01*s),
                         "speed_km_day":10*(1+.05*g)*np.exp(.01*s)})
    assert len(rows)==45
    return pd.DataFrame(rows)


class TestFrozenWildGroupHistory(unittest.TestCase):
    def test_original_source_and_shrink_rule_frozen(self):
        self.assertEqual(m.ORIGINAL_SHA256,"c6a534993e99f2cb324e9691ff7ec58095bf7cd7e82d7a38721f3575097cbb55")
        self.assertEqual(m.SEASON_ORDER,("C","D","E","F","G"))
        self.assertEqual(m.RESPONSE_NAMES,("fidelity","AREA_SQM","speed_km_day"))
        self.assertEqual(m.SHRINK_KAPPA,2.)
        self.assertEqual(m.BOOT_RESAMPLES,10000)

    def test_only_preceding_own_and_other_group_history(self):
        raw=m.registered_source(fixture())
        targets=m.eligible_targets(raw)
        self.assertGreaterEqual(len(targets),12)
        self.assertGreaterEqual(len(set(i for i,_ in targets)),8)
        out=m.predictions(m.transformed_source(raw,"fidelity"),targets)
        self.assertEqual(len(out),len(targets))
        self.assertTrue(all(t["n_group_previous_seasons"]>=1 for t in out))
        self.assertTrue(all(t["n_other_prior_groups"]>=3 for t in out))

    def test_known_truth_group_persistence_gets_positive_partial_pool_gain(self):
        raw=m.registered_source(fixture())
        targets=m.eligible_targets(raw)
        summary=m.summarize(m.predictions(m.transformed_source(raw,"fidelity"),targets),
                            "fidelity")
        self.assertEqual(summary["status"],
            "EXPLORATORY_SOURCE_DERIVED_WILD_GROUP_NEXT_SEASON_FORECAST")
        self.assertGreater(summary["n_independent_group_clusters"],8)
        self.assertGreater(summary["primary_increment_shrink_vs_external_M0_minus_M2"]["group_equal_mean_gain"],0)
        self.assertEqual(len(summary["per_group_anonymized"]),summary["n_independent_group_clusters"])

    def test_future_test_only_changes_future_error_not_historical_pred(self):
        raw=m.registered_source(fixture())
        rows=m.eligible_targets(raw)
        a=m.predictions(m.transformed_source(raw,"fidelity"),rows)
        alt=raw.copy()
        alt.loc[(alt["_id"]=="0.0") & (alt["_season"]=="F"),"fidelity"] = .99
        b=m.predictions(m.transformed_source(alt,"fidelity"),rows)
        # Exact same earlier season D/E errors for every group (F target
        # changes only future context for predictions later than F).
        before={(x["group"],x["season"]):(x["error_M0"],x["error_M1"],x["error_M2"])
                for x in a if x["season"] in ("D","E")}
        after={(x["group"],x["season"]):(x["error_M0"],x["error_M1"],x["error_M2"])
               for x in b if x["season"] in ("D","E")}
        self.assertEqual(before,after)

    def test_source_grain_drift_stops_before_behavior_model(self):
        df=fixture()
        with self.assertRaisesRegex(ValueError,"row count"):
            m.registered_source(df.iloc[:-1].copy())
        df.loc[0,"SEASON"]="invalid"
        with self.assertRaisesRegex(ValueError,"seasonal category"):
            m.registered_source(df)

    def test_duplicate_original_group_season_stops(self):
        df=fixture()
        df.loc[1,["ID","SEASON"]]=df.loc[0,["ID","SEASON"]]
        with self.assertRaisesRegex(ValueError,"Duplicated"):
            m.registered_source(df)

    def test_response_domain_fails_closed_never_tunes_primary(self):
        df=m.registered_source(fixture())
        df.loc[df.index[1],"fidelity"]=1.6
        with self.assertRaisesRegex(ValueError,"bounded"):
            m.transformed_source(df,"fidelity")
        df2=m.registered_source(fixture())
        df2.loc[df2.index[0],"AREA_SQM"]=-1.
        with self.assertRaisesRegex(ValueError,"positive-only"):
            m.transformed_source(df2,"AREA_SQM")

    def test_year_order_not_used_as_independent_group_replicates(self):
        df=m.registered_source(fixture())
        target=m.eligible_targets(df)
        y=m.transformed_source(df,"fidelity")
        summary=m.summarize(m.predictions(y,target),"fidelity")
        self.assertLess(summary["n_independent_group_clusters"],
                        summary["n_heldout_future_group_season_targets"])
        self.assertLess(summary["n_independent_group_clusters"],df.shape[0])


if __name__=="__main__":
    unittest.main()
