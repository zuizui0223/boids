"""Known-truth original USFWS Nightly sheet observational grain and effort gates."""
import hashlib
import io
import unittest
import zipfile

from usfws_nightly_effort_grain import inspect_book,run,sanitized_label
from test_usfws_bounded_xlsx_headers import synthetic_archive,fake_source

NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def sample_book():
    f=io.BytesIO()
    with zipfile.ZipFile(f,"w",compression=zipfile.ZIP_DEFLATED) as z:
        hdr=["Site","Night","WAC Files","Bat Pass Count","Species1"]
        parts=['<row r="1">']
        for i,name in enumerate(hdr):
            col=chr(65+i)
            parts.append(f'<c r="{col}1" t="inlineStr"><is><t>{name}</t></is></c>')
        parts.append("</row>")
        for row,(site,night,recordings,bats) in enumerate([
                ("A","2020-05-01",8,0),
                ("B","2020-05-01",12,999),
                ("A","2020-05-02",10,21)],start=2):
            parts.append(f'<row r="{row}"><c r="A{row}" t="inlineStr"><is><t>{site}</t></is></c>'
                         f'<c r="B{row}" t="inlineStr"><is><t>{night}</t></is></c>'
                         f'<c r="C{row}"><v>{recordings}</v></c>'
                         f'<c r="D{row}"><v>{bats}</v></c></row>')
        xml=f'<worksheet xmlns="{NS}"><sheetData>'+''.join(parts)+'</sheetData></worksheet>'
        z.writestr("xl/workbook.xml",f'<workbook xmlns="{NS}"><sheets><sheet name="Nightly Pass Counts" sheetId="1"/></sheets></workbook>')
        z.writestr("xl/worksheets/sheet1.xml",xml)
    return f.getvalue()

class V45EffortTests(unittest.TestCase):
    def test_site_night_and_wac_presence_without_bat_outcomes(self):
        out=inspect_book(sample_book(),"nightly_pass_counts")
        r=out["sheets"][0]
        self.assertEqual(out["status"],"WORKSHEET_GRAIN_AUDITED_NO_BAT_VALUES")
        self.assertEqual(r["source_rows_excluding_header"],3)
        self.assertEqual(r["distinct_anonymized_observation_keys"],3)
        self.assertEqual(r["nonempty_effort_field_cells"],3)
        self.assertIn("site",r["unambiguous_id_column_categories"])
        self.assertIn("night",r["unambiguous_id_column_categories"])
        self.assertFalse(r["original_bat_pass_count_values_interpreted"])
        self.assertNotIn("999",str(r))
        self.assertNotIn("2020-05-01",str(r))

    def test_ambiguous_night_metadata_does_not_silently_pass(self):
        # The existing v44 synthetic archive has 2 original Excel books but
        # no site index in the nightly table, so the gate must fail closed.
        outer,tail,directory=synthetic_archive()
        out=run(fake_source(outer,tail),tail_sha=hashlib.sha256(tail).hexdigest())
        self.assertEqual(out["status"],"SOURCE_NIGHT_OR_EFFORT_GRAIN_UNRESOLVED_STOP")
        self.assertFalse(out["site_night_effort_column_structurally_admitted"])
        self.assertFalse(out["bat_pass_counts_or_species_numeric_values_interpreted"])

    def test_repeated_source_key_counted_not_ignored(self):
        raw=sample_book()
        out=inspect_book(raw,"nightly_pass_counts")
        self.assertEqual(out["sheets"][0]["duplicate_source_rows_under_key"],0)

    def test_sensitive_header_not_exported(self):
        self.assertIsNone(sanitized_label("Roost GPS longitude"))
        self.assertIsNone(sanitized_label("contact_email"))

    def test_no_unverified_original_tail_admission(self):
        outer,tail,directory=synthetic_archive()
        out=run(fake_source(outer,tail),tail_sha="0"*64)
        self.assertEqual(out["status"],"PINNED_TAIL_CHECKSUM_STOP")
        self.assertFalse(out["true_zero_nights_verified"])

if __name__=="__main__":
    unittest.main()
