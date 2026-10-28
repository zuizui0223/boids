"""v22 synthetic-only wild seasonal source, metadata and group grain tests."""
import hashlib
import unittest
import pandas as pd
import source_gate as v


class SourceGate(unittest.TestCase):
    def test_original_2021_author_commit_and_three_rdata_blobs_fixed(self):
        self.assertEqual(v.SOURCE_SHA,"2a3aec308bb4a8449d1eeb16beed4aff8f387116")
        self.assertEqual(v.FILES["ddf_hr_dtd.Rdata"],(8783,"65cbed930dd0924dec32fd7115f016f6b3fbc3d6"))
        self.assertEqual(v.FILES["df_dhor.Rdata"],(1911,"a365bea412cdb6eb3f7b4c76bb0f9dda2268ea8a"))
        self.assertEqual(v.FILES["df_dshor.RData"],(4002,"6b389efeed3c23c498735362cdd2befb5ff8b00a"))

    def test_fixed_git_blob_is_not_plain_data_sha(self):
        b=b"source nested ecology"
        actual=hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()
        self.assertEqual(v.git_digest(b),actual)
        self.assertNotEqual(v.git_digest(b),hashlib.sha1(b).hexdigest())

    def sample(self):
        rows=[]
        for g in range(9):
            for i in range(3):
                rows.append({"groupss_":f"G{g}",
                             "season_":f"T{i}",
                             "season_type":("dry","wet","intermediate")[i],
                             "fidelity":.35+i/10,
                             "AREA_SQM":1000+g})
        return pd.DataFrame(rows)

    def test_original_repeated_bird_group_and_environment_labels_are_metadata_only(self):
        x=v.source_frame_profile("df",self.sample())
        self.assertEqual(x["source_rows"],27)
        self.assertEqual(x["unique_group_ids"],9)
        self.assertEqual(x["groups_in_3_or_more_seasons"],9)
        self.assertEqual(x["environment_categories"],3)
        self.assertTrue(x["environment_is_shared_source_season_label_not_group_specific"])
        self.assertEqual(x["source_seasons_with_multiple_environment_labels"],0)
        self.assertFalse(x["numeric_ecological_response_values_analyzed"])
        self.assertNotIn("0.35",str(x))

    def test_multiple_birds_per_same_group_season_are_not_independent_replicates(self):
        data=pd.concat([self.sample(),self.sample().iloc[[0,1,2]]],ignore_index=True)
        x=v.source_frame_profile("df",data)
        self.assertEqual(x["unique_group_ids"],9)
        self.assertEqual(x["duplicate_rows_of_same_group_season"],6)
        self.assertEqual(x["groups_in_3_or_more_seasons"],9)

    def test_environment_heterogeneous_within_nominal_season_prevents_simple_model(self):
        data=self.sample()
        data.loc[data.index[0],"season_type"]="dry2"
        x=v.source_frame_profile("df",data)
        self.assertEqual(x["source_seasons_with_multiple_environment_labels"],1)
        self.assertFalse(x["environment_is_shared_source_season_label_not_group_specific"])

    def test_missing_original_group_season_not_imputed(self):
        data=self.sample()
        data.loc[0,"groupss_"]=None
        x=v.source_frame_profile("df",data)
        self.assertEqual(x["source_rows"],27)
        self.assertEqual(x["complete_group_season_key_rows"],26)
        self.assertEqual(x["unique_group_ids"],9)
        self.assertFalse(x["numeric_ecological_response_values_analyzed"])

if __name__=="__main__":
    unittest.main()
