"""v115 source-bound movement-step alternatives truth checks only — no invented field response."""
from __future__ import annotations
from datetime import datetime,timedelta,timezone
import unittest
import numpy as np
from pyproj import Geod
import original_GIC_equal_step_rotated_destinations as g
import true_original_gull_equal_step_BSTI as m

GEOD=Geod(ellps='WGS84')
def cell(value,other):
    return [{'v115_real_2020_GPS_destination_native_GIC_RF':float(value),
      'v115_7_original_same_step_rotated_GIC_RF':tuple(other),
      'original_UTC':datetime(2020,6,1+(i%3),12,tzinfo=timezone.utc)}
      for i in range(8)]

class RealOriginal2020GullStepControls(unittest.TestCase):
    def test_seven_alternative_bearings_exact_original_step_length(self):
        la0,lo0,la1,lo1=51.61,3.68,51.62,3.70
        lat,lon,length,az=g.original_geodesic_same_step_length_alternatives(
            [la0],[lo0],[la1],[lo1])
        self.assertEqual(lat.shape,(1,7));self.assertEqual(lon.shape,(1,7))
        self.assertEqual(g.N_ALTERNATIVE_ENDPOINTS,7)
        azs,_,d=GEOD.inv(np.full(7,lo0),np.full(7,la0),lon[0],lat[0])
        self.assertTrue(np.allclose(d,length[0],atol=0.001))
        expected=(az[0]+g.ROTATIONS_DEGREES)%360
        self.assertTrue(np.allclose((azs+360)%360,expected,atol=1e-5))
    def test_zero_original_movement_control_not_faked(self):
        lat,lon,dist,az=g.original_geodesic_same_step_length_alternatives(
            [51.61],[3.68],[51.61],[3.68])
        self.assertAlmostEqual(dist[0],0.)
        self.assertTrue(np.allclose(lat,51.61,atol=1e-9))
        self.assertTrue(np.allclose(lon,3.68,atol=1e-9))
    def test_balanced_fourcell_step_local_source_math(self):
        events={(1,'day'):cell(0,[0]*7),
                (1,'night'):cell(80,[0]*7),
                (-1,'day'):cell(0,[0]*7),
                (-1,'night'):cell(0,[0]*7)}
        x=m.true_original_group_coefficients(events)
        self.assertAlmostEqual(x['B_balanced_endpoint_enrichment'],.25)
        self.assertAlmostEqual(x['S_solar_night_minus_day'],.5)
        self.assertAlmostEqual(x['T_tide_rising_minus_falling'],.5)
        self.assertAlmostEqual(x['I_tide_by_solar'],1.)
        y={c:cell(80,[80]*7) for c in events}
        self.assertTrue(all(abs(v)<1e-12 for v in m.true_original_group_coefficients(y).values()))
    def test_exact_true_bird_cluster_bootstrap_not_7x_intervals(self):
        group={}
        for sp in ('Larus argentatus','Larus fuscus'):
            for bird in range(8):
                for month in (5,6):
                    for height in (1,2):
                        c={}
                        for phase,day in m.CELL_CLASSES:
                            val=80 if ((sp=='Larus argentatus' and phase==1 and day=='night') or
                                       (sp=='Larus fuscus' and phase==-1 and day=='night')) else 0
                            c[(phase,day)]=cell(val,[0]*7)
                        group[(sp,f'unit_bird_{bird}',month,height)]=c
        src={'original_bird_and_all_GIC_source_admitted':True,
           'original_source_all_species':{
             s:{'source_fourcell_true_bird_month_height_strata':32}
             for s in ('Larus argentatus','Larus fuscus')}}
        x=m.evaluate_real_original_bird_two_gull_step_BSTI(group,src)
        self.assertEqual(x['status'],'EXPLORATORY_ACTUAL_2020_GULL_GIC_EQUAL_STEP_GEOGRAPHIC_ENRICHMENT_EVALUATED')
        self.assertEqual(x['genuine_source_individual_gull_species']['Larus argentatus']['original_true_independent_bird_n'],8)
        self.assertGreater(x['original_genuine_2species_contrasts']['I_tide_by_solar']['original_independent_2020_bird_bootstrap_95'][0],0)
    def test_prior_real_native_2020_gull_source_required_before_new_result(self):
        with self.assertRaisesRegex(ValueError,'OLD_2020_REAL_GULL_TIDE_SUN_MOVEMENT_SOURCE'):
            m.hard_replay_original_v111_genuine_movement_effects([],{})
        x=m.evaluate_real_original_bird_two_gull_step_BSTI({},{
            'original_bird_and_all_GIC_source_admitted':False})
        self.assertEqual(x['status'],'NOT_ESTIMATED_GENUINE_2020_2SPECIES_RWS_7ROTATED_GIC_SOURCE_GATE')
    def test_source_ghost_shift_cannot_be_adapted_to_favorable_Y(self):
        with self.assertRaisesRegex(ValueError,'UNFROZEN_REAL_RWS_GHOST_SHIFT'):
            m.source_GIC_seven_control_coverage_on_RWS_matched([],{datetime(2020,6,1,tzinfo=timezone.utc):0},5)
        self.assertEqual(m.COMMON_SOURCE_MONTHS,(5,6,7))
        self.assertTrue(g.PUBLIC_GIC_IS_TIDAL_WETLAND_NOT_TRUE_DRY_TIDAL_FLAT)
    def test_seven_alternatives_not_independent_animals(self):
        self.assertIn('true accessible feeding patches',g.__doc__.lower())
        self.assertIn('not real animal',m.__doc__.lower())
if __name__=="__main__":unittest.main()
