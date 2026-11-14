"""v130 synthetic known-truth checks. Never use synthetic tests as field evidence."""
from __future__ import annotations
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
import math,unittest
import numpy as np
import run_original_2018_matched_week_holdout as v

def fake_original_bin(bird='A',utc=None,n_f=2,n_i=8):
    dt=utc or datetime(2018,6,18,13,tzinfo=timezone.utc)
    return {'private_bird':bird,'source_month':dt.month,
        'source_utc_event':dt,'source_lat':53.3,'source_lon':5.09,
        'original_acc_forage_events':n_f,'original_acc_inactive_events':n_i}

class TrueVlielandV130MatchedWeekKnownTruth(unittest.TestCase):
    def test_original_2018_2019_provenance_mismatch_stops(self):
        with self.assertRaisesRegex(v.SourceStop,'PRIOR_V129'):
            v.exact_previous_2018_source_proof({'analysis':'unverified'},{})
        self.assertEqual(v.STAGE_OFFSETS,(0,3,7,11))
        self.assertEqual(v.WEEK_BOOT_N,10000)
        self.assertEqual(v.BOOT_SEED,20261114)
        self.assertAlmostEqual(v.RIDGE_LAMBDA,20)

    def test_same_2018_original_quarterhour_rows_for_all_stage_shifts(self):
        bins=[fake_original_bin(utc=datetime(2018,6,18,10+i,tzinfo=timezone.utc),
                                n_f=1+i,n_i=9-i) for i in range(4)]
        # i=3 loses +11d phase measured source, all other actual bin stages unchanged
        def realstage(gauge,times,t):
            if t.hour==13 and t.day==29:return None
            return {'source_stage_mNAP':.33,'source_phase':1}
        with patch.object(v,'_solar_label',return_value='day'),patch.object(
             v,'nearest_original_rws',side_effect=realstage):
            common,src=v.common_matched_source(bins,{datetime(2018,6,1,tzinfo=timezone.utc):.5})
        self.assertEqual(len(common),3)
        self.assertEqual(src['original_source_QA'][
            'source_excluded_not_all_four_real_RWS_alignments_valid'],1)
        self.assertFalse(src['all_source_gates_pass'])
        self.assertEqual(src['original_2018_genuine_source_15min_quarterhour_rows'],3)
        self.assertEqual(common[0][2],((.33,1),(.33,1),(.33,1),(.33,1)))
        self.assertNotIn('private_bird',str(src))
        # Y is never inspected by the eligibility check.
        for row in bins:row['original_acc_forage_events']=-1
        with patch.object(v,'_solar_label',return_value='day'),patch.object(
             v,'nearest_original_rws',side_effect=realstage):
            _,src2=v.common_matched_source(bins,{datetime(2018,6,1,tzinfo=timezone.utc):.5})
        self.assertEqual(src2['original_2018_genuine_source_15min_quarterhour_rows'],3)

    def test_original_week_not_row_split_and_equal_feature_counts(self):
        t=datetime(2018,6,18,13,tzinfo=timezone.utc)
        source=[
          (fake_original_bin('birdA',t,2,8),'night',
               ((.4,1),(.5,-1),(-.3,1),(.6,-1)),t.isocalendar().week),
          (fake_original_bin('birdB',t+timedelta(days=1),0,10),'day',
               ((.4,1),(.5,-1),(-.3,1),(.6,-1)),
               (t+timedelta(days=1)).isocalendar().week),
          (fake_original_bin('birdA',t+timedelta(days=7),2,8),'night',
               ((.4,1),(.5,-1),(-.3,1),(.6,-1)),
               (t+timedelta(days=7)).isocalendar().week)
        ]
        mats,labels=v.fixed_predictor_matrices(source)
        self.assertEqual(tuple(mats),v.MODEL_NAMES)
        self.assertEqual(mats['CLOCK'].shape,(3,12))
        self.assertEqual(mats['SOLAR'].shape,(3,13))
        self.assertEqual(mats['TIDE-0'].shape,(3,18))
        self.assertEqual(labels['fold'][0],labels['fold'][1])
        self.assertNotEqual(labels['source_week'][0],labels['source_week'][2])
        self.assertTrue(np.array_equal(mats['SOLAR'][:,-1],[1,0,1]))
        self.assertTrue(np.allclose(mats['TIDE-0'][0,-5:],[.4,1,.4,1,.4]))
        self.assertTrue(np.allclose(mats['TIDE-3'][1,-5:],[.5,-1,-.5,0,0]))
        self.assertTrue(np.allclose(mats['TIDE-11'][0,-5:],[.6,-1,-.6,-1,.6]))

    def test_fixed_ridge_recovers_known_linear_target_when_penalty_zero(self):
        X=np.column_stack((np.ones(8),np.array([0,0,1,1,0,1,0,1]),
                        np.array([-.2,.1,.4,.5,.3,-.1,-.4,.2])))
        y=X@np.array([.48,.12,.25])
        pred=v.ridge_fit_predict(X,y,X,lam=0.)
        self.assertTrue(np.allclose(pred,y,atol=1e-10))
        self.assertTrue(np.all((pred>=0)&(pred<=1)))

    def test_week_and_bird_equal_scoring_not_event_weighted(self):
        y=np.zeros(6)
        weeks=np.array([24,24,24,25,25,25])
        birds=np.array([0,0,1,0,1,1])
        pred={k:np.zeros(6) for k in v.MODEL_NAMES}
        pred['CLOCK'][:2]=1.
        W,m,src=v.weeks_bird_equal_scores(y,pred,weeks,birds)
        self.assertTrue(np.array_equal(W,[24,25]))
        self.assertAlmostEqual(m[0,0],.5)
        self.assertAlmostEqual(m[1,0],0.)
        self.assertEqual(src['source_genuine_bird_week_score_groups'],4)

    def test_week_effect_descriptors_with_perfect_synthetic_phase_signal(self):
        weeks=np.arange(25,45) # fixed 20 genuine week labels only for a synthetic unit test
        scores=np.tile(np.array([.50,.40,.30,.35,.38,.42]),(len(weeks),1))
        z=v.effect_from_week_scores(weeks,scores)
        d=z['predeclared_original_2018_heldout_week_solar_tide_and_phase_contrasts']
        self.assertAlmostEqual(d['D_solar_clock_minus_solar'],.1)
        self.assertAlmostEqual(d['D_tide_real_solar_minus_real'],.1)
        self.assertAlmostEqual(d['D_phase_real_gain_minus_best_wrong_gain'],.05)
        self.assertEqual(z['exploratory_correct_tide_phase_uniqueness_status'],
                         'SUGGESTIVE_WITHIN_SOURCE_ONLY')
        self.assertAlmostEqual(z['source_calendar_weeks_positive_real_tide_vs_best_wrong_fraction'],1.)
        self.assertGreater(z['source_week_paired_bootstrap_CI95_descriptive_not_causal'][
            'D_phase_real_minus_best_wrong'][0],0.)

    def test_no_true_tide_increment_or_more_accurate_wrong_phase_not_rescued(self):
        weeks=np.arange(25,45)
        scores=np.tile(np.array([.45,.40,.42,.35,.39,.39]),(len(weeks),1))
        z=v.effect_from_week_scores(weeks,scores)
        self.assertLess(z['predeclared_original_2018_heldout_week_solar_tide_and_phase_contrasts'][
           'D_phase_real_gain_minus_best_wrong_gain'],0)
        self.assertEqual(z['exploratory_correct_tide_phase_uniqueness_status'],
                         'NOT_ESTABLISHED_BY_MATCHED_WEEK_FORECAST')

    def test_prediction_score_requires_precisely_same_obs_index(self):
        with self.assertRaisesRegex(ValueError,'BAD_OBSERVATION'):
            v.weeks_bird_equal_scores(np.zeros(3),
                  {k:np.zeros(3) for k in v.MODEL_NAMES},
                  np.zeros(2),np.zeros(3))
        with self.assertRaisesRegex(ValueError,'BAD_SOURCE_PREDICTION'):
            p={k:np.zeros(3) for k in v.MODEL_NAMES}
            p['SOLAR']=np.zeros(2)
            v.weeks_bird_equal_scores(np.zeros(3),p,np.array([24,24,25]),np.array([0,1,0]))

if __name__=='__main__':unittest.main()
