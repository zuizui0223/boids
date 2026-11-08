"""Invented target trajectories only; tests do not contain bat observations."""
import unittest,math
import numpy as np
from bat_echo_memory_static_dynamic_v1 import (
  GRID,K_GRID,SOURCE_PAPER_DEFAULT_MEMORY_K,N_SYNTHETIC,
  mse_exact,continuous_optimum,integer_optimum,gain_boundary_ratio,
  one_scenario,run
)
class TestBatEchoTimescaleTheory(unittest.TestCase):
 def test_k_one_is_single_current_sensor(self):
  for q in (0,.5,2,4):self.assertAlmostEqual(mse_exact(1,1,q),1.)
 def test_static_wall_gain_is_monotonic(self):
  v=[mse_exact(k,1,0) for k in K_GRID]
  self.assertEqual(v,sorted(v,reverse=True))
  self.assertAlmostEqual(v[4],.2)
 def test_second_observation_cost_from_mobile_target(self):
  self.assertAlmostEqual(mse_exact(2,1,1),.75)
  self.assertAlmostEqual(mse_exact(2,1,2),1.)
 def test_predeclared_source_default_memory(self):
  self.assertEqual(SOURCE_PAPER_DEFAULT_MEMORY_K,5)
  self.assertAlmostEqual(mse_exact(5,1,.5),.8)
 def test_default_five_call_improvement_threshold(self):
  self.assertAlmostEqual(gain_boundary_ratio(5),2/3)
  self.assertLess(mse_exact(5,1,.5),mse_exact(1,1,.5))
  self.assertAlmostEqual(mse_exact(5,1,2/3),mse_exact(1,1,2/3))
  self.assertGreater(mse_exact(5,1,1),mse_exact(1,1,1))
 def test_ten_call_boundary(self):
  self.assertAlmostEqual(gain_boundary_ratio(10),6/19)
  self.assertAlmostEqual(mse_exact(10,1,6/19),1)
 def test_moving_prey_mem_optimum(self):
  self.assertEqual(integer_optimum(1,4),1)
  self.assertEqual(integer_optimum(1,1),2)
  self.assertEqual(integer_optimum(1,.5),3)
  self.assertEqual(integer_optimum(1,.25),4)
 def test_q_zero_no_finite_optimum(self):
  self.assertIsNone(continuous_optimum(1,0))
  self.assertEqual(integer_optimum(1,0),10)
 def test_continuous_solution(self):
  for q in (.1,.5,1,2,4):
   k=continuous_optimum(1,q)
   self.assertAlmostEqual(k,math.sqrt(3/q+.5))
 def test_invalid_inputs_rejected(self):
  for args in ((0,1,0),(1,0,0),(2,1,-1)):
   with self.assertRaises(ValueError):mse_exact(*args)
  with self.assertRaises(ValueError):gain_boundary_ratio(1)
 def test_monte_carlo_matches_exact_on_invented_histories(self):
  x=one_scenario(.5,np.random.default_rng(20261107))
  self.assertEqual(len(x["errors_by_history_K"]),10)
  self.assertLess(x["maximum_relative_MC_vs_analytic_error"],.05)
 def test_prespecified_no_source_fit(self):
  x=run()
  self.assertEqual(len(x["worlds"]),7)
  self.assertEqual(len(K_GRID),10)
  self.assertEqual(N_SYNTHETIC,40000)
  self.assertTrue(x["monte_carlo_check_pass"])
  self.assertFalse(x["original_MATLAB_source_code_replayed"])
  self.assertFalse(x["new_bat_measurements"])
  self.assertFalse(x["original_Mazar_memory_rule_identical_to_gaussian_mean"])
if __name__=="__main__":unittest.main()
