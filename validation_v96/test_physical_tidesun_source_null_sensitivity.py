"""v96 known truth: do not infer activity or claim independent replication from post-v95 sensitivity."""
from copy import deepcopy
import tempfile, json, unittest
import physical_tidesun_source_null_sensitivity as q

def fake(uid,lat,lon,F):
    return {'uid':uid,'latitude':lat,'longitude_signed':lon,'form_factor_F':F,
       'opportunity':{'n_valid_day_low_2':200,'mean_daily_abs_M':.2+F/20,
           'mean_daily_abs_M_low4':.19+F/20,'null_random_hour_baseline_abs_M':.14,
           'frac_days_absolute_M_ge_0_25':.3},
       'matched_fraction_delta_low_sun_ge_1h':.7}

class SourceBounds(unittest.TestCase):
    def test_cluster_and_null_subtraction_same_source(self):
        rows=q.cluster_environment([fake(1,12,20,.5),fake(2,12,20.2,.6),fake(3,-20,120,2)])
        self.assertEqual(len(rows),2)
        self.assertEqual(sum(x['n_eligible_sites'] for x in rows),3)
        self.assertAlmostEqual(rows[0]['actual_minus_random_hour_reference_M'],
                               rows[0]['mean_abs_M']-rows[0]['random_hour_sampling_reference_M'])
    def test_each_matched_endpoint_uses_same_geo_unit(self):
        rows=[]
        for i in range(20):
            a=fake(i+1,(i%5)*12+2 if i<10 else -((i%5)*12+2),i*15,.2+(i%4)*.4)
            rows.append(q.cluster_environment([a])[0])
        res=q.exact_permutation_in_band(rows,'mean_abs_M',nperm=20)
        self.assertEqual(res['n_geo_clusters'],20)
        self.assertEqual(res['permutations'],20)
        self.assertTrue(0<res['band_restricted_permutation_p_exploratory']<=1)
    def test_source_failures_separate_http_transport_not_biological_null(self):
        raw={'N_75_90':{'source_failures':[{'uid':2,'errors':[{'provider':'primary','http_status':404}]}]},
             'S_15_30':{'source_failures':[{'uid':3,'errors':[{'provider':'p','http_status':429}]},
                   {'uid':4,'errors':[{'provider':'p','failure':'timed out'}]}]}}
        out=q.source_failure_summary(raw)
        self.assertEqual(out['n_total'],3)
        self.assertEqual(out['by_cause']['rate_limited_HTTP429'],1)
        self.assertEqual(out['by_cause']['HTTP404_missing_source'],1)
        self.assertEqual(out['by_cause']['transport_timeout'],1)
    def test_no_bird_activity_claim(self):
        self.assertIn('no independent wild animal inference',q.__doc__)
if __name__=="__main__":unittest.main()
