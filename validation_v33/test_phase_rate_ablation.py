import math, unittest
from datetime import datetime,timezone,timedelta
import numpy as np
from phase_rate_ablation import MODES,vector,predict_fixed,compare
from observed_phase import predict

class V33AblationTests(unittest.TestCase):
    def one(self,k,b):
        t=datetime(2011,1,1,tzinfo=timezone.utc)+timedelta(hours=k)
        phase=-1 if k%3==0 else 1
        return {"id":b,"t":t,"h":math.sin(k*.2),"phase":phase,"rate":phase*(.08+.02*math.cos(k*.2)),
                "lat":53.48,"lon":6.20,"clocksin":math.sin(2*math.pi*t.hour/24),
                "clockcos":math.cos(2*math.pi*t.hour/24),
                "yearsin":math.sin(2*math.pi*t.timetuple().tm_yday/365),
                "yearcos":math.cos(2*math.pi*t.timetuple().tm_yday/365),
                "response":.3+.1*phase+.2*math.sin(k*.1)+b*.02}
    def test_feature_length_and_phase_rate_components(self):
        a=self.one(2,1)
        self.assertEqual([len(vector(a,m)) for m in MODES],[9,11,10,12])
        self.assertEqual(vector(a,"Mphase")[-2:],[a["phase"],a["phase"]*a["h"]])
        self.assertEqual(vector(a,"Mrate")[-1],a["rate"])
    def test_exact_frozen_v32_predictor_replay(self):
        train=[self.one(k,b) for b in (1,2,3) for k in range(400)]
        test=[self.one(k+401,b) for b in (1,2,3) for k in range(400)]
        self.assertTrue(np.allclose(predict_fixed(train,test,"M0"),predict(train,test,0),atol=1e-11))
        self.assertTrue(np.allclose(predict_fixed(train,test,"Mboth"),predict(train,test,1),atol=1e-11))
        r=compare(train,test)
        self.assertTrue(r["M0_and_Mboth_replay_v32_verified"])
        self.assertEqual(set(r["MSE_equal_bird"]),set(MODES))
        self.assertEqual(r["test_birds"],3)
    def test_unregistered_fails(self):
        with self.assertRaises(ValueError):
            vector(self.one(3,1),"Mnew")
if __name__=="__main__":unittest.main()
