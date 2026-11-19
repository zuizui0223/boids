"""v40 source-only covariate support: non-inferential known-truth tests."""
import unittest
import numpy as np
from finland_climate_support import support
def row(temp,night,rain=0,wind=1,period="spring",year="2020"):
    return {"weather":np.asarray([temp,night,rain,wind],dtype=float),
            "period":period,"year":year}
class Tests(unittest.TestCase):
    def test_fixed_fifth_ninetyfifth_band(self):
        train=[row(10,8) for _ in range(30)]
        test=[row(10,8),row(15,9),row(10,7)]
        z=support(train,test)
        self.assertAlmostEqual(z["mean_temp_C"]["test_outside_training_q05_q95_fraction"],1/3)
        self.assertAlmostEqual(z["joint_temp_or_nightlength_outside_fraction"],2/3)
        self.assertEqual(z["source_test_nights"],3)
    def test_unseen_period_not_misclassified_as_weather(self):
        train=[row(10,8) for _ in range(30)]
        z=support(train,[row(10,8,period="winter")])
        self.assertEqual(z["test_period_labels_unseen_in_training_nights"],1)
        self.assertEqual(z["joint_temp_or_nightlength_outside_fraction"],0.)
    def test_support_ignores_animal_outcomes(self):
        train=[dict(row(10,8),count=np.asarray([1,2,3,4])) for _ in range(20)]
        test=[dict(row(12,9),count=np.asarray([500,0,0,0]))]
        a=support(train,test)
        changed=[dict(test[0],count=np.asarray([0,500,0,0]))]
        self.assertEqual(a,support(train,changed))
if __name__=="__main__":unittest.main()
