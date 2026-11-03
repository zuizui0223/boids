import csv,gzip,tempfile,unittest
from pathlib import Path
from source_preflight import audit_gps_gz, GPS_MD5, haversine_m, parse_stamp

class SourcePreflightTests(unittest.TestCase):
    def make(self,folder,lines):
        path=Path(folder)/'source.csv.gz'
        with gzip.open(path,'wt',newline='') as f:
            w=csv.writer(f);w.writerow(['event-id','timestamp','location-lat','location-long','individual-local-identifier','visible'])
            w.writerows(lines)
        return path
    def test_original_provider_hashes_pinned(self):
        self.assertEqual(len(GPS_MD5),7)
        self.assertEqual(GPS_MD5[2008],"2624a15e124450f54ddc5a4b5c5fce91")
    def test_duplicate_and_visibility(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.make(d,[
                [1,'2008-08-14 18:31:00.000',53.48,6.21,'a','TRUE'],
                [2,'2008-08-14 18:31:03.000',53.48,6.21,'b','TRUE'],
                [3,'2008-08-14 18:31:10.000',53.49,6.22,'a','FALSE'],
                [4,'2008-08-14 18:35:00.000',53.48,6.2101,'a','TRUE'],
                [4,'2008-08-14 18:36:00.000',53.48,6.2101,'a','TRUE']])
            r=audit_gps_gz(p)
            self.assertEqual(r['raw_rows'],5)
            self.assertEqual(r['admitted_visible_valid_position_rows'],3)
            self.assertEqual(r['original_individuals'],2)
            self.assertEqual(r['source_near_neighbor_candidate_pairs_le5s_le100m'],1)
            self.assertEqual(r['dropped_source_not_visible'],1)
            self.assertEqual(r['dropped_duplicate_or_missing_event_id'],1)
            self.assertFalse(r['tide_linked'])
    def test_timestamp_ambiguity_and_metre_geometry(self):
        self.assertEqual(parse_stamp('2008-08-14 18:31:00.000').year,2008)
        with self.assertRaises(ValueError):parse_stamp('2008-08-14T18:31:00Z')
        self.assertLess(haversine_m((None,53.48,6.21),(None,53.48,6.21001)),1)
        self.assertGreater(haversine_m((None,53.48,6.21),(None,53.49,6.21)),1000)

if __name__=='__main__': unittest.main()
