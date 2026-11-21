import unittest,random
from osf_uncertainty import simulate_uniform_positions,evaluate,JITTER_DRAWS,PERM_PER_DRAW
class TestSensitivity(unittest.TestCase):
 def fake(self,n=9):
    return [{"t":float(i),"xyz":(float(i),0.,0.),
             "uncert":[.1,.2,.3],"label":"call","uid":str(i)} for i in range(n)]
 def test_independent_jitter_within_declared_span(self):
    x=self.fake()
    p=simulate_uniform_positions(x,random.Random(1))
    self.assertEqual(len(p),9)
    self.assertTrue(all(abs(a[0]-b["xyz"][0])<=.05 for a,b in zip(p,x)))
 def test_zero_uncertainty_is_identity(self):
    x=self.fake()
    for z in x:z["uncert"]=[0.,0.,0.]
    p=simulate_uniform_positions(x,random.Random(1))
    self.assertEqual(p,[z["xyz"] for z in x])
 def test_small_source_stops(self):
    self.assertEqual(evaluate(self.fake(3),1)["status"],"STOP_FEW_EVENTS_OR_120S_PAIRS")
 def test_span_stop_if_unknown(self):
    x=self.fake()
    x[3]["uncert"]=[None,.1,.2]
    self.assertEqual(evaluate(x,1)["status"],"STOP_MISSING_SPAN")
 def test_fixture_evaluated(self):
    x=self.fake()
    r=evaluate(x,1)
    self.assertEqual(r["status"],"EXPLORATORY_UNCERTAINTY_SCENARIO_RUN")
    self.assertEqual(r["n_simulated_location_scenarios"],JITTER_DRAWS)
    self.assertEqual(r["n_null_shuffles_per_scenario"],PERM_PER_DRAW)
if __name__=="__main__":unittest.main()
