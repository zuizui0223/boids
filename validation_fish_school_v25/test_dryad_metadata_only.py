"""v25 all known-truth tests are fake HTTP; no live original biological data."""
import io,json,unittest
from urllib.error import HTTPError
from validation_fish_school_v25 import dryad_metadata_only as m

class Fake:
    def __init__(self,content,url):
        self.content=content
        self.url=url
    def read(self,n):
        return self.content[:n]
    def geturl(self):
        return self.url
    def __enter__(self):return self
    def __exit__(self,*args):return False

def mock(pages):
    def openapi(req,timeout=25):
        if req.full_url not in pages:raise HTTPError(req.full_url,404,"Not Found",None,None)
        p=pages[req.full_url]
        if isinstance(p,int):raise HTTPError(req.full_url,p,"HTTP block",None,None)
        return Fake(json.dumps(p).encode(),req.full_url)
    return openapi

class OriginalAPIFixtures(unittest.TestCase):
    def test_only_metadata_no_fish_outcomes(self):
        pages={
          m.URL:{"identifier":"doi:10.5061/dryad.gxd25482b","title":"known-truth fixture",
                 "_links":{"stash:versions":{"href":"/api/v2/datasets/123/versions"}}},
          m.ROOT+"/api/v2/datasets/123/versions":{"_embedded":{"stash:versions":[{"id":101}]}},
          m.ROOT+"/api/v2/versions/101/files":{"_embedded":{"stash:files":[{"path":"data.csv","size":42}]}}
        }
        ans=m.metadata_only(mock(pages))
        self.assertEqual(ans["status"],"METADATA_ONLY_NOT_YET_TRAJECTORIES")
        self.assertEqual(ans["file_count"],1)
        self.assertFalse(ans["original_fish_values_or_files_downloaded"])
        self.assertFalse(ans["treatment_effect_reestimated"])

    def test_401_403_404_do_not_fabricate(self):
        for code in (401,403,404):
            ans=m.metadata_only(mock({m.URL:code}))
            self.assertEqual(ans["status"],"SOURCE_ACCESS_STOP")
            self.assertEqual(ans["stop_reason"],"HTTP_"+str(code))
            self.assertNotIn("files",ans)

    def test_api_error_envelope_cannot_count_as_dataset(self):
        ans=m.metadata_only(mock({m.URL:{"identifier":"doi:10.5061/dryad.gxd25482b","message":"Not found","id":7}}))
        self.assertEqual(ans["status"],"SOURCE_ACCESS_STOP")
        self.assertEqual(ans["stop_reason"],"API_ERROR_ENVELOPE_NOT_PUBLISHED_DATASET_METADATA")
        self.assertEqual(ans["source_api_message"],"Not found")

    def test_doi_mismatch_rejected(self):
        ans=m.metadata_only(mock({m.URL:{"identifier":"doi:10.5061/dryad.xxxxx"}}))
        self.assertEqual(ans["stop_reason"],"DOI_IDENTITY_NOT_VERIFIED")

    def test_never_download_raw_files(self):
        with self.assertRaises(m.SourceStop):
            m.safe_link("https://datadryad.org/api/v2/versions/2/files/45/download")
        with self.assertRaises(m.SourceStop):
            m.safe_link("http://attacker.example/file.json")
        with self.assertRaises(m.SourceStop):
            m.safe_link("https://datadryad.org/download/file.zip")

    def test_incomplete_pagination_stop(self):
        pages={
          m.URL:{"doi":"10.5061/dryad.gxd25482b","_links":{"stash:version":{"href":"/api/v2/versions/12"}}},
          m.ROOT+"/api/v2/versions/12":{"id":12},
          m.ROOT+"/api/v2/versions/12/files":{"count":101,"files":[{"name":"file.txt"}]}
        }
        out=m.metadata_only(mock(pages))
        self.assertEqual(out["stop_reason"],"PAGINATION_INCOMPLETE")

    def test_empty_or_bad_file_list_source_stop(self):
        pages={
          m.URL:{"identifier":"doi:10.5061/dryad.gxd25482b",
                 "_links":{"stash:version":{"href":"/api/v2/versions/12"}}},
          m.ROOT+"/api/v2/versions/12":{"id":12},
          m.ROOT+"/api/v2/versions/12/files":{"files":[]}
        }
        out=m.metadata_only(mock(pages))
        self.assertEqual(out["status"],"SOURCE_ACCESS_STOP")


if __name__=="__main__":unittest.main()
