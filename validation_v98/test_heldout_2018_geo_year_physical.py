"""v98 2018 unseen calendar-year / unseen spatial-band prediction known truths."""
import unittest, math
import heldout_2018_geo_year_physical as q

def synthetic_site(uid,band_i):
    lat=(5+15*band_i) if band_i<4 else -(5+15*(band_i-4))
    return {'uid':uid,'latitude':lat,'longitude_signed':uid*1.,
        'harmonics_mm':{'M2':100,'S2':100,'K1':10,'O1':10},
        'form_factor_F':0.2+band_i/8,
        'opportunity':{'mean_daily_abs_M':.1+.06*math.log1p(.2+band_i/8)}}
class ObservedYearIsolation(unittest.TestCase):
    def test_limited_original_2018_source_support_does_not_score(self):
        groups=[[synthetic_site(i, i%8)] for i in range(1,21)]
        r=q.evaluate_heldout_geography_year(groups,{})
        self.assertEqual(r['source_gate'],'NO_CROSS_YEAR_REGIONAL_SUPPORT_LT25')
    def test_cross_year_no_2018_outcome_in_training_feature_path(self):
        groups=[[synthetic_site(i,i%8)] for i in range(1,65)]
        holdout={i:{'2018_physical':{'2018_mean_daily_abs_M':
                  .1+.06*math.log1p(.2+(i%8)/8)}} for i in range(1,65)}
        r=q.evaluate_heldout_geography_year(groups,holdout)
        self.assertEqual(r['source_gate'],'INDEPENDENT_2018_CALENDAR_YEAR_AND_UNSEEN_GEO_BANDS_EVALUATED')
        self.assertEqual(r['n_2018_heldout_geo_clusters'],64)
        self.assertTrue(r['2018_hourly_waterheights_never_used_in_training'])
        self.assertEqual(r['n_test_latitude_bands'],8)
        self.assertTrue(math.isfinite(r['M0_minus_M1_gain']))
    def test_source_group_features_single_grain(self):
        s=synthetic_site(8,3)
        row=q.features_row([s])
        self.assertEqual(row['F_mean'],s['form_factor_F'])
        self.assertEqual(row['Y_2019_original'],s['opportunity']['mean_daily_abs_M'])
        self.assertNotIn('Y_2018_original',row)
    def test_2018_is_earlier_not_future_as_frozen(self):
        self.assertEqual(q.V94_RUN,42616065580)
        self.assertEqual(q.V97_RUN,42729101678)
        self.assertIn('2018 is earlier',q.evaluate_heldout_geography_year(
           [[synthetic_site(i, i%8)] for i in range(1,50)],
           {i:{'2018_physical':{'2018_mean_daily_abs_M':.2}} for i in range(1,50)}
           )['source_and_scientific_boundary'])
if __name__=='__main__':unittest.main()
