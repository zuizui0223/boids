"""v103: ensure same 100-km cluster cannot leak from 2019 train into 2018 cross-band test."""
import unittest
import heldout_2018_geo_year_physical as m
def site(uid,lat):
    return {'uid':uid,'latitude':lat,'longitude_signed':(uid*37)%180,
       'harmonics_mm':{'M2':120,'S2':40,'K1':20,'O1':15},
       'form_factor_F':0.4+uid%9*.1,
       'opportunity':{'mean_daily_abs_M':0.14+(uid%9)*.013}}
class GeographicSourceOnlyGroup(unittest.TestCase):
    def test_group_band_frozen_from_all2019_not_2018_matching_subsource(self):
        # Group straddles 15°N: one source 2019 gauge is unavailable in 2018.
        # Spatial cluster must still be assigned to 2019 source-defined group band.
        coastal_pair=[site(1,14.9),site(2,15.1)]
        self.assertEqual(m.features_row(coastal_pair)['band'],'N_00_15')
        self.assertEqual(m.features_row([coastal_pair[1]])['band'],'N_15_30')
        groups=[coastal_pair]
        groups.extend([[site(i,5+15*(i%4))] for i in range(3,54)])
        valid={i:{'2018_physical':{'2018_mean_daily_abs_M':.12+(i%9)*.014}} for i in range(2,54)}
        r=m.evaluate_heldout_geography_year(groups,valid)
        self.assertEqual(r['source_gate'],'INDEPENDENT_2018_CALENDAR_YEAR_AND_UNSEEN_GEO_BANDS_EVALUATED')
        self.assertGreaterEqual(r['band_outcome_2018']['N_00_15']['n_test_100km_clusters'],1)
        self.assertEqual(r['n_2018_heldout_geo_clusters'],52)
if __name__=='__main__':unittest.main()
