import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
import matched_state_learner_v8 as m

CLASSES=('Arable','Margins','Natural')

def synthetic(gamma=1.5,n_birds=28,n_steps=95,seed=100):
    rng=np.random.default_rng(seed)
    out=[]
    for bird in range(n_birds):
        for si in range(n_steps):
            origin=CLASSES[int(rng.integers(3))]
            dst=[CLASSES[int(rng.integers(3))] for j in range(6)]
            lens=rng.normal(2.0,0.6,size=6)
            turn=rng.uniform(-1,1,size=6)
            scores=np.array([0 if d=='Arable' else (0.3 if d=='Margins' else 0.1) for d in dst])+gamma*np.array([d==origin for d in dst])+.25*(lens-2)+.2*turn
            ex=np.exp(scores-scores.max());probs=ex/ex.sum()
            used=int(rng.choice(len(dst),p=probs))
            out.append(m.StepSet(f'bird_{bird:02d}',str(si),origin,tuple(dst),tuple(lens),tuple(turn),used))
    return out

class KnownTruth(unittest.TestCase):
    def test_reject_inconsistent_candidate_origins(self):
        rows=[{'id':'one','burst_':1,'step_id_':99,'t1_':'01','t2_':'02','case_':case,'landUse_start':start,'landUse_end':end,'sl_':2,'cos_ta_':0,'x1_':100.0,'y1_':200.0,'x2_':101.0,'y2_':202.0} for case,start,end in [('TRUE','Arable','Natural'),('FALSE','Natural','Arable'),('FALSE','Arable','Margins')]]
        with self.assertRaisesRegex(ValueError,'origins'):m.from_source_rows(rows)
    def test_correct_source_matched_set(self):
        rows=[{'id':'one','burst_':1,'step_id_':99,'t1_':'01','t2_':'02','case_':case,'landUse_start':'Arable','landUse_end':end,'sl_':2,'cos_ta_':0,'x1_':100.0,'y1_':200.0,'x2_':101.0,'y2_':202.0} for case,end in [('FALSE','Margins'),('TRUE','Natural'),('FALSE','Arable')]]
        s=m.from_source_rows(rows)
        self.assertEqual(len(s),1)
        self.assertEqual(s[0].chosen,1)
        self.assertEqual(s[0].origin,'Arable')
    def test_reject_incomplete_set(self):
        s=m.StepSet('one','1','Arable',('Arable','Margins'),(1.,1.),(.1,.1),0)
        with self.assertRaisesRegex(ValueError,'dimensions'):m.validate([s],CLASSES,strict=False)
    def test_no_fold_leakage(self):
        xs=[f'bird_{i}' for i in range(80)]
        self.assertEqual(set(m.fold(i) for i in xs),set(range(5)))
    def test_detect_origin_tracking_known_truth(self):
        r=m.evaluate(synthetic(gamma=1.55),CLASSES,bootstrap=1000)
        self.assertGreater(r['mean_equal_bird_logscore_gain_nats'],0.04)
        self.assertEqual(r['gate'],'PASS')
        self.assertEqual(len(r['folds']),5)
    def test_no_false_large_gain_when_origin_irrelevant(self):
        r=m.evaluate(synthetic(gamma=0,seed=200),CLASSES,bootstrap=1000)
        self.assertLess(abs(r['mean_equal_bird_logscore_gain_nats']),0.04)
    def test_identifiability_gate_rejects_one_origin_state(self):
        orig=synthetic(gamma=1.2,n_birds=25,n_steps=110)
        x=[m.StepSet(s.animal,s.step,'Arable',s.destinations,s.lengths,s.turns,s.chosen) for s in orig]
        with self.assertRaisesRegex(ValueError,'origin-state contrast'):
            m.validate(x,CLASSES,strict=True)
    def test_unequal_animal_numbers_still_individual_weighted(self):
        base=synthetic(gamma=1.4,n_birds=25,n_steps=100)
        more=[m.StepSet(s.animal,'extra'+s.step,s.origin,s.destinations,s.lengths,s.turns,s.chosen) for s in base if s.animal=='bird_00']
        r=m.evaluate(base+more,CLASSES,bootstrap=300)
        self.assertEqual(r['number_of_animals'],25)
        self.assertEqual(r['number_of_groups'],2600)

if __name__=='__main__':unittest.main()
