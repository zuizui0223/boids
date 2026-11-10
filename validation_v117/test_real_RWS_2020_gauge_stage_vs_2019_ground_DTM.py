"""v117 physical math known-truth only; synthetic values are NEVER reported as original data."""
from __future__ import annotations
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
import unittest
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
import real_RWS_2020_gauge_stage_vs_2019_ground_DTM as q
from original_2019_Oosterschelde_DTM_ground_source import WGS

class OriginalRWSGroundTideMathTruth(unittest.TestCase):
    def test_vertical_water_upshift_can_only_reduce_conditional_above_stage_fraction(self):
        utc=datetime(2020,5,1,tzinfo=timezone.utc)
        sea={utc+timedelta(hours=i):v for i,v in enumerate([-1,1,-1,1])}
        with patch.object(q,'_astral_source_solar_days',return_value=(
             np.array([True,False,True,False]),np.array([False,True,False,True]))):
            a=q.physical_native_2019_ground_above_2020_real_gauge_source(
                np.array([-.25,0,.25]),sea,51.6,3.7)
        self.assertEqual(a['source_status'],
            'CONDITIONAL_RWS_GAUGE_STAGE_ABOVE_ORIGINAL_2019_GROUND_PROPORTION')
        d=a['genuine_RWS_stage_uncertainty_scenarios']
        self.assertGreaterEqual(d['-0.2']['native_ground_pixels_mean_above_GAUGE_stage_proportion_all_hours'],
                                d['0.0']['native_ground_pixels_mean_above_GAUGE_stage_proportion_all_hours'])
        self.assertGreaterEqual(d['0.0']['native_ground_pixels_mean_above_GAUGE_stage_proportion_all_hours'],
                                d['0.2']['native_ground_pixels_mean_above_GAUGE_stage_proportion_all_hours'])
        self.assertEqual(a['actual_tide_flat_exposure_or_bird_activity'],'NOT_ESTIMATED')
    def test_original_survey_zero_ground_is_valid_height_not_missing_and_island_dry(self):
        utc=datetime(2020,5,1,tzinfo=timezone.utc)
        t={utc+timedelta(hours=i):.5 for i in range(4)}
        with patch.object(q,'_astral_source_solar_days',return_value=(
             np.array([1,1,0,0],dtype=bool),
             np.array([0,0,1,1],dtype=bool))):
            res=q.physical_native_2019_ground_above_2020_real_gauge_source(
                [0.,1.,5.,10.],t,51.6,3.7)
        self.assertEqual(res['genuine_RWS_stage_uncertainty_scenarios']['0.0'][
             'native_ground_pixels_mean_above_GAUGE_stage_proportion_all_hours'],.75)
    def test_native_original_2020_clock_hour_no_interpolation_and_threshold(self):
        t0=datetime(2020,5,1,tzinfo=timezone.utc)
        one={t0+timedelta(minutes=10*i):float(i) for i in range(144*31)}
        with self.assertRaisesRegex(q.OriginalSourceStop,'TOO_FEW'):
            q._real_hourly_RWS_source(one)
        big={t0+timedelta(minutes=10*i):float(i) for i in range(144*100)}
        r=q._real_hourly_RWS_source(big)
        self.assertTrue(len(r)>2000)
        self.assertTrue(all(t.minute==0 for t in r))
        self.assertLess(len(r),len(big))
    def test_exact_original_DTM_5m_pixels_match_public_v116_square_source(self):
        p={'driver':'GTiff','count':1,'dtype':'float32','width':25,'height':25,
           'crs':'EPSG:28992','transform':from_origin(160000,400000,5.,5.),
           'nodata':-9999.}
        z=np.full((25,25),-.1,dtype=np.float32);z[10,10]=-9999
        with MemoryFile() as m:
            with m.open(**p) as ds:ds.write(z,1)
            with m.open() as ds:
                lo,la=WGS.transform(160060,399940)
                a,meta=q._extract_fixed_original_square(ds,{'lat':la,'lon':lo})
                self.assertEqual(len(a),440)
                self.assertEqual(meta['n_source_total_native_square_pixels'],441)
                self.assertEqual(meta['native_horizontal_cell_area_square_metres'],25.)
    def test_original_source_gauge_assignments_frozen_and_2019_SHA(self):
        self.assertEqual(q.SOURCE_GAUGE_FIXED_ASSIGNMENT['Roggenplaat shoal'],q.NATIVE_SECONDARY)
        self.assertEqual(q.SOURCE_GAUGE_FIXED_ASSIGNMENT['Roompotsluis Buiten gauge'],q.NATIVE_PRIMARY)
        self.assertEqual(len(q.EXPECTED_DTM_SOURCE_SHA256),64)
        self.assertEqual(q.EXPECTED_SOURCE_BYTES,34799884)
    def test_actual_2020_sun_day_night_used_without_calendar_inference(self):
        sun=[datetime(2020,6,21,12,tzinfo=timezone.utc),
             datetime(2020,6,21,0,tzinfo=timezone.utc)]
        day,night=q._astral_source_solar_days(sun,51.619722,3.681944)
        self.assertEqual(day.tolist(),[True,False])
        self.assertEqual(night.tolist(),[False,True])
if __name__=='__main__':unittest.main()
