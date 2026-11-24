"""v34b original-source-only ZIP and author metadata audit known-truth fake data."""
from __future__ import annotations
import hashlib,io,zipfile,unittest
from validation_fish_school_v34.original_small_source_files import (
    safe_zip_original_members,source_code_names_only,SourceStop,exact_small_author_bytes,
    source_run
)

def synthetic_zip(entries=None):
    if entries is None:entries=[("trial_manifest.csv",b"id,condition\n"),("README.txt",b"SYNTHETIC")]
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as z:
        for n,data in entries:z.writestr(n,data)
    return b.getvalue()

class FakeResp:
    def __init__(self,url,body):self.url=url;self.body=body
    def __enter__(self):return self
    def __exit__(self,*a):return False
    def geturl(self):return self.url
    def read(self,n):return self.body[:n]

class SourceOnlyAuthorCodeKnownTruth(unittest.TestCase):
    def test_archive_original_member_names_only_no_original_rows_decompressed(self):
        summary=safe_zip_original_members(synthetic_zip())
        self.assertEqual(summary["original_archive_entries"],2)
        self.assertFalse(summary["original_zip_data_members_read"])
        self.assertTrue(all(x["member_contents_NOT_EXTRACTED"] for x in summary["original_zip_member_listing_without_extracting_content"]))

    def test_untrusted_parent_directory_member_rejected(self):
        with self.assertRaises(SourceStop):
            safe_zip_original_members(synthetic_zip([("../bad.csv",b"1,2\n")]))

    def test_empty_corrupted_zip_rejected(self):
        with self.assertRaises(SourceStop):
            safe_zip_original_members(b"HTTP ERROR 403")

    def test_original_md5_and_size_required_without_source_redirect(self):
        url="https://ndownloader.figshare.com/files/123"
        raw=b"Synthetic only, no fish"
        md5=hashlib.md5(raw).hexdigest()
        opener=lambda req,timeout:FakeResp(url,raw)
        self.assertEqual(exact_small_author_bytes(url,len(raw),md5,opener),raw)
        with self.assertRaises(SourceStop):
            exact_small_author_bytes(url,len(raw)+1,md5,opener)

    def test_original_provider_URL_external_is_rejected(self):
        with self.assertRaises(SourceStop):
            exact_small_author_bytes("https://fish-data-unverified.example.com/x",22,"0"*32)

    def test_source_code_AST_only_no_execution(self):
        raw=b"import numpy as np\ncondition='C1-OneReal+OneVirtual.dat'\ndata=np.loadtxt(condition)\n"
        d=source_code_names_only("Model3D-VR.py",raw)
        self.assertTrue(d["source_original_python_code_ast_syntax_parsed_without_running"])
        self.assertFalse(d["original_author_code_NOT_EXECUTED"] is False)
        self.assertFalse(d["original_source_lines_or_coefficients_redistributed"])

    def test_unavailable_provider_source_requires_STOP_no_fish_effect(self):
        def unavailable(_):raise SourceStop("SYNTHETIC_FIGSHARE_SOURCE_MISSING")
        d=source_run(fetchmeta=unavailable)
        self.assertEqual(d["status"],"SOURCE_ACCESS_STOP")
        self.assertEqual(d["n_verified_original_author_records"],0)
        self.assertFalse(d["original_2026_research_trial_values_read"])
        self.assertFalse(d["original_experimental_treatment_effect_fit"])

if __name__=="__main__":unittest.main()
