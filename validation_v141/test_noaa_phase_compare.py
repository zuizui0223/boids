import unittest
from noaa_phase_compare import pearson,best_lag

class GaugePhaseMath(unittest.TestCase):
    def test_identical(self):
        x=[1.,2.,4.,2.,-1.,-3.,0.]*15
        (lag,corr),scores=best_lag(x,x,max_lag=4)
        self.assertEqual(lag,0)
        self.assertAlmostEqual(corr,1.0)
    def test_delayed(self):
        x=[(i%17)*.3+((i%9)**2)/10 for i in range(140)]
        y=[99.,99.]+x[:-2]
        (lag,corr),scores=best_lag(x,y,max_lag=5)
        self.assertEqual(lag,2)
        self.assertAlmostEqual(corr,1.0)
    def test_flat_refused(self):
        with self.assertRaises(ValueError):pearson([1,1,1],[2,4,8])

if __name__=="__main__":unittest.main()
