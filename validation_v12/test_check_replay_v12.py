import unittest
import math
from check_replay_v12 import compare

class TestReceiptReplay(unittest.TestCase):
    def test_numeric_close(self):
        compare({'a':[1.,2.]},{'a':[1+1e-10,2.]})
    def test_numeric_mismatch_fails(self):
        with self.assertRaisesRegex(ValueError,'STOP_V12_NUMERIC_REPLAY'):
            compare({'x':1.},{'x':1.001})
    def test_unequal_keys_fail(self):
        with self.assertRaisesRegex(ValueError,'STOP_V12_KEYSET_MISMATCH'):
            compare({'a':1},{'b':1})
    def test_nan_fails(self):
        with self.assertRaisesRegex(ValueError,'STOP_V12_NONFINITE'):
            compare({'a':1.},{'a':float('nan')})
    def test_list_length_fails(self):
        with self.assertRaisesRegex(ValueError,'STOP_V12_SEQUENCE_LENGTH'):
            compare({'a':[1]},{'a':[1,2]})

if __name__=='__main__':unittest.main()
