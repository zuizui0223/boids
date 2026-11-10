"""v108 source QA known truths; original biological effects are never synthesized."""
import json,tempfile,unittest
from pathlib import Path
import aggregate_genuine_all160_GIC_2019 as q

def one(uid):
    p={k:0.2 if 'fraction' in k else (200 if k.startswith('n_valid') else 5.)
       for k in q.MEASURES}
    return {'original_2019_UHSLC_station_ID':uid,
        'original_2019_observed_low_tide_x_sun_daily_absM':.14,
        'original_2019_measured_tidal_form_F':.4,
        q.GIC_VALUE_KEY:p,'source_status':q.COMPLETE}
def pilot(uid):
    a=one(uid)
    return {'2019_original_UHSLC_station_id':uid,
        '2019_measured_gauge_mean_abs_M':a['original_2019_observed_low_tide_x_sun_daily_absM'],
        '2019_measured_gauge_form_factor_F':a['original_2019_measured_tidal_form_F'],
        q.PILOT_VALUE_KEY:a[q.GIC_VALUE_KEY],
        'source_status':'ORIGINAL_2019_GIC_PROBABILITY_BUFFER_ADMITTED'}

class RealSourceValidationTruth(unittest.TestCase):
    def test_incomplete_global_tile_shard_frame_stops(self):
        with self.assertRaisesRegex(ValueError,'ALL_16_ORIGINAL'):
            q.source_census([])
    def test_original_eight_pilot_identity_replay_equal_pixels(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for uid in range(1,9):
                f=Path(d)/f'{uid}.json'
                f.write_text(json.dumps(pilot(uid)));paths.append(f)
            z=q.pilot_exact_replay([one(uid) for uid in range(1,9)],paths)
            self.assertEqual(len(z),8)
            self.assertEqual(sum(r['native_GIC_tile_repeated_source_fields'] for r in z),32)
    def test_one_changed_original_pilot_pixel_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for uid in range(1,9):
                x=pilot(uid)
                if uid==3:x[q.PILOT_VALUE_KEY]['n_valid_original_GIC_pixels_10km']+=1
                f=Path(d)/f'{uid}.json'
                f.write_text(json.dumps(x));paths.append(f)
            with self.assertRaisesRegex(ValueError,'RASTER_PIXELS_CHANGED'):
                q.pilot_exact_replay([one(uid) for uid in range(1,9)],paths)
    def test_spatial_environmental_correlation_is_not_biological(self):
        group=[]
        for k in range(10):
            group.append({'region_source_status':'FULL_SOURCE_COVERAGE',
              'mean_static_GIC_tidalwetland_RF_agreement_0_100':10.+k,
              'mean_fraction_valid_10km_pixels_RF_agreement_ge50':.01+k*.08,
              'mean_source_year_2019_F':.2+k*.2,
              'mean_2019_source_daily_abs_M':.05+k*.015})
        x=q._summarize_associations(group)['fully_original_10km_area_covered_100km_coasts_only']
        self.assertAlmostEqual(x['Spearman_2019_physical_tide_form_F_vs_source_static_wetland_RF50_descriptive'],1)
        self.assertEqual(x['geographical_inference_for_biological_time_niche'],'NONE_NOT_MEASURED')
if __name__=='__main__':unittest.main()
