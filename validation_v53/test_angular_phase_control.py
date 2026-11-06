"""Pure v53 tests; synthetic data are never field evidence."""
import unittest
from datetime import datetime, timedelta, timezone
import numpy as np
import angular_phase_control as subject
from bearing_decomposition import UndefinedBearing


class PhaseControlTests(unittest.TestCase):
    def row(self, year=2011, bird='a', hours=0):
        return {'id':bird, 't':datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=hours),
                'h':0.73, 'phase':1, 'target_e':1., 'target_n':0.}

    def test_fixed_duration_365_day_shift_in_leap_year(self):
        called=[]
        class Tide:
            def at_with_phase(self,t):
                called.append(t)
                return 99.,-1,0.3
        r=self.row(2012);r['t']=datetime(2012,12,31,12,tzinfo=timezone.utc)
        rows,audit=subject.attach_yearago_phase([r],Tide())
        self.assertEqual(called,[datetime(2012,1,1,12,tzinfo=timezone.utc)])
        self.assertEqual(rows[0]['h'],.73)
        self.assertEqual(rows[0]['phase'],1)
        self.assertEqual(rows[0]['ghost_phase'],-1)
        self.assertNotIn('ghost_phase',r)
        self.assertEqual(audit['removed_missing_history'],0)

    def test_ghost_slack_retained_actual_height_unchanged(self):
        class Tide:
            def at_with_phase(self,t):return -15.,0,0.
        r=self.row()
        common,audit=subject.attach_yearago_phase([r],Tide())
        ghost=subject.replace_phase(common)
        self.assertEqual(len(common),1)
        self.assertEqual(ghost[0]['phase'],0)
        self.assertEqual(common[0]['phase'],1)
        self.assertEqual(ghost[0]['h'],r['h'])
        self.assertEqual(ghost[0]['target_e'],r['target_e'])
        self.assertEqual(audit['ghost_zero_rows'],1)

    def test_history_missing_changes_common_support_not_only_one_model(self):
        class Tide:
            def at_with_phase(self,t):
                if t.hour==1:raise ValueError('source gap')
                return 0.,-1,-.1
        original=[self.row(hours=k) for k in range(3)]
        common,audit=subject.attach_yearago_phase(original,Tide())
        self.assertEqual([r['t'].hour for r in common],[0,2])
        self.assertEqual(audit['removed_missing_history'],1)
        self.assertEqual(len(subject.replace_phase(common)),2)

    def test_invalid_ghost_or_duplicate_rows_stop(self):
        with self.assertRaises(ValueError):subject.replace_phase([{**self.row(),'ghost_phase':2}])
        with self.assertRaises(ValueError):subject.source_admission([self.row(2010)], [self.row(),self.row()],2011)
        with self.assertRaises(ValueError):subject.source_admission([self.row(2011)], [self.row()],2011)

    def test_2012_869_threshold_not_relaxed(self):
        train=[self.row(2010,str(k%5),k) for k in range(1100)]
        train += [self.row(2011,str(k%5),k) for k in range(1100)]
        test=[self.row(2012,str(k%5),k) for k in range(869)]
        gate=subject.source_admission(train,test,2012)
        self.assertFalse(gate['admitted'])
        self.assertEqual(gate['test_rows'],869)
        self.assertEqual(gate['minimum_test_rows'],1000)

    def test_valid_gate_and_empty_source(self):
        train=[self.row(2010,str(k%4),k*2) for k in range(1200)]
        test=[self.row(2011,str(k%4),k*2) for k in range(1200)]
        self.assertTrue(subject.source_admission(train,test,2011)['admitted'])
        self.assertFalse(subject.source_admission([],[],2011)['admitted'])

    def test_true_vs_ghost_angle_and_same_bird_pairing(self):
        rows=[self.row(bird=str(k%3),hours=k*168) for k in range(9)]
        y=np.tile([1.,0.],(len(rows),1))
        pred={'M0':np.tile([0.,2.],(len(rows),1)),
              'Mactual':np.tile([.2,0.],(len(rows),1)),
              'M365':np.tile([1.,1.],(len(rows),1))}
        ans=subject.summarize_models(rows,y,pred,bird_draws=50,week_draws=50)
        actual=ans['equal_bird']['contrasts']['M365_minus_Mactual']
        self.assertAlmostEqual(actual['cosine_loss_gain']['mean'],1-1/np.sqrt(2))
        self.assertAlmostEqual(actual['absolute_angle_gain_degrees']['mean'],45.)
        self.assertEqual(actual['cosine_loss_gain']['positive_clusters'],3)
        self.assertEqual(ans['n_rows'],9)
        rescaled={k:v*5 for k,v in pred.items()}
        other=subject.summarize_models(rows,y,rescaled,bird_draws=50,week_draws=50)
        self.assertAlmostEqual(other['equal_bird']['contrasts']['M365_minus_Mactual']
                               ['cosine_loss_gain']['mean'],actual['cosine_loss_gain']['mean'])

    def test_equal_bird_and_equal_week_are_distinct_matching_estimands(self):
        rows=[self.row(bird='a',hours=1),self.row(bird='a',hours=2),self.row(bird='b',hours=3),
              self.row(bird='b',hours=168),self.row(bird='b',hours=169),self.row(bird='b',hours=170)]
        y=np.tile([1.,0.],(6,1))
        p0=np.tile([0.,1.],(6,1))
        p1=np.array([[1.,0.],[1.,0.],[0.,1.],[0.,1.],[0.,1.],[0.,1.]])
        result=subject.summarize_models(rows,y,{'M0':p0,'Mactual':p1,'M365':p0},
                                         bird_draws=100,week_draws=100)
        b=result['equal_bird']['contrasts']['M0_minus_Mactual']['cosine_loss_gain']['mean']
        w=result['equal_week_then_bird']['contrasts']['M0_minus_Mactual']['cosine_loss_gain']['mean']
        self.assertAlmostEqual(b,.5)
        self.assertAlmostEqual(w,.25)
        self.assertEqual(result['n_weeks'],2)

    def test_zero_predictions_no_invented_bearing_or_dropped_rows(self):
        rows=[self.row()]
        with self.assertRaises(UndefinedBearing):
            subject.summarize_models(rows,np.array([[1.,0.]]),
                {'M0':np.array([[1.,0.]]),'Mactual':np.array([[1.,0.]]),'M365':np.zeros((1,2))})

    def test_wrong_shape_and_missing_models_stop(self):
        with self.assertRaises(ValueError):
            subject.summarize_models([self.row()],np.ones((1,2)),{'M0':np.ones((1,2))})

if __name__=='__main__':unittest.main()
