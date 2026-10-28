"""v17-B pure source-provenance and masked OOXML tests: no wild GPS."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import published_S3_pair_source as p

WORKBOOK=b"""<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<workbook xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'><sheets><sheet name='S3' sheetId='1'/></sheets></workbook>"""
SHARED=b"""<?xml version='1.0' encoding='utf-8'?>
<sst xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'>
<si><t>Bird ID</t></si><si><t>Similar size pairing</t></si>
<si><t>Different size pairing</t></si><si><t>B01</t></si>
<si><t>B82</t></si><si><t>B07</t></si>
</sst>"""
SHEET=b"""<?xml version='1.0' encoding='utf-8'?>
<worksheet xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'>
<sheetData>
<row r='1'><c r='A1' t='s'><v>0</v></c><c r='B1' t='s'><v>1</v></c><c r='C1' t='s'><v>2</v></c></row>
<row r='2'><c r='A2' t='s'><v>3</v></c><c r='B2' t='s'><v>4</v></c><c r='C2' t='s'><v>5</v></c><c r='D2'><v>35.2</v></c></row>
</sheetData></worksheet>"""


class SourceSupplementTests(unittest.TestCase):
    def test_exact_public_DOI_and_restrict_direct_urls(self):
        self.assertEqual(p.SOURCE_DOI,"10.1371/journal.pbio.3000299.s008")
        self.assertTrue(all(v.startswith(("https://journals.plos.org/",
                                           "https://pmc.ncbi.nlm.nih.gov/",
                                           "https://www.ncbi.nlm.nih.gov/"))
                            for v in p.BINARY_CANDIDATES))

    def test_ooxml_shared_text_recovery_and_numeric_mask(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"published_s3.xlsx"
            with zipfile.ZipFile(f,"w") as z:
                z.writestr("xl/workbook.xml",WORKBOOK)
                z.writestr("xl/sharedStrings.xml",SHARED)
                z.writestr("xl/worksheets/sheet1.xml",SHEET)
            r=p.parse_workbook(f)
        self.assertEqual(r["workbook_sheets"],1)
        self.assertIn("B01",r["distinct_bird_identifiers_from_s3"])
        self.assertIn("B82",r["distinct_bird_identifiers_from_s3"])
        self.assertIn("B07",r["distinct_bird_identifiers_from_s3"])
        row=r["worksheet_reports"][0]["preview_first_35_rows_numeric_body_traits_masked"][1]
        self.assertEqual(row["text_only_cells"]["D"],"<numeric body trait masked>")
        self.assertNotIn("35.2",json.dumps(r))
        self.assertFalse(r["weather_or_GPS_data_read"])
        self.assertEqual(r["flight_turns_scored"],0)

    def test_alphanumeric_identifier_not_inferred_from_numeric_body_trait(self):
        self.assertEqual(p.mask_text("34.2"),"<numeric body trait masked>")
        self.assertEqual(p.ID.findall("Different size partner B07"),["B07"])
        self.assertEqual(p.mask_text("  similar sized bird  "), "similar sized bird")

    def test_duplicate_xlsx_members_fail(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"bad.xlsx"
            with zipfile.ZipFile(f,"w") as z:
                z.writestr("xl/workbook.xml",WORKBOOK)
                z.writestr("xl/worksheets/sheet1.xml",SHEET)
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    z.writestr("xl/worksheets/sheet1.xml",SHEET)
            with self.assertRaisesRegex(ValueError,"Duplicate"):
                p.parse_workbook(f)


if __name__=="__main__":
    unittest.main()
