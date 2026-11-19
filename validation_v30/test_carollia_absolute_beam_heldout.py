"""Known-truth tests for frozen v30 no-future acoustic predictors."""
import unittest
import numpy as np

from carollia_absolute_beam_heldout import (
    pre_features, target_after_call, wrap_rad,
    model_fit_predict, bootstrap_label_gain,
)


class CarolliaNoLeakTests(unittest.TestCase):
    def setUp(self):
        self.t=np.arange(10,dtype=float)*.10
        self.xy=np.column_stack((np.arange(10,dtype=float)*.4,np.zeros(10)))
        self.az=np.linspace(-.5,.5,10)
        self.fit=np.ones(10)*.8

    def test_pre_event_features_unchanged_by_future_turn(self):
        k=5
        a=pre_features(self.t,self.xy,self.az,self.fit,k)
        self.assertIsNotNone(a)
        changed=self.xy.copy()
        changed[k+1,1]=1.5
        b=pre_features(self.t,changed,self.az,self.fit,k)
        np.testing.assert_allclose(a[0],b[0])
        np.testing.assert_allclose(a[1],b[1])
        self.assertNotEqual(
            target_after_call(self.t,self.xy,k,a[2]),
            target_after_call(self.t,changed,k,b[2]),
        )

    def test_no_sonar_fit_no_admission(self):
        self.fit[5]=.299
        self.assertIsNone(pre_features(self.t,self.xy,self.az,self.fit,5))
        self.fit[5]=.3
        self.assertIsNotNone(pre_features(self.t,self.xy,self.az,self.fit,5))

    def test_wrap_around_both_directions(self):
        x=wrap_rad(np.array([np.pi+.2,-np.pi-.2,0.]))
        np.testing.assert_allclose(x,[-np.pi+.2,np.pi-.2,0.],atol=1e-10)

    def test_train_only_fit_predict_source_independent_of_test_y(self):
        rows=[]
        for i in range(25):
            rows.append({
                "motor":np.array([float(i),i/2,1,0.1,1,0,0]),
                "beam":np.array([0.1,0.9]),
                "y":i*.01
            })
        fit=model_fit_predict(rows[:20],rows[20:],"beam")
        changed=[dict(r) for r in rows[20:]]
        for r in changed:r["y"] = 10000.0
        fit2=model_fit_predict(rows[:20],changed,"beam")
        np.testing.assert_allclose(fit,fit2)

    def test_exact_sign_and_bootstrap_are_animal_level(self):
        r=bootstrap_label_gain({"a":.1,"b":.2,"c":.3,"d":.4,"e":.5,"f":.6,"g":.7,"h":.8})
        self.assertEqual(r["positive_bat_labels"],8)
        self.assertEqual(r["one_sided_exact_sign_p"],1/256)
        self.assertTrue(r["predeclared_primary_pass"])


if __name__=="__main__":
    unittest.main()
