"""Synthetic XLSX parameter-source tests; no original bat data or actual model runs."""
import unittest,io,zipfile
from mazar_2026_clustering_source_completeness_v1 import (
  source_sonar_flags,PIN,MISSING_FN,MAX_ZENODO_ZIP
)

class TestSourceCompleteness(unittest.TestCase):
 def test_author_pinned_revision(self):
  self.assertEqual(PIN,"a74fb61a8efb57ca37693893c3bd7b35fa94fa89")
 def test_missing_function_name_not_filename_guess(self):
  self.assertEqual(MISSING_FN,"BatManueverDecision_FullConfusion_ver08Aug24")
 def test_public_source_size_cap(self):
  self.assertEqual(MAX_ZENODO_ZIP,80*1024*1024)
 def test_original_workbook_param_parser_invented(self):
  b=io.BytesIO()
  xml=(
  '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
  '<sheetData><row r="3"><c r="A3" t="inlineStr"><is><t>ObsClusterFlag</t></is></c>'
  '<c r="B3"><v>1</v></c></row>'
  '<row r="4"><c r="A4" t="inlineStr"><is><t>ObsMemorySize</t></is></c>'
  '<c r="B4"><v>10</v></c></row></sheetData></worksheet>'
  )
  with zipfile.ZipFile(b,"w") as z:z.writestr("xl/worksheets/sheet3.xml",xml)
  vals=source_sonar_flags(b.getvalue())
  self.assertEqual(vals["ObsClusterFlag"]["row_values"],["ObsClusterFlag","1"])
  self.assertEqual(vals["ObsMemorySize"]["row_values"],["ObsMemorySize","10"])
 def test_requires_batsonar_workbook_sheet(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,"w") as z:z.writestr("xl/worksheets/sheet1.xml","<sheet/>")
  with self.assertRaisesRegex(ValueError,"BATSONAR_SHEET3_MISSING"):source_sonar_flags(b.getvalue())
 def test_missing_field_is_not_assumed_true(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,"w") as z:
   z.writestr("xl/worksheets/sheet3.xml",
      '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>')
  self.assertNotIn("ObsClusterFlag",source_sonar_flags(b.getvalue()))
if __name__=="__main__":unittest.main()
