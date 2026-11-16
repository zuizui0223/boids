"""No original author code loaded: test exact R-lexical helper semantics."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from r_code_source_audit import audit_R,TOKENS,SOURCE_FILE_LITERAL

class TestRSourceAudit(unittest.TestCase):
    def test_short_R_like_fixture(self):
        fixture=(
            "# read.csv('ignored.csv') is commented out\n"
            "x <- read.csv('/Users/analyst/data/input.csv')\n"
            "df <- dplyr::filter(x, clicks > 0)\n"
            "m <- glm(buzz ~ hr, data=df)\n"
        ) + ("# benign line\n"*20)
        source={
            "original_R_script_filename":"fixture.R",
            "original_R_script_bytes":len(fixture),
            "original_R_script_SHA256":"fixture",
            "original_CSV_member_filename":"fixture.csv",
            "original_CSV_member_bytes":1,
            "original_CSV_member_SHA256":"fixture",
        }
        result=audit_R(fixture.encode(),source)
        self.assertEqual(result["lexical_pattern_code_line_hits"]["read_csv_call"]["n_code_lines_with_token"],1)
        self.assertIn("input.csv",result["named_source_file_literals_basename_ONLY"])
        self.assertNotIn("ignored.csv",result["named_source_file_literals_basename_ONLY"])
        self.assertNotIn("/Users/analyst",str(result))
    def test_no_original_code_republished(self):
        self.assertIn("effort_keywords",TOKENS)
        self.assertIn("explicit_hour_grid",TOKENS)
        self.assertIsNotNone(SOURCE_FILE_LITERAL.search('"a.csv"'))

if __name__=="__main__":
    unittest.main()
