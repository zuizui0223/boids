"""Synthetic-only source byte integrity and code-index extraction tests."""
import io,json,zipfile,unittest
from unittest.mock import patch
from external_2026_EEG_and_3D_ERTF_source_gate_v1 import central_zip_names,eocd_info
import steckel_2026_range_code_source_gate_v1 as m

def fake_package():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.md","Invented 3D source README")
        z.writestr("experiments.json",json.dumps({"E1":"toy/","C1":"control/"}))
        z.writestr("MANIFEST.sha256","fake checksum")
        c=io.BytesIO()
        with zipfile.ZipFile(c,"w",zipfile.ZIP_DEFLATED) as package:
            package.writestr("bat3d/renderer.py","import numpy")
            package.writestr("tests/test_renderer.py","assert 1")
            package.writestr("requirements.txt","numpy\npytest\n")
        z.writestr("code.zip",c.getvalue())
    return b.getvalue()

class TestSourceCodeRangeAccess(unittest.TestCase):
    def test_extract_original_member_checks_exact_crc_and_sha(self):
        packed=fake_package()
        loc=eocd_info(packed[-131072:],len(packed))
        dirbytes=packed[loc["directory_offset"]:loc["directory_offset"]+loc["directory_size"]]
        entries={x["path"]:x for x in central_zip_names(dirbytes)}
        def fetch(_url,method="GET",range_header=None,maxbytes=100000):
            self.assertTrue(range_header.startswith("bytes="))
            first,last=(int(n) for n in range_header[6:].split("-"))
            if last-first+1>maxbytes:raise ValueError("FAKE OVER CAP")
            return {"http":206},packed[first:last+1]
        with patch.object(m,"fetch",fetch):
            raw,receipt=m.extract_single_member("https://zenodo.org/fake",entries["code.zip"],100000)
        self.assertEqual(receipt["member_sha256"],m.sha(raw))
        with zipfile.ZipFile(io.BytesIO(raw)) as z:self.assertIn("bat3d/renderer.py",z.namelist())
    def test_no_original_model_score_values_read_in_index(self):
        index=m.inspect_experiment_manifest(json.dumps({"E1":"run_main","E2":"run_ablation","C1":"control"}).encode())
        self.assertEqual(index["source_declared_experiment_IDs"],["C1","E1","E2"])
        self.assertEqual(index["mapping_item_count"],3)
    def test_inner_source_code_and_tests_only_file_metadata(self):
        outer=fake_package()
        with zipfile.ZipFile(io.BytesIO(outer)) as z:inner=z.read("code.zip")
        record=m.inspect_author_code(inner)
        self.assertIn("bat3d/renderer.py",record["python_bat3d_source_paths"])
        self.assertIn("tests/test_renderer.py",record["source_test_paths"])
        self.assertIn("requirements.txt",record["source_requirements_paths"])
        self.assertEqual(record["code_zip_member_count"],3)
    def test_reject_member_cap(self):
        with self.assertRaisesRegex(ValueError,"OVER_CAP"):
            m.extract_single_member("https://zenodo.org/fake",
                 {"compressed_bytes":200000,"local_header_byte_offset":0},100)
    def test_untrusted_index_and_prefix_not_a_file(self):
        self.assertNotIn("source_data/run_table.json",m.ADMITTED)
        self.assertNotIn("data/HRTF_Phyllostomus_Discolor_azel.mat",m.ADMITTED)
        self.assertNotIn("worlds.zip",m.ADMITTED)
    def test_declared_source_caps(self):
        self.assertGreater(m.ADMITTED["code.zip"],11*1024*1024)
        self.assertLess(m.ADMITTED["code.zip"],20*1024*1024)

if __name__=="__main__":
    unittest.main()
