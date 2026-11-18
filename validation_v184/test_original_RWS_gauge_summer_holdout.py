import math
import unittest
from datetime import datetime,timezone,timedelta
from validation_v184.original_RWS_gauge_summer_holdout import (
    SHIFTS,HOLDOUT,matched_rows,fit_models,evaluate_models,SourceStop)
class FrozenGaugeTransferTests(unittest.TestCase):
    def test_frozen_heldout_months_and_lags(self):
        self.assertEqual(HOLDOUT,((2018,7),(2018,8),(2018,9),(2019,7),(2019,8),(2019,9)))
        self.assertEqual(SHIFTS,(0,30,-30,90))
    def test_30minute_delayed_gauge_predicts_better(self):
        t0=datetime(2018,6,1,tzinfo=timezone.utc)
        v={t0+timedelta(minutes=10*i):math.sin(i*.12)+.1*math.sin(i*.31)
           for i in range(450)}
        w={t:.24+1.14*v[t-timedelta(minutes=30)]
           for t in v if t-timedelta(minutes=30) in v}
        rows=matched_rows(v,w)
        model=fit_models(rows)
        ev=evaluate_models(rows,model)
        self.assertLess(ev["MSE_m2"]["30"],ev["MSE_m2"]["0"])
        self.assertGreater(ev["primary_gain_MSE_same_time_minus_frozen_30min"],0)
    def test_stop_sparse_pairs(self):
        t0=datetime(2018,6,1,tzinfo=timezone.utc)
        v={t0+timedelta(minutes=10*i):i/10 for i in range(50)}
        with self.assertRaises(SourceStop):matched_rows(v,v)
if __name__=="__main__":unittest.main()
