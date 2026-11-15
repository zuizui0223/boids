import hashlib, csv, io, unittest
from unittest.mock import patch
from comparative_state import usgs_2025_schema_gate_v6b as m

class Test(unittest.TestCase):
    def fake(self, rows, header=['wetland_id','survey_year','duck_count']):
        s=io.StringIO();w=csv.writer(s);w.writerow(header);w.writerows(rows)
        return s.getvalue().encode()
    def check(self,b):
        with patch.object(m,'MD5',hashlib.md5(b).hexdigest()),patch.object(m,'BYTES',len(b)):
            return m.source_schema_from_bytes(b)
    def test_good_header(self):
        r=self.check(self.fake([[i,2023,20+i] for i in range(101)]))
        self.assertEqual(r['status'],'SOURCE_SCHEMA_ONLY_ADMITTED')
        self.assertTrue(r['no_numeric_environment_or_bird_values_opened'])
    def test_duplicate_column_stop(self):
        r=self.check(self.fake([[i,2023,20+i] for i in range(101)],header=['id','id','count']))
        self.assertEqual(r['status'],'SOURCE_SCHEMA_STOP_HEADER_INVALID')
    def test_ragged_stop(self):
        x=self.fake([[i,2023,20+i] for i in range(100)])+b'x,y\n'
        self.assertEqual(self.check(x)['status'],'SOURCE_SCHEMA_STOP_ROWS_OR_WIDTH')
    def test_hash_mismatch_stop(self):
        self.assertEqual(m.source_schema_from_bytes(b'bad')['status'],'SOURCE_STOP_SIZE_OR_MD5')
    def test_few_rows_stop(self):
        self.assertEqual(self.check(self.fake([[1,2,3]]))['status'],'SOURCE_SCHEMA_STOP_ROWS_OR_WIDTH')

if __name__=='__main__':unittest.main()
