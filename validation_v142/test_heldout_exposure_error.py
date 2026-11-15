import unittest
from datetime import datetime,timedelta
from heldout_exposure_error import exposure_errors, TRAIN_H

class GaugeExposureKnownTruth(unittest.TestCase):
    def test_exact_identity_no_mismatch(self):
        import math
        seq=[math.sin(2*math.pi*i/13)+i/10000 for i in range(168)]
        t=[datetime(2019,6,1)+timedelta(hours=i) for i in range(168)]
        from statistics import median
        x=exposure_errors(seq,seq,0,median(seq[:TRAIN_H]),median(seq[:TRAIN_H]),t)
        self.assertEqual(x["all"]["n_heldout_hours"],96)
        self.assertEqual(x["all"]["wrong_highlow_naive"],0)
        self.assertEqual(x["all"]["wrong_highlow_corrected"],0)
        self.assertEqual(x["all"]["naive_correl_source_water_height"],1.)
    def test_synthetic_known_one_hour_shift(self):
        import math
        seq=[math.sin(2*math.pi*i/12.42)+0.3*math.sin(i/7) for i in range(168)]
        target=[0.0]+seq[:-1]
        t=[datetime(2019,6,1)+timedelta(hours=i) for i in range(168)]
        from statistics import median
        x=exposure_errors(seq,target,1,median(seq[:TRAIN_H]),median(target[:TRAIN_H]),t)
        self.assertEqual(x["all"]["n_heldout_hours"],96)
        self.assertLess(x["all"]["wrong_highlow_corrected"],
                        x["all"]["wrong_highlow_naive"])
if __name__=="__main__":unittest.main()
