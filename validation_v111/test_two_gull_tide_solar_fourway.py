"""v111 precise source gates, no fixed-station 2020 bird movement result synthesized."""
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
from collections import defaultdict
import unittest, math
import numpy as np
import two_gull_tide_solar_fourway as m
import original_2020_gull_RWS_source as g

class RealTideSunSourceKnownTruth(unittest.TestCase):
    def test_nearest_native_RWS_10min_absolute_and_slope_no_interpolation(self):
        base=datetime(2020,6,1,1,tzinfo=timezone.utc)
        series={base+timedelta(minutes=10*k):.5+k*.02 for k in range(20)}
        source=sorted(series)
        good=m.nearest_original_rws(series,source,base+timedelta(minutes=30))
        self.assertEqual(good['source_phase'],1)
        self.assertEqual(good['source_height_bin'],int(math.floor(series[base+timedelta(minutes=30)]/.25)))
        self.assertAlmostEqual(good['native_real_20min_slope_mph'],.12)
        before20_missing=dict(series)
        del before20_missing[base+timedelta(minutes=10)]
        fail=m.nearest_original_rws(before20_missing,sorted(before20_missing),base+timedelta(minutes=30))
        self.assertIsNone(fail)
        self.assertIsNone(m.nearest_original_rws(series,source,base+timedelta(days=3)))
    def test_sun_at_real_UTC_native_position_and_no_twilight_claim(self):
        d=datetime(2020,6,21,12,tzinfo=timezone.utc)
        n=datetime(2020,6,21,0,tzinfo=timezone.utc)
        self.assertEqual(m.sunlight_label_at_native_gps(d,51.62,3.68),'day')
        self.assertEqual(m.sunlight_label_at_native_gps(n,51.62,3.68),'night')
    def test_one_original_bird_hour_movement_geometry_and_no_50_bird_pseudorep(self):
        center=g.GEO_PRIMARY
        hours={datetime(2020,6,1,1):(datetime(2020,6,1,1,0),center[0],center[1]),
               datetime(2020,6,1,2):(datetime(2020,6,1,2,0),center[0]+.01,center[1])}
        event,source=m.original_movement_opportunities({('Larus argentatus','testbird'):hours})
        self.assertEqual(len(event),1)
        self.assertGreater(event[0]['original_km_per_hour'],0)
        self.assertEqual(source['source_unique_original_birds_by_species_with_any_movement_opportunities']['Larus argentatus'],1)
    def test_no_complete_fourcell_does_not_calculate_biological_Y(self):
        dt=datetime(2020,6,1,12,tzinfo=timezone.utc)
        src=[{'taxon':'Larus argentatus','bird':'G','month':6,
              'original_UTC':dt,'GPS_departure_lat':51.62,
              'GPS_departure_lon':3.68,'original_km_per_hour':10.}]
        tide={dt-timedelta(minutes=20):.2,dt:.5}
        groups,gate=m.fourway_original_source(src,tide)
        self.assertFalse(gate['source_each_species_admitted'])
        self.assertEqual(m.score_if_original_two_species_admitted(groups,gate)['status'],
                         'NOT_ESTIMATED_ORIGINAL_BIOLOGICAL_SOURCE_GATE')
    def test_source_frozen_valid_fourcell_can_be_positive_negative_or_zero(self):
        adm=defaultdict(dict)
        for taxon in ('Larus argentatus','Larus fuscus'):
            for b in range(8):
                for mon in (5,6):
                    for h in (1,2,3):
                        cells={}
                        for phase,daylight in m.CELL_CLASSES:
                            if taxon=='Larus argentatus':
                                speed=10 if phase==1 and daylight=='night' else 1
                            else:speed=10 if phase==-1 and daylight=='night' else 1
                            cells[(phase,daylight)]=[
                                {'original_km_per_hour':speed,
                                 'original_UTC':datetime(2020,mon,1+i%3,12,tzinfo=timezone.utc)}
                                for i in range(6)]
                        adm[(taxon,f'b{b}',mon,h)]=cells
        gate={'source_each_species_admitted':True}
        x=m.score_if_original_two_species_admitted(adm,gate)
        self.assertEqual(x['status'],'EXPLORATORY_REAL_2020_TWO_SPECIES_MOVEMENT_PROXY_EFFECT_ESTIMATED')
        self.assertEqual(x['species_source_results']['Larus argentatus']['true_original_independent_birds'],8)
        self.assertEqual(x['species_source_results']['Larus fuscus']['true_original_independent_birds'],8)
        self.assertGreater(x['primary_two_species_bird_equal_D_difference'],0)
        self.assertGreater(x['primary_two_species_original_bird_cluster_bootstrap95'][0],0)
    def test_2020_month_RWS_no_unmeasured_QC_80percent(self):
        base=datetime(2020,5,1,tzinfo=timezone(timedelta(hours=1)))
        data=[{'Tijdstip':(base+timedelta(minutes=10*i)).isoformat(),
               'Meetwaarde':{'Waarde_Numeriek':40.}} for i in range(500)]
        native={'Succesvol':True,'WaarnemingenLijst':[{
          'AquoMetadata':{'Grootheid':{'Code':'WATHTE'},
               'Eenheid':{'Code':'cm'},'Hoedanigheid':{'Code':'NAP'}},
          'MetingenLijst':data}]}
        with self.assertRaisesRegex(g.OriginalSourceStop,'LT80PCT'):
            g.parse_official_RWS_month(native,5)
    def test_science_does_not_claim_foraging_or_internal_clock(self):
        self.assertIn('NOT true',m.__doc__)
        self.assertIn('no',g.__doc__.lower())
if __name__=='__main__':unittest.main()
