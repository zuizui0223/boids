"""Synthetic/source-invariant published Table A1 transcription tests."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from paper_tableA1_source_consistency import published_tableA1

class TestPublishedSourceMismatch(unittest.TestCase):
    def test_all_43_published_sites_and_group_sizes(self):
        t=published_tableA1()
        self.assertEqual(len(t),43)
        self.assertEqual(sum(z[0]=="ICE" for z in t.values()),17)
        self.assertEqual(sum(z[0]=="SWE" for z in t.values()),7)
        self.assertEqual(sum(z[0]=="FRASOUTH" for z in t.values()),8)
    def test_hono_source_year_mismatch_and_explicit_table_year(self):
        t=published_tableA1()
        self.assertEqual(t["HONO"][1],(2022,10))
        self.assertEqual(t["HONO"][2],(2023,9))
        self.assertFalse(t["HONO"][1]<=(2018,7)<=t["HONO"][2])
        self.assertFalse(t["NVSK4"][1]<=(2020,5)<=t["NVSK4"][2])
        self.assertFalse(t["LS4"][1]<=(2009,7)<=t["LS4"][2])
    def test_mrc4_metadata_label_alias_preserved_as_warning(self):
        t=published_tableA1()
        self.assertEqual(t["MRC4"][3],"MSC4 paper alias")

if __name__=="__main__":unittest.main()
