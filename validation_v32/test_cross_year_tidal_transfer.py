import math,unittest
from datetime import datetime,timedelta,timezone
from cross_year_tidal_transfer import _score

class CrossYearTransferTests(unittest.TestCase):
    def test_independent_year_known_truth_phase_gain(self):
        train=[];test=[]
        for period, out in [(2010,train),(2011,test)]:
            base=datetime(period,1,1,tzinfo=timezone.utc)
            for bird in range(10):
                for step in range(150):
                    phase=1 if (step+bird)%2 else -1
                    stamp=base+timedelta(days=step//3,hours=(step%3)*7)
                    hour=stamp.hour+stamp.minute/60
                    doy=stamp.timetuple().tm_yday
                    out.append({'id':str(bird),'t':stamp,'h':.4+0.06*(step%5),
                                'phase':phase,'rate':phase*.09,
                                'response':.6+phase*.12,
                                'lat':53.4+(bird%3)*.01,'lon':6.2,
                                'clocksin':math.sin(2*math.pi*hour/24),
                                'clockcos':math.cos(2*math.pi*hour/24),
                                'yearsin':math.sin(2*math.pi*doy/365.25),
                                'yearcos':math.cos(2*math.pi*doy/365.25)})
        score=_score(train,test)
        self.assertGreater(score['M0_minus_M1_gain'],0)
        self.assertEqual(score['n_heldout_birds'],10)
        self.assertGreater(score['weeks_positive'],0)
        self.assertEqual(len(score['week_bootstrap_95']),2)
    def test_insufficient_records_are_rejected(self):
        with self.assertRaises(ValueError):_score([],[])
if __name__=='__main__':unittest.main()
