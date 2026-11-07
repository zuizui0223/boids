"""v60 known-truth synthetic unit tests: not new wild GPS evidence."""
import unittest
from datetime import datetime,timedelta,timezone
from copy import deepcopy
import numpy as np
from paired_real_phase_heading import (
    reconstruct_private_pair_indices,verify_frozen_primary_source,
    score_matched_observed_heading)

def example_rows(birds=3,pairs_per_bird=35):
    rows=[]
    for k in range(birds):
        for i in range(pairs_per_bird):
            for phase,d in ((1,2*i),(-1,2*i+1)):
                t=datetime(2011,5,1,12,tzinfo=timezone.utc)+timedelta(days=d)
                vec=(1.,0.) if phase==1 else (0.,1.)
                rows.append({
                    "id":f"animal_{k}","t":t,"lat":53.4,"lon":5.5,
                    "h":0.1,"phase":phase,
                    "previous_e":1.,"previous_n":0.,"previous_speed_log":1.,
                    "target_e":vec[0],"target_n":vec[1]})
    return rows

def known_forecast(train,rows,level):
    if level!=1:raise AssertionError("Only existing frozen actual tide model")
    return np.asarray([[1.,0.] if r["phase"]==1 else [0.,1.] for r in rows])

class PairedFieldKnownTruth(unittest.TestCase):
    def setUp(self):
        self.rows=example_rows()
        self.matches,self.audit=reconstruct_private_pair_indices(self.rows)

    def test_pair_indices_are_v59_identical_source_blind(self):
        self.assertEqual(len(self.matches),105)
        self.assertEqual(self.audit["unique_disjoint_actual_opposite_tide_pairs"],105)
        self.assertEqual(len({i for pair in self.matches for i in pair}),210)
        alt=deepcopy(self.rows)
        for r in alt:r.update(target_e=-999.,target_n=999.)
        pairs2,audit2=reconstruct_private_pair_indices(alt)
        self.assertEqual(self.matches,pairs2)
        self.assertEqual(self.audit,audit2)
        self.assertEqual(self.matches,reconstruct_private_pair_indices(list(self.rows))[0])

    def test_source_requirements_frozen_and_not_relaxed(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP_FROZEN"):
            verify_frozen_primary_source(self.rows,self.matches,self.audit)
        alt=deepcopy(self.rows)
        alt[1]["phase"]=+1
        pairs,receipt=reconstruct_private_pair_indices(alt)
        self.assertNotEqual(len(pairs),len(self.matches))

    def test_observed_pair_projection_has_true_positive_known_truth(self):
        calls=[]
        def fn(train,test,level):
            calls.append((len(train),len(test),level))
            return known_forecast(train,test,level)
        r=score_matched_observed_heading(self.rows,self.rows,self.matches,fn,
                                        bird_draws=200,week_draws=120)
        self.assertEqual(calls,[(210,630,1)])
        m=r["metrics"]
        t=m["observed_paired_tide_direction_concordance"]
        self.assertAlmostEqual(t["equal_bird_mean"],.5)
        self.assertEqual(t["positive_birds"],3)
        self.assertEqual(t["whole_bird_bootstrap_95"],[.5,.5])
        self.assertEqual(t["exact_bird_sign_flip_combinations"],8)
        self.assertAlmostEqual(t["equal_bird_one_sided_sign_flip_sensitivity_p"],.125)
        self.assertAlmostEqual(m["actual_vs_flipped_tide_cosine_loss_gain"]["equal_bird_mean"],1.)
        self.assertAlmostEqual(m["observed_paired_absolute_heading_separation_degrees"]["equal_bird_mean"],90.)
        self.assertAlmostEqual(m["orthogonal_direction_projection"]["equal_bird_mean"],0.)
        self.assertEqual(r["observational_concordance_status"],"POSITIVE_CONCORDANCE_EXPLORATORY")
        self.assertEqual(r["zero_model_switch_pairs_scored_zero_not_dropped"],0)
        self.assertEqual(r["actual_real_disjoint_matched_pairs"],105)
        self.assertNotIn("animal_0",str(r))
        self.assertNotIn("2011-05",str(r))

    def test_observed_heading_reversal_negates_primary_without_reselecting_pairs(self):
        old=score_matched_observed_heading(self.rows,self.rows,self.matches,known_forecast,
                                          bird_draws=30,week_draws=20)
        other=deepcopy(self.rows)
        for r in other:
            r["target_e"],r["target_n"]=(
                (0.,1.) if r["phase"]==1 else (1.,0.))
        self.assertEqual(self.matches,reconstruct_private_pair_indices(other)[0])
        new=score_matched_observed_heading(self.rows,other,self.matches,known_forecast,
                                          bird_draws=30,week_draws=20)
        self.assertAlmostEqual(old["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"],.5)
        self.assertAlmostEqual(new["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"],-.5)
        self.assertEqual(new["observational_concordance_status"],"NO_ROBUST_POSITIVE_CONCORDANCE")

    def test_zero_model_switch_is_not_excluded_or_positive(self):
        def constant(train,test,level):
            return np.asarray([[1.,0.] for _ in test])
        out=score_matched_observed_heading(self.rows,self.rows,self.matches,constant,
                                          bird_draws=20,week_draws=20)
        self.assertEqual(out["zero_model_switch_pairs_scored_zero_not_dropped"],105)
        self.assertEqual(out["actual_real_disjoint_matched_pairs"],105)
        self.assertEqual(out["metrics"]["observed_paired_tide_direction_concordance"]["equal_bird_mean"],0.)

    def test_forecast_bad_dimensions_or_zero_vector_hard_stops(self):
        for fn in [lambda train,test,level: np.zeros((len(test),2)),
                   lambda train,test,level: np.ones((1,2))]:
            with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP"):
                score_matched_observed_heading(self.rows,self.rows,self.matches,fn,
                                              bird_draws=20,week_draws=20)

    def test_mismatched_phase_or_forecast_replay_hard_stops(self):
        b=deepcopy(self.rows)
        b[self.matches[0][0]]["phase"]=-1
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP_UNMATCHED"):
            score_matched_observed_heading(self.rows,b,self.matches,known_forecast,
                                          bird_draws=20,week_draws=20)
        def bogus(train,test,level):
            y=known_forecast(train,test,level)
            y[0]*=-1.
            return y
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP_REAL_PHASE_MODEL_REPLAY"):
            score_matched_observed_heading(self.rows,self.rows,self.matches,bogus,
                                          bird_draws=20,week_draws=20)

if __name__=="__main__":
    unittest.main()
