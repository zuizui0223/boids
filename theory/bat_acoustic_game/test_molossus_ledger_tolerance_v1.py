import unittest
from verify_molossus_2024_corrected_capture_ledger_v2 import approx

class TestLedgerNumericPrecision(unittest.TestCase):
    def test_observed_cross_runner_solver_roundoff_is_accepted(self):
        # Original CI failure 42183713913: change is 3.17e-12, not a new result.
        approx(0.0026626703237009218, 0.0026626703205352986)
    def test_material_change_is_rejected(self):
        with self.assertRaises(AssertionError):
            approx(0.0026726703205352986, 0.0026626703205352986)
    def test_nonfinite_values_are_rejected(self):
        with self.assertRaises(AssertionError):approx(float('nan'),0.)
        with self.assertRaises(AssertionError):approx(float('inf'),float('inf'))
    def test_exact_zero_is_accepted(self):
        approx(0.,0.)

if __name__=='__main__':unittest.main()
