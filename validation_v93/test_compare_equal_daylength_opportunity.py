"""Pure real-solar/original-source-format tests; these tests contain NO fabricated ecological outcomes."""
import unittest
from datetime import date,timedelta
from statistics import mean
from copy import deepcopy
from unittest.mock import patch
import compare_equal_daylength_opportunity as q

def fixture_site():
    day=date(2019,1,1)
    rows=[]
    for i in range(365):
        d=day+timedelta(days=i)
        if d==q.SOLSTICE_2019:continue
        value=(i%6)/12.
        rows.append({'date':d.isoformat(),'O':.5+value,'A':.5,
                     'M':value,'joint_original_hours':int(i%7)+1})
    return {'uid':77,'station':'SYNTHETIC_NO_REAL_GAUGE','latitude':42.,
        'longitude':0.,'country':'synthetic','record_id':101,
        'harmonics':{'regime':'semidiurnal','F':.1,'four_constituent_R2':.93},
        'physical':{'daily':rows,'n_valid_days':len(rows),'daily_mean_abs_M':
                    mean(abs(z['M']) for z in rows),'source_hours':8760,
                    'sunlit_low_hours':900,'dark_low_hours':1100}}

class EqualDaylengthKnownTruth(unittest.TestCase):
    def test_annual_same_daylength_is_solar_geometry_not_integer_hour_bin(self):
        a=q._physical_daylength_min(42,0,date(2019,4,10))
        b=q._physical_daylength_min(42,0,date(2019,9,1))
        self.assertGreater(a,700.)
        self.assertGreater(b,700.)
        self.assertLess(abs(a-b),150)
    def test_one_to_one_match_only_2019_opposite_arms(self):
        pairs=q.daylength_matching(fixture_site())
        self.assertGreaterEqual(len(pairs),50)
        self.assertEqual(len({p['before'] for p in pairs}),len(pairs))
        self.assertEqual(len({p['after'] for p in pairs}),len(pairs))
        for p in pairs:
            self.assertLessEqual(p['daylength_diff_min'],10)
            self.assertGreaterEqual((date.fromisoformat(p['after'])-
                                     date.fromisoformat(p['before'])).days,14)
            self.assertGreaterEqual(p['absolute_low_sunlit_hours_difference'],0)
    def test_source_derived_daily_mean_and_no_tampered_M(self):
        f=fixture_site()
        self.assertEqual(len(q.source_daily_audit(f)),364)
        bad=deepcopy(f)
        bad['physical']['daily'][0]['M']+=.1
        with self.assertRaisesRegex(ValueError,'source algebra'):q.source_daily_audit(bad)
        bad2=deepcopy(f)
        bad2['physical']['daily'][0]['date']=bad2['physical']['daily'][1]['date']
        with self.assertRaisesRegex(ValueError,'duplicated'):q.source_daily_audit(bad2)
    def test_four_rank_exact_test_independent_of_synthetic_biological_data(self):
        p=q.spearman_exact([1,2,3,4],[1,2,3,4])
        self.assertEqual(p['permutations'],24)
        self.assertAlmostEqual(p['rho'],1)
        self.assertAlmostEqual(p['two_sided_exact_p_exploratory'],2/24)
    def test_cancellation_measure_on_true_solar_year_subset(self):
        s=q.site_summary(fixture_site())
        self.assertTrue(0<=s['cancellation_fraction_within_days']<=1)
        self.assertGreater(s['matched_equal_daylength_pairs'],50)
        self.assertTrue(0<=s['matched_fraction_at_least_1hr']<=1)
if __name__=='__main__':unittest.main()
