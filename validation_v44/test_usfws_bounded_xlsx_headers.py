"""Pure known-truth v44 USFWS selective CRC XLSX header admission tests."""
import hashlib
import io
import struct
import unittest
import zipfile

from usfws_bounded_xlsx_headers import (
    ORIGINAL_TOTAL,TAIL_BYTES,MAX_COMPRESSED,fetch_member,
    full_directory_entries,original_xlsx_headers,run,source_prefix,
    unzip_original_member,
)
from usfws_zip_range_directory import central_location

NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def synthetic_xlsx(headers):
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("xl/workbook.xml",
            f'<workbook xmlns="{NS}"><sheets><sheet name="Nightly Data" sheetId="1"/></sheets></workbook>')
        xml=f'<worksheet xmlns="{NS}"><sheetData><row r="1">'
        for index,label in enumerate(headers):
            col=chr(ord("A")+index)
            xml+=f'<c r="{col}1" t="inlineStr"><is><t>{label}</t></is></c>'
        xml+='</row><row r="2"><c r="A2"><v>9999</v></c><c r="B2"><v>314159</v></c></row></sheetData></worksheet>'
        z.writestr("xl/worksheets/sheet1.xml",xml)
    return b.getvalue()


def synthetic_archive():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("USFWS/Nightly Pass Counts.xlsx",synthetic_xlsx(["Night","WAC Files","Hours","Pass Count"]))
        z.writestr("USFWS/Metadata.xlsx",synthetic_xlsx(["Station","Recorder","Deployment","Start Date"]))
        for k in range(9):
            z.writestr(f"USFWS/Pass Lists {k}.xlsx",synthetic_xlsx(["Source","Timestamp","Species"]))
    archive=b.getvalue()
    loc=central_location(archive)
    cdstart=loc["central_directory_offset"]
    cd=archive[cdstart:cdstart+loc["central_directory_size"]]
    footer=bytearray(archive[cdstart+loc["central_directory_size"]:])
    assert len(footer)==22
    footer[16:20]=struct.pack("<I",ORIGINAL_TOTAL-22-len(cd))
    tail=(b"\x00"*(TAIL_BYTES-len(cd)-22))+cd+bytes(footer)
    assert len(tail)==TAIL_BYTES
    return archive,tail,cd


def fake_source(archive,tail):
    def get(url,start,length):
        if start==ORIGINAL_TOTAL-TAIL_BYTES:
            payload=tail[:length]
        else:
            payload=archive[start:start+length]
        # Official server may truthfully return broader Content-Range than requested.
        return 206,f"bytes {start}-{ORIGINAL_TOTAL-1}/{ORIGINAL_TOTAL}",payload
    return get


class BoundedXLSXHeaderTests(unittest.TestCase):
    def test_original_headers_without_numeric_animal_values(self):
        archive,tail,cd=synthetic_archive()
        out=run(fake_source(archive,tail),expected_tail=hashlib.sha256(tail).hexdigest())
        self.assertEqual(out["status"],"ORIGINAL_WORKBOOK_HEADERS_VERIFIED_SOURCE_ONLY")
        self.assertEqual(out["member_selection"]["status"],"UNIQUE_SOURCE_MEMBERS_IDENTIFIED")
        self.assertEqual(set(out["member_receipts"]),{"nightly_pass_counts","source_metadata"})
        self.assertTrue(out["pinned_tail_sha256_verified"])
        self.assertFalse(out["full_detector_effort_or_true_zero_nights_verified"])
        self.assertFalse(out["original_member_payloads_requested_or_read"] if "original_member_payloads_requested_or_read" in out else False)
        self.assertFalse(out["numeric_bat_pass_counts_or_species_values_decoded"])
        self.assertNotIn("9999",str(out))
        self.assertNotIn("314159",str(out))
        self.assertNotIn("Pass Lists 0",str(out))
    def test_compressed_member_crc_mismatch_rejected(self):
        archive,tail,cd=synthetic_archive()
        loc=central_location(tail)
        entries=full_directory_entries(cd,loc["declared_entry_count"])
        e=next(q for q in entries if "night" in q["name_internal"].lower())
        start=e["local_offset"]
        header=archive[start:start+30]
        namesize=int.from_bytes(header[26:28],"little")
        extrasize=int.from_bytes(header[28:30],"little")
        content=archive[start+30+namesize+extrasize:start+30+namesize+extrasize+e["compressed"]]
        tampered=dict(e,crc=0)
        with self.assertRaises(ValueError):
            unzip_original_member(content,tampered)
    def test_fixed_compressed_size_gate(self):
        archive,tail,cd=synthetic_archive()
        entries=full_directory_entries(cd,central_location(tail)["declared_entry_count"])
        item=next(q for q in entries if "night" in q["name_internal"].lower())
        result,data=fetch_member(dict(item,compressed=MAX_COMPRESSED+1),
                                fake_source(archive,tail))
        self.assertEqual(result["status"],"ORIGINAL_SELECTED_MEMBER_CAP_STOP")
        self.assertIsNone(data)
    def test_ignoring_range_is_source_stop(self):
        result,blob=source_prefix(0,30,lambda url,start,length:(200,"",b"A"*30))
        self.assertEqual(result["status"],"SOURCE_RANGE_PREFIX_NOT_VERIFIED_STOP")
        self.assertIsNone(blob)
    def test_mismatched_original_total_is_stop(self):
        result,blob=source_prefix(0,30,lambda url,start,length:
                                 (206,f"bytes 0-100/{ORIGINAL_TOTAL+2}",b"A"*30))
        self.assertEqual(result["status"],"SOURCE_RANGE_PREFIX_NOT_VERIFIED_STOP")
        self.assertIsNone(blob)
    def test_response_category_headers_not_proof_effort(self):
        x=synthetic_xlsx(["Night","Recorder Hours","Pass Count"])
        out=original_xlsx_headers(x)
        self.assertEqual(out["status"],"ORIGINAL_XLSX_FIRST_ROW_HEADERS_ONLY")
        self.assertIn("night",str(out))
        self.assertFalse(out["numeric_bat_counts_or_record_values_decoded"])


if __name__=="__main__":
    unittest.main()
