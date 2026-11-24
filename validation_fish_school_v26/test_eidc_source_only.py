"""v26 known-truth EIDC metadata/identity checks, no real animal observations."""
from __future__ import annotations
import io
import json
import unittest
from urllib.request import Request
from validation_fish_school_v26 import eidc_source_only as m


def artificial_index(names):
    text='<html><title>Index of /datastore/eidchub/test/</title><h1>Index of /datastore/eidchub/test/</h1><pre>\n'
    for name,n in names.items():
        text+=f'<a href="{name}">{name}</a> 23-Sep-2021 13:33 {n}\n'
    text+='</pre></html>'
    return text.encode()


def artificial_data(n=110):
    return b"".join(f"{i} {i+1} {i+2} {i+3}\n".encode() for i in range(n))


class FakeResponse:
    def __init__(self,url,blob):
        self.url=url
        self.blob=blob
    def geturl(self):
        return self.url
    def read(self,n=-1):
        return self.blob[:n]
    def __enter__(self):return self
    def __exit__(self,*args):return False


class SourceFixtures(unittest.TestCase):
    def test_known_directory_index_source_bytes(self):
        result=m.parse_listing(artificial_index({"01.txt":800,"02.txt":900,"105.txt":1000}))
        self.assertEqual(result,{"01.txt":800,"02.txt":900,"105.txt":1000})

    def test_duplicate_original_number_rejected(self):
        b=artificial_index({"01.txt":800,"02.txt":900,"105.txt":1000})
        dup=b.replace(b"</pre>",b'<a href="01.txt">01.txt</a> 23-Sep-2021 13:33 800\n</pre>')
        with self.assertRaises(m.SourceStop):
            m.parse_listing(dup)

    def test_original_index_missing_probe_stops(self):
        with self.assertRaises(m.SourceStop):
            m.parse_listing(artificial_index({"01.txt":800,"02.txt":900,"03.txt":1000}))

    def test_no_original_xy_values_exported(self):
        d=artificial_data(110)
        out=m.inspect_first_lines(d)
        self.assertEqual(out["nonempty_source_line_count"],110)
        self.assertEqual(out["initial_schema_only"][0]["tokens"],4)
        self.assertTrue(out["original_fish_positions_or_timestamps_exported"] is False)
        self.assertEqual(out["original_school_ID"],"NOT_IDENTIFIED")

    def test_invalid_empty_and_broken_rows_stop(self):
        with self.assertRaises(m.SourceStop):
            m.inspect_first_lines(b"one\n")
        with self.assertRaises(m.SourceStop):
            m.inspect_first_lines(b"x\n"*150)

    def test_fake_original_repository_never_becomes_independent_biological_replicates(self):
        d=artificial_data(110)
        index=artificial_index({n:len(d) for n in m.PROBES})
        blobs={m.BASE:index}
        for name in m.PROBES:
            blobs[m.BASE+name]=d
        def fake(request,timeout=55):
            uri=request.full_url
            return FakeResponse(uri,blobs[uri])
        out=m.run(fake)
        self.assertEqual(out["status"],"SOURCE_STRUCTURE_ONLY_NOT_ECOLOGY_ADMITTED")
        self.assertEqual(out["number_of_indexed_original_TXT_files"],3)
        self.assertFalse(out["new_third_species_effect_estimated"])
        self.assertEqual(out["independent_school_ID_mapping"],"UNKNOWN")
        self.assertEqual(len(out["source_schema_probes"]),3)

    def test_off_origin_redirect_fails_closed(self):
        class Redirect(FakeResponse):
            def geturl(self):
                return "https://third-party.example.org/fish.txt"
        def fake(request,timeout=55):
            return Redirect(request.full_url,b"HELLO")
        with self.assertRaises(m.SourceStop):
            m.fetch_bound(m.BASE,100,fake)


if __name__=="__main__":
    unittest.main()
