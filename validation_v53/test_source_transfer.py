"""v53 source provenance and run guards, with no original tracks in tests."""
import unittest
from datetime import datetime,timedelta,timezone
import numpy as np
import run_phase_control_transfer as runner

class SourceTransferTests(unittest.TestCase):
    def row(self,year,i,bird=None):
        return {'id':str(i%5) if bird is None else bird,
                't':datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=i),
                'target_e':1.,'target_n':0.,'ghost_phase':0,'phase':1,'h':.5}

    def test_gauge_boundaries_merge_without_fabricated_gaps_or_averaging(self):
        start=datetime(2010,1,1,tzinfo=timezone.utc)
        class Gauge:
            def __init__(self,times,heights):self.times=times;self.heights=heights
        a=Gauge([start,start+timedelta(minutes=10)],[.1,.2])
        b=Gauge([start+timedelta(minutes=10),start+timedelta(minutes=20)],[.2,.3])
        made=[]
        def factory(values,**kwargs):made.append((values,kwargs));return 'source-object'
        merged,audit=runner.merge_gauges({2010:a,2011:b},factory)
        self.assertEqual(merged,'source-object')
        self.assertEqual(len(made[0][0]),3)
        self.assertEqual(audit['source_duplicate_boundaries_checked'],1)
        self.assertEqual(made[0][1],{'datum':'NAP_m','provenance':'observed'})
        b.heights[0]=.4
        with self.assertRaisesRegex(ValueError,'CONFLICT'):
            runner.merge_gauges({2010:a,2011:b},factory)

    def test_missing_original_tide_and_nonfinite_rejected(self):
        class Bad:
            times=[datetime(2010,1,1,tzinfo=timezone.utc)]
            heights=[float('nan')]
        with self.assertRaises(ValueError):runner.merge_gauges({2010:Bad()},lambda x,**k:x)

    def test_2012_source_hash_and_provider_verification(self):
        site='ameland';sha=runner.SHA2012[site]
        manifest={'provider_md5_match':True,'original_sha256':sha}
        self.assertTrue(runner.check_manifest(manifest,site,2012))
        with self.assertRaises(ValueError):
            runner.check_manifest({**manifest,'provider_md5_match':False},site,2012)
        with self.assertRaises(ValueError):
            runner.check_manifest({**manifest,'original_sha256':'changed'},site,2012)

    def test_small_source_prevents_all_model_fits(self):
        train=[self.row(2010,i) for i in range(1100)]+[self.row(2011,i) for i in range(1100)]
        test=[self.row(2012,i) for i in range(869)]
        called=[]
        def no_fit(*args):called.append(True);raise AssertionError('fitting forbidden')
        result=runner.compare_year(train,test,2012,no_fit)
        self.assertEqual(result['status'],'NOT_ADMITTED_SOURCE_SUPPORT')
        self.assertFalse(called)
        self.assertEqual(result['source_admission']['test_rows'],869)

    def test_ghost_field_only_changes_phase_and_same_rows(self):
        train=[self.row(2010,i) for i in range(1200)]
        test=[self.row(2011,i) for i in range(1200)]
        calls=[]
        def predict(tr,te,level):
            calls.append((tr,te,level))
            return np.tile([1.,.2 if level==0 else .1],(len(te),1))
        out=runner.compare_year(train,test,2011,predict,bird_draws=20,week_draws=20)
        self.assertEqual(out['status'],'OBSERVED_ANGULAR_PHASE_CONTROL')
        self.assertEqual([c[2] for c in calls],[0,1,1])
        self.assertEqual({r['phase'] for r in calls[2][0]},{0})
        self.assertEqual({r['h'] for r in calls[2][0]},{.5})
        self.assertEqual({r['phase'] for r in train},{1})
        self.assertEqual([r['t'] for r in calls[1][1]],[r['t'] for r in calls[2][1]])

if __name__=='__main__':unittest.main()
