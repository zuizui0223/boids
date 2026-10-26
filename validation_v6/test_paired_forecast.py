"""Tests frozen eligibility, no holdout leakage, and deterministic turning predictions."""
from __future__ import annotations
import unittest
import numpy as np
from paired_trajectory_gate import EXPECTED_PAIRS, STRIDE, MIN_DOWNSAMPLED, admit
from social_forecast import rows_for_bat, make_trial_features, run_scores


def synthetic_trial(index:int,raw_steps:int=130):
    t=np.arange(raw_steps,dtype=float)*.01
    a=np.column_stack([t, 0.1*np.sin(t*1.7+index/7),0.13*np.sin(t*1.3+index/13)])
    b=np.column_stack([t+.05, .4+0.06*np.sin(t*1.2+index/6),.2+0.07*np.sin(t*2.1+index/9)])
    return a,b


class TestPairedInference(unittest.TestCase):
    def test_gate_observes_all_pairs_not_shortened_to_one(self):
        p=[synthetic_trial(i) for i in range(EXPECTED_PAIRS)]
        accepted, audit, gate=admit(p)
        self.assertEqual(gate['eligible_pairs'],EXPECTED_PAIRS)
        self.assertEqual(gate['gate'],'PASS')
        self.assertEqual(len(audit),EXPECTED_PAIRS)
        self.assertEqual(len(accepted[0]['x']),len(p[0][0][::STRIDE]))

    def test_gate_rejects_insufficient_data_without_refit(self):
        pairs=[synthetic_trial(i) for i in range(EXPECTED_PAIRS)]
        for i in range(22):pairs[i]=synthetic_trial(i,40)
        _,audit,gate=admit(pairs)
        self.assertEqual(gate['eligible_pairs'],8)
        self.assertTrue(gate['gate'].startswith('STOP_'))
        self.assertEqual(audit[0]['decision'],'FAIL_TOO_SHORT')

    def test_future_partner_state_not_used(self):
        x,y=synthetic_trial(0)
        x,y=x[::STRIDE],y[::STRIDE]
        base, social, out=rows_for_bat(x,y)
        mutated=y.copy();mutated[-1]+=[1000,-2000,3000]
        bb, ss, yy=rows_for_bat(x,mutated)
        self.assertTrue(np.array_equal(base,bb))
        self.assertTrue(np.array_equal(out,yy))
        # social features for all but last feature row must remain unchanged.
        np.testing.assert_allclose(social[:-1],ss[:-1])

    def test_ghost_is_different_flight_episode(self):
        a,_ , gate=admit([synthetic_trial(i) for i in range(EXPECTED_PAIRS)])
        real=make_trial_features(a,ghost=False)
        ghost=make_trial_features(a,ghost=True)
        np.testing.assert_allclose(real[0]['roles'][0][0],ghost[0]['roles'][0][0])
        self.assertFalse(np.allclose(real[0]['roles'][0][1],ghost[0]['roles'][0][1]))

    def test_ghost_train_does_not_read_held_out_pair(self):
        accepted,_,gate=admit([synthetic_trial(i) for i in range(EXPECTED_PAIRS)])
        for heldout in [0, 7, 14, 23]:
            ghost=make_trial_features(accepted,ghost=True,excluded_index=heldout)
            self.assertTrue(all(rec['ghost_donor_index'] != accepted[heldout]['index']
                                for rec in ghost))

    def test_score_replay_and_no_nonfinite(self):
        accepted,_,gate=admit([synthetic_trial(i) for i in range(EXPECTED_PAIRS)])
        one=run_scores(accepted)
        two=run_scores(accepted)
        self.assertEqual(one['equal_pair_weighted_mean'],two['equal_pair_weighted_mean'])
        self.assertEqual(one['n_pair_trials'],30)
        self.assertTrue(all(np.isfinite(v) for v in one['equal_pair_weighted_mean'].values()))
        self.assertTrue(all(x['n_target_step_pairs']>0 for x in one['per_pair']))

if __name__=='__main__':unittest.main()
