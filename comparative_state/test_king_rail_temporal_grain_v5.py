"""Only synthetic, known-truth tests for King Rail temporally blocked resolution comparison."""
import math
import unittest
from comparative_state.king_rail_temporal_grain_v5 import (build_events, chronological_split, score_single, evaluate, test_circular_shift)


def fake(alpha=0.7,constant=False):
    b={}
    for i in range(10):
        name=f'{i:03}_21'
        v=[]
        for d in range(1,25):
            a=25+14*((-1)**d)+.3*i
            u=10+i*.5 + (0.0 if constant else alpha*(a-25))
            v.append({'bird':name,'prefix':f'{i:03}','event':d,'year':2021,
                      'julian':d,'A':a,'U':u,'random_count':2})
        b[name]=v
    return b

class Tests(unittest.TestCase):
    def test_chronological_no_future_used_leak(self):
        b=fake();tr,te=chronological_split(b['000_21'])
        self.assertEqual(len(tr),14)
        self.assertEqual(len(te),10)
        self.assertLess(max(e['julian'] for e in tr),min(e['julian'] for e in te))

    def test_event_aligned_synthetic_beats_lag(self):
        b=fake();x=evaluate(b,reps=200)
        self.assertEqual(x['fixed_primary_gate'],'PASS')
        self.assertGreater(x['primary_event_over_lag']['mean'],0)
        self.assertEqual(x['eligible_bird_years'],10)

    def test_stationary_used_depth_prefers_history(self):
        b=fake(constant=True);x=evaluate(b,reps=200)
        self.assertEqual(x['fixed_primary_gate'],'FAIL')
        self.assertAlmostEqual(x['primary_event_over_lag']['mean'],0,places=8)

    def test_lag_truly_ignores_current_date(self):
        b=fake();a=chronological_split(b['000_21']);other={k:chronological_split(v)[0] for k,v in b.items() if k!='000_21'}
        s=score_single('000_21',a,other)
        altered=[dict(e, A=e['A']+300) for e in a[1]]
        t=score_single('000_21',(a[0],altered),other)
        # Lag for first test record depends only on previous known dates, not own current A.
        self.assertEqual(s['train_u_mean'],t['train_u_mean'])
        self.assertNotEqual(s['mse_cm2']['current_event'],t['mse_cm2']['current_event'])
        self.assertNotEqual(s['mse_cm2']['lag_3_dates'],t['mse_cm2']['lag_3_dates'])
        # A mutation of only the final test date cannot affect the lag prediction for that final date.
        x=[dict(e) for e in a[1]];x[-1]['A']+=300
        late=score_single('000_21',(a[0],x),other)
        self.assertEqual(s['mse_cm2']['lag_3_dates'],late['mse_cm2']['lag_3_dates'])

    def test_year_identity_distinct_prefix_sensitivity(self):
        b=fake();b['001_21']=b.pop('001_21')
        xx=b.pop('001_21')
        for e in xx: e['bird']='000_20'; e['prefix']='000'
        b['000_20']=xx
        x=evaluate(b,reps=200)
        self.assertEqual(x['eligible_bird_years'],10)
        self.assertEqual(x['distinct_ID_prefixes'],9)
        self.assertEqual(x['conservative_ID_prefix_cluster_event_over_lag']['n_groups'],9)

    def test_no_inference_from_missing_used_random(self):
        rs=[{'ID':'165.020H1_21','WaterDepth':'9','Year':'2021','Julian':'140','Missing':'No'},
            {'ID':'165.020R1_1_21','WaterDepth':'21','Year':'2021','Julian':'140','Missing':'No'},
            {'ID':'165.020H2_21','WaterDepth':'19','Year':'2021','Julian':'141','Missing':'No'}]
        b,qc=build_events(rs)
        self.assertEqual(qc['valid_matched_events'],1)
        self.assertEqual(qc['unmatched_event_groups'],1)

if __name__=='__main__':unittest.main()
