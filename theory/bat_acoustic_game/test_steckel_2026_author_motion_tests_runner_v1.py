"""Original independent code runner safety tests using invented archives only."""
import io,json,tempfile,unittest,zipfile
from pathlib import Path
import steckel_2026_author_original_motion_tests_v1 as m
def fakezip(traversal=False):
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        for name in m.TESTS:z.writestr(name,"def test_origin(): assert 1==1\n")
        z.writestr("bat3d/__init__.py","")
        z.writestr("bat3d/sim/motion.py","def x():return 1\n")
        if traversal:z.writestr("bat3d/../../escape.py","pass\n")
    return b.getvalue()
class TestOriginalCodeSafety(unittest.TestCase):
 def test_three_original_test_modules_fixed(self):
    self.assertEqual(m.TESTS,("tests/test_3d_flow_ode.py","tests/test_3d_warp.py","tests/test_3d_axis_sym.py"))
 def test_exact_sixteen_test_expectations(self):
    self.assertEqual(sum(m.EXPECTED_TESTS),16)
 def test_safe_temp_source_manifest_only(self):
    with tempfile.TemporaryDirectory() as d:
        files=m.selected_original_sources(fakezip(),d)
        self.assertEqual(len(files),5)
        self.assertTrue((Path(d)/"tests/test_3d_flow_ode.py").exists())
 def test_zip_traversal_rejected(self):
    with tempfile.TemporaryDirectory() as d:
        with self.assertRaisesRegex(ValueError,"ZIP_PATH_ESCAPE"):
            m.selected_original_sources(fakezip(True),d)
 def test_source_paths_have_no_htrf_or_weights(self):
    with tempfile.TemporaryDirectory() as d:
        files=m.selected_original_sources(fakezip(),d)
        self.assertTrue(all(f["path"].endswith(".py") for f in files))
        self.assertFalse(any(x["path"].endswith((".pt",".mat",".npz")) for x in files))
if __name__=="__main__":unittest.main()
