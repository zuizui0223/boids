import unittest
from copy import deepcopy
from datetime import datetime,timedelta,timezone
import numpy as np
from cross_island_transfer import (bird_equal_center,translate_rows,covariate_support,
                                   prepare_transfer,evaluate_transfer)


def rows(year,ids,each=360,lat=53.4,lon=6.2):
    return [dict(id=b,t=datetime(year,1,2,tzinfo=timezone.utc)+timedelta(hours=4*k),
                 lat=lat+.001*(k%5),lon=lon+.002*(k%7),h=np.sin(k),
                 previous_speed_log=1.2+.01*(k%9),phase=1 if k%2 else -1,
                 ghost_phase=-1 if k%2 else 1,target_e=1.,target_n=0.)
            for b in ids for k in range(each)]


class CrossIslandTests(unittest.TestCase):
    def setUp(self):
        self.src=rows(2010,('s1','s2','s3','overlap'))
        self.ref=rows(2010,('r1','r2','r3'),lon=5.8)
        self.test=rows(2011,('t1','t2','overlap'),lon=5.8)

    def test_center_is_equal_bird_not_equal_rows(self):
        x=rows(2010,('a',),each=2,lat=10,lon=20)+rows(2010,('b',),each=20,lat=30,lon=40)
        expected=np.mean([np.mean([[r['lat'],r['lon']] for r in x if r['id']==b],axis=0)
                          for b in ('a','b')],axis=0)
        self.assertTrue(np.allclose(bird_equal_center(x),expected))
        self.assertFalse(np.allclose(expected,np.mean([[r['lat'],r['lon']] for r in x],axis=0)))

    def test_anchor_never_uses_future_year_or_targets(self):
        ref=deepcopy(self.ref)
        for r in ref:r['target_e']=999;r['target_n']=-1
        self.assertEqual(bird_equal_center(ref),bird_equal_center(self.ref))
        with self.assertRaisesRegex(ValueError,'year'):bird_equal_center(self.test)

    def test_translation_changes_only_coordinates_and_not_input(self):
        old=deepcopy(self.test)
        translated=translate_rows(self.test,(53.4,6.2),(53.4,5.8))
        self.assertEqual(self.test,old)
        for a,b in zip(old,translated):
            self.assertAlmostEqual(b['lon']-a['lon'],.4)
            self.assertEqual({k:v for k,v in a.items() if k not in ('lat','lon')},
                             {k:v for k,v in b.items() if k not in ('lat','lon')})
        self.assertEqual(translate_rows(self.test,(1.,2.),(1.,2.)),self.test)

    def test_identity_collision_removed_and_all_test_rows_kept(self):
        kept,gate=prepare_transfer(self.src,self.ref,self.test)
        self.assertEqual(len(kept),1080)
        self.assertEqual({r['id'] for r in kept},{'s1','s2','s3'})
        self.assertEqual(gate['removed_training_rows'],360)
        self.assertEqual(gate['removed_literal_identities'],1)
        self.assertEqual(gate['training_test_literal_overlap'],0)
        self.assertTrue(gate['admitted'])
        self.assertEqual(gate['test_rows'],1080)

    def test_training_and_reference_gates_before_fit(self):
        def never(*a):raise AssertionError('fit prohibited')
        for src,ref in [(self.src[:300],self.ref),(self.src,self.ref[:50])]:
            r=evaluate_transfer(src,ref,self.test,never)
            self.assertEqual(r['status'],'NOT_ADMITTED_CROSS_ISLAND_SOURCE')
            self.assertNotIn('conditions',r)

    def test_target_gate_before_fit(self):
        r=evaluate_transfer(self.src,self.ref,self.test[:50],lambda *a:1/0)
        self.assertEqual(r['status'],'NOT_ADMITTED_CROSS_ISLAND_SOURCE')

    def test_invalid_year_duplicate_or_nonfinite_rejected(self):
        for which in ('year','duplicate','finite','id'):
            x=deepcopy(self.src)
            if which=='year':x[0]['t']=x[0]['t'].replace(year=2011)
            elif which=='duplicate':x.append(x[0])
            elif which=='finite':x[0]['lat']=float('nan')
            else:x[0]['id']=''
            with self.assertRaises(ValueError):prepare_transfer(x,self.ref,self.test)

    def test_support_audit_detects_shift_without_dropping_rows(self):
        native=covariate_support(self.src,self.test)
        translated=translate_rows(self.test,bird_equal_center(self.src),bird_equal_center(self.ref))
        shifted=covariate_support(self.src,translated)
        self.assertEqual(native['per_feature_outside_1_99']['lon'],1.)
        self.assertEqual(shifted['per_feature_outside_1_99']['lon'],0.)
        self.assertEqual(len(translated),len(self.test))
        self.assertTrue(native['descriptive_only_no_rows_filtered'])

    def test_only_three_fits_for_both_conditions_no_test_targets_in_anchor(self):
        calls=[]
        def fake(tr,te,level):
            calls.append((deepcopy(tr),deepcopy(te),level))
            rad=np.deg2rad(90 if level==0 else 20 if tr[0]['phase']==self.src[0]['phase'] else 60)
            return np.tile([np.cos(rad),np.sin(rad)],(len(te),1))
        r=evaluate_transfer(self.src,self.ref,self.test,fake,bird_draws=50,week_draws=50)
        self.assertEqual(len(calls),3)
        self.assertEqual([len(c[1]) for c in calls],[2160]*3)
        self.assertEqual([c[2] for c in calls],[0,1,1])
        self.assertEqual(len(calls[0][0]),1080)
        self.assertTrue(all(x['phase']==x['ghost_phase'] for x in calls[2][0]))
        for condition in ('translated','native'):
            m=r['conditions'][condition]['metrics']
            self.assertEqual(m['n_rows'],1080)
            self.assertAlmostEqual(m['equal_bird']['contrasts']['M365_minus_Mactual']
                                   ['absolute_angle_gain_degrees']['mean'],40.)
        self.assertEqual(r['status'],'OBSERVED_CROSS_ISLAND_YEAR_TRANSFER')

    def test_undefined_bearing_cannot_invent_direction(self):
        r=evaluate_transfer(self.src,self.ref,self.test,
                            lambda tr,te,l:np.zeros((len(te),2)),bird_draws=20,week_draws=20)
        for c in r['conditions'].values():
            self.assertEqual(c['status'],'NOT_ADMITTED_UNDEFINED_BEARING')
            self.assertTrue(c['no_rows_dropped'])

    def test_wrong_forecast_shape_is_error_not_source_null(self):
        with self.assertRaises(ValueError):
            evaluate_transfer(self.src,self.ref,self.test,lambda *a:np.zeros((1,2)))

if __name__=='__main__':unittest.main()
