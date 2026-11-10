"""v100 physical clock null known truths, no actual organism responses."""
import unittest
import numpy as np
from original_UHSLC_2019_tide_solar import N,PERIODS
import harmonic_physics_null as x

class HarmonicClockExpectationTruth(unittest.TestCase):
    def test_same_source_day_bins_polar_and_date_edges(self):
        hours=np.arange(N)
        a=x.bins_at_native_local_solar_day(150.,hours)
        b=x.bins_at_native_local_solar_day(-150.,hours)
        self.assertEqual(len(a),N)
        self.assertTrue((a>=0).all())
        self.assertTrue((b>=0).all())
        self.assertNotEqual(a[0],b[0])
    def test_12h_semidiurnal_vs_24h_diurnal_low_water_clock_geometry(self):
        h=np.arange(N)
        sunlight=(h%24>=6)&(h%24<18)
        days=x.bins_at_native_local_solar_day(0,h)
        semi,_=x.daily_absolute_gauge_M(-np.cos(2*np.pi*h/12),sunlight,days)
        diurnal,_=x.daily_absolute_gauge_M(-np.cos(2*np.pi*h/24),sunlight,days)
        self.assertLess(semi,0.2)
        self.assertGreater(diurnal,.40)
        self.assertGreater(diurnal,semi+.25)
    def test_same_four_amplitude_source_with_random_phases_deterministic_seed(self):
        sun=(np.arange(N)%24>=6)&(np.arange(N)%24<18)
        days=x.bins_at_native_local_solar_day(0,np.arange(N))
        a={'M2':100.,'S2':50.,'K1':20.,'O1':10.}
        u=x.synthetic_harmonic_timecourses(a,sun,days,uid=7,nphase=4)
        v=x.synthetic_harmonic_timecourses(a,sun,days,uid=7,nphase=4)
        self.assertEqual(len(u),4)
        self.assertTrue(np.array_equal(u,v))
        self.assertTrue(np.all((u>=0)&(u<=1)))
    def test_original_site_geo_averaging_no_pseudoreplication(self):
        groups=[];generated={}
        for i in range(25):
            orig={'uid':i,'form_factor_F':.1+i*.05,
                  'opportunity':{'mean_daily_abs_M':.1+.01*i},
                  'harmonic_four_constituent_R2':.8,
                  'hourly_n':N}
            groups.append([orig])
            generated[i]={'null_M':np.linspace(.12+.005*i,.13+.005*i,4)}
        z=x.correlation_by_exact_geo_components(groups,generated,lambda s:True)
        self.assertEqual(z['status'],'DESCRIPTIVE_FOUR_HARMONIC_SURROGATE_COMPARISON')
        self.assertEqual(z['n_100km_geographic_source_clusters'],25)
        self.assertAlmostEqual(z['observed_F_vs_daily_abs_M_spearman'],1.)
        self.assertEqual(z['harmonic_phase_randomized_rho_distribution']['replicates'],4)
    def test_no_animal_and_no_real_phase_in_surrogate(self):
        self.assertIn('NO living organism',x.__doc__)
        self.assertIn('NO true original historical phase null',x.__doc__)
if __name__=='__main__':unittest.main()
