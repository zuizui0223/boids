"""v36 source-free fake author code only, no original experiment values."""
import unittest
from validation_fish_school_v36.original_published_author_code_schema import (
 source_python_AST_static,source_parameter_names_only,
 original_figshare_description_metadata,SourceStop,EXP_DAT_FILES
)
class CodeOnlySourceGate(unittest.TestCase):
    def test_original_named_experiment_DAT_file_loaders_detected(self):
        code="\n".join(["import numpy as np"]+[
           f'case_{i}=np.loadtxt("{name}")' for i,name in enumerate(EXP_DAT_FILES)])
        r=source_python_AST_static(code)
        x=r["source_identifier_presence_only"]["original_module_direct_DAT_load_source_paths"]
        self.assertTrue(x["listed_named_original_EXPERIMENTAL_DAT_in_ast_loader"])
        self.assertEqual(x["positive_original_DAT_column_number_map"],"NOT_VERIFIED")
        self.assertFalse(r["original_author_simulation_code_executed"])

    def test_simulation_writer_is_not_mistaken_for_experiment_loader(self):
        code='import numpy as np\nnp.savetxt("C2-OneReal+OneVirtual.dat",np.zeros((10,9)))\n'
        r=source_python_AST_static(code)
        x=r["source_identifier_presence_only"]["original_module_direct_DAT_load_source_paths"]
        self.assertFalse(x["listed_named_original_EXPERIMENTAL_DAT_in_ast_loader"])
        self.assertTrue(len(r["original_script_simulation_or_source_write_call_line_numbers_first_40"])>=1)

    def test_generic_model_loadtxt_without_source_file_is_not_dat_proof(self):
        r=source_python_AST_static('import numpy as np\nx=np.loadtxt("my_simulation.dat")\n')
        self.assertFalse(r["source_identifier_presence_only"][
          "original_module_direct_DAT_load_source_paths"][
            "listed_named_original_EXPERIMENTAL_DAT_in_ast_loader"])

    def test_source_code_python_syntax_error_stops_without_execution(self):
        with self.assertRaises(SourceStop):
            source_python_AST_static("def f(: pass")

    def test_author_parameters_retain_only_names_no_values(self):
        x=source_parameter_names_only("alpha = 100.0\n# no fish\nbeta: 2\n")
        self.assertEqual(x["original_input_parameter_source_line_count"],3)
        self.assertEqual(x["source_parameter_LHS_name_line_numbers_first_60"][0]["original_parameter_token_label"],"alpha")
        self.assertFalse(x["original_input_parameter_VALUES_redistributed"])
        self.assertFalse(x["original_parameter_text_executed"])

    def test_figshare_original_description_no_explicit_schema_stop(self):
        x=original_figshare_description_metadata("<p>Published 2026 data file names and 3D experiment records</p>")
        self.assertFalse(x["original_source_description_has_EXPLICIT_nine_columns_ordered"])
        self.assertTrue(x["original_source_description_text_NOT_redistributed"])

if __name__=="__main__":unittest.main()
