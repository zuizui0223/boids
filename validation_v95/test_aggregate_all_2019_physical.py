"""v95 source/geometry/aggregation known truths only; no fake external animal result."""
import unittest, math, json, tempfile
from pathlib import Path
import numpy as np
import aggregate_all_2019_physical as p
def fake(uid,lat,lon,y=.2,F=.5,band=None):
    h={'M2':100.,'S2':50.,'K1':20.,'O1':20.}
    return {'uid':uid,'latitude':lat,'longitude_signed':lon,
       'form_factor_F':F,'regime':'mixed_semidiurnal',
       'harmonic_four_constituent_R2':.8,'harmonics_mm':h,
       'opportunity':{'mean_daily_abs_M':y,'n_valid_day_low_2':300,
         'null_random_hour_baseline_abs_M':.15},
       'matched_fraction_delta_low_sun_ge_1h':.8,'qc':'ADMITTED_2019_ORIGINAL_HOURLY_PHYSICAL'}
class MacroPhysicsTruth(unittest.TestCase):
    def test_geographic_cluster_one_source_not_pseudorep_independent(self):
        rows=[fake(1,0,0),fake(2,0,.5),fake(3,0,5)]
        groups=p.coastal_clusters(rows)
        self.assertEqual(len(groups),2)
        self.assertEqual(sorted(len(z) for z in groups),[1,2])
    def test_rank_monotonic_and_outofband_model(self):
        self.assertAlmostEqual(p.spearman([1,2,3,4],[1,2,3,4]),1)
        rows=[]
        for k in range(24):
            d=fake(k+1,(-1 if k%2 else 1)*(k%6*10+2),180-k*5,y=.05+.04*math.log1p(.2+k%5),F=.2+k%5)
            z=p.row_for_cluster([d])
            z['band']=list(sorted(p.BANDS))[k%8]
            rows.append(z)
        res=p.heldout_band_models(rows)
        self.assertEqual(res['clusters_with_OOF_predictions'],24)
        self.assertTrue(math.isfinite(res['M0_mse']))
        self.assertTrue(math.isfinite(res['M1_mse']))
    def test_unique_station_and_complete_source_frame_guard(self):
        with tempfile.TemporaryDirectory() as t:
            files=[]
            for i,b in enumerate(sorted(p.BANDS)):
                file=Path(t)/(b+'.json')
                d={'analysis':'V94_ALL_STATIONS_2019_ORIGINAL_UHSLC_HOURLY_TIDE_SOLAR_PHYSICAL','band':b,
                 'candidate_unique_UHSLC_station_ids':1,'source_candidates_attempted':1,
                 'raw_station_outcomes':[],'source_skipped_qc':[{'uid':i+1}],'source_failures':[]}
                file.write_text(json.dumps(d));files.append(file)
            with self.assertRaisesRegex(ValueError,'564'):p.macro_rows(files)
            files[0].write_text(files[0].read_text().replace('"band": "N_00_15"','"band": "N_15_30"'))
            with self.assertRaisesRegex(ValueError,'duplicated'):p.macro_rows(files)
    def test_cluster_no_prey_activity_or_causes(self):
        self.assertIn('NO',p.__doc__)
        self.assertIn('organism behavior',p.__doc__)
if __name__=='__main__':unittest.main()
