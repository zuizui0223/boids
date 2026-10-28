"""v20 synthetic source-grain/identity gates; no guineafowl ecological response values."""
import unittest
import hashlib
import pandas as pd
import source_gate as v

class TestGuineafowlSource(unittest.TestCase):
    def test_author_source_pin_and_git_blob_digest(self):
        self.assertEqual(v.ORIGINAL_BYTE_COUNT,2717)
        self.assertEqual(v.AUTHOR_SHA,"15ea08ed10555beba227792f4ef106d87d52b6a4")
        self.assertEqual(v.ORIGINAL_BLOB_SHA1,"3fe1e3245cb97026b03125582d5af14ab9fd5b39")
        b=b"v20 source"
        self.assertEqual(v.git_blob_sha1(b),
                         hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest())
        self.assertNotEqual(v.git_blob_sha1(b),hashlib.sha1(b).hexdigest())

    def test_ten_repeated_groups_qualify_only_metadata_not_behavior(self):
        data=pd.DataFrame([
            {"ID":f"G{i:02d}","SEASON":f"S{s}","home_range":i+s}
            for i in range(10) for s in range(3)])
        result=v.profile_frames({"synthetic":data})
        d=result["data_objects"]["synthetic"]
        self.assertEqual(d["rows"],30)
        self.assertTrue(d["future_group_season_admitted"])
        self.assertTrue(d["three_season_memory_history_admitted"])
        self.assertEqual(d["n_unique_original_group_ids"],10)
        self.assertFalse(result["prediction_scores_computed"])
        self.assertNotIn("1.0",str(result))

    def test_seven_repeat_groups_stops_eight_group_gate(self):
        data=pd.DataFrame([
            {"ID":f"G{i:02d}","SEASON":f"S{s}","home_range":i+s}
            for i in range(7) for s in (1,2,3)])
        d=v.profile_frames({"synthetic":data})["data_objects"]["synthetic"]
        self.assertFalse(d["future_group_season_admitted"])
        self.assertFalse(d["three_season_memory_history_admitted"])
        self.assertEqual(d["groups_observed_in_3_or_more_seasons"],7)

    def test_many_single_season_groups_do_not_create_time_replication(self):
        data=pd.DataFrame([
            {"ID":f"G{i:02d}","SEASON":"S1","home_range":i}
            for i in range(21)])
        d=v.profile_frames({"synthetic":data})["data_objects"]["synthetic"]
        self.assertEqual(d["n_unique_original_group_ids"],21)
        self.assertEqual(d["groups_observed_in_2_or_more_seasons"],0)
        self.assertFalse(d["future_group_season_admitted"])

    def test_duplicate_group_season_blocks_forecasting(self):
        data=pd.DataFrame([
            {"ID":f"G{i:02d}","SEASON":f"S{s}","home_range":i+s}
            for i in range(10) for s in (1,2)])
        data=pd.concat([data,data.iloc[[0]]],ignore_index=True)
        d=v.profile_frames({"synthetic":data})["data_objects"]["synthetic"]
        self.assertEqual(d["duplicate_group_season_key_rows"],2)
        self.assertFalse(d["future_group_season_admitted"])

    def test_missing_group_or_season_does_not_count_as_replication(self):
        data=pd.DataFrame({"ID":["A","A",None,"B"],
                           "SEASON":["S1","S2","S3",None],
                           "Y":[1,2,3,4]})
        d=v.profile_frames({"synthetic":data})["data_objects"]["synthetic"]
        self.assertEqual(d["n_unique_original_group_ids"],1)
        self.assertEqual(d["n_complete_group_season_keys"],2)
        self.assertFalse(d["future_group_season_admitted"])

if __name__=="__main__":
    unittest.main()
