"""Synthetic known-truth numerical tests; field audit is performed in CI."""
import math
import unittest
from empirical_reanalysis import solve, fit, design, row_score, stratified_folds

class KnownTruth(unittest.TestCase):
    def test_linear_solve(self):
        self.assertAlmostEqual(solve([[2,0],[0,4]],[6,20])[0],3)
        self.assertAlmostEqual(solve([[2,0],[0,4]],[6,20])[1],5)
    def test_score_has_correct_optimum(self):
        self.assertGreater(row_score(9,9),row_score(9,3))
    def test_predict_known_poisson(self):
        vals=[]
        for level in (3,4,5,6,7):
            for night in (0,1):
                for i in range(20):
                    truth=math.exp(2+0.3*night-0.11*(level-5)+0.2*night*(level-5))
                    vals.append({"night":night,"water_m":level,"n_acoustic_annotations":truth})
        b=fit(vals,"night_height_interaction",ridge=0)
        for got,want in zip(b,(2,0.3,-0.11,0.2)):
            self.assertAlmostEqual(got,want,places=6)
    def test_night_design(self):
        r={"night":1,"water_m":6}
        self.assertEqual(design(r,"night_height_interaction"),[1,1.,1.,1.])
        self.assertEqual(design(r,"constant"),[1.])
        r["coefficient_level"]="High"
        self.assertEqual(design(r,"night_height_coefficient"),
                         [1.,1.,1.,0.,1.,0.])
        self.assertEqual(design(r,"night_height_coefficient_interaction"),
                         [1.,1.,1.,0.,1.,0.,0.,1.,0.])

if __name__=="__main__":
    unittest.main()
