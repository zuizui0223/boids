"""v38b synthetic-only author supplementary member identity, no fish sources."""
import unittest,json
from validation_fish_school_v38.six_speed_source_member_metadata import SOURCE_ARTICLES,run
from validation_fish_school_v38.source_vr_collection_gate import SourceStop
class NoRawFishMovieFromMetadata(unittest.TestCase):
    def test_author_api_all_missing_fails_closed(self):
        o=run(fetch=lambda url: (_ for _ in ()).throw(SourceStop("SYNTHETIC_ONLY_STOP")))
        self.assertEqual(o["status"],"SOURCE_METADATA_STOP")
        self.assertFalse(o["original_experimental_fish_trajectory_rows_loaded"])
        self.assertFalse(o["original_speed_condition_animal_effects_reanalyzed"])
        self.assertEqual(o["n_original_source_article_file_manifests_verified"],0)
        self.assertEqual(len(o["source_member_file_manifests"]),3)
    def test_fixed_original_collection_member_ids_and_role(self):
        self.assertEqual(set(SOURCE_ARTICLES.values()),{32323963,32323960,32323957})
        self.assertEqual(len(SOURCE_ARTICLES),3)
if __name__=="__main__":unittest.main()
