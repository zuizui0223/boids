"""v42 exact-source USFWS ZIP/headers only, synthetic known-truth tests."""
import io
import unittest
import urllib.error
import zipfile
from usfws_official_source_gate import source_fetch,xlsx_metadata,zip_info

NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"

def pretend_source():
    nested=io.BytesIO()
    with zipfile.ZipFile(nested,"w") as x:
        x.writestr("xl/workbook.xml",
            f'<workbook xmlns="{NS}"><sheets><sheet name="Nightly Pass Counts" sheetId="1"/></sheets></workbook>')
        x.writestr("xl/sharedStrings.xml",
            f'<sst xmlns="{NS}"><si><t>Night</t></si><si><t>Detector</t></si></sst>')
        x.writestr("xl/worksheets/sheet1.xml",
            f'<worksheet xmlns="{NS}"><sheetData><row r="1">'
            f'<c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c>'
            f'</row><row r="2"><c r="A2"><v>999</v></c><c r="B2"><v>800</v></c></row></sheetData></worksheet>')
    outer=io.BytesIO()
    with zipfile.ZipFile(outer,"w") as z:z.writestr("summary.xlsx",nested.getvalue())
    return outer.getvalue()

class Tests(unittest.TestCase):
    def test_nested_xlsx_metadata_never_reads_bat_counts(self):
        data=pretend_source()
        r=zip_info(data)
        self.assertEqual(r["status"],"ORIGINAL_ZIP_CENTRAL_DIRECTORY_AND_XLSX_HEADERS_ONLY")
        self.assertEqual(r["xlsx_member_n"],1)
        self.assertIn("night",str(r["xlsx_header_structural_previews"]))
        self.assertNotIn("999",str(r))
        self.assertFalse(r["original_numeric_bat_pass_counts_or_species_values_opened"])
    def test_valid_source_is_not_complete_effort_admission(self):
        data=pretend_source()
        r=source_fetch(lambda url:(200,"application/zip",str(len(data)),data))
        self.assertIsNotNone(r.get("source_sha256"))
        self.assertFalse(r["complete_zero_night_effort_qualified"])
    def test_html_200_is_not_source(self):
        r=source_fetch(lambda u:(200,"text/html","23",b"<html>Validating...</html>"))
        self.assertEqual(r["status"],"SOURCE_HTML_OR_JSON_STOP")
    def test_invalid_zip_stops(self):
        r=source_fetch(lambda u:(200,"application/octet-stream","5",b"noise"))
        self.assertEqual(r["status"],"ORIGINAL_ZIP_INVALID_STOP")
    def test_provider_403_is_access_stop_not_no_bats(self):
        def err(url):
            raise urllib.error.HTTPError(url,403,"denied",{},None)
        r=source_fetch(err)
        self.assertEqual(r["status"],"HTTP_ACCESS_STOP")
        self.assertFalse(r["acoustic_model_fitted"])
if __name__=="__main__":
    unittest.main()
