"""v114 1km native GIC-geodesic ring and 2020 original bird bootstrap known truths.

Fixtures are synthetic for tests ONLY, not alleged original animal outcomes.
"""
from __future__ import annotations
from datetime import datetime,timedelta,timezone
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from pyproj import Geod
import unittest
import numpy as np
import authenticated_gull_local_wetland_background as geo
import local_enrichment_gull_BSTI as stat

def synthetic_cell(used,background):
    return [{'source_original_GIC_valid_RF':float(used),
             'v114_r1000_original_GIC_8ray_native_RF':tuple(background),
             'utc':datetime(2020,6,1+(i%3),12,tzinfo=timezone.utc)} for i in range(9)]

class Native2020GullRings(unittest.TestCase):
    def test_fixed_eight_geodesic_neighbors_are_real_distance_one_km(self):
        lat,lon=geo.fixed_geodesic_neighbors([51.6],[3.7],1000)
        self.assertEqual(lat.shape,(1,8))
        self.assertEqual(lon.shape,(1,8))
        self.assertAlmostEqual(lon[0,0],3.7,places=8)
        dist=Geod(ellps='WGS84').inv(
            np.full(8,3.7),np.full(8,51.6),lon[0],lat[0])[2]
        self.assertLess(np.max(abs(dist-1000.)),1e-4)
        with self.assertRaisesRegex(ValueError,'UNREGISTERED'):
            geo.fixed_geodesic_neighbors([51.6],[3.7],4000)
    def test_zero_is_genuine_GIC_pixel_not_a_source_mask(self):
        orig=np.zeros((10,10),dtype=np.uint8)
        orig[5,6]=75
        orig[1,1]=255
        transform=from_origin(3.0,52.,.01,.01)
        p={'driver':'GTiff','count':1,'width':10,'height':10,'dtype':'uint8',
           'crs':'EPSG:4326','transform':transform,'nodata':255}
        with MemoryFile() as mem:
            with mem.open(**p) as dst:dst.write(orig,1)
            with mem.open() as src:
                lat=[51.945,51.985,50.]
                lon=[3.065,3.015,3.065]
                vals,q=geo.native_pixel_values_vector(src,lat,lon,transform)
        self.assertEqual(vals[0],75)
        self.assertTrue(np.isnan(vals[1]))
        self.assertTrue(np.isnan(vals[2]))
        self.assertEqual(q['source_points_native_valid_pixels'],1)
        self.assertEqual(q['source_points_native_masked_or_outside'],2)
    def test_balanced_local_enrichment_and_solar_tide_factorial(self):
        c={(1,'day'):synthetic_cell(0,[0]*8),
           (1,'night'):synthetic_cell(80,[0]*8),
           (-1,'day'):synthetic_cell(0,[0]*8),
           (-1,'night'):synthetic_cell(0,[0]*8)}
        x=stat.per_group_BSTI_local_Z(c,1000)
        self.assertEqual(x['B_balanced_spatial_source'],.25)
        self.assertEqual(x['S_night_minus_day'],.5)
        self.assertEqual(x['T_rising_minus_falling'],.5)
        self.assertEqual(x['I_tide_by_sun'],1.)
        # Exact same used score in ALL cells, but 8 neighbors also high:
        # relative-location enrichment must correctly be zero everywhere.
        y={cell:synthetic_cell(80,[80]*8) for cell in c}
        b=stat.per_group_BSTI_local_Z(y,1000)
        self.assertTrue(all(abs(v)<1e-12 for v in b.values()))
    def test_bird_cluster_bootstrap_independent_from_eight_ray_count(self):
        groups={}
        for s in ('Larus argentatus','Larus fuscus'):
            for bird in range(8):
                for month in (5,6):
                    for height in (2,3):
                        cells={}
                        for phase,day in ((1,'day'),(1,'night'),(-1,'day'),(-1,'night')):
                            used=80 if (s=='Larus argentatus' and phase==1 and day=='night') or (
                                        s=='Larus fuscus' and phase==-1 and day=='night') else 0
                            cells[(phase,day)]=synthetic_cell(used,[0]*8)
                        groups[(s,f'unit_tag_{bird}',month,height)]=cells
        gate={'original_raster_and_fourcell_gates_pass':True}
        v=stat.summarize_original_bird_local_Z(groups,gate,1000)
        self.assertEqual(v['source_status'],'EXPLORATORY_TRUE_2020_ORIGINAL_LOCAL_NEIGHBOR_ENRICHMENT_BSTI_EVALUATED')
        self.assertEqual(v['original_bird_species_location_enrichment']['Larus argentatus'][
            'native_original_2020_true_tagged_birds'],8)
        self.assertGreater(v['true_original_bird_species_contrasts']['I_tide_by_sun'][
            'original_independent_bird_bootstrap95'][0],0)
    def test_missing_neighborhood_not_negatively_scored(self):
        d=synthetic_cell(0,[80]*8)
        for item in d:item['v114_r1000_original_GIC_8ray_native_RF']=None
        c={(1,'day'):d,(1,'night'):d,(-1,'day'):d,(-1,'night'):d}
        with self.assertRaises((ValueError,TypeError)):
            stat.per_group_BSTI_local_Z(c,1000)
        with self.assertRaisesRegex(ValueError,'UNFROZEN_LOCAL_RADIUS'):
            stat.per_group_BSTI_local_Z(c,999)
    def test_source_preexisting_mayjuly_replay_fails_on_synthetic_source(self):
        fake={'original_raster_and_fourcell_gates_pass':False}
        with self.assertRaisesRegex(ValueError,'PREVIOUS_MATCHED_TWO_GULL_SOURCE_FAILS'):
            stat.verify_original_v113_MayJuly_source_then_effect({},fake)
    def test_fixed_source_2020_and_8ray_are_not_forage_or_causal_choices(self):
        self.assertEqual(geo.RADII_M,(500,1000,2000))
        self.assertEqual(geo.EXPECTED_N_RAYS,8)
        self.assertIn('not actual accessible alternative habitats',geo.__doc__)
        self.assertIn('not wet/dry tidalflat accessibility',stat.__doc__)
if __name__=='__main__':unittest.main()
