import unittest
from check_receipts import compare

class TestNumericalReplay(unittest.TestCase):
    def test_tolerates_last_bit_float_deviation(self):
        compare({'a':[.12345678910,True,'abc']}, {'a':[.12345678915,True,'abc']})
    def test_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'STOP_NUMERIC_REPLAY_MISMATCH'):
            compare({'a':1.}, {'a':1.00001})
    def test_unexpected_keys_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'STOP_SCHEMA_KEYS_CHANGED'):
            compare({'a':1},{'a':1,'b':1})

if __name__=='__main__':unittest.main()
