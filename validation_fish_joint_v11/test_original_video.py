import unittest
from original_video_gate import VIDEO,parse_src_time,original_acoustic_counts,SourceStop
class TestOriginalAV(unittest.TestCase):
 def test_fixed_two_publisher_scenes(self):
    self.assertEqual(len(VIDEO),2)
    self.assertEqual(VIDEO["Figure10_Rockfish_Lingcod"]["clip_seconds"],17)
 def test_UTC_iso(self):
    a=parse_src_time("2019-09-20T16:38:58Z")
    b=parse_src_time("2019-09-20T16:39:08Z")
    self.assertAlmostEqual(b-a,10.)
 def test_wrong_original_sound_hash_stops(self):
    with self.assertRaises(SourceStop):
        original_acoustic_counts(b"uuid,time_min_date\nx,2019-09-20T16:38:58Z",
                                 VIDEO["Figure10_Rockfish_Lingcod"])
 def test_other_scene_has_distinct_original(self):
    a=VIDEO["Figure9_Lingcod"];b=VIDEO["Figure10_Rockfish_Lingcod"]
    self.assertNotEqual(a["original_events_sha256"],b["original_events_sha256"])
    self.assertNotEqual(a["localization_file_id"],b["localization_file_id"])
if __name__=="__main__":unittest.main()
