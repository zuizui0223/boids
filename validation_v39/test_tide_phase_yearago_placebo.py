import math,unittest
from datetime import datetime,timedelta,timezone
import numpy as np
from tide_phase_yearago_placebo import (TIDE_PLACEBO_DAYS,CLOCKS,
                                        previous_year_phase_join,comparison,percentile_interval)
from tidal_front import TideSeries

class V39OriginalTemporalPlaceboTests(unittest.TestCase):
    def record(self,k,bird,year):
        t=datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=k*6)
        phase=(-1 if k%2 else 1)
        hr=t.hour+t.minute/60
        d=t.timetuple().tm_yday
        return {"id":str(bird),"t":t,"h":math.cos(k*.14),
                "phase":phase,"rate":phase*.08,"response":.7+.25*phase+.015*bird+math.sin(k*.3)*.03,
                "lat":53.42+bird*.01,"lon":6.20+bird*.01,
                "clocksin":math.sin(2*math.pi*hr/24),
                "clockcos":math.cos(2*math.pi*hr/24),
                "yearsin":math.sin(2*math.pi*d/365.25),
                "yearcos":math.cos(2*math.pi*d/365.25)}
    def test_fixed_placebo_and_time_source(self):
        self.assertEqual(TIDE_PLACEBO_DAYS,365)
        self.assertEqual(CLOCKS,(0,-15))
        start=datetime(2010,1,1,tzinfo=timezone.utc)
        tide=TideSeries([(start+timedelta(minutes=10*i),math.sin(i*.1)) for i in range(320)],
                        datum="NAP_m",provenance="synthetic")
        t=start+timedelta(days=365,hours=3)
        row={"t":t}
        matched,p,drop=previous_year_phase_join([row],tide)
        self.assertEqual(len(matched),1)
        self.assertEqual(drop,0)
        self.assertIn(p[0],(-1,0,1))
    def test_separate_bootstraps_match_their_point_estimands(self):
        train=[self.record(k,b,2010) for b in range(4) for k in range(380)]
        test=[self.record(k,b,2011) for b in range(4) for k in range(360)]
        ghosttrain=[1 if k%4<2 else -1 for b in range(4) for k in range(380)]
        ghostest=[1 if k%4<2 else -1 for b in range(4) for k in range(360)]
        r=comparison(train,test,ghosttrain,ghostest,bird_draws=200,week_draws=200)
        self.assertEqual(r["admission"],"OBSERVED_POSTRESULT_HISTORICAL_PLACEBO")
        c=r["model_contrasts"]["M0_minus_Mactual"]
        self.assertGreater(c["pooled_equal_bird_mean_gain"],0)
        self.assertGreater(c["separate_equal_week_bird_mean_gain"],0)
        self.assertEqual(len(c["pooled_equal_bird_95percentile_CI"]),2)
        self.assertEqual(len(c["separate_equal_week_bird_95percentile_CI"]),2)
        self.assertGreaterEqual(r["n_heldout_weeks"],4)
        self.assertEqual(r["n_heldout_birds"],4)
    def test_small_dataset_stops_inference(self):
        train=[self.record(k,0,2010) for k in range(20)]
        test=[self.record(k,0,2011) for k in range(20)]
        ans=comparison(train,test,[0]*len(train),[0]*len(test),
                       bird_draws=50,week_draws=50)
        self.assertEqual(ans["admission"],"NOT_ADMITTED_INSUFFICIENT_EXTERNAL_SOURCE")
    def test_percentile_bootstrap_degenerate_constant(self):
        self.assertEqual(percentile_interval([.123]*5,10,1),[.123,.123])

if __name__=="__main__":unittest.main()
