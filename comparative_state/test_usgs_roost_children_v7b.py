from comparative_state.usgs_roost_children_gate_v7b import parse_children,validate_url
import unittest

class ChildrenTests(unittest.TestCase):
    def test_valid_source_url(self):
        self.assertTrue(validate_url("https://www.sciencebase.gov/catalog/items?parentId=abc&format=json"))
        self.assertFalse(validate_url("https://sciencebase.gov/catalog/file/get/abc"))
    def test_children_and_file_name_not_schema(self):
        s=parse_children({"items":[{"id":"abc","parentId":"parent","title":"roost movements","files":[{"name":"roost_night.csv","size":123}]}]})
        self.assertEqual(s["child_items"],1)
        self.assertEqual(s["total_direct_files"],1)
        self.assertFalse(s["verified_true_movement_origins"])
        self.assertFalse(s["verified_matched_choice_sets"])
        self.assertFalse(s["verified_distinct_biological_cohort"])
    def test_invalid_schema(self):
        with self.assertRaises(ValueError):parse_children({"items":2})
if __name__=="__main__":unittest.main()
