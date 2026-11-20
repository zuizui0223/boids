import unittest
from osf_joint_schema import source_structure,SourceStop,FILE_IDS
class SourceTests(unittest.TestCase):
    def test_all_pinned_six_file_ids(self):
        self.assertEqual(len(FILE_IDS),6)
        self.assertEqual(len(set(FILE_IDS)),6)
    def test_localization_events_not_individual_fish_tracks(self):
        x=source_structure(b"timestamp,x,y,z,quality\\n12,1,2,3,ok\\n")
        self.assertFalse(x["has_explicit_individual_track_identifier_column"])
        self.assertEqual(x["joint_fish_movement_from_this_csv"],"NOT_ADMITTED")
    def test_observation_table_requires_both_identity_and_coordinates(self):
        x=source_structure(b"timestamp,x,y,fish_id\\n10,1,2,F1\\n11,3,4,F1\\n")
        self.assertTrue(x["has_explicit_individual_track_identifier_column"])
    def test_bad_source_stops(self):
        with self.assertRaises(SourceStop):source_structure(b"\\n")
if __name__=="__main__":unittest.main()
