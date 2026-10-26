import unittest,math,json
from forward_prediction_validation import ROOT,fit_interpolators
from predict_niche import forecast

class ForwardPredictionContracts(unittest.TestCase):
    def test_original_training_value_returned_at_exact_grid_point(self):
        rows=json.loads((ROOT/'cross_repo_phase_scan.json').read_text())['raw']
        fit=fit_interpolators(rows)
        cell=[r for r in rows if (r['preference'],r['depletion'],r['tracking'])==(.12,.08,.8)]
        self.assertEqual(len(cell),5)
        from numpy import mean
        self.assertAlmostEqual(float(fit['I_species_XY']['linear']([.12,.08,.8]).item()),
                              mean([r['species_horizontal_partition_information_nats'] for r in cell]),places=12)
    def test_extrapolation_is_forbidden(self):
        for args in ((-.1,0,0),(.1,.31,0),(.1,.2,.81)):
            with self.subTest(args=args),self.assertRaises(ValueError): forecast(*args)
    def test_example_returns_all_indices(self):
        r=forecast(.21,.16,.65)
        self.assertEqual(len(r['metrics']),4)
        self.assertTrue(all(math.isfinite(v['prediction']) for v in r['metrics'].values()))
        self.assertTrue(all(v['empirically_calibrated_error_band'][0]<=v['prediction']<=v['empirically_calibrated_error_band'][1] for v in r['metrics'].values()))

if __name__=='__main__':unittest.main()
