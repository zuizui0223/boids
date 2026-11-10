"""v113 known truths: balanced 2x2 factorial B/S/T/I algebra.
No original bird identities or biological outcomes in test fixtures.
"""
import unittest
from datetime import datetime,timezone
from collections import defaultdict
import orthogonal_tide_solar_gull_GIC_used_pixel as q

def cells(fd,fn,ed,en):
    return {(1,'day'):[{'source_original_GIC_valid_RF':fd} for _ in range(8)],
      (1,'night'):[{'source_original_GIC_valid_RF':fn} for _ in range(8)],
      (-1,'day'):[{'source_original_GIC_valid_RF':ed} for _ in range(8)],
      (-1,'night'):[{'source_original_GIC_valid_RF':en} for _ in range(8)]}
def fixture():
    groups={}
    for taxon in ('Larus argentatus','Larus fuscus'):
        for bird in range(8):
            for month in (5,6):
                for height in (1,2):
                    group=cells(0,100,0,0) if taxon=='Larus argentatus' else cells(0,0,0,100)
                    groups[(taxon,f'b{bird}',month,height)]=group
    source={'original_raster_and_fourcell_gates_pass':True,
            'per_species_native_source':{
              s:{'original_2020_native_birdmonth_0p25m_fourcell_groups':32,
                 'original_2020_months_with_frozen_fourcell_support':[5,6]}
              for s in ('Larus argentatus','Larus fuscus')}}
    return groups,source

class Real2020SolarTideAlgebra(unittest.TestCase):
    def test_pure_solar_without_tide_interaction(self):
        r=q.orthogonal_coefficients_of_original_4cells(cells(0,100,0,100))
        self.assertAlmostEqual(r['B_balanced_spatial_source'],.5)
        self.assertAlmostEqual(r['S_night_minus_day'],1.)
        self.assertAlmostEqual(r['T_rising_minus_falling'],0.)
        self.assertAlmostEqual(r['I_tide_by_sun'],0.)
    def test_pure_tide_without_solar_interaction(self):
        r=q.orthogonal_coefficients_of_original_4cells(cells(100,100,0,0))
        self.assertAlmostEqual(r['B_balanced_spatial_source'],.5)
        self.assertAlmostEqual(r['S_night_minus_day'],0.)
        self.assertAlmostEqual(r['T_rising_minus_falling'],1.)
        self.assertAlmostEqual(r['I_tide_by_sun'],0.)
    def test_only_one_cell_has_nonzero_result(self):
        r=q.orthogonal_coefficients_of_original_4cells(cells(0,100,0,0))
        self.assertAlmostEqual(r['B_balanced_spatial_source'],.25)
        self.assertAlmostEqual(r['S_night_minus_day'],.5)
        self.assertAlmostEqual(r['T_rising_minus_falling'],.5)
        self.assertAlmostEqual(r['I_tide_by_sun'],1.)
    def test_full_native_bird_source_not_fixes_and_taxon_contrast(self):
        groups,gate=fixture()
        result=q.summarize_source_orthogonal_BSTI(groups,gate)
        self.assertEqual(result['status'],'EXPLORATORY_FROZEN_FOURCELL_ORIGINAL_SOURCE_BSTI_ESTIMATED')
        self.assertEqual(result['individual_original_species']['Larus argentatus']['original_independent_native_GPS_birds'],8)
        contrast=result['independent_two_species_contrasts']
        self.assertAlmostEqual(contrast['B_balanced_spatial_source'][
            'original_bird_equal_taxon_contrast_Larus argentatus_minus_Larus fuscus'],0.)
        self.assertAlmostEqual(contrast['S_night_minus_day'][
            'original_bird_equal_taxon_contrast_Larus argentatus_minus_Larus fuscus'],0.)
        self.assertAlmostEqual(contrast['I_tide_by_sun'][
            'original_bird_equal_taxon_contrast_Larus argentatus_minus_Larus fuscus'],2.)
        self.assertGreater(contrast['T_rising_minus_falling'][
            'original_tagged_bird_bootstrap_CI95'][0],0)
    def test_known_previous_result_must_pass_source_replay_before_new_values(self):
        groups,gate=fixture()
        with self.assertRaisesRegex(ValueError,'OLD_V112_ORIGINAL_INTERACTION'):
            q.verify_previous_v112_original_replay(groups,gate)
    def test_never_guess_new_year_or_bird_and_months_during_inference(self):
        self.assertEqual(q.FIXED_SOURCE_MONTHS_COMMON,(5,6,7))
        self.assertEqual(q.KNOWN_ORIGINAL_V112_STRATA['Larus fuscus'],71)
        self.assertEqual(q.KNOWN_ORIGINAL_V112_GPS['Larus argentatus'],18660)
        self.assertIn('actual 2020 two gull species',q.__doc__.lower())
if __name__=='__main__':unittest.main()
