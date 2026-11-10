"""v109 source truth: 99 study cumulative cannot become annual bird count."""
import unittest,csv,io,gzip
import original_delta_2020_gull_source as z

class GenuineGullSourceTruth(unittest.TestCase):
    def test_2020_version_and_checksum_frozen_before_original_animal_data(self):
        self.assertEqual(z.PUBLISHER_RECORD,22102508)
        self.assertEqual(z.GPS_EXPECTED_MD5,'730549beb8079213ac893d3bf126c2bf')
        self.assertEqual(z.YEAR,2020)
        self.assertEqual(z.EXPECTED_TAGGED_CUMULATIVE,99)
        self.assertEqual(len(z.FOCAL),2)
    def test_non_official_publisher_url_rejected(self):
        with self.assertRaisesRegex(z.SourceNotAdmitted,'NOT_AUTHENTIC'):
            z.get_zenodo('https://fake.example.org/zenodo/2020')
    def test_real_source_taxon_lookup_does_not_infer_from_unknown_ID(self):
        ref='individual-local-identifier,individual-taxon-canonical-name\nGULL_A,Larus argentatus\nGULL_B,Larus fuscus\n'
        a,heads=z.native_reference_taxa(ref.encode())
        self.assertEqual(len(a),2)
        self.assertEqual(a['GULL_B'],'Larus fuscus')
        self.assertEqual(z._get_native_taxon({'individual-local-identifier':'GULL_C'}),None)
    def test_genuine_hourly_dedup_not_raw_gps_pseudoreplicates(self):
        buf=io.StringIO();w=csv.writer(buf)
        w.writerow(['event-id','timestamp','location-lat','location-long','individual-local-identifier','visible'])
        for name in ('GULL_A','GULL_B'):
            for h in range(1,50):
                for minute in (1,30):
                    w.writerow([f'{name}-{h}-{minute}',f'2020-06-01T{h%24:02d}:{minute:02d}:00Z',
                        51.6,3.7,name,'TRUE'])
        raw=gzip.compress(buf.getvalue().encode())
        a=z.native_2020_original_annual_gps_source(raw,{'GULL_A':'Larus argentatus','GULL_B':'Larus fuscus'})
        self.assertEqual(a['original_2020_native_raw_GPS_rows'],196)
        self.assertLess(a['original_2020_native_valid_unique_bird_hour_GPS_fixes_anywhere'],196)
        self.assertFalse(a['both_focal_taxa_pass_independent_original_source_gates'])
        self.assertTrue(a['source_only_NO_2020_RWS_tide_solar_activity_or_foraging_scored'])
if __name__=='__main__':unittest.main()
