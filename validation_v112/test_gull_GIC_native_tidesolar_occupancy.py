"""v112 known truths only. Synthetic test fixtures never enter original results.
Native 2020 external bird × static tidal-WETLAND source — not dry flat.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime,timedelta,timezone
import tempfile,unittest
from pathlib import Path
import numpy as np
import gull_GIC_native_tidesolar_occupancy as m
import real_2020_gull_GIC_native_pixels as pix

class NativeGullGIC2020KnownTruth(unittest.TestCase):
    def test_original_used_location_source_20km_not_movement_speed(self):
        dt=datetime(2020,6,1,12)
        center=(51.619722,3.681944)
        bird={('Larus argentatus','native_test_bird'):{
           dt:(dt,center[0],center[1]),
           dt+timedelta(hours=1):(dt+timedelta(hours=1),center[0],center[1])}}
        rows,proof=m.original_gull_position_opportunity(bird,radius=20.)
        self.assertEqual(len(rows),2)
        self.assertNotIn('original_km_per_hour',rows[0])
        self.assertTrue(proof['not_original_bird_activity_or_foraging'])
    def test_true_original_zero_RF_pixel_is_valid_eligible_not_nodata(self):
        t=datetime(2020,6,1,12,tzinfo=timezone.utc)
        e={'species':'Larus argentatus','private_bird':'unit_bird',
           'utc':t,'month':6,'latitude':51.6,'longitude':3.7,
           'source_original_GIC_valid_RF':0.0}
        tide={t-timedelta(minutes=20):.20,t:.4}
        _,qa=m.source_fourcell_only([e],tide,require_GIC_pixel=True)
        r=qa['source_genuine_GIC_RF_pixel_coverage']['Larus argentatus']
        self.assertEqual(r['native_GIC_2017_2019_valid_source_pixel_points'],1)
        self.assertEqual(r['original_native_GIC_pixel_coverage_fraction'],1)
        self.assertFalse(qa['original_raster_and_fourcell_gates_pass'])
    def test_original_raster_source_unavailable_not_zero_habitat(self):
        with self.assertRaisesRegex(ValueError,'STOP_V112'):
            m.original_gull_position_opportunity({},radius=50.)
        self.assertEqual(pix.MAX_NATIVE_SOURCE_TILES,4)
        self.assertEqual(pix.SOURCE_GIC_MAX_RADIUS_KM,30.)
    def test_source_admitted_4cell_RF50_bird_bootstrap_and_opposite_signs(self):
        grouped={}
        for species in ('Larus argentatus','Larus fuscus'):
            for b in range(8):
                for mon in (5,6):
                    for h in (2,3):
                        cc={}
                        for phase,sun in m.CELL_CLASSES:
                            if species=='Larus argentatus':
                                pixel=80. if (phase==1 and sun=='night') else 0.
                            else:
                                pixel=80. if (phase==-1 and sun=='night') else 0.
                            cc[(phase,sun)]=[
                                 {'source_original_GIC_valid_RF':pixel} for _ in range(8)]
                        grouped[(species,f'b{b}',mon,h)]=cc
        gate={'original_raster_and_fourcell_gates_pass':True}
        score=m.original_bird_bootstrap_GIC_occupancy(grouped,gate,threshold=50.)
        self.assertEqual(score['result_status'],
           'EXPLORATORY_TRUE_2020_GULL_NATIVE_GIC_SPATIAL_USE_TIDE_SOLAR_OBSERVED')
        self.assertEqual(score['original_species']['Larus argentatus']['original_independent_birds'],8)
        self.assertEqual(score['original_species']['Larus fuscus']['original_independent_birds'],8)
        self.assertGreater(score['species_contrast_independent_whole_bird_bootstrap_95pct'][0],0)
        alternate=m.original_bird_bootstrap_GIC_occupancy(grouped,gate,threshold=50.)
        self.assertEqual(score['species_contrast_true_original_bird_equal_D'],
                         alternate['species_contrast_true_original_bird_equal_D'])
    def test_no_source_gate_no_scored_species_even_if_native_pixels_available(self):
        data={'original_raster_and_fourcell_gates_pass':False}
        self.assertEqual(m.original_bird_bootstrap_GIC_occupancy({},data)['result_status'],
             'NOT_ESTIMATED_TWO_SPECIES_ORIGINAL_TIDE_SOLAR_PIXEL_SOURCE_GATE')
    def test_no_unfrozen_GIC_classification_threshold_or_phase_ghost(self):
        with self.assertRaisesRegex(ValueError,'STOP_V112_NEW_GIC_THRESHOLD'):
            m.individual_original_GIC_4cell_effects({},'Larus fuscus',threshold=75.)
        with self.assertRaisesRegex(ValueError,'STOP_V112_SOURCE_TIDE_GHOST'):
            m.source_fourcell_only([],{datetime(2020,5,1,tzinfo=timezone.utc):0.},phase_shift_days=5)
    def test_no_data_is_not_a_new_biotic_field_result(self):
        self.assertIn('POST v111 NEGATIVE',m.__doc__)
        self.assertIn('Not true tide-flat',m.__doc__)
if __name__=='__main__':unittest.main()
