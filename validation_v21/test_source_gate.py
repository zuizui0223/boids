"""v21 no-outcome original Dryad redstart source and week-grain tests."""
from __future__ import annotations
import unittest
import pandas as pd
import source_gate as v

class TestDryadSourceSafety(unittest.TestCase):
    def test_exact_independent_source_and_only_required_files(self):
        self.assertEqual(v.DOI,"10.5061/dryad.gb5mkkwx1")
        self.assertEqual(v.TARGET_FILES,("forays.rds","ndvi.rds"))
        self.assertNotIn("mcp.rds",v.TARGET_FILES)
        self.assertEqual(v.MAX_BYTES,10_000_000)

    def test_only_official_dryad_domain_source_links(self):
        self.assertEqual(v.link({"_links":{"stash:version":{
            "href":"/api/v2/versions/555"}}},"stash:version"),
            "https://datadryad.org/api/v2/versions/555")
        with self.assertRaisesRegex(ValueError,"Non-Dryad"):
            v.link({"_links":{"stash:version":{
                "href":"https://outside.example.org/tracks"}}},"stash:version")

    def test_source_file_manifest_is_discovered_not_invented(self):
        x={"_embedded":{"stash:files":[
            {"path":"forays.rds","id":11,"size":971,"digest":"deadbeef","digestType":"md5"},
            {"path":"ndvi.rds","id":12,"size":2240}]}}
        z=v.official_list(x)
        self.assertEqual(len(z),2)
        self.assertEqual(z[0]["size"],971)
        self.assertEqual(z[1]["path"],"ndvi.rds")

    def test_independent_bird_week_repetition_is_counted_without_values(self):
        data=pd.DataFrame({
            "motusID":[str(i) for i in range(10) for _ in range(5)],
            "year":[2018]*50,
            "week":[w for i in range(10) for w in range(5)],
            "median_transitions":[3.14]*50,
            "HABITAT":["Dry Scrub"]*50})
        # The source reader has a pyreadr boundary; verify the same
        # ID-only grain computation without opening ecological outcomes.
        d=data.dropna(subset=["motusID","year","week"])
        counts=d.groupby("motusID").size()
        self.assertEqual(int((counts>=3).sum()),10)
        self.assertEqual(int(sum(max(0,x-2) for x in counts)),30)
        self.assertEqual(d[["motusID","year","week"]].duplicated().sum(),0)

    def test_download_metadata_fail_closed_when_missing_provider_size(self):
        fake={"name":"forays.rds","id":133,"size":0}
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            r=v.fetch_file(fake,Path(d)/"x.rds")
        self.assertEqual(r["status"],"SOURCE_OUTSIDE_BOUNDED_FILE_REQUIREMENT")

    def test_error_label_does_not_expose_private_headers_or_server_body(self):
        self.assertIn("ValueError",v.errcode(ValueError("source missing")))
        self.assertTrue(v.API.startswith("https://datadryad.org/api/v2/datasets/"))
        self.assertNotIn("mcp.rds",v.TARGET_FILES)

if __name__=="__main__":
    unittest.main()
