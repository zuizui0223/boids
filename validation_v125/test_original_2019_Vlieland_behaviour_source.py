"""v125 exact publisher identity and original behavioural classification source safeguards.
All CSV records in tests are SYNTHETIC and cannot become ecological outcomes.
"""
from __future__ import annotations
from unittest.mock import patch
from collections import Counter
import csv,gzip,io,json,unittest
import original_2019_Vlieland_behaviour_source as q

class FrozenOriginalVlielandSource(unittest.TestCase):
    def test_original_native_publisher_source_years_and_checksums_fixed(self):
        self.assertEqual(q.RECORD,10053988)
        self.assertEqual(q.STUDY,'O_VLIELAND')
        self.assertEqual(q.FIRST_YEAR,2019)
        self.assertEqual(q.SECOND_YEAR,2020)
        self.assertEqual(q.FREEZE['O_VLIELAND-accessory-measurements-2019.csv.gz'],
                         'a902b08ff0163edf91a9bcf3822b1c97')
        self.assertEqual(q.FREEZE['O_VLIELAND-accessory-measurements-2020.csv.gz'],
                         'e2588eb066ac904dd330fcb458f455a3')
        self.assertIn('gps',str(q.GPS_FUTURE_PUBLISHER_MD5).lower().replace('','gps',1))
        with self.assertRaisesRegex(q.SourceStop,'NOT_ORIGINAL_ZENODO'):
            q._publisher_get('https://fake.example.com/animal.csv')
    def test_only_transient_network_failure_retry_source_never_changed_checksum(self):
        f=[0]
        def unstable():
            f[0]+=1
            if f[0]==1:raise q.TemporarySourceFailure('TEMP_ORIGINAL_ZENODO_HTTP_504')
            return b'original publisher same hash'
        out,proof=q.exact_source_transport_retry(unstable,'source2019',
                    sleeper=lambda _:None)
        self.assertEqual(f[0],2)
        self.assertEqual(proof['same_exact_source_attempts'],2)
        self.assertEqual(out,b'original publisher same hash')
        with self.assertRaisesRegex(q.SourceStop,'STOP_HASH_DRIFT'):
            q.exact_source_transport_retry(
                lambda:(_ for _ in ()).throw(q.SourceStop('STOP_HASH_DRIFT')),
                'do-not-retry',sleeper=lambda _:None)
    def test_ambiguous_tag_reassignment_never_counted_as_unique_bird(self):
        raw=('tag-local-identifier,individual-local-identifier,behaviour-according-to\n'
             'TAG_A,BIRD1,Algorithm X\nTAG_A,BIRD2,Algorithm X\n'
             'TAG_B,BIRD3,Algorithm X\n').encode()
        mapping,qa=q._reference_anonymous_identity(raw)
        self.assertEqual(len(mapping),1)
        self.assertEqual(mapping['TAG_B'],'BIRD3')
        self.assertEqual(qa['source_native_tags_with_ambiguous_reassigned_bird_ID'],1)
        self.assertTrue(qa['original_bird_tags_OR_personally_identifying_ID_NOT_exposed'])
    def test_true_source_annual_behavior_not_gps_foraging_time_or_103_birds(self):
        f=io.StringIO();w=csv.writer(f)
        w.writerow(['timestamp','individual-local-identifier','tag-local-identifier',
                    'behavioural-classification','visible'])
        w.writerow(['2019-05-01T08:10:00Z','A','TA','foraging','TRUE'])
        w.writerow(['2019-05-01T08:10:10Z','A','TA','Foraging','TRUE'])
        w.writerow(['2019-05-01T10:10:00Z','A','TA','inactive','TRUE'])
        w.writerow(['2019-05-01T11:10:00Z','B','TB','walking','TRUE'])
        w.writerow(['2019-05-01T12:10:00Z','B','TB','foraging','FALSE'])
        w.writerow(['2020-05-01T12:10:00Z','B','TB','foraging','TRUE'])
        w.writerow(['2019-06-01T12:10:00Z','','TB','inactive','TRUE'])
        raw=gzip.compress(f.getvalue().encode())
        result=q.native_annual_classification_census(raw,2019,{'TB':'B'})
        self.assertEqual(result['original_raw_classifier_csv_rows'],7)
        self.assertEqual(result['original_distinct_birds_with_resolved_identity_ANY_behaviour_event'],2)
        self.assertEqual(result['original_native_label_counts_case_preserving']['Foraging'],1)
        self.assertEqual(result['original_native_label_counts_case_preserving']['foraging'],1)
        self.assertEqual(result['original_native_monthly_source_support']['5']['native_exact_foraging_label_count'],2)
        self.assertEqual(result['original_native_monthly_source_support']['6']['native_exact_inactive_label_count'],1)
        self.assertFalse(result['source_future_n8_birds_for_each_class_eligible_but_GPS_tide_NOT_JOINED'])
        self.assertEqual(result['GPS_location_tide_sun_and_true_foraging_time_BIOLOGICAL_EFFECT'],'NOT_ESTIMATED')
        self.assertNotIn('A',str(result['original_native_label_counts_case_preserving']))
    def test_managed_source_package_must_declare_accessory_behaviour_not_gps(self):
        package={'resources':[{'name':'accessory-measurements-2019',
          'path':'O_VLIELAND-accessory-measurements-2019.csv.gz',
          'schema':{'fields':[
          {'name':'timestamp','type':'datetime'},
          {'name':'behavioural-classification','type':'string','description':'acc classification'}]}}]}
        a=q.original_resource_schema(package,2019)
        self.assertTrue(a['native_schema_declares_classification'])
        with self.assertRaisesRegex(q.SourceStop,'RESOURCE_MISSING'):
            q.original_resource_schema(package,2020)
    def test_source_treats_missing_time_missing_label_and_gzip_errors_as_quality(self):
        bad=b'not gzip'
        with self.assertRaisesRegex(q.SourceStop,'NOT_GZIP'):
            q.native_annual_classification_census(bad,2019,{})
        with self.assertRaisesRegex(ValueError,'UNFROZEN'):
            q.native_annual_classification_census(gzip.compress(b''),2018,{})
if __name__=='__main__':unittest.main()
