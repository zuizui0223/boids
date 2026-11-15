"""v140 known-truth tests for fold-only imputation, moon and NB scoring."""
import math
import unittest
from astro_confounds import (nb_score, design, impute_from_training,
                             generalized_fit, pred,SPECS)

def r(night,coef,moon,**extras):
    d={"night":night,"water_m":5., "coefficient_level":coef,
       "tide_coefficient":{"Low":40,"Medium":60,"High":80,"Very High":110}[coef],
       "anchor":45158, "temp":16,"wind":8,"wave":1,
       "lux":0,"moon":moon,"direction":0,
       "n_acoustic_annotations":8.}
    d.update(extras)
    return d

class KnownTruth(unittest.TestCase):
    def test_nb_score(self):
        self.assertGreater(nb_score(10,10,5),nb_score(10,2,5))
        with self.assertRaises(ValueError):nb_score(10,0,5)

    def test_categorical_zero_night_interactions(self):
        a=r(0,"High",.5)
        b=r(1,"High",.5)
        fill=impute_from_training([a,b])
        x=design(a,"weather_tide_night",fill)
        y=design(b,"weather_tide_night",fill)
        self.assertEqual(x[-3:],[0.,0.,0.])
        self.assertEqual(y[-3:],[0.,1.,0.])

    def test_moon_night_interaction_predefined(self):
        a=r(0,"Low",1)
        b=r(1,"Low",1)
        f=impute_from_training([a,b])
        self.assertEqual(design(a,"weather_moon_night",f)[-1],0.)
        self.assertGreater(design(b,"weather_moon_night",f)[-1],1.)
        self.assertEqual(len(design(b,"weather_moon_night",f)),
                         len(design(b,"weather_tide_night",f))-2)

    def test_fit_synthetic_known_truth(self):
        x=[]
        for cat in ("Low","Medium","High","Very High"):
            for night in (0,1):
                for day in range(6):
                    d=r(night,cat,.25,anchor=45140+day)
                    d["n_acoustic_annotations"]=math.exp(2+0.4*night-0.3*(cat=="High")*
                                                          night)
                    x.append(d)
        f=impute_from_training(x)
        b=generalized_fit(x,"minimal_tide_night","n_acoustic_annotations",f,ridge=.001)
        # With data made exactly by the model, predictions approximate truth.
        self.assertAlmostEqual(pred(r(1,"High",.25),"minimal_tide_night",f,b),
                               math.exp(2+0.4-0.3),places=2)

    def test_imputation_uses_train_only(self):
        train=[r(0,"Low",.1,wave=None),r(1,"Medium",.3,wave=2.0)]
        means=impute_from_training(train)
        self.assertEqual(means["wave"],2)
        held=r(1,"High",.7,wave=200.)
        # Test covariate not allowed to set the imputation mean.
        self.assertEqual(means["wave"],2)

if __name__=="__main__":
    unittest.main()
