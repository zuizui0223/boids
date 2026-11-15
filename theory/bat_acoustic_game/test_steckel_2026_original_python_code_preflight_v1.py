"""Invented original-package syntax/checkpoint-safety fixtures only."""
import io,unittest,zipfile
from steckel_2026_original_python_code_preflight_v1 import parse_source
def fakezip():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("pyproject.toml","[project]\nname='fabricated-bat3d'\nrequires-python='>=3.11'\ndependencies=['numpy','torch']\n")
        z.writestr("bat3d/kinematics.py","import numpy as np\n\ndef add(a,b): return a+b\n")
        z.writestr("tests/test_kinematics.py","import pytest\n\ndef test_add(): assert 1+2 ==3\n")
    return b.getvalue()
class TestAuthorSourceAST(unittest.TestCase):
    def test_source_modules_are_compiled_not_imported(self):
        x=parse_source(fakezip())
        self.assertEqual(x["source_python_files_AST_compiled"],2)
        self.assertEqual(x["source_total_selected_python_files"],2)
        self.assertFalse(x["original_modules_were_imported_or_run"])
    def test_source_original_unit_tests_discovered(self):
        x=parse_source(fakezip())
        self.assertEqual(x["author_test_modules"],{"tests/test_kinematics.py":["test_add"]})
    def test_source_dependencies_from_original_project(self):
        x=parse_source(fakezip())
        self.assertEqual(x["original_pyproject_declared_requirements"]["declared_project_dependencies"],["numpy","torch"])
        self.assertIn("pytest",x["top_level_import_coverage"])
    def test_source_syntax_error_is_not_silent_pass(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w") as z:z.writestr("tests/test_bad.py","def bad(:\n")
        x=parse_source(b.getvalue())
        self.assertEqual(x["source_python_files_AST_compiled"],0)
        self.assertEqual(len(x["source_syntax_errors_or_parse_stops"]),1)
        self.assertIn("SyntaxError",x["source_syntax_errors_or_parse_stops"][0]["error"])
    def test_source_eeg_or_run_data_not_in_py_dataset(self):
        a=parse_source(fakezip())
        self.assertNotIn("model.pt",a["source_python_file_sha256"])
        self.assertFalse(any(".mat" in z for z in a["source_python_file_sha256"]))
if __name__=="__main__":
    unittest.main()
