"""Known-truth tests of strict source-identity and year-disjoint prediction."""
import json
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import numpy as np
from unseen_identity_transfer import partition_training, forecast_fixed, evaluate_transfer


def rows(year, identities, each=350):
    return [dict(id=bird, t=datetime(year, 1, 2, tzinfo=timezone.utc)+timedelta(hours=4*k),
                 phase=1 if k%2 else -1, ghost_phase=-1 if k%2 else 1,
                 h=0.1, target_e=1., target_n=0.)
            for bird in identities for k in range(each)]


class IdentityTransferTests(unittest.TestCase):
    def setUp(self):
        self.train=rows(2010, ('old-A','old-B','new-C','new-D','new-E'))
        self.test={2011:rows(2011, ('old-A','test-F','test-G')),
                   2012:rows(2012, ('old-B','test-F','test-G'))}

    def test_union_removes_all_future_identities_not_only_2011(self):
        kept, receipt=partition_training(self.train,self.test)
        self.assertEqual({r['id'] for r in kept},{'new-C','new-D','new-E'})
        self.assertEqual(receipt['removed_training_rows'],700)
        self.assertEqual(receipt['removed_training_identities'],2)
        self.assertEqual(receipt['training_rows_after_exclusion'],1050)
        self.assertEqual(receipt['training_birds_after_exclusion'],3)
        self.assertEqual(receipt['train_test_identity_overlap_after_exclusion'],0)
        self.assertTrue(receipt['training_admitted'])
        self.assertNotIn('old-A',json.dumps(receipt))

    def test_partition_not_changed_by_test_targets_or_order(self):
        changed=deepcopy(self.test)
        for array in changed.values():
            for r in array:r['target_e']=-999; r['target_n']=17
            array.reverse()
        self.assertEqual(partition_training(self.train,self.test)[0],
                         partition_training(self.train,changed)[0])

    def test_missing_duplicate_naive_or_wrong_year_rejected(self):
        for mutate in ('duplicate','missing_id','wrong_year','naive'):
            data=deepcopy(self.test)
            if mutate=='duplicate': data[2011].append(data[2011][0])
            elif mutate=='missing_id':data[2011][0]['id']=''
            elif mutate=='wrong_year':data[2011][0]['t']=datetime(2010,1,1,tzinfo=timezone.utc)
            else:data[2011][0]['t']=datetime(2011,1,1)
            with self.assertRaises(ValueError):partition_training(self.train,data)
        with self.assertRaises(ValueError):partition_training(rows(2011,('X',)),self.test)

    def test_no_fitting_when_training_source_fails(self):
        def forbidden(*args):raise AssertionError('must not fit')
        report=evaluate_transfer(rows(2010,('old-A','old-B','new-C')),self.test,forbidden)
        self.assertEqual(report['status'],'NOT_ADMITTED_TRAINING_IDENTITY_SUPPORT')
        self.assertEqual(report['outcomes'],{})

    def test_three_models_use_same_disjoint_train_and_concatenated_years(self):
        kept,_=partition_training(self.train,self.test)
        calls=[]
        def fake(tr,te,level):
            calls.append((deepcopy(tr),deepcopy(te),level))
            return np.tile([1.,0.],(len(te),1))
        original=deepcopy((kept,self.test))
        p=forecast_fixed(kept,self.test,fake)
        self.assertEqual(len(calls),3)
        self.assertEqual([len(c[1]) for c in calls],[2100]*3)
        self.assertEqual([c[2] for c in calls],[0,1,1])
        self.assertEqual(set(p),{2011,2012})
        self.assertEqual(p[2012]['Mactual'].shape,(1050,2))
        self.assertEqual((kept,self.test),original)
        self.assertTrue(all(r['phase']==r['ghost_phase'] for r in calls[2][0]))
        for a,b in zip(calls[1][0],calls[2][0]):
            self.assertEqual({k:v for k,v in a.items() if k!='phase'},
                             {k:v for k,v in b.items() if k!='phase'})

    def test_chronological_fit_rejects_empty_or_wrong_prediction_shapes(self):
        kept,_=partition_training(self.train,self.test)
        with self.assertRaises(ValueError):forecast_fixed(kept,self.test,lambda a,b,c:np.zeros((2,2)))
        with self.assertRaises(ValueError):forecast_fixed(kept,self.test,lambda a,b,c:np.full((len(b),2),np.nan))
        with self.assertRaises(ValueError):forecast_fixed([],self.test,lambda *a:None)

    def test_same_original_test_rows_and_aggregate_known_angular_gain(self):
        seen=[]
        def fake(tr,te,level):
            self.assertFalse({r['id'] for r in tr}&{r['id'] for r in te})
            seen.append(len(tr))
            # Baseline 90 degrees, real phase 0 degrees, historical 60 degrees.
            angle=90 if level==0 else (0 if tr[0]['phase']==self.train[0]['phase'] else 60)
            rad=np.radians(angle)
            return np.tile([np.cos(rad),np.sin(rad)],(len(te),1))
        out=evaluate_transfer(self.train,self.test,fake,bird_draws=30,week_draws=30)
        self.assertEqual(out['status'],'OBSERVED_IDENTITY_DISJOINT_YEAR_TRANSFER')
        self.assertEqual(seen,[1050]*3)
        for year in ('2011','2012'):
            s=out['outcomes'][year]['metrics']
            self.assertEqual(s['n_rows'],1050)
            self.assertEqual(s['n_birds'],3)
            self.assertAlmostEqual(s['equal_bird']['contrasts']['M365_minus_Mactual']
                                   ['absolute_angle_gain_degrees']['mean'],60.)
        self.assertNotIn('old-A',json.dumps(out))

    def test_undefined_bearing_not_zero_loss_or_dropped_rows(self):
        out=evaluate_transfer(self.train,self.test,
                              lambda tr,te,l:np.zeros((len(te),2)),bird_draws=20,week_draws=20)
        for r in out['outcomes'].values():
            self.assertEqual(r['status'],'NOT_ADMITTED_UNDEFINED_BEARING')
            self.assertTrue(r['no_source_rows_dropped'])

    def test_insufficient_test_year_not_scored_but_its_identity_still_excluded(self):
        tests=deepcopy(self.test);tests[2012]=tests[2012][:30]
        seen=[]
        def fake(tr,te,l):
            self.assertNotIn('old-B',{r['id'] for r in tr})
            self.assertTrue(all(r['t'].year==2011 for r in te))
            seen.append(len(te));return np.tile([1.,0.],(len(te),1))
        report=evaluate_transfer(self.train,tests,fake,bird_draws=20,week_draws=20)
        self.assertEqual(seen,[1050]*3)
        self.assertEqual(report['outcomes']['2012']['status'],'NOT_ADMITTED_TEST_SOURCE_SUPPORT')
        self.assertEqual(report['outcomes']['2011']['metrics']['n_rows'],1050)

    def test_empty_sources_and_too_few_training_birds_do_not_relax_gate(self):
        _,g=partition_training([],self.test)
        self.assertFalse(g['training_admitted'])
        _,g=partition_training(rows(2010,('Z','Y'),each=600),self.test)
        self.assertFalse(g['training_admitted'])
        _,g=partition_training(self.train,{2011:[]})
        self.assertEqual(g['test_identity_count'],0)

if __name__=='__main__':unittest.main()
