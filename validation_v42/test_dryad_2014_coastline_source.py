import io
import json
import unittest
import zipfile
from urllib.request import Request

from dryad_2014_coastline_source import (
    DOI,ORIGINAL_ARCHIVE,COAST_BASENAMES,
    BoundedRangeReader,SourceStop,coast_member_info,
    original_archive_metadata,probe_range_size)

class SourceRangeTests(unittest.TestCase):
    def test_official_metadata_and_unique_original_archive(self):
        def fake(url):
            if url.endswith("/versions"):
                return {"_embedded":{"stash:versions":[
                    {"id":123,"versionNumber":1,"_links":{"stash:files":{"href":"/api/v2/versions/123/files"}}},
                    {"id":124,"versionNumber":2,"_links":{"stash:files":{"href":"/api/v2/versions/124/files"}}}]}}
            self.assertTrue(url.endswith("/versions/124/files"))
            return {"_embedded":{"stash:files":[
                {"id":45,"path":"README.md","size":100},
                {"id":46,"path":ORIGINAL_ARCHIVE,"size":1430000000}]}}
        info=original_archive_metadata(get=fake)
        self.assertEqual(info["version_id"],124)
        self.assertEqual(info["original_provider_file_id"],46)
        self.assertIn("files/46/download",info["archive_download_url"])
        self.assertEqual(DOI,"doi:10.5061/dryad.wm37pvmth")
    def test_byte_range_reader_extracts_only_selected_small_members(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,"w",compression=zipfile.ZIP_DEFLATED,allowZip64=True) as archive:
            for name in COAST_BASENAMES:
                archive.writestr("maps/"+name,
                                 "x y\n"+"".join(f"{160000+i} {603000+i}\n" for i in range(80)))
            archive.writestr("unrelated_model_file.txt","x"*500)
        source=data.getvalue()
        requested=[]
        def local_range(url,start,end,total):
            self.assertEqual(total,len(source))
            requested.append((start,end))
            return source[start:end+1]
        reader=BoundedRangeReader("https://dryad.example/original.zip",
                                  len(source),range_get=local_range)
        coastline,member_n=coast_member_info({},reader)
        self.assertEqual(member_n,3)
        self.assertEqual([x["member"] for x in coastline],list(COAST_BASENAMES))
        self.assertEqual([x["first_two_column_numeric_lines"] for x in coastline],[80,80])
        self.assertTrue(all(x["zip_original_member_CRC32_verified"] for x in coastline))
        self.assertTrue(requested)
        self.assertLess(reader.fetched,16_000_000)
    def test_server_ignoring_range_is_hard_source_stop(self):
        class FakeResponse:
            status=200
            headers={"Content-Range":""}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return b"PK"[:n]
        class FakeOpener:
            def __call__(self,req,timeout):
                self.assert_header(req)
                return FakeResponse()
            def assert_header(self,req):
                selfreq=req.get_header("Range")
                if selfreq!="bytes=0-0":raise AssertionError(selfreq)
        with self.assertRaisesRegex(SourceStop,"RANGE_NOT_SUPPORTED"):
            probe_range_size("https://datadryad.org/api/v2/files/46/download",
                             opener=FakeOpener())
    def test_untrusted_byte_offset_and_metadata_provider_rejected(self):
        with self.assertRaises(SourceStop):
            original_archive_metadata(get=lambda url:{"_embedded":{"stash:versions":[]}})
        reader=BoundedRangeReader("https://x.test",500,
                                  range_get=lambda *a:b"")
        with self.assertRaisesRegex(SourceStop,"UNBOUNDED_ZIP_READ"):
            reader.read(8_000_001)

if __name__=="__main__":
    unittest.main()
