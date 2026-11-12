"""v125 synthetic native CSV source tests only, never new Belgian bird evidence."""
from datetime import datetime,timedelta,timezone
from hashlib import md5
from unittest.mock import patch
import csv,gzip,io,json,unittest
import original_2020_belgium_gull_source as m

def fixture_gps():
    out=io.StringIO()
    w=csv.writer(out)
    w.writerow(['timestamp','location-lat','location-long',
                'individual-local-identifier','visible','individual-taxon-canonical-name'])
    for tax,bird in [('Larus argentatus','bird_A'),('Larus fuscus','bird_B')]:
        for hour in range(1,13):
            dt=datetime(2020,8,1,tzinfo=timezone.utc)+timedelta(hours=hour)
            for minute in (0,25):
                stamp=(dt+timedelta(minutes=minute)).isoformat()
                w.writerow([stamp,'51.341','3.182',bird,'TRUE',tax])
    return gzip.compress(out.getvalue().encode())

class OriginalIndependent2020BirdSource(unittest.TestCase):
    def test_frozen_native_panels_before_any_biological_GIC_result(self):
        self.assertEqual(set(m.PANELS),{'LBBG_JUVENILE','HG_OOSTENDE','LBBG_ZEEBRUGGE'})
        self.assertEqual(m.PANELS['LBBG_JUVENILE']['record'],22083230)
        self.assertEqual(m.PANELS['HG_OOSTENDE']['record'],10054230)
        self.assertEqual(m.PANELS['LBBG_ZEEBRUGGE']['record'],12336021)
        self.assertEqual(m.PANELS['LBBG_JUVENILE']['md5'],
                         '85b9ce9fa0bcee3bcd982260763c7c14')
        self.assertEqual(m.MONTHS,(7,8,9,10))
        self.assertEqual(m.RADIUS_KM,40.)
    def test_exact_Movbank_taxon_on_original_reference_not_guessed_from_filename(self):
        src=('individual-local-identifier,individual-taxon-canonical-name\n'
             'bird_A,Larus argentatus\nbird_B,Larus fuscus\n'
             'bird_BAD,Larus argentatus\nbird_BAD,Larus fuscus\n')
        r,proof=m.source_reference_taxa(src.encode())
        self.assertEqual(r['bird_A'],'Larus argentatus')
        self.assertEqual(r['bird_B'],'Larus fuscus')
        self.assertNotIn('bird_BAD',r)
        self.assertEqual(proof['reference_ids_with_ambiguous_taxon'],1)
    def test_true_original_bird_hour_not_two_fix_per_hour(self):
        source=m.parse_native_gps(fixture_gps(),{},'LBBG_JUVENILE')
        self.assertEqual(source['original_native_all_2020_gzip_GPS_rows'],48)
        self.assertEqual(source['original_native_2020_JulyOctober_rows'],48)
        self.assertEqual(source['true_all_source_bird_hour_counts_by_taxon'][
             'Larus argentatus'],12)
        self.assertEqual(source['true_all_source_bird_hour_counts_by_taxon'][
             'Larus fuscus'],12)
        self.assertFalse(source['source_both_focal_species_admitted_IN_THIS_ONE_STUDY'])
        self.assertTrue(source['NO_2020_BIRD_ID_OR_COORDINATE_OR_TIMESTAMP_EXPORTED'])
        self.assertNotIn('bird_A',json.dumps(source))
    def test_publisher_md5_raw_source_proof_no_substitute(self):
        b=b'public frozen original-source-fixture'
        d=md5(b).hexdigest()
        fake={'url':'https://zenodo.org/api/records/1/files/source/content',
              'md5':d,'size':len(b),'name':'native-file'}
        got,p=m.checked_original_file(fake,fetch_fn=lambda u:b)
        self.assertEqual(got,b)
        self.assertTrue(p['publisher_original_MD5_verified'])
        with self.assertRaisesRegex(m.OriginalSourceStop,'MD5_BYTES_CHANGED'):
            m.checked_original_file({**fake,'md5':'0'*32},fetch_fn=lambda u:b)
    def test_fake_publisher_and_study_identity_are_rejected(self):
        with self.assertRaisesRegex(m.OriginalSourceStop,'NOT_ZENODO'):
            m.get_publisher('https://fake.example.org/gps')
        data={'id':1234,'metadata':{'title':'LBBG_JUVENILE'},
              'files':[]}
        with self.assertRaisesRegex(m.OriginalSourceStop,'RECORD_IDENTITY'):
            m.native_catalog('LBBG_JUVENILE',
               fetch_fn=lambda u:json.dumps(data).encode())
    def test_separate_2020_annual_source_scope_not_cumulative_tags(self):
        self.assertEqual(m.YEAR,2020)
        self.assertEqual(m.MIN_TAXON_BIRDS,5)
        self.assertEqual(m.MIN_TAXON_HOURS,1000)
        self.assertEqual(m.MIN_MONTHS,2)
        self.assertEqual(m.MIN_STEPS,2000)
        self.assertEqual(m.MAX_DISPLACEMENT_KMH,150.)
if __name__=='__main__':unittest.main()
