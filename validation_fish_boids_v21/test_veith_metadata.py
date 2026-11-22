"""Known-truth, no-network metadata-only GIN gate tests."""
import io
import json
import unittest
from urllib.error import HTTPError, URLError

from validation_fish_boids_v21.veith_source_metadata import inspect


class SourceGateTests(unittest.TestCase):
    @staticmethod
    def fake(json_value):
        def open_ok(*args, **kwargs):
            return io.BytesIO(json.dumps(json_value).encode("utf-8"))
        return open_ok

    def test_only_metadata_listed_not_data_admitted(self):
        out = inspect(self.fake([{"name": "sample.csv", "path": "behavior/sample.csv", "type": "file", "size": 52, "sha": "provider_key"}]))
        self.assertEqual(out["status"], "METADATA_LISTED_NOT_DATA_ADMITTED")
        self.assertEqual(out["entry_count"], 1)
        self.assertEqual(out["entries"][0]["provider_sha"], "provider_key")
        self.assertFalse(out["raw_fish_data_downloaded"])
        self.assertFalse(out["field_scores_computed"])

    def test_http_401_stops_without_data_claim(self):
        def forbidden(*args, **kwargs):
            raise HTTPError("test", 401, "Unauthorized", None, None)
        out = inspect(forbidden)
        self.assertEqual((out["status"], out["http_status"]), ("SOURCE_ACCESS_STOP", 401))

    def test_network_stop(self):
        def failure(*args, **kwargs):
            raise URLError("remote unreachable")
        self.assertEqual(inspect(failure)["stop_reason"], "NETWORK_OR_TIMEOUT")

    def test_bad_json_and_nonlist_stop(self):
        def html(*args, **kwargs):
            return io.BytesIO(b"<html>login</html>")
        self.assertEqual(inspect(html)["stop_reason"], "NOT_JSON")
        self.assertEqual(inspect(self.fake({"message": "unsupported"}))["stop_reason"], "NOT_DIRECTORY_LISTING")

    def test_unbounded_path_or_schema_fails(self):
        for row in ({"name": "x", "path": "elsewhere/x", "type": "file"},
                    {"name": "x", "path": "behavior/x", "type": 3},
                    {"name": "x", "path": "behavior/x", "type": "file", "size": -1}):
            self.assertEqual(inspect(self.fake([row]))["status"], "SOURCE_ACCESS_STOP")


if __name__ == "__main__":
    unittest.main()
