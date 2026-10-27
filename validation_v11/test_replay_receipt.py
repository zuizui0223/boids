"""Validation tests of strict known-truth receipt comparison."""
import unittest
from replay_receipt import compare

class TestReplayIntegrity(unittest.TestCase):
    def test_nested_values_within_numerical_tolerance(self):
        compare({'s':[1.,{'a':True,'b':'x'}]}, {'s':[1.+1e-11,{'a':True,'b':'x'}]})

    def test_numeric_change_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'STOP_NUMERICAL_REPLAY_MISMATCH'):
            compare({'info':0.4},{'info':0.4001})

    def test_missing_keys_and_changed_labels_fail(self):
        with self.assertRaisesRegex(ValueError,'STOP_SCHEMA_KEYS_CHANGED'):
            compare({'a':1},{'a':1,'b':2})
        with self.assertRaisesRegex(ValueError,'STOP_METADATA_CHANGED'):
            compare({'status':'SYNTHETIC'},{'status':'OBSERVED'})

if __name__=='__main__':unittest.main()
