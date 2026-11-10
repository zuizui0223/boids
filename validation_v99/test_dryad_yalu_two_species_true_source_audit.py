import unittest
import dryad_yalu_two_species_true_source_audit as s
class OriginalPublisherGate(unittest.TestCase):
    def test_original_publisher_only_and_fixed_doi(self):
        self.assertEqual(s.DOI,'10.5061/dryad.h70rxwdwf')
        self.assertEqual(len(s.NAMES),2)
        with self.assertRaisesRegex(ValueError,'NOT_ORIGINAL'):
            s.get('https://example.com/another-publisher')
    def test_schema_no_fake_bird_count_if_no_identity(self):
        raw=('f_time,f_lon,f_lat,f_tide,r_time,r_lon,r_lat,r_tide,highesttide,Dawn,Dusk,r_Light,dist,predist_f\n'
             '2023-04-01 00:00:00,1,1,l0,2023-04-01 01:00:00,1,1,h0,250,05:00,19:00,day,1200,800\n').encode()
        r=s._contents_inventory(raw,'movement_data_great_knot.csv')
        self.assertEqual(r['state'],'PUBLISHED_COLUMNS_SCHEMA_PRESENT_NOT_YET_BIOLOGICAL_OUTCOME')
        self.assertEqual(r['row_count_events_NOT_INDEPENDENT_BIRDS'],1)
        self.assertIsNone(r['source_independent_id_count_if_present'])
        self.assertTrue(r['NO_BEHAVIORAL_EFFECT_ESTIMATED'])
    def test_missing_original_columns_must_not_score(self):
        r=s._contents_inventory(b'Year,Lat,Lon\n2023,21,100\n','a.csv')
        self.assertEqual(r['state'],'SOURCE_SCHEMA_INCOMPLETE_NOT_ADMITTED')
        self.assertTrue(len(r['missing_published_columns'])>0)
    def test_invalid_publisher_file_uris(self):
        with self.assertRaisesRegex(ValueError,'NOT_AVAILABLE'):
            s.source_link(s.ROOT,{},'stash:files')
        with self.assertRaisesRegex(ValueError,'NON_API'):
            s.source_link(s.ROOT,{'_links':{'stash:files':{'href':'https://evil.example/list'}}},'stash:files')
if __name__=='__main__':unittest.main()
