import unittest,math
from datetime import datetime,timedelta,timezone
import numpy as np
from heldout_2012_tidal_lag import (FROZEN_LAGS,CLOCKS,score,original_2012_gauge,with_fixed_lags)
from tidal_front import TideSeries

class Original2012TideLagTests(unittest.TestCase):
    def item(self,i,bird,year):
        t=datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=i*3)
        ph=1 if i%2 else -1
        return {"id":str(bird),"t":t,"h":math.cos(i*.12),"phase":ph,
                "rate":ph*.08,"response":.8+ph*.16+bird*.03+math.sin(i*.5)*.04,
                "lat":53.42+bird*.01,"lon":5.85+bird*.001,
                "clocksin":math.sin(t.hour*2*math.pi/24),
                "clockcos":math.cos(t.hour*2*math.pi/24),
                "yearsin":math.sin(t.timetuple().tm_yday*2*math.pi/365.25),
                "yearcos":math.cos(t.timetuple().tm_yday*2*math.pi/365.25)}
    def test_fixed_2012_holdout_only_and_replay(self):
        self.assertEqual(FROZEN_LAGS,(-120,0))
        self.assertEqual(CLOCKS,(0,-15))
        train=[self.item(i,b,2010) for b in range(4) for i in range(360)]
        test=[self.item(i,b,2012) for b in range(4) for i in range(360)]
        p_train=np.asarray([(-1 if i%3 else 1,r["phase"]) for i,r in enumerate(train)])
        p_test=np.asarray([(-1 if i%3 else 1,r["phase"]) for i,r in enumerate(test)])
        r=score(train,test,p_train,p_test,bird_draws=100,week_draws=100)
        self.assertEqual(r["test_birds"],4)
        self.assertEqual(r["status"],"2012_ORIGINAL_HELDOUT_SOURCE_OBSERVED_NO_CAUSAL_CLAIM")
        self.assertTrue(r["zero_lag_predictor_exact_v33_replay"])
        self.assertEqual(len(r["comparisons"]),3)
    def test_common_support_of_measured_phase_history(self):
        t=datetime(2012,6,4,tzinfo=timezone.utc)
        tide=TideSeries([(t-timedelta(hours=4)+timedelta(minutes=k*10),
                          math.sin(k*.1)) for k in range(70)],
                         datum="NAP_m",provenance="synthetic")
        row=self.item(0,1,2012);row["t"]=t
        kept,phase,drop=with_fixed_lags([row],tide)
        self.assertEqual(drop,0)
        self.assertEqual(phase.shape,(1,2))
        self.assertEqual(len(kept),1)
    def test_source_rejects_unregistered_2012_gauge(self):
        with self.assertRaises(ValueError):original_2012_gauge("unknown.station")

if __name__=="__main__":
    unittest.main()
