"""All mocked — no live GIN accesses."""
import io,json,unittest
from urllib.error import HTTPError
from validation_fish_boids_v21.gin_tree_metadata import probe,ENDPOINTS

class TestTreeMetadata(unittest.TestCase):
    def test_all_http_stop_not_fish_null(self):
        def blocked(req,timeout):
            raise HTTPError(req.full_url,404,"not found",None,None)
        r=probe(blocked)
        self.assertEqual(r["status"],"SOURCE_ACCESS_STOP")
        self.assertEqual(len(r["calls"]),4)
        self.assertIsNone(r["fish_behavior_scores"])

    def test_git_tree_only_metadata(self):
        def mocked(req,timeout):
            if req.full_url==ENDPOINTS["root_tree_master"]:
                return io.BytesIO(json.dumps({"tree":[{"path":"behavior","type":"tree","sha":"abc","mode":"040000"}],"truncated":False}).encode())
            raise HTTPError(req.full_url,404,"not found",None,None)
        r=probe(mocked)
        self.assertEqual(r["status"],"TREE_METADATA_FOUND_NOT_RAW_ADMITTED")
        self.assertEqual(r["calls"][1]["entries"][0]["path"],"behavior")
        self.assertFalse(r["raw_original_data_read"])
        self.assertIsNone(r["fish_behavior_scores"])

if __name__=="__main__":unittest.main()
