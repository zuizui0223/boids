import unittest
import numpy as np
from empirical_transition_benchmark import probs_from_counts, score_session, data_to_sessions, loo

class TestTransition(unittest.TestCase):
    def test_probs_normalize(self):
        c=np.arange(27,dtype=int).reshape(3,3,3)
        p0,p1,p2=probs_from_counts(c)
        self.assertAlmostEqual(p0.sum(),1)
        np.testing.assert_allclose(p1.sum(-1),np.ones(3))
        np.testing.assert_allclose(p2.sum(-1),np.ones((3,3)))
    def test_leakage_on_exclusion(self):
        c1=np.zeros((3,3,3),dtype=int);c1[2,2,2]=100
        c2=np.zeros((3,3,3),dtype=int);c2[2,2,2]=100
        c3=np.zeros((3,3,3),dtype=int);c3[0,0,0]=100
        counts={'A::1':c1,'A::2':c2,'B::1':c3}
        meta={k:{'id':k.split('::')[0]} for k in counts}
        out=loo(counts,meta)
        self.assertIn('M3',out['per_individual']['A'])
        self.assertNotIn('M3',out['per_individual']['B'])
        self.assertGreater(out['personal_excess'],0)
        unseen=loo(counts,meta,exclude_individual=True)
        self.assertNotIn('M3',unseen['summary'])
    def test_triplets_gap_and_direction(self):
        csv='animal-id,BatDay,timestamp,height-above-msl,W.Component,location-long,location-lat\n'
        from datetime import datetime,timedelta
        st=datetime(2026,1,1)
        for i in range(40):
            ts=(st+timedelta(seconds=30*i)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            csv+=f'A,1,{ts},{i*30*2},0.2,0,0\n'
        counts,meta,summ=data_to_sessions(csv.encode())
        self.assertEqual(len(counts),1)
        self.assertEqual(summ['included_triplets'],38)
        self.assertEqual(int(counts['A::1'][2,2,2]),38)

if __name__=='__main__':unittest.main()
