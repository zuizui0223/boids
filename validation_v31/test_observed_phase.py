import unittest
from datetime import datetime,timedelta,timezone
from observed_phase import make_x,heldout_compare,same_height_hysteresis
UTC=timezone.utc

class PhasePilotTests(unittest.TestCase):
    def test_design_nested(self):
        t=datetime(2009,6,1,tzinfo=UTC)
        r={'id':'a','t':t,'h':.4,'phase':1,'rate':.12,'response':0.5,
           'lat':53.4,'lon':6.2,'clocksin':0,'clockcos':1,'yearsin':.3,'yearcos':.95}
        self.assertEqual(len(make_x(r,0)),9)
        self.assertEqual(len(make_x(r,1)),12)
        self.assertEqual(make_x(r,1)[9],1)
    def test_holdout_known_truth_phase_signal(self):
        rows=[];t=datetime(2009,1,1,tzinfo=UTC)
        for day in range(100):
            for bird in range(4):
                for hour in range(0,24,6):
                    h=.5+.1*(day%4)
                    p=1 if ((day+hour//6)%2)==0 else -1
                    rows.append({'id':str(bird),'t':t+timedelta(days=day,hours=hour),
                                 'h':h,'phase':p,'rate':p*.1,'response':.4+.06*p,
                                 'lat':53.4,'lon':6.2,'clocksin':0,'clockcos':1,
                                 'yearsin':day/300,'yearcos':.99})
        r=heldout_compare(rows)
        self.assertGreater(r['M0_minus_M1_equal_bird_MSE_gain'],0)
        self.assertEqual(r['n_heldout_birds'],4)
    def test_same_height_matched_strata(self):
        t=datetime(2009,8,1,tzinfo=UTC)
        rows=[]
        for bird in ['a','b']:
            for i in range(10):
                for p in [-1,1]:
                    rows.append({'id':bird,'t':t+timedelta(days=i),
                                 'h':.3,'phase':p,'response':1. if p<0 else .8})
        r=same_height_hysteresis(rows)
        self.assertEqual(r['animals_with_ebb_flood_matched_strata'],2)
        self.assertAlmostEqual(r['ebb_minus_flood_equal_bird_mean_log1p_speed'],.2)
if __name__=='__main__': unittest.main()
