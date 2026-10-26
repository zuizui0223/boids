import math,unittest
import numpy as np
from pigeon_social_forecast import (extract_rows,components_of_birds,fit_ridge,predict,
     frozen_score,STALE_PARTNER_FIXES)


def synthetic_flight(n=130):
    out=[]
    lat0=51.0;lon0=-.2;cs=math.cos(math.radians(lat0))
    for i in range(n):
        t=float(3000000000+i)
        a=(15*i,4*np.sin(i*.2));b=(15*i+2,6+5*np.sin(i*.2+.25))
        left=(t,lat0+a[1]/111320,lon0+a[0]/(111320*cs),25.0)
        right=(t,lat0+b[1]/111320,lon0+b[0]/(111320*cs),26.0)
        out.append((left,right))
    return out
class PredictionTest(unittest.TestCase):
    def test_synthetic_features_no_nan(self):
        x=extract_rows(synthetic_flight())
        self.assertIsNotNone(x)
        self.assertTrue(x['two_roles'])
        self.assertEqual(x['own'].shape[1],8)
        self.assertEqual(x['real'].shape[1],14)
        self.assertEqual(x['stale'].shape[1],14)
        self.assertTrue(np.all(np.isfinite(x['y'])))
        self.assertGreater(len(x['y']),40)
    def test_no_future_endpoint_required_for_current_features(self):
        track=synthetic_flight()
        xx=extract_rows(track)
        track.append(((3000000130.,55.,2.,25.),(3000000130.,55.,2.,26.)))
        yy=extract_rows(track)
        np.testing.assert_allclose(xx['own'][:40],yy['own'][:40],rtol=0,atol=1e-9)
    def test_connected_components_never_reuse_same_bird_in_train(self):
        fs=[{'birds':('H31','S24')},{'birds':('H31','S02')},
            {'birds':('H32','H79')},{'birds':('H02','S27')}]
        m=components_of_birds(fs)
        self.assertEqual(m['H31'],m['S24'])
        self.assertEqual(m['S24'],m['S02'])
        self.assertNotEqual(m['H31'],m['H79'])
    def test_ridge_fit_predict(self):
        rng=np.random.default_rng(3)
        X=np.c_[np.ones(100),rng.normal(size=(100,5))]
        y=1.3*X[:,2]-0.3*X[:,1]+rng.normal(0,.05,100)
        fit=fit_ridge(X,y)
        self.assertLess(np.mean((predict(fit,X)-y)**2),.25)
    def test_known_truth_social_predictive_gain_grouped(self):
        rng=np.random.default_rng(45)
        fs=[]
        for k in range(7):
            for flight in range(2):
                own=np.c_[np.ones(90),rng.normal(size=(90,7))]
                real=np.c_[own,rng.normal(size=(90,6))]
                stale=np.c_[own,rng.normal(size=(90,6))]
                y=.2*own[:,1]+.8*real[:,-1]+rng.normal(0,.1,size=90)
                fs.append({'birds':(f'A{k}',f'B{k}'),'site':'Site1',
                    'dyad':f'A{k}-B{k}','release':flight,
                    'rows':{'own':own,'real':real,'stale':stale,'y':y}})
        res=frozen_score(fs)
        self.assertEqual(res['n_bird_components'],7)
        self.assertGreater(res['equal_component_gain']['actual_vs_stale'],0)
        self.assertGreater(res['equal_component_gain']['actual_vs_own'],0)
    def test_fixed_stale_offset(self):
        self.assertEqual(STALE_PARTNER_FIXES,10)
if __name__=='__main__':unittest.main()
