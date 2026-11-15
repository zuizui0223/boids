import unittest
from comparative_state.usgs_roost_child_files_v7c import child_url,parse_item
class GateTests(unittest.TestCase):
 def test_only_exact_child_ids(self):
  self.assertIn('6014a85dd34edf5c66ea0f16',child_url('6014a85dd34edf5c66ea0f16'))
  with self.assertRaises(ValueError):child_url('foobar')
 def test_source_schema_not_confirmed_by_names(self):
  v=parse_item('roost_night_distance','6014a85dd34edf5c66ea0f16',{'files':[{'name':'movements.csv','size':324}]})
  self.assertEqual(len(v['files']),1)
  self.assertFalse(v['true_roost_feeding_event_join_verified'])
 def test_missing_raw_list(self):
  with self.assertRaises(ValueError):parse_item('test','id',{'files':'invalid'})
if __name__=='__main__':unittest.main()
