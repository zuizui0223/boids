"""Known-truth and failure-safe regression tests for v38 source-only screening."""
import io,zipfile,unittest
from bat_diel_source_gate import csv_structure,xlsx_structure,run

class SourceTests(unittest.TestCase):
    def test_csv_site_species_time_grain_without_reading_activity(self):
        s="site,date,time,species,activity,prey_count\nA,2025-05-01,22:30,Myotis,999,4\nA,2025-05-01,23:30,Pipistrellus,2,1\nB,2025-05-02,22:30,Myotis,5,3\n"
        r=csv_structure(s.encode())
        self.assertEqual(r["row_count"],3)
        self.assertEqual(r["categorical_support"]["site"]["distinct"],2)
        self.assertEqual(r["categorical_support"]["species"]["distinct"],2)
        self.assertNotIn("activity",r["categorical_support"])
        self.assertNotIn("prey_count",r["categorical_support"])
    def test_csv_semicolon_and_zero_detection_are_not_inferred(self):
        r=csv_structure(b"plot;date;activity\np1;2025-06-01;4\n")
        self.assertEqual(r["row_count"],1)
        self.assertEqual(r["categorical_support"]["plot"]["distinct"],1)
    def test_safe_xlsx_first_row_not_numeric_values(self):
        data=io.BytesIO()
        ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        with zipfile.ZipFile(data,'w') as z:
            z.writestr('xl/workbook.xml',f'<workbook xmlns="{ns}"><sheets><sheet name="Night activity" sheetId="1"/></sheets></workbook>')
            z.writestr('xl/sharedStrings.xml',f'<sst xmlns="{ns}"><si><t>Site</t></si><si><t>Temperature</t></si></sst>')
            z.writestr('xl/worksheets/sheet1.xml',f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row><row r="2"><c r="A2"><v>42</v></c><c r="B2"><v>999</v></c></row></sheetData></worksheet>')
        result=xlsx_structure(data.getvalue())
        self.assertEqual(result["status"],"XLSX_SCHEMA_ONLY")
        self.assertEqual(result["headers"][0]["header_text_only"],["Site","Temperature"])
        self.assertNotIn("999",str(result))
    def test_wrong_original_hash_never_admitted(self):
        result=run(lambda url:(200,'text/csv',b'site,date\nA,2025-01-01\n'))
        for study in result['sources'].values():
            for file in study.values():
                self.assertEqual(file["status"],"PUBLISHED_MD5_MISMATCH_STOP")
        self.assertFalse(result['behavior_model_fitted'])
    def test_html_and_denied_not_biological_nulls(self):
        r=run(lambda url:(200,'text/html',b'<!doctype html>Validating...'))
        self.assertTrue(all(v["status"]=="ACCESS_OR_SIZE_STOP" for s in r["sources"].values() for v in s.values()))
        self.assertFalse(r["numeric_bat_or_insect_outcomes_opened"])

if __name__=="__main__":
    unittest.main()
