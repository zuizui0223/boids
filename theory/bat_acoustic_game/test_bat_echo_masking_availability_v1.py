"""Pure finite-combinatorial source-independent sensory memory tests."""
import math,unittest
from bat_echo_masking_availability_v1 import (
 exact_conditional_memory,pareto_memory,run,AVAILABILITY,RHO,K_RANGE
)
from bat_echo_memory_static_dynamic_v1 import mse_exact
class TestEchoMaskAvailability(unittest.TestCase):
 def test_all_observations_return_to_earlier_formula(self):
  for rho in (0,.25,.5,1,2,4):
   for k in range(1,11):
    a=exact_conditional_memory(k,1,rho)
    self.assertEqual(a["all_missing_probability"],0)
    self.assertAlmostEqual(a["conditional_MSE"],mse_exact(k,1,rho),places=12)
 def test_zero_availability_no_fake_estimator(self):
  a=exact_conditional_memory(5,0,1)
  self.assertIsNone(a["conditional_MSE"])
  self.assertEqual(a["all_missing_probability"],1)
 def test_one_call_conditional_error_r(self):
  for p in (1,.75,.5,.25):
   a=exact_conditional_memory(1,p,3)
   self.assertAlmostEqual(a["conditional_MSE"],1,places=12)
   self.assertAlmostEqual(a["all_missing_probability"],1-p)
 def test_five_calls_improve_echo_availability(self):
  a=exact_conditional_memory(5,.25,1)
  self.assertAlmostEqual(a["all_missing_probability"],.75**5)
  self.assertLess(a["all_missing_probability"],.75)
 def test_bernoulli_two_call_static_exact(self):
  a=exact_conditional_memory(2,.5,0)
  self.assertAlmostEqual(a["all_missing_probability"],.25)
  self.assertAlmostEqual(a["conditional_MSE"],5/6,places=12)
 def test_bernoulli_two_call_mobile_exact(self):
  a=exact_conditional_memory(2,.5,1)
  self.assertAlmostEqual(a["conditional_MSE"],5/6+5/12,places=12)
 def test_pareto_monotone_static_all_ten(self):
  r=[{"K":k,**exact_conditional_memory(k,.25,0)} for k in K_RANGE]
  self.assertEqual(pareto_memory(r),[10])
 def test_full_availability_pareto_reduces_to_optimum(self):
  r=[{"K":k,**exact_conditional_memory(k,1,1)} for k in K_RANGE]
  self.assertEqual(pareto_memory(r),[2])
 def test_dropout_pareto_high_aging_cost_needs_multiple_choices(self):
  r=[{"K":k,**exact_conditional_memory(k,.25,4)} for k in K_RANGE]
  self.assertIn(1,pareto_memory(r))
  self.assertIn(10,pareto_memory(r))
 def test_input_bounds_are_strict(self):
  for k,p,q in [(0,.5,0),(11,.5,0),(1,1.5,0),(1,-.1,0),(2,.5,-1)]:
   with self.assertRaises(ValueError):exact_conditional_memory(k,p,q)
 def test_240_source_prespecified_cases_no_measurement_claim(self):
  x=run()
  self.assertEqual(x["fixed_exact_cases"],240)
  self.assertEqual(len(x["worlds"]),24)
  self.assertEqual(len(AVAILABILITY)*len(RHO)*len(K_RANGE),240)
  self.assertFalse(x["new_bat_measurements"])
  self.assertFalse(x["authentic_MATLAB_model_rerun"])
  self.assertLess(x["analytic_formula_earlier_all_echoes_recovered"],1e-10)
if __name__=="__main__":unittest.main()
