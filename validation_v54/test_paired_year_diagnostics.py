"""Known-truth tests; synthetic data do not constitute animal evidence."""
import importlib.util
import unittest
from datetime import datetime, timedelta, timezone
import numpy as np

try:
    import paired_year_diagnostics as core
except ImportError:
    core = None

class PairedYearTests(unittest.TestCase):
    def require(self):
        self.assertIsNotNone(core, 'v54 paired-year implementation is missing')
        return core

    def sample(self, year, birds=('a','b','c'), per_month=(20,40,20)):
        rows=[]
        for bird in birds:
            for month,count in enumerate(per_month,1):
                for k in range(count):
                    t=datetime(year,month,1,tzinfo=timezone.utc)+timedelta(hours=k*6)
                    rows.append({'id':bird,'t':t,'phase':1,'ghost_phase':0,
                                 'target_e':1.,'target_n':0.})
        return rows

    def losses(self, rows, gain=.2):
        a=np.zeros((len(rows),3,3))
        a[:,0,:]=1.0; a[:,1,:]=.8-gain; a[:,2,:]=.8
        return a

    def test_implementation_present(self):
        self.require()

    def test_exact_pair_year_change_and_no_identifiers_in_output(self):
        m=self.require(); r={y:self.sample(y) for y in (2011,2012)}
        loss={2011:self.losses(r[2011],.3),2012:self.losses(r[2012],.1)}
        out=m.paired_years(r,loss,draws=100)
        self.assertEqual(out['status'],'OBSERVED_PAIRED_RECURRENT_IDENTITIES')
        self.assertEqual(out['n_paired_identities'],3)
        c=out['paired']['change_in_gain_second_minus_first']['M365_minus_Mactual']['cosine_loss']
        self.assertAlmostEqual(c['mean'],-.2)
        np.testing.assert_allclose(c['CI95'],[-.2,-.2],atol=1e-12)
        self.assertNotIn('identifiers',out)

    def test_identity_turnover_is_not_a_paired_bird(self):
        m=self.require(); r={2011:self.sample(2011),2012:self.sample(2012,('a','b','d'))}
        out=m.paired_years(r,{y:self.losses(r[y]) for y in r},draws=40)
        self.assertEqual(out['status'],'NOT_ADMITTED_RECURRENT_IDENTITY_SUPPORT')
        self.assertEqual(out['n_shared_source_identifiers'],2)
        self.assertNotIn('paired',out)

    def test_support_gate_requires_weeks_and_fifty_rows(self):
        m=self.require(); r={y:self.sample(y,per_month=(10,10,10)) for y in (2011,2012)}
        out=m.paired_years(r,{y:self.losses(r[y]) for y in r})
        self.assertEqual(out['n_eligible_recurrent_identities'],0)
        for y in r:
            for i,x in enumerate(r[y]):x['t']=datetime(y,1,1,tzinfo=timezone.utc)+timedelta(seconds=i)
        self.assertEqual(m.paired_years(r,{y:self.losses(r[y]) for y in r})['status'],
                         'NOT_ADMITTED_RECURRENT_IDENTITY_SUPPORT')

    def test_equal_month_weights_not_opportunity_weights(self):
        m=self.require(); r={y:self.sample(y,per_month=(20,80,20)) for y in (2011,2012)}
        loss={y:self.losses(r[y],0.) for y in r}
        for y in r:
            for i,x in enumerate(r[y]):
                # year 2012 benefit differs only in February; equal-month delta=-.1
                if y==2012 and x['t'].month==2:loss[y][i,1,:]+=.3
        out=m.paired_years(r,loss,month_matched=True,draws=80)
        self.assertEqual(out['status'],'OBSERVED_PAIRED_COMMON_MONTHS')
        self.assertEqual(out['retained_months_per_identity_min_max'],[3,3])
        self.assertAlmostEqual(out['paired']['change_in_gain_second_minus_first']['M365_minus_Mactual']['cosine_loss']['mean'],-.1)

    def test_calendar_match_never_borrows_unshared_month(self):
        m=self.require(); r={2011:self.sample(2011,per_month=(20,40,20)),
                            2012:self.sample(2012,per_month=(20,0,60))}
        out=m.paired_years(r,{y:self.losses(r[y]) for y in r},month_matched=True,draws=60)
        self.assertEqual(out['retained_months_per_identity_min_max'],[2,2])
        self.assertEqual(out['paired_source_rows_first'],120)
        self.assertEqual(out['paired_source_rows_second'],240)

    def test_duplicate_wrong_year_and_nan_raise(self):
        m=self.require(); r={y:self.sample(y) for y in (2011,2012)}
        bad=r[2011]+[r[2011][0]]
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            m.paired_years({2011:bad,2012:r[2012]},
                          {2011:self.losses(bad),2012:self.losses(r[2012])})
        loss={y:self.losses(r[y]) for y in r};loss[2012][0,0,0]=np.nan
        with self.assertRaises(ValueError):m.paired_years(r,loss)
        with self.assertRaises(ValueError):m.paired_years({2011:r[2012],2012:r[2011]},loss)

    def test_actual_angle_not_prediction_length(self):
        m=self.require(); r=self.sample(2011)[:3]
        pred={'M0':np.tile([0.,1.],(3,1)),
              'Mactual':np.tile([1.,0.],(3,1)),
              'M365':np.tile([1.,1.],(3,1))}
        tensor=m.loss_tensor(r,pred)
        self.assertEqual(tensor.shape,(3,3,3))
        np.testing.assert_allclose(tensor[:,0,1],90.)
        np.testing.assert_allclose(tensor[:,2,1],45.)
        scaled={k:v*8 for k,v in pred.items()}
        np.testing.assert_allclose(m.loss_tensor(r,scaled)[:,:,:2],tensor[:,:,:2])
        pred['Mactual'][0]=0
        with self.assertRaises(Exception):m.loss_tensor(r,pred)

    def test_same_2012_rows_update_difference_paired(self):
        m=self.require(); r=self.sample(2012)
        out=m.paired_update(r,self.losses(r,.1),self.losses(r,.3),draws=100)
        c=out['paired']['change_in_gain_second_minus_first']['M365_minus_Mactual']['cosine_loss']
        self.assertAlmostEqual(c['mean'],.2)
        self.assertEqual(c['positive_identities'],3)
        self.assertEqual(out['n_paired_identities'],3)

    def test_fixed_policy_only_2010_and_concatenated_test(self):
        m=self.require(); calls=[]
        tr=self.sample(2010); a=self.sample(2011); b=self.sample(2012)
        def forecast(train,test,level):
            calls.append((set(x['t'].year for x in train),set(x['t'].year for x in test),level,
                          set(x['phase'] for x in train)))
            return np.tile([1.,.1*level],(len(test),1))
        got=m.forecast_policies(tr,a,b,forecast)
        self.assertEqual(len(calls),6)
        self.assertTrue(all(c[0]=={2010} and c[1]=={2011,2012} for c in calls[:3]))
        self.assertTrue(all(c[0]=={2010,2011} and c[1]=={2012} for c in calls[3:]))
        self.assertEqual(calls[2][3],{0})
        self.assertEqual(calls[5][3],{0})
        self.assertEqual(got['F10'][2012]['Mactual'].shape,(len(b),2))
        self.assertEqual(got['F1011'][2012]['M365'].shape,(len(b),2))
        with self.assertRaises(ValueError):m.forecast_policies(a,a,b,forecast)

    def test_swap_year_benefits_reverses_difference(self):
        m=self.require(); r={y:self.sample(y) for y in (2011,2012)}
        a=m.paired_years(r,{2011:self.losses(r[2011],.1),2012:self.losses(r[2012],.3)},draws=80)
        b=m.paired_years(r,{2011:self.losses(r[2011],.3),2012:self.losses(r[2012],.1)},draws=80)
        key='change_in_gain_second_minus_first'
        self.assertAlmostEqual(a['paired'][key]['M0_minus_Mactual']['cosine_loss']['mean'],
                               -b['paired'][key]['M0_minus_Mactual']['cosine_loss']['mean'])

if __name__=='__main__':unittest.main()
