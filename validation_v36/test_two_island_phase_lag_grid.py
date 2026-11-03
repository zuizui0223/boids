"""Known-truth tests for fixed two-island lag grid, no real GPS in tests."""
import math,unittest
from datetime import datetime,timedelta,timezone
import numpy as np
from tidal_front import TideSeries
from two_island_phase_lag_grid import (LAGS,common_phase_support,model_lag_comparison)

class LagGridTests(unittest.TestCase):
    def tide(self):
        t0=datetime(2011,1,1,tzinfo=timezone.utc)
        data=[(t0+timedelta(minutes=10*k),math.cos(2*math.pi*k/74.5)) for k in range(8000)]
        return TideSeries(data,datum="NAP_m",provenance="synthetic"),t0
    def make(self,tide,t0,n=300,year=2011):
        rows=[]
        for bird in range(4):
            for i in range(n):
                t=t0+timedelta(days=4,hours=i*2)
                height,phase,rate=tide.at_with_phase(t)
                theta=2*math.pi*(t.hour+t.minute/60)/24
                day=2*math.pi*t.timetuple().tm_yday/365.25
                rows.append({"id":str(bird),"t":t,"h":height,"phase":phase,"rate":rate,
                             "lat":53.42+bird*.01,"lon":5.80+bird*.001,
                             "clocksin":math.sin(theta),"clockcos":math.cos(theta),
                             "yearsin":math.sin(day),"yearcos":math.cos(day),
                             "response":.5+.16*phase+.03*bird+.01*math.sin(i*.7)})
        return rows
    def test_lag_grid_has_five_fixed_nonoptimized_values(self):
        self.assertEqual(LAGS,(-120,-60,0,60,120))
    def test_same_source_rows_held_at_all_lags_and_model_scores(self):
        tide,t0=self.tide()
        rows=self.make(tide,t0)
        support,phase,miss=common_phase_support(rows,tide)
        self.assertEqual(miss,0)
        self.assertEqual(len(support),1200)
        self.assertEqual(phase.shape,(1200,5))
        result=model_lag_comparison(support,support,phase,phase)
        self.assertEqual(result["status"],"EXPLORATORY_FIXED_LAG_GRID_NO_SELECTION")
        self.assertEqual(len(result["lag_variants"]),5)
        self.assertEqual(result["n_heldout_birds"],4)
        self.assertGreater(result["lag_variants"][2]["M0_minus_Mphase_equal_bird_gain"],0)
        self.assertEqual(result["lag_variants"][2]["gauge_phase_lag_minutes"],0)
    def test_small_data_gate(self):
        tide,t0=self.tide()
        data=self.make(tide,t0,n=4)
        support,phase,_=common_phase_support(data,tide)
        result=model_lag_comparison(support,support,phase,phase)
        self.assertEqual(result["status"],"NOT_ADMITTED")
if __name__=="__main__":unittest.main()
