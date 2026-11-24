"""Offline fake API fixtures; no network to GIN in the tests."""
import io
import json
import unittest
from urllib.error import HTTPError
from validation_fish_boids_v21.gin_api_probe import probe,ENDPOINTS


class MultiRouteGateTests(unittest.TestCase):
    @staticmethod
    def fake(pages):
        def f(req,timeout=25):
            u=req.full_url
            value=pages[u]
            if isinstance(value,int):
                raise HTTPError(u,value,"Synthetic HTTP block",None,None)
            return io.BytesIO(json.dumps(value).encode("utf8"))
        return f

    def test_all_404_stops_with_four_receipts(self):
        out=probe(self.fake({u:404 for u in ENDPOINTS.values()}))
        self.assertEqual(out["status"],"SOURCE_ACCESS_STOP")
        self.assertEqual(len(out["endpoint_records"]),4)
        self.assertEqual([x["http_status"] for x in out["endpoint_records"]],[404]*4)
        self.assertFalse(out["raw_fish_trajectory_bytes_read"])

    def test_main_directory_lists_without_reading_any_file(self):
        pages={u:404 for u in ENDPOINTS.values()}
        pages[ENDPOINTS["repository_metadata"]]={"name":"veith_et_al_2024","default_branch":"main"}
        pages[ENDPOINTS["behavior_main"]]=[{"name":"a.csv","path":"behavior/a.csv","type":"file","size":100,"sha":"abc"}]
        result=probe(self.fake(pages))
        self.assertEqual(result["status"],"METADATA_LISTED_NOT_DATA_ADMITTED")
        self.assertEqual(result["endpoint_records"][-1]["entries"][0]["provider_sha"],"abc")
        self.assertFalse(result["raw_fish_trajectory_bytes_read"])
        self.assertIsNone(result["field_model_scores"])

    def test_broken_directory_schema_never_admits(self):
        pages={u:404 for u in ENDPOINTS.values()}
        pages[ENDPOINTS["behavior_main"]]=[{"name":"../secret","path":"bad","type":"file"}]
        self.assertEqual(probe(self.fake(pages))["status"],"SOURCE_ACCESS_STOP")

    def test_empty_directory_never_admits(self):
        pages={u:404 for u in ENDPOINTS.values()}
        pages[ENDPOINTS["behavior_main"]]=[]
        self.assertEqual(probe(self.fake(pages))["endpoint_records"][-1]["result"],"UNEXPECTED_DIRECTORY_SCHEMA")


if __name__=="__main__":
    unittest.main()
